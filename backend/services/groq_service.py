import json
import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))
MODEL = "llama-3.3-70b-versatile"


async def generate_story(user_text: str) -> dict:
    """
    Dung Groq sinh kich ban co tich 4 canh + mo ta hinh anh tung canh.
    Output: { title, script, scenes: [ {index, text, description} ] }
    """
    chat = client.chat.completions.create(
        model=MODEL,
        temperature=0.8,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    "Ban la nha ke chuyen co tich Viet Nam tai ba danh cho tre em. "
                    "Luon tra loi bang JSON hop le, khong them gi ngoai JSON."
                )
            },
            {
                "role": "user",
                "content": f"""
Goi y: "{user_text}"

Viet mot cau chuyen co tich co 4 canh, moi canh 2-3 cau, ngon ngu trong sang phu hop tre em.
Moi canh them mo ta hinh anh cu the (nhan vat, mau sac, boi canh) de AI sinh anh minh hoa.

Tra loi theo dinh dang JSON:
{{
  "title": "Tieu de ngan gon thu vi (toi da 10 tu)",
  "scenes": [
    {{
      "index": 0,
      "text": "Noi dung canh 1 (2-3 cau ke chuyen)",
      "description": "Mo ta hinh anh canh 1: nhan vat lam gi, o dau, trang phuc, mau sac"
    }},
    {{
      "index": 1,
      "text": "Noi dung canh 2",
      "description": "Mo ta hinh anh canh 2"
    }},
    {{
      "index": 2,
      "text": "Noi dung canh 3",
      "description": "Mo ta hinh anh canh 3"
    }},
    {{
      "index": 3,
      "text": "Noi dung canh 4",
      "description": "Mo ta hinh anh canh 4"
    }}
  ]
}}
"""
            }
        ]
    )

    raw    = chat.choices[0].message.content.strip()
    data   = json.loads(raw)
    title  = data["title"]
    scenes = data["scenes"]
    script = " ".join(s["text"] for s in scenes)

    return {"title": title, "script": script, "scenes": scenes}


async def translate_to_english(text_vi: str) -> str:
    """
    Dung Groq dich mo ta canh tu tieng Viet sang tieng Anh
    de HuggingFace Stable Diffusion hieu tot hon.
    """
    chat = client.chat.completions.create(
        model=MODEL,
        temperature=0.3,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a translator. Translate Vietnamese scene descriptions "
                    "to English for AI image generation prompts. "
                    "Return ONLY the English translation, nothing else."
                )
            },
            {
                "role": "user",
                "content": f"Translate to English: {text_vi}"
            }
        ]
    )
    return chat.choices[0].message.content.strip()