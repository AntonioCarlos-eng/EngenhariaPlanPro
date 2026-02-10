#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
diagnostico_bbox.py
-------------------
Script de diagnóstico para validar extração de desenhos DXF
Renderiza a região com bbox visual para debug
"""

import sys
import os
from PIL import Image, ImageDraw
import ezdxf

def diagnosticar_extracao(caminho_dxf, viga, pos):
    """Diagnóstica extração mostrando bbox e entidades"""
    
    print(f"\n{'='*60}")
    print(f"DIAGNÓSTICO: {viga} / {pos}")
    print(f"DXF: {caminho_dxf}")
    print(f"{'='*60}\n")
    
    try:
        doc = ezdxf.readfile(caminho_dxf)
        msp = doc.modelspace()
        
        # 1. Buscar textos de viga e posição
        print("1️⃣ Buscando textos...")
        textos_viga = []
        textos_pos = []
        
        for entity in msp.query('TEXT MTEXT'):
            try:
                texto = entity.dxf.text if hasattr(entity.dxf, 'text') else ""
                texto_upper = texto.upper().strip()
                
                if hasattr(entity.dxf, 'insert'):
                    px, py = entity.dxf.insert.x, entity.dxf.insert.y
                elif hasattr(entity.dxf, 'start'):
                    px, py = entity.dxf.start.x, entity.dxf.start.y
                else:
                    continue
                
                if viga.upper() in texto_upper:
                    textos_viga.append({'texto': texto, 'x': px, 'y': py})
                    print(f"   ✅ Viga: '{texto}' em ({px:.1f}, {py:.1f})")
                
                if pos.upper() in texto_upper:
                    textos_pos.append({'texto': texto, 'x': px, 'y': py})
                    print(f"   ✅ Pos: '{texto}' em ({px:.1f}, {py:.1f})")
            
            except Exception:
                continue
        
        if not textos_viga:
            print("   ❌ Nenhum texto de viga encontrado!")
            return
        if not textos_pos:
            print("   ❌ Nenhum texto de posição encontrado!")
            return
        
        # 2. Calcular centro e bbox
        print("\n2️⃣ Calculando bbox...")
        tv = textos_viga[0]
        tp = textos_pos[0]
        
        centro_x = (tv['x'] + tp['x']) / 2
        centro_y = (tv['y'] + tp['y']) / 2
        distancia = ((tv['x'] - tp['x'])**2 + (tv['y'] - tp['y'])**2)**0.5
        
        print(f"   Centro: ({centro_x:.1f}, {centro_y:.1f})")
        print(f"   Distância viga-pos: {distancia:.1f} mm")
        
        raio_x, raio_y = 60, 45
        min_x = centro_x - raio_x
        max_x = centro_x + raio_x
        min_y = centro_y - raio_y
        max_y = centro_y + raio_y
        
        print(f"   Bbox: ({min_x:.1f}, {min_y:.1f}) a ({max_x:.1f}, {max_y:.1f})")
        print(f"   Dimensões: {max_x - min_x:.1f} x {max_y - min_y:.1f} mm")
        
        # 3. Contar entidades dentro e fora da região
        print("\n3️⃣ Analisando entidades...")
        
        dentro = 0
        fora = 0
        parcial = 0
        
        for entity in msp:
            try:
                if entity.dxftype() == 'LINE':
                    x1, y1 = entity.dxf.start.x, entity.dxf.start.y
                    x2, y2 = entity.dxf.end.x, entity.dxf.end.y
                    
                    p1_dentro = min_x <= x1 <= max_x and min_y <= y1 <= max_y
                    p2_dentro = min_x <= x2 <= max_x and min_y <= y2 <= max_y
                    
                    if p1_dentro and p2_dentro:
                        dentro += 1
                    elif p1_dentro or p2_dentro:
                        parcial += 1
                    else:
                        fora += 1
                
                elif entity.dxftype() == 'CIRCLE':
                    cx, cy = entity.dxf.center.x, entity.dxf.center.y
                    if min_x <= cx <= max_x and min_y <= cy <= max_y:
                        dentro += 1
                    else:
                        fora += 1
                
                elif entity.dxftype() in ('LWPOLYLINE', 'POLYLINE', 'ARC'):
                    dentro += 1  # Simplificado
            
            except Exception:
                continue
        
        print(f"   ✅ Dentro da região: {dentro}")
        print(f"   ⚠️  Parcialmente dentro: {parcial}")
        print(f"   ❌ Fora da região: {fora}")
        print(f"   📊 Total relevante: {dentro + parcial}")
        
        # 4. Renderizar com bbox visual
        print("\n4️⃣ Renderizando diagnóstico...")
        
        largura_px, altura_px = 600, 450
        margem = 5
        w = max(1, max_x - min_x)
        h = max(1, max_y - min_y)
        escala = min((largura_px - 2*margem) / w, (altura_px - 2*margem) / h)
        
        img = Image.new('RGB', (largura_px, altura_px), 'white')
        draw = ImageDraw.Draw(img)
        
        def transformar(x, y):
            px = int((x - min_x) * escala + margem)
            py = int(altura_px - ((y - min_y) * escala + margem))
            return (px, py)
        
        # Desenhar bbox em vermelho
        p1 = transformar(min_x, min_y)
        p2 = transformar(max_x, min_y)
        p3 = transformar(max_x, max_y)
        p4 = transformar(min_x, max_y)
        draw.polygon([p1, p2, p3, p4], outline='red', width=3)
        
        # Desenhar entidades
        for entity in msp:
            try:
                if entity.dxftype() == 'LINE':
                    x1, y1 = entity.dxf.start.x, entity.dxf.start.y
                    x2, y2 = entity.dxf.end.x, entity.dxf.end.y
                    
                    # Verificar interseção com bbox
                    p1_dentro = min_x <= x1 <= max_x and min_y <= y1 <= max_y
                    p2_dentro = min_x <= x2 <= max_x and min_y <= y2 <= max_y
                    
                    if p1_dentro or p2_dentro:
                        pt1 = transformar(x1, y1)
                        pt2 = transformar(x2, y2)
                        draw.line([pt1, pt2], fill='black', width=1)
                
                elif entity.dxftype() == 'CIRCLE':
                    cx, cy = entity.dxf.center.x, entity.dxf.center.y
                    if min_x <= cx <= max_x and min_y <= cy <= max_y:
                        p = transformar(cx, cy)
                        r = int(entity.dxf.radius * escala)
                        draw.ellipse([p[0]-r, p[1]-r, p[0]+r, p[1]+r], outline='black', width=1)
            
            except Exception:
                continue
        
        # Marcar centro com cruz verde
        pc = transformar(centro_x, centro_y)
        draw.line([(pc[0]-10, pc[1]), (pc[0]+10, pc[1])], fill='green', width=2)
        draw.line([(pc[0], pc[1]-10), (pc[0], pc[1]+10)], fill='green', width=2)
        
        # Marcar textos com círculos azuis
        for tv in textos_viga:
            p = transformar(tv['x'], tv['y'])
            draw.ellipse([p[0]-8, p[1]-8, p[0]+8, p[1]+8], outline='blue', width=2)
        
        for tp in textos_pos:
            p = transformar(tp['x'], tp['y'])
            draw.ellipse([p[0]-5, p[1]-5, p[0]+5, p[1]+5], outline='cyan', width=2)
        
        # Salvar
        nome_arquivo = f"diagnostico_{viga}_{pos}.png"
        img.save(nome_arquivo)
        print(f"   ✅ Salvo: {nome_arquivo}")
        print(f"\n   🔴 Vermelho = bbox da região")
        print(f"   🟢 Verde = centro calculado")
        print(f"   🔵 Azul = texto viga")
        print(f"   🔵 Ciano = texto posição")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Teste com V8 / N1
    dxf_path = r"dxf\vig terreo f 1-R2 - Copia.DXF"
    
    if len(sys.argv) > 1:
        viga = sys.argv[1]
        pos = sys.argv[2] if len(sys.argv) > 2 else "N1"
    else:
        viga = "V8"
        pos = "N1"
    
    diagnosticar_extracao(dxf_path, viga, pos)
