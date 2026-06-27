



from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    jwt_secret: str
    jwt_expire:int 
    jwt_algorithm:str 
    google_client_id:str 
    google_client_secret:str 
    google_redirect_uri:str 
    google_auth_url:str 
    google_token_url:str 
    google_user_url:str 
    cloudinary_url:str 
    cloudconvert_api_key:str 
    database_url:str 
    fernet_key: str
    frontend_url: str = "http://localhost:5173"
    dev_mode: bool = False
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    google_api_key: str | None = None
    groq_api_key: str | None = None
    mistral_api_key: str | None = None
    openrouter_api_key: str | None = None
    huggingface_api_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
