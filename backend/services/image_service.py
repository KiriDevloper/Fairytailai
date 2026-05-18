import os
import httpx
import asyncio  
import urllib.parse
from pathlib import Path

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")

# Định hình phong cách truyện cổ tích
STYLE = (
    "children fairy tale illustration, watercolor style, "
    "soft pastel colors, cute, dreamy, high quality, 4k"
)

async def generate_image(prompt_vi: str, save_path: str) -> str:
    """
    Dịch prompt sang tiếng Anh và gọi Pollinations.ai để sinh ảnh.
    """
    from services.groq_service import translate_to_english
    
    # 1. Dịch nội dung cảnh sang tiếng Anh
    prompt_en = await translate_to_english(prompt_vi)
    full_prompt = f"{prompt_en}, {STYLE}"
    
    # 2. Encode prompt để đưa vào URL (xử lý các ký tự đặc biệt)
    encoded_prompt = urllib.parse.quote(full_prompt)
    # Model 'flux' trên Pollinations hiện đang rất đẹp và miễn phí
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&model=flux&nologo=true&seed={os.urandom(4).hex()}"

    try:
        print(f"    Sử dụng Pollinations: {full_prompt[:60]}...")
        
        async with httpx.AsyncClient() as client:
            # Gọi API lấy dữ liệu ảnh (binary)
            response = await client.get(url, timeout=90)
            
            if response.status_code == 200:
                # Tạo thư mục nếu chưa có
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                
                # Lưu dữ liệu binary thành file ảnh
                with open(save_path, "wb") as f:
                    f.write(response.content)
                
                print(f"    => Đã lưu ảnh thành công: {save_path}")
                return save_path
            else:
                raise Exception(f"Pollinations trả về lỗi: {response.status_code}")

    except Exception as e:
        print(f"    [!] Lỗi khi sinh ảnh: {str(e)}")
        # Bạn có thể trả về một ảnh mặc định nếu lỗi để code không bị dừng
        return ""

async def generate_scenes(scenes: list, story_id: str) -> list:
    """
    Lặp qua các phân cảnh để sinh ảnh tự động.
    """
    image_paths = []

    for scene in scenes:
        idx  = scene["index"]
        desc = scene.get("description", scene.get("text", ""))
        # Đường dẫn lưu ảnh: uploads/storyid_scene_0.png
        path = os.path.join(UPLOAD_DIR, f"{story_id}_scene_{idx}.png")

        print(f"  [Cảnh {idx+1}/{len(scenes)}] Đang vẽ...")
        img_path = await generate_image(desc, path)
        
        if img_path:
            await asyncio.sleep(2)
            image_paths.append(img_path)
            
    return image_paths