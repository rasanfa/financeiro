from src.repositories.movimentacoes import MovimentacoesRepository
from src.services.base import BaseService


class MovimentacoesService(BaseService):
    """Lançamentos financeiros. CRUD será implementado depois."""

    def __init__(self, repository: MovimentacoesRepository | None = None) -> None:
        super().__init__(repository or MovimentacoesRepository())
