import sys
sys.path.insert(0, r'c:\EngenhariaPlanPro')

from core.vigas_motor_v2 import processar_vigas
import ezdxf

# Processar o arquivo
arquivo = r'c:\EngenhariaPlanPro\core\v4\vig terreo f 1-R2 - Copia.DXF'

print("="*80)
print("ANÁLISE COMPLETA DO DXF")
print("="*80)

# 1. Ver todos os textos no arquivo
print("\n1. TODOS OS TEXTOS NO ARQUIVO:")
print("-"*80)
doc = ezdxf.readfile(arquivo)
msp = doc.modelspace()

textos = []
for e in msp.query("TEXT MTEXT ATTRIB"):
    try:
        txt = e.dxf.text if e.dxftype() == 'TEXT' else e.plain_text()
    except:
        txt = getattr(e, "text", "")
    if txt:
        x, y = float(e.dxf.insert[0]), float(e.dxf.insert[1])
        textos.append({"text": txt.strip(), "x": x, "y": y})
        print(f"  X={x:8.2f}  Y={y:8.2f}  => '{txt.strip()}'")

# 2. Processar com o motor
print("\n\n2. RESULTADO DO PROCESSAMENTO:")
print("-"*80)
dados, total_kg, total_barras = processar_vigas([arquivo])

print(f"\nTotal de linhas extraídas: {len(dados)}")
print(f"Total de kg: {total_kg}")
print(f"Total de barras: {total_barras}")

print("\n3. DADOS EXTRAÍDOS (ordenados):")
print("-"*80)
viga_atual = None
for viga, pos, bit, qty, comp, peso in dados:
    if viga != viga_atual:
        print(f"\n>>> {viga}")
        print("-"*60)
        viga_atual = viga
    print(f"    {pos:6s} Ø{bit:5.1f}   Qtd: {qty:2d}    Comp: {comp:5.2f} m  Peso: {peso:6.2f} kg")

# 3. Analisar padrões não detectados
print("\n\n4. ANÁLISE DE PADRÕES:")
print("-"*80)
import re

REGEX_BARRA_FULL = re.compile(
    r"""(?:(\d+)x)?      # mult opcional
        (\d+)            # qty
        \s*N(\d+)        # posição
        \s*[Øø∅]?\s*
        (\d+(?:[.,][\d]+)?) # bitola
        \s*C\s*=?\s*
        (\d+(?:[.,][\d]+)?) # comp
    """, re.IGNORECASE | re.VERBOSE
)

print("\nTextos que parecem ser barras mas não foram detectados:")
for t in textos:
    txt = t["text"]
    # Ver se tem padrão de barra
    if any(x in txt.upper() for x in ["Ø", "%%C", "C=", "MM"]) or re.search(r'N\d+', txt, re.I):
        # Verificar se foi processado
        foi_processado = False
        if REGEX_BARRA_FULL.search(txt):
            foi_processado = True
        
        if not foi_processado:
            print(f"  [{t['x']:8.2f}, {t['y']:8.2f}] => '{txt}'")
