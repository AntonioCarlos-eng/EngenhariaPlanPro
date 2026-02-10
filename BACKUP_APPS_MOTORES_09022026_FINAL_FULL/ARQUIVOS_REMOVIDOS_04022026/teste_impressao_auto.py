"""
Teste AUTOMÁTICO de impressão PowerShell (sem interação)
"""
import subprocess
import os
from PIL import Image, ImageDraw, ImageFont

print("=" * 60)
print("TESTE AUTOMÁTICO DE IMPRESSÃO")
print("=" * 60)

# 1. Criar imagem de teste
print("\n[1] Criando imagem de teste...")
img = Image.new('RGB', (1181, 1772), (255, 255, 255))
draw = ImageDraw.Draw(img)

try:
    font_grande = ImageFont.truetype("arial.ttf", 60)
    font_pequena = ImageFont.truetype("arial.ttf", 30)
except:
    font_grande = ImageFont.load_default()
    font_pequena = font_grande

draw.rectangle([50, 50, 1131, 1722], outline=(255, 0, 0), width=5)
draw.text((590, 400), "TESTE DE IMPRESSÃO", fill=(0, 0, 0), font=font_grande, anchor='mm')
draw.text((590, 500), "EngenhariaPlanPro V3", fill=(100, 116, 139), font=font_pequena, anchor='mm')

os.makedirs("output/teste", exist_ok=True)
caminho_teste = os.path.abspath("output/teste/TESTE_AUTO.png")
img.save(caminho_teste, dpi=(300, 300))
print(f"✓ Imagem criada: {caminho_teste}")

# 2. Buscar impressora padrão
print("\n[2] Buscando impressora padrão...")
try:
    import win32print
    impressora = win32print.GetDefaultPrinter()
    print(f"✓ Impressora padrão: {impressora}")
except Exception as e:
    print(f"✗ Erro: {e}")
    exit(1)

# 3. Script PowerShell
print("\n[3] Preparando script PowerShell...")
ps_script = f'''
$printerName = "{impressora}"
$imagePath = "{caminho_teste.replace(chr(92), chr(92)*2)}"

Write-Host "="*60
Write-Host "POWERSHELL PRINTING TEST"
Write-Host "="*60
Write-Host ""
Write-Host "Printer: $printerName"
Write-Host "Image:   $imagePath"
Write-Host ""

# Verificar se arquivo existe
if (-not (Test-Path $imagePath)) {{
    Write-Host "ERROR: Arquivo não encontrado!"
    exit 1
}}
Write-Host "[OK] Arquivo encontrado"

# Verificar se impressora existe
$printers = Get-WmiObject -Query "SELECT * FROM Win32_Printer WHERE Name='$printerName'"
if ($printers -eq $null) {{
    Write-Host "ERROR: Impressora não encontrada!"
    exit 1
}}
Write-Host "[OK] Impressora encontrada"

# Tentar imprimir
try {{
    Write-Host ""
    Write-Host "Carregando assemblies..."
    Add-Type -AssemblyName System.Drawing
    Write-Host "[OK] System.Drawing carregado"
    
    Write-Host "Carregando imagem..."
    $img = [System.Drawing.Image]::FromFile($imagePath)
    Write-Host "[OK] Imagem carregada: $($img.Width)x$($img.Height) pixels"
    
    Write-Host "Criando documento de impressão..."
    $printDoc = New-Object System.Drawing.Printing.PrintDocument
    $printDoc.PrinterSettings.PrinterName = $printerName
    Write-Host "[OK] Documento criado"
    
    Write-Host "Adicionando evento PrintPage..."
    $printDoc.Add_PrintPage({{
        param($sender, $ev)
        $ev.Graphics.DrawImage($img, $ev.MarginBounds)
        $ev.HasMorePages = $false
    }})
    Write-Host "[OK] Evento configurado"
    
    Write-Host ""
    Write-Host ">>> ENVIANDO PARA IMPRESSÃO <<<"
    $printDoc.Print()
    Write-Host "[OK] Print() executado!"
    
    Start-Sleep -Seconds 1
    $img.Dispose()
    Write-Host "[OK] Recursos liberados"
    
    Write-Host ""
    Write-Host "="*60
    Write-Host "SUCCESS: Impressão enviada para fila!"
    Write-Host "="*60
    exit 0
    
}} catch {{
    Write-Host ""
    Write-Host "="*60
    Write-Host "ERROR: $_"
    Write-Host "="*60
    exit 1
}}
'''

print("\n[4] Executando PowerShell...")
print("-" * 60)

result = subprocess.run(
    ['powershell', '-ExecutionPolicy', 'Bypass', '-Command', ps_script],
    capture_output=True,
    text=True,
    timeout=30
)

print(result.stdout)

if result.stderr:
    print("\n--- STDERR ---")
    print(result.stderr)

print("-" * 60)
print(f"\nReturn Code: {result.returncode}")

if result.returncode == 0:
    print("\n✅ ✅ ✅  SUCESSO!  ✅ ✅ ✅")
    print("\nA impressão foi enviada para a fila.")
    print("Verifique se saiu na impressora!")
else:
    print("\n❌ ❌ ❌  FALHA!  ❌ ❌ ❌")
    print("\nPossíveis causas:")
    print("  • Impressora offline")
    print("  • Falta de permissão")
    print("  • Erro no driver")
    
print("\n" + "=" * 60)
