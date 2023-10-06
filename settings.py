from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    storage_endpoint: str
    storage_access_key: str
    storage_secret_key: str
    storage_bucket: str
    email_app_pass: str

    class Config:
        env_file = ".env"


settings = Settings()