# Report di Valutazione (Eval) Multi-Agente a Grafo — Azienda Zero (`rootprj-377111`)

> **Ultimo Aggiornamento:** 2026-10-25 19:32:49  
> **Eval Set:** `azienda_zero_agent/azienda_zero_eval.evalset.json`  
> **Architettura Valutata:** `azero_orchestrator` $\rightarrow$ `ulss_pdta_kpi_agent` | `crav_compliance_agent` | `psn_cloud_sizing_agent`

## 1. Riepilogo Comparativo: Eval Locale (`adk web`) vs Eval Cloud (`Vertex AI Agent Engine`)

| Test Case ID | Nodi del Grafo Attraversati | Locale: Graph Trajectory | Locale: Response Rubric | Cloud: Graph Trajectory | Cloud: Response Rubric | Esito Finale |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `case_1_ulss_pdta_kpi_and_sla` | `azero_orchestrator → ulss_pdta_kpi_agent` | **1.00** | **1.00** | **1.00** | **1.00** | **✅ PASS** |
| `case_2_crav_acn_gdpr_hipaa_compliance` | `azero_orchestrator → crav_compliance_agent` | **1.00** | **1.00** | **1.00** | **1.00** | **✅ PASS** |
| `case_3_psn_sizing_usd_and_eol_guardrail` | `azero_orchestrator → psn_cloud_sizing_agent` | **1.00** | **1.00** | **1.00** | **1.00** | **✅ PASS** |
| `case_4_telemetry_and_graph_trace` | `azero_orchestrator` | **1.00** | **1.00** | **1.00** | **1.00** | **✅ PASS** |

## 2. Dettaglio Traiettoria sul Grafo e Risposte per Caso di Test

### 📌 `case_1_ulss_pdta_kpi_and_sla`
- **Prompt Utente:** *Analizza i KPI PDTA, le COT attive e i pazienti in Telemedicina per l'ULSS 6 Euganea e l'ULSS 9 Scaligera, e verifica quali ULSS del Veneto superano la soglia SLA di 30 giorni sul Time-to-Treatment.*
- **Nodi del Grafo Attesi:** `['azero_orchestrator', 'ulss_pdta_kpi_agent']` | **Nodi Attraversati:** `['azero_orchestrator', 'ulss_pdta_kpi_agent']`
- **Tool Invocati nel Grafo:** `['transfer_to_agent', 'query_ulss_pdta_kpi', 'check_pdta_sla_alert']`
- **Estratto Risposta:**
  > Per l'ULSS 6 Euganea (Padova, 932.000 assistiti, 10/10 COT attive, 23.800 pazienti in Telemedicina) il Time-to-Treatment PDTA è di 27 giorni (CONFORME rispetto al target <=30 giorni). Per l'ULSS 9 Scaligera (Verona, 926.000 assistiti, 9/9 COT attive, 21.100 pazienti in Telemedicina) il Time-to-Treatment è di 31 giorni (ALLERTA_SLA, +1 giorno oltre la soglia di 30 giorni), mentre l'ULSS 7 Pedemontana è a 29 giorni (ATTENZIONE_SOGLIA). Si attiva il protocollo di riequilibrio Azienda Zero con IOV Padova e AOUI Verona.

### 📌 `case_2_crav_acn_gdpr_hipaa_compliance`
- **Prompt Utente:** *Verifica per l'Ufficio Privacy e per il capitolato CRAV Telemedicina di Azienda Zero come sono regolati il CDPA sotto GDPR, la clausola USA HIPAA (art. 3.3 viii ToS), la Data Region Europe per ACN e i punteggi/SLA di gara.*
- **Nodi del Grafo Attesi:** `['azero_orchestrator', 'crav_compliance_agent']` | **Nodi Attraversati:** `['azero_orchestrator', 'crav_compliance_agent']`
- **Tool Invocati nel Grafo:** `['transfer_to_agent', 'verify_acn_gdpr_rules', 'search_crav_capitolati']`
- **Estratto Risposta:**
  > Secondo la Direttiva di Azienda Zero: 1) L'accettazione dei ToS instaura un rapporto diretto regolato dal CDPA standard ai sensi dell'art. 28 GDPR; 2) La clausola dell'art. 3.3(viii) ToS relativa a HIPAA riguarda esclusivamente soggetti/dati USA e non limita il trattamento di dati sanitari UE sotto GDPR; 3) La configurazione Data Region = Europe garantisce storage e processing in UE per la qualifica ACN QC2; 4) Il Capitolato CRAV prevede 70 punti tecnici (soglia minima 42/70) e 30 economici con SLA >= 99,95%, RPO 15 min e RTO 60 min.

### 📌 `case_3_psn_sizing_usd_and_eol_guardrail`
- **Prompt Utente:** *Calcola il sizing mensile in USD ($/mo con List, 1Y CUD, 3Y CUD, OS $/mo e licenza MSSQL in colonna separata) per l'ULSS 6 Euganea: 1) Cluster-Referti-ULSS6 composto da 2 VM da 8 vCPU e 32 GiB RAM con Windows Server 2022 e SQL Server 2022 Standard; 2) VM-Legacy-ULSS6 composta da 1 VM da 8 vCPU e 32 GiB RAM con Windows Server 2012 R2 e SQL Server 2012.*
- **Nodi del Grafo Attesi:** `['azero_orchestrator', 'psn_cloud_sizing_agent']` | **Nodi Attraversati:** `['azero_orchestrator', 'psn_cloud_sizing_agent']`
- **Tool Invocati nel Grafo:** `['transfer_to_agent', 'calculate_vm_mssql_sizing_usd']`
- **Estratto Risposta:**
  > Ecco il prospetto mensile in USD ($/mo): per Cluster-Referti-ULSS6 (2x 8vCPU/32GiB con Windows Server 2022 e SQL Server 2022 Standard, supportati) il Prezzo Mese List è $596.32/mo, 1Y CUD $375.68/mo, 3Y CUD $268.34/mo, OS $/mo $537.28/mo, Totale con OS $1,133.60/mo e COSTO MESE LICENZA MSSQL $/MO separato pari a $1,512.00/mo. Per VM-Legacy-ULSS6 (Windows Server 2012 R2 e SQL Server 2012, fuori supporto) il costo licenza OS e il costo licenza MSSQL sono ESCLUSI in quanto fuori supporto.

### 📌 `case_4_telemetry_and_graph_trace`
- **Prompt Utente:** *Mostrami l'ora corrente in Italia, lo stato della telemetria OpenTelemetry sul progetto rootprj-377111 e la traccia di esecuzione del grafo.*
- **Nodi del Grafo Attesi:** `['azero_orchestrator']` | **Nodi Attraversati:** `['azero_orchestrator']`
- **Tool Invocati nel Grafo:** `['get_azero_session_telemetry']`
- **Estratto Risposta:**
  > La telemetria OpenTelemetry (Cloud Trace e Cloud Logging) è attiva sul progetto rootprj-377111 (us-central1).

