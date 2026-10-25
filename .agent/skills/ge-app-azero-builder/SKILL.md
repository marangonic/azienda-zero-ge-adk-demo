---
name: ge-app-azero-builder
description: Progetta, configura e pubblica sul progetto GCP rootprj-377111 il Connettore Documentale GCS (azero-crav-pdta-ds), l'App Gemini Enterprise (azero-governance-app), le 3 Skills e l'Agente Multi-Livello (Assistente Governance CRAV e PDTA Azienda Zero) per la demo di Azienda Zero Veneto.
---

# Skill: Gemini Enterprise App & Connector Builder — Azienda Zero (`rootprj-377111`)

Usa questa skill quando l'utente chiede in Antigravity di:
- Creare o sincronizzare il **Connettore Documentale Cloud Storage** (`azero-crav-pdta-ds`) per Azienda Zero (Regione del Veneto) su `rootprj-377111`.
- Generare le istruzioni o pubblicare l'agente Gemini Enterprise App **`Assistente Governance CRAV e PDTA Azienda Zero`** e le relative **3 Skills** nell'App Gemini Enterprise (`azero-governance-app`).

## 1. Architettura del Connettore e dell'Agente GE App
- **Progetto GCP**: `rootprj-377111` (Location Discovery Engine: `global`)
- **Bucket GCS**: `gs://rootprj-377111-azienda-zero-veneto/documenti_azero/`
- **Data Store (Connettore)**: `azero-crav-pdta-ds` (*"Connettore Documentale Azienda Zero Veneto — CRAV, PDTA & Privacy ACN"*)
- **Gemini Enterprise App (Engine)**: `azero-governance-app` (*"Azienda Zero Veneto — Governance & Sanità Digitale"*)
- **Agente Multi-Livello (`lowCodeAgentDefinition` con `gemini-3.8-flash`)**:
  - **Root (`SequentialAgentNode`)**: `Assistente Governance CRAV e PDTA Azienda Zero`
  - **Fase 1 (`coord_crav_compliance`)**: *Coordinatore Gare CRAV, PNRR & Compliance ACN/GDPR*
    - Sub-Agent 1.1 (`spec_gare_crav`): *Specialista Capitolati CRAV Telemedicina & FSE 2.0*
    - Sub-Agent 1.2 (`spec_privacy_acn`): *Specialista Privacy GDPR, CDPA & Qualifica ACN*
  - **Fase 2 (`coord_pdta_atti`)**: *Coordinatore PDTA Regionali 9 ULSS & Atti Amministrativi*
    - Sub-Agent 2.1 (`spec_pdta_ulss`): *Analista PDTA Regionali & KPI 9 ULSS Venete*
    - Sub-Agent 2.2 (`spec_determine_crav`): *Redattore Determine Dirigenziali CRAV in 6 Sezioni*

## 2. Comandi Pronti per Eseguire il Setup e il Deploy da Antigravity

### Passo A — Creazione Bucket, Caricamento 6 Documenti Ufficiali e Indicizzazione Istantanea nel Connettore `azero-crav-pdta-ds`
```bash
python3 setup_azero_ge_connector.py
```
Cosa fa:
1. Crea `gs://rootprj-377111-azienda-zero-veneto` e carica i 6 documenti HTML di Azienda Zero.
2. Crea il Data Store `azero-crav-pdta-ds`, indicizza i 6 documenti in **2 secondi** (`branches/0/documents`) e avvia la sync del connettore `gcsSource`.
3. Crea/aggiorna l'App Gemini Enterprise `azero-governance-app` abilitando `no-code-agent-builder` e `skills`, e salva l'URL diretto della Web App in `WEB_APP_URL_AZERO.txt`.

### Passo B — Creazione e Pubblicazione dell'Agente GE App e delle 3 Skills
```bash
python3 register_azero_ge_agent.py
```
Cosa fa:
1. Pubblica le **3 Skills** in `/r/skills`:
   - `Verifica Compliance GDPR CDPA e ACN Data Region Europe`
   - `Valutazione Capitolato Gara CRAV Telemedicina e FSE`
   - `Generatore Bozza Determina Indizione Gara CRAV`
2. Crea, distribuisce (`:deployLowCode`) e condivide (`ALL_USERS`) il Chat Agent Multi-Livello **`Assistente Governance CRAV e PDTA Azienda Zero`**.
3. Se è già stato deployato anche l'agente ADK su Vertex AI Agent Engine, lo collega automaticamente come nodo `referencedAdkAgentNode`!

## 3. Specifiche Copy-Paste per il Visual Builder (Dolphin ADK)
Se l'utente vuole mostrare in demo il copy-paste manuale o l'ispezione delle istruzioni Dolphin ADK, apri il file:
- `artifacts/GE_APP_AGENT_INSTRUCTIONS_AZERO.md`
