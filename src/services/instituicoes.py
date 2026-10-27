from __future__ import annotations

from src.repositories.instituicoes import InstituicoesRepository
from src.services.base import BaseService


class InstituicoesService(BaseService):

    def __init__(
        self,
        repository: InstituicoesRepository | None = None
    ) -> None:

        super().__init__(
            repository or InstituicoesRepository()
        )

    def listar(self) -> list[dict]:
        return self.repository.listar()

    def criar(
        self,
        usuario_id: str,
        nome: str,
        tipo: str
    ) -> dict:

        nome = nome.strip()

        if not nome:
            raise ValueError(
                "Nome da instituição é obrigatório."
            )

        return self.repository.criar(
            {
                "usuario_id": usuario_id,
                "nome": nome,
                "tipo": tipo,
                "ativo": True
            }
        )