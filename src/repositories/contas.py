from __future__ import annotations

from src.repositories.base import BaseRepository


class ContasRepository(BaseRepository):

    table_name = "contas"

    def listar(self) -> list[dict]:

        response = (
            self.client
            .table(self.table_name)
            .select(
                """
                *,
                instituicoes (
                    nome
                )
                """
            )
            .order("apelido")
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
        conta_id: str,
        dados: dict
    ):

        (
            self.client
            .table(self.table_name)
            .update(dados)
            .eq("id", conta_id)
            .execute()
        )

    def inativar(
        self,
        conta_id: str
    ):

        (
            self.client
            .table(self.table_name)
            .update(
                {
                    "ativo": False
                }
            )
            .eq("id", conta_id)
            .execute()
        )