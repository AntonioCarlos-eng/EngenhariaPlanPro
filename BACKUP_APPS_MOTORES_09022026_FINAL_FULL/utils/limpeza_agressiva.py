import os
import shutil
from pathlib import Path

RAIZ = r"c:\EngenhariaPlanPro"
LIMPEZA = os.path.join(RAIZ, "ARQUIVOS_REMOVIDOS_04022026")
DOCS = os.path.join(RAIZ, "docs")
EXEMPLOS = os.path.join(RAIZ, "exemplos")

# Criar pastas
os.makedirs(LIMPEZA, exist_ok=True)
os.makedirs(DOCS, exist_ok=True)
os.makedirs(EXEMPLOS, exist_ok=True)

print("🗑️  LIMPEZA AGRESSIVA DO PROJETO")
print("=" * 70)

# Arquivos a REMOVER
REMOVER = [
    "add_corpo_display.py", "adicionar_aviso.py", "busca_posicoes_v10.py",
    "correcao_divisao.py", "CORRECAO_FINAL_REGERAR_PNGS.py", "CORRECAO_ORDEM_FINAL.py",
    "corrigir_dobra_dupla.py", "corrigir_preview.py", "criar_banco_desenhos.py",
    "DEMO_CHECKBOXES_VISUAL.py", "demo_nomenclatura_expandida.py", "diagnostico_bbox.py",
    "encontrar_coluna_pos.py", "encontrar_n57_completo.py", "etiqueta_impressao_png.py",
    "exemplo_integracao_completa.py", "extrair_desenhos_auto.py", "FLUXO_COMPLETO.py",
    "gerar_desenhos_vigas.py", "gerar_pngs_simples.py", "IMPLEMENTAR_OPCAO_A.py",
    "ler_arquivo_original.py", "ler_dwg_oda.py", "limpar_formato.py",
    "LIMPAR_PNGS_ANTIGOS.py", "main.py", "motor_pilares.py", "nova_funcao_editar.py",
    "novo_preview.py", "PASSO7_TESTES_FINAIS.py", "PATCH_CORRECAO_PREVIEW.py",
    "process_tokens_local.py", "process_tokens_local_v2.py", "processa_sujo.py",
    "processar_l1_020.py", "refinar_campos_dobra.py", "REVERTER_E_CORRIGIR.py",
    "SOLUCAO_DEFINITIVA_FINAL.py", "teste_agrupamento_gerador.py", "teste_carregar_etiqueta.py",
    "teste_completo_integrado.py", "teste_etiquetas_dinamico.py", "teste_extracao_direto.py",
    "teste_extracao_n8.py", "teste_extracao_real.py", "teste_fluxo_desenho.py",
    "teste_fluxo_etiquetas.py", "teste_imports.py", "teste_impressao.py",
    "teste_impressao_auto.py", "teste_impressao_direta.py", "teste_impressoras.py",
    "teste_integracao_completa.py", "teste_leitura_dxf.py", "teste_leitura_pilares.py",
    "teste_log.py", "teste_motor_pilares.py", "teste_novo_motor.py",
    "teste_numeracao_logica.py", "teste_png_integracao.py", "teste_png_integracao_real.py",
    "teste_rapido.py", "teste_simplificacao.py", "update_preview.py",
    "validar_impressao.py", "ver_log.py", "verifica_final.py",
    "VERIFICACAO_IMPLEMENTACAO.py", "verificar_ultimas_linhas.py", "gerar_romaneio_final.py",
]

# Arquivos duplicados a mover
DUPLICADOS = [
    "lajes_app_CORRIGIDO_04FEV.py",
    "lajes_app_PONTO_ATUAL.py", 
    "lajes_app_TEMP_FIX.py",
    "vigas_app_restaurado.py",
]

# Arquivos a reorganizar
REORGANIZAR = {
    "lajes_app_metodos_etiquetas.py": DOCS,
    "lajes_dados_reais.py": EXEMPLOS,
}

removidos = 0
movidos = 0
reorganizados = 0
total_liberado = 0

try:
    # REMOVER arquivos de teste/debug
    print("\n📌 REMOVENDO TESTES/DEBUG (68 arquivos):")
    for arquivo in REMOVER:
        caminho = os.path.join(RAIZ, arquivo)
        if os.path.exists(caminho):
            try:
                tamanho = os.path.getsize(caminho)
                shutil.move(caminho, os.path.join(LIMPEZA, arquivo))
                removidos += 1
                total_liberado += tamanho
                print(f"  ✓ {arquivo}")
            except Exception as e:
                print(f"  ✗ {arquivo}: {e}")
    
    # MOVER duplicados
    print("\n📌 MOVENDO DUPLICADOS (4 arquivos):")
    for arquivo in DUPLICADOS:
        caminho = os.path.join(RAIZ, arquivo)
        if os.path.exists(caminho):
            try:
                tamanho = os.path.getsize(caminho)
                shutil.move(caminho, os.path.join(LIMPEZA, arquivo))
                movidos += 1
                total_liberado += tamanho
                print(f"  ✓ {arquivo}")
            except Exception as e:
                print(f"  ✗ {arquivo}: {e}")
    
    # REORGANIZAR
    print("\n📌 REORGANIZANDO (2 arquivos):")
    for arquivo, destino in REORGANIZAR.items():
        caminho = os.path.join(RAIZ, arquivo)
        if os.path.exists(caminho):
            try:
                dest_path = os.path.join(destino, arquivo)
                shutil.move(caminho, dest_path)
                reorganizados += 1
                pasta = os.path.basename(destino)
                print(f"  ✓ {arquivo} → {pasta}/")
            except Exception as e:
                print(f"  ✗ {arquivo}: {e}")
    
    print("\n" + "=" * 70)
    print(f"📊 RESULTADO FINAL:")
    print(f"  ✓ Arquivos removidos: {removidos}")
    print(f"  ✓ Duplicados movidos: {movidos}")
    print(f"  ✓ Arquivos reorganizados: {reorganizados}")
    print(f"  ✓ Total de operações: {removidos + movidos + reorganizados}")
    print(f"  ✓ Espaço liberado: {total_liberado / (1024**2):.2f} MB")
    print("=" * 70)
    
    print("\n✅ PROJETO LIMPO E REORGANIZADO!")
    print("\n📁 Estrutura final:")
    print(f"  c:\\EngenhariaPlanPro\\")
    print(f"  ├── vigas_app.py")
    print(f"  ├── pilares_app.py")
    print(f"  ├── lajes_app.py")
    print(f"  ├── abrir_lajes_app.py")
    print(f"  ├── blocos_app.py")
    print(f"  ├── core/")
    print(f"  │   ├── lajes_motor.py")
    print(f"  │   ├── pilares_motor.py")
    print(f"  │   ├── vigas_motor_v2.py")
    print(f"  │   └── ...")
    print(f"  ├── docs/")
    print(f"  │   └── lajes_app_metodos_etiquetas.py")
    print(f"  ├── exemplos/")
    print(f"  │   └── lajes_dados_reais.py")
    print(f"  ├── BACKUP_APPS_MOTORES_04022026/")
    print(f"  └── ARQUIVOS_REMOVIDOS_04022026/")
    
except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
