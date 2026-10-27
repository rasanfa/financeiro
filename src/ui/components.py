# src/ui/components.py

import streamlit as st

def render_total_card(
    titulo: str,
    valor: int
):
    col1, col2 = st.columns([2, 8])

    with col1:
        st.metric(
            label=titulo,
            value=valor
        )