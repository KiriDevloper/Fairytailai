import asyncio
from gtts import gTTS


async def text_to_speech(text: str,
                          output_path: str,
                          lang: str = "vi") -> str:
    """
    Chuyen van ban thanh file audio MP3 bang gTTS.
    - lang="vi" : giong Viet Nam
    - Chay trong thread rieng de khong block async
    - Tra ve duong dan file da luu
    """
    def _generate():
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(output_path)

    # gTTS la thu vien dong bo, chay trong executor de khong block FastAPI
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _generate)

    return output_path