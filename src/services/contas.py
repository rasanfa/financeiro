from src.repositories.contas import ContasRepository
from src.services.base import BaseService


class ContasService(BaseService):
    """Cadastro de contas. CRUD será implementado depois."""

    def __init__(self, repository: ContasRepository | None = None) -> None:
        super().__init__(repository or ContasRepository())
