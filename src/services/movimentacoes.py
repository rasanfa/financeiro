from __future__ import annotations

import calendar
from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from uuid import uuid4

from src.repositories.movimentacoes import MovimentacoesRepository
from src.services.base import BaseService

TIPOS_MOVIMENTO = (
    "RECEITA",
    "DESPESA_AVISTA",
    "DESPESA_PARCELADA",
    "TRANSFERENCIA_INTERNA"
)

TIPOS_COM_CATEGORIA = (
    "RECEITA",
    "DESPESA_AVISTA",
    "DESPESA_PARCELADA"
)


class MovimentacoesService(BaseService):

    def __init__(
        self,
        repository: MovimentacoesRepository | None = None
    ) -> None:

        movimentacoes_repository = (
            repository or MovimentacoesRepository()
        )

        super().__init__(movimentacoes_repository)

        self._movimentacoes_repository = movimentacoes_repository

    def listar(self) -> list[dict]:

        return self._movimentacoes_repository.listar()

    def listar_catalogos(
        self,
        usuario_id: str
    ) -> dict[str, list[dict]]:

        catalogos = self._movimentacoes_repository.listar_catalogos(
            usuario_id
        )

        contas = [
            conta
            for conta in catalogos["contas"]
            if conta.get("ativo") is True
            and conta.get("usuario_id") == usuario_id
        ]
        cartoes = [
            cartao
            for cartao in catalogos["cartoes"]
            if cartao.get("ativo") is True
            and cartao.get("usuario_id") == usuario_id
        ]
        categorias = [
            categoria
            for categoria in catalogos["categorias"]
            if categoria.get("ativo") is True
            and categoria.get("usuario_id") == usuario_id
        ]
        ids_categorias_ativas = {
            categoria["id"]
            for categoria in categorias
        }

        return {
            "contas": contas,
            "cartoes": cartoes,
            "categorias": categorias,
            "subcategorias": [
                subcategoria
                for subcategoria in catalogos["subcategorias"]
                if subcategoria.get("ativo") is True
                and subcategoria["categoria_id"] in ids_categorias_ativas
            ],
            "beneficiarios": [
                beneficiario
                for beneficiario in catalogos["beneficiarios"]
                if beneficiario.get("ativo") is True
                and beneficiario.get("usuario_id") == usuario_id
            ],
            "formas_pagamento": [
                forma
                for forma in catalogos["formas_pagamento"]
                if forma.get("ativo") is True
            ]
        }

    def criar(
        self,
        usuario_id: str,
        tipo_movimento: str,
        data: date,
        competencia: date | None,
        descricao: str,
        valor: int | float | str | Decimal,
        conta_id: str | None = None,
        conta_destino_id: str | None = None,
        cartao_id: str | None = None,
        forma_pagamento_id: str | None = None,
        categoria_id: str | None = None,
        subcategoria_id: str | None = None,
        beneficiario_id: str | None = None,
        total_parcelas: int = 1
    ) -> list[dict]:

        data = self._validar_data(data, "Data")
        competencia = self._resolver_competencia(
            tipo_movimento,
            data,
            competencia
        )

        dados = self._validar_e_montar_dados(
            usuario_id=usuario_id,
            tipo_movimento=tipo_movimento,
            data=data,
            competencia=competencia,
            descricao=descricao,
            valor=valor,
            conta_id=conta_id,
            conta_destino_id=conta_destino_id,
            cartao_id=cartao_id,
            forma_pagamento_id=forma_pagamento_id,
            categoria_id=categoria_id,
            subcategoria_id=subcategoria_id,
            beneficiario_id=beneficiario_id,
            total_parcelas=total_parcelas
        )

        grupo_transacao = str(uuid4())
        lancamentos = []

        for parcela in range(1, total_parcelas + 1):

            data_parcela = self._somar_meses(data, parcela - 1)
            competencia_parcela = self._somar_meses(
                competencia.replace(day=1),
                parcela - 1
            )

            if data_parcela < date(2020, 1, 1):
                raise ValueError(
                    "A data das movimentações deve ser a partir de 01/01/2020."
                )

            lancamentos.append(
                {
                    **dados,
                    "data": data_parcela.isoformat(),
                    "competencia": competencia_parcela.isoformat(),
                    "grupo_transacao": grupo_transacao,
                    "parcela_atual": parcela,
                    "total_parcelas": total_parcelas
                }
            )

        return self._movimentacoes_repository.criar(lancamentos)

    def atualizar(
        self,
        movimentacao_id: str,
        usuario_id: str,
        tipo_movimento: str,
        data: date,
        competencia: date | None,
        descricao: str,
        valor: int | float | str | Decimal,
        conta_id: str | None = None,
        conta_destino_id: str | None = None,
        cartao_id: str | None = None,
        forma_pagamento_id: str | None = None,
        categoria_id: str | None = None,
        subcategoria_id: str | None = None,
        beneficiario_id: str | None = None
    ) -> None:

        data = self._validar_data(data, "Data")
        competencia = self._resolver_competencia(
            tipo_movimento,
            data,
            competencia
        )

        existente = self._movimentacoes_repository.buscar(
            movimentacao_id
        )

        if not existente:
            raise ValueError(
                "Movimentação não encontrada."
            )

        if existente["status_movimentacao"] != "ATIVA":
            raise ValueError(
                "Movimentações canceladas não podem ser alteradas."
            )

        if existente["total_parcelas"] > 1:
            raise ValueError(
                "Movimentações parceladas não podem ser editadas individualmente."
            )

        dados = self._validar_e_montar_dados(
            usuario_id=usuario_id,
            tipo_movimento=tipo_movimento,
            data=data,
            competencia=competencia,
            descricao=descricao,
            valor=valor,
            conta_id=conta_id,
            conta_destino_id=conta_destino_id,
            cartao_id=cartao_id,
            forma_pagamento_id=forma_pagamento_id,
            categoria_id=categoria_id,
            subcategoria_id=subcategoria_id,
            beneficiario_id=beneficiario_id,
            total_parcelas=1
        )

        self._movimentacoes_repository.atualizar(
            movimentacao_id,
            {
                **dados,
                "data": data.isoformat(),
                "competencia": competencia.replace(day=1).isoformat(),
                "grupo_transacao": existente["grupo_transacao"],
                "parcela_atual": existente["parcela_atual"],
                "total_parcelas": existente["total_parcelas"]
            }
        )

    def cancelar(
        self,
        movimentacao_id: str
    ) -> None:

        existente = self._movimentacoes_repository.buscar(
            movimentacao_id
        )

        if not existente:
            raise ValueError(
                "Movimentação não encontrada."
            )

        if existente["status_movimentacao"] != "ATIVA":
            raise ValueError(
                "A movimentação já está cancelada."
            )

        self._movimentacoes_repository.cancelar(
            movimentacao_id
        )

    def _validar_e_montar_dados(
        self,
        usuario_id: str,
        tipo_movimento: str,
        data: date,
        competencia: date,
        descricao: str,
        valor: int | float | str | Decimal,
        conta_id: str | None,
        conta_destino_id: str | None,
        cartao_id: str | None,
        forma_pagamento_id: str | None,
        categoria_id: str | None,
        subcategoria_id: str | None,
        beneficiario_id: str | None,
        total_parcelas: int
    ) -> dict:

        if not usuario_id:
            raise ValueError(
                "Usuário é obrigatório."
            )

        if tipo_movimento not in TIPOS_MOVIMENTO:
            raise ValueError(
                "Tipo de movimentação inválido."
            )

        data = self._validar_data(data, "Data")
        competencia = self._validar_data(
            competencia,
            "Competência"
        )

        if data < date(2020, 1, 1):
            raise ValueError(
                "A data deve ser a partir de 01/01/2020."
            )

        descricao = descricao.strip()

        if not descricao:
            raise ValueError(
                "Descrição é obrigatória."
            )

        valor_decimal = self._validar_valor(valor)

        if (
            isinstance(total_parcelas, bool)
            or not isinstance(total_parcelas, int)
            or total_parcelas < 1
        ):
            raise ValueError(
                "O número de parcelas deve ser um inteiro maior que zero."
            )

        if (
            tipo_movimento != "DESPESA_PARCELADA"
            and total_parcelas != 1
        ):
            raise ValueError(
                "Somente despesas parceladas podem ter mais de uma parcela."
            )

        catalogos = self.listar_catalogos(usuario_id)
        contas = catalogos["contas"]
        cartoes = catalogos["cartoes"]
        categorias = catalogos["categorias"]
        subcategorias = catalogos["subcategorias"]
        beneficiarios = catalogos["beneficiarios"]
        formas_pagamento = catalogos["formas_pagamento"]

        ids_contas = {
            conta["id"]
            for conta in contas
        }
        ids_cartoes = {
            cartao["id"]
            for cartao in cartoes
        }
        categorias_por_id = {
            categoria["id"]: categoria
            for categoria in categorias
        }

        if tipo_movimento == "RECEITA":
            if beneficiario_id is not None:
                raise ValueError(
                    "Receitas não podem ser vinculadas a beneficiário."
                )

            self._exigir_referencia(
                conta_id,
                ids_contas,
                "Selecione uma conta ativa."
            )

        elif tipo_movimento == "DESPESA_AVISTA":
            if conta_id is None and beneficiario_id is None:
                raise ValueError(
                    "Selecione uma conta ou um beneficiário."
                )
            if conta_id is not None:
                self._exigir_referencia(
                    conta_id,
                    ids_contas,
                    "Selecione uma conta ativa."
                )

        if tipo_movimento in ("RECEITA", "DESPESA_AVISTA"):
            if cartao_id is not None:
                raise ValueError(
                    "Receitas e despesas à vista não podem usar cartão."
                )

            if conta_destino_id is not None:
                raise ValueError(
                    "Conta de destino só se aplica a transferências."
                )

        elif tipo_movimento == "DESPESA_PARCELADA":
            self._exigir_referencia(
                cartao_id,
                ids_cartoes,
                "Selecione um cartão de crédito ativo."
            )

            if conta_id is not None or conta_destino_id is not None:
                raise ValueError(
                    "Despesas parceladas devem usar cartão de crédito, não conta."
                )

        else:
            self._exigir_referencia(
                conta_id,
                ids_contas,
                "Selecione uma conta de origem ativa."
            )
            self._exigir_referencia(
                conta_destino_id,
                ids_contas,
                "Selecione uma conta de destino ativa."
            )

            if conta_id == conta_destino_id:
                raise ValueError(
                    "As contas de origem e destino devem ser diferentes."
                )

            if cartao_id is not None:
                raise ValueError(
                    "Transferências internas não podem usar cartão."
                )

        exige_categoria = tipo_movimento in TIPOS_COM_CATEGORIA

        if (
            exige_categoria
            and categoria_id is None
            and not (
                tipo_movimento == "DESPESA_AVISTA"
                and beneficiario_id is not None
            )
        ):
            raise ValueError(
                "Categoria é obrigatória, exceto em despesas à vista com beneficiário."
            )

        if categoria_id is None and subcategoria_id is not None:
            raise ValueError(
                "Selecione uma categoria antes de selecionar subcategoria."
            )

        if categoria_id is not None:
            categoria = categorias_por_id.get(categoria_id)

            if not categoria:
                raise ValueError(
                    "A categoria selecionada não existe ou está inativa."
                )

            tipo_categoria = categoria["tipo_categoria"]

            if (
                tipo_movimento == "RECEITA"
                and tipo_categoria == "DESPESA"
            ):
                raise ValueError(
                    "Categoria de despesa não pode ser usada em receita."
                )

            if (
                tipo_movimento in ("DESPESA_AVISTA", "DESPESA_PARCELADA")
                and tipo_categoria == "RECEITA"
            ):
                raise ValueError(
                    "Categoria de receita não pode ser usada em despesa."
                )

            if subcategoria_id is not None:
                subcategoria_valida = any(
                    subcategoria["id"] == subcategoria_id
                    and subcategoria["categoria_id"] == categoria_id
                    for subcategoria in subcategorias
                )

                if not subcategoria_valida:
                    raise ValueError(
                        "A subcategoria selecionada não pertence à categoria ou está inativa."
                    )

        if beneficiario_id is not None:
            self._exigir_referencia(
                beneficiario_id,
                {
                    beneficiario["id"]
                    for beneficiario in beneficiarios
                },
                "O beneficiário selecionado não existe ou está inativo."
            )

        if tipo_movimento == "DESPESA_PARCELADA":
            formas_credito = {
                forma["id"]
                for forma in formas_pagamento
                if forma.get("codigo") == "CREDITO"
            }
            self._exigir_referencia(
                forma_pagamento_id,
                formas_credito,
                "Despesa parcelada deve usar a forma de pagamento Crédito."
            )
        elif tipo_movimento in TIPOS_COM_CATEGORIA:
            self._exigir_referencia(
                forma_pagamento_id,
                {
                    forma["id"]
                    for forma in formas_pagamento
                },
                "Selecione uma forma de pagamento ativa."
            )
        elif forma_pagamento_id is not None:
            self._exigir_referencia(
                forma_pagamento_id,
                {
                    forma["id"]
                    for forma in formas_pagamento
                },
                "A forma de pagamento selecionada não existe ou está inativa."
            )

        return {
            "usuario_id": usuario_id,
            "tipo_movimento": tipo_movimento,
            "status_movimentacao": "ATIVA",
            "descricao": descricao,
            "valor": float(valor_decimal),
            "conta_id": conta_id,
            "conta_destino_id": conta_destino_id,
            "cartao_id": cartao_id,
            "forma_pagamento_id": forma_pagamento_id,
            "categoria_id": categoria_id,
            "subcategoria_id": subcategoria_id,
            "beneficiario_id": beneficiario_id
        }

    @classmethod
    def _resolver_competencia(
        cls,
        tipo_movimento: str,
        data_movimento: date,
        competencia: date | None
    ) -> date:

        if tipo_movimento == "DESPESA_PARCELADA":
            if competencia is None:
                raise ValueError(
                    "Competência é obrigatória para despesas parceladas."
                )

            return cls._validar_data(
                competencia,
                "Competência"
            )

        return data_movimento

    @staticmethod
    def _validar_data(valor: date, campo: str) -> date:

        if isinstance(valor, datetime):
            return valor.date()

        if not isinstance(valor, date):
            raise ValueError(
                f"{campo} deve ser uma data válida."
            )

        return valor

    @staticmethod
    def _validar_valor(valor: int | float | str | Decimal) -> Decimal:

        try:
            valor_decimal = Decimal(str(valor))
        except (InvalidOperation, ValueError):
            raise ValueError(
                "Valor deve ser um número válido."
            ) from None

        if not valor_decimal.is_finite() or valor_decimal <= 0:
            raise ValueError(
                "Valor deve ser maior que zero."
            )

        try:
            valor_decimal = valor_decimal.quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP
            )
        except InvalidOperation:
            raise ValueError(
                "Valor excede o limite permitido."
            ) from None

        if valor_decimal <= 0:
            raise ValueError(
                "Valor deve ser maior que zero."
            )

        if valor_decimal >= Decimal("1000000000000"):
            raise ValueError(
                "Valor excede o limite permitido."
            )

        return valor_decimal

    @staticmethod
    def _exigir_referencia(
        valor: str | None,
        ids_validos: set[str],
        mensagem: str
    ) -> None:

        if valor is None or valor not in ids_validos:
            raise ValueError(mensagem)

    @staticmethod
    def _somar_meses(data_base: date, meses: int) -> date:

        mes_total = data_base.month - 1 + meses
        ano = data_base.year + mes_total // 12
        mes = mes_total % 12 + 1

        if ano > 9999:
            raise ValueError(
                "As datas das parcelas excedem o intervalo permitido."
            )

        dia = min(
            data_base.day,
            calendar.monthrange(ano, mes)[1]
        )

        return date(ano, mes, dia)
