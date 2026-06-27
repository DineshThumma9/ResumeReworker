from collections import defaultdict
from typing import Dict, List

import httpx
from cryptography.fernet import Fernet
from fastapi import HTTPException
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from core.config import settings
from models.models import APIKEYS, User
from utils.constants import _VALIDATION_URLS


class CryptoService:
    def __init__(self):
        self.fernet = Fernet(settings.fernet_key)

    def encrypt(self, key: str) -> str:
        return self.fernet.encrypt(key.encode()).decode()

    def decrypt(self, key: str) -> str:
        return self.fernet.decrypt(key.encode()).decode()


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.crypto = CryptoService()

    async def get_api_key(self, provider: str, user: User) -> str:
        result = await self.db.execute(
            select(APIKEYS).where(
                APIKEYS.user_id == user.id,
                APIKEYS.provider == provider,
            )
        )
        api_key = result.scalars().first()
        if not api_key:
            raise HTTPException(
                status_code=404, detail=f"API KEY NOT FOUND: {provider}"
            )
        return self.crypto.decrypt(api_key.encrypted_key)

    async def get_all_api_keys(self, user: User) -> Dict[str, str]:
        result = await self.db.execute(
            select(APIKEYS).where(APIKEYS.user_id == user.id)
        )
        return {
            entry.provider: self.crypto.decrypt(entry.encrypted_key)
            for entry in result.scalars().all()
        }

    async def get_valid_models(self, user: User) -> Dict[str, List[str]]:
        """Return available models based on central settings."""
        valid_models: Dict[str, List[str]] = defaultdict(list)
        
        STATIC_MODELS = {
            "openai": ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
            "anthropic": ["claude-3-5-sonnet-20240620", "claude-3-opus-20240229", "claude-3-haiku-20240307"],
            "google_genai": ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"],
            "groq": ["llama3-70b-8192", "llama3-8b-8192", "mixtral-8x7b-32768"],
            "mistralai": ["mistral-large-latest", "mistral-small-latest", "open-mixtral-8x7b"],
            "openrouter": ["anthropic/claude-3.5-sonnet", "openai/gpt-4o", "meta-llama/llama-3-70b-instruct"],
            "huggingface": ["meta-llama/Meta-Llama-3-70B-Instruct", "mistralai/Mixtral-8x7B-Instruct-v0.1"],
        }

        # Check which providers have API keys set in the centralized config
        provider_keys = {
            "openai": settings.openai_api_key,
            "anthropic": settings.anthropic_api_key,
            "google_genai": settings.google_api_key,
            "groq": settings.groq_api_key,
            "mistralai": settings.mistral_api_key,
            "openrouter": settings.openrouter_api_key,
            "huggingface": settings.huggingface_api_key,
        }
        
        for provider, key in provider_keys.items():
            if key and provider in STATIC_MODELS:
                valid_models[provider] = STATIC_MODELS[provider]
        
        # Fallback if no keys are set (so UI isn't completely empty for testing)
        if not valid_models:
            # Just return Google GenAI as a dummy option if no keys are found
            valid_models["google_genai"] = STATIC_MODELS["google_genai"]
            
        return dict(valid_models)
