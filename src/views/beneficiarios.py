from __future__ import annotations

import streamlit as st

from src.services.beneficiarios import BeneficiariosService
from src.ui.components import render_total_card

USUARIO_ID = "17c95aaa-3ec6-4dc0-824b-7708fa280c5a"

service = BeneficiariosService()
tipos = [
    "PESSOA",
    "EMPRESA",
    "GOVERNO",
    "OUTROS"
]
opcoes_tipo = [
    "Não informado",
    *tipos
]

if "beneficiario_edicao" not in st.session_state:
    st.session_state.beneficiario_edicao = None

if "mostrar_form_beneficiario" not in st.session_state:
    st.session_state.mostrar_form_beneficiario = False

st.title("👥 Beneficiários")

try:

    beneficiarios = service.listar()

    render_total_card(
        "Beneficiários",
        len(beneficiarios)
    )

    if st.button("Novo Beneficiário"):
        st.session_state.mostrar_form_beneficiario = True

    if st.session_state.mostrar_form_beneficiario:

        with st.expander(
            "Novo Beneficiário",
            expanded=True
        ):

            with st.form("beneficiario_form"):

                nome = st.text_input("Nome")

                tipo = st.selectbox(
                    "Tipo",
                    opcoes_tipo
                )

                observacao = st.text_area("Observação")

                salvar = st.form_submit_button("Salvar")

                if salvar:

                    service.criar(
                        usuario_id=USUARIO_ID,
                        nome=nome,
                        tipo=tipo if tipo != "Não informado" else None,
                        observacao=observacao or None
                    )

                    st.session_state.mostrar_form_beneficiario = False

                    st.rerun()

    st.divider()

    h1, h2, h3 = st.columns(
        [6, 3, 1]
    )

    h1.markdown("**Nome**")
    h2.markdown("**Tipo**")
    h3.markdown("**Ações**")

    for beneficiario in beneficiarios:

        c1, c2, c3 = st.columns(
            [6, 3, 1]
        )

        c1.write(beneficiario["nome"])

        c2.write(beneficiario["tipo"] or "—")

        if c3.button(
            "Editar",
            key=f"editar_{beneficiario['id']}"
        ):

            st.session_state.beneficiario_edicao = beneficiario

            st.rerun()

    if st.session_state.beneficiario_edicao:

        beneficiario = st.session_state.beneficiario_edicao

        st.divider()

        st.subheader(
            f"Editar {beneficiario['nome']}"
        )

        tipo_atual = beneficiario.get("tipo")
        indice_tipo = (
            opcoes_tipo.index(tipo_atual)
            if tipo_atual in opcoes_tipo
            else 0
        )

        with st.form("editar_beneficiario"):

            editar_nome = st.text_input(
                "Nome",
                value=beneficiario["nome"]
            )

            editar_tipo = st.selectbox(
                "Tipo",
                opcoes_tipo,
                index=indice_tipo
            )

            editar_observacao = st.text_area(
                "Observação",
                value=beneficiario.get("observacao") or ""
            )

            col1, col2 = st.columns(2)

            with col1:

                salvar = st.form_submit_button(
                    "Salvar Alterações"
                )

            with col2:

                inativar = st.form_submit_button(
                    "Inativar Beneficiário"
                )

            if salvar:

                service.atualizar(
                    beneficiario["id"],
                    editar_nome,
                    editar_tipo if editar_tipo != "Não informado" else None,
                    editar_observacao or None
                )

                st.session_state.beneficiario_edicao = None

                st.rerun()

            if inativar:

                service.inativar(
                    beneficiario["id"]
                )

                st.session_state.beneficiario_edicao = None

                st.rerun()

except Exception as exc:

    st.error(
        f"Erro ao carregar beneficiários: {exc}"
    )
