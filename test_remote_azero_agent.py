#!/usr/bin/env python3
"""
Test end-to-end del Multi-Agente a Grafo `azienda_zero_agent` deployato su Vertex AI Agent Engine (`rootprj-377111`).
Mostra in tempo reale i passaggi tra i sub-agenti (`transfer_to_agent`) e le invocazioni dei tool,
generando gli span gerarchici su Cloud Trace e i log strutturati su Cloud Logging.
"""

import json
import os
import vertexai
from vertexai import agent_engines

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "rootprj-377111")
REGION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")


def load_resource_name() -> str:
    if os.path.exists("deployment_metadata_azero.json"):
        with open("deployment_metadata_azero.json", "r", encoding="utf-8") as f:
            return json.load(f)["remote_agent_runtime_id"]
    if os.path.exists("DEPLOYED_AZERO_AGENT.txt"):
        with open("DEPLOYED_AZERO_AGENT.txt", "r", encoding="utf-8") as f:
            return f.read().strip()
    raise FileNotFoundError("Esegui prima `python3 deploy_azero_adk.py`.")


def main():
    resource_name = load_resource_name()
    print(f"🔗 Connessione al Multi-Agente Azienda Zero su Agent Engine: {resource_name}")
    vertexai.init(project=PROJECT_ID, location=REGION)
    remote_agent = agent_engines.get(resource_name)

    session = remote_agent.create_session(user_id="demo-azero-beltrami")
    session_id = session["id"] if isinstance(session, dict) else session.id
    print(f"✅ Sessione remota creata: {session_id}\n")

    test_prompts = [
        (
            "Test 1 — Sub-Agent PDTA & KPI 9 ULSS (`ulss_pdta_kpi_agent`)",
            "Analizza i KPI PDTA, le COT attive e i pazienti in Telemedicina per l'ULSS 6 Euganea e l'ULSS 9 Scaligera, e verifica quali ULSS del Veneto superano i 30 giorni sul Time-to-Treatment.",
        ),
        (
            "Test 2 — Sub-Agent Gare CRAV & Compliance ACN/GDPR (`crav_compliance_agent`)",
            "Verifica per l'Ufficio Privacy e per il capitolato CRAV Telemedicina di Azienda Zero come sono regolati il CDPA sotto GDPR, la clausola USA HIPAA (art. 3.3 viii ToS), la Data Region Europe per ACN e i punteggi/SLA di gara.",
        ),
        (
            "Test 3 — Sub-Agent Sizing Cloud/PSN in USD (`psn_cloud_sizing_agent`)",
            "Calcola il sizing mensile in USD ($/mo con List, 1Y CUD, 3Y CUD, OS $/mo e licenza MSSQL in colonna separata) per l'ULSS 6 Euganea: 1) Cluster-Referti-ULSS6 composto da 2 VM da 8 vCPU e 32 GiB RAM con Windows Server 2022 e SQL Server 2022 Standard; 2) VM-Legacy-ULSS6 composta da 1 VM da 8 vCPU e 32 GiB RAM con Windows Server 2012 R2 e SQL Server 2012.",
        ),
    ]

    for title, prompt in test_prompts:
        print("=" * 88)
        print(f"▶ {title}")
        print(f"Prompt: {prompt}")
        print("-" * 88)
        for event in remote_agent.stream_query(
            user_id="demo-azero-beltrami",
            session_id=session_id,
            message=prompt,
        ):
            if isinstance(event, dict):
                author = event.get("author", "agent")
                content = event.get("content", {})
                for part in content.get("parts", []):
                    if "function_call" in part:
                        fc = part["function_call"]
                        print(f"  🔀 [Graph Node: {author}] -> 🛠️ {fc.get('name')}({fc.get('args')})")
                    if "text" in part and part["text"].strip():
                        print(f"\n🤖 [{author}]:\n{part['text'].strip()}\n")


if __name__ == "__main__":
    main()
