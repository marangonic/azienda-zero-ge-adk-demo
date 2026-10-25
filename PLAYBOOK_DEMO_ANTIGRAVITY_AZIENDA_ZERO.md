# 🎬 Playbook & Regia Live Demo — Azienda Zero (Regione del Veneto) da Antigravity (`rootprj-377111`)

> **Partecipanti:** Ing. Claudio Beltrami (Azienda Zero), Luca Maculan (Miriade), Andrea Fogazzaro, Christian Marangoni  
> **Ambiente:** Google Antigravity sul tuo PC collegato al progetto GCP **`rootprj-377111`**  
> **Durata stimata:** 45 minuti divisi in **4 Atti**

---

## 🛠️ Preparazione Pre-Demo (5 minuti prima della call)

Sul terminale del tuo PC (dentro la cartella `azienda-zero-ge-adk-demo` aperta in Antigravity):

```bash
# 1. Verifica che il progetto attivo sia rootprj-377111
export GOOGLE_CLOUD_PROJECT=rootprj-377111
export GOOGLE_CLOUD_LOCATION=us-central1
gcloud config set project rootprj-377111

# 2. (Consigliato prima della call) Esegui il provisioning del Connettore GCS + Agente GE App
python3 setup_azero_ge_connector.py
python3 register_azero_ge_agent.py

# 3. (Consigliato prima della call) Fai il deploy dell'Agente Multi-Agente ADK su Agent Engine
#    così durante la demo non devi attendere i 3 minuti di creazione container!
python3 deploy_azero_adk.py
```

---

## 🟢 ATTO 1 — Da Antigravity a Gemini Enterprise App con Connettore Documentale (10–12 min)

### 1. Cosa mostri in Antigravity
Mostra a Claudio Beltrami e Luca Maculan come Antigravity sul tuo PC è configurato con:
- **Rules di progetto** (`.agent/rules/01-azienda-zero-context.md` e `02-ge-app-dolphin-adk.md`) che conoscono la struttura di Azienda Zero (CRAV, 9 ULSS, PDTA, direttive privacy GDPR/CDPA/ACN e regole di pricing USD).
- **Skills specializzate** (`.agent/skills/ge-app-azero-builder/SKILL.md`).
- **Server MCP locale** (`mcp_servers/azero_crav_mcp_server.py`).

### 2. Prompt da scrivere in Antigravity (Atto 1)
Copia e incolla nella chat di Antigravity:
```text
Usa la skill ge-app-azero-builder per configurare sul progetto rootprj-377111 il Connettore Documentale Cloud Storage di Azienda Zero (azero-crav-pdta-ds) con i 6 documenti ufficiali su Gare CRAV, PDTA delle 9 ULSS e Direttiva Privacy GDPR/CDPA/ACN, e pubblica l'agente multi-livello "Assistente Governance CRAV e PDTA Azienda Zero" con le 3 Skills in Gemini Enterprise App.
```
*(In alternativa puoi digitare direttamente `/1-ge-app-connector`)*.

### 3. Cosa mostri nella Web App di Gemini Enterprise
Apri l'URL stampato in `WEB_APP_URL_AZERO.txt`:
1. Mostra il **Connettore Data Store `azero-crav-pdta-ds`** con i 6 documenti di Azienda Zero indicizzati.
2. Apri l'agente **`Assistente Governance CRAV e PDTA Azienda Zero`** (in *Agent Builder* vedranno il grafo No-Code a 2 fasi con i 4 sub-agenti su `gemini-3.8-flash` collegati al Connettore!) e invia questo prompt:
   ```text
   Verifica nei documenti del Connettore Azienda Zero come sono regolati la nomina a Responsabile del Trattamento (CDPA sotto GDPR), l'inapplicabilità della clausola USA HIPAA (art. 3.3 viii ToS) ai dati sanitari europei e il requisito ACN Data Region Europe, e riassumi i punteggi (70/30) e gli SLA (99,95%) del Capitolato CRAV Telemedicina.
   ```

---

## 🔵 ATTO 2 — Da Antigravity al Multi-Agente ADK a Grafo in Locale (`adk web` + Topology View) (12–15 min)

### 1. Il messaggio chiave
*"Quando oltre alla ricerca documentale serve un'orchestrazione multi-agente con calcoli deterministici, regole di business rigorose e integrazione con i database delle 9 ULSS, usiamo Antigravity per creare un sistema Multi-Agente con Google ADK."*

### 2. Prompt da scrivere in Antigravity (Atto 2)
```text
Usa la skill adk-multiagent-graph-builder per mostrarmi la topologia del grafo multi-agente in azienda_zero_agent/agent.py e avvia adk web in locale sulla porta 8080 così possiamo ispezionare visualmente il Graph mentre interroghiamo i sub-agenti.
```
*(Oppure lancia `./run_local_adk_web.sh` e apri `http://localhost:8080`)*.

### 3. Cosa mostri in `adk web` (`http://localhost:8080`)
1. Seleziona **`azienda_zero_agent`** in alto a sinistra.
2. Clicca sulla scheda **Graph** (Topology): fai vedere la topologia a grafo con **`azero_orchestrator`** al centro collegato ai 3 sub-agenti specialistici:
   - **`ulss_pdta_kpi_agent`** (*PDTA & KPI 9 ULSS Veneto*)
   - **`crav_compliance_agent`** (*Gare CRAV, GDPR/CDPA & ACN*)
   - **`psn_cloud_sizing_agent`** (*Sizing Cloud/PSN Mensile in `$ USD/mo`*)
3. Invia nella chat di `adk web` questo prompt multi-agente che fa illuminare i nodi del grafo:
   ```text
   Dobbiamo preparare l'istruttoria per l'ULSS 6 Euganea e l'ULSS 9 Scaligera:
   1) Controlla i KPI PDTA e verifica se ci sono sforamenti della soglia SLA di 30 giorni sul Time-to-Treatment;
   2) Calcola il sizing mensile in USD ($/mo con List, 1Y CUD, 3Y CUD, OS $/mo e licenza MSSQL in colonna separata) per l'ULSS 6 Euganea: 2 VM da 8 vCPU e 32 GiB RAM con Windows Server 2022 e SQL Server 2022 Standard (Cluster-Referti-ULSS6) più 1 VM legacy da 8 vCPU e 32 GiB RAM con Windows Server 2012 R2 e SQL Server 2012 (VM-Legacy-ULSS6).
   ```
4. **Cosa far notare nel Graph e nella Risposta**:
   - Nel tab **Graph** e **Events**, mostra come `azero_orchestrator` esegue `transfer_to_agent` passando prima a `ulss_pdta_kpi_agent` e poi a `psn_cloud_sizing_agent`.
   - Nella tabella prezzi in `$ USD/mo`, fai notare come il tool applichi automaticamente la regola di governance: espone **Prezzo Mese List (`$/mo`)**, **1Y CUD (`$/mo`)**, **3Y CUD (`$/mo`)**, **OS `$/mo`** e **COSTO MESE LICENZA MSSQL `$/mo`** separato per le 2 VM `Windows Server 2022 + SQL Server 2022`, mentre **esclude automaticamente il costo licenza OS e DB** per la VM `Windows Server 2012 R2 / SQL Server 2012` perché **fuori supporto**!

---

## 🟣 ATTO 3 — Valutazione (Eval) Locale del Grafo su `adk web` e CLI (8–10 min)

### 1. Il messaggio chiave
*"Come facciamo a essere sicuri che, cambiando un prompt o un modello, l'orchestratore continui a seguire esattamente il percorso giusto nel grafo (Graph Trajectory) e rispetti sempre le nostre regole di compliance e di pricing? Con la suite di Evaluation integrata in ADK."*

### 2. Cosa mostri nel tab `Eval` di `adk web` (e da Antigravity)
1. In `adk web` (`http://localhost:8080`), clicca sul tab **Eval** nella barra sinistra.
2. Seleziona l'Eval Set **`azienda_zero_eval`** (`azienda_zero_eval.evalset.json` con i 4 casi di test ufficiali).
3. Clicca **Run Evaluation** per mostrare nella UI di `adk web` il calcolo di:
   - **`tool_trajectory_avg_score`**: verifica che il grafo abbia seguito esattamente i salti `transfer_to_agent` e i tool attesi.
   - **`response_match_score`**: verifica la qualità e completezza della risposta.
4. Da Antigravity, chiedi anche di generare il report strutturato locale:
   ```text
   Usa la skill adk-eval-local-and-cloud per eseguire run_local_eval.py e generare il report di valutazione locale della traiettoria sul grafo.
   ```

---

## 🟠 ATTO 4 — Deploy in Cloud (Vertex AI Agent Engine + Agent Registry A2A) & Ripetizione Eval in Cloud (10–12 min)

### 1. Prompt da scrivere in Antigravity (Atto 4)
```text
Usa la skill adk-eval-local-and-cloud e adk-multiagent-graph-builder per interrogare il nostro multi-agente deployato su Vertex AI Agent Engine (rootprj-377111), verificare la registrazione A2A in Agent Registry e ripetere la stessa identica valutazione (Eval) in Cloud con run_cloud_eval.py generando il report comparativo Locale vs Cloud.
```
*(Oppure digita `/4-deploy-and-cloud-eval`)*.

### 2. Cosa mostri in Cloud Console e in Antigravity
1. **Vertex AI Agent Engine Playground & Cloud Trace**:
   - Apri il link del Playground stampato in `deployment_metadata_azero.json`.
   - Mostra in **Cloud Trace Explorer** gli span OpenTelemetry (`invocation` $\rightarrow$ `azero_orchestrator` $\rightarrow$ `transfer_to_agent` $\rightarrow$ `ulss_pdta_kpi_agent` / `crav_compliance_agent` / `psn_cloud_sizing_agent`) che riflettono in Cloud la stessa topologia vista in locale su `adk web`.
2. **Agent Registry (`A2A Agent Card`)**:
   - Mostra in **Agent Registry** il servizio `Azienda Zero Governance & Sizing Multi-Agent` registrato con protocollo **`A2A (0.3.0)`** e collegato dentro Gemini Enterprise App.
3. **Report Comparativo Eval Locale (`adk web`) vs Eval Cloud (`Vertex AI Agent Engine`)**:
   - Apri in Antigravity (o nel browser) il file generato da `run_cloud_eval.py`:
     - 📄 [`artifacts/EVAL_COMPARISON_LOCAL_VS_CLOUD.md`](./artifacts/EVAL_COMPARISON_LOCAL_VS_CLOUD.md)
     - 🌐 [`artifacts/eval_report_comparison.html`](./artifacts/eval_report_comparison.html)
   - Mostra la tabella side-by-side che certifica **100% Trajectory Match (`1.00`)** sia in Locale su `adk web` sia in Cloud su `Vertex AI Agent Engine`!
