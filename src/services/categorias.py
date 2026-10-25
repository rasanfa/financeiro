from src.repositories.categorias import CategoriasRepository, SubcategoriasRepository
from src.services.base import BaseService


class CategoriasService(BaseService):
    """Cadastro de categorias e subcategorias. CRUD será implementado depois."""

    def __init__(
        self,
        repository: CategoriasRepository | None = None,
        subcategorias: SubcategoriasRepository | None = None,
    ) -> None:
        super().__init__(repository or CategoriasRepository())
        self._subcategorias = subcategorias or SubcategoriasRepository()
