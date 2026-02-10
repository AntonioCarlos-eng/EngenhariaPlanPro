import os
import shutil
from pathlib import Path

# Pasta principal
RAIZ = r"c:\EngenhariaPlanPro"
LIMPEZA = os.path.join(RAIZ, "ARQUIVOS_REMOVIDOS_04022026")

# Criar pasta de "lixo" (seguro)
os.makedirs(LIMPEZA, exist_ok=True)

# Padrões para REMOVER
REMOVER = [
    # Fix/Debug scripts
    "*fix_*.py",
    "*debug_*.py",
    "*test_*.py",
    "aplicar_*.py",
    "converter_*.py",
    "gera_*.py",
    "*analisar*.py",
    "simular_*.py",
    
    # Pastas temporárias
    "temp_*",
    "_temp_*",
    "VERSOES",
    "teste",
    "etiquetas_teste",
    "TEMP",
    "temp",
    
    # Motores obsoletos
    "core/vigas_motor.py",
    "core/vigas_motor_dxf*.py",
    "core/vigas_motor_old.py",
    "core/*_old.py",
    
    # Backups antigos (manter apenas o de hoje)
    "lajes_app_BACKUP_TEMP.py",
    "lajes_app_TEMP_FIX.py",
    "*_OLD.py",
    "*_backup*.py",
    "vigas_app_backup_*.py",
    "vigas_app_restaurado.py",
    
    # Análise temporária
    "lajes_dados_reais.py",
    "analise_*.py",
    "testar_*.py",
    "*amostra*.txt",
    "*analise*.txt",
]

# Manter (essencial)
MANTER = [
    "BACKUP_APPS_MOTORES_04022026",
    "vigas_app.py",
    "pilares_app.py", 
    "lajes_app.py",
    "abrir_lajes_app.py",
    "blocos_app.py",
]

print("🗑️  LIMPEZA DO PROJETO ENGENHARIAPLANNPRO")
print("=" * 60)

removidos_arquivo = []
removidos_pasta = []
total_liberado = 0

try:
    for pattern in REMOVER:
        # Se é arquivo
        if "*" in pattern and "/" not in pattern:
            from glob import glob
            for arquivo in glob(os.path.join(RAIZ, pattern)):
                nome = os.path.basename(arquivo)
                
                # Não remover se está na lista MANTER
                if any(m in nome for m in MANTER):
                    continue
                
                if os.path.isfile(arquivo):
                    try:
                        tamanho = os.path.getsize(arquivo)
                        shutil.move(arquivo, os.path.join(LIMPEZA, nome))
                        removidos_arquivo.append(nome)
                        total_liberado += tamanho
                        print(f"  ✓ {nome} ({tamanho/1024:.1f} KB)")
                    except Exception as e:
                        print(f"  ✗ Erro ao remover {nome}: {e}")
        
        # Se é pasta
        elif "/" in pattern:
            caminho = os.path.join(RAIZ, pattern.replace("/", ""))
            if os.path.isdir(caminho):
                try:
                    shutil.rmtree(caminho)
                    removidos_pasta.append(os.path.basename(caminho))
                    print(f"  ✓ Pasta: {os.path.basename(caminho)}/")
                except Exception as e:
                    print(f"  ✗ Erro ao remover pasta: {e}")
        
        # Se é pasta sem /*
        else:
            caminho = os.path.join(RAIZ, pattern)
            if os.path.isdir(caminho):
                try:
                    shutil.rmtree(caminho)
                    removidos_pasta.append(pattern)
                    print(f"  ✓ Pasta: {pattern}/")
                except Exception as e:
                    print(f"  ✗ Erro ao remover {pattern}: {e}")

    print("\n" + "=" * 60)
    print(f"📊 RESULTADO DA LIMPEZA:")
    print(f"  • Arquivos movidos: {len(removidos_arquivo)}")
    print(f"  • Pastas removidas: {len(removidos_pasta)}")
    print(f"  • Espaço liberado: {total_liberado / (1024**2):.2f} MB")
    print(f"  • Arquivos salvos em: {LIMPEZA}")
    print("=" * 60)
    print("✅ LIMPEZA CONCLUÍDA COM SUCESSO!")
    print("\n💾 Os arquivos removidos estão em:")
    print(f"   {LIMPEZA}")
    print("\n⚠️  Se precisar recuperar algo, copie de lá!")
    
except Exception as e:
    print(f"\n❌ ERRO CRÍTICO: {e}")
    import traceback
    traceback.print_exc()
