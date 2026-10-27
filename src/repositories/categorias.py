from __future__ import annotations

from src.repositories.base import BaseRepository


class CategoriasRepository(BaseRepository):

    table_name = "categorias"

    def listar(self) -> list[dict]:

        response = (
            self.client
            .table(self.table_name)
            .select("*")
            .order("nome")
            .execute()
        )

        return response.data or []

    def criar(
        self,
        dados: dict
    ) -> dict:

        response = (
            self.client
            .table(self.table_name)
            .insert(dados)
            .execute()
        )

        return response.data[0]

    def atualizar(
        self,
        categoria_id: str,
        dados: dict
    ):

        (
            self.client
            .table(self.table_name)
            .update(dados)
            .eq("id", categoria_id)
            .execute()
        )

    def inativar(
        self,
        categoria_id: str
    ):

        (
            self.client
            .table(self.table_name)
            .update(
                {
                    "ativo": False
                }
            )
            .eq("id", categoria_id)
            .execute()
        )


class SubcategoriasRepository(BaseRepository):

    table_name = "subcategorias"

    def listar(self) -> list[dict]:

        response = (
            self.client
            .table(self.table_name)
            .select(
                """
                *,
                categorias (
                    nome
                )
                """
            )
            .order("nome")
            .execute()
        )

        return response.data or []

    def criar(
        self,
        dados: dict
    ) -> dict:

        response = (
            self.client
            .table(self.table_name)
            .insert(dados)
            .execute()
        )

        return response.data[0]

    def atualizar(
        self,
        subcategoria_id: str,
        dados: dict
    ):

        (
            self.client
            .table(self.table_name)
            .update(dados)
            .eq("id", subcategoria_id)
            .execute()
        )

    def inativar(
        self,
        subcategoria_id: str
    ):

        (
            self.client
            .table(self.table_name)
            .update(
                {
                    "ativo": False
                }
            )
            .eq("id", subcategoria_id)
            .execute()
        )