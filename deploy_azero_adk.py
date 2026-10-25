#!/usr/bin/env python3
"""
ATTO 4 — Deploy del Multi-Agente a Grafo `azienda_zero_agent` ("Azienda Zero Governance & Sizing Multi-Agent")
su Vertex AI Agent Engine (`rootprj-377111`, `us-central1`):
1. Attiva Cloud Trace, Cloud Logging e OpenTelemetry GenAI Capture (`enable_tracing=True`
   + `GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY=true`) e abilita il Playground.
2. Inietta `a2a_agent_card` in `spec.classMethods` (`async_create_session`) sul Reasoning Engine
   per popolare `spec.agentCard` mantenendo tutti i metodi ADK del Playground.
3. Registra e aggiorna l'agente con Agent Card A2A completa (`azero-governance-adk-agent`)
   in Agent Platform -> Agent Registry (`global` e `us-central1`).
4. Salva il Resource Name in `deployment_metadata_azero.json` e `DEPLOYED_AZERO_AGENT.txt`.
"""

import datetime
import json
import os
import subprocess
import time
import urllib.error
import urllib.request

import vertexai
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp

from azienda_zero_agent.agent import root_agent

DISPLAY_NAME = "Azienda Zero Governance & Sizing Multi-Agent"
SERVICE_ID = "azero-governance-adk-agent"


def _detect_project_id() -> str:
    for env_key in ("GOOGLE_CLOUD_PROJECT", "DEVSHELL_PROJECT_ID", "GCLOUD_PROJECT"):
        val = os.environ.get(env_key, "").strip()
        if val:
            return val
    try:
        res = subprocess.run(
            ["gcloud", "config", "get-value", "project"],
            check=True,
            capture_output=True,
            text=True,
        )
        if res.stdout.strip():
            return res.stdout.strip()
    except Exception:
        pass
    return "rootprj-377111"


def _ensure_staging_bucket(project_id: str, region: str) -> str:
    explicit = os.environ.get("STAGING_BUCKET", "").strip()
    if explicit:
        return explicit if explicit.startswith("gs://") else f"gs://{explicit}"
    bucket_name = f"{project_id}-agent-engine-staging"
    bucket_uri = f"gs://{bucket_name}"
    chk = subprocess.run(
        ["gcloud", "storage", "buckets", "describe", bucket_uri, f"--project={project_id}"],
        capture_output=True,
        text=True,
    )
    if chk.returncode != 0:
        subprocess.run(
            [
                "gcloud",
                "storage",
                "buckets",
                "create",
                bucket_uri,
                f"--project={project_id}",
                f"--location={region}",
                "--quiet",
            ],
            check=False,
        )
    return bucket_uri


def _get_access_token() -> str:
    for cmd in (
        ["gcloud", "auth", "application-default", "print-access-token"],
        ["gcloud", "auth", "print-access-token"],
    ):
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
    return ""


def _build_agent_card(a2a_url: str, streaming: bool = True) -> dict:
    return {
        "name": DISPLAY_NAME,
        "description": (
            "Sistema Multi-Agente ADK a grafo per Azienda Zero (Regione del Veneto) su Agent Engine: "
            "Orchestratore (`azero_orchestrator`) + 3 Sub-Agenti specialistici (`ulss_pdta_kpi_agent`, "
            "`crav_compliance_agent`, `psn_cloud_sizing_agent`)."
        ),
        "version": "1.0.0",
        "protocolVersion": "0.3.0",
        "preferredTransport": "HTTP+JSON",
        "url": a2a_url,
        "defaultInputModes": ["text/plain"],
        "defaultOutputModes": ["application/json", "text/plain"],
        "capabilities": {"streaming": streaming},
        "supportsAuthenticatedExtendedCard": True,
        "skills": [
            {
                "id": "ulss_pdta_kpi_monitoring",
                "name": "Monitoraggio KPI PDTA & COT 9 ULSS Veneto",
                "description": "Analizza Time-to-Treatment PDTA (<=30 gg), COT attive e volumi Telemedicina delle 9 ULSS del Veneto e IOV.",
                "tags": ["azienda-zero", "pdta", "ulss", "veneto", "sanita"],
                "examples": [
                    "Analizza i KPI PDTA e lo stato delle COT per ULSS 6 Euganea e ULSS 9 Scaligera.",
                ],
            },
            {
                "id": "crav_acn_gdpr_compliance",
                "name": "Verifica Gare CRAV, GDPR/CDPA, HIPAA & ACN Data Region Europe",
                "description": "Verifica conformità art. 28 GDPR (CDPA), esclusione clausola USA HIPAA per dati UE e requisiti ACN QC2/QC3.",
                "tags": ["crav", "gdpr", "cdpa", "hipaa", "acn"],
                "examples": [
                    "Verifica come sono regolati il CDPA sotto GDPR, la clausola HIPAA e la Data Region Europe per Azienda Zero.",
                ],
            },
            {
                "id": "psn_cloud_sizing_usd",
                "name": "Calcolo Sizing Cloud/PSN Mensile in USD ($/mo)",
                "description": "Calcola Prezzo Mese List ($/mo), 1Y CUD ($/mo), 3Y CUD ($/mo), OS $/mo (solo OS supportati) e COSTO MESE LICENZA MSSQL $/MO separato.",
                "tags": ["sizing", "usd", "cud", "mssql", "psn"],
                "examples": [
                    "Calcola il sizing mensile in USD per 2 VM 8vCPU/32GiB con Windows Server 2022 e SQL Server 2022 Standard e 1 VM con Windows Server 2012 R2.",
                ],
            },
        ],
    }


def _patch_reasoning_engine_a2a_card(project_id: str, region: str, resource_name: str):
    token = _get_access_token()
    if not token:
        return
    base_url = f"https://{region}-aiplatform.googleapis.com/v1beta1"
    a2a_url = f"{base_url}/{resource_name}/a2a"

    def _api(method: str, url: str, body=None):
        data = json.dumps(body).encode("utf-8") if body is not None else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Authorization", f"Bearer {token}")
        req.add_header("X-Goog-User-Project", project_id)
        if data is not None:
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return resp.status, json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode("utf-8", errors="replace")

    st, current_re = _api("GET", f"{base_url}/{resource_name}")
    if st != 200 or not isinstance(current_re, dict):
        return
    spec = current_re.get("spec", {})
    class_methods = spec.get("classMethods", [])
    card_dict = _build_agent_card(a2a_url, streaming=False)
    card_json_str = json.dumps(card_dict)

    for cm in class_methods:
        if cm.get("name") == "async_create_session":
            cm["a2a_agent_card"] = card_json_str

    patch_body = {
        "displayName": current_re.get("displayName", DISPLAY_NAME),
        "description": current_re.get("description", card_dict["description"]),
        "spec": {
            "classMethods": class_methods,
            "agentFramework": spec.get("agentFramework", "google-adk"),
        },
    }
    st_p, resp_p = _api(
        "PATCH",
        f"{base_url}/{resource_name}?updateMask=spec.class_methods",
        patch_body,
    )
    if st_p == 200 and isinstance(resp_p, dict) and "name" in resp_p:
        op_name = resp_p["name"]
        for _ in range(30):
            _, op_res = _api("GET", f"{base_url}/{op_name}")
            if isinstance(op_res, dict) and op_res.get("done"):
                print("  -> ✅ `spec.agentCard` popolato sul Reasoning Engine.")
                break
            time.sleep(2)


def register_in_agent_registry(project_id: str, region: str, resource_name: str):
    a2a_url = f"https://{region}-aiplatform.googleapis.com/v1beta1/{resource_name}/a2a"
    agent_card = _build_agent_card(a2a_url, streaming=True)

    for loc in ("global", region):
        subprocess.run(
            [
                "gcloud",
                "alpha",
                "agent-registry",
                "services",
                "delete",
                SERVICE_ID,
                f"--location={loc}",
                f"--project={project_id}",
                "--quiet",
            ],
            capture_output=True,
            text=True,
        )
        cmd_create = [
            "gcloud",
            "alpha",
            "agent-registry",
            "services",
            "create",
            SERVICE_ID,
            f"--location={loc}",
            f"--project={project_id}",
            f"--display-name={DISPLAY_NAME}",
            "--description=Multi-Agente ADK a grafo per Azienda Zero (PDTA 9 ULSS, Compliance CRAV/ACN/GDPR e Sizing USD)",
            "--agent-spec-type=a2a-agent-card",
            f"--agent-spec-content={json.dumps(agent_card)}",
            "--quiet",
        ]
        res = subprocess.run(cmd_create, capture_output=True, text=True)
        if res.returncode == 0:
            print(f"  -> ✅ Registrato servizio A2A '{SERVICE_ID}' in Agent Registry (location={loc})")
        else:
            print(f"  -> ℹ️ Output Agent Registry ({loc}): {res.stderr.strip()}")


def main():
    project_id = _detect_project_id()
    region = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
    staging_bucket = _ensure_staging_bucket(project_id, region)

    print(f"=== 1. Inizializzazione Vertex AI ({project_id} | {region} | {staging_bucket}) ===")
    vertexai.init(project=project_id, location=region, staging_bucket=staging_bucket)

    adk_app = AdkApp(agent=root_agent, enable_tracing=True)
    req_file = "azienda_zero_agent/requirements.txt" if os.path.exists("azienda_zero_agent/requirements.txt") else "requirements.txt"
    with open(req_file, "r", encoding="utf-8") as f:
        reqs = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]

    env_vars = {
        "GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY": "true",
        "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT": "true",
        "ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS": "true",
    }

    print(f"=== 2. Deploy Multi-Agente '{DISPLAY_NAME}' su Vertex AI Agent Engine ===")
    remote_agent = agent_engines.create(
        agent_engine=adk_app,
        display_name=DISPLAY_NAME,
        description=(
            "Sistema Multi-Agente ADK a grafo per Azienda Zero (Regione del Veneto) con "
            "Orchestratore + 3 Sub-Agenti (PDTA 9 ULSS, Compliance CRAV/GDPR/ACN, Sizing Cloud USD) e OpenTelemetry."
        ),
        requirements=reqs,
        extra_packages=["azienda_zero_agent"],
        env_vars=env_vars,
    )

    resource_name = remote_agent.resource_name
    engine_id = resource_name.split("/")[-1]
    print(f"  -> ✅ Reasoning Engine creato con successo: {resource_name}")

    metadata = {
        "remote_agent_runtime_id": resource_name,
        "engine_id": engine_id,
        "project_id": project_id,
        "location": region,
        "display_name": DISPLAY_NAME,
        "deployment_target": "agent_runtime",
        "telemetry_enabled": True,
        "tracing_enabled": True,
        "playground_url": (
            f"https://console.cloud.google.com/vertex-ai/agents/agent-engines/"
            f"locations/{region}/agent-engines/{engine_id}/playground?project={project_id}"
        ),
        "cloud_trace_url": f"https://console.cloud.google.com/traces/explorer?project={project_id}",
        "a2a_endpoint_url": f"https://{region}-aiplatform.googleapis.com/v1beta1/{resource_name}/a2a",
        "deployment_timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    with open("deployment_metadata_azero.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    with open("DEPLOYED_AZERO_AGENT.txt", "w", encoding="utf-8") as f:
        f.write(resource_name + "\n")

    print("=== 3. Configurazione A2A Card & Registrazione in Agent Registry ===")
    _patch_reasoning_engine_a2a_card(project_id, region, resource_name)
    register_in_agent_registry(project_id, region, resource_name)
    print(f"\n🎉 Playground Agent Engine pronto:\n   {metadata['playground_url']}")


if __name__ == "__main__":
    main()
