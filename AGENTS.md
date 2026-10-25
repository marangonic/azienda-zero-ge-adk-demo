# AGENTS.md — Istruzioni Operative per Antigravity (PC) + Cloud Shell (`rootprj-377111`)

Quando l'utente lavora in questo workspace da **Antigravity sul proprio PC**:
1. **Cosa esegui direttamente in Antigravity (PC)**:
   - Creazione, modifica e spiegazione dei prompt Dolphin ADK per Gemini Enterprise App (`artifacts/GE_APP_AGENT_INSTRUCTIONS_AZERO.md`).
   - Creazione, modifica e spiegazione del codice del Multi-Agente ADK a Grafo (`azienda_zero_agent/agent.py`, `azienda_zero_agent/tools.py`, `azienda_zero_agent/callbacks.py`) e dell'Eval Set (`azienda_zero_agent/azienda_zero_eval.evalset.json`).
   - Esecuzione live dei 3 tool del **Server MCP locale** (`azero-crav-governance-mcp`: `azero_get_ulss_pdta_kpi`, `azero_check_acn_gdpr_compliance`, `azero_calculate_cloud_sizing_usd`).
   - Apertura e visualizzazione dei report in `artifacts/EVAL_COMPARISON_LOCAL_VS_CLOUD.md` e `artifacts/eval_report_comparison.html`.
2. **Cosa viene eseguito in Google Cloud Shell (`rootprj-377111`)**:
   - `adk web --port 8080 --allow_origins "*"` (con Cloud Shell Web Preview sulla porta `8080` per mostrare i tab **Graph / Topology** ed **Eval**).
   - I comandi di provisioning e deploy verso GCP (`./setup_cloudshell_azero.sh`, `python3 setup_azero_ge_connector.py`, `python3 register_azero_ge_agent.py`, `python3 deploy_azero_adk.py`, `python3 run_local_eval.py`, `python3 run_cloud_eval.py`).
   - Fornisci sempre all'utente il comando esatto pronto per il copy-paste in **Cloud Shell**.
3. **Regola Tassativa Prezzi**:
   - Mantieni tutti i prezzi sempre in `$ USD` su base mensile (`Prezzo Mese List $/mo`, `Prezzo Mese 1Y CUD $/mo`, `Prezzo Mese 3Y CUD $/mo`, `OS $/mo` e `Totale con OS $/mo` solo per OS supportati, e `COSTO MESE LICENZA MSSQL $/MO` in colonna separata solo per DB supportati su OS supportato).
