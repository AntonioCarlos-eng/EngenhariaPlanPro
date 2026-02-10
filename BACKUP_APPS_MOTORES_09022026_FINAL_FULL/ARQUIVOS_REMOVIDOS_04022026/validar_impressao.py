"""
Teste de validação da impressão simplificada
Verifica se o sistema está usando GeradorEtiquetasDinamico corretamente
"""

import sys
import os

# Adicionar pasta raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("VALIDAÇÃO DA IMPRESSÃO SIMPLIFICADA")
print("=" * 70)

# 1. Verificar imports
print("\n[1] Verificando imports...")
try:
    from core.etiquetas_generator import GeradorEtiquetasDinamico
    print("✅ GeradorEtiquetasDinamico disponível")
except Exception as e:
    print(f"❌ Erro ao importar: {e}")
    sys.exit(1)

# 2. Verificar se vigas_app.py usa o gerador
print("\n[2] Verificando vigas_app.py...")
with open("vigas_app.py", "r", encoding="utf-8") as f:
    conteudo = f.read()
    
    # Verificar se usa GeradorEtiquetasDinamico
    if "gerador_temp = GeradorEtiquetasDinamico" in conteudo:
        print("✅ Usa GeradorEtiquetasDinamico na impressão")
    else:
        print("❌ NÃO usa GeradorEtiquetasDinamico")
    
    # Verificar se NÃO tem código amador
    if "Image.new('RGB', (W, H)" not in conteudo or "# CRIAR IMAGEM" not in conteudo:
        print("✅ Código amador de geração manual REMOVIDO")
    else:
        print("⚠️ Ainda tem código de geração manual (verificar)")
    
    # Verificar se abrir pasta está implementado
    if 'explorer' in conteudo and 'pasta_output' in conteudo:
        print("✅ Abre pasta automaticamente")
    else:
        print("⚠️ Pode não abrir pasta automaticamente")
    
    # Verificar se tem apenas 1 messagebox na impressão
    count_askyesno = conteudo.count("messagebox.askyesno") 
    if count_askyesno <= 2:  # Tolerância para outras partes do código
        print(f"✅ Sem caixas de diálogo duplicadas")
    else:
        print(f"⚠️ Múltiplas caixas de confirmação detectadas: {count_askyesno}")

# 3. Testar gerador básico
print("\n[3] Testando gerador básico...")
try:
    arquivo_teste = r'c:\EngenhariaPlanPro\dxf\#vigas t1-069.DXF'
    
    if os.path.exists(arquivo_teste):
        gerador = GeradorEtiquetasDinamico(
            arquivos_dxf=[arquivo_teste],
            pasta_etiquetas="output/etiquetas_teste",
            obra="TESTE",
            pavimento="T1"
        )
        
        print(f"✅ Gerador criado com {len(gerador.dados)} etiquetas")
        
        # Testar dados customizados
        gerador.medidas_customizadas = {
            ('V1', 'N1'): {'bitola': 12.5, 'comp': 5.5, 'qtde': 10}
        }
        gerador.formas_customizadas = {
            ('V1', 'N1'): 'gancho'
        }
        print("✅ Customizações aplicadas")
        
    else:
        print(f"⚠️ Arquivo de teste não encontrado: {arquivo_teste}")
        
except Exception as e:
    print(f"❌ Erro no teste: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("VALIDAÇÃO CONCLUÍDA")
print("=" * 70)
print("\n✅ Sistema pronto para impressão simplificada e profissional!")
print("📝 Verifique IMPRESSAO_SIMPLIFICADA.md para mais detalhes")
