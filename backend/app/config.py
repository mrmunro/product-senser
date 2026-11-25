from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    gemini_api_key: str = ""
    gemini_interviewer_model: str = "gemini-2.5-flash"
    gemini_evaluator_model: str = "gemini-2.5-flash"
    elevenlabs_api_key: str = ""
    elevenlabs_voice_id: str = "JBFqnCBsd6RMkjVDRZzb"
    elevenlabs_model_id: str = "eleven_flash_v2_5"
    backend_host: str = "127.0.0.1"
    backend_port: int = 8000

    cases_dir: Path = PROJECT_ROOT / "cases"
    sessions_dir: Path = PROJECT_ROOT / "sessions"

    @property
    def demo_mode(self) -> bool:
        return not bool(self.gemini_api_key and self.gemini_api_key.strip())

    @property
    def elevenlabs_configured(self) -> bool:
        return bool(self.elevenlabs_api_key and self.elevenlabs_api_key.strip())


settings = Settings()
