# 🎬 Playbook & Regia Live Demo — Azienda Zero (Regione del Veneto)
### 💻 Antigravity (sul tuo PC) + ☁️ Google Cloud Shell + 🌐 Console GCP (`rootprj-377111`)

> **Partecipanti:** Ing. Claudio Beltrami (Azienda Zero), Luca Maculan (Miriade), Andrea Fogazzaro, Christian Marangoni  
> **Progetto GCP:** **`rootprj-377111`** (`global` per Gemini Enterprise App, `us-central1` per Vertex AI Agent Engine)  
> **Divisione degli Ambienti durante la Demo:**
> - 💻 **Sul tuo PC (Antigravity):** mostri Rules, Skills, Server MCP locale, generi/ispezioni le istruzioni dell'agente GE App e il codice Python del Multi-Agente ADK a Grafo + EvalSet.
> - ☁️ **In Google Cloud Shell (`rootprj-377111`):** esegui `adk web --port 8080 --allow_origins "*"` (aprendo **Web Preview -> Port 8080** per mostrare il **Graph / Topology** e il tab **Eval**) e lanci gli script di provisioning/deploy/eval.
> - 🌐 **In Console GCP & Web App Gemini Enterprise:** mostri il Connettore `azero-crav-pdta-ds`, il Chat Agent GE App, il Playground di Agent Engine, Cloud Trace e Agent Registry (A2A).

---

## ⚡ Setup 1-Click Pre-Demo (5 minuti prima della call)

### 1. In Google Cloud Shell (progetto `rootprj-377111`)
Apri [Google Cloud Shell su `rootprj-377111`](https://console.cloud.google.com/?cloudshell=true&project=rootprj-377111) e incolla questo singolo comando:

```bash
git clone https://github.com/marangonic/azienda-zero-ge-adk-demo.git ~/azero_demo && cd ~/azero_demo && ./setup_cloudshell_azero.sh --with-adk
```
**Cosa fa in automatico questo comando in Cloud Shell:**
1. Crea l'ambiente `.venv` con `google-adk` e `google-cloud-aiplatform[agent_engines,adk,evaluation]`.
2. Crea il bucket `gs://rootprj-377111-azienda-zero-veneto`, carica i **6 documenti HTML ufficiali** di Azienda Zero e li indicizza in **2 secondi** nel Connettore Data Store **`azero-crav-pdta-ds`**.
3. Effettua il deploy del Multi-Agente a Grafo **`azienda_zero_agent`** su **Vertex AI Agent Engine** (`us-central1`) con OpenTelemetry attivo e lo registra con **A2A Agent Card** in **Agent Registry**.
4. Pubblica le **3 Skills** e il Chat Agent Multi-Livello **`Assistente Governance CRAV e PDTA Azienda Zero`** (`gemini-3.8-flash`) in **Gemini Enterprise App**.
5. Esegue la valutazione preliminare Locale e Cloud e **avvia automaticamente `adk web --port 8080 --allow_origins "*"`** lasciandolo pronto per il **Web Preview (porta 8080)**!

### 2. Sul tuo PC (in Google Antigravity)
Clona la stessa repository sul tuo PC e aprila come workspace in **Antigravity**:
```bash
git clone https://github.com/marangonic/azienda-zero-ge-adk-demo.git
```

---

## 🟢 ATTO 1 — Da Antigravity (PC) a Gemini Enterprise App con Connettore (`azero-crav-pdta-ds`) (10–12 min)

### Step 1.1 — In Antigravity (sul tuo PC): Mostra Skills, Rules, MCP e genera l'Agente GE App
1. Fai vedere nel file explorer di Antigravity come il workspace di Azienda Zero è strutturato con:
   - **Rules** (`.agent/rules/01-azienda-zero-context.md` e `02-ge-app-dolphin-adk.md`)
   - **Skills** (`.agent/skills/ge-app-azero-builder/SKILL.md`, `adk-multiagent-graph-builder`, `adk-eval-local-and-cloud`)
   - **Server MCP locale** (`mcp_servers/azero_crav_mcp_server.py`)
2. Nella chat di **Antigravity sul PC**, incolla questo prompt:
   ```text
   Usa il tool MCP azero_check_acn_gdpr_compliance e la skill ge-app-azero-builder per mostrarmi l'architettura e i System Prompt Dolphin ADK dell'agente multi-livello "Assistente Governance CRAV e PDTA Azienda Zero" (in artifacts/GE_APP_AGENT_INSTRUCTIONS_AZERO.md) collegato al Connettore azero-crav-pdta-ds, e dammi il comando Cloud Shell per pubblicarlo su Gemini Enterprise App.
   ```
3. Antigravity interroga il server MCP locale, apre/mostra [`artifacts/GE_APP_AGENT_INSTRUCTIONS_AZERO.md`](./artifacts/GE_APP_AGENT_INSTRUCTIONS_AZERO.md) (con i prompt strutturati secondo le best practice Dolphin ADK: *internal reasoning in English, final output in formal Italian*, modello `gemini-3.8-flash`, 4 sub-agenti specialistici) e mostra come `register_azero_ge_agent.py` lo pubblica via API.

### Step 1.2 — Nel Browser (Gemini Enterprise Web App + Console): Mostra Connettore e Agente Live
1. In **Google Cloud Console -> Gemini Enterprise -> Data Stores**, mostra il Connettore **`azero-crav-pdta-ds`** con i 6 documenti di Azienda Zero indicizzati.
2. Apri la **Web App di Gemini Enterprise** (l'URL stampato in Cloud Shell in `WEB_APP_URL_AZERO.txt`):
   - Mostra le **3 Skills** nella sezione *Skills* (`/r/skills`).
   - Apri **`Assistente Governance CRAV e PDTA Azienda Zero`** in *Agent Builder* (mostrando il grafo visuale No-Code a 2 fasi) e invia questo prompt:
     ```text
     Verifica nei documenti del Connettore Azienda Zero come sono regolati la nomina a Responsabile del Trattamento (CDPA sotto GDPR), l'inapplicabilità della clausola USA HIPAA (art. 3.3 viii ToS) ai dati sanitari europei e il requisito ACN Data Region Europe, e riassumi i punteggi (70/30) e gli SLA (99,95%) del Capitolato CRAV Telemedicina.
     ```

---

## 🔵 ATTO 2 — Da Antigravity (PC) a `adk web` in Cloud Shell con Vista Topology / Graph (12–15 min)

### Step 2.1 — In Antigravity (sul tuo PC): Mostra il Codice del Multi-Agente a Grafo
1. Nella chat di **Antigravity sul PC**, incolla questo prompt:
   ```text
   Usa la skill adk-multiagent-graph-builder per spiegarmi come è costruita la topologia a grafo del multi-agente in azienda_zero_agent/agent.py e azienda_zero_agent/tools.py (con azero_orchestrator e i 3 sub-agenti ulss_pdta_kpi_agent, crav_compliance_agent, psn_cloud_sizing_agent) e testa subito con il tool MCP azero_calculate_cloud_sizing_usd il calcolo per 2 VM Windows Server 2022 + SQL Server 2022 Standard da 8 vCPU e 32 GiB RAM.
   ```
2. Mostra in Antigravity [`azienda_zero_agent/agent.py`](./azienda_zero_agent/agent.py): evidenzia come `root_agent` (`azero_orchestrator`) dichiara `sub_agents=[ulss_pdta_kpi_agent, crav_compliance_agent, psn_cloud_sizing_agent]` e le 6 callback di osservabilità (`callbacks.py`).

### Step 2.2 — In Cloud Shell (`Web Preview -> Port 8080`): Interrogazione in `adk web` e Vista `Graph`
1. Passa alla scheda di **Google Cloud Shell** dove è attivo `adk web --port 8080 --allow_origins "*"` (se l'avevi fermato, rilancialo con `./run_local_adk_web.sh`).
2. Clicca sull'icona **Web Preview** in alto a destra in Cloud Shell $\rightarrow$ **Preview on port 8080**.
3. Nell'interfaccia di **`adk web`**:
   - Seleziona **`azienda_zero_agent`** dal menu a tendina in alto a sinistra.
   - Clicca sul tab **Graph** (Topology): mostra a Beltrami e Maculan il grafo visuale con **`azero_orchestrator`** al centro e i 3 nodi sub-agente (**`ulss_pdta_kpi_agent`**, **`crav_compliance_agent`**, **`psn_cloud_sizing_agent`**) + i rispettivi tool.
   - Incolla nella chat di `adk web` questo prompt che attraversa più nodi del grafo:
     ```text
     Dobbiamo preparare l'istruttoria per l'ULSS 6 Euganea e l'ULSS 9 Scaligera:
     1) Controlla i KPI PDTA e verifica se ci sono sforamenti della soglia SLA di 30 giorni sul Time-to-Treatment;
     2) Calcola il sizing mensile in USD ($/mo con List, 1Y CUD, 3Y CUD, OS $/mo e licenza MSSQL in colonna separata) per l'ULSS 6 Euganea: 2 VM da 8 vCPU e 32 GiB RAM con Windows Server 2022 e SQL Server 2022 Standard (Cluster-Referti-ULSS6) più 1 VM legacy da 8 vCPU e 32 GiB RAM con Windows Server 2012 R2 e SQL Server 2012 (VM-Legacy-ULSS6).
     ```
   - **Cosa far notare nel Graph di `adk web`**:
     - I nodi del grafo **si illuminano di verde in tempo reale** mentre `azero_orchestrator` invoca `transfer_to_agent` verso `ulss_pdta_kpi_agent` e poi verso `psn_cloud_sizing_agent`.
     - Nel tab **State** di `adk web`, mostra `graph_execution_trace` con la sequenza esatta dei nodi visitati.
     - Nella risposta finale, mostra la tabella in `$ USD/mo` che calcola `List`, `1Y CUD`, `3Y CUD`, `OS $/mo` e `COSTO MESE LICENZA MSSQL $/MO` per le VM supportate ed **esclude automaticamente il costo licenza OS e DB** per la VM `Windows Server 2012 R2 / SQL Server 2012` fuori supporto.

---

## 🟣 ATTO 3 — Valutazione (Eval) in Locale su `adk web` (in Cloud Shell) (8–10 min)

### Step 3.1 — In Antigravity (PC): Ispeziona l'Eval Set (`azienda_zero_eval.evalset.json`)
In Antigravity apri [`azienda_zero_agent/azienda_zero_eval.evalset.json`](./azienda_zero_agent/azienda_zero_eval.evalset.json) e mostra come sono definiti i 4 test case con la **traiettoria attesa sul grafo** (`intermediate_data.tool_uses`: `transfer_to_agent` $\rightarrow$ `ulss_pdta_kpi_agent` / `crav_compliance_agent` / `psn_cloud_sizing_agent` $\rightarrow$ tool specifici).

### Step 3.2 — In `adk web` (Cloud Shell Web Preview Porta 8080): Esecuzione nel Tab `Eval`
1. Nella UI di **`adk web`**, clicca sulla scheda **Eval** nella barra laterale sinistra.
2. Seleziona l'Eval Set **`azienda_zero_eval`**.
3. Seleziona i 4 test case e clicca **Run Evaluation**:
   - Mostra in diretta i risultati **Pass** con le metriche **`tool_trajectory_avg_score`** (verifica che l'agente abbia seguito esattamente il percorso atteso nel grafo) e **`response_match_score`**.
4. *(Opzionale da terminale Cloud Shell)* Se vuoi generare anche il file JSON/HTML locale da CLI in Cloud Shell:
   ```bash
   cd ~/azero_demo && source .venv/bin/activate && python3 run_local_eval.py
   ```

---

## 🟠 ATTO 4 — Deploy in Cloud (Agent Engine + Agent Registry A2A) & Ripetizione Eval in Cloud (10–12 min)

### Step 4.1 — In Cloud Shell & Console GCP: Deploy e Verifica in Cloud (Playground, Trace, Agent Registry)
1. In **Cloud Shell**, mostra lo script [`deploy_azero_adk.py`](./deploy_azero_adk.py) (già eseguito nel pre-setup, o lancia un test live sull'agente remoto in Cloud):
   ```bash
   cd ~/azero_demo && source .venv/bin/activate && python3 test_remote_azero_agent.py
   ```
2. In **Google Cloud Console (`rootprj-377111`)**:
   - Apri **Vertex AI -> Agent Engine -> `Azienda Zero Governance & Sizing Multi-Agent` -> Playground**: fai una domanda live nel Playground Cloud.
   - Apri **Cloud Trace Explorer**: mostra gli span OpenTelemetry gerarchici (`invocation` $\rightarrow$ `agent_run [azero_orchestrator]` $\rightarrow$ `execute_tool [transfer_to_agent]` $\rightarrow$ `agent_run [ulss_pdta_kpi_agent]`) che riproducono in Cloud la topologia del grafo vista in `adk web`.
   - Apri **Vertex AI -> Agent Registry**: mostra l'agente registrato con protocollo **`A2A (0.3.0)`** e le 3 skills A2A.

### Step 4.2 — In Cloud Shell: Ripetizione della Valutazione (Eval) in Cloud (`run_cloud_eval.py`)
1. Apri un secondo tab nel terminale di **Google Cloud Shell** e lancia la valutazione contro il `ReasoningEngine` deployato in Cloud:
   ```bash
   cd ~/azero_demo && source .venv/bin/activate && python3 run_cloud_eval.py
   ```
2. Lo script interroga in streaming il Multi-Agente deployato su **Vertex AI Agent Engine**, ricostruisce per ciascuno dei 4 casi i nodi del grafo attraversati in Cloud (`actual_graph_nodes`) e i tool invocati (`actual_tools`), calcola il **Cloud Graph Trajectory Score** e il **Cloud Rubric Score**, e aggiorna la tabella comparativa **Locale (`adk web`) vs Cloud (`Vertex AI Agent Engine`)** in:
   - 📄 [`artifacts/EVAL_COMPARISON_LOCAL_VS_CLOUD.md`](./artifacts/EVAL_COMPARISON_LOCAL_VS_CLOUD.md)
   - 🌐 [`artifacts/eval_report_comparison.html`](./artifacts/eval_report_comparison.html)
3. Per mostrare la dashboard HTML comparativa direttamente dal browser in Cloud Shell:
   ```bash
   python3 -m http.server 8081 --directory artifacts
   ```
   *(e clicca **Web Preview -> Change port -> 8081 -> `eval_report_comparison.html`**, oppure aprila direttamente in **Antigravity sul tuo PC**!)*.
