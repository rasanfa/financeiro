from __future__ import annotations

import streamlit as st

from src.config import get_settings


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

    dashboard = st.Page(
        "src/views/dashboard.py",
        title="Dashboard",
        icon="📊",
        default=True,
    )
    categorias = st.Page(
        "src/views/categorias.py",
        title="Categorias",
        icon="🏷️",
    )
    contas = st.Page(
        "src/views/contas.py",
        title="Contas",
        icon="🏦",
    )

    navigator = st.navigation(
        {
            "Menu": [dashboard, categorias, contas],
        }
    )
    _render_sidebar_status()
    navigator.run()
