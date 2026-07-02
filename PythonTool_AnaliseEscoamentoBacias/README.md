# AnaliseEscoamentoBacias

Compila as cotas das estações elevatórias (EEB), a maior cota ao longo de cada linha de recalque (LR), a extensão da linha e a bacia de destino da rota de escoamento de esgoto de cada bacia.

## Requisitos

```bash
pip install numpy geopandas rasterio requests shapely pyproj tqdm openpyxl
```

## Insumos necessários

Defina estes no topo da seção "Código Principal":

```python
bacias    = gpd.read_file(...)   # polígonos das bacias
coluna_bacias = 'Nome'           # coluna com o nome da bacia em `bacias`
eeb       = ...                  # pontos das estações elevatórias
mde_path  = ...                  # raster MDE principal (.tif)
mde_reserva = ...                # raster MDE de reserva (.tif), usado quando um ponto cai fora/sem dado no principal
caminho_lr = ...                 # linhas de recalque (.gpkg/.shp)
saida     = ...                  # pasta de saída
crs       = "EPSG:31981"         # CRS projetado em metros — ajuste por região
alt_nome  = ...                  # nome desta alternativa/cenário de linha de recalque
```

Todas as camadas devem cobrir o mesmo município/região e ser reprojetáveis para o mesmo `crs`.

## O que pode ser alterado

- `crs` — precisa ser um CRS projetado em metros; escolha o EPSG certo para a região.
- `alt_nome` — identificador livre do cenário/alternativa analisado; é usado como sufixo nas colunas de saída e no nome do arquivo, então dá para reprocessar várias alternativas sem sobrescrever resultados.
- `mde_reserva` — um MDE de reserva de menor resolução, usado só quando o MDE principal não tem dado num ponto; troque por qualquer raster que cubra uma área mais ampla.
- Amostragem da linha — `interpolar_linha_em_pontos(geom, intervalo_m=10.0)` amostra pontos a cada `intervalo_m` metros ao longo de cada linha de recalque antes de extrair as cotas; diminua para mais precisão (mais lento), aumente para mais velocidade. Há também um `interpolar_linha_em_pontos_v0` antigo (número fixo de amostras) mantido no notebook, mas não usado no fluxo principal.

## Problema conhecido

O markdown de introdução menciona um "fallback online" para o MDE, mas o código só lê dois rasters locais (`mde_path` / `mde_reserva`) — não há nenhuma requisição de rede de fato, apesar do `requests` ser importado. Trate a descrição de "fallback online" como desatualizada.

## Saída

- `bacia_destino_{alt_nome}.xlsx` — uma linha por bacia, com a cota da EEB (`cota_eeb`), a cota máxima da linha de recalque, a extensão e a bacia de destino da alternativa.
- `bacia_destino_dropduplicates.csv` — a mesma tabela sem linhas duplicadas.
