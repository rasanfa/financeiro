from src.repositories.cartoes import CartoesRepository
from src.services.base import BaseService


class CartoesService(BaseService):
    """Cadastro de cartões. CRUD será implementado depois."""

    def __init__(self, repository: CartoesRepository | None = None) -> None:
        super().__init__(repository or CartoesRepository())
