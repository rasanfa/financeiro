from __future__ import annotations

from src.repositories.categorias import (
    CategoriasRepository,
    SubcategoriasRepository,
)

from src.services.base import BaseService


class CategoriasService(BaseService):

    def __init__(
        self,
        repository: CategoriasRepository | None = None,
        subcategorias: SubcategoriasRepository | None = None,
    ) -> None:

        super().__init__(
            repository or CategoriasRepository()
        )

        self._subcategorias = (
            subcategorias
            or SubcategoriasRepository()
        )

    def listar(self) -> list[dict]:

        return self.repository.listar()

    def criar(
        self,
        usuario_id: str,
        nome: str,
        tipo_categoria: str
    ):

        nome = nome.strip()

        if not nome:
            raise ValueError(
                "Nome da categoria é obrigatório."
            )

        return self.repository.criar(
            {
                "usuario_id": usuario_id,
                "nome": nome,
                "tipo_categoria": tipo_categoria,
                "ativo": True
            }
        )

    def atualizar(
        self,
        categoria_id: str,
        nome: str,
        tipo_categoria: str
    ):

        self.repository.atualizar(
            categoria_id,
            {
                "nome": nome,
                "tipo_categoria": tipo_categoria
            }
        )

    def inativar(
        self,
        categoria_id: str
    ):

        self.repository.inativar(
            categoria_id
        )