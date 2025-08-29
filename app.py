# app.py
import os
import json
import asyncio
from dotenv import load_dotenv

# AutoGen imports
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Load environment
load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_KEY:
    raise ValueError("OPENAI_API_KEY not found in .env")

# -------------------------
# Tool Functions
# -------------------------
async def lead_capture_tool(lead_input: str) -> str:
    lead = {
        "name": "Ravi",
        "phone": "9876543210",
        "project_type": "road",
        "location": "Salem",
        "size": "2 km",
        "notes": lead_input[:120]
    }
    return json.dumps(lead, ensure_ascii=False)

async def estimator_tool(lead_json: str) -> str:
    try:
        lead = json.loads(lead_json)
        project_type = lead.get("project_type", "road")
        size = lead.get("size", "1 km")
        estimated_value = 625000 * (2 if "2 km" in size else 1)
    except:
        estimated_value = 1250000.0

    estimate = {
        "estimated_value": estimated_value,
        "currency": "INR",
        "assumptions": [f"Cost for {project_type} project, {size} long"]
    }
    return json.dumps(estimate, ensure_ascii=False)

async def sales_writer_tool(context_json: str) -> str:
    try:
        ctx = json.loads(context_json)
        lead = ctx.get("lead", {})
        estimate = ctx.get("estimate", {})
    except:
        lead = {}
        estimate = {}

    proposal = {
        "subject": f"Proposal for {lead.get('project_type', 'project')} at {lead.get('location', 'unknown')}",
        "body": "Dear Sir/Madam,\nWe propose to execute the construction work as per agreed terms.",
        "amount": estimate.get("estimated_value", 0),
        "currency": estimate.get("currency", "INR")
    }
    return json.dumps(proposal, ensure_ascii=False)

async def manager_approval_tool(full_context_json: str) -> str:
    try:
        ctx = json.loads(full_context_json)
        value = ctx.get("estimate", {}).get("estimated_value", 0)
    except:
        value = 0
    approved = value < 5000000
    comment = "Approved" if approved else "Requires board approval"
    return json.dumps({"approved": approved, "comment": comment}, ensure_ascii=False)

# -------------------------
# Main Function
# -------------------------
async def main():
    # Initialize model
    model = OpenAIChatCompletionClient(
        model="gpt-3.5-turbo",
        api_key=OPENAI_KEY
    )

    # Create agents
    lead_agent = AssistantAgent(
        name="LeadCapture",
        model_client=model,
        tools=[lead_capture_tool],
        system_message="Use lead_capture_tool to extract lead info and return JSON."
    )

    estimator_agent = AssistantAgent(
        name="Estimator",
        model_client=model,
        tools=[estimator_tool],
        system_message="Use estimator_tool to generate cost estimate from lead JSON."
    )

    sales_agent = AssistantAgent(
        name="SalesWriter",
        model_client=model,
        tools=[sales_writer_tool],
        system_message="Use sales_writer_tool to create a proposal from lead + estimate JSON."
    )

    manager_agent = AssistantAgent(
        name="Manager",
        model_client=model,
        tools=[manager_approval_tool],
        system_message="Use manager_approval_tool to return {approved: bool, comment: str}."
    )

    # Initial input
    initial_message = "Client enquiry: Need road estimate near Salem, 2 km, single carriageway."
    print("🚀 App is running...")
    print(f"📨 Input: {initial_message}")

    try:
        # Step 1: Capture Lead
        print("\n🔍 Step 1: Capturing Lead...")
        lead_result = await lead_agent.run(task=initial_message)
        # ✅ Fix: Handle object, not dict
        last_msg = lead_result.messages[-1]
        lead_content = last_msg.content if hasattr(last_msg, "content") else str(last_msg)
        print(f"✅ Lead: {lead_content}")

        # Step 2: Estimate
        print("\n💰 Step 2: Generating Estimate...")
        est_result = await estimator_agent.run(task=lead_content)
        last_msg = est_result.messages[-1]
        est_content = last_msg.content if hasattr(last_msg, "content") else str(last_msg)
        print(f"✅ Estimate: {est_content}")

        # Step 3: Proposal
        print("\n📝 Step 3: Writing Proposal...")
        context = {
            "lead": json.loads(lead_content),
            "estimate": json.loads(est_content)
        }
        proposal_input = json.dumps(context, ensure_ascii=False)
        sales_result = await sales_agent.run(task=proposal_input)
        last_msg = sales_result.messages[-1]
        sales_content = last_msg.content if hasattr(last_msg, "content") else str(last_msg)
        print(f"✅ Proposal: {sales_content}")

        # Step 4: Approval
        print("\n👨‍💼 Step 4: Getting Approval...")
        approval_input = json.dumps(context, ensure_ascii=False)
        approval_result = await manager_agent.run(task=approval_input)
        last_msg = approval_result.messages[-1]
        approval_content = last_msg.content if hasattr(last_msg, "content") else str(last_msg)

        # Final Output
        print("\n✅------ FINAL DECISION ------✅")
        try:
            parsed = json.loads(approval_content)
            print(json.dumps(parsed, indent=2, ensure_ascii=False))
        except:
            print(approval_content)

        print(f"\n📌 Approved by: {manager_agent.name}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

    # ✅ FINAL FIX
    await model.close()  # ✅ Not model.close() alone

# -------------------------
# Entry Point
# -------------------------
if __name__ == "__main__":
    asyncio.run(main())