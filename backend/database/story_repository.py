from datetime import datetime
from typing import Optional
from beanie import PydanticObjectId
from database.models import Story, FilePaths, StatusEnum


# ── CREATE ────────────────────────────────────────────────────

async def create_story(user_text: str, session_id: str) -> Story:
    story = Story(user_text=user_text, session_id=session_id)
    await story.insert()
    return story


# ── UPDATE ────────────────────────────────────────────────────

async def update_script(story_id: PydanticObjectId,
                         title: str, script: str) -> Optional[Story]:
    story = await Story.get(story_id)
    if not story:
        return None
    story.title      = title
    story.script     = script
    story.updated_at = datetime.utcnow()
    await story.save()
    return story


async def update_files(story_id: PydanticObjectId,
                        image_path: str = None,
                        audio_path: str = None,
                        video_path: str = None) -> Optional[Story]:
    story = await Story.get(story_id)
    if not story:
        return None
    if image_path: story.files.image_path = image_path
    if audio_path: story.files.audio_path = audio_path
    if video_path: story.files.video_path = video_path
    story.updated_at = datetime.utcnow()
    await story.save()
    return story


async def update_status(story_id: PydanticObjectId,
                         status: StatusEnum,
                         error_message: str = None) -> Optional[Story]:
    story = await Story.get(story_id)
    if not story:
        return None
    story.status        = status
    story.error_message = error_message
    story.updated_at    = datetime.utcnow()
    await story.save()
    return story


# ── READ ──────────────────────────────────────────────────────

async def get_by_id(story_id: PydanticObjectId) -> Optional[Story]:
    return await Story.get(story_id)


async def get_by_session(session_id: str, limit: int = 20) -> list[Story]:
    return (
        await Story
        .find(Story.session_id == session_id)
        .sort(-Story.created_at)
        .limit(limit)
        .to_list()
    )


async def get_all(limit: int = 50) -> list[Story]:
    return (
        await Story
        .find_all()
        .sort(-Story.created_at)
        .limit(limit)
        .to_list()
    )


# ── DELETE ────────────────────────────────────────────────────

async def delete_by_id(story_id: PydanticObjectId) -> bool:
    story = await Story.get(story_id)
    if not story:
        return False
    await story.delete()
    return True