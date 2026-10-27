from __future__ import annotations

import math

import streamlit as st

from src.services.categorias import CategoriasService
from src.ui.components import render_total_card

service = CategoriasService()

if "mostrar_form_subcategoria" not in st.session_state:
    st.session_state.mostrar_form_subcategoria = False


st.title("🗂️ Plano de Categorias")

try:

    categorias = service.listar()

    subcategorias = service.listar_subcategorias()

    render_total_card(
        "Subcategorias",
        len(subcategorias)
    )

    if st.button("Nova Subcategoria"):
        st.session_state.mostrar_form_subcategoria = True

    if st.session_state.mostrar_form_subcategoria:

        with st.expander(
            "Nova Subcategoria",
            expanded=True
        ):

            with st.form(
                "subcategoria_form"
            ):

                categoria_nome = st.selectbox(
                    "Categoria",
                    [
                        c["nome"]
                        for c in categorias
                        if c.get("ativo", True)
                    ]
                )

                nome = st.text_input(
                    "Nome"
                )

                salvar = st.form_submit_button(
                    "Salvar"
                )

                if salvar:

                    categoria_id = next(
                        c["id"]
                        for c in categorias
                        if c["nome"] == categoria_nome
                    )

                    service.criar_subcategoria(
                        categoria_id,
                        nome
                    )

                    st.session_state.mostrar_form_subcategoria = False

                    st.rerun()

    # --------------------------------------------------
    # Agrupamento
    # --------------------------------------------------

    categorias_receita = []
    categorias_despesa = []

    for categoria in categorias:

        if not categoria.get("ativo", True):
            continue

        categoria["subcategorias"] = [

            sub["nome"]

            for sub in subcategorias

            if sub["categoria_id"] == categoria["id"]
            and sub.get("ativo", True)

        ]

        if categoria["tipo_categoria"] in (
            "RECEITA",
            "AMBOS"
        ):
            categorias_receita.append(
                categoria
            )

        if categoria["tipo_categoria"] in (
            "DESPESA",
            "AMBOS"
        ):
            categorias_despesa.append(
                categoria
            )

    total_receitas = len(
        categorias_receita
    )

    total_despesas = len(
        categorias_despesa
    )

    total = max(
        total_receitas + total_despesas,
        1
    )

    colunas_receita = max(
        1,
        round(
            4 * total_receitas / total
        )
    )

    colunas_despesa = (
        4 - colunas_receita
    )

    if colunas_despesa < 1:
        colunas_despesa = 1
        colunas_receita = 3

    st.divider()

    st.subheader("🟢 Receitas")

    receita_cols = st.columns(
        colunas_receita
    )

    for idx, categoria in enumerate(
        categorias_receita
    ):

        with receita_cols[
            idx % colunas_receita
        ]:

            with st.container():

                st.markdown(
                    f"#### {categoria['nome']}"
                )

                if categoria["subcategorias"]:

                    for nome in categoria[
                        "subcategorias"
                    ]:

                        st.write(
                            f"• {nome}"
                        )

                else:

                    st.caption(
                        "Sem subcategorias"
                    )

    st.divider()

    st.subheader("🔴 Despesas")

    despesa_cols = st.columns(
        colunas_despesa
    )

    for idx, categoria in enumerate(
        categorias_despesa
    ):

        with despesa_cols[
            idx % colunas_despesa
        ]:

            with st.container():

                st.markdown(
                    f"#### {categoria['nome']}"
                )

                if categoria["subcategorias"]:

                    for nome in categoria[
                        "subcategorias"
                    ]:

                        st.write(
                            f"• {nome}"
                        )

                else:

                    st.caption(
                        "Sem subcategorias"
                    )

except Exception as exc:

    st.error(
        f"Erro ao carregar plano de categorias: {exc}"
    )