# PopulacaoBaciaSetorCensitario

Estima população e número de domicílios dentro de uma Área de Prestação de Serviços (APS) e por bacia de esgoto, cruzando dados de setores censitários do IBGE com pontos de domicílios (CNEFE) e shapefiles de bacias/APS. Também calcula extensão de rede e área por bacia.

## Requisitos

```bash
pip install pandas geopandas numpy openpyxl
```

## Como baixar os dados de origem

- **Setores censitários:** https://www.ibge.gov.br/estatisticas/sociais/trabalho/22827-censo-demografico-2022.html?edicao=41852&t=resultados — baixe a malha de setores censitários por UF.
- **Domicílios (CNEFE):** https://www.ibge.gov.br/estatisticas/sociais/populacao/38734-cadastro-nacional-de-enderecos-para-fins-estatisticos.html?edicao=38891&t=resultados — selecione o arquivo do município específico.
  - Encontre o código do município em: https://www.ibge.gov.br/explica/codigos-dos-municipios.php
- **APS (Área de Prestação de Serviços):** encaminhada pela CORSAN.
- **Bacias:** delimitadas pelo analista (deve incluir uma coluna com o nome da bacia).

## Como organizar os arquivos

Defina estes caminhos e parâmetros no topo do notebook (1º Passo):

```python
setores = gpd.read_file(...)            # .gpkg com os setores censitários (por UF)
domicilios = pd.read_csv(..., delimiter=';')  # .csv do CNEFE para o município
aps = gpd.read_file(...)                # .shp com a área de prestação de serviços
bacias = gpd.read_file(...)             # .gpkg/.shp com as bacias delimitadas
coluna_nome_bacias = 'Nome'             # coluna com o nome da bacia em `bacias`
caminho_exportacao = ...                # caminho de saída
crs = "EPSG:31981"                      # CRS projetado em metros, ajuste por região
```

Não precisa de estrutura de pastas fixa — tudo é apontado por caminhos absolutos nessa célula. Só garanta que os quatro insumos sejam do mesmo município/região e que `crs` seja um CRS projetado (em metros) adequado à área.

## O que pode ser alterado

- `crs` — precisa ser um CRS projetado em metros (usado nos cálculos de extensão/área); escolha o EPSG certo para a região.
- `coluna_nome_bacias` — nome da coluna identificadora da bacia na camada `bacias`.
- Filtro de domicílios — atualmente mantém só `COD_ESPECIE == 1` (domicílios particulares); igrejas (`COD_ESPECIE == 8`) são citadas no markdown mas não são de fato filtradas no código — confira isso se precisar dessa exclusão.
- Correção de densidade — conforme a diretriz CORSAN 2025, a densidade domiciliar é recalculada como `v0001 / v0003` (população / total de domicílios particulares) em vez do padrão do IBGE (que só conta domicílios ocupados, `v0007`). Ajuste essa fórmula se a diretriz mudar.
- Camada de vias para extensão de rede — `eixolog` (usado na etapa final "Extensão e Área das Bacias") pode ser trocado por qualquer camada de linhas (ex.: a rede de esgoto real em vez das ruas do OSM).

## Problema conhecido

Na seção "4º Passo", duas linhas que criam `dompart_setores_filtrado` e `bacias_setores_filtrado` estão comentadas, mas ambas as variáveis são usadas algumas células adiante — descomente-as (logo depois do bloco de `sjoin`) ou o cálculo de população por bacia vai falhar com um `NameError`.

## Saída

- `dompart_setores.xlsx` / `bacias_setores.xlsx` — camadas intermediárias cruzadas.
- Resultado final (`resultado_final`, exportado no fim) — tabela por bacia com domicílios, população, % do total e da APS, extensão de rede e área.
