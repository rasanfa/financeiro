from __future__ import annotations

import streamlit as st

from src.services.instituicoes import InstituicoesService
from src.ui.components import render_total_card

USUARIO_ID = "17c95aaa-3ec6-4dc0-824b-7708fa280c5a"

service = InstituicoesService()

if "instituicao_edicao" not in st.session_state:
    st.session_state.instituicao_edicao = None

if "mostrar_form_instituicao" not in st.session_state:
    st.session_state.mostrar_form_instituicao = False

st.title("🏦 Instituições")

try:

    instituicoes = service.listar()

    render_total_card(
        "Instituições",
        len(instituicoes)
    )

    if st.button("Nova Instituição"):
        st.session_state.mostrar_form_instituicao = True

    if st.session_state.mostrar_form_instituicao:

        with st.expander(
            "Nova Instituição",
            expanded=True
        ):

            with st.form("instituicao_form"):

                nome = st.text_input("Nome")

                tipos = [
                    "BANCO",
                    "CORRETORA",
                    "CARTEIRA_DIGITAL"
                ]

                tipo = st.selectbox(
                    "Tipo",
                    tipos
                )

                salvar = st.form_submit_button(
                    "Salvar"
                )

                if salvar:

                    service.criar(
                        usuario_id=USUARIO_ID,
                        nome=nome,
                        tipo=tipo
                    )

                    st.session_state.mostrar_form_instituicao = False

                    st.rerun()

    st.divider()

    h1, h2, h3 = st.columns(
        [6, 3, 1]
    )

    h1.markdown("**Nome**")
    h2.markdown("**Tipo**")
    h3.markdown("**Ações**")

    for item in instituicoes:

        c1, c2, c3 = st.columns(
            [6, 3, 1]
        )

        c1.write(item["nome"])

        c2.write(item["tipo"])

        if c3.button(
            "Editar",
            key=f"editar_{item['id']}"
        ):

            st.session_state.instituicao_edicao = item

            st.rerun()

    if st.session_state.instituicao_edicao:

        item = st.session_state.instituicao_edicao

        st.divider()

        st.subheader(
            f"Editar {item['nome']}"
        )

        tipos = [
            "BANCO",
            "CORRETORA",
            "CARTEIRA_DIGITAL"
        ]

        with st.form(
            "editar_instituicao"
        ):

            editar_nome = st.text_input(
                "Nome",
                value=item["nome"]
            )

            editar_tipo = st.selectbox(
                "Tipo",
                tipos,
                index=tipos.index(
                    item["tipo"]
                )
            )

            salvar = st.form_submit_button(
                "Salvar Alterações"
            )

            if salvar:

                service.atualizar(
                    item["id"],
                    editar_nome,
                    editar_tipo
                )

                st.session_state.instituicao_edicao = None

                st.rerun()

except Exception as exc:

    st.error(
        f"Erro ao carregar instituições: {exc}"
    )