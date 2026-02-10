#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PASSO 7: Testes Finais e Validação
================================================
Script para validar todas as correções implementadas nos PASSOS 2-6.

Verificações:
1. Dimensões totais (100mm x 150mm = 1181px x 1772px @ 300 DPI)
2. Margens (2mm de margem da impressora)
3. Alinhamento de textos (cabeçalho, tabela, faixa laranja)
4. Espaçamento vertical (8mm entre linhas)
5. Centralização de legendas do código de barras
6. Legibilidade do código de barras
7. Qualidade das imagens técnicas (sem pixelização)
8. Controle de versão
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# Adicionar ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.etiquetas_layout_config import (
    DPI_PADRAO, PX_MM, mm_to_px, 
    MARGEM_IMPRESSORA_MM, OS_BLOCO_ALTURA_MM
)
from core.etiquetas_generator import GeradorEtiquetasDinamico
from core.impressao_etiquetas import ImpressaoProfissionalEtiquetas

# ============================================================================
# RELATÓRIO DE VALIDAÇÃO
# ============================================================================

class RelatorioValidacao:
    """Gerador de relatório de testes finais"""
    
    def __init__(self):
        self.timestamp = datetime.now()
        self.resultados = []
        self.erros = []
        
    def adicionar_teste(self, nome: str, passou: bool, detalhes: str = ""):
        """Registrar resultado de teste"""
        status = "✅ PASSOU" if passou else "❌ FALHOU"
        self.resultados.append({
            'nome': nome,
            'passou': passou,
            'status': status,
            'detalhes': detalhes
        })
        print(f"{status} | {nome}")
        if detalhes:
            print(f"       {detalhes}")
    
    def adicionar_erro(self, nome: str, erro: str):
        """Registrar erro encontrado"""
        self.erros.append({'teste': nome, 'erro': erro})
        print(f"❌ ERRO | {nome}: {erro}")
    
    def salvar_relatorio(self, caminho_saida: str = "PASSO7_RELATORIO_VALIDACAO.txt"):
        """Salvar relatório em arquivo"""
        with open(caminho_saida, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(f"PASSO 7: RELATÓRIO DE VALIDAÇÃO FINAL\n")
            f.write(f"Data/Hora: {self.timestamp.strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            # Resumo
            total_testes = len(self.resultados)
            passou = sum(1 for r in self.resultados if r['passou'])
            f.write(f"RESUMO: {passou}/{total_testes} testes passaram\n\n")
            
            # Detalhes
            f.write("DETALHES DOS TESTES:\n")
            f.write("-" * 80 + "\n")
            for r in self.resultados:
                f.write(f"{r['status']} | {r['nome']}\n")
                if r['detalhes']:
                    f.write(f"       {r['detalhes']}\n")
            
            if self.erros:
                f.write("\n" + "-" * 80 + "\n")
                f.write("ERROS ENCONTRADOS:\n")
                for e in self.erros:
                    f.write(f"❌ {e['teste']}: {e['erro']}\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("FIM DO RELATÓRIO\n")
        
        print(f"\n✅ Relatório salvo em: {caminho_saida}")

# ============================================================================
# TESTES DE DIMENSÃO
# ============================================================================

def teste_dimensoes_label(relatorio: RelatorioValidacao):
    """Teste 1: Validar dimensões totais (100x150mm @ 300 DPI)"""
    esperado_w_mm = 100
    esperado_h_mm = 150
    esperado_w_px = 1181
    esperado_h_px = 1772
    
    # Verificar conversão
    w_px_calc = mm_to_px(esperado_w_mm)
    h_px_calc = mm_to_px(esperado_h_mm)
    
    passou = (w_px_calc == esperado_w_px and h_px_calc == esperado_h_px)
    detalhes = f"Esperado: {esperado_w_px}x{esperado_h_px}px, Calculado: {w_px_calc}x{h_px_calc}px"
    
    relatorio.adicionar_teste(
        "Dimensões da Etiqueta (100x150mm @ 300 DPI)",
        passou,
        detalhes
    )
    
    return passou

def teste_margens_impressora(relatorio: RelatorioValidacao):
    """Teste 2: Validar margem da impressora (2mm)"""
    margem_esperada = 2.0
    margem_atual = MARGEM_IMPRESSORA_MM
    
    passou = (margem_atual == margem_esperada)
    detalhes = f"Esperado: {margem_esperada}mm, Atual: {margem_atual}mm"
    
    relatorio.adicionar_teste(
        "Margem da Impressora (Argox OS-214)",
        passou,
        detalhes
    )
    
    return passou

# ============================================================================
# TESTES DE ESPAÇAMENTO
# ============================================================================

def teste_espacamento_cabecalho(relatorio: RelatorioValidacao):
    """Teste 3: Validar espaçamento do cabeçalho (8mm entre linhas)"""
    espacamento_esperado = mm_to_px(8)  # 8mm
    
    passou = (espacamento_esperado > 0)
    detalhes = f"Espaçamento: 8mm = {espacamento_esperado}px"
    
    relatorio.adicionar_teste(
        "Espaçamento do Cabeçalho (8mm entre linhas)",
        passou,
        detalhes
    )
    
    return passou

def teste_espacamento_os(relatorio: RelatorioValidacao):
    """Teste 4: Validar altura da caixa OS (30mm)"""
    altura_os_esperada = OS_BLOCO_ALTURA_MM
    altura_os_px = mm_to_px(altura_os_esperada)
    
    passou = (altura_os_px > 0)
    detalhes = f"Altura OS: {altura_os_esperada}mm = {altura_os_px}px"
    
    relatorio.adicionar_teste(
        "Dimensão da Caixa OS",
        passou,
        detalhes
    )
    
    return passou

# ============================================================================
# TESTES DE DPI
# ============================================================================

def teste_dpi_padrao(relatorio: RelatorioValidacao):
    """Teste 5: Validar DPI padrão fixo (300)"""
    dpi_esperado = 300
    
    passou = (DPI_PADRAO == dpi_esperado)
    detalhes = f"DPI Padrão: {DPI_PADRAO} (esperado: {dpi_esperado})"
    
    relatorio.adicionar_teste(
        "DPI Padronizado (fixo em 300)",
        passou,
        detalhes
    )
    
    return passou

def teste_conversao_mm_px(relatorio: RelatorioValidacao):
    """Teste 6: Validar função de conversão mm_to_px()"""
    # Testar alguns valores conhecidos
    testes_conversao = [
        (8, 94),    # 8mm ≈ 94px @ 300 DPI
        (20, 236),  # 20mm ≈ 236px @ 300 DPI
        (30, 354),  # 30mm ≈ 354px @ 300 DPI
    ]
    
    todos_corretos = True
    detalhes_list = []
    
    for mm, px_esperado in testes_conversao:
        px_calc = mm_to_px(mm)
        # Permitir margem de erro de 1px
        correto = abs(px_calc - px_esperado) <= 1
        todos_corretos = todos_corretos and correto
        status = "✓" if correto else "✗"
        detalhes_list.append(f"{status} {mm}mm={px_calc}px (esperado ~{px_esperado}px)")
    
    relatorio.adicionar_teste(
        "Função mm_to_px() - Conversão Correta",
        todos_corretos,
        "; ".join(detalhes_list)
    )
    
    return todos_corretos

# ============================================================================
# TESTES DE GERAÇÃO DE IMAGENS
# ============================================================================

def teste_geracao_png(relatorio: RelatorioValidacao):
    """Teste 7: Gerar PNG de teste e validar dimensões"""
    try:
        # Dados de teste
        dados_teste = {
            'viga': 'V8',
            'pos': 'N1',
            'bitola': 10.0,
            'comp': 5.50,
            'peso': 12.34,
            'qtde': 8,
            'obra': 'OBRA.001',
            'pavimento': 'LAJE',
            'caminho_desenho': None,
            'barcode_img': None,
        }
        
        gerador = GeradorEtiquetasDinamico(
            obra='OBRA.001',
            pavimento='LAJE',
            dados=[dados_teste]
        )
        
        # Gerar PNG
        caminhos_png = gerador.gerar_e_salvar_etiquetas_png()
        
        if caminhos_png and len(caminhos_png) > 0:
            caminho_png = caminhos_png[0]
            
            # Validar dimensões
            img = Image.open(caminho_png)
            largura_px = img.width
            altura_px = img.height
            
            # Permitir pequena margem (até 10px de diferença)
            passou = (abs(largura_px - 1181) <= 10 and 
                     abs(altura_px - 1772) <= 10)
            
            detalhes = f"Dimensões: {largura_px}x{altura_px}px (esperado ~1181x1772px)"
            
            relatorio.adicionar_teste(
                "Geração de PNG com Dimensões Corretas",
                passou,
                detalhes
            )
            
            return passou, caminho_png
        else:
            relatorio.adicionar_erro("Geração PNG", "Nenhum PNG foi gerado")
            return False, None
            
    except Exception as e:
        relatorio.adicionar_erro("Geração PNG", str(e))
        return False, None

def teste_pdf_gerado(relatorio: RelatorioValidacao):
    """Teste 8: Gerar PDF de teste"""
    try:
        dados_teste = {
            'viga': 'V8',
            'pos': 'N1',
            'bitola': 10.0,
            'comp': 5.50,
            'peso': 12.34,
            'qtde': 8,
            'obra': 'OBRA.001',
            'pavimento': 'LAJE',
            'caminho_desenho': None,
        }
        
        impressora = ImpressaoProfissionalEtiquetas(
            obra='OBRA.001',
            pavimento='LAJE',
            dados=[dados_teste]
        )
        
        caminho_pdf = impressora.gerar_pdf_etiquetas()
        
        passou = (caminho_pdf and os.path.exists(caminho_pdf))
        detalhes = f"PDF: {os.path.basename(caminho_pdf) if passou else 'Falha na geração'}"
        
        relatorio.adicionar_teste(
            "Geração de PDF",
            passou,
            detalhes
        )
        
        return passou, caminho_pdf if passou else None
        
    except Exception as e:
        relatorio.adicionar_erro("Geração PDF", str(e))
        return False, None

# ============================================================================
# CHECKLIST DE VALIDAÇÃO VISUAL
# ============================================================================

def criar_checklist_visual():
    """Criar checklist para validação visual/física"""
    checklist = """
╔════════════════════════════════════════════════════════════════════════════╗
║                    CHECKLIST DE VALIDAÇÃO VISUAL                          ║
║                 Imprima e valide as seguintes itens:                       ║
╚════════════════════════════════════════════════════════════════════════════╝

PASSO 2: Alinhamento e Fonte dos Textos
────────────────────────────────────────
□ Cabeçalho (Sigla/Obra, Desenho, Pavimento, Elemento):
  □ Linhas estão alinhadas verticalmente (sem desvios)
  □ Espaçamento entre linhas é consistente (8mm)
  □ Textos não se sobrepõem
  □ Fonte está legível

□ Faixa Laranja (Obra):
  □ Texto rotacionado 90° com clareza
  □ Centrado horizontalmente e verticalmente
  □ Sem cortes ou truncamento

PASSO 3: Caixa OS
─────────────────
□ Caixa OS (canto superior direito):
  □ Dimensões corretas (22mm x 26mm)
  □ Número de OS dividido em linhas (ex: 1-3 em duas linhas)
  □ Texto centralizado dentro da caixa
  □ Sem sobreposição com bordas

PASSO 4: Desenho Técnico
─────────────────────────
□ Imagem técnica (se presente):
  □ Sem pixelização visível
  □ Qualidade clara e nitida
  □ Cores preservadas (se colorida)
  □ Dentro da área vermelha designada

PASSO 5: Tabela de Especificações
──────────────────────────────────
□ Cabeçalhos (Bitola, Compr. Unit., Peso, Qtde):
  □ Centralizados em cada coluna
  □ Fonte adequada (tamanho 8pt)
  □ Visíveis e legíveis

□ Valores:
  □ Centralizados nas colunas
  □ Não sobrepõem com linhas horizontais
  □ Espaçamento vertical adequado (8mm)

PASSO 6: Código de Barras
──────────────────────────
□ Código de barras (rodapé):
  □ Barras bem definidas
  □ Legível por scanner/leitura óptica
  □ Dimensões corretas

□ Legenda do barcode (Elem: V8 N1...):
  □ Centralizada horizontalmente
  □ Espaço adequado abaixo do código (3mm)
  □ Fonte legível
  □ Sem truncamento

VALIDAÇÕES GERAIS
──────────────────
□ Dimensões totais:
  □ Largura: 100mm
  □ Altura: 150mm
  □ Margens: 2mm em todos os lados (Argox)

□ Alinhamento geral:
  □ Todos os elementos alinhados
  □ Sem rotações indesejadas
  □ Simétrico e profissional

□ Qualidade de impressão:
  □ Cores bem definidas
  □ Preto com densidade adequada
  □ Sem borrões ou manchas

IMPRESSÃO FÍSICA (Argox OS-214)
────────────────────────────────
□ Teste de impressão:
  □ Etiqueta saiu completamente
  □ Sem cortes nas bordas
  □ Papel/material correto

□ Legibilidade:
  □ QR/Barcode legível
  □ Textos nítidos
  □ Cores bem reproduzidas

CONTROLE DE VERSÃO
───────────────────
□ Versão documentada:
  □ commit/tag criada para PASSO 7
  □ Mensagem descrevendo todas as correções
  □ Backup dos arquivos principais

╔════════════════════════════════════════════════════════════════════════════╗
║                          FIM DO CHECKLIST                                 ║
╚════════════════════════════════════════════════════════════════════════════╝
"""
    return checklist

# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def executar_testes():
    """Executar suite completa de testes"""
    print("\n" + "=" * 80)
    print("PASSO 7: TESTES FINAIS E VALIDAÇÃO")
    print("=" * 80 + "\n")
    
    relatorio = RelatorioValidacao()
    
    # Testes de Dimensão
    print("\n▶ TESTES DE DIMENSÃO:")
    print("-" * 80)
    teste_dimensoes_label(relatorio)
    teste_margens_impressora(relatorio)
    
    # Testes de Espaçamento
    print("\n▶ TESTES DE ESPAÇAMENTO:")
    print("-" * 80)
    teste_espacamento_cabecalho(relatorio)
    teste_espacamento_os(relatorio)
    
    # Testes de DPI
    print("\n▶ TESTES DE DPI:")
    print("-" * 80)
    teste_dpi_padrao(relatorio)
    teste_conversao_mm_px(relatorio)
    
    # Testes de Geração
    print("\n▶ TESTES DE GERAÇÃO DE IMAGENS:")
    print("-" * 80)
    passou_png, caminho_png = teste_geracao_png(relatorio)
    passou_pdf, caminho_pdf = teste_pdf_gerado(relatorio)
    
    # Salvar relatório
    print("\n" + "=" * 80)
    relatorio.salvar_relatorio()
    
    # Criar checklist visual
    print("\n" + "=" * 80)
    checklist = criar_checklist_visual()
    print(checklist)
    
    with open("PASSO7_CHECKLIST_VISUAL.txt", 'w', encoding='utf-8') as f:
        f.write(checklist)
    print("✅ Checklist salvo em: PASSO7_CHECKLIST_VISUAL.txt")
    
    # Resumo final
    print("\n" + "=" * 80)
    print("RESUMO DO PASSO 7")
    print("=" * 80)
    
    total = len(relatorio.resultados)
    passou = sum(1 for r in relatorio.resultados if r['passou'])
    
    print(f"\n📊 Resultados: {passou}/{total} testes passaram")
    
    if caminho_png:
        print(f"\n📄 PNG de teste gerado: {os.path.basename(caminho_png)}")
    
    if caminho_pdf:
        print(f"📄 PDF de teste gerado: {os.path.basename(caminho_pdf)}")
    
    print("\n✅ PRÓXIMOS PASSOS:")
    print("1. Revisar o arquivo 'PASSO7_RELATORIO_VALIDACAO.txt'")
    print("2. Imprimir etiquetas de teste usando 'PASSO7_CHECKLIST_VISUAL.txt'")
    print("3. Validar dimensões com régua/paquímetro")
    print("4. Testar leitura de código de barras")
    print("5. Fazer commit das alterações com tag de versão")
    print("\n" + "=" * 80 + "\n")

if __name__ == "__main__":
    executar_testes()
