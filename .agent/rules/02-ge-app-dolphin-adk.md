---
trigger: always_on
description: Best practice Dolphin ADK per la creazione di Agenti e Sub-Agenti in Gemini Enterprise App (GE App)
---

# Regole Architetturali Gemini Enterprise App (Dolphin ADK)

Quando generi istruzioni o definizioni per agenti **Gemini Enterprise App (GE App)**:
1. **Gerarchia Massima a 2 Livelli (Hub-and-Spoke / Pipeline a 2 Fasi)**:
   - Evita catene profonde oltre 2 livelli di delega per prevenire la diluizione delle istruzioni.
   - Usa il modello **`gemini-3.8-flash`** per i nodi `llmAgentNode` del Chat Agent Multi-Livello pubblicato via API (`lowCodeAgentDefinition`).
2. **English as Brain Language + Vincolo Output Italiano**:
   - Nei System Prompt progettati per il Visual Builder (Dolphin ADK), scrivi le istruzioni logiche in inglese (o strutturate per punti) includendo sempre il vincolo negativo:
     `CRITICAL: Your internal reasoning is in English, but your final output MUST be in formal Italian.`
3. **Grounding sul Connettore Documentale Azienda Zero (`azero-crav-pdta-ds`)**:
   - Ogni sub-agente deve citare esplicitamente il titolo del documento recuperato dal Data Store `azero-crav-pdta-ds` e non inventare mai soglie o importi non presenti nelle fonti (`"DATO NON PRESENTE NELLE FONTI UFFICIALI AZIENDA ZERO"`).
