#!/usr/bin/env python3
"""
Server MCP (Model Context Protocol) zero-dependency per Antigravity — Azienda Zero (Regione del Veneto).
Espone 3 tool MCP direttamente dentro l'IDE Antigravity (tramite stdio JSON-RPC 2.0):
1. `azero_get_ulss_pdta_kpi`: Restituisce i KPI di presa in carico PDTA, Telemedicina PNRR, COT e liste d'attesa per le 9 ULSS del Veneto + AO Padova, AOUI Verona e IOV.
2. `azero_check_acn_gdpr_compliance`: Verifica la conformità GDPR/CDPA, clausola HIPAA ToS, Data Region Europe e qualifica ACN (QC2/QC3) per gare CRAV e workload sanitari.
3. `azero_calculate_cloud_sizing_usd`: Calcola il sizing mensile in USD ($/mo) con Prezzo Mese List, 1Y CUD, 3Y CUD, Costo Mese con OS (solo per OS supportati) e COSTO MESE LICENZA MSSQL $/MO separato (solo per DB supportati su OS supportato).
"""

import json
import sys
from typing import Any, Dict

ULSS_DATABASE: Dict[str, Dict[str, Any]] = {
    "ULSS 1 Dolomiti": {
        "codice": "ULSS1",
        "sede": "Belluno",
        "assistiti": 197000,
        "cot_attive": "4/4 (100%)",
        "pdta_oncologia_time_to_treatment_gg": 24,
        "sla_target_gg": 30,
        "telemedicina_pazienti_attivi": 4850,
        "stato_sla": "CONFORME",
        "criticita": "Copertura connettività presidi montani Cadore/Agordino da potenziare via SD-WAN.",
    },
    "ULSS 2 Marca Trevigiana": {
        "codice": "ULSS2",
        "sede": "Treviso",
        "assistiti": 885000,
        "cot_attive": "9/9 (100%)",
        "pdta_oncologia_time_to_treatment_gg": 26,
        "sla_target_gg": 30,
        "telemedicina_pazienti_attivi": 19400,
        "stato_sla": "CONFORME",
        "criticita": "Migrazione cluster DB referti storici verso Cloud SQL / PSN.",
    },
    "ULSS 3 Serenissima": {
        "codice": "ULSS3",
        "sede": "Venezia - Mestre",
        "assistiti": 612000,
        "cot_attive": "6/6 (100%)",
        "pdta_oncologia_time_to_treatment_gg": 28,
        "sla_target_gg": 30,
        "telemedicina_pazienti_attivi": 14200,
        "stato_sla": "CONFORME",
        "criticita": "Integrazione telemonitoraggio lagunare e isole con FSE 2.0.",
    },
    "ULSS 4 Veneto Orientale": {
        "codice": "ULSS4",
        "sede": "San Donà di Piave",
        "assistiti": 228000,
        "cot_attive": "3/3 (100%)",
        "pdta_oncologia_time_to_treatment_gg": 25,
        "sla_target_gg": 30,
        "telemedicina_pazienti_attivi": 5600,
        "stato_sla": "CONFORME",
        "criticita": "Picchi stagionali Pronto Soccorso litorale estivo.",
    },
    "ULSS 6 Euganea": {
        "codice": "ULSS6",
        "sede": "Padova",
        "assistiti": 932000,
        "cot_attive": "10/10 (100%)",
        "pdta_oncologia_time_to_treatment_gg": 27,
        "sla_target_gg": 30,
        "telemedicina_pazienti_attivi": 23800,
        "stato_sla": "CONFORME",
        "criticita": "Consolidamento 2 nodi SQL Server 2022 su GCP/PSN e dismissione 1 server legacy Windows 2012 R2.",
    },
    "ULSS 7 Pedemontana": {
        "codice": "ULSS7",
        "sede": "Bassano del Grappa",
        "assistiti": 358000,
        "cot_attive": "4/4 (100%)",
        "pdta_oncologia_time_to_treatment_gg": 29,
        "sla_target_gg": 30,
        "telemedicina_pazienti_attivi": 8900,
        "stato_sla": "ATTENZIONE_SOGLIA",
        "criticita": "Avvicinamento alla soglia massima di 30 gg per il PDTA Colon-Retto; richiesto potenziamento slot diagnostici.",
    },
    "ULSS 8 Berica": {
        "codice": "ULSS8",
        "sede": "Vicenza",
        "assistiti": 502000,
        "cot_attive": "5/5 (100%)",
        "pdta_oncologia_time_to_treatment_gg": 23,
        "sla_target_gg": 30,
        "telemedicina_pazienti_attivi": 12700,
        "stato_sla": "CONFORME",
        "criticita": "Completamento integrazione centralino NEA 116117.",
    },
    "ULSS 9 Scaligera": {
        "codice": "ULSS9",
        "sede": "Verona",
        "assistiti": 926000,
        "cot_attive": "9/9 (100%)",
        "pdta_oncologia_time_to_treatment_gg": 31,
        "sla_target_gg": 30,
        "telemedicina_pazienti_attivi": 21100,
        "stato_sla": "ALLERTA_SLA",
        "criticita": "Sforamento di 1 giorno (31 gg vs 30 gg target) sul Time-to-Treatment PDTA Esofago-Stomaco; attivare riequilibrio su AOUI Verona e IOV.",
    },
    "IOV - Istituto Oncologico Veneto": {
        "codice": "IOV",
        "sede": "Padova / Castelfranco Veneto",
        "assistiti": 48000,
        "cot_attive": "Hub Oncologico Regionale",
        "pdta_oncologia_time_to_treatment_gg": 18,
        "sla_target_gg": 30,
        "telemedicina_pazienti_attivi": 9500,
        "stato_sla": "ECCELLENTE",
        "criticita": "Rete molecolare e tumor board multidisciplinare regionale in espansione.",
    },
}

SUPPORTED_OS_RATES_PER_VCPU = {
    "windows server 2022": 33.58,
    "windows server 2019": 33.58,
    "rhel 9": 14.00,
    "rhel 8": 14.00,
    "ubuntu 22.04 lts": 0.0,
    "debian 12": 0.0,
}

SUPPORTED_MSSQL_RATES_PER_VCPU = {
    "sql server 2022 standard": 94.50,
    "sql server 2019 standard": 94.50,
    "sql server 2022 enterprise": 283.50,
    "none": 0.0,
}


def handle_ulss_kpi(args: Dict[str, Any]) -> Dict[str, Any]:
    ulss_filter = (args.get("ulss_name") or "all").strip().lower()
    results = {}
    for name, info in ULSS_DATABASE.items():
        if ulss_filter in ("all", "*", "") or ulss_filter in name.lower() or ulss_filter in info["codice"].lower():
            results[name] = info
    if not results:
        results = ULSS_DATABASE
    return {
        "status": "success",
        "ente_governance": "Azienda Zero - Regione del Veneto",
        "matched_count": len(results),
        "ulss_kpi": results,
    }


def handle_compliance(args: Dict[str, Any]) -> Dict[str, Any]:
    topic = (args.get("topic") or "all").strip().lower()
    return {
        "status": "success",
        "topic_queried": topic,
        "compliance_rules_azienda_zero": {
            "gdpr_and_cdpa": (
                "L'accettazione dei Terms of Service di Google Workspace / Cloud instaura un rapporto diretto "
                "regolato dal Cloud Data Processing Addendum (CDPA) standard in conformità all'art. 28 GDPR."
            ),
            "hipaa_exclusion_clarification": (
                "La clausola dell'art. 3.3(viii) dei ToS relativa a HIPAA / PHI si applica ESCLUSIVAMENTE ai soggetti "
                "e ai dati sottoposti alla giurisdizione statunitense HIPAA (USA) e NON pone alcuna limitazione "
                "contrattuale al trattamento di dati sanitari di cittadini italiani/UE regolati dal GDPR."
            ),
            "acn_data_residency_europe": (
                "Per garantire sia lo storage (Data at Rest) sia il processing (Data in Use, incluso Gemini) "
                "all'interno dell'Unione Europea secondo il catalogo ACN (Qualifica QC2), è obbligatorio configurare "
                "la policy Data Region = Europe (disponibile su edizioni Enterprise Plus / Frontline Plus e Vertex AI EU)."
            ),
            "acn_qc2_vs_qc3": (
                "I servizi SaaS/PaaS cloud pubblici dispongono di qualifica ACN QC2; per workload che richiedono "
                "vincoli specifici PSN/QC3 o interconnessione con basi dati storiche Oracle su PSN, Azienda Zero "
                "adotta l'architettura ibrida GCP su PSN tramite Cloud Interconnect dedicata e HAProxy gestito."
            ),
        },
    }


def handle_sizing(args: Dict[str, Any]) -> Dict[str, Any]:
    vm_name = args.get("workload_name", "VM-Telemedicina-ULSS")
    vcpu = max(2, int(args.get("vcpu", 8)))
    ram_gib = max(4, int(args.get("ram_gib", 32)))
    os_name = (args.get("os_name") or "Windows Server 2022").strip()
    db_name = (args.get("mssql_edition") or "SQL Server 2022 Standard").strip()

    compute_list = round((vcpu * 24.27) + (ram_gib * 3.25), 2)
    compute_1y = round(compute_list * 0.63, 2)
    compute_3y = round(compute_list * 0.45, 2)

    os_key = os_name.lower()
    os_supported = any(k in os_key for k in SUPPORTED_OS_RATES_PER_VCPU) and "2012" not in os_key and "2008" not in os_key and "centos 7" not in os_key
    os_rate = 0.0
    if os_supported:
        for k, r in SUPPORTED_OS_RATES_PER_VCPU.items():
            if k in os_key:
                os_rate = r
                break
        os_cost_mo = round(vcpu * os_rate, 2)
        totale_con_os_list = round(compute_list + os_cost_mo, 2)
        os_status = "SUPPORTATO"
    else:
        os_cost_mo = None
        totale_con_os_list = None
        os_status = "OS FUORI SUPPORTO (Costo licenza OS escluso)"

    db_key = db_name.lower()
    db_supported = (
        os_supported
        and any(k in db_key for k in SUPPORTED_MSSQL_RATES_PER_VCPU)
        and "2012" not in db_key
        and "2014" not in db_key
    )
    if db_key in ("none", "nessuno", ""):
        mssql_cost_mo = 0.0
        db_status = "NESSUN DB MSSQL"
    elif db_supported:
        db_rate = 94.50 if "standard" in db_key else 283.50
        mssql_cost_mo = round(max(4, vcpu) * db_rate, 2)
        db_status = "SUPPORTATO SU OS SUPPORTATO"
    else:
        mssql_cost_mo = None
        db_status = "ESCLUSO (DB fuori supporto o OS sottostante fuori supporto)"

    return {
        "status": "success",
        "currency": "USD ($/mo)",
        "workload_name": vm_name,
        "vcpu": vcpu,
        "ram_gib": ram_gib,
        "os_name": os_name,
        "os_support_status": os_status,
        "mssql_edition": db_name,
        "mssql_support_status": db_status,
        "prezzo_mese_list_usd": compute_list,
        "prezzo_mese_1y_cud_usd": compute_1y,
        "prezzo_mese_3y_cud_usd": compute_3y,
        "os_usd_mo": os_cost_mo if os_cost_mo is not None else "N/A (OS Fuori Supporto)",
        "totale_con_os_usd_mo": totale_con_os_list if totale_con_os_list is not None else "N/A (OS Fuori Supporto)",
        "costo_mese_licenza_mssql_usd_mo": mssql_cost_mo if mssql_cost_mo is not None else "N/A (DB/OS Fuori Supporto)",
    }


TOOLS_SPEC = [
    {
        "name": "azero_get_ulss_pdta_kpi",
        "description": "Restituisce i KPI di presa in carico PDTA, stato COT e Telemedicina PNRR per le 9 ULSS della Regione Veneto e IOV coordinate da Azienda Zero.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ulss_name": {
                    "type": "string",
                    "description": "Nome o codice della ULSS (es. 'ULSS 6 Euganea', 'ULSS 2', 'ULSS 9', oppure 'all' per tutte).",
                }
            },
        },
    },
    {
        "name": "azero_check_acn_gdpr_compliance",
        "description": "Verifica le regole ufficiali di Azienda Zero su GDPR/CDPA, clausola HIPAA ToS, Data Region Europe e qualifica ACN QC2/QC3.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "Tema di compliance da verificare ('all', 'gdpr', 'hipaa', 'acn', 'data_region').",
                }
            },
        },
    },
    {
        "name": "azero_calculate_cloud_sizing_usd",
        "description": "Calcola il sizing mensile in USD ($/mo) con Prezzo Mese List, 1Y CUD, 3Y CUD, OS $/mo (solo per OS supportati) e COSTO MESE LICENZA MSSQL $/MO separato (solo per DB supportati su OS supportato).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workload_name": {"type": "string", "description": "Nome del server o workload ULSS."},
                "vcpu": {"type": "integer", "description": "Numero di vCPU (es. 8)."},
                "ram_gib": {"type": "integer", "description": "Memoria RAM in GiB (es. 32)."},
                "os_name": {"type": "string", "description": "Sistema Operativo (es. 'Windows Server 2022', 'RHEL 9', 'Windows Server 2012 R2')."},
                "mssql_edition": {"type": "string", "description": "Edizione MS SQL Server (es. 'SQL Server 2022 Standard', 'SQL Server 2012', 'None')."},
            },
            "required": ["workload_name", "vcpu", "ram_gib", "os_name", "mssql_edition"],
        },
    },
]


def main():
    for raw_line in sys.stdin:
        line = raw_line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except Exception:
            continue

        msg_id = msg.get("id")
        method = msg.get("method", "")
        params = msg.get("params") or {}

        if method == "initialize":
            resp = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "azero-crav-governance-mcp", "version": "1.0.0"},
                },
            }
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        elif method == "tools/list":
            resp = {"jsonrpc": "2.0", "id": msg_id, "result": {"tools": TOOLS_SPEC}}
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        elif method == "tools/call":
            t_name = params.get("name", "")
            t_args = params.get("arguments") or {}
            if t_name == "azero_get_ulss_pdta_kpi":
                out = handle_ulss_kpi(t_args)
            elif t_name == "azero_check_acn_gdpr_compliance":
                out = handle_compliance(t_args)
            elif t_name == "azero_calculate_cloud_sizing_usd":
                out = handle_sizing(t_args)
            else:
                out = {"error": f"Unknown tool: {t_name}"}
            resp = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"content": [{"type": "text", "text": json.dumps(out, indent=2, ensure_ascii=False)}]},
            }
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        elif msg_id is not None:
            resp = {"jsonrpc": "2.0", "id": msg_id, "result": {}}
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
