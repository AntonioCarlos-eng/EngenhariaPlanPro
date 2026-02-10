"""
Debug: Simular o que _gerar_imagem_etiqueta recebe e processa
"""
import os

# Simular os dados que vêm de self.dados_processados
# Baseado na imagem: V8, N1, 10.00, 2, 2.950
dados_exemplo = [
    ('V8', 'N1', 10.00, 2, 2.950),
]

pasta_etiq = r"c:\EngenhariaPlanPro\etiquetas"

print("=" * 80)
print("DEBUG: Simulando _gerar_imagem_etiqueta")
print("=" * 80)

for idx, dado in enumerate(dados_exemplo):
    print(f"\n[Etiqueta {idx+1}]")
    print(f"  Dado recebido: {dado}")
    print(f"  Tipo: {type(dado)}")
    print(f"  Len: {len(dado)}")
    
    try:
        viga = str(dado[0])
        pos = str(dado[1])
        bitola = float(dado[2])
        qtde = int(dado[3])
        comp_m = float(dado[4])
        
        print(f"  ✓ Extração OK:")
        print(f"    - Viga: {viga} (type: {type(viga).__name__})")
        print(f"    - Pos: {pos} (type: {type(pos).__name__})")
        print(f"    - Bitola: {bitola} (type: {type(bitola).__name__})")
        print(f"    - Qtde: {qtde} (type: {type(qtde).__name__})")
        print(f"    - Comp_m: {comp_m} (type: {type(comp_m).__name__})")
        
        comp_cm = int(round(comp_m * 100))
        bitola_str = f"{bitola:.1f}"
        
        print(f"\n  Formatação:")
        print(f"    - Comp_cm: {comp_cm}")
        print(f"    - Bitola_str: {bitola_str}")
        
        # Padrão flexível
        target_pattern = f"_{viga}_{pos}_b{bitola_str}_q{qtde}_c{comp_cm}cm_"
        print(f"\n  Padrão de busca: *{target_pattern}*")
        
        # Procura
        encontrado = None
        if os.path.exists(pasta_etiq):
            print(f"\n  Procurando em: {pasta_etiq}")
            print(f"  Total de arquivos: {len(os.listdir(pasta_etiq))}")
            
            for arq in os.listdir(pasta_etiq):
                if arq.endswith('.png') and target_pattern in arq:
                    encontrado = os.path.join(pasta_etiq, arq)
                    print(f"\n  ✅ ENCONTRADO: {os.path.basename(encontrado)}")
                    break
            
            if not encontrado:
                print(f"\n  ❌ NÃO ENCONTRADO")
                # Debug: mostrar arquivos V8/N1 disponíveis
                v8n1_files = [f for f in os.listdir(pasta_etiq) if 'V8' in f and 'N1' in f and f.endswith('.png')]
                print(f"\n  Arquivos disponíveis com V8 e N1: {len(v8n1_files)}")
                for f in v8n1_files[:5]:
                    print(f"    - {f}")
                    # Mostrar se contém o padrão
                    if target_pattern in f:
                        print(f"      ✓ CONTÉM O PADRÃO!")
                    else:
                        print(f"      ✗ NÃO contém o padrão")
    
    except Exception as e:
        print(f"  ❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 80)
