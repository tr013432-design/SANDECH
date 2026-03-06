import streamlit as st

from crm.config import LIBRARY_CATEGORIES
from crm.database import fetch_all, fetch_by_id
from crm.services import save_library_item
from crm.ui import header, setup_page

setup_page("Biblioteca")
header("Biblioteca comercial / técnica", "Premissas, exclusões, modelos e referências para acelerar propostas com proteção de escopo.")

items = fetch_all("library_items")
existing = {f"{row['category']} | {row['title']} (#{int(row['id'])})": int(row["id"]) for _, row in items.iterrows()} if not items.empty else {}
mode = st.radio("Modo", ["Novo item", "Editar item"], horizontal=True)
record = None
record_id = None
if mode == "Editar item" and existing:
    label = st.selectbox("Item", list(existing.keys()))
    record_id = existing[label]
    record = fetch_by_id("library_items", record_id)

with st.form("library_form"):
    category = st.selectbox("Categoria", LIBRARY_CATEGORIES, index=LIBRARY_CATEGORIES.index(record["category"]) if record and record["category"] in LIBRARY_CATEGORIES else 0)
    title = st.text_input("Título", value=record["title"] if record else "")
    content = st.text_area("Conteúdo", value=record["content"] if record else "", height=180)
    submitted = st.form_submit_button("Salvar item", type="primary")
    if submitted:
        save_library_item({"category": category, "title": title, "content": content}, record_id=record_id)
        st.success("Item salvo com sucesso.")
        st.rerun()

st.markdown("### Base da biblioteca")
if items.empty:
    st.info("Sem itens cadastrados.")
else:
    selected_category = st.selectbox("Filtrar categoria", ["Todas"] + LIBRARY_CATEGORIES)
    view = items.copy()
    if selected_category != "Todas":
        view = view[view["category"] == selected_category]
    st.dataframe(view[["id", "category", "title", "updated_at"]], use_container_width=True, hide_index=True)
    st.markdown("### Conteúdo")
    for _, row in view.iterrows():
        with st.expander(f"{row['category']} | {row['title']}"):
            st.write(row["content"])
