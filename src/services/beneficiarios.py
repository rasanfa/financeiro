from src.repositories.beneficiarios import BeneficiariosRepository
from src.services.base import BaseService


class BeneficiariosService(BaseService):
    """Cadastro de beneficiários. CRUD será implementado depois."""

    def __init__(self, repository: BeneficiariosRepository | None = None) -> None:
        super().__init__(repository or BeneficiariosRepository())
