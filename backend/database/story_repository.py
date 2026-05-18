from datetime import datetime
from typing import Optional
from beanie import PydanticObjectId
from database.models import Story, StatusEnum


async def create_story(user_text: str, session_id: str,
                        user_id: str = None) -> Story:
    story = Story(user_text=user_text, session_id=session_id, user_id=user_id)
    await story.insert()
    return story


async def update_script(story_id, title: str, script: str):
    story = await Story.get(story_id)
    if story:
        story.title = title; story.script = script
        story.updated_at = datetime.utcnow()
        await story.save()
    return story


async def update_files(story_id, image_path=None,
                        audio_path=None, video_path=None):
    story = await Story.get(story_id)
    if story:
        if image_path: story.files.image_path = image_path
        if audio_path: story.files.audio_path = audio_path
        if video_path: story.files.video_path = video_path
        story.updated_at = datetime.utcnow()
        await story.save()
    return story


async def update_status(story_id, status: StatusEnum, error: str = None):
    story = await Story.get(story_id)
    if story:
        story.status = status; story.error_message = error
        story.updated_at = datetime.utcnow()
        await story.save()
    return story


async def get_by_id(story_id: PydanticObjectId):
    return await Story.get(story_id)


async def get_by_user(user_id: str, limit: int = 50):
    return (await Story.find(Story.user_id == user_id)
            .sort(-Story.created_at).limit(limit).to_list())


async def get_by_session(session_id: str, limit: int = 20):
    return (await Story.find(Story.session_id == session_id)
            .sort(-Story.created_at).limit(limit).to_list())


async def get_all(limit: int = 50):
    return (await Story.find_all()
            .sort(-Story.created_at).limit(limit).to_list())


async def delete_by_id(story_id: PydanticObjectId) -> bool:
    story = await Story.get(story_id)
    if not story: return False
    await story.delete()
    return True