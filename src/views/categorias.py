from __future__ import annotations

import streamlit as st

from src.services.categorias import CategoriasService
from src.ui.components import render_total_card

USUARIO_ID = "17c95aaa-3ec6-4dc0-824b-7708fa280c5a"

service = CategoriasService()

if "categoria_edicao" not in st.session_state:
    st.session_state.categoria_edicao = None

if "mostrar_form_categoria" not in st.session_state:
    st.session_state.mostrar_form_categoria = False

st.title("🏷️ Categorias")

try:

    categorias = service.listar()

    render_total_card(
        "Categorias",
        len(categorias)
    )

    if st.button("Nova Categoria"):
        st.session_state.mostrar_form_categoria = True

    if st.session_state.mostrar_form_categoria:

        with st.expander(
            "Nova Categoria",
            expanded=True
        ):

            with st.form("categoria_form"):

                nome = st.text_input(
                    "Nome"
                )

                tipos = [
                    "RECEITA",
                    "DESPESA",
                    "AMBOS"
                ]

                tipo_categoria = st.selectbox(
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
                        tipo_categoria=tipo_categoria
                    )

                    st.session_state.mostrar_form_categoria = False

                    st.rerun()

    st.divider()

    h1, h2, h3 = st.columns(
        [6, 3, 1]
    )

    h1.markdown("**Nome**")
    h2.markdown("**Tipo**")
    h3.markdown("**Ações**")

    for categoria in categorias:

        c1, c2, c3 = st.columns(
            [6, 3, 1]
        )

        c1.write(
            categoria["nome"]
        )

        c2.write(
            categoria["tipo_categoria"]
        )

        if c3.button(
            "Editar",
            key=f"editar_{categoria['id']}"
        ):

            st.session_state.categoria_edicao = categoria

            st.rerun()

    if st.session_state.categoria_edicao:

        categoria = (
            st.session_state.categoria_edicao
        )

        st.divider()

        st.subheader(
            f"Editar {categoria['nome']}"
        )

        tipos = [
            "RECEITA",
            "DESPESA",
            "AMBOS"
        ]

        with st.form(
            "editar_categoria"
        ):

            editar_nome = st.text_input(
                "Nome",
                value=categoria["nome"]
            )

            editar_tipo = st.selectbox(
                "Tipo",
                tipos,
                index=tipos.index(
                    categoria["tipo_categoria"]
                )
            )

            col1, col2 = st.columns(2)

            with col1:

                salvar = st.form_submit_button(
                    "Salvar Alterações"
                )

            with col2:

                inativar = st.form_submit_button(
                    "Inativar Categoria"
                )

            if salvar:

                service.atualizar(
                    categoria["id"],
                    editar_nome,
                    editar_tipo
                )

                st.session_state.categoria_edicao = None

                st.rerun()

            if inativar:

                service.inativar(
                    categoria["id"]
                )

                st.session_state.categoria_edicao = None

                st.rerun()

except Exception as exc:

    st.error(
        f"Erro ao carregar categorias: {exc}"
    )