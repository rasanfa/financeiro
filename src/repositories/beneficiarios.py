from src.repositories.base import BaseRepository


class BeneficiariosRepository(BaseRepository):

    table_name = "beneficiarios"

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
        beneficiario_id: str,
        dados: dict
    ):

        (
            self.client
            .table(self.table_name)
            .update(dados)
            .eq("id", beneficiario_id)
            .execute()
        )

    def inativar(
        self,
        beneficiario_id: str
    ):

        (
            self.client
            .table(self.table_name)
            .update(
                {
                    "ativo": False
                }
            )
            .eq("id", beneficiario_id)
            .execute()
        )
