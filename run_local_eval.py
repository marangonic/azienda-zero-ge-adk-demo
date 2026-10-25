#!/usr/bin/env python3
"""
ATTO 3 — Valutazione (Eval) Locale del Multi-Agente a Grafo `azienda_zero_agent`
Utilizza lo stesso dataset `azienda_zero_agent/azienda_zero_eval.evalset.json` usato dal tab `Eval` di `adk web`.
Misura:
1. `tool_trajectory_avg_score` (Graph Routing & Tool Trajectory Match): verifica che l'orchestratore
   attraversi i nodi sub-agente attesi (`ulss_pdta_kpi_agent`, `crav_compliance_agent`, `psn_cloud_sizing_agent`)
   e invochi i `FunctionTool` corretti.
2. `response_match_score` (Domain Grounding & Pricing Guardrail Rubric): verifica che la risposta finale
   contenga i dati reali delle ULSS venete, i riferimenti GDPR/CDPA/HIPAA/ACN e i prezzi mensili in USD ($/mo).
Salva i risultati in `artifacts/local_eval_results.json` e aggiorna il report comparativo
`artifacts/EVAL_COMPARISON_LOCAL_VS_CLOUD.md` e `artifacts/eval_report_comparison.html`.
"""

import asyncio
import datetime
import json
import os
import time
from typing import Any, Dict, List

EVALSET_PATH = os.path.join("azienda_zero_agent", "azienda_zero_eval.evalset.json")
LOCAL_RESULTS_PATH = os.path.join("artifacts", "local_eval_results.json")
CLOUD_RESULTS_PATH = os.path.join("artifacts", "cloud_eval_results.json")
MD_REPORT_PATH = os.path.join("artifacts", "EVAL_COMPARISON_LOCAL_VS_CLOUD.md")
HTML_REPORT_PATH = os.path.join("artifacts", "eval_report_comparison.html")


def score_trajectory(expected_tools: List[str], actual_tools: List[str]) -> float:
    if not expected_tools:
        return 1.0
    actual_set = set(actual_tools)
    hits = sum(1 for t in expected_tools if t in actual_set)
    return round(hits / len(expected_tools), 2)


def score_keywords(expected_keywords: List[str], response_text: str) -> float:
    if not expected_keywords:
        return 1.0
    text_lower = (response_text or "").lower()
    hits = sum(1 for kw in expected_keywords if kw.lower() in text_lower)
    return round(hits / len(expected_keywords), 2)


async def run_single_case_local(runner: Any, eval_case: Dict[str, Any], idx: int) -> Dict[str, Any]:
    from google.genai import types
    eval_id = eval_case["eval_id"]
    turn = eval_case["conversation"][0]
    prompt = turn["user_content"]["parts"][0]["text"]
    expected_tools = eval_case.get("expected_tools", [])
    expected_nodes = eval_case.get("expected_graph_nodes", [])
    expected_keywords = eval_case.get("expected_keywords", [])

    user_id = f"eval-local-user-{idx}"
    session = await runner.session_service.create_session(
        app_name="azienda_zero_eval",
        user_id=user_id,
    )

    actual_tools: List[str] = []
    actual_nodes: List[str] = ["azero_orchestrator"]
    final_texts: List[str] = []

    t0 = time.time()
    content = types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session.id,
        new_message=content,
    ):
        author = getattr(event, "author", None)
        if author and author not in actual_nodes:
            actual_nodes.append(author)
        ev_content = getattr(event, "content", None)
        if ev_content and getattr(ev_content, "parts", None):
            for part in ev_content.parts:
                fc = getattr(part, "function_call", None)
                if fc and getattr(fc, "name", None):
                    actual_tools.append(fc.name)
                    if fc.name == "transfer_to_agent" and getattr(fc, "args", None):
                        target_ag = dict(fc.args).get("agent_name")
                        if target_ag and target_ag not in actual_nodes:
                            actual_nodes.append(target_ag)
                txt = getattr(part, "text", None)
                if txt and txt.strip():
                    final_texts.append(txt.strip())

    elapsed_s = round(time.time() - t0, 2)
    full_response = "\n".join(final_texts)
    traj_score = score_trajectory(expected_tools, actual_tools)
    rubric_score = score_keywords(expected_keywords, full_response)
    passed = (traj_score >= 0.8) and (rubric_score >= 0.65)

    return {
        "eval_id": eval_id,
        "prompt": prompt,
        "expected_graph_nodes": expected_nodes,
        "actual_graph_nodes": actual_nodes,
        "expected_tools": expected_tools,
        "actual_tools": actual_tools,
        "tool_trajectory_avg_score": traj_score,
        "response_match_score": rubric_score,
        "latency_seconds": elapsed_s,
        "status": "PASS" if passed else "FAIL",
        "response_preview": full_response[:600],
    }


def generate_comparison_reports():
    os.makedirs("artifacts", exist_ok=True)
    local_data = None
    cloud_data = None
    if os.path.exists(LOCAL_RESULTS_PATH):
        with open(LOCAL_RESULTS_PATH, "r", encoding="utf-8") as f:
            local_data = json.load(f)
    if os.path.exists(CLOUD_RESULTS_PATH):
        with open(CLOUD_RESULTS_PATH, "r", encoding="utf-8") as f:
            cloud_data = json.load(f)

    local_cases = {c["eval_id"]: c for c in (local_data.get("cases", []) if local_data else [])}
    cloud_cases = {c["eval_id"]: c for c in (cloud_data.get("cases", []) if cloud_data else [])}
    all_ids = list(local_cases.keys() or cloud_cases.keys())

    md_lines = [
        "# Report di Valutazione (Eval) Multi-Agente a Grafo — Azienda Zero (`rootprj-377111`)",
        "",
        f"> **Ultimo Aggiornamento:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
        "> **Eval Set:** `azienda_zero_agent/azienda_zero_eval.evalset.json`  ",
        "> **Architettura Valutata:** `azero_orchestrator` $\\rightarrow$ `ulss_pdta_kpi_agent` | `crav_compliance_agent` | `psn_cloud_sizing_agent`",
        "",
        "## 1. Riepilogo Comparativo: Eval Locale (`adk web`) vs Eval Cloud (`Vertex AI Agent Engine`)",
        "",
        "| Test Case ID | Nodi del Grafo Attraversati | Locale: Graph Trajectory | Locale: Response Rubric | Cloud: Graph Trajectory | Cloud: Response Rubric | Esito Finale |",
        "| :--- | :--- | :---: | :---: | :---: | :---: | :---: |",
    ]

    html_rows = []
    for cid in all_ids:
        lc = local_cases.get(cid, {})
        cc = cloud_cases.get(cid, {})
        nodes_str = " → ".join(lc.get("actual_graph_nodes") or cc.get("actual_graph_nodes") or ["azero_orchestrator"])
        l_traj = f"{lc['tool_trajectory_avg_score']:.2f}" if "tool_trajectory_avg_score" in lc else "N/A"
        l_rub = f"{lc['response_match_score']:.2f}" if "response_match_score" in lc else "N/A"
        c_traj = f"{cc['tool_trajectory_avg_score']:.2f}" if "tool_trajectory_avg_score" in cc else "In attesa deploy/eval cloud"
        c_rub = f"{cc['response_match_score']:.2f}" if "response_match_score" in cc else "In attesa deploy/eval cloud"
        status_badge = "✅ PASS" if (lc.get("status") == "PASS" and (not cc or cc.get("status") == "PASS")) else "⚠️ CHECK"
        md_lines.append(f"| `{cid}` | `{nodes_str}` | **{l_traj}** | **{l_rub}** | **{c_traj}** | **{c_rub}** | **{status_badge}** |")
        html_rows.append(
            f"<tr><td><code>{cid}</code></td><td><code>{nodes_str}</code></td>"
            f"<td><code>{', '.join(lc.get('actual_tools') or cc.get('actual_tools') or [])}</code></td>"
            f"<td><strong>{l_traj}</strong></td><td><strong>{l_rub}</strong></td>"
            f"<td><strong>{c_traj}</strong></td><td><strong>{c_rub}</strong></td>"
            f"<td><span class='badge'>{status_badge}</span></td></tr>"
        )

    md_lines.extend([
        "",
        "## 2. Dettaglio Traiettoria sul Grafo e Risposte per Caso di Test",
        "",
    ])
    for cid in all_ids:
        c = cloud_cases.get(cid) or local_cases.get(cid) or {}
        md_lines.extend([
            f"### 📌 `{cid}`",
            f"- **Prompt Utente:** *{c.get('prompt', '')}*",
            f"- **Nodi del Grafo Attesi:** `{c.get('expected_graph_nodes', [])}` | **Nodi Attraversati:** `{c.get('actual_graph_nodes', [])}`",
            f"- **Tool Invocati nel Grafo:** `{c.get('actual_tools', [])}`",
            f"- **Estratto Risposta:**\n  > {c.get('response_preview', '').replace(chr(10), ' ')}",
            "",
        ])

    with open(MD_REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines) + "\n")

    html_content = f"""<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <title>Azienda Zero — ADK Multi-Agent Graph Evaluation (Local vs Cloud)</title>
  <style>
    body {{ font-family: 'Google Sans', Roboto, sans-serif; background: #f8fafc; color: #0f172a; margin: 32px; }}
    .card {{ background: #ffffff; border-radius: 12px; padding: 24px; box-shadow: 0 2px 10px rgba(0,0,0,0.06); margin-bottom: 24px; }}
    h1 {{ color: #1a73e8; margin-top: 0; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 16px; }}
    th, td {{ border: 1px solid #e2e8f0; padding: 12px; text-align: left; font-size: 14px; }}
    th {{ background: #f1f5f9; color: #1e293b; }}
    .badge {{ background: #dcfce7; color: #166534; padding: 4px 10px; border-radius: 999px; font-weight: 600; }}
    code {{ background: #f1f5f9; padding: 2px 6px; border-radius: 4px; font-size: 13px; }}
  </style>
</head>
<body>
  <div class="card">
    <h1>🏥 Azienda Zero Veneto — ADK Multi-Agent Graph Evaluation</h1>
    <p>Confronto tra la valutazione eseguita in <strong>Locale (<code>adk web</code>)</strong> e la valutazione ripetuta in <strong>Cloud (<code>Vertex AI Agent Engine</code> su <code>rootprj-377111</code>)</strong>.</p>
    <table>
      <thead>
        <tr>
          <th>Test Case ID</th>
          <th>Traiettoria Nodi del Grafo</th>
          <th>Tool Invocati</th>
          <th>Locale: Trajectory Score</th>
          <th>Locale: Rubric Score</th>
          <th>Cloud: Trajectory Score</th>
          <th>Cloud: Rubric Score</th>
          <th>Stato</th>
        </tr>
      </thead>
      <tbody>
        {''.join(html_rows)}
      </tbody>
    </table>
  </div>
</body>
</html>"""
    with open(HTML_REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)


async def main_async():
    from google.adk.runners import InMemoryRunner
    from azienda_zero_agent.agent import root_agent

    os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "TRUE")
    os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "rootprj-377111")
    os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")

    with open(EVALSET_PATH, "r", encoding="utf-8") as f:
        evalset = json.load(f)

    runner = InMemoryRunner(agent=root_agent, app_name="azienda_zero_eval")
    cases_out = []

    print("=" * 90)
    print("🧪 ATTO 3: Esecuzione Valutazione (Eval) LOCALE sul Grafo Multi-Agente `azienda_zero_agent`")
    print("=" * 90)

    for idx, ec in enumerate(evalset.get("eval_cases", []), start=1):
        print(f"\n▶ [{idx}/{len(evalset['eval_cases'])}] Valutazione caso: {ec['eval_id']} ...")
        res = await run_single_case_local(runner, ec, idx)
        cases_out.append(res)
        print(f"   • Nodi Grafo Visitati        : {' -> '.join(res['actual_graph_nodes'])}")
        print(f"   • Tool Chiamati              : {res['actual_tools']}")
        print(f"   • Graph Trajectory Score     : {res['tool_trajectory_avg_score']:.2f} ( soglia >= 0.80 )")
        print(f"   • Response Rubric Score      : {res['response_match_score']:.2f} ( soglia >= 0.65 )")
        print(f"   • Esito                      : {res['status']} ({res['latency_seconds']}s)")

    avg_traj = round(sum(c["tool_trajectory_avg_score"] for c in cases_out) / max(1, len(cases_out)), 2)
    avg_rub = round(sum(c["response_match_score"] for c in cases_out) / max(1, len(cases_out)), 2)

    os.makedirs("artifacts", exist_ok=True)
    summary = {
        "environment": "LOCAL_ADK_WEB",
        "timestamp": datetime.datetime.now().isoformat(),
        "avg_tool_trajectory_score": avg_traj,
        "avg_response_match_score": avg_rub,
        "cases": cases_out,
    }
    with open(LOCAL_RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    generate_comparison_reports()
    print("\n" + "=" * 90)
    print(f"✅ EVAL LOCALE COMPLETATA | Media Trajectory: {avg_traj:.2f} | Media Rubric: {avg_rub:.2f}")
    print(f"📄 Report Markdown : {MD_REPORT_PATH}")
    print(f"🌐 Report HTML     : {HTML_REPORT_PATH}")
    print("=" * 90)


if __name__ == "__main__":
    asyncio.run(main_async())
