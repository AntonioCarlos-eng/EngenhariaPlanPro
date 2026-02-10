"""
LIMPAR_PNGS_ANTIGOS.py
----------------------
SOLUÇÃO: Apagar todos os PNGs antigos que estão atrapalhando
"""

import os
import shutil
from pathlib import Path

def limpar_pngs_antigos():
    """Apaga todos os PNGs de etiquetas antigas"""
    
    pastas_para_limpar = [
        "etiquetas",
        "output/etiquetas",
        "etiquetas_teste",
        "temp_print"
    ]
    
    total_apagados = 0
    
    print("\n" + "="*70)
    print("LIMPANDO PNGs ANTIGOS")
    print("="*70 + "\n")
    
    for pasta in pastas_para_limpar:
        if os.path.exists(pasta):
            print(f"📁 Verificando: {pasta}")
            
            # Listar PNGs
            pngs = [f for f in os.listdir(pasta) if f.endswith('.png')]
            
            if pngs:
                print(f"   Encontrados: {len(pngs)} PNG(s)")
                
                # Apagar cada PNG
                for png in pngs:
                    caminho = os.path.join(pasta, png)
                    try:
                        os.remove(caminho)
                        total_apagados += 1
                        print(f"   ✅ Apagado: {png}")
                    except Exception as e:
                        print(f"   ❌ Erro ao apagar {png}: {e}")
            else:
                print(f"   ℹ️ Nenhum PNG encontrado")
        else:
            print(f"📁 Pasta não existe: {pasta}")
    
    print("\n" + "="*70)
    print(f"✅ LIMPEZA CONCLUÍDA!")
    print(f"📊 Total de PNGs apagados: {total_apagados}")
    print("="*70)
    print("\n💡 PRÓXIMO PASSO:")
    print("   1. Execute o vigas_app.py")
    print("   2. Processe os arquivos DXF")
    print("   3. Abra o Editor e faça suas edições")
    print("   4. Clique em 'Imprimir'")
    print("   5. Os PNGs serão gerados NOVOS com suas edições!")
    print("="*70 + "\n")

if __name__ == "__main__":
    limpar_pngs_antigos()
