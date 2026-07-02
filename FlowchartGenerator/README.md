# FlowchartGenerator

Generates a Graphviz flowchart from an Excel file describing basin-to-basin sewage connections, colored by node type/classification, with optional legend overlay.

## Requirements

```bash
pip install pandas graphviz pillow openpyxl
```

You also need **Graphviz itself** (not just the Python package) — the `graphviz` pip package only builds the `.dot` file and calls the Graphviz executable to render it.

- Download: https://graphviz.org/download/
- Either install it system-wide and add it to PATH, or use the portable `.zip` and point `graphviz_bin_path` to its `bin/` folder (this is what the example call does).

## Folder structure

```
flowchart/
├── drivers/
│   └── Graphviz-x.x.x-win64/bin/   ← graphviz_bin_path
├── input/
│   └── basins.xlsx
├── legend/
│   └── legend.png                  ← optional
├── output/
└── script.py
```

## Required Excel columns

| Column | Required | Description |
|---|---|---|
| `Bacias` | ✅ | Source node name |
| `bacia_destino` | ✅ | Destination node. Empty → defaults to `"ETE"` |
| `Tipo` | ✅ | `"GRAVIDADE"` (blue edge) or `"RECALQUE"` (red edge); anything else → black |
| `classificacao` / `classificacao_destino` | optional | Stored but **not currently used** to color nodes |
| `color` | optional | Hex color (`#RRGGBB`) to force a node's fill color |

Text is auto-normalized (accents stripped, whitespace collapsed).

## What you can customize

- **Node colors** — in the node-creation loop: prefix rules (`ETE` → gray, `INT` → white), default fallback `#CFE8ED`, or the `color` column.
- **Color palette** (`paleta_pastel`) — defined but unused today; only relevant if you re-enable coloring by `classificacao`.
- **Edge colors** — `{"GRAVIDADE": "blue", "RECALQUE": "red"}` dict.
- **Layout** — `rankdir` (LR/TB), `size`, `dpi`, `nodesep`, `ranksep` in `graph_attr`.
- **Node/edge styling** — font, shape, size, `penwidth` in `node_attr`/`edge_attr`.
- **Legend placement** — `posicao_norm` (x, y as 0–1), `escala` (relative size), `ref_dim` (`"largura"`/`"altura"`/`"menor"`).

## Notes

- Missing required columns → raises `ValueError`.
- `graphviz_bin_path` must point to the folder containing `dot.exe`.
- Missing/invalid `caminho_legenda` → flowchart is still generated, just without the legend.
- Output: `{name}.png` (flowchart), `{name}_com_legenda.png` (with legend, if provided).
