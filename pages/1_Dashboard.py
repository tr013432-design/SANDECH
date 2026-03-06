import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from crm.config import OPEN_STAGES, PIPELINE_STAGES
from crm.services import dashboard_snapshot
from crm.ui import format_currency, header, setup_page

setup_page("Dashboard")

snap = dashboard_snapshot()
opps = snap["opportunities_df"].copy()
activities = snap["activities_df"].copy()

header("Dashboard Comercial", "Pipeline técnico-comercial, valor ponderado, aging, conversão e gargalos.")

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Pipeline aberto", format_currency(snap["open_pipeline_value"]))
c2.metric("Pipeline ponderado", format_currency(snap["weighted_pipeline_value"]))
c3.metric("Oportunidades abertas", snap["open_opportunities"])
c4.metric("Taxa de conversão", f"{snap['win_rate']:.1f}%")
c5.metric("Atividades vencidas", snap["overdue_activities"])
c6.metric("Propostas registradas", snap["proposals_total"])

if opps.empty:
    st.warning("Ainda não há oportunidades registradas.")
    st.stop()

open_opps = opps[opps["stage"].isin(OPEN_STAGES)].copy()
stage_order = {stage: idx for idx, stage in enumerate(PIPELINE_STAGES)}
opps["stage_order"] = opps["stage"].map(stage_order)

left, right = st.columns((1.2, 1))
with left:
    st.markdown("### Pipeline por etapa")
    stage_df = opps.groupby("stage", dropna=False)["estimated_value"].sum().reset_index()
    stage_df["stage_order"] = stage_df["stage"].map(stage_order)
    stage_df = stage_df.sort_values("stage_order")
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.bar(stage_df["stage"], stage_df["estimated_value"])
    ax.set_ylabel("Valor estimado (R$)")
    ax.tick_params(axis="x", rotation=45)
    st.pyplot(fig)

with right:
    st.markdown("### Oportunidades por segmento")
    seg_df = opps.groupby("segment", dropna=False)["id"].count().reset_index().sort_values("id", ascending=False)
    fig2, ax2 = plt.subplots(figsize=(7, 4))
    ax2.barh(seg_df["segment"], seg_df["id"])
    ax2.invert_yaxis()
    ax2.set_xlabel("Qtd.")
    st.pyplot(fig2)

col_a, col_b = st.columns((1.2, 1))
with col_a:
    st.markdown("### Aging das oportunidades abertas")
    open_opps["created_at"] = pd.to_datetime(open_opps["created_at"], errors="coerce")
    open_opps["aging_days"] = (pd.Timestamp.today() - open_opps["created_at"]).dt.days
    aging_view = open_opps[["opportunity_name", "account_name", "stage", "estimated_value", "probability", "aging_days", "next_step_date"]].sort_values(["aging_days", "estimated_value"], ascending=[False, False])
    st.dataframe(aging_view, use_container_width=True, hide_index=True)

with col_b:
    st.markdown("### Motivos de perda")
    losses = opps[opps["stage"] == "Perdida"].copy()
    if losses.empty:
        st.info("Sem perdas registradas ainda.")
    else:
        loss_df = losses.groupby("loss_reason")["id"].count().reset_index().sort_values("id", ascending=False)
        fig3, ax3 = plt.subplots(figsize=(7, 4))
        ax3.barh(loss_df["loss_reason"], loss_df["id"])
        ax3.invert_yaxis()
        st.pyplot(fig3)

st.markdown("### Próximas ações")
if activities.empty:
    st.info("Nenhuma atividade cadastrada.")
else:
    next_activities = activities.copy()
    next_activities["due_date"] = pd.to_datetime(next_activities["due_date"], errors="coerce")
    next_activities = next_activities.sort_values("due_date").head(12)
    st.dataframe(next_activities[["related_type", "related_id", "activity_type", "description", "owner", "due_date", "status"]], use_container_width=True, hide_index=True)
