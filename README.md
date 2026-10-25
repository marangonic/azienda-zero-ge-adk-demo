# Azienda Zero (Regione del Veneto) — End-to-End Demo: Antigravity (PC) + Cloud Shell (`adk web`) + Gemini Enterprise App & Agent Engine (`rootprj-377111`)

Repository completo per la demo live di **Azienda Zero (Regione del Veneto)** sul progetto GCP **`rootprj-377111`**, strutturato per operare in sinergia su **3 ambienti**:
1. 💻 **Google Antigravity (sul tuo PC)**: contiene `.agent/rules/`, `.agent/skills/`, `.agent/workflows/` e il **Server MCP locale** (`mcp_servers/azero_crav_mcp_server.py`) per progettare l'agente Gemini Enterprise App (`artifacts/GE_APP_AGENT_INSTRUCTIONS_AZERO.md`), sviluppare/ispezionare il codice del **Multi-Agente ADK a Grafo** (`azienda_zero_agent/`) e il dataset di **Eval** (`azienda_zero_eval.evalset.json`).
2. ☁️ **Google Cloud Shell (su `rootprj-377111`)**: esegue con un comando 1-click (`./setup_cloudshell_azero.sh --with-adk`) il provisioning del Connettore GCS, la pubblicazione dell'agente GE App, il deploy su Vertex AI Agent Engine, l'interfaccia **`adk web --port 8080 --allow_origins "*"`** (apribile via **Cloud Shell Web Preview -> Port 8080** per mostrare il **Graph / Topology** e il tab **Eval**) e gli script di valutazione `run_local_eval.py` e `run_cloud_eval.py`.
3. 🌐 **Google Cloud Console & Gemini Enterprise Web App (`rootprj-377111`)**: dimostrazione live del Connettore `azero-crav-pdta-ds`, del Chat Agent Multi-Livello in Gemini Enterprise App, del Playground di Vertex AI Agent Engine, di Cloud Trace e di Agent Registry (A2A).

---

## ⚡ Comando 1-Click in Google Cloud Shell (`rootprj-377111`)

Apri [Google Cloud Shell su `rootprj-377111`](https://console.cloud.google.com/?cloudshell=true&project=rootprj-377111) ed esegui:

```bash
git clone -b azienda-zero-ge-adk-demo https://github.com/cloud-gtm/ge-agets-creator.git ~/azero_demo && cd ~/azero_demo && ./setup_cloudshell_azero.sh --with-adk
# oppure dal branch main (use cases/Azienda-Zero-Veneto):
git clone https://github.com/cloud-gtm/ge-agets-creator.git ~/ge-agets-creator && cd ~/ge-agets-creator/"use cases/Azienda-Zero-Veneto" && ./setup_cloudshell_azero.sh --with-adk
```

Al termine del setup, lo script avvia automaticamente **`adk web --port 8080 --allow_origins "*"`**: clicca sull'icona **Web Preview** in alto a destra in Cloud Shell $\rightarrow$ **Preview on port 8080** per mostrare il tab **Graph** (topologia del multi-agente) e il tab **Eval** (`azienda_zero_eval`).

> 📖 **Guida e Copione Passo-Passo per la Demo Live:** consulta [**`PLAYBOOK_DEMO_ANTIGRAVITY_AZIENDA_ZERO.md`**](./PLAYBOOK_DEMO_ANTIGRAVITY_AZIENDA_ZERO.md).
