import os

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())


class Settings:
    OPENAI_KEY: str = os.environ["OPENAI_KEY"]
    REVIEWER_MODEL: str = os.environ["REVIEWER_MODEL"]
    HEADER_EXTRACTOR_MODEL: str = os.environ["HEADER_EXTRACTOR_MODEL"]
    GROBID_URL: str = os.environ.get("GROBID_URL", "http://localhost:8070")
    CORS_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.environ.get("CORS_ORIGINS", "http://localhost:8080").split(",")
        if origin.strip()
    ]
    MAX_UPLOAD_MB: int = int(os.environ.get("MAX_UPLOAD_MB", "20"))
    SEMANTIC_SCHOLAR_API_KEY: str = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "")
    TAVILY_API_KEY: str = os.environ.get("TAVILY_API_KEY", "")


settings = Settings()
