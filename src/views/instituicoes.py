from __future__ import annotations

import pandas as pd
import streamlit as st

from src.services.instituicoes import InstituicoesService

USUARIO_ID = "17c95aaa-3ec6-4dc0-824b-7708fa280c5a"

service = InstituicoesService()

st.title("🏦 Instituições")
st.caption("Bancos, corretoras e carteiras digitais")

col1, col2 = st.columns([1, 5])

with col1:
    st.button("🔄 Atualizar")

try:

    instituicoes = service.listar()

    st.metric(
        "Total de Instituições",
        len(instituicoes)
    )

    # ==========================
    # FORMULÁRIO DE CADASTRO
    # ==========================

    st.divider()

    st.subheader("Nova Instituição")

    with st.form("instituicao_form"):

        nome = st.text_input(
            "Nome"
        )

        tipo = st.selectbox(
            "Tipo",
            [
                "BANCO",
                "CORRETORA",
                "CARTEIRA_DIGITAL"
            ]
        )

        salvar = st.form_submit_button(
            "💾 Salvar"
        )

        if salvar:

            try:

                service.criar(
                    usuario_id=USUARIO_ID,
                    nome=nome,
                    tipo=tipo
                )

                st.success(
                    "Instituição cadastrada com sucesso."
                )

                st.rerun()

            except Exception as exc:

                st.error(
                    f"Erro ao salvar: {exc}"
                )

    # ==========================
    # LISTAGEM
    # ==========================

    st.divider()

    st.subheader("Instituições Cadastradas")

    if not instituicoes:

        st.info(
            "Nenhuma instituição cadastrada."
        )

    else:

        df = pd.DataFrame(instituicoes)

        if "ativo" in df.columns:
            df["status"] = df["ativo"].apply(
                lambda x: "✅ Ativa" if x else "❌ Inativa"
            )

        if "created_at" in df.columns:
            df["criada_em"] = pd.to_datetime(
                df["created_at"]
            ).dt.strftime("%d/%m/%Y")

        colunas_exibir = []

        if "nome" in df.columns:
            colunas_exibir.append("nome")

        if "tipo" in df.columns:
            colunas_exibir.append("tipo")

        if "status" in df.columns:
            colunas_exibir.append("status")

        if "criada_em" in df.columns:
            colunas_exibir.append("criada_em")

        df = df[colunas_exibir]

        df.columns = [
            "Nome",
            "Tipo",
            "Status",
            "Criada em"
        ][: len(df.columns)]

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )

except Exception as exc:

    st.error(
        f"Erro ao carregar instituições: {exc}"
    )