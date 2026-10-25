# Antigravity Workspace — Demo Azienda Zero (Regione del Veneto) su `rootprj-377111`

Questo workspace è progettato per una **demo ibrida divisa su 3 ambienti complementari**:
1. 💻 **Google Antigravity (sul tuo PC)** — Progettazione agentica assistita da **Rules** (`.agent/rules/`), **Skills** (`.agent/skills/`) e **Server MCP locale** (`azero-crav-governance-mcp`):
   - Creazione e raffinamento delle istruzioni Dolphin ADK per l'agente **Gemini Enterprise App** (`artifacts/GE_APP_AGENT_INSTRUCTIONS_AZERO.md`).
   - Sviluppo, ispezione e spiegazione del codice **Multi-Agente ADK a Grafo** (`azienda_zero_agent/agent.py`, `tools.py`, `callbacks.py`) e dell'**Eval Set** (`azienda_zero_eval.evalset.json`).
   - Interrogazione diretta dei tool MCP di Azienda Zero (KPI 9 ULSS, compliance GDPR/CDPA/ACN, calcolatore sizing USD) dalla chat di Antigravity.
2. ☁️ **Google Cloud Shell (sul progetto `rootprj-377111`)** — Esecuzione di `adk web` e di tutti i comandi CLI/API verso Google Cloud:
   - Setup 1-click (`./setup_cloudshell_azero.sh --with-adk`) per creare il Bucket GCS, il Connettore `azero-crav-pdta-ds` e pubblicare l'agente GE App e le 3 Skills.
   - Esecuzione di **`adk web --port 8080 --allow_origins "*"`** (con **Cloud Shell Web Preview -> Port 8080**) per mostrare il **Graph / Topology** del multi-agente e il tab **Eval**.
   - Esecuzione del deploy su **Vertex AI Agent Engine + Agent Registry A2A** (`python3 deploy_azero_adk.py`) e delle **Valutazioni (Eval)** in Cloud Shell (`python3 run_local_eval.py`) e contro il Cloud (`python3 run_cloud_eval.py`).
3. 🌐 **Google Cloud Console & Gemini Enterprise Web App (`rootprj-377111`)** — Dimostrazione live:
   - **Gemini Enterprise Web App**: Connettore `azero-crav-pdta-ds`, Agent Designer (Visual Builder), 3 Skills e Chat Agent `Assistente Governance CRAV e PDTA Azienda Zero`.
   - **Vertex AI Agent Engine Playground, Cloud Trace & Agent Registry**: test del multi-agente in Cloud, ispezione degli span OpenTelemetry dei sub-agenti e verifica della `A2A Agent Card`.

---

## ⚠️ Regola Operativa per Antigravity sul PC
Quando l'utente ti chiede in Antigravity di creare/modificare l'agente GE App, il multi-agente ADK o l'Eval:
- **Genera, mostra o modifica direttamente i file nel workspace** (`artifacts/GE_APP_AGENT_INSTRUCTIONS_AZERO.md`, `azienda_zero_agent/agent.py`, `azienda_zero_agent/tools.py`, `azienda_zero_agent/azienda_zero_eval.evalset.json`) oppure invoca i tool del **Server MCP locale** (`azero-crav-governance-mcp`).
- **NON tentare di lanciare `adk web` o `gcloud` sul PC locale**: fornisci invece all'utente il blocco comandi pronto da incollare in **Google Cloud Shell** (su `rootprj-377111`)!

---

## 💰 Regola Tassativa di Pricing & Sizing (Mandatory Rule)
Ogni volta che generi tabelle di costo, preventivi o tool di sizing (sia in chat, sia negli agenti ADK/MCP):
- Mantieni tutti i prezzi **sempre in dollari (`$ USD`) su base mensile (`Prezzo Mese`)**, inserendo sempre le colonne dedicate:
  - **Prezzo Mese List (`$/mo`)**
  - **Prezzo Mese 1Y CUD (`$/mo`)**
  - **Prezzo Mese 3Y CUD (`$/mo`)**
- Per le **VM con sistema operativo**, esponi sempre il **Costo Mese con Sistema Operativo (`OS $/mo` e `Totale con OS $/mo`)** fornendo il costo licenza OS (`Windows Server`, `RHEL`, ecc.) **solo per gli OS supportati** (escludendo il costo licenza per gli OS fuori supporto / End-of-Support).
- Per i database **MS SQL Server**, fornisci il costo licenza in una **colonna separata (`COSTO MESE LICENZA MSSQL $/MO`)** **solo per le istanze supportate su OS supportato** (non fornire il costo licenza DB se il DB è fuori supporto o se l'OS sottostante è fuori supporto).
