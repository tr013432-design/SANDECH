import streamlit as st

from crm.database import fetch_all, fetch_by_id
from crm.services import accounts_lookup, save_contact
from crm.ui import header, setup_page

setup_page("Contatos")
header("Contatos", "Gestão de stakeholders, influência na compra e dados de relacionamento.")

accounts = accounts_lookup()
account_labels = [""] + [name for _, name in accounts]
account_label_to_id = {name: _id for _id, name in accounts}

contacts = fetch_all("contacts")
contact_options = {f"{row['name']} (#{row['id']})": int(row["id"]) for _, row in contacts.iterrows()} if not contacts.empty else {}

mode = st.radio("Modo", ["Novo contato", "Editar contato"], horizontal=True)
selected_id = None
record = None
if mode == "Editar contato" and contact_options:
    selected_label = st.selectbox("Contato", options=list(contact_options.keys()))
    selected_id = contact_options[selected_label]
    record = fetch_by_id("contacts", selected_id)

with st.form("contact_form"):
    c1, c2 = st.columns(2)
    name = c1.text_input("Nome", value=record["name"] if record else "")
    account_name = c2.selectbox("Conta", account_labels, index=account_labels.index(next((name for _id, name in accounts if record and _id == record["account_id"]), "")) if record else 0)
    c3, c4, c5 = st.columns(3)
    role = c3.text_input("Cargo", value=record["role"] if record else "")
    email = c4.text_input("E-mail", value=record["email"] if record else "")
    phone = c5.text_input("Telefone", value=record["phone"] if record else "")
    c6, c7 = st.columns(2)
    influence_level = c6.selectbox("Influência na compra", ["", "Decisor", "Influenciador", "Usuário técnico", "Compras", "Patrocinador"], index=["", "Decisor", "Influenciador", "Usuário técnico", "Compras", "Patrocinador"].index(record["influence_level"]) if record and record["influence_level"] in ["", "Decisor", "Influenciador", "Usuário técnico", "Compras", "Patrocinador"] else 0)
    notes = c7.text_input("Observação rápida", value=record["notes"] if record else "")
    submitted = st.form_submit_button("Salvar contato", type="primary")
    if submitted:
        save_contact({"account_id": account_label_to_id.get(account_name), "name": name, "role": role, "email": email, "phone": phone, "influence_level": influence_level, "notes": notes}, record_id=selected_id)
        st.success("Contato salvo com sucesso.")
        st.rerun()

st.markdown("### Base de contatos")
if contacts.empty:
    st.info("Sem contatos cadastrados.")
else:
    st.dataframe(contacts[["id", "account_id", "name", "role", "email", "phone", "influence_level", "updated_at"]], use_container_width=True, hide_index=True)
