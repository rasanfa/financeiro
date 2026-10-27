from __future__ import annotations

from src.repositories.contas import ContasRepository
from src.services.base import BaseService


class ContasService(BaseService):

    def __init__(
        self,
        repository: ContasRepository | None = None
    ) -> None:

        super().__init__(
            repository or ContasRepository()
        )

    def listar(self) -> list[dict]:

        return self.repository.listar()

    def criar(
        self,
        usuario_id: str,
        instituicao_id: str,
        nome: str,
        apelido: str,
        tipo_conta: str,
        saldo_inicial: float
    ):

        nome = nome.strip()
        apelido = apelido.strip()

        if not nome:
            raise ValueError(
                "Nome é obrigatório."
            )

        if not apelido:
            raise ValueError(
                "Apelido é obrigatório."
            )

        return self.repository.criar(
            {
                "usuario_id": usuario_id,
                "instituicao_id": instituicao_id,
                "nome": nome,
                "apelido": apelido,
                "tipo_conta": tipo_conta,
                "saldo_inicial": saldo_inicial,
                "ativo": True
            }
        )

    def atualizar(
        self,
        conta_id: str,
        instituicao_id: str,
        nome: str,
        apelido: str,
        tipo_conta: str,
        saldo_inicial: float
    ):

        self.repository.atualizar(
            conta_id,
            {
                "instituicao_id": instituicao_id,
                "nome": nome,
                "apelido": apelido,
                "tipo_conta": tipo_conta,
                "saldo_inicial": saldo_inicial
            }
        )

    def inativar(
        self,
        conta_id: str
    ):

        self.repository.inativar(
            conta_id
        )