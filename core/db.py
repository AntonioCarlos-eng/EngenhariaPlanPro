# db/db.py – Banco de Dados V8.4 Premium
# ---------------------------------------
# Tabelas:
#   romaneios(id, data, obra, etapa, plano, tipo, total_peso, total_barras, texto)
#   arquivos_romaneio(romaneio_id, arquivo)
#
# Todas compatíveis com app_gui.py V8.3/V8.4

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.getcwd(), "engenharia_planpro.db")


# ---------------------------------------------------------
# Inicialização
# ---------------------------------------------------------
def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Tabela principal
    cur.execute("""
        CREATE TABLE IF NOT EXISTS romaneios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            obra TEXT,
            etapa TEXT,
            plano TEXT,
            tipo TEXT,
            total_peso REAL,
            total_barras INTEGER,
            texto TEXT
        )
    """)

    # Arquivos ligados ao romaneio
    cur.execute("""
        CREATE TABLE IF NOT EXISTS arquivos_romaneio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            romaneio_id INTEGER,
            arquivo TEXT,
            FOREIGN KEY (romaneio_id) REFERENCES romaneios(id)
        )
    """)

    conn.commit()
    conn.close()


# ---------------------------------------------------------
# SALVAR ROMANEIO
# ---------------------------------------------------------
def salvar_romaneio(obra, etapa, plano, tipo, arquivos, barras, texto):
    total_peso = sum([b["peso"] for b in barras])
    total_barras = sum([b["qt"] for b in barras])

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    data = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    cur.execute("""
        INSERT INTO romaneios (data, obra, etapa, plano, tipo, total_peso, total_barras, texto)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (data, obra, etapa, plano, tipo, total_peso, total_barras, texto))

    rom_id = cur.lastrowid

    # Salvar arquivos utilizados
    for arq in arquivos:
        cur.execute("""
            INSERT INTO arquivos_romaneio (romaneio_id, arquivo)
            VALUES (?, ?)
        """, (rom_id, arq))

    conn.commit()
    conn.close()
    return rom_id


# ---------------------------------------------------------
# LISTAR ROMANEIOS
# ---------------------------------------------------------
def listar_romaneios(obra=None, plano=None, tipo=None):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    query = "SELECT * FROM romaneios WHERE 1=1"
    params = []

    if obra:
        query += " AND obra LIKE ?"
        params.append(f"%{obra}%")

    if plano:
        query += " AND plano LIKE ?"
        params.append(f"%{plano}%")

    if tipo:
        query += " AND tipo = ?"
        params.append(tipo)

    query += " ORDER BY id DESC"

    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return rows


# ---------------------------------------------------------
# CARREGAR ROMANEIO POR ID
# ---------------------------------------------------------
def carregar_romaneio(rom_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT * FROM romaneios WHERE id = ?", (rom_id,))
    row = cur.fetchone()

    if not row:
        conn.close()
        return None

    cur.execute("SELECT arquivo FROM arquivos_romaneio WHERE romaneio_id = ?", (rom_id,))
    arquivos = [r["arquivo"] for r in cur.fetchall()]

    conn.close()

    return {
        "id": row["id"],
        "data": row["data"],
        "obra": row["obra"],
        "etapa": row["etapa"],
        "plano": row["plano"],
        "tipo": row["tipo"],
        "total_peso": row["total_peso"],
        "total_barras": row["total_barras"],
        "texto": row["texto"],
        "arquivos": arquivos,
    }
