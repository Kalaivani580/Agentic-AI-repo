# everest_team.py
import os
import json
import asyncio
from typing import Any
from dotenv import load_dotenv
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.conditions import TextMentionTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient

load_dotenv()

# --- OpenAI setup ---
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def build_model_client() -> OpenAIChatCompletionClient:
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY missing in environment variables")
    return OpenAIChatCompletionClient(
        model=OPENAI_MODEL,
        api_key=OPENAI_API_KEY,
        temperature=0.4,
    )

# --- simple tool for rough rate ---
CITY_BASELINE = {
    "chennai": {"basic": 1900, "standard": 2300, "premium": 3000},
    "coimbatore": {"basic": 1750, "standard": 2150, "premium": 2850},
    "salem": {"basic": 1700, "standard": 2100, "premium": 2750},
}

async def get_inr_rate_per_sqft(city: str, spec: str = "standard") -> str:
    c = city.lower().strip()
    s = spec.lower().strip()
    table = CITY_BASELINE.get(c) or CITY_BASELINE["salem"]
    rate = table.get(s, table["standard"])
    return json.dumps({"city": c, "spec": s, "inr_per_sqft": rate})

# --- build Everest 4-agent team ---
def build_everest_team(model_client: OpenAIChatCompletionClient) -> RoundRobinGroupChat:
    lead_intake = AssistantAgent(
        name="LeadIntake",
        model_client=model_client,
        system_message=(
            "Role: Senior Lead Qualifier. Extract clean spec from user message as 'Lead Brief'. "
            "Include: city, plot size, built-up area, floors, bedrooms, bathrooms, finish level, special requirements, contact."
        ),
    )

    estimator = AssistantAgent(
        name="Estimator",
        model_client=model_client,
        tools=[get_inr_rate_per_sqft],
        system_message=(
            "Role: Civil Estimator. Input: 'Lead Brief'. "
            "Call tool get_inr_rate_per_sqft(city,spec) and produce rough cost, timeline, subtotal, GST, grand total."
        ),
    )

    sales_writer = AssistantAgent(
        name="SalesWriter",
        model_client=model_client,
        system_message=(
            "Role: Client Communication Specialist. Input: 'Rough Estimate'. "
            "Write short, polite message summarizing estimate and timeline, mention it's ballpark, end with [[FINAL_ANSWER]]."
        ),
    )

    manager = AssistantAgent(
        name="Manager",
        model_client=model_client,
        system_message=(
            "Role: Quality Manager. Review SalesWriter message. Ensure clarity, politeness, completeness. "
            "Always end with [[FINAL_ANSWER]]."
        ),
    )

    termination = TextMentionTermination(text="[[FINAL_ANSWER]]")
    team = RoundRobinGroupChat(
        [lead_intake, estimator, sales_writer, manager],
        termination_condition=termination,
        max_turns=10
    )
    return team

# --- high-level async API ---
async def run_builders_team(task: str) -> str:
    model_client = build_model_client()
    team = build_everest_team(model_client)
    result = await team.run(task=task)
    last_text = ""
    for m in result.messages:
        if isinstance(m, TextMessage):
            last_text = m.content
    return last_text.replace("[[FINAL_ANSWER]]", "").strip()
