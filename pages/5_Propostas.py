import pandas as pd
import streamlit as st

from crm.database import fetch_by_id
from crm.services import next_revision_number, opportunities_lookup, proposals_table, save_proposal
from crm.ui import format_currency, header, setup_page

setup_page("Propostas")
header("Propostas e Revisões", "Controle de versões, valor, validade, premissas, fora de escopo e entregáveis.")

opps = opportunities_lookup()
opp_labels = [""] + [name for _, name in opps]
opp_label_to_id = {name: _id for _id, name in opps}
id_to_label = {_id: name for _id, name in opps}

df = proposals_table()
mode = st.radio("Modo", ["Nova proposta", "Editar proposta"], horizontal=True)
record = None
record_id = None
existing = {f"{row['opportunity_name']} | {row['version_label']} (#{int(row['id'])})": int(row["id"]) for _, row in df.iterrows()} if not df.empty else {}
if mode == "Editar proposta" and existing:
    label = st.selectbox("Proposta", list(existing.keys()))
    record_id = existing[label]
    record = fetch_by_id("proposals", record_id)

with st.form("proposal_form"):
    c1, c2, c3 = st.columns(3)
    opp_name = c1.selectbox("Oportunidade", opp_labels, index=opp_labels.index(id_to_label.get(record["opportunity_id"], "")) if record else 0)
    opportunity_id = opp_label_to_id.get(opp_name)
    suggested_rev = next_revision_number(opportunity_id) if opportunity_id else 1
    revision_number = c2.number_input("Revisão", min_value=1, step=1, value=int(record["revision_number"]) if record else suggested_rev)
    version_label = c3.text_input("Rótulo da versão", value=record["version_label"] if record else f"R{suggested_rev}")
    d1, d2, d3, d4 = st.columns(4)
    proposal_value = d1.number_input("Valor da proposta (R$)", min_value=0.0, step=10000.0, value=float(record["proposal_value"] or 0) if record else 0.0)
    sent_date = d2.date_input("Data de envio", value=pd.to_datetime(record["sent_date"]).date() if record and record["sent_date"] else pd.Timestamp.today().date())
    validity_days = d3.number_input("Validade (dias)", min_value=1, step=1, value=int(record["validity_days"]) if record else 30)
    execution_deadline = d4.date_input("Prazo de execução", value=pd.to_datetime(record["execution_deadline"]).date() if record and record["execution_deadline"] else pd.Timestamp.today().date())
    status = st.selectbox("Status", ["Rascunho", "Em revisão", "Enviada", "Em negociação", "Aprovada", "Rejeitada"], index=["Rascunho", "Em revisão", "Enviada", "Em negociação", "Aprovada", "Rejeitada"].index(record["status"]) if record and record["status"] in ["Rascunho", "Em revisão", "Enviada", "Em negociação", "Aprovada", "Rejeitada"] else 0)
    objective_text = st.text_area("Objetivo do escopo", value=record["objective_text"] if record else "", height=90)
    service_description = st.text_area("Descrição dos serviços", value=record["service_description"] if record else "", height=120)
    assumptions_text = st.text_area("Premissas", value=record["assumptions_text"] if record else "Cliente fornecerá documentos base, acessos, liberações e validações necessárias ao desenvolvimento da engenharia.", height=120)
    exclusions_text = st.text_area("Fora de escopo", value=record["exclusions_text"] if record else "Não inclui fornecimento, obra, montagem, instalação, manutenção operacional ou comissionamento executivo.", height=120)
    deliverables_text = st.text_area("Lista de documentos / entregáveis", value=record["deliverables_text"] if record else "", height=120)
    hh_summary = st.text_area("Composição HH / perfis", value=record["hh_summary"] if record else "", height=90)
    pricing_notes = st.text_area("Notas comerciais / PPU / condições", value=record["pricing_notes"] if record else "", height=90)
    submitted = st.form_submit_button("Salvar proposta", type="primary")
    if submitted:
        save_proposal({"opportunity_id": opportunity_id, "revision_number": revision_number, "version_label": version_label, "proposal_value": proposal_value, "sent_date": sent_date.isoformat() if sent_date else None, "validity_days": validity_days, "execution_deadline": execution_deadline.isoformat() if execution_deadline else None, "status": status, "objective_text": objective_text, "service_description": service_description, "assumptions_text": assumptions_text, "exclusions_text": exclusions_text, "deliverables_text": deliverables_text, "hh_summary": hh_summary, "pricing_notes": pricing_notes}, record_id=record_id)
        st.success("Proposta salva com sucesso.")
        st.rerun()

st.markdown("### Registro de propostas")
if df.empty:
    st.info("Sem propostas cadastradas.")
else:
    st.dataframe(df[["id", "opportunity_name", "version_label", "revision_number", "proposal_value", "sent_date", "status", "opportunity_stage"]], use_container_width=True, hide_index=True)
    st.markdown("### Valor total registrado")
    st.metric("Total", format_currency(df["proposal_value"].fillna(0).sum()))
