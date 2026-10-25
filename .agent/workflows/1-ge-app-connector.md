---
description: Atto 1 — Configura il Connettore GCS Documentale (azero-crav-pdta-ds), pubblica l'App Gemini Enterprise (azero-governance-app), le 3 Skills e il Chat Agent Multi-Livello su rootprj-377111
---

# Workflow Atto 1 — Gemini Enterprise App + Connettore Azienda Zero (`rootprj-377111`)

1. Esegui lo script di provisioning del Bucket GCS, caricamento dei 6 documenti ufficiali di Azienda Zero, creazione e indicizzazione istantanea (2 secondi) del Connettore `azero-crav-pdta-ds` e dell'App `azero-governance-app`:
   ```bash
   python3 setup_azero_ge_connector.py
   ```
2. Pubblica le **3 Skills** e il Chat Agent Multi-Livello **`Assistente Governance CRAV e PDTA Azienda Zero`** (modello `gemini-3.8-flash`) collegato al connettore `azero-crav-pdta-ds`:
   ```bash
   python3 register_azero_ge_agent.py
   ```
3. Mostra all'utente l'URL diretto della Web App Gemini Enterprise salvato in `WEB_APP_URL_AZERO.txt` e i 3 prompt di test pronti da provare in Web App.
