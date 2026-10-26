#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

VENV_DIR="/tmp/azero_venv"
if [ ! -f "${VENV_DIR}/bin/adk" ]; then
  echo "=== Creazione ambiente virtuale Python in ${VENV_DIR} (symlink .venv) ==="
  rm -rf ~/.cache/pip /tmp/pip_tmp .venv "${VENV_DIR}" 2>/dev/null || true
  mkdir -p /tmp/pip_tmp
  export TMPDIR=/tmp/pip_tmp
  python3 -m venv "${VENV_DIR}"
  ln -sfn "${VENV_DIR}" .venv
  source "${VENV_DIR}/bin/activate"
  pip install --no-cache-dir --upgrade pip --quiet
  pip install --no-cache-dir -r requirements.txt --quiet
  rm -rf /tmp/pip_tmp
else
  ln -sfn "${VENV_DIR}" .venv
  source "${VENV_DIR}/bin/activate"
fi

export GOOGLE_GENAI_USE_VERTEXAI=TRUE
export GOOGLE_CLOUD_PROJECT="${GOOGLE_CLOUD_PROJECT:-rootprj-377111}"
export GOOGLE_CLOUD_QUOTA_PROJECT="${GOOGLE_CLOUD_PROJECT}"
export GOOGLE_CLOUD_LOCATION="${GOOGLE_CLOUD_LOCATION:-us-central1}"
export GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY=true
export OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=true
export ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS=true

echo "================================================================================"
echo "🚀 Avvio ADK Web UI per Azienda Zero (Regione del Veneto) in Cloud Shell (Porta 8080)"
echo "   Progetto GCP : ${GOOGLE_CLOUD_PROJECT} (${GOOGLE_CLOUD_LOCATION})"
echo "   Agente       : azienda_zero_agent (Grafo: azero_orchestrator + 3 Sub-Agenti)"
echo "   👉 In Cloud Shell clicca 'Web Preview' (in alto a destra) -> 'Preview on port 8080'"
echo "   Tab da aprire: 1) Chat & Graph/Topology   2) Eval (azienda_zero_eval)"
echo "================================================================================"

adk web --port 8080 --allow_origins "*"
