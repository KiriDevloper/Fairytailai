from gtts import gTTS
import asyncio


async def text_to_speech(text: str,
                          output_path: str,
                          voice: str = "female",
                          rate: str  = "-5%") -> str:
    """
    Chuyen van ban thanh file audio MP3 bang gTTS.
    Chay trong thread rieng de khong block async.
    """
    def _generate():
        tts = gTTS(text=text, lang="vi", slow=False)
        tts.save(output_path)

    # Chay dong bo trong thread pool de khong block FastAPI
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _generate)

    return output_path