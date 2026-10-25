---
name: adk-eval-local-and-cloud
description: Esegue la valutazione automatizzata (Eval) del multi-agente a grafo azienda_zero_agent sia in locale (nel tab Eval di adk web e via run_local_eval.py) sia in Cloud contro l'agente deployato su Vertex AI Agent Engine (run_cloud_eval.py), confrontando la traiettoria sul grafo (tool_trajectory_avg_score) e la qualità delle risposte (response_match_score / LLM Rubric).
---

# Skill: ADK Evaluation (Eval) — Locale (`adk web`) vs Cloud (`Vertex AI Agent Engine`)

Usa questa skill quando l'utente chiede in Antigravity di:
- Mostrare o eseguire una **valutazione (`Eval`) in locale** sul multi-agente `azienda_zero_agent` (tramite il tab **Eval** di `adk web`, `adk eval` o `python3 run_local_eval.py`).
- Ripetere la **stessa valutazione (`Eval`) in Cloud** sull'agente deployato su **Vertex AI Agent Engine** (`rootprj-377111`) tramite `python3 run_cloud_eval.py`.
- Generare o aprire il report comparativo **Locale vs Cloud** (`artifacts/EVAL_COMPARISON_LOCAL_VS_CLOUD.md` e `artifacts/eval_report_comparison.html`) che verifica come il grafo multi-agente segua la traiettoria attesa (`Expected Graph Trajectory` vs `Actual Graph Trajectory`).

## 1. Come Funziona la Valutazione del Grafo Multi-Agente
Il file di valutazione `azienda_zero_agent/azienda_zero_eval.evalset.json` (accompagnato da `azienda_zero_agent/test_config.json`) contiene **4 scenari di test ufficiali per Azienda Zero**:
1. **`case_1_ulss_pdta_kpi`**: Verifica che `azero_orchestrator` instradi la richiesta al nodo `ulss_pdta_kpi_agent` e invochi `query_ulss_pdta_kpi` per estrarre i KPI di `ULSS 6 Euganea` e `ULSS 2 Marca Trevigiana`.
2. **`case_2_crav_acn_gdpr_compliance`**: Verifica che `azero_orchestrator` instradi la richiesta al nodo `crav_compliance_agent` e invochi `verify_acn_gdpr_rules` confermando l'inapplicabilità della clausola USA HIPAA ai dati sanitari UE sotto GDPR e l'obbligo di `Data Region = Europe`.
3. **`case_3_psn_sizing_usd_and_eol_guardrail`**: Verifica che `azero_orchestrator` instradi la richiesta al nodo `psn_cloud_sizing_agent` e invochi `calculate_vm_mssql_sizing_usd`, esponendo i prezzi mensili in `$ USD` (`List $/mo`, `1Y CUD $/mo`, `3Y CUD $/mo`), il costo `OS $/mo` e `COSTO MESE LICENZA MSSQL $/MO` per `Windows Server 2022 + SQL Server 2022`, ed **escludendo il costo licenza** per i sistemi fuori supporto (`Windows Server 2012 R2`).
4. **`case_4_multi_hop_full_governance_graph`**: Prompt complesso multi-dominio che attraversa **tutti e 3 i sub-agenti del grafo** in sequenza (`ulss_pdta_kpi_agent` $\rightarrow$ `crav_compliance_agent` $\rightarrow$ `psn_cloud_sizing_agent`).

## 2. Eseguire la Valutazione in Locale (`adk web` + `run_local_eval.py`)

### A. Visualizzazione Interattiva nel Tab `Eval` di `adk web`
1. Avvia `adk web --port 8080 --allow_origins "*"` e seleziona `azienda_zero_agent`.
2. Clicca sulla scheda **Eval** nella barra laterale sinistra.
3. Seleziona l'Eval Set **`azienda_zero_eval`** (`azienda_zero_eval.evalset.json`).
4. Clicca **Run Evaluation**: vedrai l'esecuzione live di ciascun test case con il punteggio **`tool_trajectory_avg_score`** (verifica dei salti nel grafo e dei tool chiamati) e **`response_match_score`**.

### B. Esecuzione da Terminale Antigravity con Report HTML/Markdown Locale
```bash
python3 run_local_eval.py
```
Esegue i 4 casi sul runner ADK in locale, calcola:
- **Graph Trajectory Score (`tool_trajectory_avg_score`)**
- **Rubric & Keyword Grounding Score (`response_rubric_score`)**
- Salva i risultati in `artifacts/local_eval_results.json` e `artifacts/EVAL_COMPARISON_LOCAL_VS_CLOUD.md`.

## 3. Ripetere la Valutazione in Cloud su Vertex AI Agent Engine (`run_cloud_eval.py`)
Dopo il deploy dell'agente su `rootprj-377111`, esegui la stessa identica suite di valutazione contro il `ReasoningEngine` in Cloud (con integrazione **Vertex AI Evaluation / Gemini Judge**):
```bash
python3 run_cloud_eval.py
```
Cosa fa:
1. Si collega al `ReasoningEngine` deployato su `rootprj-377111` (`us-central1`).
2. Invia i 4 prompt dell'Eval Set e intercetta in streaming tutti gli eventi dei sub-agenti e le `function_call` eseguite nel grafo remoto in Cloud.
3. Calcola il **Cloud Graph Trajectory Score**, il **Cloud Rubric Score** e invoca anche il valutatore **Vertex AI GenAI Evaluation (`vertexai.preview.evaluation` / Gemini Judge)** per certificare la coerenza e la fedeltà alle regole di Azienda Zero.
4. Genera il report comparativo finale **Locale (`adk web`) vs Cloud (`Agent Engine`)** in:
   - `artifacts/EVAL_COMPARISON_LOCAL_VS_CLOUD.md`
   - `artifacts/eval_report_comparison.html` (apribile direttamente nel browser per mostrarlo al cliente!).
