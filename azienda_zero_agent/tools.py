"""
Tool ADK Standard (`FunctionTool` + `ToolContext`) per il sistema Multi-Agente a Grafo
di Azienda Zero (Regione del Veneto) sul progetto `rootprj-377111`:

1. Tool per `ulss_pdta_kpi_agent` (Specialista PDTA & KPI 9 ULSS Veneto):
   - `query_ulss_pdta_kpi`: interroga i KPI di presa in carico PDTA, stato COT e Telemedicina PNRR delle 9 ULSS venete e IOV.
   - `check_pdta_sla_alert`: individua le ULSS che superano o sfiorano la soglia di 30 giorni sul Time-to-Treatment e genera il protocollo di riequilibrio inter-aziendale.

2. Tool per `crav_compliance_agent` (Specialista Gare CRAV, Privacy GDPR/CDPA & Qualifica ACN):
   - `verify_acn_gdpr_rules`: verifica conformità GDPR art. 28 (CDPA), inapplicabilità clausola USA HIPAA (art. 3.3 viii ToS) ai dati sanitari UE e obbligo `Data Region = Europe` (ACN QC2 vs QC3).
   - `search_crav_capitolati`: recupera criteri di aggiudicazione (70/30, sbarramento 42/70), SLA (99,95%, RPO 15m, RTO 60m) e struttura in 6 sezioni della Determina CRAV.

3. Tool per `psn_cloud_sizing_agent` (Specialista Architettura PSN & Sizing Mensile USD):
   - `calculate_vm_mssql_sizing_usd`: calcola il sizing mensile in USD (`$/mo`) esponendo:
     * `Prezzo Mese List ($/mo)`, `Prezzo Mese 1Y CUD ($/mo)`, `Prezzo Mese 3Y CUD ($/mo)`
     * `OS $/mo` e `Totale con OS $/mo` **solo per gli OS supportati** (escludendo il costo licenza per OS fuori supporto come Windows Server 2012 R2 o CentOS 7)
     * `COSTO MESE LICENZA MSSQL $/MO` in colonna separata **solo per istanze MS SQL Server supportate su OS supportato** (non fornisce il costo se il DB o l'OS sottostante sono fuori supporto).
   - `calculate_agent_engine_sizing_usd`: calcola i costi mensili in USD (`List $/mo`, `1Y CUD $/mo`, `3Y CUD $/mo`) per Vertex AI Agent Engine + Gemini 2.5 Flash.

4. Tool per `azero_orchestrator` (Root Agent):
   - `get_azero_session_telemetry`: restituisce l'ora italiana, stato OpenTelemetry e la traccia completa dei nodi e tool attraversati nel grafo (`graph_execution_trace`).
"""

import datetime
import os
from typing import Any, Dict, List
from zoneinfo import ZoneInfo

from google.adk.tools import FunctionTool, ToolContext

ULSS_KPI_DATA: Dict[str, Dict[str, Any]] = {
    "ULSS 1 Dolomiti": {
        "codice": "ULSS1",
        "sede": "Belluno",
        "assistiti": 197000,
        "cot_attive": "4/4 (100%)",
        "pdta_time_to_treatment_gg": 24,
        "sla_max_gg": 30,
        "pazienti_telemedicina": 4850,
        "stato_sla": "CONFORME",
        "hub_riferimento": "Ospedale San Martino Belluno / IOV",
        "workload_cloud": "1 VM RHEL 9 (4 vCPU, 16 GiB RAM, No MSSQL)",
    },
    "ULSS 2 Marca Trevigiana": {
        "codice": "ULSS2",
        "sede": "Treviso",
        "assistiti": 885000,
        "cot_attive": "9/9 (100%)",
        "pdta_time_to_treatment_gg": 26,
        "sla_max_gg": 30,
        "pazienti_telemedicina": 19400,
        "stato_sla": "CONFORME",
        "hub_riferimento": "Ospedale Ca' Foncello Treviso / IOV Castelfranco",
        "workload_cloud": "1 VM Windows Server 2022 + SQL Server 2022 Standard (8 vCPU, 32 GiB RAM)",
    },
    "ULSS 3 Serenissima": {
        "codice": "ULSS3",
        "sede": "Venezia - Mestre",
        "assistiti": 612000,
        "cot_attive": "6/6 (100%)",
        "pdta_time_to_treatment_gg": 28,
        "sla_max_gg": 30,
        "pazienti_telemedicina": 14200,
        "stato_sla": "CONFORME",
        "hub_riferimento": "Ospedale dell'Angelo Mestre",
        "workload_cloud": "1 VM RHEL 9 (8 vCPU, 32 GiB RAM)",
    },
    "ULSS 4 Veneto Orientale": {
        "codice": "ULSS4",
        "sede": "San Donà di Piave",
        "assistiti": 228000,
        "cot_attive": "3/3 (100%)",
        "pdta_time_to_treatment_gg": 25,
        "sla_max_gg": 30,
        "pazienti_telemedicina": 5600,
        "stato_sla": "CONFORME",
        "hub_riferimento": "Ospedale Ca' Foncello / Mestre",
        "workload_cloud": "1 VM Ubuntu 22.04 LTS (4 vCPU, 16 GiB RAM)",
    },
    "ULSS 6 Euganea": {
        "codice": "ULSS6",
        "sede": "Padova",
        "assistiti": 932000,
        "cot_attive": "10/10 (100%)",
        "pdta_time_to_treatment_gg": 27,
        "sla_max_gg": 30,
        "pazienti_telemedicina": 23800,
        "stato_sla": "CONFORME",
        "hub_riferimento": "AO Padova / IOV Padova",
        "workload_cloud": "2 VM Windows Server 2022 + SQL Server 2022 Standard (8 vCPU, 32 GiB RAM) + 1 VM Legacy Windows Server 2012 R2 (FUORI SUPPORTO)",
    },
    "ULSS 7 Pedemontana": {
        "codice": "ULSS7",
        "sede": "Bassano del Grappa / Santorso",
        "assistiti": 358000,
        "cot_attive": "4/4 (100%)",
        "pdta_time_to_treatment_gg": 29,
        "sla_max_gg": 30,
        "pazienti_telemedicina": 8900,
        "stato_sla": "ATTENZIONE_SOGLIA",
        "hub_riferimento": "Ospedale Alto Vicentino / IOV Castelfranco",
        "workload_cloud": "1 VM Windows Server 2022 + SQL Server 2012 Legacy (DB FUORI SUPPORTO)",
    },
    "ULSS 8 Berica": {
        "codice": "ULSS8",
        "sede": "Vicenza",
        "assistiti": 502000,
        "cot_attive": "5/5 (100%)",
        "pdta_time_to_treatment_gg": 23,
        "sla_max_gg": 30,
        "pazienti_telemedicina": 12700,
        "stato_sla": "CONFORME",
        "hub_riferimento": "Ospedale San Bortolo Vicenza",
        "workload_cloud": "1 VM RHEL 9 (8 vCPU, 32 GiB RAM) Gateway CTI 116117",
    },
    "ULSS 9 Scaligera": {
        "codice": "ULSS9",
        "sede": "Verona",
        "assistiti": 926000,
        "cot_attive": "9/9 (100%)",
        "pdta_time_to_treatment_gg": 31,
        "sla_max_gg": 30,
        "pazienti_telemedicina": 21100,
        "stato_sla": "ALLERTA_SLA",
        "hub_riferimento": "AOUI Verona / IOV",
        "workload_cloud": "2 VM Windows Server 2022 + SQL Server 2022 Standard (8 vCPU, 32 GiB RAM)",
    },
    "IOV - Istituto Oncologico Veneto": {
        "codice": "IOV",
        "sede": "Padova / Castelfranco Veneto",
        "assistiti": 48000,
        "cot_attive": "Hub Oncologico Regionale",
        "pdta_time_to_treatment_gg": 18,
        "sla_max_gg": 30,
        "pazienti_telemedicina": 9500,
        "stato_sla": "ECCELLENTE",
        "hub_riferimento": "IRCCS Rete Oncologica Veneta",
        "workload_cloud": "Cluster AI & Tumor Board Regionale su Vertex AI",
    },
}


def query_ulss_pdta_kpi(
    ulss_filter: str,
    tool_context: ToolContext,
) -> dict:
    """Interroga i KPI di presa in carico PDTA, le COT attive e i volumi di Telemedicina delle 9 ULSS del Veneto e IOV.

    Args:
        ulss_filter: Nome o codice della ULSS da cercare (es. 'ULSS 6', 'ULSS 2', 'ULSS 9', oppure 'all' per tutte le 9 ULSS e IOV).

    Returns:
        Dizionario con i KPI ufficiali delle ULSS selezionate e i target regionali di Azienda Zero.
    """
    q = (ulss_filter or "all").strip().lower()
    matched: Dict[str, Any] = {}
    for name, data in ULSS_KPI_DATA.items():
        if q in ("all", "*", "tutte", "") or q in name.lower() or q in data["codice"].lower() or q in data["sede"].lower():
            matched[name] = data
    if not matched:
        matched = ULSS_KPI_DATA

    tool_context.state["last_ulss_queried"] = list(matched.keys())
    return {
        "status": "success",
        "ente_governance": "Azienda Zero - Regione del Veneto",
        "ulss_count": len(matched),
        "target_regionale_time_to_treatment_gg": 30,
        "target_time_to_diagnosis_gg": 15,
        "results": matched,
    }


def check_pdta_sla_alert(
    threshold_days: int,
    tool_context: ToolContext,
) -> dict:
    """Identifica le ULSS venete che superano o sono prossime alla soglia SLA PDTA (default 30 giorni) e genera il protocollo di riequilibrio.

    Args:
        threshold_days: Soglia di giorni per il Time-to-Treatment PDTA (default 30).

    Returns:
        Dizionario con le ULSS critiche e il piano operativo di riequilibrio verso AO Padova, AOUI Verona e IOV.
    """
    limit = max(20, int(threshold_days or 30))
    alerts: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []

    for name, data in ULSS_KPI_DATA.items():
        ttt = data["pdta_time_to_treatment_gg"]
        if ttt > limit:
            alerts.append({"ulss": name, **data, "scostamento_gg": ttt - limit})
        elif ttt >= limit - 1:
            warnings.append({"ulss": name, **data, "margine_gg": limit - ttt})

    tool_context.state["sla_alerts_detected"] = [a["ulss"] for a in alerts]
    return {
        "status": "success",
        "threshold_days": limit,
        "ulss_in_allerta_sla": alerts,
        "ulss_in_attenzione_soglia": warnings,
        "protocollo_escalation_azienda_zero": [
            "Step 1: Attivazione immediata slot chirurgici e diagnostici protetti presso IOV (Padova/Castelfranco), AO Padova e AOUI Verona.",
            "Step 2: Convocazione del Teleconsulto GOM (Gruppo Oncologico Multidisciplinare) entro 7 giorni tramite Piattaforma Telemedicina regionale.",
            "Step 3: Presa in carico post-dimissione tramite la COT distrettuale con Telemonitoraggio integrato su FSE 2.0.",
        ],
    }


def verify_acn_gdpr_rules(
    compliance_topic: str,
    tool_context: ToolContext,
) -> dict:
    """Verifica le regole ufficiali di Azienda Zero su GDPR/CDPA, clausola HIPAA ToS, Data Region Europe e qualifica ACN QC2/QC3.

    Args:
        compliance_topic: Argomento da verificare ('all', 'gdpr_cdpa', 'hipaa', 'data_region_europe', 'acn_qc2_qc3').

    Returns:
        Dizionario con le direttive legali e tecniche validate dall'Ufficio Privacy e dalla UOC Sistemi Informativi di Azienda Zero.
    """
    tool_context.state["last_compliance_check"] = compliance_topic
    return {
        "status": "success",
        "topic": compliance_topic,
        "fonte_ufficiale": "03_Direttiva_Privacy_GDPR_CDPA_ACN_Data_Region_Europe.html",
        "direttive_azienda_zero": {
            "1_nomina_responsabile_cdpa_gdpr": (
                "L'accettazione dei Terms of Service (ToS) di Google Workspace e Google Cloud instaura un rapporto diretto "
                "regolato dal Cloud Data Processing Addendum (CDPA) standard ai sensi dell'art. 28 del GDPR (Regolamento UE 2016/679)."
            ),
            "2_inapplicabilita_clausola_usa_hipaa": (
                "La clausola dell'art. 3.3(viii) dei ToS relativa a HIPAA / PHI riguarda ESCLUSIVAMENTE i soggetti e i dati "
                "sottoposti alla legge federale statunitense HIPAA (USA) e NON pone alcuna limitazione contrattuale al trattamento "
                "di dati sanitari di cittadini italiani/UE sotto GDPR."
            ),
            "3_data_region_europe_acn_qc2": (
                "Per garantire sia lo storage (Data at Rest) sia il processing (Data in Use, incluso Gemini) in Unione Europea "
                "secondo il Catalogo ACN (Qualifica QC2), è obbligatorio configurare la policy Data Region = Europe "
                "(disponibile nelle edizioni Enterprise Plus / Frontline Plus e sulle region europee di Vertex AI)."
            ),
            "4_architettura_ibrida_psn_qc3": (
                "Per i workload interconnessi con il Polo Strategico Nazionale (PSN) o basi dati Oracle PaaS su PSN, "
                "Azienda Zero adotta l'architettura ibrida GCP su PSN con Cloud Interconnect dedicata, HAProxy gestito, "
                "Cloud SQL HA e integrazione a bassa latenza con i nodi CTI 116117."
            ),
        },
    }


def search_crav_capitolati(
    query: str,
    tool_context: ToolContext,
) -> dict:
    """Cerca le regole dei capitolati di gara CRAV (punteggi 70/30, SLA 99.95%, RPO/RTO) e lo schema in 6 sezioni della Determina Dirigenziale.

    Args:
        query: Argomento di gara o sezione da cercare (es. 'criteri punteggio', 'sla telemedicina', 'determina 6 sezioni').

    Returns:
        Dizionario con i parametri ufficiali del Capitolato CRAV `CRAV-AZERO-2026-TLM-01` e del modello `MOD-DET-CRAV-AZERO-2026`.
    """
    tool_context.state["last_crav_query"] = query
    return {
        "status": "success",
        "query": query,
        "codice_gara": "CRAV-AZERO-2026-TLM-01",
        "criteri_aggiudicazione_oepv": {
            "punteggio_tecnico_max": 70,
            "soglia_minima_sbarramento_tecnico": 42,
            "punteggio_economico_max": 30,
            "ripartizione_tecnica": {
                "Architettura Cloud & Interoperabilità FHIR FSE 2.0": 25,
                "Sicurezza ACN/GDPR & Data Residency Europe": 20,
                "Integrazione COT e PDTA Regionali 9 ULSS": 15,
                "SLA migliorativi e Supporto Operativo": 10,
            },
        },
        "sla_obbligatori": {
            "disponibilita_mensile": ">= 99,95% (24x7x365)",
            "rpo_max": "15 minuti",
            "rto_max": "60 minuti",
            "presa_in_carico_severity_1": "15 minuti (risoluzione entro 4 ore)",
        },
        "modello_determina_6_sezioni": [
            "SEZIONE 1: Intestazione, UOC Proponente (Sistemi Informativi / CRAV) e Nomina RUP (art. 15 D.Lgs. 36/2023)",
            "SEZIONE 2: Premesse di Fatto, L.R. Veneto n. 19/2016 e Obiettivi PNRR M6",
            "SEZIONE 3: Analisi Tecnica, KPI PDTA e Tabella Sizing Infrastrutturale Cloud in USD ($/mo)",
            "SEZIONE 4: Quadro Economico e Copertura Finanziaria (PNRR / GSA Veneto)",
            "SEZIONE 5: Presidi Obbligatori di Conformità GDPR (CDPA art. 28), ACN (Data Region Europe) e AI Act UE 2024/1689",
            "SEZIONE 6: Dispositivo di Approvazione, Codici CIG/CUP e Trasmissione alle 9 ULSS",
        ],
    }


def calculate_vm_mssql_sizing_usd(
    workload_name: str,
    vm_count: int,
    vcpu_per_vm: int,
    ram_gib_per_vm: int,
    os_name: str,
    mssql_edition: str,
    tool_context: ToolContext,
) -> dict:
    """Calcola il preventivo mensile in dollari ($ USD/mo) per VM su GCP/PSN con regole rigorose su OS supportati e licenze MS SQL Server.

    Regole applicate automaticamente dal tool:
    - Espone sempre: Prezzo Mese List ($/mo), Prezzo Mese 1Y CUD ($/mo), Prezzo Mese 3Y CUD ($/mo).
    - Espone Costo Mese con Sistema Operativo (`OS $/mo` e `Totale con OS $/mo`) SOLO per gli OS supportati
      (es. Windows Server 2022/2019, RHEL 8/9, Ubuntu 22.04 LTS), escludendo il costo licenza per gli OS fuori supporto (es. Windows Server 2012 R2, CentOS 7).
    - Espone `COSTO MESE LICENZA MSSQL $/MO` in colonna separata SOLO per le istanze MS SQL Server supportate (es. SQL Server 2019/2022)
      su OS supportato (non fornisce il costo licenza DB se il DB è fuori supporto es. SQL Server 2012/2014 o se l'OS sottostante è fuori supporto).

    Args:
        workload_name: Nome identificativo del workload o della ULSS (es. 'Cluster-Referti-ULSS6' o 'VM-Legacy-ULSS6').
        vm_count: Numero di VM identiche nel gruppo (es. 1 o 2).
        vcpu_per_vm: Numero di vCPU per ciascuna VM (es. 8).
        ram_gib_per_vm: Memoria RAM in GiB per ciascuna VM (es. 32).
        os_name: Sistema operativo della VM (es. 'Windows Server 2022', 'RHEL 9', 'Windows Server 2012 R2').
        mssql_edition: Edizione MS SQL Server installata (es. 'SQL Server 2022 Standard', 'SQL Server 2012', 'None').

    Returns:
        Dizionario con i costi mensili in USD ($/mo) e una riga Markdown già formattata secondo lo standard obbligatorio.
    """
    count = max(1, int(vm_count or 1))
    vcpu = max(2, int(vcpu_per_vm or 8))
    ram = max(4, int(ram_gib_per_vm or 32))
    total_vcpu = count * vcpu
    total_ram = count * ram

    # Prezzo Mese Compute Base in USD ($/mo)
    compute_list_usd = round((total_vcpu * 24.27) + (total_ram * 3.25), 2)
    compute_1y_cud_usd = round(compute_list_usd * 0.63, 2)
    compute_3y_cud_usd = round(compute_list_usd * 0.45, 2)

    os_clean = (os_name or "Windows Server 2022").strip()
    os_lower = os_clean.lower()
    os_is_eol = any(eol in os_lower for eol in ("2012", "2008", "2003", "centos 7", "centos 6", "rhel 6", "debian 9", "ubuntu 16", "ubuntu 18"))

    if os_is_eol:
        os_supported = False
        os_cost_usd_mo = None
        totale_con_os_list_usd = None
        totale_con_os_1y_usd = None
        totale_con_os_3y_usd = None
        os_label = "ESCLUSO (OS Fuori Supporto)"
    else:
        os_supported = True
        if "windows" in os_lower:
            os_rate_vcpu = 33.58
        elif "rhel" in os_lower or "red hat" in os_lower:
            os_rate_vcpu = 14.00
        elif "sles" in os_lower or "suse" in os_lower:
            os_rate_vcpu = 12.50
        else:
            os_rate_vcpu = 0.0
        os_cost_usd_mo = round(total_vcpu * os_rate_vcpu, 2)
        totale_con_os_list_usd = round(compute_list_usd + os_cost_usd_mo, 2)
        totale_con_os_1y_usd = round(compute_1y_cud_usd + os_cost_usd_mo, 2)
        totale_con_os_3y_usd = round(compute_3y_cud_usd + os_cost_usd_mo, 2)
        os_label = f"${os_cost_usd_mo:,.2f}/mo"

    db_clean = (mssql_edition or "None").strip()
    db_lower = db_clean.lower()
    has_mssql = db_lower not in ("none", "nessuno", "no", "", "n/a")
    db_is_eol = any(eol in db_lower for eol in ("2012", "2014", "2008", "2005"))

    if not has_mssql:
        mssql_status = "Nessun DB MSSQL"
        mssql_cost_usd_mo = 0.0
        mssql_col_str = "$0.00/mo (No MSSQL)"
    elif not os_supported:
        mssql_status = "ESCLUSO (OS Sottostante Fuori Supporto)"
        mssql_cost_usd_mo = None
        mssql_col_str = "ESCLUSO (OS Fuori Supporto)"
    elif db_is_eol:
        mssql_status = "ESCLUSO (DB MSSQL Fuori Supporto)"
        mssql_cost_usd_mo = None
        mssql_col_str = "ESCLUSO (DB Fuori Supporto)"
    else:
        mssql_status = "SUPPORTATO (DB Supportato su OS Supportato)"
        rate_per_vcpu = 283.50 if "enterprise" in db_lower else 94.50
        licensed_vcpu = count * max(4, vcpu)
        mssql_cost_usd_mo = round(licensed_vcpu * rate_per_vcpu, 2)
        mssql_col_str = f"${mssql_cost_usd_mo:,.2f}/mo"

    result = {
        "status": "success",
        "currency": "USD ($/mo)",
        "workload_name": workload_name,
        "vm_count": count,
        "vcpu_per_vm": vcpu,
        "ram_gib_per_vm": ram,
        "os_name": os_clean,
        "os_supported": os_supported,
        "mssql_edition": db_clean,
        "mssql_status": mssql_status,
        "prezzo_mese_list_usd": compute_list_usd,
        "prezzo_mese_1y_cud_usd": compute_1y_cud_usd,
        "prezzo_mese_3y_cud_usd": compute_3y_cud_usd,
        "os_usd_mo": os_cost_usd_mo if os_cost_usd_mo is not None else "ESCLUSO (OS Fuori Supporto)",
        "totale_con_os_list_usd_mo": totale_con_os_list_usd if totale_con_os_list_usd is not None else "ESCLUSO (OS Fuori Supporto)",
        "totale_con_os_1y_cud_usd_mo": totale_con_os_1y_usd if totale_con_os_1y_usd is not None else "ESCLUSO (OS Fuori Supporto)",
        "totale_con_os_3y_cud_usd_mo": totale_con_os_3y_usd if totale_con_os_3y_usd is not None else "ESCLUSO (OS Fuori Supporto)",
        "costo_mese_licenza_mssql_usd_mo": mssql_cost_usd_mo if mssql_cost_usd_mo is not None else mssql_col_str,
        "markdown_table_row": (
            f"| {workload_name} ({count}x {vcpu}vCPU/{ram}GiB) | {os_clean} | {db_clean} "
            f"| ${compute_list_usd:,.2f} | ${compute_1y_cud_usd:,.2f} | ${compute_3y_cud_usd:,.2f} "
            f"| {os_label} | {('$' + format(totale_con_os_list_usd, ',.2f') + '/mo') if totale_con_os_list_usd is not None else 'ESCLUSO (OS EOL)'} "
            f"| {mssql_col_str} |"
        ),
    }
    history = list(tool_context.state.get("sizing_calculations", []))
    history.append(result)
    tool_context.state["sizing_calculations"] = history
    return result


def calculate_agent_engine_sizing_usd(
    daily_requests: int,
    avg_input_tokens: int,
    avg_output_tokens: int,
    vcpu_count: int,
    memory_gib: int,
    tool_context: ToolContext,
) -> dict:
    """Calcola la stima di costo mensile in USD ($/mo) per il runtime Vertex AI Agent Engine e Gemini 2.5 Flash.

    Args:
        daily_requests: Richieste/conversazioni giornaliere (es. 5000).
        avg_input_tokens: Token medi di input per richiesta (es. 1500).
        avg_output_tokens: Token medi di output per richiesta (es. 600).
        vcpu_count: vCPU allocate al runtime Agent Engine (es. 2 o 4).
        memory_gib: RAM in GiB allocata al runtime Agent Engine (es. 4 o 8).

    Returns:
        Dizionario con Prezzo Mese List ($/mo), Prezzo Mese 1Y CUD ($/mo) e Prezzo Mese 3Y CUD ($/mo).
    """
    monthly_requests = max(1, int(daily_requests)) * 30
    monthly_input_m = (monthly_requests * max(100, int(avg_input_tokens))) / 1_000_000.0
    monthly_output_m = (monthly_requests * max(50, int(avg_output_tokens))) / 1_000_000.0

    hours_per_month = 730.0
    runtime_vcpu_list = round(max(1, int(vcpu_count)) * hours_per_month * 0.086, 2)
    runtime_mem_list = round(max(1, int(memory_gib)) * hours_per_month * 0.009, 2)
    llm_tokens_list = round((monthly_input_m * 0.30) + (monthly_output_m * 2.50), 2)

    total_list_usd = round(runtime_vcpu_list + runtime_mem_list + llm_tokens_list, 2)
    total_1y_cud_usd = round((runtime_vcpu_list + runtime_mem_list) * 0.72 + llm_tokens_list * 0.90, 2)
    total_3y_cud_usd = round((runtime_vcpu_list + runtime_mem_list) * 0.54 + llm_tokens_list * 0.80, 2)

    res = {
        "status": "success",
        "currency": "USD ($/mo)",
        "monthly_requests": monthly_requests,
        "prezzo_mese_list_usd": total_list_usd,
        "prezzo_mese_1y_cud_usd": total_1y_cud_usd,
        "prezzo_mese_3y_cud_usd": total_3y_cud_usd,
    }
    tool_context.state["last_agent_engine_sizing"] = res
    return res


def get_azero_session_telemetry(tool_context: ToolContext) -> dict:
    """Restituisce data/ora corrente in Italia, stato di OpenTelemetry e la traccia completa dei nodi del grafo visitati.

    Returns:
        Dizionario con lo stato della telemetria e l'elenco ordinato dei sub-agenti e tool invocati nel grafo.
    """
    now = datetime.datetime.now(ZoneInfo("Europe/Rome"))
    return {
        "status": "success",
        "current_datetime_rome": now.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "gcp_project": os.getenv("GOOGLE_CLOUD_PROJECT", "rootprj-377111"),
        "gcp_location": os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
        "telemetry": {
            "cloud_trace_enabled": True,
            "cloud_logging_enabled": True,
            "agent_engine_telemetry": os.getenv("GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY", "true"),
        },
        "graph_state_summary": {
            "total_agent_hops": tool_context.state.get("total_agent_hops", 1),
            "last_ulss_queried": tool_context.state.get("last_ulss_queried", []),
            "sla_alerts_detected": tool_context.state.get("sla_alerts_detected", []),
            "last_compliance_check": tool_context.state.get("last_compliance_check"),
            "sizing_calculations_count": len(tool_context.state.get("sizing_calculations", [])),
            "graph_execution_trace": tool_context.state.get("graph_execution_trace", []),
        },
    }


# Esportazione dei FunctionTool ADK divisi per ciascun Sub-Agente del Grafo
query_ulss_pdta_kpi_tool = FunctionTool(func=query_ulss_pdta_kpi)
check_pdta_sla_alert_tool = FunctionTool(func=check_pdta_sla_alert)

verify_acn_gdpr_rules_tool = FunctionTool(func=verify_acn_gdpr_rules)
search_crav_capitolati_tool = FunctionTool(func=search_crav_capitolati)

calculate_vm_mssql_sizing_usd_tool = FunctionTool(func=calculate_vm_mssql_sizing_usd)
calculate_agent_engine_sizing_usd_tool = FunctionTool(func=calculate_agent_engine_sizing_usd)

get_azero_session_telemetry_tool = FunctionTool(func=get_azero_session_telemetry)

ULSS_PDTA_TOOLS = [query_ulss_pdta_kpi_tool, check_pdta_sla_alert_tool]
CRAV_COMPLIANCE_TOOLS = [verify_acn_gdpr_rules_tool, search_crav_capitolati_tool]
PSN_SIZING_TOOLS = [calculate_vm_mssql_sizing_usd_tool, calculate_agent_engine_sizing_usd_tool]
ORCHESTRATOR_TOOLS = [get_azero_session_telemetry_tool]
