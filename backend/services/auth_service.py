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
        """Return available models by fetching them dynamically from provider endpoints."""
        valid_models: Dict[str, List[str]] = defaultdict(list)

        STATIC_MODELS = {
            "openai": ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
            "anthropic": [
                "claude-3-5-sonnet-20240620",
                "claude-3-opus-20240229",
                "claude-3-haiku-20240307",
            ],
            "google_genai": ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"],
            "groq": ["llama3-70b-8192", "llama3-8b-8192", "mixtral-8x7b-32768"],
            "mistralai": [
                "mistral-large-latest",
                "mistral-small-latest",
                "open-mixtral-8x7b",
            ],
            "openrouter": [
                "anthropic/claude-3.5-sonnet",
                "openai/gpt-4o",
                "meta-llama/llama-3-70b-instruct",
            ],
            "huggingface": [
                "meta-llama/Meta-Llama-3-70B-Instruct",
                "mistralai/Mixtral-8x7B-Instruct-v0.1",
            ],
        }

        # Check centralized environment keys
        provider_keys = {
            "openai": settings.openai_api_key,
            "anthropic": settings.anthropic_api_key,
            "google_genai": settings.google_api_key,
            "groq": settings.groq_api_key,
            "mistralai": settings.mistral_api_key,
            "openrouter": settings.openrouter_api_key,
            "huggingface": settings.huggingface_api_key,
        }

        # Retrieve user configured database keys
        user_keys = await self.get_all_api_keys(user)

        async with httpx.AsyncClient(timeout=4.0) as client:
            for provider in STATIC_MODELS:
                key = provider_keys.get(provider) or user_keys.get(provider)
                if not key:
                    continue

                url = _VALIDATION_URLS.get(provider)
                if not url:
                    valid_models[provider] = STATIC_MODELS[provider]
                    continue

                try:
                    if provider == "google_genai":
                        r = await client.get(f"{url}?key={key}")
                        if r.status_code == 200:
                            data = r.json()
                            models_list = [
                                m["name"].split("/")[-1] for m in data.get("models", [])
                            ]
                            if models_list:
                                valid_models[provider] = [
                                    m for m in models_list if "gemini" in m.lower()
                                ]
                            else:
                                valid_models[provider] = STATIC_MODELS[provider]
                        else:
                            valid_models[provider] = STATIC_MODELS[provider]
                    elif provider == "anthropic":
                        valid_models[provider] = STATIC_MODELS[provider]
                    else:
                        headers = {"Authorization": f"Bearer {key}"}
                        r = await client.get(url, headers=headers)
                        if r.status_code == 200:
                            data = r.json()
                            models_list = [m["id"] for m in data.get("data", [])]
                            if models_list:
                                valid_models[provider] = models_list[
                                    :15
                                ]  # Cap list size
                            else:
                                valid_models[provider] = STATIC_MODELS[provider]
                        else:
                            valid_models[provider] = STATIC_MODELS[provider]
                except Exception as e:
                    logger.warning(
                        f"Failed to dynamically fetch models for {provider}: {e}"
                    )
                    valid_models[provider] = STATIC_MODELS[provider]

        if not valid_models:
            valid_models["google_genai"] = STATIC_MODELS["google_genai"]

        return dict(valid_models)
