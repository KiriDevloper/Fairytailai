from moviepy.editor import (ImageClip, AudioFileClip,
                             TextClip, CompositeVideoClip)
from PIL import Image
import numpy as np


def create_video(image_path: str,
                 audio_path: str,
                 output_path: str,
                 title: str = "") -> str:
    """
    Ghep anh + audio thanh video MP4.
    - Hien thi anh trong suot thoi gian audio
    - Them tieu de o phia tren anh
    - Tra ve duong dan video da luu
    """
    # Doc audio lay do dai
    audio = AudioFileClip(audio_path)
    duration = audio.duration

    # Tao clip tu anh, resize ve 720p
    img_clip = (
        ImageClip(image_path)
        .set_duration(duration)
        .resize(height=720)
        .fadein(0.5)
        .fadeout(0.5)
    )

    clips = [img_clip]

    # Them tieu de neu co (can cai imagemagick tren may)
    # Neu loi thi bo comment doan try/except nay
    try:
        if title:
            txt_clip = (
                TextClip(title,
                         fontsize=36,
                         color="white",
                         stroke_color="black",
                         stroke_width=2,
                         method="caption",
                         size=(img_clip.w - 40, None))
                .set_position(("center", 30))
                .set_duration(duration)
            )
            clips.append(txt_clip)
    except Exception:
        pass  # Bo qua neu khong co ImageMagick

    # Ghep va xuat video
    final = CompositeVideoClip(clips).set_audio(audio)
    final.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        logger=None
    )

    audio.close()
    final.close()
    return output_path