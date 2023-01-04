from pydantic import BaseSettings


class Settings(BaseSettings):
    marvel_public_key: str
    marvel_private_key: str


settings = Settings()
