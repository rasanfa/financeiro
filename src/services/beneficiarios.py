from __future__ import annotations

from src.repositories.beneficiarios import BeneficiariosRepository
from src.services.base import BaseService


class BeneficiariosService(BaseService):

    def __init__(
        self,
        repository: BeneficiariosRepository | None = None,
    ) -> None:

        super().__init__(
            repository or BeneficiariosRepository()
        )

    def listar(self) -> list[dict]:

        return self.repository.listar()

    def criar(
        self,
        usuario_id: str,
        nome: str,
        tipo: str | None = None,
        observacao: str | None = None
    ) -> dict:

        nome = nome.strip()

        if not nome:
            raise ValueError(
                "Nome do beneficiário é obrigatório."
            )

        return self.repository.criar(
            {
                "usuario_id": usuario_id,
                "nome": nome,
                "tipo": tipo,
                "observacao": observacao,
                "ativo": True
            }
        )

    def atualizar(
        self,
        beneficiario_id: str,
        nome: str,
        tipo: str | None = None,
        observacao: str | None = None
    ):

        nome = nome.strip()

        if not nome:
            raise ValueError(
                "Nome do beneficiário é obrigatório."
            )

        self.repository.atualizar(
            beneficiario_id,
            {
                "nome": nome,
                "tipo": tipo,
                "observacao": observacao
            }
        )

    def inativar(
        self,
        beneficiario_id: str
    ):

        self.repository.inativar(
            beneficiario_id
        )
