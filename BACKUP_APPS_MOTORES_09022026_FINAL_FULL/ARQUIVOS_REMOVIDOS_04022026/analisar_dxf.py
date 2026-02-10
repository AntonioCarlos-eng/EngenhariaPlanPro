#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
analisar_dxf.py
---------------
Análise completa da estrutura do DXF para entender como os desenhos estão organizados
"""

import ezdxf
import sys
from collections import defaultdict

def analisar_estrutura_dxf(caminho_dxf):
    """Analisa estrutura completa do DXF"""
    
    print(f"\n{'='*80}")
    print(f"ANÁLISE COMPLETA: {caminho_dxf}")
    print(f"{'='*80}\n")
    
    try:
        doc = ezdxf.readfile(caminho_dxf)
        msp = doc.modelspace()
        
        # 1. Estatísticas por tipo
        print("1️⃣ TIPOS DE ENTIDADES")
        print("-" * 80)
        tipos = defaultdict(int)
        for entity in msp:
            tipos[entity.dxftype()] += 1
        
        for tipo, count in sorted(tipos.items(), key=lambda x: -x[1]):
            print(f"   {tipo:20} : {count:6} entidades")
        
        # 2. Layers
        print("\n2️⃣ LAYERS")
        print("-" * 80)
        layers = defaultdict(int)
        for entity in msp:
            if hasattr(entity, 'dxf') and hasattr(entity.dxf, 'layer'):
                layers[entity.dxf.layer] += 1
        
        for layer, count in sorted(layers.items(), key=lambda x: -x[1])[:20]:
            print(f"   {layer:30} : {count:6} entidades")
        
        # 3. Textos (amostra)
        print("\n3️⃣ TEXTOS (primeiros 50)")
        print("-" * 80)
        count = 0
        textos_por_conteudo = defaultdict(list)
        
        for entity in msp.query('TEXT MTEXT'):
            try:
                texto = entity.dxf.text if hasattr(entity.dxf, 'text') else ""
                
                if hasattr(entity.dxf, 'insert'):
                    px, py = entity.dxf.insert.x, entity.dxf.insert.y
                elif hasattr(entity.dxf, 'start'):
                    px, py = entity.dxf.start.x, entity.dxf.start.y
                else:
                    continue
                
                layer = entity.dxf.layer if hasattr(entity.dxf, 'layer') else "?"
                
                textos_por_conteudo[texto.strip()].append((px, py, layer))
                
                if count < 50:
                    print(f"   [{layer:20}] '{texto}' em ({px:.1f}, {py:.1f})")
                    count += 1
            
            except Exception as e:
                continue
        
        # 4. Buscar padrões de viga
        print("\n4️⃣ PADRÕES DE IDENTIFICAÇÃO DE VIGAS")
        print("-" * 80)
        
        padroes_viga = {}
        for texto, locais in textos_por_conteudo.items():
            texto_up = texto.upper()
            
            # Procurar V seguido de números
            if 'V' in texto_up and any(c.isdigit() for c in texto_up):
                padroes_viga[texto] = locais
        
        print(f"   Encontrados {len(padroes_viga)} textos com padrão 'V':")
        for texto, locais in list(padroes_viga.items())[:20]:
            print(f"      '{texto}' aparece {len(locais)} vez(es)")
            for px, py, layer in locais[:3]:
                print(f"         └─ ({px:.1f}, {py:.1f}) layer={layer}")
        
        # 5. Buscar padrões de posição (N seguido de números)
        print("\n5️⃣ PADRÕES DE POSIÇÃO")
        print("-" * 80)
        
        padroes_pos = {}
        for texto, locais in textos_por_conteudo.items():
            texto_up = texto.upper()
            
            if texto_up.startswith('N') and any(c.isdigit() for c in texto_up):
                padroes_pos[texto] = locais
        
        print(f"   Encontrados {len(padroes_pos)} textos com padrão 'N':")
        for texto, locais in list(padroes_pos.items())[:30]:
            print(f"      '{texto}' aparece {len(locais)} vez(es)")
        
        # 6. Buscar padrões de comprimento (C=)
        print("\n6️⃣ PADRÕES DE COMPRIMENTO (C=)")
        print("-" * 80)
        
        padroes_comp = {}
        for texto, locais in textos_por_conteudo.items():
            if 'C=' in texto.upper():
                padroes_comp[texto] = locais
        
        print(f"   Encontrados {len(padroes_comp)} textos com 'C=':")
        for texto, locais in list(padroes_comp.items())[:20]:
            print(f"      '{texto}' em ({locais[0][0]:.1f}, {locais[0][1]:.1f})")
        
        # 7. Análise de BLOCKs
        print("\n7️⃣ BLOCKS DEFINIDOS")
        print("-" * 80)
        
        if hasattr(doc, 'blocks'):
            for block in list(doc.blocks)[:20]:
                try:
                    print(f"   Block: {block.name}")
                except:
                    pass
        
        # 8. INSERT entities (instâncias de blocos)
        print("\n8️⃣ INSERT ENTITIES (instâncias de blocos)")
        print("-" * 80)
        
        inserts = defaultdict(list)
        for entity in msp.query('INSERT'):
            try:
                nome = entity.dxf.name if hasattr(entity.dxf, 'name') else "?"
                px, py = entity.dxf.insert.x, entity.dxf.insert.y
                inserts[nome].append((px, py))
            except:
                pass
        
        for nome, locais in list(inserts.items())[:20]:
            print(f"   {nome}: {len(locais)} instâncias")
            if len(locais) <= 3:
                for px, py in locais:
                    print(f"      └─ ({px:.1f}, {py:.1f})")
        
        # 9. Bounding box geral
        print("\n9️⃣ BOUNDING BOX GERAL DO PROJETO")
        print("-" * 80)
        
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')
        
        for entity in msp:
            try:
                if entity.dxftype() == 'LINE':
                    min_x = min(min_x, entity.dxf.start.x, entity.dxf.end.x)
                    max_x = max(max_x, entity.dxf.start.x, entity.dxf.end.x)
                    min_y = min(min_y, entity.dxf.start.y, entity.dxf.end.y)
                    max_y = max(max_y, entity.dxf.start.y, entity.dxf.end.y)
            except:
                pass
        
        print(f"   X: {min_x:.1f} a {max_x:.1f} (largura: {max_x - min_x:.1f} mm)")
        print(f"   Y: {min_y:.1f} a {max_y:.1f} (altura: {max_y - min_y:.1f} mm)")
        print(f"   Área: {(max_x - min_x) * (max_y - min_y) / 1000000:.2f} m²")
        
        print("\n" + "="*80)
        print("✅ Análise concluída!")
        print("="*80 + "\n")
    
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    dxf_path = r"dxf\vig terreo f 1-R2 - Copia.DXF"
    
    if len(sys.argv) > 1:
        dxf_path = sys.argv[1]
    
    analisar_estrutura_dxf(dxf_path)
