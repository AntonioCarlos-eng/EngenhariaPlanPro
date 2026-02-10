"""
Script de teste - Listar impressoras disponíveis
"""

print("=" * 70)
print("TESTE: Listar Impressoras Disponíveis")
print("=" * 70)

try:
    from core.etiquetas_generator import GeradorEtiquetasDinamico
    
    print("\n1️⃣ Listando impressoras...")
    impressoras = GeradorEtiquetasDinamico.listar_impressoras_disponiveis()
    print(f"\n✅ Encontradas {len(impressoras)} impressora(s):")
    for i, imp in enumerate(impressoras, 1):
        print(f"   {i}. {imp}")
    
    print("\n2️⃣ Obtendo impressora padrão...")
    padrao = GeradorEtiquetasDinamico.obter_impressora_padrao()
    print(f"✅ Impressora padrão: {padrao}")
    
    print("\n" + "=" * 70)
    print("✅ Teste concluído!")
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
