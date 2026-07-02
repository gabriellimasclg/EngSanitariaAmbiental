# CompiladorEstacoesAnatel

Limpa e remove duplicatas dos registros de estações de telefonia móvel (SMP) da ANATEL para um ou mais municípios: padroniza endereços, agrupa estações duplicadas, junta os valores de geração (2G/3G/4G/5G) e tecnologia, e exporta um CSV por município.

## Como obter os dados

1. Acesse: https://informacoes.anatel.gov.br/paineis/outorga-e-licenciamento/estacoes-do-smp
2. Filtre pelo município ou estado de interesse.
3. Baixe a seção **"Detalhamento de estações"** — este é o arquivo de entrada (`database.xlsx`).

Opcionalmente, https://informacoes.anatel.gov.br/paineis/infraestrutura/panorama tem dados úteis para descrever o sistema telefônico de forma mais ampla (não usado diretamente pelo script).

## Requisitos

```bash
pip install pandas openpyxl
```

## Como organizar os arquivos

Só um arquivo de entrada é necessário:
```python
arquivo  = r"...\database.xlsx"   # o download de "Detalhamento de estações"
repopath = r"..."                  # pasta onde os CSVs de saída são salvos
```
Não precisa de estrutura de pastas específica — defina os dois caminhos no topo do notebook.

## Como usar

```python
cidades = ['Concórdia']   # lista de municípios a processar (deve bater exatamente com a coluna "Município")
```
Rode a célula. Um CSV é gerado por município em `cidades`, chamado `tecnologia_telefonica_{cidade}.csv`.

## O que pode ser alterado

- `cidades` — lista de municípios a filtrar e exportar; adicione quantos quiser.
- Chave de agrupamento — as estações são agrupadas por `Município`, `Número Estação`, `Operadora`, lat/long arredondadas e uma chave de endereço normalizada. Ajuste as colunas do `groupby` para deduplicação mais frouxa/rígida.
- Dicionário `substituicoes` em `formatar_primeiras_maiusculas` — padronização de abreviações (ex.: `Km` → `KM`, `Br` → `BR`); adicione mais abreviações de estado/via conforme necessário.
- `palavras_bonus` em `score_endereco` — palavras-chave (`LOTE`, `QUADRA`, `COLONIA`, `BAIRRO`, `KM`) que aumentam o score de um endereço na hora de escolher a versão "mais completa" entre duplicatas; estenda se aparecerem outros complementos úteis nos seus dados.
- Formato de saída — o CSV é escrito com separador `;`, `,` como decimal e codificação `latin1` (amigável ao Excel-BR); altere os argumentos do `to_csv` se precisar de outro formato.

## Saída

- `tecnologia_telefonica_{cidade}.csv` por município — uma linha por estação deduplicada, com o endereço mais completo escolhido e todos os valores de geração/tecnologia juntos (ex.: `"2G / 3G / 4G"`).
