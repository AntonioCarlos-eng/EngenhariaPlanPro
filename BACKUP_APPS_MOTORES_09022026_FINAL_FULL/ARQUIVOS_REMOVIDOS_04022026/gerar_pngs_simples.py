#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Gera PNGs dos desenhos usando mapeamento existente (sem GUI)
"""
import os
import json
import ezdxf
from PIL import Image, ImageDraw

def renderizar_dxf_completo(caminho_dxf):
    """Renderiza o DXF completo em PIL Image"""
    try:
        doc = ezdxf.readfile(caminho_dxf)
        msp = doc.modelspace()
        
        # Calcular bbox
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
        
        bbox = (min_x, min_y, max_x, max_y)
        
        # Criar imagem em alta resolução
        largura_mm = max_x - min_x
        altura_mm = max_y - min_y
        
        # 2 pixels por mm = boa resolução
        escala = 2
        img_width = int(largura_mm * escala)
        img_height = int(altura_mm * escala)
        
        # Limitar tamanho máximo
        max_size = 4000
        if img_width > max_size or img_height > max_size:
            ratio = min(max_size / img_width, max_size / img_height)
            img_width = int(img_width * ratio)
            img_height = int(img_height * ratio)
            escala *= ratio
        
        print(f"Renderizando DXF: {img_width}x{img_height}px")
        
        # Renderizar
        img = Image.new('RGB', (img_width, img_height), 'white')
        draw = ImageDraw.Draw(img)
        
        def transformar(x, y):
            px = int((x - min_x) * escala)
            py = int(img_height - ((y - min_y) * escala))
            return (px, py)
        
        # Desenhar entidades
        count = 0
        for entity in msp:
            try:
                if entity.dxftype() == 'LINE':
                    p1 = transformar(entity.dxf.start.x, entity.dxf.start.y)
                    p2 = transformar(entity.dxf.end.x, entity.dxf.end.y)
                    draw.line([p1, p2], fill='black', width=1)
                    count += 1
                
                elif entity.dxftype() == 'CIRCLE':
                    cx, cy = transformar(entity.dxf.center.x, entity.dxf.center.y)
                    r = int(entity.dxf.radius * escala)
                    draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline='black', width=1)
                    count += 1
                
                elif entity.dxftype() in ('LWPOLYLINE', 'POLYLINE'):
                    points = [transformar(p[0], p[1]) for p in entity.get_points()]
                    if len(points) > 1:
                        draw.line(points, fill='black', width=1)
                        count += 1
            except:
                pass
        
        print(f"Renderizadas {count} entidades")
        return img
    
    except Exception as e:
        print(f"❌ Erro ao renderizar DXF: {e}")
        import traceback
        traceback.print_exc()
        return None


def gerar_pngs(caminho_dxf, mapeamento_json, pasta_saida="export/desenhos_vigas"):
    """Gera PNGs baseado no mapeamento JSON"""
    
    # Carregar mapeamento
    try:
        with open(mapeamento_json, 'r', encoding='utf-8') as f:
            mapeamento = json.load(f)
        print(f"✅ Mapeamento carregado: {len(mapeamento)} vigas")
    except Exception as e:
        print(f"❌ Erro ao carregar mapeamento: {e}")
        return
    
    # Renderizar DXF
    img_completa = renderizar_dxf_completo(caminho_dxf)
    if img_completa is None:
        return
    
    # Criar pasta de saída
    os.makedirs(pasta_saida, exist_ok=True)
    
    # Gerar PNGs
    gerados = 0
    for viga, coords in mapeamento.items():
        try:
            x, y, w, h = coords['x'], coords['y'], coords['w'], coords['h']
            
            # Crop da imagem
            crop = img_completa.crop((x, y, x + w, y + h))
            
            # Salvar
            arquivo = os.path.join(pasta_saida, f"{viga}_desenho.png")
            crop.save(arquivo)
            gerados += 1
            print(f"✅ {arquivo} ({w}x{h}px)")
            
        except Exception as e:
            print(f"❌ Erro ao gerar PNG de {viga}: {e}")
    
    print(f"\n✨ Gerados {gerados} PNGs em {pasta_saida}")


if __name__ == "__main__":
    caminho_dxf = r"dxf\vig terreo f 1-R2 - Copia.DXF"
    mapeamento_json = "mapeamento_desenhos.json"
    
    print("="*60)
    print("GERADOR DE PNGs (SEM GUI)")
    print("="*60)
    print()
    
    gerar_pngs(caminho_dxf, mapeamento_json)
