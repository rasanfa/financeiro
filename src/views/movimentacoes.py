from __future__ import annotations

from datetime import date

import streamlit as st

from src.services.movimentacoes import (
    TIPOS_MOVIMENTO,
    MovimentacoesService,
)
from src.ui.components import render_total_card

USUARIO_ID = "17c95aaa-3ec6-4dc0-824b-7708fa280c5a"

ROTULOS_TIPO = {
    "RECEITA": "Receita",
    "DESPESA_AVISTA": "Despesa à vista",
    "DESPESA_PARCELADA": "Despesa parcelada",
    "TRANSFERENCIA_INTERNA": "Transferência interna"
}

service = MovimentacoesService()

if "mostrar_form_movimentacao" not in st.session_state:
    st.session_state.mostrar_form_movimentacao = False

if "movimentacao_edicao" not in st.session_state:
    st.session_state.movimentacao_edicao = None


def _data(valor: date | str | None) -> date:

    if isinstance(valor, date):
        return valor

    if valor:
        return date.fromisoformat(valor[:10])

    return date.today()


def _rotulo_opcao(
    identificador: str | None,
    rotulos: dict[str, str],
    rotulo_vazio: str
) -> str:

    if identificador is None:
        return rotulo_vazio

    return rotulos.get(
        identificador,
        "Cadastro não disponível"
    )


def _render_formulario(
    catalogos: dict[str, list[dict]],
    movimentacao: dict | None = None
) -> None:

    editando = movimentacao is not None
    sufixo = movimentacao["id"] if editando else "nova"
    prefixo = "editar" if editando else "nova"
    chave_tipo = f"tipo_movimento_{prefixo}_{sufixo}"

    if editando and chave_tipo not in st.session_state:
        st.session_state[chave_tipo] = movimentacao["tipo_movimento"]

    if not editando:
        st.subheader("Nova Movimentação")

    tipo_movimento = st.selectbox(
        "Tipo de movimentação",
        TIPOS_MOVIMENTO,
        format_func=lambda tipo: ROTULOS_TIPO[tipo],
        key=chave_tipo
    )

    categorias = catalogos["categorias"]

    if tipo_movimento == "RECEITA":
        categorias_validas = [
            categoria
            for categoria in categorias
            if categoria["tipo_categoria"] in ("RECEITA", "AMBOS")
        ]
    elif tipo_movimento in ("DESPESA_AVISTA", "DESPESA_PARCELADA"):
        categorias_validas = [
            categoria
            for categoria in categorias
            if categoria["tipo_categoria"] in ("DESPESA", "AMBOS")
        ]
    else:
        categorias_validas = categorias

    nomes_categorias = {
        categoria["id"]: categoria["nome"]
        for categoria in categorias_validas
    }

    chave_categoria = f"categoria_{prefixo}_{sufixo}"

    if (
        st.session_state.get(chave_categoria) is not None
        and st.session_state[chave_categoria] not in nomes_categorias
    ):
        st.session_state[chave_categoria] = None

    contas = catalogos["contas"]
    nomes_contas = {
        conta["id"]: (
            f"{conta['apelido']} — {conta['nome']}"
            if conta.get("apelido")
            else conta["nome"]
        )
        for conta in contas
    }
    cartoes = catalogos["cartoes"]
    nomes_cartoes = {
        cartao["id"]: cartao["nome"]
        for cartao in cartoes
    }
    beneficiarios = catalogos["beneficiarios"]
    nomes_beneficiarios = {
        beneficiario["id"]: beneficiario["nome"]
        for beneficiario in beneficiarios
    }
    formas_pagamento = catalogos["formas_pagamento"]
    nomes_formas_pagamento = {
        forma["id"]: forma["nome"]
        for forma in formas_pagamento
    }

    if editando:
        st.subheader(f"Editar {movimentacao['descricao']}")

    coluna_categoria, coluna_subcategoria = st.columns(2)

    with coluna_categoria:
        categoria_id = st.selectbox(
            "Categoria" if tipo_movimento != "TRANSFERENCIA_INTERNA"
            else "Categoria (opcional)",
            [None, *nomes_categorias],
            format_func=lambda valor: _rotulo_opcao(
                valor,
                nomes_categorias,
                "Sem categoria"
            ),
            key=chave_categoria
        )

    subcategorias_validas = [
        subcategoria
        for subcategoria in catalogos["subcategorias"]
        if categoria_id is not None
        and subcategoria["categoria_id"] == categoria_id
    ]
    nomes_subcategorias = {
        subcategoria["id"]: subcategoria["nome"]
        for subcategoria in subcategorias_validas
    }
    chave_subcategoria = f"subcategoria_{prefixo}_{sufixo}"

    if (
        st.session_state.get(chave_subcategoria) is not None
        and st.session_state[chave_subcategoria] not in nomes_subcategorias
    ):
        st.session_state[chave_subcategoria] = None

    with coluna_subcategoria:
        subcategoria_id = st.selectbox(
            "Subcategoria (opcional)",
            [None, *nomes_subcategorias],
            format_func=lambda valor: _rotulo_opcao(
                valor,
                nomes_subcategorias,
                "Sem subcategoria"
            ),
            key=chave_subcategoria
        )

    with st.form(f"form_movimentacao_{prefixo}_{sufixo}"):

        descricao = st.text_input(
            "Descrição",
            value=movimentacao["descricao"] if editando else ""
        )

        data_movimento = st.date_input(
            "Data",
            value=_data(movimentacao.get("data") if editando else None)
        )

        competencia = None

        if tipo_movimento == "DESPESA_PARCELADA":
            competencia = st.date_input(
                "Competência",
                value=_data(
                    movimentacao.get("competencia")
                    if editando
                    else date.today()
                ),
                help="Independente da data do lançamento; será considerada pelo mês."
            )

        valor = st.number_input(
            "Valor positivo",
            min_value=0.01,
            value=(
                float(movimentacao["valor"])
                if editando
                else 0.01
            ),
            step=0.01,
            format="%.2f"
        )

        if tipo_movimento == "TRANSFERENCIA_INTERNA":

            col_origem, col_destino = st.columns(2)

            with col_origem:
                conta_id = st.selectbox(
                    "Conta de origem",
                    [None, *nomes_contas],
                    index=(
                        [None, *nomes_contas].index(movimentacao["conta_id"])
                        if editando
                        and movimentacao.get("conta_id") in nomes_contas
                        else 0
                    ),
                    format_func=lambda valor: _rotulo_opcao(
                        valor,
                        nomes_contas,
                        "Selecione uma conta"
                    )
                )

            with col_destino:
                conta_destino_id = st.selectbox(
                    "Conta de destino",
                    [None, *nomes_contas],
                    index=(
                        [None, *nomes_contas].index(
                            movimentacao["conta_destino_id"]
                        )
                        if editando
                        and movimentacao.get("conta_destino_id") in nomes_contas
                        else 0
                    ),
                    format_func=lambda valor: _rotulo_opcao(
                        valor,
                        nomes_contas,
                        "Selecione uma conta"
                    )
                )

            cartao_id = None

        elif tipo_movimento == "DESPESA_PARCELADA":

            cartao_id = st.selectbox(
                "Cartão",
                [None, *nomes_cartoes],
                index=(
                    [None, *nomes_cartoes].index(movimentacao["cartao_id"])
                    if editando
                    and movimentacao.get("cartao_id") in nomes_cartoes
                    else 0
                ),
                format_func=lambda valor: _rotulo_opcao(
                    valor,
                    nomes_cartoes,
                    "Selecione um cartão"
                )
            )
            conta_id = None
            conta_destino_id = None

        else:

            conta_id = st.selectbox(
                "Conta",
                [None, *nomes_contas],
                index=(
                    [None, *nomes_contas].index(movimentacao["conta_id"])
                    if editando
                    and movimentacao.get("conta_id") in nomes_contas
                    else 0
                ),
                format_func=lambda valor: _rotulo_opcao(
                    valor,
                    nomes_contas,
                    "Selecione uma conta"
                )
            )
            conta_destino_id = None
            cartao_id = None

        forma_obrigatoria = tipo_movimento in (
            "RECEITA",
            "DESPESA_AVISTA",
            "DESPESA_PARCELADA"
        )
        if tipo_movimento == "DESPESA_PARCELADA":
            formas_credito = {
                forma["id"]: forma["nome"]
                for forma in formas_pagamento
                if forma.get("codigo") == "CREDITO"
            }

            if formas_credito:
                forma_pagamento_id = st.selectbox(
                    "Forma de pagamento",
                    list(formas_credito),
                    index=(
                        list(formas_credito).index(
                            movimentacao["forma_pagamento_id"]
                        )
                        if editando
                        and movimentacao.get("forma_pagamento_id")
                        in formas_credito
                        else 0
                    ),
                    format_func=lambda valor: formas_credito[valor]
                )
            else:
                forma_pagamento_id = None
                st.warning(
                    "A forma de pagamento Crédito não está cadastrada como ativa."
                )
        else:
            forma_pagamento_id = st.selectbox(
                "Forma de pagamento" if forma_obrigatoria
                else "Forma de pagamento (opcional)",
                [None, *nomes_formas_pagamento],
                index=(
                    [None, *nomes_formas_pagamento].index(
                        movimentacao["forma_pagamento_id"]
                    )
                    if editando
                    and movimentacao.get("forma_pagamento_id")
                    in nomes_formas_pagamento
                    else 0
                ),
                format_func=lambda valor: _rotulo_opcao(
                    valor,
                    nomes_formas_pagamento,
                    "Selecione uma forma de pagamento"
                    if forma_obrigatoria
                    else "Não informada"
                )
            )

        beneficiario_id = st.selectbox(
            "Beneficiário (opcional)",
            [None, *nomes_beneficiarios],
            index=(
                [None, *nomes_beneficiarios].index(
                    movimentacao["beneficiario_id"]
                )
                if editando
                and movimentacao.get("beneficiario_id")
                in nomes_beneficiarios
                else 0
            ),
            format_func=lambda valor: _rotulo_opcao(
                valor,
                nomes_beneficiarios,
                "Não informado"
            )
        )

        total_parcelas = 1

        if tipo_movimento == "DESPESA_PARCELADA":
            total_parcelas = st.number_input(
                "Número de parcelas",
                min_value=1,
                value=(
                    movimentacao["total_parcelas"]
                    if editando
                    else 1
                ),
                step=1,
                disabled=editando
            )
            st.caption(
                "O valor informado é o valor de cada parcela. "
                "Data e competência avançam um mês por parcela."
            )

        col_salvar, col_cancelar = st.columns(2)

        with col_salvar:
            salvar = st.form_submit_button(
                "Salvar Alterações" if editando else "Salvar Movimentação"
            )

        with col_cancelar:
            cancelar = (
                st.form_submit_button("Cancelar Movimentação")
                if editando
                else False
            )

        if salvar:

            argumentos = {
                "usuario_id": USUARIO_ID,
                "tipo_movimento": tipo_movimento,
                "data": data_movimento,
                "competencia": competencia,
                "descricao": descricao,
                "valor": valor,
                "conta_id": conta_id,
                "conta_destino_id": conta_destino_id,
                "cartao_id": cartao_id,
                "forma_pagamento_id": forma_pagamento_id,
                "categoria_id": categoria_id,
                "subcategoria_id": subcategoria_id,
                "beneficiario_id": beneficiario_id
            }

            try:
                if editando:
                    service.atualizar(
                        movimentacao["id"],
                        **argumentos
                    )
                    st.session_state.movimentacao_edicao = None
                else:
                    service.criar(
                        **argumentos,
                        total_parcelas=int(total_parcelas)
                    )
                    st.session_state.mostrar_form_movimentacao = False

                st.rerun()

            except Exception as exc:
                st.error(
                    f"Não foi possível salvar a movimentação: {exc}"
                )

        if cancelar and editando:

            try:
                service.cancelar(movimentacao["id"])
                st.session_state.movimentacao_edicao = None
                st.rerun()

            except Exception as exc:
                st.error(
                    f"Não foi possível cancelar a movimentação: {exc}"
                )


st.title("📒 Movimentações")

try:

    catalogos = service.listar_catalogos(USUARIO_ID)
    movimentacoes = service.listar()

    total_ativas = sum(
        1
        for movimentacao in movimentacoes
        if movimentacao["status_movimentacao"] == "ATIVA"
    )

    render_total_card(
        "Movimentações ativas",
        total_ativas
    )

    if st.button("Nova Movimentação"):
        st.session_state.mostrar_form_movimentacao = True
        st.session_state.movimentacao_edicao = None

    if st.session_state.mostrar_form_movimentacao:
        _render_formulario(catalogos)

    nomes_contas = {
        conta["id"]: (
            f"{conta['apelido']} — {conta['nome']}"
            if conta.get("apelido")
            else conta["nome"]
        )
        for conta in catalogos["contas"]
    }
    nomes_cartoes = {
        cartao["id"]: cartao["nome"]
        for cartao in catalogos["cartoes"]
    }
    nomes_categorias = {
        categoria["id"]: categoria["nome"]
        for categoria in catalogos["categorias"]
    }
    nomes_beneficiarios = {
        beneficiario["id"]: beneficiario["nome"]
        for beneficiario in catalogos["beneficiarios"]
    }

    st.divider()

    colunas_titulo = st.columns(
        [1.1, 1.1, 2.2, 1.5, 1.2, 1.8, 1.1, 1.1, 1.5]
    )
    titulos = (
        "Data",
        "Competência",
        "Descrição",
        "Tipo",
        "Valor",
        "Conta / Cartão",
        "Parcelas",
        "Status",
        "Ações"
    )

    for coluna, titulo in zip(colunas_titulo, titulos):
        coluna.markdown(f"**{titulo}**")

    for movimentacao in movimentacoes:

        colunas = st.columns(
            [1.1, 1.1, 2.2, 1.5, 1.2, 1.8, 1.1, 1.1, 1.5]
        )
        conta_nome = nomes_contas.get(
            movimentacao.get("conta_id"),
            ""
        )
        destino_nome = nomes_contas.get(
            movimentacao.get("conta_destino_id"),
            ""
        )
        cartao_nome = nomes_cartoes.get(
            movimentacao.get("cartao_id"),
            ""
        )
        meio = cartao_nome or conta_nome

        if destino_nome:
            meio = f"{conta_nome} → {destino_nome}"

        colunas[0].write(_data(movimentacao["data"]).strftime("%d/%m/%Y"))
        colunas[1].write(
            _data(movimentacao["competencia"]).strftime("%m/%Y")
        )
        colunas[2].write(movimentacao["descricao"])
        detalhes = []
        categoria_nome = nomes_categorias.get(
            movimentacao.get("categoria_id")
        )
        beneficiario_nome = nomes_beneficiarios.get(
            movimentacao.get("beneficiario_id")
        )

        if categoria_nome:
            detalhes.append(categoria_nome)

        if beneficiario_nome:
            detalhes.append(beneficiario_nome)

        if detalhes:
            colunas[2].caption(" · ".join(detalhes))

        colunas[3].write(
            ROTULOS_TIPO.get(
                movimentacao["tipo_movimento"],
                movimentacao["tipo_movimento"]
            )
        )
        colunas[4].write(
            f"R$ {float(movimentacao['valor']):,.2f}"
        )
        colunas[5].write(meio or "—")
        colunas[6].write(
            f"{movimentacao['parcela_atual']}/"
            f"{movimentacao['total_parcelas']}"
        )
        colunas[7].write(movimentacao["status_movimentacao"])

        with colunas[8]:
            acao_editar, acao_cancelar = st.columns(2)

            pode_editar = (
                movimentacao["status_movimentacao"] == "ATIVA"
                and movimentacao["total_parcelas"] == 1
            )

            if acao_editar.button(
                "Editar",
                key=f"editar_movimentacao_{movimentacao['id']}",
                disabled=not pode_editar
            ):

                st.session_state.movimentacao_edicao = movimentacao
                chave_tipo = f"tipo_movimento_editar_{movimentacao['id']}"
                st.session_state[chave_tipo] = movimentacao["tipo_movimento"]
                st.session_state[
                    f"categoria_editar_{movimentacao['id']}"
                ] = movimentacao.get("categoria_id")
                st.session_state[
                    f"subcategoria_editar_{movimentacao['id']}"
                ] = movimentacao.get("subcategoria_id")

                st.rerun()

            if acao_cancelar.button(
                "Cancelar",
                key=f"cancelar_movimentacao_{movimentacao['id']}",
                disabled=movimentacao["status_movimentacao"] != "ATIVA"
            ):

                service.cancelar(movimentacao["id"])
                st.rerun()

    if st.session_state.movimentacao_edicao:
        _render_formulario(
            catalogos,
            st.session_state.movimentacao_edicao
        )

except Exception as exc:

    st.error(
        f"Erro ao carregar movimentações: {exc}"
    )
