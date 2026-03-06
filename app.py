from crm.database import init_db
from crm.seed import seed_if_empty
from crm.ui import header, setup_page

setup_page("Início")
init_db()
seed_if_empty()

import streamlit as st

header("SANDECH CRM", "CRM técnico-comercial para engenharia consultiva, com pipeline, propostas, follow-up e dashboards.")

st.markdown(
    """
    <div class=\"card\">
        <strong>Visão do produto</strong><br>
        Estrutura inspirada em CRMs modernos de vendas, mas adaptada para o contexto da SANDECH:
        contas, contatos, oportunidades, propostas, histórico, automações por etapa e biblioteca comercial/técnica.
        Use o menu lateral para navegar.
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2 = st.columns(2)
with col1:
    st.info("Fluxo comercial: Lead identificado → Qualificação inicial → Entendimento do escopo → Go / No-Go → Elaboração de proposta → Proposta enviada → Negociação → Decisão.")
with col2:
    st.success("Proteções do sistema: não posiciona a empresa como executora de obra, montagem, fornecimento ou manutenção operacional.")
