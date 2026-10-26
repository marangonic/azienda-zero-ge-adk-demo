#!/usr/bin/env python3
"""
Script di Pulizia e Undeploy Completo (Teardown) per il Laboratorio / Demo Azienda Zero
sul progetto GCP `rootprj-377111`.

Rimuove esclusivamente le risorse create per la demo di Azienda Zero (Regione del Veneto),
lasciando intatte eventuali altre risorse del progetto e mantenendo intatto il repository:
1. Undeploy / Delete del Multi-Agente ADK `Azienda Zero Governance & Sizing Multi-Agent`
   da Vertex AI Agent Engine (`us-central1`).
2. Rimozione del servizio A2A `azero-governance-adk-agent` da Agent Registry (`global` e `us-central1`).
3. Rimozione del Chat Agent `Assistente Governance CRAV e PDTA Azienda Zero`,
   dell'Agente ADK registrato e delle 3 Skills di Azienda Zero da Gemini Enterprise App.
4. Rimozione dell'Engine dedicato `azero-governance-app` (se presente) e del Connettore Data Store
   `azero-crav-pdta-ds`.
5. Svuotamento e cancellazione del Bucket Cloud Storage `gs://rootprj-377111-azienda-zero-veneto`.
"""

import json
import os
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "rootprj-377111").strip() or "rootprj-377111"
REGION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1").strip() or "us-central1"
DATA_STORE_ID = "azero-crav-pdta-ds"
ENGINE_ID = "azero-governance-app"
BUCKET_NAME = f"{PROJECT_ID}-azienda-zero-veneto"
SERVICE_ID = "azero-governance-adk-agent"

AZERO_AGENT_DISPLAY_NAMES = {
    "Assistente Governance CRAV e PDTA Azienda Zero",
    "Azienda Zero Governance & Sizing Multi-Agent (ADK)",
    "Verifica Compliance GDPR CDPA e ACN Data Region Europe",
    "Analisi KPI PDTA e Piano Riequilibrio 9 ULSS Veneto",
    "Generatore Bozza Determina Indizione Gara CRAV",
}


def get_token() -> str:
    for cmd in (
        ["gcloud", "auth", "print-access-token"],
        ["gcloud", "auth", "application-default", "print-access-token"],
    ):
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
    raise RuntimeError("Impossibile ottenere il token OAuth2. Esegui `gcloud auth login`.")


def api_request(method: str, url: str, token: str, body=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("X-Goog-User-Project", PROJECT_ID)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
            return resp.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")


def undeploy_reasoning_engines(token: str):
    print(f"\n=== 1. Undeploy Multi-Agente ADK da Vertex AI Agent Engine ({REGION}) ===")
    base_url = f"https://{REGION}-aiplatform.googleapis.com/v1beta1/projects/{PROJECT_ID}/locations/{REGION}/reasoningEngines"
    st, resp = api_request("GET", base_url, token)
    if st != 200 or not isinstance(resp, dict):
        print(f"  -> Nessun ReasoningEngine elencato (HTTP {st}).")
        return
    engines = resp.get("reasoningEngines", [])
    deleted_any = False
    for eng in engines:
        name = eng.get("name", "")
        dname = eng.get("displayName", "")
        if "azienda zero" in dname.lower() or "azero" in dname.lower():
            del_url = f"https://{REGION}-aiplatform.googleapis.com/v1beta1/{name}?force=true"
            st_del, resp_del = api_request("DELETE", del_url, token)
            print(f"  -> 🗑️ Eliminato Reasoning Engine `{dname}` ({name}) — HTTP {st_del}")
            deleted_any = True
    if not deleted_any:
        print("  -> ℹ️ Nessun Reasoning Engine di Azienda Zero presente su Agent Engine.")


def cleanup_agent_registry(token: str):
    print("\n=== 2. Rimozione Servizio A2A da Vertex AI Agent Registry ===")
    for loc in ("global", REGION):
        url = f"https://cloudapiregistry.googleapis.com/v1alpha/projects/{PROJECT_ID}/locations/{loc}/apis/-/services/{SERVICE_ID}"
        st, _ = api_request("DELETE", url, token)
        if st in (200, 204):
            print(f"  -> 🗑️ Eliminato servizio A2A `{SERVICE_ID}` da Agent Registry ({loc}).")
        elif st == 404:
            print(f"  -> ℹ️ Servizio A2A `{SERVICE_ID}` non presente in Agent Registry ({loc}).")
        else:
            print(f"  -> ℹ️ Agent Registry ({loc}): HTTP {st}")


def cleanup_gemini_enterprise(token: str):
    print("\n=== 3. Rimozione Agenti, Skills, Engine e Connettore da Gemini Enterprise App ===")
    base = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_ID}/locations/global/collections/default_collection"
    st_e, resp_e = api_request("GET", f"{base}/engines", token)
    engines = resp_e.get("engines", []) if st_e == 200 and isinstance(resp_e, dict) else []

    for eng in engines:
        eng_name = eng.get("name", "")
        eng_id = eng_name.split("/")[-1]
        if not eng_id:
            continue
        agents_url = f"{base}/engines/{eng_id}/assistants/default_assistant/agents"
        st_a, resp_a = api_request("GET", agents_url, token)
        agents = resp_a.get("agents", []) if st_a == 200 and isinstance(resp_a, dict) else []
        for ag in agents:
            ag_name = ag.get("name", "")
            ag_display = ag.get("displayName", "")
            if (
                ag_display in AZERO_AGENT_DISPLAY_NAMES
                or "azienda zero" in ag_display.lower()
                or "crav" in ag_display.lower()
            ):
                st_del, _ = api_request("DELETE", f"https://discoveryengine.googleapis.com/v1alpha/{ag_name}", token)
                print(f"  -> 🗑️ [{eng_id}] Eliminato Agente/Skill `{ag_display}` (HTTP {st_del})")

        # Se l'Engine è quello creato specificamente per Azienda Zero (`azero-governance-app`), eliminalo
        if eng_id == ENGINE_ID:
            st_de, _ = api_request("DELETE", f"{base}/engines/{ENGINE_ID}", token)
            print(f"  -> 🗑️ Eliminata App Gemini Enterprise dedicata `{ENGINE_ID}` (HTTP {st_de})")
            time.sleep(2)

    # Elimina il Connettore Data Store `azero-crav-pdta-ds`
    st_ds, _ = api_request("DELETE", f"{base}/dataStores/{DATA_STORE_ID}", token)
    if st_ds in (200, 204):
        print(f"  -> 🗑️ Eliminato Connettore Data Store `{DATA_STORE_ID}` (HTTP {st_ds}).")
    elif st_ds == 404:
        print(f"  -> ℹ️ Connettore Data Store `{DATA_STORE_ID}` già assente.")
    else:
        print(f"  -> ℹ️ Stato eliminazione Data Store `{DATA_STORE_ID}`: HTTP {st_ds}")


def cleanup_gcs_bucket(token: str):
    print(f"\n=== 4. Eliminazione Bucket Cloud Storage `gs://{BUCKET_NAME}` ===")
    list_url = f"https://storage.googleapis.com/storage/v1/b/{BUCKET_NAME}/o"
    st_l, resp_l = api_request("GET", list_url, token)
    if st_l == 404:
        print(f"  -> ℹ️ Bucket `gs://{BUCKET_NAME}` già assente.")
        return
    if st_l == 200 and isinstance(resp_l, dict):
        items = resp_l.get("items", [])
        for it in items:
            obj_name = it.get("name", "")
            if obj_name:
                del_obj_url = f"https://storage.googleapis.com/storage/v1/b/{BUCKET_NAME}/o/{urllib.parse.quote(obj_name, safe='')}"
                api_request("DELETE", del_obj_url, token)
        print(f"  -> 🗑️ Eliminati {len(items)} oggetti da `gs://{BUCKET_NAME}`.")

    st_b, _ = api_request("DELETE", f"https://storage.googleapis.com/storage/v1/b/{BUCKET_NAME}", token)
    if st_b in (200, 204):
        print(f"  -> 🗑️ Bucket `gs://{BUCKET_NAME}` eliminato con successo.")
    else:
        print(f"  -> ℹ️ Stato eliminazione Bucket `gs://{BUCKET_NAME}`: HTTP {st_b}")


def cleanup_local_runtime_files():
    for fname in ("DEPLOYED_AZERO_AGENT.txt", "WEB_APP_URL_AZERO.txt", "deployment_metadata_azero.json"):
        if os.path.exists(fname):
            os.remove(fname)


def main():
    print("================================================================================")
    print(f"🧹 TEARDOWN & UNDEPLOY LABORATORIO AZIENDA ZERO SU `{PROJECT_ID}`")
    print("================================================================================")
    token = get_token()
    undeploy_reasoning_engines(token)
    cleanup_agent_registry(token)
    cleanup_gemini_enterprise(token)
    cleanup_gcs_bucket(token)
    cleanup_local_runtime_files()
    print("\n================================================================================")
    print("✅ PULIZIA E UNDEPLOY COMPLETATI! Il repository GitHub resta intatto.")
    print("================================================================================")


if __name__ == "__main__":
    main()
