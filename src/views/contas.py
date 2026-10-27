from __future__ import annotations

import pandas as pd
import streamlit as st

from src.db.client import get_supabase_client
from src.services.contas import ContasService

USUARIO_ID = "17c95aaa-3ec6-4dc0-824b-7708fa280c5a"

service = ContasService()

st.title("🏦 Contas")
st.caption("Contas identificadas pelo apelido")

try:

    supabase = get_supabase_client()

    instituicoes = (
        supabase
        .table("instituicoes")
        .select("id,nome")
        .eq("ativo", True)
        .order("nome")
        .execute()
        .data
    )

    st.metric(
        "Total de Contas",
        len(service.listar())
    )

    st.divider()

    st.subheader("Nova Conta")

    with st.form("conta_form"):

        if instituicoes:

            instituicao_nome = st.selectbox(
                "Instituição",
                [i["nome"] for i in instituicoes]
            )

        else:

            instituicao_nome = None

            st.warning(
                "Cadastre uma instituição primeiro."
            )

        nome = st.text_input(
            "Nome"
        )

        apelido = st.text_input(
            "Apelido"
        )

        tipo_conta = st.selectbox(
            "Tipo de Conta",
            [
                "CONTA_CORRENTE",
                "CONTA_POUPANCA",
                "CARTEIRA_DIGITAL",
                "INVESTIMENTO",
                "BENEFICIO_RESTRITO"
            ]
        )

        saldo_inicial = st.number_input(
            "Saldo Inicial",
            value=0.0,
            step=100.0
        )

        salvar = st.form_submit_button(
            "💾 Salvar"
        )

        if salvar:

            try:

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
                    saldo_inicial=saldo_inicial
                )

                st.success(
                    "Conta cadastrada."
                )

                st.rerun()

            except Exception as exc:

                st.error(
                    f"Erro ao salvar: {exc}"
                )

    st.divider()

    st.subheader(
        "Contas Cadastradas"
    )

    contas = service.listar()

    if not contas:

        st.info(
            "Nenhuma conta cadastrada."
        )

    else:

        linhas = []

        for conta in contas:

            linhas.append(
                {
                    "Apelido": conta["apelido"],
                    "Nome": conta["nome"],
                    "Instituição": conta["instituicoes"]["nome"],
                    "Tipo": conta["tipo_conta"],
                    "Saldo Inicial": conta["saldo_inicial"],
                    "Status": (
                        "✅ Ativa"
                        if conta["ativo"]
                        else "❌ Inativa"
                    )
                }
            )

        st.dataframe(
            pd.DataFrame(linhas),
            use_container_width=True,
            hide_index=True
        )

except Exception as exc:

    st.error(
        f"Erro ao carregar contas: {exc}"
    )