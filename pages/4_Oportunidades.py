from datetime import date

import pandas as pd
import streamlit as st

from crm.config import DISCIPLINES, LEAD_SOURCES, LOCATIONS, LOSS_REASONS, OPPORTUNITY_NATURES, PIPELINE_STAGES, PROJECT_PHASES, SEGMENTS, SERVICE_TYPES, STAGE_PROBABILITIES, TEAM_MEMBERS
from crm.database import fetch_by_id
from crm.services import accounts_lookup, infer_probability_from_stage, open_activities_for_opportunity, opportunity_defaults, opportunity_history, opportunities_table, save_opportunity
from crm.ui import format_currency, header, setup_page

setup_page("Oportunidades")
header("Oportunidades", "Pipeline técnico-comercial com aderência ao processo de engenharia consultiva.")

accounts = accounts_lookup()
account_labels = [""] + [name for _, name in accounts]
account_label_to_id = {name: _id for _id, name in accounts}
id_to_account_label = {_id: name for _id, name in accounts}

df = opportunities_table()
filters = st.columns(4)
with filters[0]:
    selected_stage = st.selectbox("Filtrar por etapa", ["Todas"] + PIPELINE_STAGES)
with filters[1]:
    selected_segment = st.selectbox("Filtrar por segmento", ["Todos"] + SEGMENTS)
with filters[2]:
    selected_owner = st.selectbox("Responsável comercial", ["Todos"] + TEAM_MEMBERS)
with filters[3]:
    min_value = st.number_input("Valor mínimo estimado", min_value=0.0, step=50000.0)

view_df = df.copy()
if not view_df.empty:
    if selected_stage != "Todas":
        view_df = view_df[view_df["stage"] == selected_stage]
    if selected_segment != "Todos":
        view_df = view_df[view_df["segment"] == selected_segment]
    if selected_owner != "Todos":
        view_df = view_df[view_df["commercial_owner"] == selected_owner]
    view_df = view_df[view_df["estimated_value"] >= min_value]

tab1, tab2, tab3 = st.tabs(["Kanban", "Tabela", "Cadastro / edição"])

with tab1:
    if view_df.empty:
        st.info("Nenhuma oportunidade para os filtros selecionados.")
    else:
        display_stages = [s for s in PIPELINE_STAGES if s not in ["Ganha", "Perdida", "Stand-by"]]
        cols = st.columns(len(display_stages))
        for col, stage in zip(cols, display_stages):
            with col:
                st.markdown(f'<div class="kanban-stage"><div class="kanban-title">{stage}</div>', unsafe_allow_html=True)
                stage_items = view_df[view_df["stage"] == stage].sort_values("estimated_value", ascending=False)
                if stage_items.empty:
                    st.caption("Sem oportunidades")
                for _, row in stage_items.head(10).iterrows():
                    st.markdown(f"""
                        <div class=\"kanban-card\">
                            <strong>{row['opportunity_name']}</strong><br>
                            <span class=\"small-muted\">{row.get('account_name', '')}</span><br>
                            <span class=\"pill\">{row['main_discipline']}</span>
                            <span class=\"pill\">{row['segment']}</span><br><br>
                            <strong>{format_currency(row['estimated_value'])}</strong><br>
                            Prob.: {int(row['probability'])}%<br>
                            Próximo passo: {row.get('next_step', '') or '-'}
                        </div>
                    """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    if view_df.empty:
        st.info("Nenhuma oportunidade cadastrada.")
    else:
        st.dataframe(view_df[["id", "opportunity_name", "account_name", "stage", "segment", "service_type", "main_discipline", "estimated_value", "probability", "weighted_value", "next_step_date"]], use_container_width=True, hide_index=True)
        st.markdown("### Detalhe rápido")
        option_labels = [f"{row['opportunity_name']} (#{int(row['id'])})" for _, row in view_df.iterrows()]
        option_map = {f"{row['opportunity_name']} (#{int(row['id'])})": int(row["id"]) for _, row in view_df.iterrows()}
        selected = st.selectbox("Selecionar oportunidade", option_labels)
        selected_id = option_map[selected]
        record = fetch_by_id("opportunities", selected_id)
        c1, c2 = st.columns((1.3, 1))
        with c1:
            st.markdown("#### Resumo")
            st.write(record["scope_summary"] or "-")
            st.markdown("#### Objetivo do cliente")
            st.write(record["client_objective"] or "-")
            st.markdown("#### Entregáveis")
            st.write(record["key_deliverables"] or "-")
        with c2:
            st.markdown("#### Controle")
            st.write(f"**Etapa:** {record['stage']}")
            st.write(f"**Valor estimado:** {format_currency(record['estimated_value'])}")
            st.write(f"**Probabilidade:** {record['probability']}%")
            st.write(f"**Risco:** {record['risk_level']}")
            st.write(f"**Bloqueador:** {record['current_blocker'] or '-'}")
        st.markdown("#### Histórico de etapa")
        st.dataframe(opportunity_history(selected_id), use_container_width=True, hide_index=True)
        st.markdown("#### Atividades abertas")
        st.dataframe(open_activities_for_opportunity(selected_id), use_container_width=True, hide_index=True)

with tab3:
    record_id = None
    existing_options = {f"{row['opportunity_name']} (#{int(row['id'])})": int(row["id"]) for _, row in df.iterrows()} if not df.empty else {}
    mode = st.radio("Modo", ["Nova oportunidade", "Editar oportunidade"], horizontal=True, key="opp_mode")
    current = opportunity_defaults()
    previous_stage = None
    if mode == "Editar oportunidade" and existing_options:
        selected_label = st.selectbox("Oportunidade", list(existing_options.keys()), key="edit_opp_select")
        record_id = existing_options[selected_label]
        rec = fetch_by_id("opportunities", record_id)
        current.update(rec)
        previous_stage = rec["stage"]

    with st.form("opp_form"):
        a1, a2, a3 = st.columns(3)
        opportunity_name = a1.text_input("Nome da oportunidade", value=current["opportunity_name"])
        internal_code = a2.text_input("Código interno", value=current["internal_code"] or "")
        account_name = a3.selectbox("Cliente", account_labels, index=account_labels.index(id_to_account_label.get(current["account_id"], "")) if current["account_id"] else 0)
        b1, b2, b3, b4 = st.columns(4)
        unit_asset = b1.text_input("Unidade / ativo", value=current["unit_asset"] or "")
        segment = b2.selectbox("Segmento", [""] + SEGMENTS, index=([""] + SEGMENTS).index(current["segment"]) if current["segment"] in SEGMENTS else 0)
        lead_source = b3.selectbox("Origem do lead", [""] + LEAD_SOURCES, index=([""] + LEAD_SOURCES).index(current["lead_source"]) if current["lead_source"] in LEAD_SOURCES else 0)
        service_type = b4.selectbox("Tipo de serviço", [""] + SERVICE_TYPES, index=([""] + SERVICE_TYPES).index(current["service_type"]) if current["service_type"] in SERVICE_TYPES else 0)
        c1, c2, c3, c4 = st.columns(4)
        main_discipline = c1.selectbox("Disciplina principal", [""] + DISCIPLINES, index=([""] + DISCIPLINES).index(current["main_discipline"]) if current["main_discipline"] in DISCIPLINES else 0)
        involved_disciplines = c2.multiselect("Disciplinas envolvidas", DISCIPLINES, default=[d.strip() for d in (current["involved_disciplines"] or "").split(",") if d.strip()])
        nature = c3.selectbox("Natureza", [""] + OPPORTUNITY_NATURES, index=([""] + OPPORTUNITY_NATURES).index(current["nature"]) if current["nature"] in OPPORTUNITY_NATURES else 0)
        project_phase = c4.selectbox("Fase do projeto", [""] + PROJECT_PHASES, index=([""] + PROJECT_PHASES).index(current["project_phase"]) if current["project_phase"] in PROJECT_PHASES else 0)
        d1, d2, d3, d4 = st.columns(4)
        location_type = d1.selectbox("Onshore / Offshore", [""] + LOCATIONS, index=([""] + LOCATIONS).index(current["location_type"]) if current["location_type"] in LOCATIONS else 0)
        stage = d2.selectbox("Etapa do funil", PIPELINE_STAGES, index=PIPELINE_STAGES.index(current["stage"]) if current["stage"] in PIPELINE_STAGES else 0)
        probability = d3.number_input("Probabilidade (%)", min_value=0, max_value=100, value=int(current["probability"] or infer_probability_from_stage(stage)))
        risk_level = d4.selectbox("Risco", ["Baixo", "Médio", "Alto"], index=["Baixo", "Médio", "Alto"].index(current["risk_level"]) if current["risk_level"] in ["Baixo", "Médio", "Alto"] else 1)
        scope_summary = st.text_area("Resumo do escopo", value=current["scope_summary"] or "", height=90)
        client_objective = st.text_area("Objetivo do cliente", value=current["client_objective"] or "", height=90)
        key_deliverables = st.text_area("Entregáveis principais", value=current["key_deliverables"] or "", height=90)
        e1, e2 = st.columns(2)
        critical_assumptions = e1.text_area("Premissas críticas", value=current["critical_assumptions"] or "", height=120)
        information_gaps = e2.text_area("Lacunas de informação", value=current["information_gaps"] or "", height=120)
        f1, f2, f3, f4, f5 = st.columns(5)
        needs_site_visit = f1.checkbox("Visita técnica", value=bool(current["needs_site_visit"]))
        needs_technical_meeting = f2.checkbox("Reunião técnica", value=bool(current["needs_technical_meeting"]))
        needs_nda = f3.checkbox("NDA", value=bool(current["needs_nda"]))
        needs_contract_draft = f4.checkbox("Minuta", value=bool(current["needs_contract_draft"]))
        needs_registration = f5.checkbox("Cadastro prévio", value=bool(current["needs_registration"]))
        g1, g2, g3, g4 = st.columns(4)
        estimated_value = g1.number_input("Valor estimado (R$)", min_value=0.0, step=10000.0, value=float(current["estimated_value"] or 0))
        estimated_hh = g2.number_input("HH estimadas", min_value=0.0, step=10.0, value=float(current["estimated_hh"] or 0))
        target_margin = g3.number_input("Margem alvo (%)", min_value=0.0, max_value=100.0, step=1.0, value=float(current["target_margin"] or 0))
        mapped_competitor = g4.text_input("Concorrente mapeado", value=current["mapped_competitor"] or "")
        h1, h2 = st.columns(2)
        proposal_deadline = h1.date_input("Prazo da proposta", value=pd.to_datetime(current["proposal_deadline"]).date() if current["proposal_deadline"] else date.today())
        execution_deadline = h2.date_input("Prazo de execução", value=pd.to_datetime(current["execution_deadline"]).date() if current["execution_deadline"] else date.today())
        i1, i2, i3, i4 = st.columns(4)
        commercial_owner = i1.selectbox("Responsável comercial", TEAM_MEMBERS, index=TEAM_MEMBERS.index(current["commercial_owner"]) if current["commercial_owner"] in TEAM_MEMBERS else 0)
        proposal_owner = i2.selectbox("Responsável da proposta", TEAM_MEMBERS, index=TEAM_MEMBERS.index(current["proposal_owner"]) if current["proposal_owner"] in TEAM_MEMBERS else 1 if len(TEAM_MEMBERS) > 1 else 0)
        technical_coordinator = i3.selectbox("Coordenação técnica", TEAM_MEMBERS, index=TEAM_MEMBERS.index(current["technical_coordinator"]) if current["technical_coordinator"] in TEAM_MEMBERS else 1 if len(TEAM_MEMBERS) > 1 else 0)
        approving_director = i4.selectbox("Diretor aprovador", TEAM_MEMBERS, index=TEAM_MEMBERS.index(current["approving_director"]) if current["approving_director"] in TEAM_MEMBERS else 3 if len(TEAM_MEMBERS) > 3 else 0)
        j1, j2 = st.columns(2)
        next_step = j1.text_input("Próximo passo", value=current["next_step"] or "")
        next_step_date = j2.date_input("Data do próximo passo", value=pd.to_datetime(current["next_step_date"]).date() if current["next_step_date"] else date.today())
        k1, k2, k3 = st.columns(3)
        current_blocker = k1.text_input("Bloqueador atual", value=current["current_blocker"] or "")
        go_no_go_status = k2.selectbox("Status Go / No-Go", ["Em análise", "Go", "No-Go"], index=["Em análise", "Go", "No-Go"].index(current["go_no_go_status"]) if current["go_no_go_status"] in ["Em análise", "Go", "No-Go"] else 0)
        loss_reason = k3.selectbox("Motivo de perda", [""] + LOSS_REASONS, index=([""] + LOSS_REASONS).index(current["loss_reason"]) if current["loss_reason"] in LOSS_REASONS else 0)
        submitted = st.form_submit_button("Salvar oportunidade", type="primary")
        if submitted:
            payload = {"opportunity_name": opportunity_name, "internal_code": internal_code, "account_id": account_label_to_id.get(account_name), "unit_asset": unit_asset, "segment": segment, "lead_source": lead_source, "service_type": service_type, "main_discipline": main_discipline, "involved_disciplines": ", ".join(involved_disciplines), "nature": nature, "project_phase": project_phase, "location_type": location_type, "scope_summary": scope_summary, "client_objective": client_objective, "key_deliverables": key_deliverables, "critical_assumptions": critical_assumptions, "information_gaps": information_gaps, "needs_site_visit": 1 if needs_site_visit else 0, "needs_technical_meeting": 1 if needs_technical_meeting else 0, "needs_nda": 1 if needs_nda else 0, "needs_contract_draft": 1 if needs_contract_draft else 0, "needs_registration": 1 if needs_registration else 0, "estimated_value": estimated_value, "estimated_hh": estimated_hh, "target_margin": target_margin, "probability": probability if probability else STAGE_PROBABILITIES.get(stage, 0), "proposal_deadline": proposal_deadline.isoformat() if proposal_deadline else None, "execution_deadline": execution_deadline.isoformat() if execution_deadline else None, "commercial_owner": commercial_owner, "proposal_owner": proposal_owner, "technical_coordinator": technical_coordinator, "approving_director": approving_director, "next_step": next_step, "next_step_date": next_step_date.isoformat() if next_step_date else None, "current_blocker": current_blocker, "mapped_competitor": mapped_competitor, "loss_reason": loss_reason, "stage": stage, "go_no_go_status": go_no_go_status, "risk_level": risk_level}
            save_opportunity(payload, record_id=record_id, previous_stage=previous_stage)
            st.success("Oportunidade salva com sucesso.")
            st.rerun()
