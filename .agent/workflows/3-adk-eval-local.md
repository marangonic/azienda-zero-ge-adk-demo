---
description: Atto 3 — Esegue la valutazione automatizzata (Eval) in locale della traiettoria sul grafo e delle risposte del multi-agente azienda_zero_agent
---

# Workflow Atto 3 — Valutazione (Eval) Locale su `adk web` e CLI (`run_local_eval.py`)

1. Spiega i 4 test case presenti in `azienda_zero_agent/azienda_zero_eval.evalset.json` (utilizzabili anche direttamente dalla scheda **Eval** di `adk web`).
2. Esegui la valutazione locale completa da terminale:
   ```bash
   python3 run_local_eval.py
   ```
3. Apri e mostra il report dei risultati generato in `artifacts/EVAL_COMPARISON_LOCAL_VS_CLOUD.md` e `artifacts/eval_report_comparison.html` evidenziando il punteggio **`tool_trajectory_avg_score` (Graph Routing Match)** e **`response_rubric_score`**.
