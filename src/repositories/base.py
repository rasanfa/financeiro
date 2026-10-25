from __future__ import annotations

from supabase import Client

from src.db.client import get_supabase_client


class BaseRepository:
    """Acesso a uma tabela ou view do schema V1. Sem operações ainda."""

    table_name: str = ""

    def __init__(self, client: Client | None = None) -> None:
        self._client = client

    @property
    def client(self) -> Client:
        if self._client is None:
            self._client = get_supabase_client()
        return self._client
