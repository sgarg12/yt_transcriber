import asyncio
import uuid
import os

import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq.middleware.middleware import Middleware
from sqlalchemy import select

from database import async_session_maker
from models import GeneratedTextFile
from settings import settings
from storage import Storage
from sound_to_text import SoundToText
from download_wav import downloadVideo
from email_sender import sendEmail

class SoundToTextMiddleware(Middleware):
    def __init__(self) -> None:
        super().__init__()
        self.sound_to_text = SoundToText()

    def after_process_boot(self, broker):
        self.sound_to_text.load_model()
        return super().after_process_boot(broker)

storage = Storage()
sound_to_text_middleware = SoundToTextMiddleware()
redis_broker = RedisBroker(host="localhost")
redis_broker.add_middleware(sound_to_text_middleware)
dramatiq.set_broker(redis_broker)

@dramatiq.actor()
def sound_to_text_task(file_id: int, receiver_email: str):
    file = get_file(file_id)
    
    new_path, title = downloadVideo(file.url)

    file_output = sound_to_text_middleware.sound_to_text.get_transcription_whisper(new_path)

    file_name = f"{uuid.uuid4()}.txt"

    storage = Storage()
    storage.upload_text(file_output, file_name, settings.storage_bucket)

    update_file_info(file, file_name, title)
    
    if receiver_email is not None:
        sendEmail(receiver_email, storage.get_presigned_url(file_name, settings.storage_bucket), title)
    os.remove(new_path)
    

def get_file(id: int) -> GeneratedTextFile:
    async def _get_file(id: int) -> GeneratedTextFile:
        async with async_session_maker() as session:
            select_query = select(GeneratedTextFile).where(GeneratedTextFile.id == id)
            result = await session.execute(select_query)
            f = result.scalar_one_or_none()

            if f is None:
                raise Exception("File does not exist")

            return f

    return asyncio.run(_get_file(id))
    
def update_file_info(file: GeneratedTextFile, file_name: str, title: str):
    async def _update_file_info(file: GeneratedTextFile, file_name: str, title: str):
        async with async_session_maker() as session:
            file.file_name = file_name
            file.title = title
            file.completed = True
            session.add(file)
            await session.commit()

    asyncio.run(_update_file_info(file, file_name, title))

    
