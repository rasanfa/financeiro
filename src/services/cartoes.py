from __future__ import annotations

from src.repositories.cartoes import CartoesRepository
from src.services.base import BaseService


class CartoesService(BaseService):

    def __init__(
        self,
        repository: CartoesRepository | None = None
    ) -> None:

        super().__init__(
            repository or CartoesRepository()
        )

    def listar(self) -> list[dict]:

        return self.repository.listar()

    def criar(
        self,
        usuario_id: str,
        nome: str,
        instituicao_id: str | None = None,
        conta_id: str | None = None,
        limite: float | None = None,
        dia_fechamento: int | None = None,
        dia_vencimento: int | None = None
    ) -> dict:

        nome = nome.strip()

        if not nome:
            raise ValueError(
                "Nome do cartão é obrigatório."
            )

        return self.repository.criar(
            {
                "usuario_id": usuario_id,
                "instituicao_id": instituicao_id,
                "conta_id": conta_id,
                "nome": nome,
                "limite": limite,
                "dia_fechamento": dia_fechamento,
                "dia_vencimento": dia_vencimento,
                "ativo": True
            }
        )

    def atualizar(
        self,
        cartao_id: str,
        nome: str,
        instituicao_id: str | None = None,
        conta_id: str | None = None,
        limite: float | None = None,
        dia_fechamento: int | None = None,
        dia_vencimento: int | None = None
    ):

        nome = nome.strip()

        if not nome:
            raise ValueError(
                "Nome do cartão é obrigatório."
            )

        self.repository.atualizar(
            cartao_id,
            {
                "instituicao_id": instituicao_id,
                "conta_id": conta_id,
                "nome": nome,
                "limite": limite,
                "dia_fechamento": dia_fechamento,
                "dia_vencimento": dia_vencimento
            }
        )

    def inativar(
        self,
        cartao_id: str
    ):

        self.repository.inativar(
            cartao_id
        )
