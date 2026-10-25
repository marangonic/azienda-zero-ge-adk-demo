---
description: Atto 2 — Mostra l'architettura del Multi-Agente ADK a Grafo (azienda_zero_agent) e avvia adk web sulla porta 8080 per ispezionare il tab Graph / Topology
---

# Workflow Atto 2 — Multi-Agente ADK `azienda_zero_agent` in Locale + Graph Topology (`adk web`)

1. Mostra la struttura del grafo multi-agente definita in `azienda_zero_agent/agent.py`:
   - `azero_orchestrator` (Root Agent)
   - `ulss_pdta_kpi_agent` (Sub-Agent PDTA & KPI delle 9 ULSS Venete)
   - `crav_compliance_agent` (Sub-Agent Gare CRAV, Privacy GDPR/CDPA & Qualifica ACN)
   - `psn_cloud_sizing_agent` (Sub-Agent Sizing Mensile USD con Prezzo Mese List, 1Y CUD, 3Y CUD, OS $/mo e Licenza MSSQL $/mo separata)
2. Avvia l'interfaccia locale `adk web` collegata a `rootprj-377111`:
   ```bash
   ./run_local_adk_web.sh
   ```
3. Ricorda all'utente di aprire `http://localhost:8080`, selezionare `azienda_zero_agent`, cliccare sul tab **Graph** per visualizzare la topologia del multi-agente e inviare il prompt multi-hop.
