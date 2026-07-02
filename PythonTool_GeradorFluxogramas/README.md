# GeradorFluxogramas

Gera um fluxograma no Graphviz a partir de um Excel que descreve as ligações entre bacias de esgoto (origem → destino), colorido por tipo/classificação do nó, com sobreposição opcional de legenda.

## Requisitos

```bash
pip install pandas graphviz pillow openpyxl
```

Você também precisa do **Graphviz em si** (não só o pacote Python) — o pacote pip `graphviz` apenas monta o arquivo `.dot` e chama o executável do Graphviz para renderizar.

- Download: https://graphviz.org/download/
- Instale no sistema e adicione ao PATH, ou use o `.zip` portátil e aponte `graphviz_bin_path` para a pasta `bin/` dele (é o que a chamada de exemplo faz).

## Estrutura de pastas

```
fluxograma/
├── drivers/
│   └── Graphviz-x.x.x-win64/bin/   ← graphviz_bin_path
├── input/
│   └── bacias.xlsx
├── legenda/
│   └── legenda.png                 ← opcional
├── output/
└── script.py
```

## Colunas obrigatórias do Excel

| Coluna | Obrigatória | Descrição |
|---|---|---|
| `Bacias` | ✅ | Nome do nó de origem |
| `bacia_destino` | ✅ | Nó de destino. Vazio → vira `"ETE"` |
| `Tipo` | ✅ | `"GRAVIDADE"` (aresta azul) ou `"RECALQUE"` (aresta vermelha); qualquer outro → preto |
| `classificacao` / `classificacao_destino` | opcional | Guardadas mas **não usadas** atualmente para colorir os nós |
| `color` | opcional | Cor hex (`#RRGGBB`) para forçar a cor de preenchimento de um nó |

O texto é normalizado automaticamente (acentos removidos, espaços colapsados).

## O que pode ser alterado

- **Cores dos nós** — no loop de criação de nós: regras por prefixo (`ETE` → cinza, `INT` → branco), cor padrão `#CFE8ED`, ou a coluna `color`.
- **Paleta de cores** (`paleta_pastel`) — definida mas não usada hoje; só relevante se você reativar a coloração por `classificacao`.
- **Cores das arestas** — dicionário `{"GRAVIDADE": "blue", "RECALQUE": "red"}`.
- **Layout** — `rankdir` (LR/TB), `size`, `dpi`, `nodesep`, `ranksep` em `graph_attr`.
- **Estilo de nós/arestas** — fonte, formato, tamanho, `penwidth` em `node_attr`/`edge_attr`.
- **Posição da legenda** — `posicao_norm` (x, y de 0 a 1), `escala` (tamanho relativo), `ref_dim` (`"largura"`/`"altura"`/`"menor"`).

## Observações

- Falta de coluna obrigatória → lança `ValueError`.
- `graphviz_bin_path` precisa apontar para a pasta que contém o `dot.exe`.
- `caminho_legenda` ausente/inválido → o fluxograma é gerado mesmo assim, só sem a legenda.
- Saída: `{nome}.png` (fluxograma) e `{nome}_com_legenda.png` (com legenda, se fornecida).
