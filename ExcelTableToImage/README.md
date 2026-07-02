# ExcelTableToImage

Converts Excel sheets into cropped table images, in two steps:
1. Exports each worksheet (its used range) as a PDF — one PDF per sheet.
2. Crops each PDF to just the table area and saves it as a high-quality JPG.

## Requirements

```bash
pip install pymupdf pillow opencv-python numpy pywin32
```

- **Windows + Microsoft Excel installed** — step 1 automates Excel via COM (`win32com`), so it won't run on Mac/Linux or without Excel.
- Step 2 only needs PyMuPDF, Pillow, OpenCV and NumPy (cross-platform).

## Usage

```python
exportar_abas_para_pdf(
    excel_path,                 # path to the .xlsx file
    output_folder=None,         # None = same folder as the Excel file
    ajustar_uma_pagina=True,    # fit each sheet to one page
)

crop_pdf_to_table(
    input_folder,   # folder with the PDFs generated above
    output_folder,  # where the cropped JPGs are saved
    zoom=4.0,       # render resolution multiplier (higher = sharper)
    quality=100,    # JPG quality
)
```

## What you can customize

- `ajustar_uma_pagina` — set `False` to keep the sheet's original page size instead of fitting to one page.
- Margins and page centering — inside `exportar_abas_para_pdf`, via `ps.LeftMargin`/`RightMargin`/`TopMargin`/`BottomMargin`.
- `zoom` — controls output resolution/sharpness of the cropped image.
- `quality` — JPG compression quality (1–100).
- Table detection — cropping uses Otsu thresholding + the largest contour to find the table; adjust `cv2.threshold` if a sheet has extra borders/artifacts being picked up instead of the table.

## Notes

- Empty sheets are skipped automatically.
- Sheet names are sanitized (`\ / * ? : " < > |` → `_`) to avoid invalid filenames.
- Each PDF page in a sheet is cropped to its largest detected contour, assumed to be the table.
