import streamlit as st

from crm.config import SEGMENTS
from crm.database import fetch_all, fetch_by_id
from crm.services import account_contacts, save_account
from crm.ui import header, setup_page

setup_page("Contas")
header("Contas / Clientes", "Cadastro de clientes, plantas, contas estratégicas e contexto comercial.")

accounts = fetch_all("accounts")
account_options = {f"{row['name']} (#{row['id']})": int(row["id"]) for _, row in accounts.iterrows()} if not accounts.empty else {}

st.markdown("### Cadastro / edição de conta")
selected_id = None
mode = st.radio("Modo", ["Nova conta", "Editar conta"], horizontal=True)
record = None
if mode == "Editar conta" and account_options:
    selected_label = st.selectbox("Conta", options=list(account_options.keys()))
    selected_id = account_options[selected_label]
    record = fetch_by_id("accounts", selected_id)

with st.form("account_form"):
    c1, c2, c3 = st.columns(3)
    name = c1.text_input("Nome da conta", value=record["name"] if record else "")
    segment = c2.selectbox("Segmento", [""] + SEGMENTS, index=([""] + SEGMENTS).index(record["segment"]) if record and record["segment"] in SEGMENTS else 0)
    strategic_status = c3.selectbox("Status", ["Prospect", "Ativa", "Conta estratégica", "Inativa"], index=["Prospect", "Ativa", "Conta estratégica", "Inativa"].index(record["strategic_status"]) if record and record["strategic_status"] in ["Prospect", "Ativa", "Conta estratégica", "Inativa"] else 0)
    c4, c5, c6 = st.columns(3)
    cnpj = c4.text_input("CNPJ", value=record["cnpj"] if record else "")
    site = c5.text_input("Site", value=record["site"] if record else "")
    main_unit = c6.text_input("Unidade principal / ativo", value=record["main_unit"] if record else "")
    notes = st.text_area("Notas comerciais / técnicas", value=record["notes"] if record else "", height=120)
    submitted = st.form_submit_button("Salvar conta", type="primary")
    if submitted:
        save_account({"name": name, "segment": segment, "cnpj": cnpj, "site": site, "main_unit": main_unit, "strategic_status": strategic_status, "notes": notes}, record_id=selected_id)
        st.success("Conta salva com sucesso.")
        st.rerun()

st.markdown("### Base de contas")
if accounts.empty:
    st.info("Sem contas cadastradas.")
else:
    st.dataframe(accounts[["id", "name", "segment", "main_unit", "strategic_status", "updated_at"]], use_container_width=True, hide_index=True)
    st.markdown("### Contatos por conta")
    if account_options:
        account_label = st.selectbox("Ver contatos da conta", options=list(account_options.keys()), key="contacts_by_account")
        contacts_df = account_contacts(account_options[account_label])
        if contacts_df.empty:
            st.info("Sem contatos vinculados.")
        else:
            st.dataframe(contacts_df[["name", "role", "email", "phone", "influence_level"]], use_container_width=True, hide_index=True)
