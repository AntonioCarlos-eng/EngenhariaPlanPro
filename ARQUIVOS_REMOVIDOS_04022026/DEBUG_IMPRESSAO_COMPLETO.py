"""
DEBUG COMPLETO - Testar impressão step by step
"""
import os
import sys
sys.path.insert(0, r'c:\EngenhariaPlanPro')

print("=" * 80)
print("DEBUG: FLUXO COMPLETO DE IMPRESSÃO")
print("=" * 80)

# 1. Verificar arquivos DXF
print("\n[1] Verificando arquivos DXF...")
dxf_dir = r'c:\EngenhariaPlanPro\dxf'
dxf_files = [f for f in os.listdir(dxf_dir) if f.lower().endswith('.dxf')][:1]
if dxf_files:
    arquivo_teste = os.path.join(dxf_dir, dxf_files[0])
    print(f"✅ Arquivo teste: {arquivo_teste}")
else:
    print("❌ Nenhum DXF encontrado!")
    sys.exit(1)

# 2. Testar GeradorEtiquetasDinamico
print("\n[2] Testando GeradorEtiquetasDinamico...")
try:
    from core.etiquetas_generator import GeradorEtiquetasDinamico
    gerador = GeradorEtiquetasDinamico([arquivo_teste])
    print(f"✅ Gerador criado")
    print(f"   Dados carregados: {len(gerador.dados)}")
except Exception as e:
    print(f"❌ Erro ao criar gerador: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 3. Testar gerar_dados_etiqueta
print("\n[3] Testando gerar_dados_etiqueta...")
try:
    if len(gerador.dados) > 0:
        dados = gerador.gerar_dados_etiqueta(0)
        print(f"✅ Dados gerados para primeira etiqueta:")
        print(f"   Viga: {dados.get('viga', 'N/A')}")
        print(f"   Pos: {dados.get('pos', 'N/A')}")
        print(f"   OS: {dados.get('os_num', 'N/A')}")
        print(f"   Desenho: {'Sim' if dados.get('caminho_desenho') else 'Não'}")
        print(f"   Barcode: {'Sim' if dados.get('barcode_img') else 'Não'}")
    else:
        print("❌ Nenhum dado no gerador!")
        sys.exit(1)
except Exception as e:
    print(f"❌ Erro ao gerar dados: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 4. Testar geração de etiqueta PNG
print("\n[4] Testando geração de PNG...")
try:
    caminho_png = gerador.gerar_etiqueta_png(0)
    if caminho_png and os.path.exists(caminho_png):
        tamanho = os.path.getsize(caminho_png) / 1024
        print(f"✅ PNG gerado: {caminho_png}")
        print(f"   Tamanho: {tamanho:.1f} KB")
        
        # Verificar se não é branco
        from PIL import Image
        img = Image.open(caminho_png)
        print(f"   Dimensões: {img.size}")
        print(f"   Modo: {img.mode}")
    else:
        print("❌ PNG não foi gerado!")
        sys.exit(1)
except Exception as e:
    print(f"❌ Erro ao gerar PNG: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 5. Listar impressoras
print("\n[5] Testando listagem de impressoras...")
try:
    impressoras = GeradorEtiquetasDinamico.listar_impressoras_disponiveis()
    print(f"✅ Impressoras encontradas: {len(impressoras)}")
    for imp in impressoras:
        print(f"   - {imp}")
    
    padrao = GeradorEtiquetasDinamico.obter_impressora_padrao()
    print(f"✅ Impressora padrão: {padrao}")
except Exception as e:
    print(f"❌ Erro ao listar impressoras: {e}")
    import traceback
    traceback.print_exc()

# 6. Testar comando print do Windows
print("\n[6] Testando comando print do Windows...")
try:
    import subprocess
    
    # Teste com arquivo temporário
    test_file = caminho_png
    teste_cmd = ['cmd', '/c', 'print', f'/D:"{padrao}"', test_file]
    print(f"   Comando: {' '.join(teste_cmd)}")
    
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    result = subprocess.run(
        teste_cmd,
        check=False,
        shell=False,
        capture_output=True,
        text=True,
        creationflags=creationflags
    )
    
    print(f"   Return code: {result.returncode}")
    if result.stdout:
        print(f"   Stdout: {result.stdout.strip()}")
    if result.stderr:
        print(f"   Stderr: {result.stderr.strip()}")
    
    if result.returncode == 0:
        print("✅ Comando print funcionou!")
    else:
        print("❌ Comando print retornou erro!")
        
except Exception as e:
    print(f"❌ Erro ao testar print: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("DEBUG CONCLUÍDO")
print("=" * 80)
