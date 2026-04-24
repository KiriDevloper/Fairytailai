import uuid
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from beanie import PydanticObjectId

from database.models      import StatusEnum
from database             import story_repository as repo
from services.gemini_service import generate_story
from services.tts_service    import text_to_speech
from services.video_service  import create_video
from utils.file_helper       import save_upload, build_output_path
from utils.response_helper   import success, error

router = APIRouter(prefix="/stories", tags=["Stories"])


# ── POST /stories/create ──────────────────────────────────────

@router.post("/create")
async def create_fairytale(
    file:       UploadFile = File(...),
    user_text:  str        = Form(...),
    session_id: str        = Form(default=""),
):
    """
    Nhan anh + text -> sinh kich ban -> TTS -> tao video -> luu DB.
    """
    if not session_id:
        session_id = f"sess_{uuid.uuid4().hex[:12]}"

    # 1. Tao story moi trong DB (status: pending)
    story    = await repo.create_story(user_text=user_text,
                                       session_id=session_id)
    story_id = story.id

    try:
        # 2. Luu anh upload
        image_path = await save_upload(file, str(story_id))
        await repo.update_files(story_id, image_path=image_path)

        # 3. Gemini: phan tich anh + sinh kich ban
        result = await generate_story(image_path, user_text)
        title  = result["title"]
        script = result["script"]
        await repo.update_script(story_id, title=title, script=script)

        # 4. Edge TTS: sinh audio
        audio_path = build_output_path(str(story_id), ".mp3")
        await text_to_speech(script, audio_path)
        await repo.update_files(story_id, audio_path=audio_path)

        # 5. MoviePy: tao video
        video_path = build_output_path(str(story_id), ".mp4")
        create_video(image_path, audio_path, video_path, title)
        await repo.update_files(story_id, video_path=video_path)

        # 6. Cap nhat status: done
        await repo.update_status(story_id, StatusEnum.DONE)

        return success({
            "story_id":   str(story_id),
            "session_id": session_id,
            "title":      title,
            "script":     script,
            "video_url":  f"/outputs/{story_id}.mp4",
            "audio_url":  f"/outputs/{story_id}.mp3",
        }, message="Tao video thanh cong!")

    except Exception as e:
        await repo.update_status(story_id, StatusEnum.FAILED, str(e))
        raise HTTPException(status_code=500, detail=str(e))


# ── GET /stories ──────────────────────────────────────────────

@router.get("")
async def list_stories(limit: int = 50):
    """Lay tat ca cau chuyen (moi nhat truoc)."""
    stories = await repo.get_all(limit)
    return success({"total": len(stories), "stories": stories})


# ── GET /stories/session/{session_id} ────────────────────────

@router.get("/session/{session_id}")
async def get_history(session_id: str):
    """Lay lich su tao video theo phien lam viec."""
    stories = await repo.get_by_session(session_id)
    return success({
        "session_id": session_id,
        "total":      len(stories),
        "stories":    stories
    })


# ── GET /stories/{story_id} ───────────────────────────────────

@router.get("/{story_id}")
async def get_story(story_id: str):
    """Lay chi tiet 1 cau chuyen theo ID."""
    story = await repo.get_by_id(PydanticObjectId(story_id))
    if not story:
        raise HTTPException(status_code=404,
                            detail="Khong tim thay cau chuyen.")
    return success(story)


# ── DELETE /stories/{story_id} ────────────────────────────────

@router.delete("/{story_id}")
async def delete_story(story_id: str):
    """Xoa 1 cau chuyen theo ID."""
    deleted = await repo.delete_by_id(PydanticObjectId(story_id))
    if not deleted:
        raise HTTPException(status_code=404,
                            detail="Khong tim thay cau chuyen.")
    return success({"deleted_id": story_id}, message="Da xoa thanh cong.")