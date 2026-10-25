"""
Callback di Observability, Telemetria OpenTelemetry e Cloud Logging per il Multi-Agente ADK `azienda_zero_agent`.
Traccia ogni passaggio tra i nodi del grafo (`azero_orchestrator` -> `ulss_pdta_kpi_agent`,
`crav_compliance_agent`, `psn_cloud_sizing_agent`) e le esecuzioni dei singoli tool in:
- `callback_context.state["graph_execution_trace"]` (visibile nel tab State di `adk web` e usato per l'Eval)
- Cloud Logging & Cloud Trace (`[ADK-AGENT-START]`, `[ADK-LLM-TOOL-CALL]`, `[ADK-TOOL-START]`, `[ADK-TOOL-END]`, `[ADK-AGENT-END]`)
"""

import datetime
import logging
import time
from typing import Any, Dict, Optional
from zoneinfo import ZoneInfo

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext

logger = logging.getLogger("azero_adk_observability")
logger.setLevel(logging.INFO)


def before_agent_log(callback_context: CallbackContext) -> Optional[Any]:
    """Registra l'ingresso in un nodo del grafo multi-agente (Orchestrator o Sub-Agent)."""
    state = callback_context.state
    state["turn_start_ts"] = time.time()
    state["total_agent_hops"] = state.get("total_agent_hops", 0) + 1
    trace_list = list(state.get("graph_execution_trace", []))
    trace_list.append(
        {
            "event": "agent_node_enter",
            "agent_name": callback_context.agent_name,
            "timestamp": datetime.datetime.now(ZoneInfo("Europe/Rome")).strftime("%H:%M:%S"),
        }
    )
    state["graph_execution_trace"] = trace_list
    logger.info(
        "[ADK-AGENT-START] agent=%s invocation_id=%s hop=%s",
        callback_context.agent_name,
        getattr(callback_context, "invocation_id", "n/a"),
        state["total_agent_hops"],
    )
    return None


def after_agent_log(callback_context: CallbackContext) -> Optional[Any]:
    """Registra l'uscita da un nodo del grafo multi-agente e la latenza in ms."""
    state = callback_context.state
    start_ts = state.get("turn_start_ts")
    elapsed_ms = round((time.time() - start_ts) * 1000, 2) if start_ts else 0.0
    logger.info(
        "[ADK-AGENT-END] agent=%s invocation_id=%s elapsed_ms=%s",
        callback_context.agent_name,
        getattr(callback_context, "invocation_id", "n/a"),
        elapsed_ms,
    )
    return None


def log_query_to_model(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """Registra il prompt inviato al modello LLM dal nodo corrente del grafo."""
    if llm_request.contents and llm_request.contents[-1].role == "user":
        for part in llm_request.contents[-1].parts:
            if getattr(part, "text", None):
                logger.info(
                    "[ADK-LLM-REQUEST] agent=%s prompt=%s",
                    callback_context.agent_name,
                    part.text[:400],
                )
    return None


def log_model_response(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> Optional[LlmResponse]:
    """Registra la risposta testuale o le deleghe (`transfer_to_agent` / tool call) nel grafo."""
    if llm_response.content and llm_response.content.parts:
        for part in llm_response.content.parts:
            if getattr(part, "text", None):
                logger.info(
                    "[ADK-LLM-RESPONSE] agent=%s text=%s",
                    callback_context.agent_name,
                    part.text[:400],
                )
            elif getattr(part, "function_call", None):
                logger.info(
                    "[ADK-LLM-TOOL-CALL] agent=%s tool_name=%s args=%s",
                    callback_context.agent_name,
                    part.function_call.name,
                    dict(part.function_call.args) if part.function_call.args else {},
                )
    return None


def before_tool_log(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext
) -> Optional[Dict[str, Any]]:
    """Registra l'avvio di un tool ADK o il trasferimento a un sub-agente nel grafo."""
    trace_list = list(tool_context.state.get("graph_execution_trace", []))
    trace_list.append(
        {
            "event": "tool_call",
            "agent_name": tool_context.agent_name,
            "tool_name": tool.name,
            "args": args,
            "timestamp": datetime.datetime.now(ZoneInfo("Europe/Rome")).strftime("%H:%M:%S"),
        }
    )
    tool_context.state["graph_execution_trace"] = trace_list
    logger.info(
        "[ADK-TOOL-START] agent=%s tool=%s args=%s",
        tool_context.agent_name,
        tool.name,
        args,
    )
    return None


def after_tool_log(
    tool: BaseTool,
    args: Dict[str, Any],
    tool_context: ToolContext,
    tool_response: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """Registra il completamento del tool ADK."""
    logger.info(
        "[ADK-TOOL-END] agent=%s tool=%s status=%s",
        tool_context.agent_name,
        tool.name,
        tool_response.get("status", "completed") if isinstance(tool_response, dict) else "ok",
    )
    return None
