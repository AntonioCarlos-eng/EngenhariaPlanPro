#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de teste para verificar se a aplicação funciona
"""

import sys
import os

try:
    print("[TEST] Importando vigas_app...")
    import vigas_app
    print("[✓] vigas_app importado com sucesso!")
    
    print("[TEST] Iniciando aplicação...")
    app = vigas_app.App()
    print("[✓] Aplicação iniciada!")
    
except Exception as e:
    print(f"[✗] ERRO: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
