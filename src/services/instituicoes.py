from src.repositories.instituicoes import InstituicoesRepository
from src.services.base import BaseService


class InstituicoesService(BaseService):
    """Cadastro de instituições. CRUD será implementado depois."""

    def __init__(self, repository: InstituicoesRepository | None = None) -> None:
        super().__init__(repository or InstituicoesRepository())
