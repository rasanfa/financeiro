from __future__ import annotations

import streamlit as st

from src.db.client import get_supabase_client
from src.services.contas import ContasService
from src.ui.components import render_total_card

USUARIO_ID = "17c95aaa-3ec6-4dc0-824b-7708fa280c5a"

service = ContasService()

if "conta_edicao" not in st.session_state:
    st.session_state.conta_edicao = None

if "mostrar_form_conta" not in st.session_state:
    st.session_state.mostrar_form_conta = False

st.title("🏦 Contas")

try:

    supabase = get_supabase_client()

    instituicoes = (
        supabase
        .table("instituicoes")
        .select("id,nome")
        .order("nome")
        .execute()
        .data
    )

    contas = service.listar()

    render_total_card(
        "Contas",
        len(contas)
    )

    if st.button("Nova Conta"):
        st.session_state.mostrar_form_conta = True

    if st.session_state.mostrar_form_conta:

        with st.expander(
            "Nova Conta",
            expanded=True
        ):

            with st.form("conta_form"):

                instituicao_nome = st.selectbox(
                    "Instituição",
                    [i["nome"] for i in instituicoes]
                )

                nome = st.text_input("Nome")

                apelido = st.text_input("Apelido")

                tipos = [
                    "CONTA_CORRENTE",
                    "CONTA_POUPANCA",
                    "CARTEIRA_DIGITAL",
                    "INVESTIMENTO",
                    "BENEFICIO_RESTRITO"
                ]

                tipo_conta = st.selectbox(
                    "Tipo de Conta",
                    tipos
                )

                saldo_texto = st.text_input(
                    "Saldo Inicial",
                    placeholder="1000,00"
                )

                salvar = st.form_submit_button(
                    "Salvar"
                )

                if salvar:

                    if not saldo_texto.strip():
                        saldo = 0.0
                    else:
                        saldo = float(
                            saldo_texto
                            .replace(".", "")
                            .replace(",", ".")
                        )

                    instituicao_id = next(
                        i["id"]
                        for i in instituicoes
                        if i["nome"] == instituicao_nome
                    )

                    service.criar(
                        usuario_id=USUARIO_ID,
                        instituicao_id=instituicao_id,
                        nome=nome,
                        apelido=apelido,
                        tipo_conta=tipo_conta,
                        saldo_inicial=saldo
                    )

                    st.session_state.mostrar_form_conta = False

                    st.rerun()

    st.divider()

    h1, h2, h3, h4, h5, h6 = st.columns(
        [2, 3, 2, 2, 2, 1]
    )

    h1.markdown("**Apelido**")
    h2.markdown("**Nome**")
    h3.markdown("**Instituição**")
    h4.markdown("**Tipo**")
    h5.markdown("**Saldo**")
    h6.markdown("**Ações**")

    for conta in contas:

        c1, c2, c3, c4, c5, c6 = st.columns(
            [2, 3, 2, 2, 2, 1]
        )

        c1.write(conta["apelido"])

        c2.write(conta["nome"])

        c3.write(
            conta["instituicoes"]["nome"]
        )

        c4.write(
            conta["tipo_conta"]
        )

        c5.write(
            f"R$ {float(conta['saldo_inicial']):,.2f}"
        )

        if c6.button(
            "Editar",
            key=f"editar_{conta['id']}"
        ):

            st.session_state.conta_edicao = conta

            st.rerun()

    if st.session_state.conta_edicao:

        conta = st.session_state.conta_edicao

        st.divider()

        st.subheader(
            f"Editar {conta['apelido']}"
        )

        nomes_instituicoes = [
            i["nome"]
            for i in instituicoes
        ]

        tipos = [
            "CONTA_CORRENTE",
            "CONTA_POUPANCA",
            "CARTEIRA_DIGITAL",
            "INVESTIMENTO",
            "BENEFICIO_RESTRITO"
        ]

        with st.form(
            "editar_conta"
        ):

            instituicao_nome = st.selectbox(
                "Instituição",
                nomes_instituicoes,
                index=nomes_instituicoes.index(
                    conta["instituicoes"]["nome"]
                )
            )

            editar_nome = st.text_input(
                "Nome",
                value=conta["nome"]
            )

            editar_apelido = st.text_input(
                "Apelido",
                value=conta["apelido"]
            )

            editar_tipo = st.selectbox(
                "Tipo de Conta",
                tipos,
                index=tipos.index(
                    conta["tipo_conta"]
                )
            )

            editar_saldo = st.text_input(
                "Saldo Inicial",
                value=str(
                    conta["saldo_inicial"]
                )
            )

            col1, col2 = st.columns(2)

            with col1:
                salvar_edicao = st.form_submit_button(
                    "Salvar Alterações"
                )

            with col2:
                inativar_conta = st.form_submit_button(
                    "Inativar Conta"
                )

            if salvar_edicao:

                if not editar_saldo.strip():
                    saldo = 0.0
                else:
                    saldo = float(
                        editar_saldo
                        .replace(".", "")
                        .replace(",", ".")
                    )

                instituicao_id = next(
                    i["id"]
                    for i in instituicoes
                    if i["nome"] == instituicao_nome
                )

                service.atualizar(
                    conta["id"],
                    instituicao_id,
                    editar_nome,
                    editar_apelido,
                    editar_tipo,
                    saldo
                )

                st.session_state.conta_edicao = None

                st.rerun()

            if inativar_conta:

                service.inativar(
                    conta["id"]
                )

                st.session_state.conta_edicao = None

                st.rerun()

except Exception as exc:

    st.error(
        f"Erro ao carregar contas: {exc}"
    )