import uuid
from fastapi import APIRouter, Form, HTTPException, Depends
from beanie import PydanticObjectId

from database.models        import StatusEnum
from database               import story_repository as repo
from services.groq_service  import generate_story
from services.image_service import generate_scenes
from services.tts_service   import text_to_speech
from services.video_service import create_video
from services.auth_service  import require_login, check_and_consume
from utils.file_helper      import build_output_path
from utils.response_helper  import success
from database.models        import User

router = APIRouter(prefix="/stories", tags=["Stories"])


@router.post("/create")
async def create_fairytale(
    user_text:  str  = Form(...),
    session_id: str  = Form(default=""),
    user:       User = Depends(require_login),
):
    """
    Kiem tra luot dung -> Groq sinh kich ban -> HuggingFace sinh anh
    -> gTTS tao audio -> MoviePy ghep video -> luu MongoDB
    """
    if not session_id:
        session_id = f"sess_{uuid.uuid4().hex[:12]}"

    # 1. Kiem tra luot dung
    usage = await check_and_consume(user)
    if not usage["allowed"]:
        raise HTTPException(status_code=429, detail={
            "message":      usage["message"],
            "used_today":   usage["used_today"],
            "limit":        usage["limit"],
            "need_upgrade": usage["need_upgrade"],
        })

    story    = await repo.create_story(
        user_text  = user_text,
        session_id = session_id,
        user_id    = str(user.id)
    )
    story_id = story.id

    try:
        # 2. Groq: sinh kich ban
        print(f"[{story_id}] Groq dang sinh kich ban...")
        result = await generate_story(user_text)
        title  = result["title"]
        script = result["script"]
        scenes = result["scenes"]
        await repo.update_script(story_id, title=title, script=script)

        # 3. Pollinations: sinh anh tung canh
        print(f"[{story_id}] Dang sinh {len(scenes)} anh...")
        image_paths = await generate_scenes(scenes, str(story_id))
        await repo.update_files(story_id, image_path=image_paths[0])

        # 4. gTTS: tao audio
        print(f"[{story_id}] Dang tao audio...")
        audio_path = build_output_path(str(story_id), ".mp3")
        await text_to_speech(script, audio_path)
        await repo.update_files(story_id, audio_path=audio_path)

        # 5. MoviePy: tao video
        print(f"[{story_id}] Dang tao video...")
        video_path = build_output_path(str(story_id), ".mp4")
        create_video(image_paths, audio_path, video_path, title)
        await repo.update_files(story_id, video_path=video_path)

        await repo.update_status(story_id, StatusEnum.DONE)
        print(f"[{story_id}] HOAN THANH!")

        return success({
            "story_id":    str(story_id),
            "session_id":  session_id,
            "title":       title,
            "script":      script,
            "scenes":      scenes,
            "image_count": len(image_paths),
            "video_url":   f"/outputs/{story_id}.mp4",
            "audio_url":   f"/outputs/{story_id}.mp3",
            "usage":       usage,
        }, message="Tao video thanh cong!")

    except Exception as e:
        await repo.update_status(story_id, StatusEnum.FAILED, str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
async def list_stories(user: User = Depends(require_login)):
    stories = await repo.get_by_user(str(user.id))
    return success({"total": len(stories), "stories": stories})


@router.get("/session/{session_id}")
async def get_history(session_id: str, user: User = Depends(require_login)):
    stories = await repo.get_by_session(session_id)
    return success({"total": len(stories), "stories": stories})


@router.get("/{story_id}")
async def get_story(story_id: str, user: User = Depends(require_login)):
    story = await repo.get_by_id(PydanticObjectId(story_id))
    if not story:
        raise HTTPException(404, "Khong tim thay cau chuyen")
    return success(story)


@router.delete("/{story_id}")
async def delete_story(story_id: str, user: User = Depends(require_login)):
    deleted = await repo.delete_by_id(PydanticObjectId(story_id))
    if not deleted:
        raise HTTPException(404, "Khong tim thay cau chuyen")
    return success({"deleted_id": story_id}, message="Da xoa thanh cong")