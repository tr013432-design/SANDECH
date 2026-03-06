import streamlit as st

from crm.config import BG_COLOR, CARD_COLOR, PRIMARY_COLOR, SECONDARY_COLOR, TEXT_COLOR


def setup_page(page_title: str):
    st.set_page_config(page_title=f"{page_title} | SANDECH CRM", page_icon="🏗️", layout="wide", initial_sidebar_state="expanded")
    apply_theme()


def apply_theme():
    st.markdown(f"""
    <style>
    .stApp {{ background-color: {BG_COLOR}; color: {TEXT_COLOR}; }}
    .main-title {{ font-size: 2rem; font-weight: 700; color: {SECONDARY_COLOR}; margin-bottom: .2rem; }}
    .subtitle {{ color: #55606e; margin-bottom: 1rem; }}
    .card {{ background: {CARD_COLOR}; border: 1px solid #E6ECF2; border-radius: 14px; padding: 16px; box-shadow: 0 2px 10px rgba(16,24,40,.04); margin-bottom: 12px; }}
    .kanban-card {{ background: white; border-radius: 12px; padding: 12px; border: 1px solid #E6ECF2; margin-bottom: 10px; box-shadow: 0 1px 6px rgba(16,24,40,.05); }}
    .kanban-stage {{ background: linear-gradient(180deg,#f9fbfd 0%,#f2f6fa 100%); border:1px solid #dbe6f0; border-radius:16px; padding:12px; min-height:520px; }}
    .kanban-title {{ font-size:.95rem; font-weight:700; color:{SECONDARY_COLOR}; margin-bottom:.6rem; }}
    .small-muted {{ color:#6B7280; font-size:.85rem; }}
    .pill {{ display:inline-block; background:#E6F4F1; color:#0E6B59; padding:3px 8px; border-radius:999px; font-size:.78rem; margin-right:6px; margin-top:4px; }}
    div[data-testid="stMetric"] {{ background:white; border:1px solid #E6ECF2; border-radius:14px; padding:10px; }}
    .block-container {{ padding-top:1.2rem; }}
    </style>
    """, unsafe_allow_html=True)


def header(title: str, subtitle: str):
    st.markdown(f'<div class="main-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="subtitle">{subtitle}</div>', unsafe_allow_html=True)


def format_currency(value) -> str:
    try:
        return f"R$ {float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "R$ 0,00"
