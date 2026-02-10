"""
imprimir_etiquetas.py
---------------------
Impressão DIRETA dos PNGs gerados em 300 DPI
Sem canvas, sem complicação, SÓ PRINT
"""
import os
import subprocess
import sys
from pathlib import Path


def imprimir_pngs_etiquetas(pasta_etiquetas: str, impressora: str = None, copia: int = 1):
    """
    Imprime todos os PNGs da pasta diretamente na impressora
    
    Args:
        pasta_etiquetas: Caminho para pasta com ETIQUETA_*.png
        impressora: Nome da impressora (se None, usa padrão do sistema)
        copia: Número de cópias
    
    Returns:
        (sucesso, mensagem)
    """
    try:
        # Validar pasta
        if not os.path.exists(pasta_etiquetas):
            return False, f"Pasta não existe: {pasta_etiquetas}"
        
        # Listar PNGs
        pngs = sorted(Path(pasta_etiquetas).glob("ETIQUETA_*.png"))
        
        if not pngs:
            return False, f"Nenhuma etiqueta encontrada em {pasta_etiquetas}"
        
        print(f"[IMPRIMIR] Encontrados {len(pngs)} PNGs")
        
        # Usar Windows Print Spooler
        for png_path in pngs:
            try:
                # Comando Windows para imprimir
                cmd = [
                    "rundll32",
                    "shimgvw.dll,ImageView_Fullscreen",
                    str(png_path)
                ]
                
                # Se tiver impressora específica
                if impressora:
                    cmd = [
                        "powershell",
                        "-Command",
                        f'Add-Type -AssemblyName System.Drawing; '
                        f'$doc = New-Object System.Drawing.Bitmap("{png_path}"); '
                        f'$pd = New-Object System.Drawing.Printing.PrintDocument; '
                        f'$pd.PrinterSettings.PrinterName = "{impressora}"; '
                        f'$pd.Add_PrintPage({{ $e.Graphics.DrawImage($doc, 0, 0) }}); '
                        f'$pd.Print()'
                    ]
                
                print(f"  ▶ Imprimindo: {png_path.name}")
                subprocess.run(cmd, check=False)
                
            except Exception as e:
                print(f"  ✗ Erro ao imprimir {png_path.name}: {e}")
        
        return True, f"Impressão de {len(pngs)} etiquetas iniciada!"
        
    except Exception as e:
        return False, f"Erro ao imprimir: {e}"


def imprimir_etiquetas_simples(dxf_arquivo: str, impressora: str = None):
    """
    Fluxo COMPLETO: Gera PNGs + Imprime
    
    Args:
        dxf_arquivo: Arquivo DXF para processar
        impressora: Nome da impressora (opcional)
    
    Returns:
        Mensagem de resultado
    """
    try:
        from core.etiquetas_generator import GeradorEtiquetasDinamico
        
        print(f"[ETIQUETAS] Processando: {dxf_arquivo}")
        
        # Gerar etiquetas PNG
        gerador = GeradorEtiquetasDinamico([dxf_arquivo])
        print(f"[ETIQUETAS] {len(gerador.dados)} barras encontradas")
        
        # Gerar PNGs em 300 DPI
        print(f"[ETIQUETAS] Gerando PNGs...")
        caminhos = gerador.gerar_e_salvar_etiquetas_png(dpi_x=300, dpi_y=300)
        print(f"[ETIQUETAS] ✅ {len(caminhos)} PNGs gerados em {gerador.pasta_etiquetas}")
        
        # Imprimir
        print(f"[IMPRIMIR] Iniciando impressão...")
        sucesso, msg = imprimir_pngs_etiquetas(gerador.pasta_etiquetas, impressora)
        
        return f"✅ {msg}" if sucesso else f"❌ {msg}"
        
    except Exception as e:
        import traceback
        print(f"[ERRO] {e}")
        traceback.print_exc()
        return f"❌ Erro: {e}"


if __name__ == "__main__":
    # Teste
    dxf = r"c:\EngenhariaPlanPro\dxf\#vigas t1-069.DXF"
    resultado = imprimir_etiquetas_simples(dxf)
    print(f"\n{resultado}")
