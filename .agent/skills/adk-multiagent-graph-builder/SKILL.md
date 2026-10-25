---
name: adk-multiagent-graph-builder
description: Sviluppa, avvia in locale con adk web (mostrando la vista Topology / Graph dei sub-agenti) e distribuisce in Cloud su Vertex AI Agent Engine e Agent Registry (A2A) il sistema multi-agente ADK azienda_zero_agent sul progetto rootprj-377111.
---

# Skill: ADK Multi-Agent Graph Builder & Cloud Deployer (`azienda_zero_agent` su `rootprj-377111`)

Usa questa skill quando l'utente chiede in Antigravity di:
- Creare, modificare o spiegare l'architettura del **Multi-Agente ADK `azienda_zero_agent`**.
- Avviare **`adk web`** in locale sul PC per mostrare la conversazione e la **Topology / Graph View** con l'illuminazione in tempo reale dei nodi del grafo.
- Eseguire il **deploy in Cloud** su **Vertex AI Agent Engine** (`rootprj-377111`, `us-central1`) con OpenTelemetry (`Cloud Trace` & `Cloud Logging`) e registrare l'agente con protocollo **A2A** in **Agent Registry**.

## 1. Topologia del Grafo Multi-Agente (`azienda_zero_agent/agent.py`)
Il package `azienda_zero_agent` espone `root_agent` (`azero_orchestrator`) strutturato come grafo multi-agente gerarchico con `sub_agents` + tool specialistici, progettato specificamente per rendere visibile nella scheda **Graph / Topology** di `adk web` il flusso di delega:

```text
                       ┌──────────────────────────────┐
                       │      azero_orchestrator      │
                       │   (Root LlmAgent - Gemini)   │
                       └──────────────┬───────────────┘
            ┌─────────────────────────┼─────────────────────────┐
            ▼                         ▼                         ▼
┌───────────────────────┐ ┌───────────────────────┐ ┌───────────────────────┐
│  ulss_pdta_kpi_agent  │ │crav_compliance_agent  │ │ psn_cloud_sizing_agent│
│  (Sub-Agent PDTA/ULSS)│ │ (Sub-Agent CRAV/ACN)  │ │(Sub-Agent Sizing USD) │
└───────────┬───────────┘ └───────────┬───────────┘ └───────────┬───────────┘
            │                         │                         │
  • query_ulss_pdta_kpi     • verify_acn_gdpr_rules   • calculate_vm_mssql_sizing_usd
  • check_pdta_sla_alert    • search_crav_capitolati  • calculate_agent_engine_sizing_usd
```

Inoltre `azero_orchestrator` dispone del tool di telemetria di sessione `get_azero_session_telemetry` per ispezionare lo stato condiviso (`tool_context.state`) accumulato dai vari nodi del grafo.

## 2. Esecuzione Locale dal PC con `adk web` (Vista Graph / Topology)
Per avviare l'interfaccia web locale di ADK dal terminale di Antigravity:
```bash
./run_local_adk_web.sh
```
*(Oppure direttamente)*:
```bash
export GOOGLE_GENAI_USE_VERTEXAI=TRUE
export GOOGLE_CLOUD_PROJECT=rootprj-377111
export GOOGLE_CLOUD_LOCATION=us-central1
adk web --port 8080 --allow_origins "*"
```
1. Apri `http://localhost:8080` nel browser (o nel preview pane di Antigravity).
2. Seleziona **`azienda_zero_agent`** dal menu a tendina in alto a sinistra.
3. Clicca sul tab **Graph** (o **Events** / **Trace**) per mostrare la **topologia a grafo** con `azero_orchestrator` collegato ai 3 sub-agenti (`ulss_pdta_kpi_agent`, `crav_compliance_agent`, `psn_cloud_sizing_agent`) e ai rispettivi tool.
4. Invia il prompt multi-agente di demo:
   > *"Per l'attivazione della piattaforma di Telemedicina e FSE sull'ULSS 6 Euganea e sull'ULSS 2 Marca Trevigiana: 1) verifica i KPI PDTA e lo stato delle COT nelle due ULSS, 2) controlla i requisiti di compliance GDPR/CDPA e ACN Data Region Europe per il capitolato CRAV, e 3) calcola il sizing mensile in USD (List, 1Y CUD, 3Y CUD, OS e licenza MSSQL separata) per 2 VM e2-standard-8 con Windows Server 2022 e SQL Server 2022 Standard più 1 VM legacy con Windows Server 2012 R2."*

## 3. Deploy in Cloud su Vertex AI Agent Engine + Agent Registry (A2A)
Per distribuire il multi-agente su `rootprj-377111` (`us-central1`):
```bash
python3 deploy_azero_adk.py
```
Cosa esegue:
1. Incapsula `root_agent` in `AdkApp(agent=root_agent, enable_tracing=True)` con `GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY=true`.
2. Crea il `ReasoningEngine` su Vertex AI Agent Engine (`rootprj-377111`, `us-central1`) e salva gli ID in `deployment_metadata_azero.json` e `DEPLOYED_AZERO_AGENT.txt`.
3. Inietta la `a2a_agent_card` (`spec.agentCard`) e registra il servizio A2A `azero-governance-adk-agent` in **Agent Registry** (`us-central1` e `global`).
4. Per interrogare da CLI/Antigravity il multi-agente appena deployato in Cloud:
   ```bash
   python3 test_remote_azero_agent.py
   ```
