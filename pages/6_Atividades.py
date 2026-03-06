import pandas as pd
import streamlit as st

from crm.config import ACTIVITY_TYPES, TEAM_MEMBERS
from crm.services import activities_table, opportunities_lookup, save_activity
from crm.ui import header, setup_page

setup_page("Atividades")
header("Atividades e Follow-up", "Agenda operacional do comercial, engenharia, jurídico e diretoria.")

opps = opportunities_lookup()
opp_labels = [""] + [name for _, name in opps]
opp_label_to_id = {name: _id for _id, name in opps}

df = activities_table()
with st.form("activity_form"):
    c1, c2, c3 = st.columns(3)
    opp_name = c1.selectbox("Oportunidade relacionada", opp_labels)
    activity_type = c2.selectbox("Tipo", ACTIVITY_TYPES)
    owner = c3.selectbox("Responsável", TEAM_MEMBERS)
    c4, c5 = st.columns((2, 1))
    description = c4.text_input("Descrição")
    due_date = c5.date_input("Prazo", value=pd.Timestamp.today().date())
    status = st.selectbox("Status", ["Aberta", "Em andamento", "Concluída"])
    submitted = st.form_submit_button("Salvar atividade", type="primary")
    if submitted:
        save_activity({"related_type": "opportunity", "related_id": opp_label_to_id.get(opp_name, 0), "activity_type": activity_type, "description": description, "owner": owner, "due_date": due_date.isoformat() if due_date else None, "status": status})
        st.success("Atividade salva com sucesso.")
        st.rerun()

st.markdown("### Backlog de atividades")
if df.empty:
    st.info("Sem atividades.")
else:
    df["due_date"] = pd.to_datetime(df["due_date"], errors="coerce")
    today = pd.Timestamp.today().normalize()
    overdue = df[(df["status"] != "Concluída") & (df["due_date"] < today)]
    due_soon = df[(df["status"] != "Concluída") & (df["due_date"] >= today)].sort_values("due_date")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Vencidas")
        st.dataframe(overdue, use_container_width=True, hide_index=True)
    with col2:
        st.markdown("#### Próximas")
        st.dataframe(due_soon.head(15), use_container_width=True, hide_index=True)
