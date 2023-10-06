import contextlib

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import schemas
from database import create_all_tables, get_async_session
from models import GeneratedTextFile
from settings import settings
from storage import Storage
from worker import sound_to_text_task


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    await create_all_tables()
    yield


app = FastAPI(lifespan=lifespan)

async def get_generated_textfile_or_404(
    id: int, session: AsyncSession = Depends(get_async_session)
) -> GeneratedTextFile:
    select_query = select(GeneratedTextFile).where(GeneratedTextFile.id == id)
    result = await session.execute(select_query)
    f = result.scalar_one_or_none()

    if f is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return f


async def get_storage() -> Storage:
    return Storage()


@app.post(
    "/generate-file",
    response_model=schemas.GeneratedTextFileRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_generated_textfile(
    generated_textfile_create: schemas.GeneratedTextFileCreate,
    session: AsyncSession = Depends(get_async_session),
) -> GeneratedTextFile:
    f = GeneratedTextFile(url=generated_textfile_create.url)
    session.add(f)
    await session.commit()

    sound_to_text_task.send(f.id, generated_textfile_create.email)
    return f

@app.get("/generated-file/{id}", response_model=schemas.GeneratedTextFileRead)
async def get_generated_file(
    file: GeneratedTextFile = Depends(get_generated_textfile_or_404),
) -> GeneratedTextFile:
    return file

@app.get("/generated-file/{id}/url")
async def get_generated_file_url(
    file: GeneratedTextFile = Depends(get_generated_textfile_or_404),
    storage: Storage = Depends(get_storage),
) -> schemas.GeneratedTextFileURL:
    if not file.completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is not available yet. Please try again later.",
        )

    url = storage.get_presigned_url(file.file_name, settings.storage_bucket)
    return schemas.GeneratedTextFileURL(url=url)