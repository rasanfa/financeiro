from __future__ import annotations

from src.repositories.base import BaseRepository


class InstituicoesRepository(BaseRepository):

    table_name = "instituicoes"

    def listar(self) -> list[dict]:

        response = (
            self.client
            .table(self.table_name)
            .select("*")
            .order("nome")
            .execute()
        )

        return response.data or []

    def criar(self, dados: dict) -> dict:

        response = (
            self.client
            .table(self.table_name)
            .insert(dados)
            .execute()
        )

        return response.data[0]