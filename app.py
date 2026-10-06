import asyncio
from aiohttp import web
from botbuilder.core import (
    ActivityHandler, TurnContext, MessageFactory, CardFactory,
    BotFrameworkAdapter, BotFrameworkAdapterSettings
)
from botbuilder.schema import Activity

# ==========================================
# ADAPTIVE CARD FACTORIES (VSME Template Aligned)
# ==========================================

def create_vsme_scoping_card():
    """Phase 1: General Information (Emulator-Compatible Version 1.2)"""
    return {
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "type": "AdaptiveCard",
        "version": "1.2", # Downgraded for Emulator compatibility
        "body": [
            {
                "type": "TextBlock",
                "text": "📊 EFRAG VSME Reporting Setup",
                "weight": "Bolder",
                "size": "Large"
            },
            {
                "type": "TextBlock",
                "text": "To align with the official EFRAG VSME Digital Template, please provide the baseline entity information.",
                "wrap": True,
                "spacing": "Medium"
            },
            # Replaced "label" with standalone TextBlocks
            {
                "type": "TextBlock",
                "text": "Entity Name (B1) *",
                "weight": "Bolder",
                "spacing": "Medium"
            },
            {
                "type": "Input.Text",
                "id": "entity_name",
                "placeholder": "e.g., Pacetti S.r.l."
            },
            {
                "type": "TextBlock",
                "text": "Reporting Period (B2) *",
                "weight": "Bolder",
                "spacing": "Medium"
            },
            {
                "type": "Input.Text",
                "id": "reporting_period",
                "placeholder": "e.g., 2025-01-01 to 2025-12-31"
            },
            {
                "type": "TextBlock",
                "text": "Accounting Standard (B3)",
                "weight": "Bolder",
                "spacing": "Medium"
            },
            {
                "type": "Input.ChoiceSet",
                "id": "accounting_standard",
                "choices": [
                    { "title": "Local GAAP", "value": "Local GAAP" },
                    { "title": "IFRS", "value": "IFRS" }
                ],
                "value": "Local GAAP"
            },
            {
                "type": "TextBlock",
                "text": "Select VSME Modules to Populate:",
                "weight": "Bolder",
                "spacing": "Medium"
            },
            {
                "type": "Input.Toggle",
                "id": "module_basic",
                "title": "Basic Module (B12 - Environmental, Social, Business metrics)",
                "value": "true"
            },
            {
                "type": "Input.Toggle",
                "id": "module_narrative",
                "title": "Narrative Module (N1 - Policies, Actions, Targets)",
                "value": "true"
            }
        ],
        "actions": [
            {
                "type": "Action.Submit",
                "title": "Initialize Template",
                "data": { "action": "init_template" }
            }
        ]
    }

def create_extraction_summary_card(filename):
    """Phase 2: Post-Upload Extraction Summary (Simulating vsme2025eng.pdf parsing)"""
    return {
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "type": "AdaptiveCard",
        "version": "1.4",
        "body": [
            {
                "type": "TextBlock",
                "text": "✅ Document Parsed Successfully",
                "weight": "Bolder",
                "color": "Good",
                "size": "Medium"
            },
            {
                "type": "TextBlock",
                "text": f"Extracted key data from **{filename}** mapping to VSME-Digital-Template-Sample-1.3.0.xlsx:",
                "wrap": True
            },
            {
                "type": "FactSet",
                "facts": [
                    { "title": "Turnover:", "value": "€10,263,228" },
                    { "title": "Electricity:", "value": "86,360 kWh" },
                    { "title": "Total Employees:", "value": "46 (34 Ops, 12 Office)" },
                    { "title": "Waste (Recycled):", "value": "94.49%" }
                ]
            }
        ],
        "actions": [
            {
                "type": "Action.Submit",
                "title": "Review Missing Metrics",
                "data": { "action": "review_missing" }
            }
        ]
    }

def create_hitl_clarification_card():
    """Phase 3: Interactive HITL for VSME Specifics"""
    return {
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "type": "AdaptiveCard",
        "version": "1.4",
        "body": [
            {
                "type": "TextBlock",
                "text": "⚠️ Clarification Required: Emissions Data",
                "weight": "Bolder",
                "color": "Warning"
            },
            {
                "type": "TextBlock",
                "text": "The report states total CO2 emissions are **2,408.12 tonnes**. The EFRAG Basic Module requires this split into Scope 1 (Direct) and Scope 2 (Indirect).",
                "wrap": True
            },
            {
                "type": "Input.Text",
                "id": "scope_1",
                "label": "Scope 1 Emissions (tonnes CO2eq)",
                "placeholder": "e.g., 1000"
            },
            {
                "type": "Input.Text",
                "id": "scope_2",
                "label": "Scope 2 Emissions (tonnes CO2eq)",
                "placeholder": "e.g., 1408.12"
            }
        ],
        "actions": [
            {
                "type": "Action.Submit",
                "title": "Patch Schema & Generate XBRL",
                "data": { "action": "patch_emissions" }
            }
        ]
    }

# ==========================================
# BOT ACTIVITY HANDLER
# ==========================================

class VSMEBot(ActivityHandler):
    def __init__(self):
        self.state = {}

    async def on_members_added_activity(self, members_added, turn_context: TurnContext):
        """Sends the initial VSME Setup form."""
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                card = CardFactory.adaptive_card(create_vsme_scoping_card())
                await turn_context.send_activity(MessageFactory.attachment(card))

    async def on_message_activity(self, turn_context: TurnContext):
        activity = turn_context.activity
        
        # 1. Handle UI Form Submissions
        if activity.value:
            action = activity.value.get("action")
            
            if action == "init_template":
                entity = activity.value.get("entity_name", "Unknown Entity")
                await turn_context.send_activity(
                    f"✅ **{entity}** workspace initialized against `VSME-Digital-Template-1.3.0.xlsx`.\n\n"
                    "Please upload your sustainability report (e.g., `vsme2025eng.pdf`) to begin data extraction."
                )
                return

            if action == "review_missing":
                await turn_context.send_activity("Scanning schema for null values...")
                await asyncio.sleep(1)
                # Trigger the HITL card regarding the emissions split
                card = CardFactory.adaptive_card(create_hitl_clarification_card())
                await turn_context.send_activity(MessageFactory.attachment(card))
                return

            if action == "patch_emissions":
                s1 = activity.value.get("scope_1", "0")
                s2 = activity.value.get("scope_2", "0")
                await turn_context.send_activity(
                    f"✅ Schema patched. Scope 1: {s1}t, Scope 2: {s2}t.\n\n"
                    "Injecting data via `openpyxl` and generating Inline XBRL..."
                )
                return

        # 2. Handle File Uploads
        if activity.attachments:
            file_names = [att.name for att in activity.attachments]
            await turn_context.send_activity(f"⏳ Ingesting {', '.join(file_names)} with Docling...")
            await asyncio.sleep(2) # Mock processing time
            
            # Send extraction summary based on the uploaded file
            summary_card = CardFactory.adaptive_card(create_extraction_summary_card(file_names[0]))
            await turn_context.send_activity(MessageFactory.attachment(summary_card))
            return
        
        # 3. Handle Standard Text/Fallback
        else:
            text = activity.text.strip().lower() if activity.text else ""
            
            # --- NEW UPLOAD BYPASS ---
            if text.startswith("upload"):
                filename = "vsme2025eng.pdf"
                await turn_context.send_activity(f"⏳ Ingesting {filename} with Docling...")
                await asyncio.sleep(2) 
                
                summary_card = CardFactory.adaptive_card(create_extraction_summary_card(filename))
                await turn_context.send_activity(MessageFactory.attachment(summary_card))
                return
            # -------------------------

            if text in ["hi", "hello", "start", "menu"]:
                card = CardFactory.adaptive_card(create_vsme_scoping_card())
                await turn_context.send_activity(MessageFactory.attachment(card))
            else:
                await turn_context.send_activity(
                    "I didn't catch that. Type **'start'** to bring up the setup menu, or type **'upload'** to simulate a document upload."
                )

        await turn_context.send_activity("Please interact with the Adaptive Cards or upload a report.")

# ==========================================
# SERVER SETUP
# ==========================================
adapter = BotFrameworkAdapter(BotFrameworkAdapterSettings("", ""))
bot = VSMEBot()

async def messages_handler(req: web.Request) -> web.Response:
    if "application/json" in req.headers.get("Content-Type", ""):
        body = await req.json()
    else:
        return web.Response(status=415)
        
    activity = Activity().deserialize(body)
    auth_header = req.headers.get("Authorization", "")
    
    try:
        response = await adapter.process_activity(activity, auth_header, bot.on_turn)
        if response:
            return web.json_response(data=response.body, status=response.status)
        return web.Response(status=201)
    except Exception as e:
        print(f"Error processing activity: {e}")
        return web.Response(status=500)

app = web.Application()
app.router.add_post("/api/messages", messages_handler)

if __name__ == "__main__":
    print("EFRAG Bot server running on http://localhost:3978/api/messages")
    web.run_app(app, host="localhost", port=3978)