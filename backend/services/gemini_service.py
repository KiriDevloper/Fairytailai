# import json
# import google.generativeai as genai
# from config import GEMINI_API_KEY

# genai.configure(api_key=GEMINI_API_KEY)
# # gemini-1.5-flash da bi tat - dung gemini-2.0-flash
# model = genai.GenerativeModel("gemini-2.0-flash")


# async def generate_story(user_text: str) -> dict:
#     """
#     Sinh kich ban co tich va tach thanh cac canh co mo ta hinh anh.
#     Input : goi y noi dung tu nguoi dung (text)
#     Output: { title, script, scenes: [ {index, text, description} ] }
#     """
#     prompt = f"""
# Ban la nha ke chuyen co tich Viet Nam tai ba danh cho tre em.

# Goi y: "{user_text}"

# Hay thuc hien:
# 1. Dat tieu de hay cho cau chuyen (ngan, thu vi, toi da 10 tu)
# 2. Viet cau chuyen co 4 canh, moi canh 2-3 cau, ngon ngu trong sang cho tre em.
# 3. Moi canh them mo ta hinh anh cu the (nhan vat, mau sac, boi canh) de AI ve tranh.

# Tra loi CHINH XAC theo dinh dang JSON sau, khong them gi khac:
# {{
#   "title": "Tieu de cau chuyen",
#   "scenes": [
#     {{
#       "index": 0,
#       "text": "Noi dung canh 1 (2-3 cau ke chuyen)",
#       "description": "Mo ta hinh anh canh 1: nhan vat lam gi, o dau, trang phuc, mau sac boi canh"
#     }},
#     {{
#       "index": 1,
#       "text": "Noi dung canh 2",
#       "description": "Mo ta hinh anh canh 2"
#     }},
#     {{
#       "index": 2,
#       "text": "Noi dung canh 3",
#       "description": "Mo ta hinh anh canh 3"
#     }},
#     {{
#       "index": 3,
#       "text": "Noi dung canh 4",
#       "description": "Mo ta hinh anh canh 4"
#     }}
#   ]
# }}
# """
#     response = model.generate_content(prompt)
#     raw = response.text.strip()

#     # Loai bo markdown ```json ... ``` neu co
#     raw = raw.replace("```json", "").replace("```", "").strip()

#     data   = json.loads(raw)
#     title  = data["title"]
#     scenes = data["scenes"]

#     # Ghep toan bo text thanh script hoan chinh
#     script = " ".join(s["text"] for s in scenes)

#     return {"title": title, "script": script, "scenes": scenes}