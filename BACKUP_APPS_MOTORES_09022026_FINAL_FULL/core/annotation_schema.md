```text
ANNOTATION SCHEMA (exemplo e instruções)

Objetivo: criar anotações que permitam treinar um modelo multimodal depois.
Formato por arquivo (JSON): arquivo_nome.json

Estrutura (exemplo):
{
  "file": "####ES-007-R2 - Copia.DXF",
  "scale": 1.0,
  "texts": [
    {"id": 1, "text": "V10", "x": 123.45, "y": 678.90, "layer": "TEXT"},
    {"id": 2, "text": "N1", "x": 130.00, "y": 670.00, "layer": "TEXT"},
    ...
  ],
  "annotations": [
    {
      "viga": "V10",
      "pos": "N1",
      "bitola_mm": 12.5,
      "qty": 25,
      "comp_m": 3.06,
      "material": "CA50",
      "text_ids": [2, 5, 8],   // ids do campo texts que suportam essa anotação
      "bbox": [x1,y1,x2,y2],   // opcional: bbox da região para crop de etiqueta
      "notes": "estribo/long." // opcional
    }
  ]
}

Como anotar (recomendado):
1) Rode o script de debug (core/debug_textos_v2.py) para a viga que deseja anotar:
   python core/debug_textos_v2.py "caminho/arquivo.dxf" --viga V10 --max 200 > debug_v10.txt
2) Abra debug_v10.txt e copie as janelas que correspondem a cada linha anotada.
3) Preencha um JSON conforme esquema acima para cada viga.
4) Envie-me os JSONs (ou cole aqui as partes relevantes).

Observação: se preferir, posso gerar um CSV de anotações a partir das tuas correções no vigas_debug.csv.
```