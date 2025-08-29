# everest_team_runner.py
import asyncio
from everest_team import run_builders_team

def run_team_sync(task: str) -> str:
    """
    Run Everest Builders multi-agent team synchronously for Streamlit.
    """
    return asyncio.run(run_builders_team(task))
