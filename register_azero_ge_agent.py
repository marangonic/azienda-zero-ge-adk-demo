#!/usr/bin/env python3
"""
ATTO 1 — Pubblicazione automatica dell'Agente Multi-Livello Gemini Enterprise App
(`Assistente Governance CRAV e PDTA Azienda Zero` con `gemini-3.8-flash`) e delle 3 Skills
collegate al Connettore Documentale `azero-crav-pdta-ds` sul progetto `rootprj-377111`.
"""

import argparse
import json
import os
import subprocess
import urllib.error
import urllib.request

DATA_STORE_ID = "azero-crav-pdta-ds"
PREFERRED_ENGINE_ID = "azero-governance-app"

REQUIRED_ENGINE_FEATURES = {
    "agent-gallery": "FEATURE_STATE_ON",
    "no-code-agent-builder": "FEATURE_STATE_ON",
    "prompt-gallery": "FEATURE_STATE_ON",
    "model-selector": "FEATURE_STATE_ON",
    "agent-sharing": "FEATURE_STATE_ON",
    "agent-sharing-without-admin-approval": "FEATURE_STATE_ON",
    "skills": "FEATURE_STATE_ON",
    "skill-sharing": "FEATURE_STATE_ON",
    "skill-sharing-without-admin-approval": "FEATURE_STATE_ON",
    "workflow-agents": "FEATURE_STATE_ON",
    "workflow-agent-sharing": "FEATURE_STATE_ON",
    "workflow-agent-sharing-without-admin-approval": "FEATURE_STATE_ON",
}


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


def _detect_project_number(project_id: str) -> str:
    try:
        res = subprocess.run(
            ["gcloud", "projects", "describe", project_id, "--format=value(projectNumber)"],
            check=True,
            capture_output=True,
            text=True,
        )
        if res.stdout.strip():
            return res.stdout.strip()
    except Exception:
        pass
    return "482813436426"


def get_token() -> str:
    for cmd in (
        ["gcloud", "auth", "print-access-token"],
        ["gcloud", "auth", "application-default", "print-access-token"],
    ):
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
    raise RuntimeError("Esegui `gcloud auth login` prima di lanciare lo script.")


def api_request(method: str, url: str, token: str, project_id: str, body=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("X-Goog-User-Project", project_id)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            raw = resp.read().decode("utf-8")
            return resp.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")


def discover_target_engines(project_id: str, token: str):
    url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{project_id}/locations/global/collections/default_collection/engines"
    st, resp = api_request("GET", url, token, project_id)
    if st != 200 or not isinstance(resp, dict):
        raise RuntimeError(f"Impossibile elencare gli Engine Gemini Enterprise ({st}): {resp}")
    engines = resp.get("engines", [])
    if not engines:
        raise RuntimeError("Nessun Engine Gemini Enterprise trovato. Esegui prima `python3 setup_azero_ge_connector.py`.")
    # Pubblichiamo l'agente sia sull'Engine `azero-governance-app` sia sull'Engine principale del progetto così è visibile ovunque!
    engine_ids = []
    for eng in engines:
        eid = eng.get("name", "").split("/")[-1]
        if eid and eid not in engine_ids:
            engine_ids.append(eid)
    return engine_ids


def discover_deployed_azero_re(project_id: str, token: str, region: str = "us-central1") -> str:
    if os.path.exists("DEPLOYED_AZERO_AGENT.txt"):
        with open("DEPLOYED_AZERO_AGENT.txt", "r", encoding="utf-8") as f:
            val = f.read().strip()
            if val:
                return val
    url = f"https://{region}-aiplatform.googleapis.com/v1beta1/projects/{project_id}/locations/{region}/reasoningEngines"
    st, resp = api_request("GET", url, token, project_id)
    if st != 200 or not isinstance(resp, dict):
        return ""
    engines = resp.get("reasoningEngines", [])
    engines.sort(key=lambda x: x.get("createTime", ""), reverse=True)
    for e in engines:
        if "azienda zero" in e.get("displayName", "").lower() or "azero" in e.get("displayName", "").lower():
            return e.get("name", "")
    return engines[0].get("name", "") if engines else ""


def publish_on_engine(project_id: str, project_number: str, engine_id: str, token: str, reasoning_engine: str):
    eng_url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{project_id}/locations/global/collections/default_collection/engines/{engine_id}"
    st, eng = api_request("GET", eng_url, token, project_id)
    feats = dict(eng.get("features", {})) if st == 200 and isinstance(eng, dict) else {}
    feats.update(REQUIRED_ENGINE_FEATURES)
    api_request("PATCH", f"{eng_url}?updateMask=features", token, project_id, {"features": feats})

    agents_url = f"{eng_url}/assistants/default_assistant/agents"
    st_list, resp_list = api_request("GET", agents_url, token, project_id)
    existing_agents = resp_list.get("agents", []) if st_list == 200 and isinstance(resp_list, dict) else []

    # 1. Registra eventuale Agente ADK Azienda Zero su questo Engine
    adk_agent_resource = ""
    if reasoning_engine:
        adk_display = "Azienda Zero Governance & Sizing Multi-Agent (ADK)"
        for ag in existing_agents:
            if ag.get("displayName") == adk_display:
                api_request("DELETE", f"https://discoveryengine.googleapis.com/v1alpha/{ag['name']}", token, project_id)
        adk_body = {
            "displayName": adk_display,
            "description": (
                "Sistema Multi-Agente ADK a grafo per Azienda Zero (Regione del Veneto): "
                "KPI PDTA 9 ULSS, Compliance GDPR/CDPA/ACN e Sizing Mensile USD con regole OS e MSSQL."
            ),
            "adkAgentDefinition": {
                "toolSettings": {
                    "toolDescription": (
                        "Interroga il grafo multi-agente ADK di Azienda Zero per KPI PDTA delle 9 ULSS, "
                        "verifica compliance ACN/GDPR/HIPAA e calcolo sizing mensile in USD ($/mo)."
                    )
                },
                "provisionedReasoningEngine": {"reasoningEngine": reasoning_engine},
            },
            "sharingConfig": {"scope": "ALL_USERS"},
        }
        st_adk, resp_adk = api_request("POST", agents_url, token, project_id, adk_body)
        if st_adk == 200 and isinstance(resp_adk, dict):
            adk_agent_resource = resp_adk.get("name", "")
            print(f"  -> [{engine_id}] Registrato Agente ADK `{adk_display}` ({adk_agent_resource}).")

    # 2. Crea le 3 Skills di Azienda Zero in /r/skills
    skills_defs = [
        {
            "displayName": "Verifica Compliance GDPR CDPA e ACN Data Region Europe",
            "description": "Verifica per Azienda Zero la conformità GDPR art. 28 (CDPA), l'inapplicabilità della clausola USA HIPAA ai dati UE e il requisito ACN Data Region Europe.",
            "instruction": (
                "Quando l'utente chiede chiarimenti su privacy, GDPR, CDPA, HIPAA o qualifica ACN per Azienda Zero e le 9 ULSS del Veneto, "
                "consulta il documento '03_Direttiva_Privacy_GDPR_CDPA_ACN_Data_Region_Europe.html' nel Connettore `azero-crav-pdta-ds` ed esponi sempre:\n"
                "1. Validità del CDPA standard all'accettazione dei ToS (art. 28 GDPR);\n"
                "2. Inapplicabilità della clausola USA HIPAA (art. 3.3 viii ToS) ai dati sanitari di cittadini italiani/UE sotto GDPR;\n"
                "3. Obbligo di configurazione Data Region = Europe (storage + processing incluso Gemini) su Enterprise Plus / Frontline Plus per conformità ACN QC2, e architettura ibrida Cloud Interconnect su PSN per i carichi integrati."
            ),
        },
        {
            "displayName": "Analisi KPI PDTA e Piano Riequilibrio 9 ULSS Veneto",
            "description": "Analizza i tempi di attesa PDTA (soglia <=30 giorni), lo stato delle COT e i pazienti in Telemedicina delle 9 ULSS del Veneto proponendo il protocollo di riequilibrio.",
            "instruction": (
                "Quando l'utente chiede lo stato dei PDTA o delle Centrali Operative Territoriali (COT) delle ULSS venete, "
                "consulta '02_Linee_Guida_PDTA_Oncologia_Cronicita_ULSS_Veneto.html' e '05_Matrice_Fabbisogni_ICT_e_KPI_9_ULSS_Regione_Veneto.html' e presenta:\n"
                "1. Tabella con Assistiti, COT attive, Time-to-Treatment (soglia <=30 gg) e Pazienti in Telemedicina;\n"
                "2. Segnalazione immediata delle ULSS in ALLERTA_SLA (ULSS 9 Scaligera a 31 gg) o ATTENZIONE_SOGLIA (ULSS 7 Pedemontana a 29 gg);\n"
                "3. Attivazione dei 3 step del Protocollo di Escalation con IOV Padova, AOUI Verona e Teleconsulto GOM."
            ),
        },
        {
            "displayName": "Generatore Bozza Determina Indizione Gara CRAV",
            "description": "Redige la bozza di Determina Dirigenziale CRAV di Azienda Zero nelle 6 sezioni ufficiali (MOD-DET-CRAV-AZERO-2026) con tabella prezzi mensili in USD.",
            "instruction": (
                "Quando l'utente chiede di preparare una Determina Dirigenziale per gare CRAV o attivazione servizi Cloud/Telemedicina per le ULSS del Veneto, "
                "usa obbligatoriamente le 6 SEZIONI del modello '06_Template_Determina_Indizione_Gara_CRAV_Azienda_Zero.html' (Intestazione e RUP art. 15 D.Lgs. 36/2023, Premesse L.R. Veneto 19/2016, Analisi Tecnica e Sizing Cloud in USD $/mo, Quadro Economico PNRR/GSA, Presidi GDPR/CDPA/ACN Data Region Europe, Dispositivo con CIG/CUP)."
            ),
        },
    ]

    for s in skills_defs:
        for ag in existing_agents:
            if ag.get("displayName") == s["displayName"]:
                api_request("DELETE", f"https://discoveryengine.googleapis.com/v1alpha/{ag['name']}", token, project_id)
        skill_payload = {
            "displayName": s["displayName"],
            "description": s["description"],
            "skillAgentDefinition": {"instruction": s["instruction"]},
            "sharingConfig": {"scope": "ALL_USERS"},
        }
        st_sk, resp_sk = api_request("POST", agents_url, token, project_id, skill_payload)
        if st_sk == 200 and isinstance(resp_sk, dict):
            sk_name = resp_sk["name"]
            api_request("POST", f"https://discoveryengine.googleapis.com/v1alpha/{sk_name}:requestAgentReview", token, project_id, {})
            api_request("PATCH", f"https://discoveryengine.googleapis.com/v1alpha/{sk_name}?updateMask=sharingConfig", token, project_id, {"sharingConfig": {"scope": "ALL_USERS"}})
            print(f"  -> [{engine_id} | Skill] Creata e condivisa `{s['displayName']}`.")

    # 3. Crea e pubblica il Chat Agent Multi-Livello con Gemini 3.8 Flash connesso a `azero-crav-pdta-ds`
    chat_display_name = "Assistente Governance CRAV e PDTA Azienda Zero"
    for ag in existing_agents:
        if "Assistente Governance CRAV" in ag.get("displayName", ""):
            api_request("DELETE", f"https://discoveryengine.googleapis.com/v1alpha/{ag['name']}", token, project_id)

    ds_resource = f"projects/{project_number}/locations/global/collections/default_collection/dataStores/{DATA_STORE_ID}"
    ds_spec = {"specs": [{"dataStore": ds_resource}]}

    phase2_sub_agents = ["spec_pdta_ulss", "spec_determine_crav"]
    if adk_agent_resource:
        phase2_sub_agents.append("ref_adk_azero")

    nodes = [
        {
            "id": "root_agent",
            "displayName": chat_display_name,
            "sequentialAgentNode": {
                "description": "Orchestratore sequenziale multi-livello Azienda Zero Veneto: Fase 1 Istruttoria Gare CRAV & Compliance ACN/GDPR -> Fase 2 Monitoraggio PDTA 9 ULSS & Redazione Atti.",
                "subAgentIds": ["coord_crav_compliance", "coord_pdta_atti"],
            },
        },
        {
            "id": "coord_crav_compliance",
            "displayName": "Fase 1 - Istruttoria Gare CRAV e Compliance ACN GDPR",
            "llmAgentNode": {
                "model": "gemini-3.8-flash",
                "description": "Use this coordinator agent to analyze CRAV tender specifications (Telemedicina/FSE PNRR) and verify GDPR/CDPA, HIPAA exclusion, and ACN Data Region Europe compliance.",
                "instruction": (
                    "CRITICAL: Your internal reasoning is in English, but your final output MUST be in formal Italian.\n"
                    "You are the Phase 1 Coordinator for CRAV Tenders and Regulatory Compliance at Azienda Zero (Regione del Veneto).\n"
                    "Delegate and coordinate your two specialist sub-agents:\n"
                    "- Use 'Specialista Capitolati CRAV e Architettura PSN' to extract tender evaluation criteria (70/30 quality/price, 42/70 threshold), SLA (99.95%, RPO 15m, RTO 60m), and GCP/PSN hybrid architecture (HAProxy, Cloud SQL, Cloud Interconnect to Oracle PSN, CTI 116117);\n"
                    "- Use 'Specialista Privacy GDPR CDPA e Qualifica ACN' to verify art. 28 GDPR CDPA validity, US HIPAA art. 3.3(viii) non-applicability to EU citizens under GDPR, and ACN Data Region Europe (storage + processing)."
                ),
                "subAgentIds": ["spec_gare_crav", "spec_privacy_acn"],
                "dataStoreSpecs": ds_spec,
            },
        },
        {
            "id": "spec_gare_crav",
            "displayName": "Specialista Capitolati CRAV e Architettura PSN",
            "llmAgentNode": {
                "model": "gemini-3.8-flash",
                "description": "Use this specialist agent to retrieve CRAV tender requirements, PNRR Telemedicina SLAs, and GCP/PSN architecture details from the Azienda Zero connector.",
                "instruction": (
                    "CRITICAL: Your internal reasoning is in English, but your final output MUST be in formal Italian.\n"
                    "Ground your answer strictly on '01_Capitolato_CRAV_Telemedicina_FSE_PNRR_Veneto_2026.html' and '04_Architettura_Infrastruttura_GCP_PSN_CTI_116_117.html'.\n"
                    "Always cite the document title and report exact SLA thresholds (99.95%, RPO 15 min, RTO 60 min), scoring rules (70 technical / 30 economic, 42/70 minimum threshold), and the 3-workload GCP/PSN architecture with CTI 116117."
                ),
                "subAgentIds": [],
                "dataStoreSpecs": ds_spec,
            },
        },
        {
            "id": "spec_privacy_acn",
            "displayName": "Specialista Privacy GDPR CDPA e Qualifica ACN",
            "llmAgentNode": {
                "model": "gemini-3.8-flash",
                "description": "Use this specialist agent to verify GDPR art. 28 CDPA, HIPAA clause non-applicability, and ACN Data Region Europe requirements.",
                "instruction": (
                    "CRITICAL: Your internal reasoning is in English, but your final output MUST be in formal Italian.\n"
                    "Ground your answer strictly on '03_Direttiva_Privacy_GDPR_CDPA_ACN_Data_Region_Europe.html'.\n"
                    "Clearly explain: 1) Standard CDPA governs Data Processor appointment under Art. 28 GDPR; 2) Art. 3.3(viii) HIPAA restriction applies ONLY to US HIPAA entities and does NOT restrict EU healthcare data under GDPR; 3) Data Region = Europe guarantees storage and processing in EU for ACN QC2 compliance."
                ),
                "subAgentIds": [],
                "dataStoreSpecs": ds_spec,
            },
        },
        {
            "id": "coord_pdta_atti",
            "displayName": "Fase 2 - Monitoraggio PDTA 9 ULSS e Atti CRAV",
            "llmAgentNode": {
                "model": "gemini-3.8-flash",
                "description": "Use this coordinator agent to benchmark PDTA KPIs across the 9 Veneto ULSS, trigger SLA escalation protocols, and draft 6-section CRAV administrative determinations.",
                "instruction": (
                    "CRITICAL: Your internal reasoning is in English, but your final output MUST be in formal Italian.\n"
                    "You are the Phase 2 Coordinator for Clinical PDTA Monitoring and Administrative Acts at Azienda Zero.\n"
                    "Delegate and coordinate your specialist sub-agents:\n"
                    "- Use 'Analista PDTA Regionali e KPI 9 ULSS Venete' to analyze patient volumes, COT status, and Time-to-Treatment (<=30 days target) across ULSS 1-9 and IOV;\n"
                    "- Use 'Redattore Determine Dirigenziali CRAV' to draft formal 6-section CRAV determinations (MOD-DET-CRAV-AZERO-2026) and format any cloud sizing tables in monthly USD ($/mo)."
                ),
                "subAgentIds": phase2_sub_agents,
                "dataStoreSpecs": ds_spec,
            },
        },
        {
            "id": "spec_pdta_ulss",
            "displayName": "Analista PDTA Regionali e KPI 9 ULSS Venete",
            "llmAgentNode": {
                "model": "gemini-3.8-flash",
                "description": "Use this specialist agent to compare PDTA Time-to-Treatment, COT activation, and Telemedicina KPIs across the 9 ULSS of Veneto and IOV.",
                "instruction": (
                    "CRITICAL: Your internal reasoning is in English, but your final output MUST be in formal Italian.\n"
                    "Ground your answer strictly on '02_Linee_Guida_PDTA_Oncologia_Cronicita_ULSS_Veneto.html' and '05_Matrice_Fabbisogni_ICT_e_KPI_9_ULSS_Regione_Veneto.html'.\n"
                    "Highlight ULSS 9 Scaligera (31 days -> ALLERTA_SLA) and ULSS 7 Pedemontana (29 days -> ATTENZIONE_SOGLIA) and detail the 3-step escalation protocol with IOV Padova and AOUI Verona."
                ),
                "subAgentIds": [],
                "dataStoreSpecs": ds_spec,
            },
        },
        {
            "id": "spec_determine_crav",
            "displayName": "Redattore Determine Dirigenziali CRAV",
            "llmAgentNode": {
                "model": "gemini-3.8-flash",
                "description": "Use this specialist agent to draft 6-section administrative determinations (MOD-DET-CRAV-AZERO-2026) for Azienda Zero.",
                "instruction": (
                    "CRITICAL: Your internal reasoning is in English, but your final output MUST be in formal Italian.\n"
                    "Ground your answer strictly on '06_Template_Determina_Indizione_Gara_CRAV_Azienda_Zero.html' and '05_Matrice_Fabbisogni_ICT_e_KPI_9_ULSS_Regione_Veneto.html'.\n"
                    "Always structure the administrative act in the 6 official sections and keep all monthly cloud costs in USD ($/mo) with List, 1Y CUD, 3Y CUD, OS $/mo (only for supported OS) and separate MSSQL license $/mo (only for supported DB on supported OS)."
                ),
                "subAgentIds": [],
                "dataStoreSpecs": ds_spec,
            },
        },
    ]

    if adk_agent_resource:
        nodes.append(
            {
                "id": "ref_adk_azero",
                "displayName": "Azienda Zero Governance & Sizing Multi-Agent (ADK)",
                "referencedAdkAgentNode": {
                    "sourceAgent": adk_agent_resource,
                    "sourceAgentName": adk_agent_resource,
                },
            }
        )

    starter_prompts = [
        {"text": "Verifica nel Connettore Azienda Zero i criteri di aggiudicazione e gli SLA del Capitolato CRAV Telemedicina/FSE 2.0 e la conformità GDPR/CDPA e ACN Data Region Europe."},
        {"text": "Confronta i KPI PDTA e lo stato delle COT delle 9 ULSS del Veneto (evidenziando chi supera i 30 giorni di Time-to-Treatment) e proponi il piano di riequilibrio con lo IOV."},
        {"text": "Redigi nelle 6 sezioni ufficiali (MOD-DET-CRAV-AZERO-2026) la bozza di Determina Dirigenziale CRAV per l'attivazione della Telemedicina su ULSS 6 Euganea e ULSS 2 Marca Trevigiana."},
    ]
    chat_payload = {
        "displayName": chat_display_name,
        "description": "Assistente Multi-Livello (Gemini 3.8 Flash) collegato al Connettore Documentale Azienda Zero Veneto per Gare CRAV, PDTA 9 ULSS e Compliance GDPR/ACN.",
        "starterPrompts": starter_prompts,
        "lowCodeAgentDefinition": {
            "draftDisplayName": chat_display_name,
            "draftDescription": "Assistente Multi-Livello (Gemini 3.8 Flash) collegato al Connettore Documentale Azienda Zero Veneto per Gare CRAV, PDTA 9 ULSS e Compliance GDPR/ACN.",
            "draftStarterPrompts": starter_prompts,
            "rootAgentId": "root_agent",
            "nodes": nodes,
            "deployedRootAgentId": "root_agent",
            "deployedNodes": nodes,
        },
        "sharingConfig": {"scope": "ALL_USERS"},
    }
    st_ch, resp_ch = api_request("POST", agents_url, token, project_id, chat_payload)
    if st_ch == 200 and isinstance(resp_ch, dict):
        ch_name = resp_ch["name"]
        api_request("POST", f"https://discoveryengine.googleapis.com/v1alpha/{ch_name}:deployLowCode", token, project_id, {"name": ch_name})
        api_request("POST", f"https://discoveryengine.googleapis.com/v1alpha/{ch_name}:requestAgentReview", token, project_id, {})
        api_request("PATCH", f"https://discoveryengine.googleapis.com/v1alpha/{ch_name}?updateMask=sharingConfig", token, project_id, {"sharingConfig": {"scope": "ALL_USERS"}})
        print(f"  -> [{engine_id} | Chat Agent Multi-Livello] Creato, deployato e condiviso `{chat_display_name}` ({ch_name}).")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reasoning-engine", default=os.environ.get("REASONING_ENGINE_RES", ""))
    args = parser.parse_args()

    project_id = _detect_project_id()
    project_number = _detect_project_number(project_id)
    token = get_token()
    engine_ids = discover_target_engines(project_id, token)
    re_res = args.reasoning_engine.strip() or discover_deployed_azero_re(project_id, token)

    print(f"=== Pubblicazione Agente GE App & Skills Azienda Zero su `{project_id}` (Engines: {engine_ids}) ===")
    for eid in engine_ids:
        publish_on_engine(project_id, project_number, eid, token, re_res)


if __name__ == "__main__":
    main()
