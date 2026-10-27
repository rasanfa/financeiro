from __future__ import annotations

import streamlit as st

from src.services.instituicoes import InstituicoesService

USUARIO_ID = "17c95aaa-3ec6-4dc0-824b-7708fa280c5a"

service = InstituicoesService()

if "instituicao_edicao" not in st.session_state:
    st.session_state.instituicao_edicao = None

st.title("🏦 Instituições")
st.caption("Bancos, corretoras e carteiras digitais")

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

        nome = st.text_input("Nome")

        tipo = st.selectbox(
            "Tipo",
            [
                "BANCO",
                "CORRETORA",
                "CARTEIRA_DIGITAL"
            ]
        )

        salvar = st.form_submit_button("💾 Salvar")

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
    # EDIÇÃO
    # ==========================

    if st.session_state.instituicao_edicao:

        instituicao = st.session_state.instituicao_edicao

        st.divider()

        st.subheader("Editar Instituição")

        with st.form("editar_instituicao"):

            editar_nome = st.text_input(
                "Nome",
                value=instituicao["nome"]
            )

            tipos = [
                "BANCO",
                "CORRETORA",
                "CARTEIRA_DIGITAL"
            ]

            editar_tipo = st.selectbox(
                "Tipo",
                tipos,
                index=tipos.index(
                    instituicao["tipo"]
                )
            )

            salvar_edicao = st.form_submit_button(
                "Salvar Alterações"
            )

            if salvar_edicao:

                try:

                    service.atualizar(
                        instituicao["id"],
                        editar_nome,
                        editar_tipo
                    )

                    st.session_state.instituicao_edicao = None

                    st.success(
                        "Instituição atualizada."
                    )

                    st.rerun()

                except Exception as exc:

                    st.error(
                        f"Erro: {exc}"
                    )

    # ==========================
    # LISTAGEM
    # ==========================

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

            col1, col2, col3, col4, col5 = st.columns(
                [4, 3, 2, 2, 2]
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
                    st.write("✅ Ativa")
                else:
                    st.write("❌ Inativa")

            with col4:

                if item.get("ativo", True):

                    if st.button(
                        "Inativar",
                        key=f"inativar_{item['id']}"
                    ):

                        service.inativar(
                            item["id"]
                        )

                        st.rerun()

            with col5:

                if st.button(
                    "Editar",
                    key=f"editar_{item['id']}"
                ):

                    st.session_state.instituicao_edicao = item

                    st.rerun()

            st.divider()

except Exception as exc:

    st.error(
        f"Erro ao carregar instituições: {exc}"
    )