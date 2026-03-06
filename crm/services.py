from datetime import date, timedelta

import pandas as pd

from crm.config import LOSS_REASONS, OPEN_STAGES, PIPELINE_STAGES, STAGE_PROBABILITIES
from crm.database import fetch_all, fetch_df, insert_record, now_str, update_record


def pipeline_index(stage: str) -> int:
    try:
        return PIPELINE_STAGES.index(stage)
    except ValueError:
        return 999


def save_account(payload: dict, record_id: int | None = None) -> int:
    payload["updated_at"] = now_str()
    if record_id:
        update_record("accounts", record_id, payload)
        return record_id
    payload["created_at"] = now_str()
    return insert_record("accounts", payload)


def save_contact(payload: dict, record_id: int | None = None) -> int:
    payload["updated_at"] = now_str()
    if record_id:
        update_record("contacts", record_id, payload)
        return record_id
    payload["created_at"] = now_str()
    return insert_record("contacts", payload)


def save_opportunity(payload: dict, record_id: int | None = None, previous_stage: str | None = None) -> int:
    payload["updated_at"] = now_str()
    payload["probability"] = int(payload.get("probability") or STAGE_PROBABILITIES.get(payload.get("stage"), 0))
    if payload.get("stage") == "Perdida" and not payload.get("loss_reason"):
        payload["loss_reason"] = "Outro, com justificativa"
    if record_id:
        update_record("opportunities", record_id, payload)
        current_id = record_id
    else:
        payload["created_at"] = now_str()
        current_id = insert_record("opportunities", payload)
        previous_stage = None
    new_stage = payload["stage"]
    if previous_stage != new_stage:
        insert_record("stage_history", {"opportunity_id": current_id, "old_stage": previous_stage, "new_stage": new_stage, "note": f"Alteração automática para {new_stage}", "changed_at": now_str()})
        create_stage_automation(current_id, new_stage)
    return current_id


def next_revision_number(opportunity_id: int) -> int:
    df = fetch_df("SELECT COALESCE(MAX(revision_number), 0) AS rev FROM proposals WHERE opportunity_id = ?", (opportunity_id,))
    return int(df.iloc[0]["rev"]) + 1 if not df.empty else 1


def save_proposal(payload: dict, record_id: int | None = None) -> int:
    payload["updated_at"] = now_str()
    if record_id:
        update_record("proposals", record_id, payload)
        return record_id
    payload["created_at"] = now_str()
    return insert_record("proposals", payload)


def save_activity(payload: dict, record_id: int | None = None) -> int:
    payload["updated_at"] = now_str()
    if record_id:
        update_record("activities", record_id, payload)
        return record_id
    payload["created_at"] = now_str()
    return insert_record("activities", payload)


def save_library_item(payload: dict, record_id: int | None = None) -> int:
    payload["updated_at"] = now_str()
    if record_id:
        update_record("library_items", record_id, payload)
        return record_id
    payload["created_at"] = now_str()
    return insert_record("library_items", payload)


def create_stage_automation(opportunity_id: int, stage: str):
    templates = {
        "Entendimento do escopo": ("Análise TR/RFQ", "Solicitar TR/RFQ, validar escopo, mapear disciplinas e lacunas de informação.", 2),
        "Go / No-Go interno": ("Validação interna", "Consolidar aderência, risco, capacidade interna e decisão Go / No-Go.", 2),
        "Em elaboração de proposta": ("Revisão de proposta", "Consolidar HH, LD, premissas, fora de escopo, valor e aprovadores internos.", 3),
        "Proposta enviada": ("Follow-up", "Executar follow-up comercial pós-envio da proposta e registrar feedback do cliente.", 7),
        "Em negociação": ("Jurídico / minuta", "Alinhar pontos técnicos, comerciais e minuta contratual com interfaces internas.", 3),
        "Aguardando decisão do cliente": ("Follow-up", "Registrar checkpoint com cliente e avaliar risco de aging / perda.", 5),
    }
    if stage not in templates:
        return
    activity_type, description, days = templates[stage]
    due_date = (date.today() + timedelta(days=days)).isoformat()
    insert_record("activities", {"related_type": "opportunity", "related_id": opportunity_id, "activity_type": activity_type, "description": description, "owner": "Comercial", "due_date": due_date, "status": "Aberta", "created_at": now_str(), "updated_at": now_str()})


def dashboard_snapshot() -> dict:
    opps = fetch_df("SELECT o.*, a.name AS account_name FROM opportunities o LEFT JOIN accounts a ON a.id = o.account_id")
    activities = fetch_all("activities")
    proposals = fetch_all("proposals")
    if opps.empty:
        opps = pd.DataFrame(columns=["estimated_value", "probability", "stage", "created_at", "next_step_date", "segment", "loss_reason"])
    opps["estimated_value"] = pd.to_numeric(opps.get("estimated_value"), errors="coerce").fillna(0)
    opps["probability"] = pd.to_numeric(opps.get("probability"), errors="coerce").fillna(0)
    opps["weighted_value"] = opps["estimated_value"] * opps["probability"] / 100
    open_opps = opps[opps["stage"].isin(OPEN_STAGES)] if not opps.empty else opps
    overdue = pd.DataFrame()
    if not activities.empty and "due_date" in activities.columns:
        activities["due_date"] = pd.to_datetime(activities["due_date"], errors="coerce")
        overdue = activities[(activities["status"] != "Concluída") & (activities["due_date"] < pd.Timestamp.today().normalize())]
    wins = int((opps["stage"] == "Ganha").sum()) if not opps.empty else 0
    losses = int((opps["stage"] == "Perdida").sum()) if not opps.empty else 0
    closed = wins + losses
    win_rate = (wins / closed * 100) if closed else 0
    return {"open_pipeline_value": float(open_opps["estimated_value"].sum()) if not open_opps.empty else 0, "weighted_pipeline_value": float(open_opps["weighted_value"].sum()) if not open_opps.empty else 0, "open_opportunities": int(len(open_opps)), "win_rate": float(win_rate), "overdue_activities": int(len(overdue)), "proposals_total": int(len(proposals)), "opportunities_df": opps, "activities_df": activities, "proposals_df": proposals}


def opportunities_table() -> pd.DataFrame:
    df = fetch_df("SELECT o.*, a.name AS account_name FROM opportunities o LEFT JOIN accounts a ON a.id = o.account_id ORDER BY o.updated_at DESC")
    if df.empty:
        return df
    df["estimated_value"] = pd.to_numeric(df["estimated_value"], errors="coerce").fillna(0)
    df["probability"] = pd.to_numeric(df["probability"], errors="coerce").fillna(0)
    df["weighted_value"] = df["estimated_value"] * df["probability"] / 100
    df["stage_order"] = df["stage"].apply(pipeline_index)
    return df.sort_values(["stage_order", "updated_at"], ascending=[True, False])


def proposals_table() -> pd.DataFrame:
    return fetch_df("SELECT p.*, o.opportunity_name, o.stage AS opportunity_stage FROM proposals p INNER JOIN opportunities o ON o.id = p.opportunity_id ORDER BY p.updated_at DESC")


def activities_table() -> pd.DataFrame:
    return fetch_df("SELECT * FROM activities ORDER BY CASE status WHEN 'Aberta' THEN 0 WHEN 'Em andamento' THEN 1 ELSE 2 END, due_date ASC, updated_at DESC")


def accounts_lookup():
    df = fetch_all("accounts")
    return [] if df.empty else [(int(r["id"]), r["name"]) for _, r in df.sort_values("name").iterrows()]


def opportunities_lookup():
    df = fetch_all("opportunities")
    return [] if df.empty else [(int(r["id"]), r["opportunity_name"]) for _, r in df.sort_values("opportunity_name").iterrows()]


def infer_probability_from_stage(stage: str) -> int:
    return int(STAGE_PROBABILITIES.get(stage, 0))


def opportunity_defaults() -> dict:
    return {"opportunity_name": "", "internal_code": "", "account_id": None, "unit_asset": "", "segment": "", "lead_source": "", "service_type": "", "main_discipline": "", "involved_disciplines": "", "nature": "", "project_phase": "", "location_type": "", "scope_summary": "", "client_objective": "", "key_deliverables": "", "critical_assumptions": "", "information_gaps": "", "needs_site_visit": 0, "needs_technical_meeting": 0, "needs_nda": 0, "needs_contract_draft": 0, "needs_registration": 0, "estimated_value": 0, "estimated_hh": 0, "target_margin": 0, "probability": 10, "proposal_deadline": None, "execution_deadline": None, "commercial_owner": "Comercial", "proposal_owner": "Engenharia", "technical_coordinator": "Engenharia", "approving_director": "Diretoria", "next_step": "", "next_step_date": None, "current_blocker": "", "mapped_competitor": "", "loss_reason": "", "stage": "Lead identificado", "go_no_go_status": "Em análise", "risk_level": "Médio"}


def account_contacts(account_id: int) -> pd.DataFrame:
    return fetch_df("SELECT * FROM contacts WHERE account_id = ? ORDER BY name", (account_id,))


def opportunity_history(opportunity_id: int) -> pd.DataFrame:
    return fetch_df("SELECT * FROM stage_history WHERE opportunity_id = ? ORDER BY changed_at DESC", (opportunity_id,))


def open_activities_for_opportunity(opportunity_id: int) -> pd.DataFrame:
    return fetch_df("SELECT * FROM activities WHERE related_type = 'opportunity' AND related_id = ? AND status != 'Concluída' ORDER BY due_date ASC", (opportunity_id,))
