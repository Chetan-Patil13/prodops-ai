# backend/app/core/config.py

import os
from dotenv import load_dotenv
from pathlib import Path

# Load env file (same logic as seed_data.py)
env_path = Path(__file__).resolve().parent.parent.parent.parent / ".env.example"
load_dotenv(env_path)


class Settings:
    DB_USER: str = os.getenv("USER")
    DB_PASSWORD: str = os.getenv("PASSWORD")
    DB_HOST: str = os.getenv("HOST")
    DB_PORT: str = os.getenv("PORT")
    DB_NAME: str = os.getenv("DBNAME")

    ENV: str = os.getenv("ENV", "dev")

    @property
    def DATABASE_URL(self) -> str:
        if not all(
            [
                self.DB_USER,
                self.DB_PASSWORD,
                self.DB_HOST,
                self.DB_PORT,
                self.DB_NAME,
            ]
        ):
            raise RuntimeError("One or more DB environment variables are missing")

        return (
            f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            "?sslmode=require"
        )


settings = Settings()
