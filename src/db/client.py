from __future__ import annotations

from functools import lru_cache

from supabase import Client, create_client

from src.config import get_settings


class SupabaseNotConfiguredError(RuntimeError):
    """Raised when SUPABASE_URL or SUPABASE_KEY is missing."""


@lru_cache(maxsize=1)
def get_supabase_client() -> Client:
    settings = get_settings()
    if not settings.supabase_configured:
        raise SupabaseNotConfiguredError(
            "Defina SUPABASE_URL e SUPABASE_KEY no arquivo .env."
        )
    return create_client(settings.supabase_url, settings.supabase_key)
