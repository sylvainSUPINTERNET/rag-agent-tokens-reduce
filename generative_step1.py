from dotenv import load_dotenv
from langchain.messages import AIMessage
load_dotenv()

import json
import base64
from langchain_google_genai import ChatGoogleGenerativeAI


def encode_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

image_base64 = encode_image("email.png")

model = ChatGoogleGenerativeAI(model="gemini-3.1-pro-preview", 
                               temperature=0
                               #vertexai=True,
                               )
messages = [
    (
        "system",
        """
You are a senior B2B negotiation expert specialized in client communications about pricing, equipment, and contracts.

You analyze email conversations (including screenshots) to extract meaning, detect leverage, and suggest negotiation strategy.

You MUST return ONLY a valid JSON with this structure:

{
 'item_name':'<name if present or null>',
 'quantity': <number if present or null>,
 'price': <number if present or null>
 'quick_summary': '<one or two sentences summarizing the client's position and intentions if none let it null>',
 }


Rules:
- Be pragmatic and business-oriented
- Detect hidden intentions (budget pressure, bluff, urgency tricks)
- Highlight anything suspicious or illogical
- Keep answers concise and actionable
- Do NOT add any text outside JSON
"""
    ),
    (
        "human",
        [
            {
                "type": "text",
                 "text": """
                 Analyze this client email and fetch the information with the right JSON format provided in the system prompt.
                 
                 """
            },
            {
                "type": "image_url",
                "image_url": f"data:image/png;base64,{image_base64}"
            },
        ],
    ),
]

ai_msg:AIMessage = model.invoke(messages)
content = ai_msg.content if isinstance(ai_msg.content, str) else json.dumps(ai_msg.content) if isinstance(ai_msg.content, (list, dict)) else str(ai_msg.content)
data = json.loads(content)
print(json.dumps(data, indent=2, ensure_ascii=False))

with open('generative_response_step1.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)