# Preencher e Padronizar (Modelo Semente)

Plugin de QGIS que integra uma camada vetorial de geometria com uma tabela de atributos (CSV) e uma **camada semente** (modelo com a estrutura de colunas exigida), consolidando os dados e padronizando o produto final num GeoPackage (GPKG) conforme padrões técnicos pré-definidos.

## O que faz

A partir de três camadas já carregadas no QGIS, o algoritmo:
1. Cruza a geometria de entrada com a tabela de atributos por um campo-chave comum.
2. Herda a estrutura de colunas da camada semente (nomes, tipos e tamanhos de campo), garantindo que a saída siga sempre o mesmo padrão.
3. Calcula automaticamente campos geométricos quando existirem na semente e estiverem vazios: `AREA_HA` (hectares), `Shape__Area` (m²), `Shape__Length` (m) e `EXTENSAO` (comprimento em m) — área/perímetro para polígonos, comprimento para linhas.
4. Opcionalmente preenche o campo `BAIRRO` via geocodificação reversa no OpenStreetMap/Nominatim, apenas onde estiver vazio.
5. Exporta a camada padronizada.

## Requisitos

- **QGIS 3.20+** (o cabeçalho do algoritmo indica compatibilidade testada em 3.34+).
- Bibliotecas Python no ambiente do QGIS: `pandas` e `shapely`. Se faltarem, o plugin ainda carrega, mas avisa no painel de mensagens; instale no Python do QGIS com `pip install pandas shapely`.
- `geopy` também é importado (via pasta `vendor/` embutida) para apoio à geocodificação.
- Conexão com a internet **apenas** se usar o preenchimento de `BAIRRO` via OSM.

## Instalação

Copie a pasta do plugin para o diretório de plugins do QGIS:
```
<perfil QGIS>/python/plugins/preencher_semente/
```
Estrutura esperada da pasta:
```
preencher_semente/
├── __init__.py
├── preencher_semente.py      # registra o provider e o botão na toolbar
├── preenchimento_alg.py      # algoritmo de processamento (lógica principal)
├── metadata.txt
├── logo.png                  # ícone do plugin
└── vendor/                   # dependências embutidas (ex.: geopy)
```
Depois ative em *Complementos → Gerenciar e Instalar Complementos*. Um botão aparece na toolbar e o algoritmo fica em *Caixa de Ferramentas de Processamento → Ferramentas de Padronização*.

## Como usar

Antes de rodar, carregue no QGIS: a camada de geometria, a camada semente (modelo) e o CSV de atributos (como "Texto Delimitado").

Parâmetros do algoritmo:

| Parâmetro | Descrição |
|---|---|
| Camada Vetorial de Entrada (Geometria) | Camada com as feições a padronizar |
| Camada Semente (Modelo) | Camada-modelo cuja estrutura de colunas será herdada |
| Tabela de Atributos (CSV) | CSV carregado no QGIS com os atributos a juntar |
| Campo Chave na Camada GIS | Coluna de junção na geometria (padrão: `NOME`) |
| Campo Chave na Tabela (CSV) | Coluna de junção no CSV (padrão: `NOME`) |
| Preencher BAIRRO via OSM | Liga/desliga a geocodificação reversa (padrão: ligado; pode ser lento) |
| Saída (Camada Padronizada) | GPKG de saída |

## O que pode ser alterado

- **Campos-chave** — `GIS_KEY` / `XLS_KEY` (padrão `NOME`); ajuste na execução para a coluna de junção real.
- **Preenchimento de BAIRRO** — desligue o parâmetro `FILL_BAIRRO_OSM` para acelerar quando não precisar do bairro ou não houver internet.
- **Campos geométricos calculados** — `AREA_HA`, `Shape__Area`, `Shape__Length`, `EXTENSAO` só são preenchidos se existirem na semente e estiverem vazios; a existência deles é controlada pela estrutura da camada semente.
- **Estrutura de saída** — definida inteiramente pela camada semente; para mudar o padrão do produto final, troque a semente.

## Observações

- O CSV é lido direto do disco (não pelos valores já interpretados pelo QGIS) e passa por detecção de encoding + normalização de texto, para evitar problemas de acentuação no merge.
- A geometria é preservada da camada de entrada; a lat/lon para o Nominatim usa `pointOnSurface()` em polígonos, o primeiro vértice em linhas e o próprio ponto em pontos.
- O preenchimento de `BAIRRO` depende do Nominatim estar disponível e respeita a política de uso (uma requisição por feição); em bases grandes pode ficar lento.
