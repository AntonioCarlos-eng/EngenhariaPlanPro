#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
teste_log.py - Escreve resultado em arquivo
"""

import sys
import os

os.chdir(r'c:\EngenhariaPlanPro')

from core.desenho_extractor import localizar_desenho_viga_no_dxf

with open('teste_debug.log', 'w', encoding='utf-8') as f:
    f.write("INICIANDO TESTE\n")
    f.write(f"CWD: {os.getcwd()}\n")
    
    try:
        f.write("Importação OK\n")
        f.flush()
        
        dxf_path = r"dxf\vig terreo f 1-R2 - Copia.DXF"
        f.write(f"DXF path: {dxf_path}\n")
        f.write(f"DXF exists: {os.path.exists(dxf_path)}\n")
        f.flush()
        
        f.write("Chamando localizar_desenho_viga_no_dxf...\n")
        f.flush()
        
        img = localizar_desenho_viga_no_dxf(dxf_path, 'V8', 'N1', 220, 170)
        
        if img:
            f.write(f"✅ Imagem gerada: {img.size}\n")
            img.save("teste_log_v8_n1.png")
            f.write("   Salvo em: teste_log_v8_n1.png\n")
        else:
            f.write("❌ Retornou None\n")
        
        f.flush()
    
    except Exception as e:
        f.write(f"ERROR: {e}\n")
        import traceback
        f.write(traceback.format_exc())
        f.flush()

print("Teste escrito em teste_debug.log")
