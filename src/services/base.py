from __future__ import annotations

from src.repositories.base import BaseRepository


class BaseService:

    def __init__(self, repository: BaseRepository) -> None:
        self._repository = repository

    @property
    def repository(self) -> BaseRepository:
        return self._repository