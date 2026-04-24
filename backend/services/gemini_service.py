# import google.generativeai as genai
# from PIL import Image
# from config import GEMINI_API_KEY
# import time

# genai.configure(api_key=GEMINI_API_KEY)

# # Thu lan luot cac model, model nao kha dung thi dung
# MODELS = [
#     "gemini-1.5-flash-latest",
#     "gemini-1.5-flash-001",
#     "gemini-1.5-pro-latest",
#     "gemini-2.0-flash",
# ]


# async def generate_story(image_path: str, user_text: str) -> dict:
#     image = Image.open(image_path)

#     prompt = f"""
# Ban la mot nha ke chuyen co tich Viet Nam tai ba danh cho tre em.

# Dua vao hinh anh va goi y nay: "{user_text}"

# Hay thuc hien 2 viec:
# 1. Dat mot tieu de hay cho cau chuyen (ngan gon, thu vi, toi da 10 tu)
# 2. Ke mot cau chuyen co tich ngan (6-8 cau), ngon ngu trong sang, phu hop tre em 5-10 tuoi.

# Tra loi CHINH XAC theo dinh dang sau (khong them gi khac):
# TITLE: <tieu de>
# STORY: <noi dung cau chuyen>
# """

#     last_error = None

#     # Thu tung model, neu loi thi thu model tiep theo
#     for model_name in MODELS:
#         try:
#             model    = genai.GenerativeModel(model_name)
#             response = model.generate_content([prompt, image])
#             text     = response.text.strip()

#             title  = ""
#             script = ""
#             for line in text.splitlines():
#                 if line.startswith("TITLE:"):
#                     title = line.replace("TITLE:", "").strip()
#                 elif line.startswith("STORY:"):
#                     script = line.replace("STORY:", "").strip()

#             if not title:  title  = text.split(".")[0][:60]
#             if not script: script = text

#             print(f"Dung model: {model_name}")
#             return {"title": title, "script": script}

#         except Exception as e:
#             print(f"Model {model_name} loi: {e}")
#             last_error = e
#             time.sleep(3)  # Cho 3 giay truoc khi thu model tiep
#             continue

#     # Tat ca model deu that bai
#     raise Exception(f"Tat ca model Gemini deu loi: {last_error}")
import google.generativeai as genai
from groq import Groq
from PIL import Image
from config import GEMINI_API_KEY, GROQ_API_KEY

genai.configure(api_key=GEMINI_API_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)


async def _describe_image(image_path: str) -> str:
    """Dung Gemini mo ta anh ngan gon (rat it token)."""
    try:
        image = Image.open(image_path)
        model = genai.GenerativeModel("gemini-2.0-flash")
        resp  = model.generate_content([
            "Mo ta ngan gon hinh anh nay trong 2-3 cau tieng Viet. "
            "Chi mo ta nhung gi nhin thay, khong them gi khac.",
            image
        ])
        return resp.text.strip()
    except Exception as e:
        print(f"Gemini mo ta anh loi: {e}")
        return "Mot canh dep trong tu nhien"  # fallback


async def generate_story(image_path: str, user_text: str) -> dict:
    """
    B1: Gemini mo ta anh (it token)
    B2: Groq sinh kich ban co tich (khong gioi han)
    """
    # Buoc 1: Mo ta anh
    image_desc = await _describe_image(image_path)
    print(f"Mo ta anh: {image_desc}")

    # Buoc 2: Groq sinh kich ban
    prompt = f"""Ban la nha ke chuyen co tich Viet Nam tai ba danh cho tre em.

Hinh anh mo ta: {image_desc}
Goi y them tu nguoi dung: {user_text}

Hay thuc hien 2 viec:
1. Dat mot tieu de hay cho cau chuyen (ngan gon, toi da 10 tu)
2. Ke mot cau chuyen co tich ngan (6-8 cau), ngon ngu trong sang, phu hop tre em 5-10 tuoi.

Tra loi CHINH XAC theo dinh dang (khong them gi khac):
TITLE: <tieu de>
STORY: <noi dung cau chuyen>"""

    response = groq_client.chat.completions.create(
        model    = "llama-3.3-70b-versatile",  # Model manh nhat, mien phi
        messages = [{"role": "user", "content": prompt}],
        max_tokens = 800,
    )

    text   = response.choices[0].message.content.strip()
    title  = ""
    script = ""

    for line in text.splitlines():
        if line.startswith("TITLE:"):
            title = line.replace("TITLE:", "").strip()
        elif line.startswith("STORY:"):
            script = line.replace("STORY:", "").strip()

    if not title:  title  = text.split(".")[0][:60]
    if not script: script = text

    print(f"Sinh kich ban thanh cong bang Groq!")
    return {"title": title, "script": script}