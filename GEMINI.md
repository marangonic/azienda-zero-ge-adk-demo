# Antigravity Workspace — Demo Azienda Zero (Regione del Veneto) su `rootprj-377111`

Questo workspace è pre-configurato per la demo live da **Google Antigravity** collegato al progetto GCP **`rootprj-377111`** (`us-central1` per Vertex AI Agent Engine e `global` per Gemini Enterprise App).

## 🎯 Obiettivo della Demo (4 Atti)
1. **ATTO 1 — Gemini Enterprise App + Connettore GCS (`azero-crav-pdta-ds`)**:
   - Creazione/verifica del Connettore Cloud Storage (`gs://rootprj-377111-azienda-zero-veneto/documenti_azero/*.html`) con 6 documenti ufficiali di Azienda Zero (Gare CRAV Telemedicina/FSE PNRR, PDTA Regionali ULSS 1–9, Direttiva Privacy GDPR/CDPA/ACN Data Region Europe, Architettura GCP su PSN e CTI 116117, Matrice Fabbisogni 9 ULSS, Template Determina CRAV).
   - Generazione e pubblicazione da Antigravity dell'agente multi-livello **`Assistente Governance CRAV e PDTA Azienda Zero`** (modello `gemini-3.8-flash`) e delle **3 Skills** dentro Gemini Enterprise App (`azero-governance-app`).
2. **ATTO 2 — Agente Multi-Agente ADK (`azienda_zero_agent`) in Locale (`adk web`) e Topologia Graph**:
   - Architettura Multi-Agente a Grafo (`azero_orchestrator` -> 3 Sub-Agenti specialistici `ulss_pdta_kpi_agent`, `crav_compliance_acn_agent`, `psn_cloud_sizing_agent` + pipeline `azero_full_audit_pipeline`).
   - Avvio di `adk web --port 8080` per mostrare nel tab **Graph / Topology** come l'orchestratore delega il lavoro ai nodi del grafo e aggiorna lo stato condiviso (`tool_context.state`).
3. **ATTO 3 — Valutazione (Eval) Locale su `adk web` e CLI (`run_local_eval.py`)**:
   - Esecuzione dell'Eval Set `azienda_zero_agent/azienda_zero_eval.evalset.json` nel tab **Eval** di `adk web` (o via `python3 run_local_eval.py`) per validare la **traiettoria sul grafo** (`tool_trajectory_avg_score`) e la qualità della risposta (`response_match_score`).
4. **ATTO 4 — Deploy in Cloud (Vertex AI Agent Engine + Agent Registry A2A) ed Eval in Cloud (`run_cloud_eval.py`)**:
   - Deploy del multi-agente su **Vertex AI Agent Engine** (`rootprj-377111`, `us-central1`) con OpenTelemetry (`Cloud Trace` & `Cloud Logging`) e registrazione in **Agent Registry** (`A2A Agent Card`).
   - Ripetizione della stessa valutazione in Cloud contro il `ReasoningEngine` remoto (`python3 run_cloud_eval.py`) con report comparativo **Locale vs Cloud** (`artifacts/EVAL_COMPARISON_LOCAL_VS_CLOUD.md` e `artifacts/eval_report_cloud.html`).

---

## 💰 Regola Tassativa di Pricing & Sizing (Mandatory Rule)
Ogni volta che generi tabelle di costo, preventivi o tool di sizing (sia in chat, sia negli agenti ADK/MCP):
- Mantieni tutti i prezzi **sempre in dollari (`$ USD`) su base mensile (`Prezzo Mese`)**, inserendo sempre le colonne dedicate:
  - **Prezzo Mese List (`$/mo`)**
  - **Prezzo Mese 1Y CUD (`$/mo`)**
  - **Prezzo Mese 3Y CUD (`$/mo`)**
- Per le **VM con sistema operativo**, esponi sempre il **Costo Mese con Sistema Operativo (`OS $/mo` e `Totale con OS $/mo`)** fornendo il costo licenza OS (`Windows Server`, `RHEL`, ecc.) **solo per gli OS supportati** (escludendo il costo licenza per gli OS fuori supporto / End-of-Support).
- Per i database **MS SQL Server**, fornisci il costo licenza in una **colonna separata (`COSTO MESE LICENZA MSSQL $/MO`)** **solo per le istanze supportate su OS supportato** (non fornire il costo licenza DB se il DB è fuori supporto o se l'OS sottostante è fuori supporto).

---

## 🛠️ Skills & MCP Server Attivi in questo Workspace
- **Skills (`.agent/skills/`)**:
  - `ge-app-azero-builder`: Progetta e pubblica agenti No-Code/Low-Code e Connettori in Gemini Enterprise App (`rootprj-377111`).
  - `adk-multiagent-graph-builder`: Sviluppa, avvia in `adk web` (con Graph Topology) e distribuisce su Vertex AI Agent Engine + Agent Registry il multi-agente `azienda_zero_agent`.
  - `adk-eval-local-and-cloud`: Esegue e confronta le valutazioni (`Eval`) della traiettoria sul grafo sia in locale (`adk web` / `run_local_eval.py`) sia in Cloud (`run_cloud_eval.py`).
- **MCP Server Locale (`mcp_servers/azero_crav_mcp_server.py`)**:
  - Server MCP stdio (`azero-crav-governance-mcp`) configurato in `.agent/mcp_config.json` e `.gemini/settings.json` con tool live per interrogare i KPI delle 9 ULSS venete, la compliance ACN/GDPR e il calcolatore di sizing GCP/PSN in `$ USD/mo`.
