"""
Script para abrir o arquivo de log de impressão
"""

import os
import time

log_file = "output/impressao/log_impressao.txt"

if os.path.exists(log_file):
    print(f"📄 Abrindo log de impressão: {log_file}\n")
    print("=" * 80)
    with open(log_file, 'r', encoding='utf-8') as f:
        print(f.read())
    print("=" * 80)
else:
    print(f"❌ Arquivo de log não encontrado: {log_file}")
    print("\nExecute o vigas_app.py, faça uma impressão e volte aqui.")
