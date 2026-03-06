import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

import pandas as pd

from crm.config import DB_PATH


def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@contextmanager
def get_connection():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.commit()
        conn.close()


def init_db():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                segment TEXT,
                cnpj TEXT,
                site TEXT,
                main_unit TEXT,
                strategic_status TEXT,
                notes TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER,
                name TEXT NOT NULL,
                role TEXT,
                email TEXT,
                phone TEXT,
                influence_level TEXT,
                notes TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(account_id) REFERENCES accounts(id)
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS opportunities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                opportunity_name TEXT NOT NULL,
                internal_code TEXT,
                account_id INTEGER,
                unit_asset TEXT,
                segment TEXT,
                lead_source TEXT,
                service_type TEXT,
                main_discipline TEXT,
                involved_disciplines TEXT,
                nature TEXT,
                project_phase TEXT,
                location_type TEXT,
                scope_summary TEXT,
                client_objective TEXT,
                key_deliverables TEXT,
                critical_assumptions TEXT,
                information_gaps TEXT,
                needs_site_visit INTEGER DEFAULT 0,
                needs_technical_meeting INTEGER DEFAULT 0,
                needs_nda INTEGER DEFAULT 0,
                needs_contract_draft INTEGER DEFAULT 0,
                needs_registration INTEGER DEFAULT 0,
                estimated_value REAL DEFAULT 0,
                estimated_hh REAL DEFAULT 0,
                target_margin REAL DEFAULT 0,
                probability INTEGER DEFAULT 0,
                proposal_deadline TEXT,
                execution_deadline TEXT,
                commercial_owner TEXT,
                proposal_owner TEXT,
                technical_coordinator TEXT,
                approving_director TEXT,
                next_step TEXT,
                next_step_date TEXT,
                current_blocker TEXT,
                mapped_competitor TEXT,
                loss_reason TEXT,
                stage TEXT NOT NULL,
                go_no_go_status TEXT DEFAULT 'Em análise',
                risk_level TEXT DEFAULT 'Médio',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(account_id) REFERENCES accounts(id)
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS proposals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                opportunity_id INTEGER NOT NULL,
                revision_number INTEGER NOT NULL,
                version_label TEXT,
                proposal_value REAL DEFAULT 0,
                sent_date TEXT,
                validity_days INTEGER DEFAULT 30,
                execution_deadline TEXT,
                status TEXT DEFAULT 'Rascunho',
                objective_text TEXT,
                service_description TEXT,
                assumptions_text TEXT,
                exclusions_text TEXT,
                deliverables_text TEXT,
                hh_summary TEXT,
                pricing_notes TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(opportunity_id) REFERENCES opportunities(id)
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                related_type TEXT NOT NULL,
                related_id INTEGER NOT NULL,
                activity_type TEXT NOT NULL,
                description TEXT NOT NULL,
                owner TEXT NOT NULL,
                due_date TEXT,
                status TEXT DEFAULT 'Aberta',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS stage_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                opportunity_id INTEGER NOT NULL,
                old_stage TEXT,
                new_stage TEXT NOT NULL,
                note TEXT,
                changed_at TEXT NOT NULL,
                FOREIGN KEY(opportunity_id) REFERENCES opportunities(id)
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS library_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)


def fetch_df(query: str, params=()):
    with get_connection() as conn:
        return pd.read_sql_query(query, conn, params=params)


def fetch_all(table: str):
    return fetch_df(f"SELECT * FROM {table} ORDER BY id DESC")


def fetch_by_id(table: str, row_id: int):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM {table} WHERE id = ?", (row_id,))
        row = cur.fetchone()
        return dict(row) if row else None


def insert_record(table: str, data: dict) -> int:
    keys = list(data.keys())
    values = [data[k] for k in keys]
    placeholders = ", ".join(["?"] * len(keys))
    query = f"INSERT INTO {table} ({', '.join(keys)}) VALUES ({placeholders})"
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(query, values)
        return cur.lastrowid


def update_record(table: str, row_id: int, data: dict):
    keys = list(data.keys())
    values = [data[k] for k in keys]
    set_clause = ", ".join([f"{k} = ?" for k in keys])
    query = f"UPDATE {table} SET {set_clause} WHERE id = ?"
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(query, values + [row_id])
