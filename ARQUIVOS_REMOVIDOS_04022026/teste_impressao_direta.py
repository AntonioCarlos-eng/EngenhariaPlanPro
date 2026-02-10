"""
Teste isolado de impressão PowerShell
"""
import subprocess
import os
from PIL import Image, ImageDraw, ImageFont

# 1. Criar uma imagem de teste simples
print("=" * 60)
print("TESTE DE IMPRESSÃO DIRETA")
print("=" * 60)

# Criar imagem de teste
print("\n[1] Criando imagem de teste...")
img = Image.new('RGB', (1181, 1772), (255, 255, 255))
draw = ImageDraw.Draw(img)

try:
    font = ImageFont.truetype("arial.ttf", 40)
except:
    font = ImageFont.load_default()

draw.text((590, 886), "TESTE DE IMPRESSÃO", fill=(0, 0, 0), font=font, anchor='mm')

# Salvar
os.makedirs("output/teste", exist_ok=True)
caminho_teste = "output/teste/TESTE_IMPRESSAO.png"
img.save(caminho_teste, dpi=(300, 300))
print(f"✓ Imagem criada: {caminho_teste}")

# 2. Listar impressoras
print("\n[2] Buscando impressoras disponíveis...")
try:
    import win32print
    impressoras = [impressora[2] for impressora in win32print.EnumPrinters(2)]
    impressora_padrao = win32print.GetDefaultPrinter()
    print(f"✓ Encontradas {len(impressoras)} impressora(s):")
    for i, imp in enumerate(impressoras, 1):
        marcador = " ★ (PADRÃO)" if imp == impressora_padrao else ""
        print(f"   {i}. {imp}{marcador}")
except Exception as e:
    print(f"✗ Erro ao buscar impressoras: {e}")
    exit(1)

if not impressoras:
    print("✗ Nenhuma impressora encontrada!")
    exit(1)

# 3. Perguntar qual impressora usar
print("\n[3] Selecione a impressora:")
escolha = input(f"Digite o número (1-{len(impressoras)}) ou ENTER para usar padrão: ").strip()

if escolha:
    try:
        idx = int(escolha) - 1
        impressora = impressoras[idx]
    except:
        print("✗ Escolha inválida, usando padrão")
        impressora = impressora_padrao
else:
    impressora = impressora_padrao

print(f"✓ Usando impressora: {impressora}")

# 4. Tentar imprimir via PowerShell
print("\n[4] Enviando para impressão via PowerShell...")

caminho_abs = os.path.abspath(caminho_teste)
ps_script = f'''
$printerName = "{impressora}"
$imagePath = "{caminho_abs.replace(chr(92), chr(92)*2)}"

Write-Host "Printer: $printerName"
Write-Host "Image: $imagePath"

try {{
    Add-Type -AssemblyName System.Drawing
    $img = [System.Drawing.Image]::FromFile($imagePath)
    
    $printDoc = New-Object System.Drawing.Printing.PrintDocument
    $printDoc.PrinterSettings.PrinterName = $printerName
    
    $printDoc.Add_PrintPage({{
        param($sender, $ev)
        $ev.Graphics.DrawImage($img, $ev.MarginBounds)
        $ev.HasMorePages = $false
    }})
    
    $printDoc.Print()
    $img.Dispose()
    
    Write-Host "SUCCESS: Impressão enviada!"
    exit 0
}} catch {{
    Write-Host "ERROR: $_"
    exit 1
}}
'''

print("\n--- Script PowerShell ---")
print(ps_script)
print("--- Executando ---\n")

result = subprocess.run(
    ['powershell', '-Command', ps_script],
    capture_output=True,
    text=True,
    timeout=30
)

print("--- STDOUT ---")
print(result.stdout)

if result.stderr:
    print("--- STDERR ---")
    print(result.stderr)

print(f"\n--- Return Code: {result.returncode} ---")

if result.returncode == 0:
    print("\n✓✓✓ IMPRESSÃO ENVIADA COM SUCESSO! ✓✓✓")
    print("Verifique a fila de impressão da impressora.")
else:
    print("\n✗✗✗ ERRO NA IMPRESSÃO ✗✗✗")
    print("Verifique:")
    print("  1. A impressora está ligada?")
    print("  2. A impressora está online?")
    print("  3. Você tem permissão para imprimir?")

print("\n" + "=" * 60)
