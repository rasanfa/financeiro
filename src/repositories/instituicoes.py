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

    def inativar(self, instituicao_id: str):

        (
            self.client
            .table(self.table_name)
            .update(
                {
                    "ativo": False
                }
            )
            .eq("id", instituicao_id)
            .execute()
        )

    def atualizar(self, instituicao_id: str, dados: dict):

        (
            self.client
            .table(self.table_name)
            .update(dados)
            .eq("id", instituicao_id)
            .execute()
        )

    def reativar(
        self,
        instituicao_id: str
    ):

        (
            self.client
            .table(self.table_name)
            .update(
                {
                    "ativo": True
                }
            )
            .eq("id", instituicao_id)
            .execute()
        )