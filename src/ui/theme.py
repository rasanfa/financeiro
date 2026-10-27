from __future__ import annotations

import streamlit as st


def apply_theme() -> None:

    st.markdown(
        """
        <style>

        .stApp {
            background-color: #F8FAFC;
        }

        .main .block-container {
            max-width: 1350px;
            padding-top: 1.5rem;
        }

        /* SIDEBAR */

        section[data-testid="stSidebar"] {

            background: #1E293B;

        }

        section[data-testid="stSidebar"] * {

            color: white;

        }

        /* TITULOS */

        h1,h2,h3 {

            color: #0F172A;

        }

        /* METRICAS */

        div[data-testid="stMetric"] {

            background: white;

            border: 1px solid #CBD5E1;

            border-radius: 16px;

            padding: 16px;

            box-shadow:
                0 2px 6px rgba(0,0,0,.05);

        }

        /* FORMULARIOS */

        div[data-testid="stForm"] {

            background: #FFFFFF;

            border: 1px solid #CBD5E1;

            border-radius: 16px;

            padding: 1.5rem;

            box-shadow:
                0 2px 6px rgba(0,0,0,.05);
        }

        /* EXPANDERS */

        div[data-testid="stExpander"] {

            background: white;

            border: 1px solid #CBD5E1;

            border-radius: 16px;

        }

        /* INPUTS */

        div[data-testid="stTextInput"] input {

            background: #FFFFFF !important;

            border: 2px solid #CBD5E1 !important;

            border-radius: 10px !important;

            color: #111827 !important;

        }

        div[data-testid="stTextInput"] input:focus {

            border-color: #334155 !important;

            box-shadow:
                0 0 0 2px rgba(51,65,85,.15);

        }

        /* SELECT */

        div[data-testid="stSelectbox"] {

            background: transparent;

        }

        /* BOTÕES */

        div.stButton > button {

            background: #FFFFFF !important;

            color: #0F172A !important;

            border: 1px solid #CBD5E1 !important;

            border-radius: 10px !important;

            font-weight: 600 !important;

            box-shadow:
                0 1px 2px rgba(0,0,0,.05);

        }

        div.stButton > button:hover {

            background: #F8FAFC !important;

            border-color: #94A3B8 !important;

        }

        /* CABEÇALHOS DAS LISTAS */

        hr {

            border-color: #CBD5E1;

        }

        </style>
        """,
        unsafe_allow_html=True,
    )