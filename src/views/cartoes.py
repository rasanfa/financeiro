from __future__ import annotations

import streamlit as st

from src.db.client import get_supabase_client
from src.services.cartoes import CartoesService
from src.ui.components import render_total_card

USUARIO_ID = "17c95aaa-3ec6-4dc0-824b-7708fa280c5a"

service = CartoesService()

if "cartao_edicao" not in st.session_state:
    st.session_state.cartao_edicao = None

if "mostrar_form_cartao" not in st.session_state:
    st.session_state.mostrar_form_cartao = False

st.title("💳 Cartões")

try:

    supabase = get_supabase_client()

    instituicoes = (
        supabase
        .table("instituicoes")
        .select("id,nome")
        .order("nome")
        .execute()
        .data
        or []
    )

    contas = (
        supabase
        .table("contas")
        .select("id,nome")
        .order("nome")
        .execute()
        .data
        or []
    )

    cartoes = service.listar()

    render_total_card(
        "Cartões",
        len(cartoes)
    )

    if st.button("Novo Cartão"):
        st.session_state.mostrar_form_cartao = True

    if st.session_state.mostrar_form_cartao:

        with st.expander(
            "Novo Cartão",
            expanded=True
        ):

            with st.form("cartao_form"):

                nome = st.text_input("Nome")

                instituicao_nome = st.selectbox(
                    "Instituição",
                    ["Não informada", *[i["nome"] for i in instituicoes]]
                )

                conta_nome = st.selectbox(
                    "Conta para pagamento",
                    ["Não informada", *[c["nome"] for c in contas]]
                )

                limite_texto = st.text_input(
                    "Limite",
                    placeholder="1000,00"
                )

                dia_fechamento_texto = st.text_input(
                    "Dia de fechamento",
                    placeholder="1 a 31"
                )

                dia_vencimento_texto = st.text_input(
                    "Dia de vencimento",
                    placeholder="1 a 31"
                )

                salvar = st.form_submit_button("Salvar")

                if salvar:

                    limite = (
                        float(
                            limite_texto
                            .replace(".", "")
                            .replace(",", ".")
                        )
                        if limite_texto.strip()
                        else None
                    )

                    dia_fechamento = (
                        int(dia_fechamento_texto)
                        if dia_fechamento_texto.strip()
                        else None
                    )

                    dia_vencimento = (
                        int(dia_vencimento_texto)
                        if dia_vencimento_texto.strip()
                        else None
                    )

                    instituicao_id = next(
                        (
                            i["id"]
                            for i in instituicoes
                            if i["nome"] == instituicao_nome
                        ),
                        None
                    )

                    conta_id = next(
                        (
                            c["id"]
                            for c in contas
                            if c["nome"] == conta_nome
                        ),
                        None
                    )

                    service.criar(
                        usuario_id=USUARIO_ID,
                        nome=nome,
                        instituicao_id=instituicao_id,
                        conta_id=conta_id,
                        limite=limite,
                        dia_fechamento=dia_fechamento,
                        dia_vencimento=dia_vencimento
                    )

                    st.session_state.mostrar_form_cartao = False

                    st.rerun()

    st.divider()

    cabecalhos = st.columns([3, 2, 2, 1, 1, 1])
    cabecalhos[0].markdown("**Nome**")
    cabecalhos[1].markdown("**Instituição**")
    cabecalhos[2].markdown("**Limite**")
    cabecalhos[3].markdown("**Fechamento**")
    cabecalhos[4].markdown("**Vencimento**")
    cabecalhos[5].markdown("**Ações**")

    instituicoes_por_id = {
        instituicao["id"]: instituicao["nome"]
        for instituicao in instituicoes
    }

    for cartao in cartoes:

        colunas = st.columns([3, 2, 2, 1, 1, 1])

        colunas[0].write(cartao["nome"])
        colunas[1].write(
            instituicoes_por_id.get(
                cartao.get("instituicao_id"),
                "—"
            )
        )
        colunas[2].write(
            f"R$ {float(cartao['limite']):,.2f}"
            if cartao.get("limite") is not None
            else "—"
        )
        colunas[3].write(cartao.get("dia_fechamento") or "—")
        colunas[4].write(cartao.get("dia_vencimento") or "—")

        if colunas[5].button(
            "Editar",
            key=f"editar_{cartao['id']}"
        ):

            st.session_state.cartao_edicao = cartao

            st.rerun()

    if st.session_state.cartao_edicao:

        cartao = st.session_state.cartao_edicao

        st.divider()

        st.subheader(
            f"Editar {cartao['nome']}"
        )

        nomes_instituicoes = [
            "Não informada",
            *[i["nome"] for i in instituicoes]
        ]
        nomes_contas = [
            "Não informada",
            *[c["nome"] for c in contas]
        ]
        instituicao_atual = instituicoes_por_id.get(
            cartao.get("instituicao_id")
        )
        conta_atual = next(
            (
                conta["nome"]
                for conta in contas
                if conta["id"] == cartao.get("conta_id")
            ),
            None
        )

        with st.form("editar_cartao"):

            editar_nome = st.text_input(
                "Nome",
                value=cartao["nome"]
            )

            editar_instituicao = st.selectbox(
                "Instituição",
                nomes_instituicoes,
                index=(
                    nomes_instituicoes.index(instituicao_atual)
                    if instituicao_atual in nomes_instituicoes
                    else 0
                )
            )

            editar_conta = st.selectbox(
                "Conta para pagamento",
                nomes_contas,
                index=(
                    nomes_contas.index(conta_atual)
                    if conta_atual in nomes_contas
                    else 0
                )
            )

            editar_limite = st.text_input(
                "Limite",
                value=(
                    str(cartao["limite"])
                    if cartao.get("limite") is not None
                    else ""
                ),
                placeholder="1000,00"
            )

            editar_dia_fechamento = st.text_input(
                "Dia de fechamento",
                value=(
                    str(cartao["dia_fechamento"])
                    if cartao.get("dia_fechamento") is not None
                    else ""
                ),
                placeholder="1 a 31"
            )

            editar_dia_vencimento = st.text_input(
                "Dia de vencimento",
                value=(
                    str(cartao["dia_vencimento"])
                    if cartao.get("dia_vencimento") is not None
                    else ""
                ),
                placeholder="1 a 31"
            )

            col1, col2 = st.columns(2)

            with col1:
                salvar_edicao = st.form_submit_button(
                    "Salvar Alterações"
                )

            with col2:
                inativar_cartao = st.form_submit_button(
                    "Inativar Cartão"
                )

            if salvar_edicao:

                limite = (
                    float(
                        editar_limite
                        .replace(".", "")
                        .replace(",", ".")
                    )
                    if editar_limite.strip()
                    else None
                )

                dia_fechamento = (
                    int(editar_dia_fechamento)
                    if editar_dia_fechamento.strip()
                    else None
                )

                dia_vencimento = (
                    int(editar_dia_vencimento)
                    if editar_dia_vencimento.strip()
                    else None
                )

                instituicao_id = next(
                    (
                        i["id"]
                        for i in instituicoes
                        if i["nome"] == editar_instituicao
                    ),
                    None
                )

                conta_id = next(
                    (
                        c["id"]
                        for c in contas
                        if c["nome"] == editar_conta
                    ),
                    None
                )

                service.atualizar(
                    cartao["id"],
                    editar_nome,
                    instituicao_id=instituicao_id,
                    conta_id=conta_id,
                    limite=limite,
                    dia_fechamento=dia_fechamento,
                    dia_vencimento=dia_vencimento
                )

                st.session_state.cartao_edicao = None

                st.rerun()

            if inativar_cartao:

                service.inativar(
                    cartao["id"]
                )

                st.session_state.cartao_edicao = None

                st.rerun()

except Exception as exc:

    st.error(
        f"Erro ao carregar cartões: {exc}"
    )
