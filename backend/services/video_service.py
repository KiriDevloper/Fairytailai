from moviepy.editor import (ImageClip, AudioFileClip,
                             concatenate_videoclips, CompositeVideoClip)


def create_video(image_paths: list,
                 audio_path: str,
                 output_path: str,
                 title: str = "") -> str:
    """
    Ghep nhieu anh + 1 audio thanh video MP4.
    - Moi anh hien thi dung phan deu thoi gian audio
    - Co hieu ung fade giua cac canh
    - Tra ve duong dan video da luu
    """
    audio    = AudioFileClip(audio_path)
    duration = audio.duration

    # Chia deu thoi gian cho moi anh
    n               = len(image_paths)
    time_per_scene  = duration / n

    clips = []
    for i, img_path in enumerate(image_paths):
        clip = (
            ImageClip(img_path)
            .set_duration(time_per_scene)
            .resize(height=720)
            .fadein(0.4)
            .fadeout(0.4)
        )
        clips.append(clip)

    # Ghep tat ca canh lai
    final_video = concatenate_videoclips(clips, method="compose")
    final_video = final_video.set_audio(audio)

    final_video.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        logger=None
    )

    audio.close()
    final_video.close()
    return output_path