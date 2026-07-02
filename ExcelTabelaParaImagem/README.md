# ExcelTabelaParaImagem

Converte abas de Excel em imagens recortadas das tabelas, em duas etapas:
1. Exporta cada aba (seu intervalo usado) como PDF — um PDF por aba.
2. Recorta cada PDF só na área da tabela e salva como JPG de alta qualidade.

## Requisitos

```bash
pip install pymupdf pillow opencv-python numpy pywin32
```

- **Windows + Microsoft Excel instalado** — a etapa 1 automatiza o Excel via COM (`win32com`), então não roda em Mac/Linux nem sem o Excel.
- A etapa 2 só precisa de PyMuPDF, Pillow, OpenCV e NumPy (multiplataforma).

## Como usar

```python
exportar_abas_para_pdf(
    excel_path,                 # caminho do arquivo .xlsx
    output_folder=None,         # None = mesma pasta do Excel
    ajustar_uma_pagina=True,    # ajusta cada aba a uma página
)

crop_pdf_to_table(
    input_folder,   # pasta com os PDFs gerados acima
    output_folder,  # onde os JPGs recortados são salvos
    zoom=4.0,       # multiplicador de resolução (maior = mais nítido)
    quality=100,    # qualidade do JPG
)
```

## O que pode ser alterado

- `ajustar_uma_pagina` — coloque `False` para manter o tamanho de página original da aba em vez de ajustar a uma página.
- Margens e centralização da página — dentro de `exportar_abas_para_pdf`, via `ps.LeftMargin`/`RightMargin`/`TopMargin`/`BottomMargin`.
- `zoom` — controla a resolução/nitidez da imagem recortada.
- `quality` — qualidade de compressão do JPG (1–100).
- Detecção da tabela — o recorte usa limiarização de Otsu + o maior contorno para achar a tabela; ajuste o `cv2.threshold` se alguma aba tiver bordas/artefatos extras sendo pegos no lugar da tabela.

## Observações

- Abas vazias são puladas automaticamente.
- Nomes de abas são higienizados (`\ / * ? : " < > |` → `_`) para evitar nomes de arquivo inválidos.
- Cada página de PDF de uma aba é recortada no seu maior contorno detectado, assumido como a tabela.
