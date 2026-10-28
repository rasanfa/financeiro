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
        
    def listar_subcategorias(self):

        return self._subcategorias.listar()

    def criar_subcategoria(
        self,
        categoria_id: str,
        nome: str
    ):

        return self._subcategorias.criar(
            {
                "categoria_id": categoria_id,
                "nome": nome,
                "ativo": True
            }
        )

    def atualizar_subcategoria(
        self,
        subcategoria_id: str,
        categoria_id: str,
        nome: str
    ):

        self._subcategorias.atualizar(
            subcategoria_id,
            {
                "categoria_id": categoria_id,
                "nome": nome
            }
        )

    def inativar_subcategoria(
        self,
        subcategoria_id: str
    ):

        self._subcategorias.inativar(
            subcategoria_id
        )