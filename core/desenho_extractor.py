#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
desenho_extractor.py
--------------------
Extrai desenhos técnicos de barras diretamente do DXF
Renderiza as entidades gráficas (linhas, círculos, arcos) como imagem PIL
"""

import os
import sys
import re
from typing import Optional, Tuple, List, Dict
from PIL import Image, ImageDraw
import ezdxf
import math


def _abrir_dxf_seguro(caminho_dxf: str):
    """Tenta abrir o DXF com recover para arquivos incompletos/ENDSEC faltando."""
    try:
        return ezdxf.readfile(caminho_dxf)
    except Exception:
        try:
            doc, auditor = ezdxf.recover(caminho_dxf)
            if auditor.has_errors:
                print(f"⚠️ DXF recuperado com {len(auditor.errors)} erro(s) em {caminho_dxf}")
            return doc
        except Exception as e:
            print(f"⚠️ Falha ao abrir DXF {caminho_dxf}: {e}")
            return None


def localizar_desenho_viga_no_dxf(caminho_dxf: str, viga: str, pos: str, 
                                  largura_px: int = 200, altura_px: int = 150) -> Optional[Image.Image]:
    """
    NOVA ESTRATÉGIA: Buscar por texto de especificação técnica da viga
    Ex: "V8 14X60", "V301 12X50" - textos que aparecem APENAS no detalhe técnico
    """
    try:
        print(f"      🔍 Buscando especificação técnica de {viga}...")
        
        doc = _abrir_dxf_seguro(caminho_dxf)
        if doc is None:
            return None
        msp = doc.modelspace()
        
        viga_up = viga.upper().strip()
        
        # Buscar textos com padrão de especificação: viga + dimensão (ex: "V8 14X60")
        textos_spec = []
        
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
                
                # Padrão: viga + espaço + números + X + números
                # Ex: "V8 14X60", "V301 12X50", "VM2 10X40"
                if viga_up in texto_upper and 'X' in texto_upper:
                    # Verificar se tem padrão numérico NxN
                    import re
                    if re.search(r'\d+\s*[Xx]\s*\d+', texto_upper):
                        textos_spec.append({'texto': texto, 'x': px, 'y': py})
                        print(f"      ✅ Spec: '{texto}' em ({px:.0f}, {py:.0f})")
            
            except Exception:
                continue
        
        if textos_spec:
            # Usar a PRIMEIRA especificação encontrada
            spec = textos_spec[0]
            centro_x = spec['x']
            centro_y = spec['y']
            
            print(f"      🎯 Usando spec em ({centro_x:.0f}, {centro_y:.0f})")
            
            # Região pequena ao redor da especificação (onde está o detalhe)
            raio_x = 60  # ±60mm
            raio_y = 40  # ±40mm
            
            min_x = centro_x - raio_x
            max_x = centro_x + raio_x
            min_y = centro_y - raio_y
            max_y = centro_y + raio_y
            
            print(f"      Bbox: ({min_x:.0f},{min_y:.0f}) → ({max_x:.0f},{max_y:.0f})")
            
            return renderizar_regiao_dxf_estrita(caminho_dxf, min_x, min_y, max_x, max_y, largura_px, altura_px)
        
        print(f"      ❌ Nenhuma especificação encontrada")
        return None
    
    except Exception as e:
        print(f"      ❌ Erro: {e}")
        return None


def renderizar_regiao_dxf_estrita(caminho_dxf: str, min_x: float, min_y: float, max_x: float, max_y: float,
                                  largura_px: int = 200, altura_px: int = 150) -> Optional[Image.Image]:
    """
    Renderiza APENAS entidades COMPLETAMENTE dentro da região (ambos os pontos)
    """
    try:
        doc = ezdxf.readfile(caminho_dxf)
        msp = doc.modelspace()
        
        # Margens
        margem = 5
        w = max(1, max_x - min_x)
        h = max(1, max_y - min_y)
        escala = min((largura_px - 2*margem) / w, (altura_px - 2*margem) / h)
        
        # Criar imagem
        img = Image.new('RGB', (largura_px, altura_px), 'white')
        draw = ImageDraw.Draw(img)
        
        def transformar(x, y):
            px = int((x - min_x) * escala + margem)
            py = int(altura_px - ((y - min_y) * escala + margem))
            return (px, py)
        
        def ponto_dentro(x, y):
            return min_x <= x <= max_x and min_y <= y <= max_y
        
        # Contadores
        dentro = 0
        fora = 0
        
        # Desenhar APENAS se TODOS os pontos estiverem dentro
        for entity in msp:
            try:
                if entity.dxftype() == 'LINE':
                    x1, y1 = entity.dxf.start.x, entity.dxf.start.y
                    x2, y2 = entity.dxf.end.x, entity.dxf.end.y
                    
                    # AMBOS os pontos EXATAMENTE dentro
                    p1_dentro = ponto_dentro(x1, y1)
                    p2_dentro = ponto_dentro(x2, y2)
                    
                    if p1_dentro and p2_dentro:
                        p1 = transformar(x1, y1)
                        p2 = transformar(x2, y2)
                        draw.line([p1, p2], fill='black', width=1)
                        dentro += 1
                    else:
                        fora += 1
                
                elif entity.dxftype() == 'CIRCLE':
                    cx, cy = entity.dxf.center.x, entity.dxf.center.y
                    r = entity.dxf.radius
                    
                    # Centro E todas as extremidades do raio dentro
                    if ponto_dentro(cx, cy) and ponto_dentro(cx+r, cy) and ponto_dentro(cx-r, cy) and ponto_dentro(cx, cy+r) and ponto_dentro(cx, cy-r):
                        p = transformar(cx, cy)
                        r_px = int(r * escala)
                        draw.ellipse([p[0]-r_px, p[1]-r_px, p[0]+r_px, p[1]+r_px], outline='black', width=1)
                        dentro += 1
                    else:
                        fora += 1
                
                elif entity.dxftype() == 'ARC':
                    cx, cy = entity.dxf.center.x, entity.dxf.center.y
                    if ponto_dentro(cx, cy):
                        p = transformar(cx, cy)
                        r = int(entity.dxf.radius * escala)
                        start_angle = math.radians(entity.dxf.start_angle)
                        end_angle = math.radians(entity.dxf.end_angle)
                        steps = 20
                        for i in range(steps):
                            t = i / steps
                            angle = start_angle + (end_angle - start_angle) * t
                            x1 = p[0] + r * math.cos(angle)
                            y1 = p[1] + r * math.sin(angle)
                            t2 = (i + 1) / steps
                            angle2 = start_angle + (end_angle - start_angle) * t2
                            x2 = p[0] + r * math.cos(angle2)
                            y2 = p[1] + r * math.sin(angle2)
                            draw.line([int(x1), int(y1), int(x2), int(y2)], fill='black', width=1)
                        dentro += 1
                    else:
                        fora += 1
                
                elif entity.dxftype() in ('LWPOLYLINE', 'POLYLINE'):
                    all_points = list(entity.get_points())
                    if len(all_points) > 1:
                        # TODOS os pontos devem estar dentro
                        todos_dentro = all(ponto_dentro(pt[0], pt[1]) for pt in all_points)
                        
                        if todos_dentro:
                            points = [transformar(pt[0], pt[1]) for pt in all_points]
                            if len(points) > 1:
                                draw.line(points, fill='black', width=1)
                            dentro += 1
                        else:
                            fora += 1
            
            except Exception:
                fora += 1
                continue
        
        print(f"✅ Renderizadas: {dentro} entidades")
        
        if dentro == 0:
            print(f"      ⚠️ Região vazia!")
        
        return img
    
    except Exception as e:
        print(f"⚠️ Erro ao renderizar região: {e}")
        return None


if __name__ == "__main__":
    # Teste
    if len(sys.argv) > 1:
        dxf_path = sys.argv[1]
        viga = sys.argv[2] if len(sys.argv) > 2 else "V8"
        pos = sys.argv[3] if len(sys.argv) > 3 else "N1"
        
        img = localizar_desenho_viga_no_dxf(dxf_path, viga, pos, 300, 200)
        if img:
            img.save(f"teste_{viga}_{pos}.png")
            print(f"✅ Salvo: teste_{viga}_{pos}.png")
        else:
            print(f"❌ Não foi possível extrair desenho")
