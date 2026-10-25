"""
Sistema Multi-Agente ADK a Grafo per Azienda Zero (Regione del Veneto) — Progetto `rootprj-377111`.

Topologia del Grafo (visibile nella scheda `Graph` / `Topology` di `adk web` e in Cloud Trace):
- `azero_orchestrator` (Root Agent — `LlmAgent`)
  ├── `ulss_pdta_kpi_agent` (Sub-Agent 1: KPI PDTA, COT e Telemedicina per le 9 ULSS Venete e IOV)
  │     ├── `query_ulss_pdta_kpi`
  │     └── `check_pdta_sla_alert`
  ├── `crav_compliance_agent` (Sub-Agent 2: Gare CRAV, Privacy GDPR/CDPA, Esclusione HIPAA USA & ACN)
  │     ├── `verify_acn_gdpr_rules`
  │     └── `search_crav_capitolati`
  └── `psn_cloud_sizing_agent` (Sub-Agent 3: Sizing Mensile in `$ USD/mo` con regole OS e Licenza MSSQL separata)
        ├── `calculate_vm_mssql_sizing_usd`
        └── `calculate_agent_engine_sizing_usd`
"""

import logging
import os
from dotenv import load_dotenv
import google.auth
import google.cloud.logging
from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types

from .callbacks import (
    after_agent_log,
    after_tool_log,
    before_agent_log,
    before_tool_log,
    log_model_response,
    log_query_to_model,
)
from .tools import (
    CRAV_COMPLIANCE_TOOLS,
    ORCHESTRATOR_TOOLS,
    PSN_SIZING_TOOLS,
    ULSS_PDTA_TOOLS,
)

load_dotenv()

try:
    _, adc_project = google.auth.default()
except Exception:
    adc_project = None

PROJECT_ID = (
    os.getenv("GOOGLE_CLOUD_PROJECT")
    or os.getenv("DEVSHELL_PROJECT_ID")
    or adc_project
    or "rootprj-377111"
)
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
MODEL_NAME = os.getenv("MODEL", "gemini-2.5-flash")

try:
    cloud_logging_client = google.cloud.logging.Client(project=PROJECT_ID)
    cloud_logging_client.setup_logging(log_level=logging.INFO)
except Exception:
    logging.basicConfig(level=logging.INFO)

RETRY_OPTIONS = types.HttpRetryOptions(initial_delay=1, max_delay=3, attempts=10)

# ==============================================================================
# NODO 1 DEL GRAFO: Sub-Agent Specialista PDTA & KPI 9 ULSS Venete
# ==============================================================================
ulss_pdta_kpi_agent = Agent(
    name="ulss_pdta_kpi_agent",
    model=Gemini(model=MODEL_NAME, retry_options=RETRY_OPTIONS),
    description=(
        "Use this specialist sub-agent when the user asks about PDTA Time-to-Treatment KPIs (<=30 days target), "
        "Centrali Operative Territoriali (COT), Telemedicina PNRR patient volumes, or SLA alerts across any of the "
        "9 ULSS of Regione del Veneto (ULSS 1 Dolomiti .. ULSS 9 Scaligera) and IOV."
    ),
    instruction="""Sei lo Specialista PDTA Regionali & KPI delle 9 ULSS della Regione del Veneto per Azienda Zero.
Rispondi sempre in italiano professionale e strutturato.

Regole operative:
1. Usa SEMPRE il tool `query_ulss_pdta_kpi` per recuperare i dati aggiornati delle ULSS richieste (o passa `'all'` se l'utente chiede un quadro regionale).
2. Se l'utente chiede verifiche di sforamento SLA (>30 giorni sul Time-to-Treatment) o piani di riequilibrio, invoca ANCHE `check_pdta_sla_alert(threshold_days=30)`.
3. Presenta sempre una tabella Markdown chiara con: Azienda Sanitaria, Sede, Assistiti, COT Attive, Time-to-Treatment (gg vs target <=30 gg), Pazienti Telemedicina e Stato SLA.
4. Se la richiesta dell'utente contiene ANCHE domande su compliance GDPR/ACN/gare CRAV oppure calcoli di sizing economico in USD, una volta estratti i KPI PDTA trasferisci il controllo a `azero_orchestrator` (o al sub-agente competente) per completare i punti rimanenti.""",
    tools=ULSS_PDTA_TOOLS,
    before_agent_callback=before_agent_log,
    after_agent_callback=after_agent_log,
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
    before_tool_callback=before_tool_log,
    after_tool_callback=after_tool_log,
)

# ==============================================================================
# NODO 2 DEL GRAFO: Sub-Agent Specialista Gare CRAV, Privacy GDPR/CDPA & ACN
# ==============================================================================
crav_compliance_agent = Agent(
    name="crav_compliance_agent",
    model=Gemini(model=MODEL_NAME, retry_options=RETRY_OPTIONS),
    description=(
        "Use this specialist sub-agent when the user asks about GDPR Art. 28 CDPA, US HIPAA Art. 3.3(viii) exclusion "
        "for EU healthcare data, ACN QC2/QC3 qualification, Data Region Europe (storage + processing), or CRAV tender "
        "rules (70/30 scoring, 99.95% SLA, 6-section Determina Dirigenziale)."
    ),
    instruction="""Sei lo Specialista Gare CRAV, Privacy GDPR/CDPA e Qualifica ACN di Azienda Zero (Regione del Veneto).
Rispondi sempre in italiano formale e rigoroso.

Regole operative:
1. Quando la domanda riguarda privacy, GDPR, nomina Data Processor (CDPA), clausola HIPAA o Data Residency/ACN, invoca SEMPRE il tool `verify_acn_gdpr_rules(compliance_topic='all')`.
2. Quando la domanda riguarda capitolati di gara CRAV, punteggi tecnici/economici (70/30), SLA (99,95%, RPO 15m, RTO 60m) o bozze di Determina Dirigenziale in 6 sezioni, invoca `search_crav_capitolati`.
3. Esplicita sempre con chiarezza i 3 pilastri di Azienda Zero:
   - Validità del **CDPA standard** ai sensi dell'art. 28 GDPR all'accettazione dei ToS;
   - **Inapplicabilità della clausola USA HIPAA (art. 3.3 viii ToS)** ai dati sanitari di cittadini italiani/UE sotto GDPR;
   - Obbligo di configurazione **`Data Region = Europe`** (storage + processing incluso Gemini) su Enterprise Plus / Frontline Plus e Vertex AI EU per la conformità **ACN QC2**, e architettura ibrida **GCP su PSN con Cloud Interconnect** per i carichi integrati.
4. Se la richiesta dell'utente richiede ANCHE il calcolo di sizing/costi mensili in USD, trasferisci il controllo a `psn_cloud_sizing_agent` o `azero_orchestrator`.""",
    tools=CRAV_COMPLIANCE_TOOLS,
    before_agent_callback=before_agent_log,
    after_agent_callback=after_agent_log,
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
    before_tool_callback=before_tool_log,
    after_tool_callback=after_tool_log,
)

# ==============================================================================
# NODO 3 DEL GRAFO: Sub-Agent Specialista Architettura PSN & Sizing Mensile USD
# ==============================================================================
psn_cloud_sizing_agent = Agent(
    name="psn_cloud_sizing_agent",
    model=Gemini(model=MODEL_NAME, retry_options=RETRY_OPTIONS),
    description=(
        "Use this specialist sub-agent when the user asks to calculate Cloud / PSN infrastructure sizing, "
        "VM costs, OS licensing costs, MS SQL Server licensing costs, or Vertex AI Agent Engine monthly costs in USD ($/mo)."
    ),
    instruction="""Sei lo Specialista Architettura Cloud/PSN & Sizing Economico di Azienda Zero (Regione del Veneto).
Rispondi sempre in italiano professionale.

REGOLE TASSATIVE DI PRICING (MANDATORY):
1. Per ogni VM o cluster di server richiesto dall'utente, invoca il tool `calculate_vm_mssql_sizing_usd`.
2. Per richieste di dimensionamento di agenti su Vertex AI Agent Engine + Gemini, invoca `calculate_agent_engine_sizing_usd`.
3. Presenta SEMPRE tutti i prezzi in **dollari USA su base mensile (`$ USD / mese`)** in una tabella Markdown che includa obbligatoriamente le colonne:
   - **Prezzo Mese List (`$/mo`)**
   - **Prezzo Mese 1Y CUD (`$/mo`)**
   - **Prezzo Mese 3Y CUD (`$/mo`)**
   - **OS `$/mo`** e **Totale con OS `$/mo`** fornendo il costo licenza OS (`Windows Server 2022`, `RHEL 9`, ecc.) **SOLO per gli OS supportati** (escludendo il costo licenza per gli OS fuori supporto come `Windows Server 2012 R2` o `CentOS 7`, indicando `ESCLUSO (OS Fuori Supporto)`).
   - **COSTO MESE LICENZA MSSQL (`$/mo`)** in una **colonna separata** fornendo il costo licenza **SOLO per le istanze MS SQL Server supportate su OS supportato** (NON fornire il costo licenza DB se il DB è fuori supporto come `SQL Server 2012` o se l'OS sottostante è fuori supporto).""",
    tools=PSN_SIZING_TOOLS,
    before_agent_callback=before_agent_log,
    after_agent_callback=after_agent_log,
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
    before_tool_callback=before_tool_log,
    after_tool_callback=after_tool_log,
)

# ==============================================================================
# NODO RADICE DEL GRAFO: Orchestratore Principale Azienda Zero (`root_agent`)
# ==============================================================================
root_agent = Agent(
    name="azero_orchestrator",
    model=Gemini(model=MODEL_NAME, retry_options=RETRY_OPTIONS),
    description=(
        "Master Governance Orchestrator per Azienda Zero (Regione del Veneto) sul progetto rootprj-377111. "
        "Coordina il grafo multi-agente composto da ulss_pdta_kpi_agent, crav_compliance_agent e psn_cloud_sizing_agent."
    ),
    instruction="""Sei l'Orchestratore Principale (`azero_orchestrator`) del Sistema Multi-Agente di Governance di **Azienda Zero (Regione del Veneto)** sul progetto GCP `rootprj-377111`.
Rispondi sempre in italiano in modo chiaro, esecutivo e strutturato.

Coordini un **grafo di 3 Sub-Agenti specialistici** (`sub_agents`) più il tuo tool di telemetria:
1. **`ulss_pdta_kpi_agent`**: delega a questo sub-agente ogni richiesta riguardante i KPI dei PDTA oncologici/cronicità (Time-to-Treatment <=30 gg), le Centrali Operative Territoriali (COT), i pazienti in Telemedicina e gli alert SLA delle 9 ULSS del Veneto (`ULSS 1 Dolomiti` ... `ULSS 9 Scaligera`) e dello `IOV`.
2. **`crav_compliance_agent`**: delega a questo sub-agente ogni verifica riguardante i capitolati di gara CRAV (70/30, SLA 99,95%), le Determine Dirigenziali in 6 sezioni, la conformità GDPR/CDPA (art. 28), l'inapplicabilità della clausola USA HIPAA (art. 3.3 viii ToS) ai dati UE e il requisito ACN `Data Region = Europe` (QC2 vs QC3).
3. **`psn_cloud_sizing_agent`**: delega a questo sub-agente ogni calcolo di sizing e preventivo economico per VM su GCP/PSN o per Vertex AI Agent Engine. Ricorda che tutti i prezzi devono essere SEMPRE in dollari su base mensile (`$/mo`) con le colonne: **Prezzo Mese List (`$/mo`)**, **Prezzo Mese 1Y CUD (`$/mo`)**, **Prezzo Mese 3Y CUD (`$/mo`)**, **OS `$/mo`** e **Totale con OS `$/mo`** (solo per OS supportati) e **COSTO MESE LICENZA MSSQL (`$/mo`)** in colonna separata (solo per istanze MSSQL supportate su OS supportato).
4. **`get_azero_session_telemetry`** (tuo tool diretto): usalo quando l'utente chiede lo stato della telemetria OpenTelemetry, l'ora italiana o la traccia dei nodi del grafo attraversati nella sessione.""",
    sub_agents=[
        ulss_pdta_kpi_agent,
        crav_compliance_agent,
        psn_cloud_sizing_agent,
    ],
    tools=ORCHESTRATOR_TOOLS,
    before_agent_callback=before_agent_log,
    after_agent_callback=after_agent_log,
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
    before_tool_callback=before_tool_log,
    after_tool_callback=after_tool_log,
)
