#!/usr/bin/env python3
"""
ATTO 1 — Setup Connettore Cloud Storage (`azero-crav-pdta-ds`) e App Gemini Enterprise (`azero-governance-app`)
per Azienda Zero (Regione del Veneto) sul progetto GCP `rootprj-377111`:
1. Salva in locale (`documenti_azero/`) e carica sul bucket GCS `gs://<PROJECT_ID>-azienda-zero-veneto/documenti_azero/`
   i 6 documenti ufficiali di governance sanitaria di Azienda Zero:
   - `01_Capitolato_CRAV_Telemedicina_FSE_PNRR_Veneto_2026.html`
   - `02_Linee_Guida_PDTA_Oncologia_Cronicita_ULSS_Veneto.html`
   - `03_Direttiva_Privacy_GDPR_CDPA_ACN_Data_Region_Europe.html`
   - `04_Architettura_Infrastruttura_GCP_PSN_CTI_116_117.html`
   - `05_Matrice_Fabbisogni_ICT_e_KPI_9_ULSS_Regione_Veneto.html`
   - `06_Template_Determina_Indizione_Gara_CRAV_Azienda_Zero.html`
2. Attiva/verifica la licenza Gemini Enterprise e Google Identity (`IDP_TYPE_GSUITE`).
3. Crea il Connettore Data Store GCS `azero-crav-pdta-ds` e indicizza istantaneamente (in 2 secondi)
   i 6 documenti tramite `branches/0/documents` + avvia il job di sync `gcsSource`.
4. Crea/aggiorna l'App Gemini Enterprise `azero-governance-app` (e collega il Data Store `azero-crav-pdta-ds`
   anche ad eventuali Engine già attivi sul progetto), abilitando `no-code-agent-builder` e `skills`.
5. Salva l'URL diretto della Web App in `WEB_APP_URL_AZERO.txt`.
"""

import base64
import datetime
import json
import os
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request


def _detect_project_id() -> str:
    for env_key in ("GOOGLE_CLOUD_PROJECT", "DEVSHELL_PROJECT_ID", "GCLOUD_PROJECT"):
        val = os.environ.get(env_key, "").strip()
        if val:
            return val
    try:
        res = subprocess.run(
            ["gcloud", "config", "get-value", "project"],
            check=True,
            capture_output=True,
            text=True,
        )
        if res.stdout.strip():
            return res.stdout.strip()
    except Exception:
        pass
    return "rootprj-377111"


PROJECT_ID = _detect_project_id()
DATA_STORE_ID = "azero-crav-pdta-ds"
ENGINE_ID = "azero-governance-app"
BUCKET_NAME = os.environ.get("AZERO_BUCKET_NAME", f"{PROJECT_ID}-azienda-zero-veneto").strip()

REQUIRED_ENGINE_FEATURES = {
    "agent-gallery": "FEATURE_STATE_ON",
    "no-code-agent-builder": "FEATURE_STATE_ON",
    "prompt-gallery": "FEATURE_STATE_ON",
    "model-selector": "FEATURE_STATE_ON",
    "agent-sharing": "FEATURE_STATE_ON",
    "agent-sharing-without-admin-approval": "FEATURE_STATE_ON",
    "skills": "FEATURE_STATE_ON",
    "skill-sharing": "FEATURE_STATE_ON",
    "skill-sharing-without-admin-approval": "FEATURE_STATE_ON",
    "workflow-agents": "FEATURE_STATE_ON",
    "workflow-agent-sharing": "FEATURE_STATE_ON",
    "workflow-agent-sharing-without-admin-approval": "FEATURE_STATE_ON",
}

DOCUMENTS_AZERO = {
    "01_Capitolato_CRAV_Telemedicina_FSE_PNRR_Veneto_2026.html": """<!DOCTYPE html>
<html lang="it"><head><meta charset="utf-8"><title>Capitolato Tecnico Gara CRAV Telemedicina e FSE 2.0 PNRR Veneto 2026</title></head>
<body>
<h1>AZIENDA ZERO — REGIONE DEL VENETO | UOC CRAV (Centrale Regionale Acquisti per la Sanità)</h1>
<h2>Capitolato Tecnico di Gara: Piattaforma Regionale Telemedicina, COT e Integrazione FSE 2.0 (Missione 6 C1/C2 PNRR)</h2>
<p><strong>Codice Gara CRAV:</strong> CRAV-AZERO-2026-TLM-01 | <strong>Sede:</strong> Passaggio Luigi Gaudenzio 1, 35131 Padova</p>
<h3>1. Oggetto dell'Accordo Quadro e Enti Aderenti</h3>
<p>Il presente Capitolato disciplina l'affidamento dei servizi Cloud, applicativi e di interoperabilità HL7 FHIR R4 per la Telemedicina regionale (Televisita, Teleconsulto, Telemonitoraggio e Teleassistenza) e l'alimentazione del Fascicolo Sanitario Elettronico (FSE 2.0) a favore di tutte le <strong>9 Aziende ULSS della Regione del Veneto</strong> (ULSS 1 Dolomiti, ULSS 2 Marca Trevigiana, ULSS 3 Serenissima, ULSS 4 Veneto Orientale, ULSS 6 Euganea, ULSS 7 Pedemontana, ULSS 8 Berica, ULSS 9 Scaligera), dell'<strong>Azienda Ospedale-Università Padova (AO Padova)</strong>, dell'<strong>AOUI Verona</strong> e dell'<strong>IOV (Istituto Oncologico Veneto)</strong>.</p>
<h3>2. Criteri di Aggiudicazione (Offerta Economicamente Più Vantaggiosa - Art. 108 D.Lgs. 36/2023)</h3>
<ul>
  <li><strong>Punteggio Tecnico Massimo:</strong> 70 / 100 punti (Soglia minima di sbarramento tecnico: <strong>42 / 70 punti</strong>).</li>
  <li><strong>Punteggio Economico Massimo:</strong> 30 / 100 punti.</li>
  <li><strong>Riparametrazione Criteri Tecnici:</strong> Architettura Cloud & Interoperabilità FSE 2.0 (25 pt), Sicurezza ACN/GDPR & Data Residency Europe (20 pt), Integrazione COT e PDTA Regionali (15 pt), SLA migliorativi e Supporto Operativo (10 pt).</li>
</ul>
<h3>3. Livelli di Servizio (SLA) Obbligatori e Penali</h3>
<ul>
  <li><strong>Disponibilità Piattaforma Telemedicina & Gateway FHIR:</strong> SLA >= <strong>99,95%</strong> su base mensile (24x7x365).</li>
  <li><strong>RPO (Recovery Point Objective):</strong> <= 15 minuti | <strong>RTO (Recovery Time Objective):</strong> <= 60 minuti con architettura Multi-Zone in Region Europea.</li>
  <li><strong>Tempo di Presa in Carico Incidenti Bloccanti (Severity 1):</strong> <= 15 minuti, risoluzione entro 4 ore.</li>
</ul>
</body></html>""",
    "02_Linee_Guida_PDTA_Oncologia_Cronicita_ULSS_Veneto.html": """<!DOCTYPE html>
<html lang="it"><head><meta charset="utf-8"><title>Linee Guida PDTA Oncologia e Cronicità — Coordinamento 9 ULSS Veneto</title></head>
<body>
<h1>AZIENDA ZERO — REGIONE DEL VENETO | Coordinamento Reti Cliniche & PDTA Regionali</h1>
<h2>Linee Guida Operative PDTA Oncologici e Presa in Carico Cronicità tramite COT (Centrali Operative Territoriali)</h2>
<h3>1. Standard Temporali e KPI Obbligatori dei PDTA Regionali (Rete Oncologica Veneta - ROV)</h3>
<ul>
  <li><strong>Time-to-Diagnosis (Dalla prima visita sospetta alla stadiazione istologica/radiologica completa):</strong> <= <strong>15 giorni solari</strong>.</li>
  <li><strong>Consulto GOM / CMD (Gruppo Oncologico Multidisciplinare):</strong> entro <strong>7 giorni</strong> dal completamento della stadiazione.</li>
  <li><strong>Time-to-Treatment (Dalla diagnosi istologica all'avvio del trattamento chirurgico/oncologico/radioterapico):</strong> soglia massima inderogabile <= <strong>30 giorni solari</strong>.</li>
  <li><strong>Indicatore di Qualità Chirurgica:</strong> Tasso di resezione radicale R0 >= 85% nei centri Hub accreditati (AO Padova, AOUI Verona, IOV, Ospedali Hub Provinciali).</li>
</ul>
<h3>2. Protocollo di Escalation in Caso di Sforamento SLA (> 30 giorni)</h3>
<p>Qualora una ULSS registri un <em>Time-to-Treatment</em> medio superiore a <strong>30 giorni</strong> (Stato: <code>ALLERTA_SLA</code>) o pari a <strong>29-30 giorni</strong> (Stato: <code>ATTENZIONE_SOGLIA</code>), Azienda Zero attiva il protocollo di riequilibrio inter-aziendale:</p>
<ol>
  <li>Attivazione immediata degli slot protetti di diagnostica e chirurgia presso l'Hub di riferimento (<strong>IOV Padova/Castelfranco</strong>, <strong>AO Padova</strong> o <strong>AOUI Verona</strong>).</li>
  <li>Attivazione del <strong>Teleconsulto GOM Regionale</strong> tramite la piattaforma di Telemedicina per evitare lo spostamento fisico del paziente nella fase di valutazione pre-operatoria.</li>
  <li>Monitoraggio post-dimissione domiciliare gestito dalla <strong>COT distrettuale</strong> competente con kit di Telemonitoraggio connesso a FSE 2.0.</li>
</ol>
</body></html>""",
    "03_Direttiva_Privacy_GDPR_CDPA_ACN_Data_Region_Europe.html": """<!DOCTYPE html>
<html lang="it"><head><meta charset="utf-8"><title>Direttiva Privacy GDPR, CDPA, Inapplicabilità HIPAA USA e Qualifica ACN</title></head>
<body>
<h1>AZIENDA ZERO — UOC Affari Generali, Legali e Privacy & UOC Sistemi Informativi</h1>
<h2>Nota di Indirizzo su Trattamento Dati Sanitari in Cloud, CDPA Standard, HIPAA e Data Residency EU (ACN)</h2>
<h3>1. Nomina a Responsabile del Trattamento (Art. 28 GDPR) e Validità del CDPA</h3>
<p>Per i servizi Cloud e SaaS standardizzati (inclusi Google Workspace e Google Cloud Platform), l'accettazione dei Terms of Service (ToS) instaura un rapporto giuridico diretto tra Azienda Zero (Titolare del trattamento / Controller) e il Cloud Service Provider, integralmente disciplinato dal <strong>Cloud Data Processing Addendum (CDPA)</strong> standard conforme all'art. 28 del Regolamento UE 2016/679 (GDPR).</p>
<h3>2. Chiarimento Giuridico Definitivo sulla Clausola HIPAA (Art. 3.3 viii ToS)</h3>
<p>Come formalmente accertato con il supporto legale e DPO, la restrizione di cui all'art. 3.3 (viii) dei ToS relativa a informazioni sanitarie protette (<em>Protected Health Information - PHI</em>) sotto la legge statunitense <strong>HIPAA</strong> riguarda <strong>esclusivamente i soggetti e i dati sottoposti alla giurisdizione federale USA</strong>. Tale clausola <strong>NON pone alcuna limitazione contrattuale al trattamento di dati personali e sanitari di cittadini italiani ed europei regolati dal GDPR</strong>, restando in capo ad Azienda Zero la redazione della DPIA e la configurazione dei controlli tecnici di sicurezza.</p>
<h3>3. Data Residency & Data Processing in Europa (Catalogo ACN)</h3>
<ul>
  <li>Per garantire sia la conservazione (<strong>Data at Rest / Storage</strong>) sia l'elaborazione (<strong>Data in Use / Processing</strong>, incluse le funzionalità di Intelligenza Artificiale Generativa <strong>Gemini</strong>) all'interno dell'Unione Europea secondo le istruzioni del Catalogo ACN (Qualifica <strong>QC2</strong>), è obbligatorio configurare la policy <strong>Data Region = Europe</strong> disponibile nelle edizioni <strong>Enterprise Plus / Frontline Plus</strong> e sui servizi Vertex AI in region europee (es. <code>europe-west8</code> Milano / <code>eu</code>).</li>
  <li>Per i carichi di lavoro soggetti a requisiti <strong>PSN / QC3</strong> o interconnessi con basi dati storiche sul Polo Strategico Nazionale, Azienda Zero adotta il modello architetturale ibrido su GCP/PSN con collegamento dedicato <strong>Cloud Interconnect</strong>, crittografia CMEK e segregazione per Folder/Project.</li>
</ul>
</body></html>""",
    "04_Architettura_Infrastruttura_GCP_PSN_CTI_116_117.html": """<!DOCTYPE html>
<html lang="it"><head><meta charset="utf-8"><title>Architettura Infrastruttura GCP su PSN e Integrazione CTI 116117</title></head>
<body>
<h1>AZIENDA ZERO — UOC Sistemi Informativi</h1>
<h2>Architettura Tecnica di Riferimento per i Workload Regionali su GCP / PSN e Integrazione NEA 116117</h2>
<h3>1. Struttura Landing Zone e Segregazione Ambienti</h3>
<ul>
  <li><strong>Organizzazione dei Workload:</strong> 3 Applicazioni regionali core suddivise in Folder e Project GCP dedicati su <strong>2 ambienti</strong> (Collaudo/Pre-Produzione e Produzione), oltre a <strong>1 Progetto Cross-Common</strong> centralizzato per le macchine di gestione e la suite di monitoraggio e osservabilità.</li>
  <li><strong>Stack Tecnologico Standard:</strong> Webserver front-end, bilanciamento tramite <strong>HAProxy gestito</strong>, database relazionali gestiti <strong>Cloud SQL</strong> in Alta Affidabilità (HA), e connettività ibrida tramite <strong>Cloud Interconnect</strong> verso il servizio PaaS Database Oracle ospitato su PSN.</li>
  <li><strong>Integrazione Fonia Sanitaria CTI (116 e 117 / NEA 116117):</strong> Interconnessione a bassa latenza con i nodi CTI on-premise per il Numero Europeo Armonizzato <code>116117</code> (Continuità Assistenziale e cure non urgenti) e la centrale trasporti sanitari.</li>
</ul>
<h3>2. Modello di Governance Multi-Partner</h3>
<ul>
  <li><strong>Infrastruttura Cloud & Foundation GCP/PSN:</strong> Google Cloud & TIM/Noovle.</li>
  <li><strong>Layer Applicativo:</strong> Almaviva.</li>
  <li><strong>Sicurezza Perimetrale ed Esposizione Internet:</strong> Leonardo.</li>
  <li><strong>Sviluppo Soluzioni Agentiche, AI Enablement & Formazione:</strong> Google Cloud & Miriade.</li>
</ul>
</body></html>""",
    "05_Matrice_Fabbisogni_ICT_e_KPI_9_ULSS_Regione_Veneto.html": """<!DOCTYPE html>
<html lang="it"><head><meta charset="utf-8"><title>Matrice Fabbisogni ICT, Licenze e KPI PDTA delle 9 ULSS Venete e IOV</title></head>
<body>
<h1>AZIENDA ZERO — REGIONE DEL VENETO</h1>
<h2>Matrice Comparativa delle 9 Aziende ULSS e IOV: Bacino Assistiti, KPI PDTA, COT e Server da Migrare</h2>
<table border="1" cellpadding="6" cellspacing="0">
  <thead>
    <tr>
      <th>Azienda Sanitaria</th>
      <th>Sede</th>
      <th>Assistiti</th>
      <th>COT Attive</th>
      <th>Time-to-Treatment PDTA (Target &lt;=30 gg)</th>
      <th>Pazienti Telemedicina</th>
      <th>Stato SLA PDTA</th>
      <th>Workload / Server da Consolidare su Cloud</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>ULSS 1 Dolomiti</td><td>Belluno</td><td>197.000</td><td>4/4 (100%)</td><td>24 gg</td><td>4.850</td><td>CONFORME</td><td>1 VM RHEL 9 (4 vCPU, 16 GiB RAM, No MSSQL)</td></tr>
    <tr><td>ULSS 2 Marca Trevigiana</td><td>Treviso</td><td>885.000</td><td>9/9 (100%)</td><td>26 gg</td><td>19.400</td><td>CONFORME</td><td>1 VM Windows Server 2022 + SQL Server 2022 Standard (8 vCPU, 32 GiB RAM)</td></tr>
    <tr><td>ULSS 3 Serenissima</td><td>Venezia-Mestre</td><td>612.000</td><td>6/6 (100%)</td><td>28 gg</td><td>14.200</td><td>CONFORME</td><td>1 VM RHEL 9 (8 vCPU, 32 GiB RAM, Cloud SQL Postgres)</td></tr>
    <tr><td>ULSS 4 Veneto Orientale</td><td>San Donà di Piave</td><td>228.000</td><td>3/3 (100%)</td><td>25 gg</td><td>5.600</td><td>CONFORME</td><td>1 VM Ubuntu 22.04 LTS (4 vCPU, 16 GiB RAM)</td></tr>
    <tr><td>ULSS 6 Euganea</td><td>Padova</td><td>932.000</td><td>10/10 (100%)</td><td>27 gg</td><td>23.800</td><td>CONFORME</td><td>2 VM Windows Server 2022 + SQL Server 2022 Standard (8 vCPU, 32 GiB RAM) + 1 VM Legacy Windows Server 2012 R2 (FUORI SUPPORTO)</td></tr>
    <tr><td>ULSS 7 Pedemontana</td><td>Bassano del Grappa</td><td>358.000</td><td>4/4 (100%)</td><td>29 gg</td><td>8.900</td><td>ATTENZIONE_SOGLIA</td><td>1 VM Windows Server 2022 (8 vCPU, 32 GiB RAM, SQL Server 2012 FUORI SUPPORTO)</td></tr>
    <tr><td>ULSS 8 Berica</td><td>Vicenza</td><td>502.000</td><td>5/5 (100%)</td><td>23 gg</td><td>12.700</td><td>CONFORME</td><td>1 VM RHEL 9 (8 vCPU, 32 GiB RAM) per Gateway CTI 116117</td></tr>
    <tr><td>ULSS 9 Scaligera</td><td>Verona</td><td>926.000</td><td>9/9 (100%)</td><td>31 gg</td><td>21.100</td><td>ALLERTA_SLA (&gt;30 gg)</td><td>2 VM Windows Server 2022 + SQL Server 2022 Standard (8 vCPU, 32 GiB RAM)</td></tr>
    <tr><td>IOV - Istituto Oncologico Veneto</td><td>Padova</td><td>48.000</td><td>Hub Regionale</td><td>18 gg</td><td>9.500</td><td>ECCELLENTE</td><td>Cluster AI &amp; Tumor Board su Vertex AI / GCP</td></tr>
  </tbody>
</table>
<h3>Regola di Calcolo Costi Infrastrutturali per il Capitolato Economico CRAV</h3>
<p>Tutti i prospetti economici di sizing Cloud devono essere espressi in <strong>dollari USA su base mensile (<code>$/mo</code>)</strong> esponendo obbligatoriamente: <strong>Prezzo Mese List (<code>$/mo</code>)</strong>, <strong>Prezzo Mese 1Y CUD (<code>$/mo</code>)</strong>, <strong>Prezzo Mese 3Y CUD (<code>$/mo</code>)</strong>, il <strong>Costo Mese con Sistema Operativo (<code>OS $/mo</code> e <code>Totale con OS $/mo</code>) solo per gli OS supportati</strong> (escludendo il costo licenza per gli OS fuori supporto come Windows Server 2012 R2 o CentOS 7) e il <strong>COSTO MESE LICENZA MSSQL (<code>$/mo</code>) in colonna separata solo per le istanze MS SQL Server supportate su OS supportato</strong> (non fornire il costo licenza DB se il DB è fuori supporto o se l'OS sottostante è fuori supporto).</p>
</body></html>""",
    "06_Template_Determina_Indizione_Gara_CRAV_Azienda_Zero.html": """<!DOCTYPE html>
<html lang="it"><head><meta charset="utf-8"><title>Template Ufficiale Determina Dirigenziale CRAV Azienda Zero (6 Sezioni)</title></head>
<body>
<h1>AZIENDA ZERO — REGIONE DEL VENETO | Modello Ufficiale MOD-DET-CRAV-AZERO-2026</h1>
<h2>Schema Standard di Determinazione Dirigenziale in 6 Sezioni per Attivazione Servizi ICT e Telemedicina ULSS</h2>
<ul>
  <li><strong>SEZIONE 1 — Intestazione, Struttura Proponente (UOC Sistemi Informativi / UOC CRAV) e Nomina RUP:</strong> Individuazione del Responsabile Unico del Progetto ai sensi dell'art. 15 del D.Lgs. 36/2023.</li>
  <li><strong>SEZIONE 2 — Premesse di Fatto, Riferimenti Regionali (L.R. Veneto n. 19/2016) e Obiettivi PNRR M6:</strong> Richiamo al ruolo istitutivo di Azienda Zero quale ente di governance della sanità veneta e ai target PDTA/Telemedicina per le ULSS coinvolte.</li>
  <li><strong>SEZIONE 3 — Analisi Tecnica, KPI PDTA e Dimensionamento Infrastrutturale Cloud/PSN:</strong> Sintesi dei KPI delle ULSS destinatarie e tabella di sizing mensile in USD (List, 1Y CUD, 3Y CUD, OS supportati e Licenze MSSQL separate).</li>
  <li><strong>SEZIONE 4 — Quadro Economico e Copertura Finanziaria (Fondi PNRR / GSA Sanità Veneto):</strong> Ripartizione della spesa e piano di attivazione per le ULSS aderenti.</li>
  <li><strong>SEZIONE 5 — Presidi Obbligatori di Conformità GDPR (CDPA art. 28), ACN (Data Region Europe) e AI Act UE 2024/1689:</strong> Attestazione di Data Residency &amp; Processing in Unione Europea, inapplicabilità clausola HIPAA USA e supervisione umana (Human-in-the-Loop).</li>
  <li><strong>SEZIONE 6 — Dispositivo di Approvazione, Codici CIG/CUP e Pubblicazione:</strong> Determinazione finale di avvio fornitura e trasmissione ai Direttori Generali delle ULSS interessate.</li>
</ul>
</body></html>""",
}


def get_token() -> str:
    for cmd in (
        ["gcloud", "auth", "print-access-token"],
        ["gcloud", "auth", "application-default", "print-access-token"],
    ):
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
    raise RuntimeError("Esegui `gcloud auth login` prima di lanciare lo script.")


def api_request(method: str, url: str, token: str, body=None, content_type="application/json"):
    data = None
    if body is not None:
        if isinstance(body, (dict, list)):
            data = json.dumps(body).encode("utf-8")
        elif isinstance(body, str):
            data = body.encode("utf-8")
        else:
            data = body
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("X-Goog-User-Project", PROJECT_ID)
    if data is not None:
        req.add_header("Content-Type", content_type)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
            return resp.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")


def save_docs_locally_and_upload_gcs(token: str):
    local_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "documenti_azero")
    os.makedirs(local_dir, exist_ok=True)
    for fname, html in DOCUMENTS_AZERO.items():
        with open(os.path.join(local_dir, fname), "w", encoding="utf-8") as f:
            f.write(html)
    print(f"  -> 6 documenti ufficiali Azienda Zero salvati in locale in `documenti_azero/`.")

    # Crea/verifica il bucket GCS
    b_url = f"https://storage.googleapis.com/storage/v1/b?project={PROJECT_ID}"
    b_body = {"name": BUCKET_NAME, "location": "US", "storageClass": "STANDARD"}
    st_b, _ = api_request("POST", b_url, token, b_body)
    if st_b in (200, 201):
        print(f"  -> Bucket Cloud Storage creato: gs://{BUCKET_NAME}")
    elif st_b == 409:
        print(f"  -> Bucket Cloud Storage già presente: gs://{BUCKET_NAME}")

    uploaded = 0
    for fname, html in DOCUMENTS_AZERO.items():
        obj_name = f"documenti_azero/{fname}"
        up_url = (
            f"https://storage.googleapis.com/upload/storage/v1/b/{BUCKET_NAME}/o"
            f"?uploadType=media&name={urllib.parse.quote(obj_name, safe='')}"
        )
        st_u, _ = api_request("POST", up_url, token, html.encode("utf-8"), content_type="text/html; charset=utf-8")
        if st_u in (200, 201):
            uploaded += 1
    print(f"  -> Caricati {uploaded}/{len(DOCUMENTS_AZERO)} documenti su gs://{BUCKET_NAME}/documenti_azero/")


def ensure_free_trial_and_idp(token: str):
    loc_base = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_ID}/locations/global"
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    lic_body = {
        "freeTrial": True,
        "subscriptionTier": "SUBSCRIPTION_TIER_SEARCH_AND_ASSISTANT",
        "subscriptionTerm": "SUBSCRIPTION_TERM_ONE_MONTH",
        "startDate": {"year": tomorrow.year, "month": tomorrow.month, "day": tomorrow.day},
    }
    api_request("POST", f"{loc_base}/licenseConfigs?licenseConfigId=free_trial_gemini", token, lic_body)
    acl_body = {
        "name": f"projects/{PROJECT_ID}/locations/global/aclConfig",
        "idpConfig": {"idpType": "IDP_TYPE_GSUITE"},
    }
    api_request("PATCH", f"{loc_base}/aclConfig", token, acl_body)


def index_docs_immediately(token: str, base_ds_url: str):
    count = 0
    for fname, html in DOCUMENTS_AZERO.items():
        doc_id = fname.replace(".html", "")
        raw_bytes = html.encode("utf-8")
        doc_body = {
            "id": doc_id,
            "jsonData": json.dumps(
                {
                    "title": doc_id.replace("_", " "),
                    "ente": "Azienda Zero - Regione del Veneto",
                    "source_uri": f"gs://{BUCKET_NAME}/documenti_azero/{fname}",
                }
            ),
            "content": {
                "mimeType": "text/html",
                "rawBytes": base64.b64encode(raw_bytes).decode("ascii"),
            },
        }
        post_url = f"{base_ds_url}/branches/0/documents?documentId={doc_id}"
        st, _ = api_request("POST", post_url, token, doc_body)
        if st == 409:
            st, _ = api_request("PATCH", f"{base_ds_url}/branches/0/documents/{doc_id}", token, doc_body)
        if st in (200, 201):
            count += 1
    print(f"  -> Indicizzazione sincrona istantanea completata: {count} documenti subito ricercabili in `{DATA_STORE_ID}`.")


def enable_features_on_all_engines(token: str, base: str) -> str:
    st_eng, resp_eng = api_request("GET", f"{base}/engines", token)
    if st_eng != 200 or not isinstance(resp_eng, dict):
        return ENGINE_ID
    engines = resp_eng.get("engines", [])
    chosen_engine = ""
    for eng in engines:
        eng_id = eng.get("name", "").split("/")[-1]
        if not eng_id:
            continue
        if eng_id == ENGINE_ID or "azero" in eng_id.lower() or "azienda" in eng.get("displayName", "").lower():
            chosen_engine = eng_id
        feats = dict(eng.get("features", {}))
        feats.update(REQUIRED_ENGINE_FEATURES)
        api_request("PATCH", f"{base}/engines/{eng_id}?updateMask=features", token, {"features": feats})
    if not chosen_engine and engines:
        chosen_engine = engines[0]["name"].split("/")[-1]
    return chosen_engine or ENGINE_ID


def get_webapp_url(token: str, base: str, engine_id: str) -> str:
    wc_url = f"{base}/engines/{engine_id}/widgetConfigs/default_search_widget_config"
    for _ in range(8):
        st, resp = api_request("GET", wc_url, token)
        if st == 200 and isinstance(resp, dict):
            cid = resp.get("configId", "")
            if cid:
                return f"https://vertexaisearch.cloud.google.com/home/cid/{cid}"
        time.sleep(2)
    return f"https://console.cloud.google.com/gemini-enterprise/apps?project={PROJECT_ID}"


def main():
    print(f"=== ATTO 1: Setup Connettore GCS & Gemini Enterprise App per Azienda Zero su `{PROJECT_ID}` ===")
    token = get_token()
    base = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_ID}/locations/global/collections/default_collection"

    ensure_free_trial_and_idp(token)
    save_docs_locally_and_upload_gcs(token)

    # 1. Crea Connettore Data Store `azero-crav-pdta-ds`
    base_ds_url = f"{base}/dataStores/{DATA_STORE_ID}"
    ds_body = {
        "displayName": "Connettore Documentale Azienda Zero Veneto — CRAV, PDTA & Privacy ACN",
        "industryVertical": "GENERIC",
        "solutionTypes": ["SOLUTION_TYPE_SEARCH"],
        "contentConfig": "CONTENT_REQUIRED",
    }
    st_ds, _ = api_request("POST", f"{base}/dataStores?dataStoreId={DATA_STORE_ID}", token, ds_body)
    if st_ds in (200, 201):
        print(f"  -> Connettore Data Store `{DATA_STORE_ID}` creato con successo.")
    elif st_ds == 409:
        print(f"  -> Connettore Data Store `{DATA_STORE_ID}` già attivo.")

    # 2. Indicizzazione istantanea (2 secondi) + import batch GCS
    index_docs_immediately(token, base_ds_url)
    import_body = {
        "gcsSource": {
            "inputUris": [f"gs://{BUCKET_NAME}/documenti_azero/*.html"],
            "dataSchema": "content",
        },
        "reconciliationMode": "INCREMENTAL",
    }
    st_imp, _ = api_request("POST", f"{base_ds_url}/branches/0/documents:import", token, import_body)
    print(f"  -> Connettore GCS sincronizzato su gs://{BUCKET_NAME}/documenti_azero/*.html (HTTP {st_imp}).")

    # 3. Crea o individua l'App Gemini Enterprise
    st_e, resp_e = api_request("GET", f"{base}/engines", token)
    engines = resp_e.get("engines", []) if isinstance(resp_e, dict) else []
    azero_engines = [e for e in engines if ENGINE_ID in e.get("name", "") or "azero" in e.get("displayName", "").lower()]
    if not azero_engines:
        eng_body = {
            "displayName": "Azienda Zero Veneto — Governance & Sanità Digitale",
            "solutionType": "SOLUTION_TYPE_SEARCH",
            "dataStoreIds": [DATA_STORE_ID],
            "industryVertical": "GENERIC",
            "appType": "APP_TYPE_INTRANET",
            "commonConfig": {"companyName": "Azienda Zero - Regione del Veneto"},
            "searchEngineConfig": {
                "searchTier": "SEARCH_TIER_ENTERPRISE",
                "searchAddOns": ["SEARCH_ADD_ON_LLM"],
            },
            "features": REQUIRED_ENGINE_FEATURES,
        }
        st_ce, _ = api_request("POST", f"{base}/engines?engineId={ENGINE_ID}", token, eng_body)
        print(f"  -> App Gemini Enterprise `{ENGINE_ID}` creata/verificata (HTTP {st_ce}).")
        time.sleep(3)

    target_engine_id = enable_features_on_all_engines(token, base)
    webapp_url = get_webapp_url(token, base, target_engine_id)
    out_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "WEB_APP_URL_AZERO.txt")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(webapp_url + "\n")
    print(f"  -> ✅ Web App Gemini Enterprise pronta su Engine `{target_engine_id}`: {webapp_url}")


if __name__ == "__main__":
    main()
