#!/usr/bin/env bash
# ==============================================================================
# Script 1-Click per Google Cloud Shell (Progetto `rootprj-377111`)
# Demo Azienda Zero (Regione del Veneto) — Gemini Enterprise + ADK Graph & Eval
#
# Modalità d'uso in Cloud Shell:
#   ./setup_cloudshell_azero.sh                 # Setup Connettore GCS + App GE + Agente GE App + venv ADK
#   ./setup_cloudshell_azero.sh --with-adk      # Come sopra + Deploy Multi-Agente ADK su Agent Engine & Agent Registry + Eval Cloud
#   ./setup_cloudshell_azero.sh --web-only      # Avvia subito `adk web --port 8080 --allow_origins "*"` in Cloud Shell
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

WITH_ADK=false
WEB_ONLY=false
START_WEB=true

for arg in "$@"; do
  case "$arg" in
    --with-adk|--instructor|--all)
      WITH_ADK=true
      ;;
    --web-only)
      WEB_ONLY=true
      ;;
    --no-web)
      START_WEB=false
      ;;
  esac
done

export PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-rootprj-377111}"
export GOOGLE_CLOUD_PROJECT="${PROJECT_ID}"
export GOOGLE_CLOUD_QUOTA_PROJECT="${PROJECT_ID}"
export GOOGLE_CLOUD_LOCATION="us-central1"
export GOOGLE_GENAI_USE_VERTEXAI=TRUE
export GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY=true
export OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=true
export ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS=true

gcloud config set project "${PROJECT_ID}" --quiet >/dev/null 2>&1 || true

echo "================================================================================"
echo "🏥 AZIENDA ZERO (REGIONE DEL VENETO) — SETUP CLOUD SHELL SU ${PROJECT_ID}"
echo "================================================================================"

# 1. Preparazione Virtualenv Python persistente in .venv (dentro ~/azero_demo/.venv)
if [ -L ".venv" ]; then
  rm -f .venv
fi
if [ ! -f ".venv/bin/adk" ]; then
  echo "▶ [1/5] Creazione virtualenv Python persistente (.venv) e installazione Google ADK & Vertex AI SDK..."
  rm -rf .venv /tmp/pip_tmp 2>/dev/null || true
  mkdir -p /tmp/pip_tmp
  export TMPDIR=/tmp/pip_tmp
  python3 -m venv .venv
  source .venv/bin/activate
  pip install --no-cache-dir --upgrade pip --quiet
  pip install --no-cache-dir -r requirements.txt --quiet
  rm -rf /tmp/pip_tmp
else
  source .venv/bin/activate
fi

if [ "${WEB_ONLY}" = true ]; then
  echo "▶ Avvio immediato di ADK Web in Cloud Shell (Web Preview -> Port 8080)..."
  exec adk web --port 8080 --allow_origins "*"
fi

# 2. Setup Connettore GCS `azero-crav-pdta-ds` + 6 Documenti Ufficiali + App Gemini Enterprise
echo "▶ [2/5] Configurazione Bucket GCS, Connettore `azero-crav-pdta-ds` e App Gemini Enterprise..."
python3 setup_azero_ge_connector.py

# 3. Deploy opzionale del Multi-Agente ADK su Vertex AI Agent Engine + Agent Registry (A2A)
if [ "${WITH_ADK}" = true ]; then
  echo "▶ [3/5] Abilitazione permessi IAM Telemetria e Deploy Multi-Agente ADK su Vertex AI Agent Engine..."
  PROJECT_NUMBER=$(gcloud projects describe "${PROJECT_ID}" --format="value(projectNumber)" 2>/dev/null || echo "482813436426")
  RE_SA="service-${PROJECT_NUMBER}@gcp-sa-aiplatform-re.iam.gserviceaccount.com"
  for ROLE in \
    roles/aiplatform.user \
    roles/cloudtrace.agent \
    roles/telemetry.tracesWriter \
    roles/logging.logWriter \
    roles/monitoring.metricWriter \
    roles/serviceusage.serviceUsageConsumer \
    roles/storage.objectViewer; do
    gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
      --member="serviceAccount:${RE_SA}" \
      --role="${ROLE}" \
      --condition=None \
      --quiet >/dev/null 2>&1 || true
  done
  python3 deploy_azero_adk.py
else
  echo "▶ [3/5] Deploy Agent Engine saltato (usa --with-adk o esegui `python3 deploy_azero_adk.py` quando vuoi fare il deploy)."
fi

# 4. Pubblicazione Chat Agent Multi-Livello (Gemini 3.8 Flash) + 3 Skills in Gemini Enterprise App
echo "▶ [4/5] Pubblicazione Chat Agent Multi-Livello e 3 Skills in Gemini Enterprise App..."
python3 register_azero_ge_agent.py

# 5. Esecuzione preliminare Eval Locale (e Cloud se deployato) per popolare i report
echo "▶ [5/5] Esecuzione Valutazione (Eval) Locale sul Grafo Multi-Agente..."
python3 run_local_eval.py || true
if [ -f "DEPLOYED_AZERO_AGENT.txt" ]; then
  echo "▶ [5b/5] Esecuzione Valutazione (Eval) in Cloud contro il ReasoningEngine deployato..."
  python3 run_cloud_eval.py || true
fi

echo ""
echo "================================================================================"
echo "✅ AMBIENTE CLOUD SHELL PRONTO SU ${PROJECT_ID}!"
if [ -f "WEB_APP_URL_AZERO.txt" ]; then
  echo "🌐 Gemini Enterprise Web App URL : $(cat WEB_APP_URL_AZERO.txt)"
fi
if [ -f "DEPLOYED_AZERO_AGENT.txt" ]; then
  echo "🤖 Agent Engine Resource         : $(cat DEPLOYED_AZERO_AGENT.txt)"
fi
echo "📊 Report Eval Locale vs Cloud   : artifacts/EVAL_COMPARISON_LOCAL_VS_CLOUD.md"
echo "================================================================================"

if [ "${START_WEB}" = true ]; then
  echo ""
  echo "🚀 Avvio `adk web --port 8080 --allow_origins \"*\"` in Cloud Shell..."
  echo "👉 Clicca sull'icona 'Web Preview' in alto a destra in Cloud Shell -> 'Preview on port 8080'"
  echo "   • Seleziona `azienda_zero_agent`"
  echo "   • Apri il tab 'Graph' per mostrare la topologia del multi-agente"
  echo "   • Apri il tab 'Eval' -> `azienda_zero_eval` per lanciare la valutazione dalla UI!"
  echo ""
  adk web --port 8080 --allow_origins "*"
fi
