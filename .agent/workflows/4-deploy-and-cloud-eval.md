---
description: Atto 4 — Esegue il deploy del multi-agente ADK su Vertex AI Agent Engine + Agent Registry (A2A) su rootprj-377111 e ripete la valutazione (Eval) in Cloud
---

# Workflow Atto 4 — Deploy in Cloud (Agent Engine + Agent Registry A2A) & Eval in Cloud (`rootprj-377111`)

1. Esegui il deploy (o verifica il deploy attivo) del multi-agente `azienda_zero_agent` su **Vertex AI Agent Engine** (`rootprj-377111`, `us-central1`) con OpenTelemetry (`Cloud Trace` & `Cloud Logging`) e registrazione **A2A Agent Card** in **Agent Registry**:
   ```bash
   python3 deploy_azero_adk.py
   ```
2. Testa l'agente remoto su Agent Engine:
   ```bash
   python3 test_remote_azero_agent.py
   ```
3. Esegui la **Valutazione (Eval) in Cloud** contro il `ReasoningEngine` remoto usando lo stesso dataset `azienda_zero_eval.evalset.json` e genera il confronto **Locale (`adk web`) vs Cloud (`Vertex AI Agent Engine`)**:
   ```bash
   python3 run_cloud_eval.py
   ```
4. Apri `artifacts/EVAL_COMPARISON_LOCAL_VS_CLOUD.md` e `artifacts/eval_report_comparison.html` per mostrare il confronto side-by-side della traiettoria sul grafo in Locale vs in Cloud.
