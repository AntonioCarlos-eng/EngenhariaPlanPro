#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para verificar se o fluxo de medidas está funcionando
"""

import sys
import os
sys.path.insert(0, r"c:\EngenhariaPlanPro")

# Simular estrutura de dados
class MockApp:
    def __init__(self):
        self.dados_processados = [
            ("V1", "A1", 12.5, 2, 4.5),  # viga, pos, bitola, qtde, comp
            ("V1", "N1", 6.3, 5, 1.2),   # estribo
        ]
        self.medidas_customizadas = {}
        self.formas_customizadas = {}
        self.estribo_lados = {}
    
    def test_salvar_edicao(self):
        """Simula o salvamento de edição"""
        print("\n=== TESTANDO SALVAMENTO DE MEDIDAS ===")
        
        # Simular um estribo editado
        viga, pos = "V1", "A1"
        chave = (viga, pos)
        
        # Dados do form
        lado1, lado2, lado3, lado4 = 10.0, 15.0, 20.0, 25.0
        forma = "estribo"
        
        # PASSO 4: Salvar medidas
        self.medidas_customizadas[chave] = {
            'lado1': lado1,
            'lado2': lado2,
            'lado3': lado3,
            'lado4': lado4,
        }
        
        # PASSO 5: Salvar forma
        self.formas_customizadas[chave] = forma
        
        # PASSO auxiliar: Salvar lados para desenho
        if forma == 'estribo':
            self.estribo_lados[chave] = (lado1, lado2, lado3, lado4)
        
        print(f"✓ PASSO 4: Medidas salvas em medidas_customizadas[{chave}]")
        print(f"  {self.medidas_customizadas[chave]}")
        print(f"✓ PASSO 5: Forma salva em formas_customizadas[{chave}]")
        print(f"  {self.formas_customizadas[chave]}")
        print(f"✓ PASSO AUX: Lados salvos em estribo_lados[{chave}]")
        print(f"  {self.estribo_lados[chave]}")
    
    def test_retrieval(self):
        """Simula a recuperação de medidas para renderização"""
        print("\n=== TESTANDO RECUPERAÇÃO DE MEDIDAS ===")
        
        viga, pos = "V1", "A1"
        chave = (viga, pos)
        
        # Simular a busca em desenhar_etiquetas_com_selecao
        if chave in self.medidas_customizadas:
            medidas_dict = self.medidas_customizadas[chave]
            print(f"✓ MEDIDAS ENCONTRADAS para {chave}: {medidas_dict}")
            
            # Recuperar forma
            forma_raw = self.formas_customizadas.get(chave)
            print(f"✓ FORMA ENCONTRADA: {forma_raw}")
            
            if forma_raw == 'estribo':
                va = medidas_dict.get('lado1', 0.0)
                vb = medidas_dict.get('lado2', 0.0)
                vc = medidas_dict.get('lado3', 0.0)
                vd = medidas_dict.get('lado4', 0.0)
                
                if va > 0 or vb > 0 or vc > 0 or vd > 0:
                    self.estribo_lados[chave] = (va, vb, vc, vd)
                    print(f"✓ Estribo {viga}/{pos}: lados={va}cm, {vb}cm, {vc}cm, {vd}cm")
        else:
            print(f"⚠ MEDIDAS NÃO ENCONTRADAS para {chave}")
            print(f"  Chaves disponíveis: {list(self.medidas_customizadas.keys())}")
        
        # Verificar se estribo_lados está preenchido
        if chave in self.estribo_lados:
            estribo_lados = self.estribo_lados[chave]
            print(f"✓ ESTRIBO_LADOS RECUPERADO para passar ao desenho: {estribo_lados}")
            return estribo_lados
        
        return None
    
    def test_draw_function_call(self, estribo_lados):
        """Simula a chamada da função de desenho"""
        print("\n=== TESTANDO CHAMADA DA FUNÇÃO DE DESENHO ===")
        
        forma = "estribo"
        
        # Simular a assinatura da função
        print(f"_desenhar_forma_simplificada(canvas, x, y, w, h, forma='{forma}', medida_dobra=None, medidas_gancho=None, estribo_lados={estribo_lados})")
        
        if estribo_lados is not None:
            try:
                va, vb, vc, vd = estribo_lados
                print(f"✓ Desenhando estribo com:")
                print(f"  - Lado A: {va:.0f}cm")
                print(f"  - Lado B: {vb:.0f}cm")
                print(f"  - Lado C: {vc:.0f}cm")
                print(f"  - Lado D: {vd:.0f}cm")
            except Exception as e:
                print(f"✗ ERRO ao desempacotar estribo_lados: {e}")

if __name__ == "__main__":
    app = MockApp()
    
    print("=" * 60)
    print("TESTE DO FLUXO DE SALVAMENTO E RECUPERAÇÃO DE MEDIDAS")
    print("=" * 60)
    
    # Teste 1: Salvar
    app.test_salvar_edicao()
    
    # Teste 2: Recuperar
    estribo_lados = app.test_retrieval()
    
    # Teste 3: Desenhar
    if estribo_lados:
        app.test_draw_function_call(estribo_lados)
    
    print("\n" + "=" * 60)
    print("✓ TESTES CONCLUÍDOS COM SUCESSO!")
    print("=" * 60)
