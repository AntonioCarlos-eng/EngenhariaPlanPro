# db/db.py - Funções de banco de dados
import sqlite3
import os
from datetime import datetime

def init_db():
    """Inicializa o banco de dados"""
    # Criar diretório db se não existir
    db_dir = os.path.dirname(os.path.abspath(__file__))
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    # Conectar ao banco
    db_path = os.path.join(db_dir, 'romaneios.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Criar tabela de romaneios se não existir
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS romaneios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_criacao TEXT,
            obra TEXT,
            plano TEXT,
            tipo TEXT,
            total_peso REAL,
            total_barras INTEGER,
            conteudo TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    
    print(f"[DB] Banco de dados inicializado em: {db_path}")
    return True