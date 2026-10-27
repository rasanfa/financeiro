from __future__ import annotations

import pandas as pd
import streamlit as st

from src.services.instituicoes import InstituicoesService

USUARIO_ID = "17c95aaa-3ec6-4dc0-824b-7708fa280c5a"

service = InstituicoesService()

st.title("🏦 Instituições")
st.caption("Bancos, corretoras e carteiras digitais")

with st.container():

    if st.button("🔄 Atualizar"):
        st.rerun()

try:

    instituicoes = service.listar()

    st.metric(
        "Total de Instituições",
        len(instituicoes)
    )

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

    st.divider()

    st.subheader(
        "Instituições Cadastradas"
    )

    if not instituicoes:

        st.info(
            "Nenhuma instituição cadastrada."
        )

    else:

        for item in instituicoes:

            col1, col2, col3, col4 = st.columns(
                [4, 3, 2, 2]
            )

            with col1:
                st.write(
                    f"**{item['nome']}**"
                )

            with col2:
                st.write(
                    item["tipo"]
                )

            with col3:

                if item.get("ativo", True):

                    st.write(
                        "✅ Ativa"
                    )

                else:

                    st.write(
                        "❌ Inativa"
                    )

            with col4:

                if item.get("ativo", True):

                    if st.button(
                        "Inativar",
                        key=f"inativar_{item['id']}"
                    ):

                        try:

                            service.inativar(
                                item["id"]
                            )

                            st.success(
                                "Instituição inativada."
                            )

                            st.rerun()

                        except Exception as exc:

                            st.error(
                                f"Erro: {exc}"
                            )

            st.divider()

except Exception as exc:

    st.error(
        f"Erro ao carregar instituições: {exc}"
    )