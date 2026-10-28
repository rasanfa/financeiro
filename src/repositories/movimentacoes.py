from __future__ import annotations

from src.repositories.base import BaseRepository


class MovimentacoesRepository(BaseRepository):

    table_name = "movimentacoes"

    def listar(self) -> list[dict]:

        response = (
            self.client
            .table(self.table_name)
            .select("*")
            .order("data", desc=True)
            .order("created_at", desc=True)
            .execute()
        )

        return response.data or []

    def listar_paginado(
        self,
        pagina: int,
        itens_por_pagina: int | None
    ) -> tuple[list[dict], int]:

        query = (
            self.client
            .table(self.table_name)
            .select("*", count="exact")
            .order("data", desc=True)
            .order("created_at", desc=True)
        )

        if itens_por_pagina is not None:
            inicio = (pagina - 1) * itens_por_pagina
            query = query.range(inicio, inicio + itens_por_pagina - 1)
            response = query.execute()

            return response.data or [], response.count or 0

        resposta = query.range(0, 499).execute()
        movimentacoes = resposta.data or []
        total = resposta.count or 0

        while len(movimentacoes) < total:
            inicio = len(movimentacoes)
            resposta = (
                self.client
                .table(self.table_name)
                .select("*")
                .order("data", desc=True)
                .order("created_at", desc=True)
                .range(inicio, inicio + 499)
                .execute()
            )
            pagina_atual = resposta.data or []

            if not pagina_atual:
                break

            movimentacoes.extend(pagina_atual)

        return movimentacoes, total

    def contar_ativas(self) -> int:

        response = (
            self.client
            .table(self.table_name)
            .select("id", count="exact")
            .eq("status_movimentacao", "ATIVA")
            .limit(1)
            .execute()
        )

        return response.count or 0

    def buscar(self, movimentacao_id: str) -> dict | None:

        response = (
            self.client
            .table(self.table_name)
            .select("*")
            .eq("id", movimentacao_id)
            .maybe_single()
            .execute()
        )

        return response.data

    def criar(
        self,
        dados: list[dict]
    ) -> list[dict]:

        response = (
            self.client
            .table(self.table_name)
            .insert(dados)
            .execute()
        )

        return response.data or []

    def atualizar(
        self,
        movimentacao_id: str,
        dados: dict
    ):

        (
            self.client
            .table(self.table_name)
            .update(dados)
            .eq("id", movimentacao_id)
            .execute()
        )

    def cancelar(
        self,
        movimentacao_id: str
    ):

        (
            self.client
            .table(self.table_name)
            .update(
                {
                    "status_movimentacao": "CANCELADA"
                }
            )
            .eq("id", movimentacao_id)
            .execute()
        )

    def listar_catalogos(
        self,
        usuario_id: str
    ) -> dict[str, list[dict]]:

        contas = (
            self.client
            .table("contas")
            .select("id,nome,apelido,ativo,usuario_id")
            .eq("usuario_id", usuario_id)
            .eq("ativo", True)
            .order("apelido")
            .execute()
        )

        cartoes = (
            self.client
            .table("cartoes")
            .select("id,nome,ativo,usuario_id")
            .eq("usuario_id", usuario_id)
            .eq("ativo", True)
            .order("nome")
            .execute()
        )

        categorias = (
            self.client
            .table("categorias")
            .select("id,nome,tipo_categoria,ativo,usuario_id")
            .eq("usuario_id", usuario_id)
            .eq("ativo", True)
            .order("nome")
            .execute()
        )

        subcategorias = (
            self.client
            .table("subcategorias")
            .select("id,nome,categoria_id,ativo")
            .eq("ativo", True)
            .order("nome")
            .execute()
        )

        beneficiarios = (
            self.client
            .table("beneficiarios")
            .select("id,nome,ativo,usuario_id")
            .eq("usuario_id", usuario_id)
            .eq("ativo", True)
            .order("nome")
            .execute()
        )

        formas_pagamento = (
            self.client
            .table("formas_pagamento")
            .select("id,codigo,nome,ativo")
            .eq("ativo", True)
            .order("nome")
            .execute()
        )

        return {
            "contas": contas.data or [],
            "cartoes": cartoes.data or [],
            "categorias": categorias.data or [],
            "subcategorias": subcategorias.data or [],
            "beneficiarios": beneficiarios.data or [],
            "formas_pagamento": formas_pagamento.data or []
        }
