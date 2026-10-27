from __future__ import annotations

import streamlit as st

from src.config import get_settings
from src.ui.theme import apply_theme


def _render_sidebar_status() -> None:
    settings = get_settings()
    with st.sidebar:
        st.divider()
        if settings.supabase_configured:
            st.caption("Supabase: configurado")
        else:
            st.caption("Supabase: pendente (.env)")


def run_app() -> None:
    st.set_page_config(
        page_title="Finanças Pessoais",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    apply_theme()

    dashboard = st.Page(
        "src/views/dashboard.py",
        title="Dashboard",
        icon="📊",
        default=True,
    )
    instituicoes = st.Page(
        "src/views/instituicoes.py",
        title="Instituições",
        icon="🏛️",
    )
    contas = st.Page(
        "src/views/contas.py",
        title="Contas",
        icon="🏦",
    )
    cartoes = st.Page(
        "src/views/cartoes.py",
        title="Cartões",
        icon="💳",
    )
    categorias = st.Page(
        "src/views/categorias.py",
        title="Categorias",
        icon="🏷️",
    )
    beneficiarios = st.Page(
        "src/views/beneficiarios.py",
        title="Beneficiários",
        icon="👤",
    )
    movimentacoes = st.Page(
        "src/views/movimentacoes.py",
        title="Movimentações",
        icon="📒",
    )

    navigator = st.navigation(
        {
            "Início": [dashboard],
            "Cadastros": [
                instituicoes,
                contas,
                cartoes,
                categorias,
                beneficiarios,
            ],
            "Lançamentos": [movimentacoes],
        }
    )
    _render_sidebar_status()
    navigator.run()
