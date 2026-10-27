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