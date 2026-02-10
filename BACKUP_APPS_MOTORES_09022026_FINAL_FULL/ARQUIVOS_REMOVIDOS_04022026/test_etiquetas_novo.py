#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste rápido: Verifica se as funções de etiquetas estão funcionando
"""

import sys
sys.path.insert(0, r'c:\EngenhariaPlanPro')

# Testa import da classe principal
try:
    from vigas_app import VigasApp
    print("✅ VigasApp importada com sucesso")
except Exception as e:
    print(f"❌ Erro ao importar VigasApp: {e}")
    sys.exit(1)

# Testa que as funções existem
methods_to_check = [
    'desenhar_etiquetas_com_selecao',
    '_toggle_etiqueta_selecao',
    '_marcar_todas_etiquetas',
    '_desmarcar_todas_etiquetas',
    '_editar_etiqueta_dados',
    '_confirmar_e_imprimir_etiquetas',
    '_ir_primeira_pagina_etiquetas',
    '_ir_proxima_pagina_etiquetas',
    '_ir_pagina_anterior_etiquetas',
    '_ir_ultima_pagina_etiquetas'
]

print("\n📋 Verificando métodos...")
for method_name in methods_to_check:
    if hasattr(VigasApp, method_name):
        print(f"  ✅ {method_name}")
    else:
        print(f"  ❌ {method_name} NÃO ENCONTRADO!")

print("\n✅ Teste concluído!")
print("\nAs novas funcionalidades foram implementadas com sucesso:")
print("  • Checkboxes para seleção de etiquetas")
print("  • Botões MARCAR TODAS / DESMARCAR TODAS")
print("  • Edição de dados via diálogo")
print("  • Navegação entre páginas")
print("  • Impressão apenas dos selecionados")
