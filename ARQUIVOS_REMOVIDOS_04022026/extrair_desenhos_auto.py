"""
Script automatizado para extrair desenhos de vigas do DXF limpo
e popular o banco_desenhos automaticamente.
"""
import os
import json
import ezdxf
from PIL import Image, ImageDraw
from collections import defaultdict
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


# Caminho do DXF limpo fornecido pelo usuário
DXF_LIMPO = r"c:\Users\orqui\OneDrive\Área de Trabalho\projetos\vigas\#PRANCHAS PREDIO Vigas 3 laje VN3 - Copia.dxf"
PASTA_BANCO = "banco_desenhos"
ARQUIVO_JSON = "banco_desenhos.json"

# Configurações de renderização
ESCALA_DPI = 300  # DPI para renderização
MARGEM_MM = 50    # Margem ao redor de cada desenho (em mm)


def carregar_dxf():
    """Carrega o arquivo DXF"""
    print(f"📂 Carregando DXF: {DXF_LIMPO}")
    try:
        doc = ezdxf.readfile(DXF_LIMPO)
        msp = doc.modelspace()
        print(f"✅ DXF carregado com sucesso")
        return doc, msp
    except Exception as e:
        print(f"❌ Erro ao carregar DXF: {e}")
        return None, None


def encontrar_vigas(msp):
    """
    Identifica todas as vigas no DXF procurando por textos como VN3- 1, VN2- 54, etc.
    Retorna dicionário: {viga: [(x, y), ...]}
    """
    vigas_posicoes = defaultdict(list)
    
    print("\n🔍 Procurando vigas no DXF...")
    
    # Procurar em MTEXT (formato: VN3- 1, VN2- 54, etc)
    for text_entity in msp.query('MTEXT'):
        if hasattr(text_entity, 'text'):
            texto = text_entity.text.strip().upper()
            
            # Padrão: VN3- 1, VN2- 54, etc (pode ter espaço)
            import re
            match = re.match(r'^VN\d+-\s*\d+[A-Z]?$', texto)
            if match:
                # Normalizar: remover espaço -> VN3-1
                viga = texto.replace(" ", "")
                pos = text_entity.dxf.insert
                vigas_posicoes[viga].append((pos.x, pos.y))
    
    # Procurar também em TEXT
    for text_entity in msp.query('TEXT'):
        texto = text_entity.dxf.text.strip().upper()
        import re
        match = re.match(r'^VN\d+-\s*\d+[A-Z]?$', texto)
        if match:
            viga = texto.replace(" ", "")
            pos = text_entity.dxf.insert
            vigas_posicoes[viga].append((pos.x, pos.y))
    
    print(f"✅ Encontradas {len(vigas_posicoes)} vigas únicas")
    for viga in sorted(vigas_posicoes.keys())[:10]:
        print(f"   • {viga}: {len(vigas_posicoes[viga])} ocorrências")
    
    return dict(vigas_posicoes)


def identificar_posicoes_por_viga(vigas_posicoes):
    """
    Para cada viga com múltiplas ocorrências, identifica as posições como N1, N2, N3...
    baseado na ordem da esquerda para direita, cima para baixo.
    """
    vigas_com_posicoes = {}
    
    print("\n🎯 Identificando posições (N1, N2, N3...)...")
    
    for viga, posicoes in vigas_posicoes.items():
        if len(posicoes) == 1:
            # Apenas uma ocorrência - assumir N1
            vigas_com_posicoes[f"{viga}_N1"] = posicoes[0]
        else:
            # Múltiplas ocorrências - ordenar por X (esquerda->direita), depois Y (cima->baixo)
            posicoes_ordenadas = sorted(posicoes, key=lambda p: (p[0], -p[1]))
            
            for idx, pos in enumerate(posicoes_ordenadas, 1):
                identificacao = f"{viga}_N{idx}"
                vigas_com_posicoes[identificacao] = pos
                print(f"   • {identificacao}: ({pos[0]:.1f}, {pos[1]:.1f})")
    
    print(f"✅ Total de {len(vigas_com_posicoes)} identificações criadas")
    return vigas_com_posicoes


def calcular_bbox_ao_redor(x_centro, y_centro, largura_mm=400, altura_mm=300):
    """
    Calcula bounding box ao redor de um ponto central.
    Retorna: (x_min, y_min, x_max, y_max)
    """
    x_min = x_centro - largura_mm / 2
    x_max = x_centro + largura_mm / 2
    y_min = y_centro - altura_mm / 2
    y_max = y_centro + altura_mm / 2
    
    return (x_min, y_min, x_max, y_max)


def renderizar_regiao_dxf(doc, bbox, output_path, dpi=300):
    """
    Renderiza uma região específica do DXF e salva como PNG.
    bbox = (x_min, y_min, x_max, y_max)
    """
    try:
        fig = plt.figure(figsize=(8, 6), dpi=dpi)
        ax = fig.add_axes([0, 0, 1, 1])
        
        # Configurar limites da região
        ax.set_xlim(bbox[0], bbox[2])
        ax.set_ylim(bbox[1], bbox[3])
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Renderizar DXF
        msp = doc.modelspace()
        
        # Desenhar entidades
        for entity in msp:
            if entity.dxftype() == 'LINE':
                start = entity.dxf.start
                end = entity.dxf.end
                ax.plot([start.x, end.x], [start.y, end.y], 'k-', linewidth=0.5)
            
            elif entity.dxftype() == 'LWPOLYLINE':
                points = list(entity.get_points())
                if points:
                    xs = [p[0] for p in points]
                    ys = [p[1] for p in points]
                    ax.plot(xs, ys, 'k-', linewidth=0.5)
            
            elif entity.dxftype() == 'CIRCLE':
                center = entity.dxf.center
                radius = entity.dxf.radius
                circle = plt.Circle((center.x, center.y), radius, fill=False, color='k', linewidth=0.5)
                ax.add_patch(circle)
            
            elif entity.dxftype() == 'ARC':
                from matplotlib.patches import Arc
                center = entity.dxf.center
                radius = entity.dxf.radius
                start_angle = entity.dxf.start_angle
                end_angle = entity.dxf.end_angle
                arc = Arc((center.x, center.y), 2*radius, 2*radius, 
                         angle=0, theta1=start_angle, theta2=end_angle,
                         color='k', linewidth=0.5)
                ax.add_patch(arc)
            
            elif entity.dxftype() in ['TEXT', 'MTEXT']:
                try:
                    texto = entity.dxf.text if entity.dxftype() == 'TEXT' else entity.text
                    pos = entity.dxf.insert
                    height = entity.dxf.height if hasattr(entity.dxf, 'height') else 2.5
                    ax.text(pos.x, pos.y, texto, fontsize=height*2, ha='left', va='bottom')
                except:
                    pass
        
        # Salvar
        plt.savefig(output_path, dpi=dpi, bbox_inches='tight', pad_inches=0.1)
        plt.close(fig)
        
        return True
    
    except Exception as e:
        print(f"❌ Erro ao renderizar {output_path}: {e}")
        return False


def extrair_todos_desenhos():
    """Função principal para extrair todos os desenhos automaticamente"""
    
    # Criar pasta banco_desenhos se não existir
    if not os.path.exists(PASTA_BANCO):
        os.makedirs(PASTA_BANCO)
        print(f"📁 Pasta {PASTA_BANCO}/ criada")
    
    # Carregar DXF
    doc, msp = carregar_dxf()
    if not doc:
        return
    
    # Encontrar vigas
    vigas_posicoes = encontrar_vigas(msp)
    if not vigas_posicoes:
        print("❌ Nenhuma viga encontrada no DXF")
        return
    
    # Identificar posições
    vigas_com_ids = identificar_posicoes_por_viga(vigas_posicoes)
    
    # Extrair cada desenho
    print(f"\n🖼️ Extraindo {len(vigas_com_ids)} desenhos...")
    
    banco_dados = {}
    contador_sucesso = 0
    
    for identificacao, (x_centro, y_centro) in vigas_com_ids.items():
        # Calcular bounding box
        bbox = calcular_bbox_ao_redor(x_centro, y_centro, largura_mm=400, altura_mm=300)
        
        # Caminho do arquivo
        output_path = os.path.join(PASTA_BANCO, f"{identificacao}.png")
        
        # Renderizar
        print(f"   Renderizando {identificacao}...", end=" ")
        sucesso = renderizar_regiao_dxf(doc, bbox, output_path, dpi=ESCALA_DPI)
        
        if sucesso:
            # Armazenar informações no JSON
            banco_dados[identificacao] = {
                "bbox": bbox,
                "centro": [x_centro, y_centro],
                "arquivo": f"{identificacao}.png"
            }
            contador_sucesso += 1
            print("✅")
        else:
            print("❌")
    
    # Salvar JSON
    json_path = os.path.join(PASTA_BANCO, ARQUIVO_JSON)
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(banco_dados, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Extração concluída!")
    print(f"   📊 {contador_sucesso}/{len(vigas_com_ids)} desenhos extraídos com sucesso")
    print(f"   📁 Salvos em: {PASTA_BANCO}/")
    print(f"   📄 Índice: {json_path}")
    
    # Listar alguns exemplos
    print(f"\n📋 Exemplos de arquivos criados:")
    arquivos = sorted([f for f in os.listdir(PASTA_BANCO) if f.endswith('.png')])[:10]
    for arq in arquivos:
        print(f"   • {arq}")


if __name__ == "__main__":
    print("=" * 80)
    print("  EXTRAÇÃO AUTOMÁTICA DE DESENHOS DE VIGAS")
    print("=" * 80)
    print()
    
    if not os.path.exists(DXF_LIMPO):
        print(f"❌ Arquivo não encontrado: {DXF_LIMPO}")
        print("\n⚠️ ATENÇÃO: Edite a variável DXF_LIMPO no início do script")
        print("   com o caminho correto do seu arquivo DXF limpo.")
    else:
        extrair_todos_desenhos()
    
    print("\n" + "=" * 80)
    input("\nPressione ENTER para sair...")
