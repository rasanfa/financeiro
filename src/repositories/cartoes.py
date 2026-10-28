from __future__ import annotations

from src.repositories.base import BaseRepository


class CartoesRepository(BaseRepository):

    table_name = "cartoes"

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
        cartao_id: str,
        dados: dict
    ):

        (
            self.client
            .table(self.table_name)
            .update(dados)
            .eq("id", cartao_id)
            .execute()
        )

    def inativar(
        self,
        cartao_id: str
    ):

        (
            self.client
            .table(self.table_name)
            .update(
                {
                    "ativo": False
                }
            )
            .eq("id", cartao_id)
            .execute()
        )
