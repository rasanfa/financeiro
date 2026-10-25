from __future__ import annotations

from src.repositories.base import BaseRepository


class BaseService:
    """Regras de aplicação sobre um repositório. Sem operações ainda."""

    def __init__(self, repository: BaseRepository) -> None:
        self._repository = repository
