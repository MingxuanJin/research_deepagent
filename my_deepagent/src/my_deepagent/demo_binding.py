"""Expose a local DeepAgents runnable to agentseek."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Literal

from dotenv import load_dotenv

_project_root = Path(__file__).resolve().parents[2]
_parent_env = _project_root.parent / ".env"

if _parent_env.exists():
    load_dotenv(_parent_env, override=False)
# 项目自己的 .env 放在后面，允许覆盖父目录
load_dotenv(_project_root / ".env", override=True)

from agentseek_langchain import messages_spec
from deepagents import ProviderProfile, create_deep_agent, register_provider_profile
from langchain.agents.middleware import TodoListMiddleware

from .settings import get_settings

# ============================================================
# 实验一：Hello World + 计算器 Agent（纯本地工具）
# ============================================================

def get_weather(city: str) -> str:
    """Get weather for a given city.

    Args:
        city: The city name, e.g. "北京".
    """
    return f"It's always sunny in {city}!"


def calculate(expression: str) -> float:
    """Evaluate a math expression and return the result.

    Args:
        expression: A math expression, e.g. "1 + 2 * 3".
    """
    return eval(expression)


def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str = "CNY",
) -> dict:
    """Convert an amount from one currency to another.

    Args:
        amount: The amount to convert.
        from_currency: The source currency code, e.g. "USD".
        to_currency: The target currency code, defaults to "CNY".
    """
    rates = {"USD": 7.2, "CNY": 1.0, "EUR": 7.8}
    cny = amount * rates[from_currency]
    return {"amount": round(cny / rates[to_currency], 2), "currency": to_currency}


# ============================================================
# 实验二：研究助手（需要 TAVILY_API_KEY）
# ============================================================

def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
):
    """Run a web search for the given query.

    Args:
        query: The search query string.
        max_results: Maximum number of results to return.
        topic: The topic category for the search.
        include_raw_content: Whether to include raw page content.
    """
    from tavily import TavilyClient

    client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
    return client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )
# ============================================================
# Agent 构建
# ============================================================

def _collect_tools() -> list:
    """Local tools always available; internet_search only if TAVILY_API_KEY exists."""
    tools = [get_weather, calculate, convert_currency]
    if os.environ.get("TAVILY_API_KEY"):
        tools.append(internet_search)
    return tools
def outline_answer(topic: str) -> str:
    """Return a lightweight response outline for planning-heavy prompts."""

    cleaned = topic.strip()
    if not cleaned:
        return "No topic provided."
    return (
        f"Suggested outline for {cleaned}:\n"
        "1. State the goal in one sentence.\n"
        "2. List the main constraints and tradeoffs.\n"
        "3. Finish with recommended next steps."
    )


def build_agent() -> Any:
    """Build a local DeepAgents runnable."""

    settings = get_settings()
    settings.apply_openai_env_bridge()
    register_provider_profile(
        "openai",
        ProviderProfile(init_kwargs={"use_responses_api": False}),
    )
    return create_deep_agent(
        model=settings.require_model(),
        tools=[outline_answer,],
        middleware=[TodoListMiddleware()],
        system_prompt=("You are a helpful engineering and research assistant. "
            "Answer in the same language as the user's question. "
            "Available tools:\n"
            "- get_weather: check the weather for a city\n"
            "- calculate: evaluate a math expression\n"
            "- convert_currency: convert between currencies\n"
            "- internet_search: search the web for information\n"
            "Use tools whenever they help answer the user's question."),
    )


def build_spec():
    """Return a RunnableSpec for AGENTSEEK_LANGCHAIN_SPEC."""

    return messages_spec(build_agent(), include_agents_md=True)
