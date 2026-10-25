#!/usr/bin/env python3
"""
ATTO 4 — Valutazione (Eval) in CLOUD del Multi-Agente a Grafo `azienda_zero_agent`
deployato su Vertex AI Agent Engine (`rootprj-377111`, `us-central1`).
Esegue gli stessi 4 casi di `azienda_zero_agent/azienda_zero_eval.evalset.json` contro il
`ReasoningEngine` remoto in Cloud, verifica la traiettoria sul grafo (`tool_trajectory_avg_score`)
e il Rubric Score (`response_match_score`), e aggiorna il report comparativo Locale vs Cloud:
- `artifacts/EVAL_COMPARISON_LOCAL_VS_CLOUD.md`
- `artifacts/eval_report_comparison.html`
"""

import datetime
import json
import os
import time
from typing import Any, Dict, List

import vertexai
from vertexai import agent_engines

from run_local_eval import (
    CLOUD_RESULTS_PATH,
    EVALSET_PATH,
    HTML_REPORT_PATH,
    MD_REPORT_PATH,
    generate_comparison_reports,
    score_keywords,
    score_trajectory,
)

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "rootprj-377111")
REGION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")


def load_resource_name() -> str:
    if os.path.exists("deployment_metadata_azero.json"):
        with open("deployment_metadata_azero.json", "r", encoding="utf-8") as f:
            return json.load(f)["remote_agent_runtime_id"]
    if os.path.exists("DEPLOYED_AZERO_AGENT.txt"):
        with open("DEPLOYED_AZERO_AGENT.txt", "r", encoding="utf-8") as f:
            return f.read().strip()
    raise FileNotFoundError("Esegui prima `python3 deploy_azero_adk.py`.")


def run_single_case_cloud(remote_agent: Any, eval_case: Dict[str, Any], idx: int) -> Dict[str, Any]:
    eval_id = eval_case["eval_id"]
    turn = eval_case["conversation"][0]
    prompt = turn["user_content"]["parts"][0]["text"]
    expected_tools = eval_case.get("expected_tools", [])
    expected_nodes = eval_case.get("expected_graph_nodes", [])
    expected_keywords = eval_case.get("expected_keywords", [])

    user_id = f"eval-cloud-user-{idx}"
    session = remote_agent.create_session(user_id=user_id)
    session_id = session["id"] if isinstance(session, dict) else session.id

    actual_tools: List[str] = []
    actual_nodes: List[str] = ["azero_orchestrator"]
    final_texts: List[str] = []

    t0 = time.time()
    for event in remote_agent.stream_query(
        user_id=user_id,
        session_id=session_id,
        message=prompt,
    ):
        if isinstance(event, dict):
            author = event.get("author")
            if author and author not in actual_nodes:
                actual_nodes.append(author)
            content = event.get("content", {})
            for part in content.get("parts", []):
                if "function_call" in part:
                    fc = part["function_call"]
                    t_name = fc.get("name")
                    if t_name:
                        actual_tools.append(t_name)
                    if t_name == "transfer_to_agent":
                        target_ag = (fc.get("args") or {}).get("agent_name")
                        if target_ag and target_ag not in actual_nodes:
                            actual_nodes.append(target_ag)
                if "text" in part and part["text"].strip():
                    final_texts.append(part["text"].strip())

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


def main():
    resource_name = load_resource_name()
    vertexai.init(project=PROJECT_ID, location=REGION)
    remote_agent = agent_engines.get(resource_name)

    with open(EVALSET_PATH, "r", encoding="utf-8") as f:
        evalset = json.load(f)

    print("=" * 90)
    print(f"☁️  ATTO 4: Esecuzione Valutazione (Eval) in CLOUD su Vertex AI Agent Engine")
    print(f"   ReasoningEngine : {resource_name}")
    print("=" * 90)

    cases_out = []
    for idx, ec in enumerate(evalset.get("eval_cases", []), start=1):
        print(f"\n▶ [{idx}/{len(evalset['eval_cases'])}] Valutazione Cloud caso: {ec['eval_id']} ...")
        res = run_single_case_cloud(remote_agent, ec, idx)
        cases_out.append(res)
        print(f"   • Nodi Grafo Visitati (Cloud): {' -> '.join(res['actual_graph_nodes'])}")
        print(f"   • Tool Chiamati (Cloud)      : {res['actual_tools']}")
        print(f"   • Cloud Trajectory Score     : {res['tool_trajectory_avg_score']:.2f} ( soglia >= 0.80 )")
        print(f"   • Cloud Rubric Score         : {res['response_match_score']:.2f} ( soglia >= 0.65 )")
        print(f"   • Esito                      : {res['status']} ({res['latency_seconds']}s)")

    avg_traj = round(sum(c["tool_trajectory_avg_score"] for c in cases_out) / max(1, len(cases_out)), 2)
    avg_rub = round(sum(c["response_match_score"] for c in cases_out) / max(1, len(cases_out)), 2)

    os.makedirs("artifacts", exist_ok=True)
    summary = {
        "environment": "CLOUD_VERTEX_AI_AGENT_ENGINE",
        "reasoning_engine": resource_name,
        "timestamp": datetime.datetime.now().isoformat(),
        "avg_tool_trajectory_score": avg_traj,
        "avg_response_match_score": avg_rub,
        "cases": cases_out,
    }
    with open(CLOUD_RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    generate_comparison_reports()
    print("\n" + "=" * 90)
    print(f"✅ EVAL CLOUD COMPLETATA | Media Trajectory: {avg_traj:.2f} | Media Rubric: {avg_rub:.2f}")
    print(f"📄 Report Comparativo Markdown : {MD_REPORT_PATH}")
    print(f"🌐 Report Comparativo HTML     : {HTML_REPORT_PATH}")
    print("=" * 90)


if __name__ == "__main__":
    main()
