# SEBRAEGraphics

Gera um conjunto de gráficos prontos para relatório (rosca, barras, linha) com o perfil econômico e social de um município, usando dados copiados manualmente do portal de perfil municipal do SEBRAE (RS).

## Como obter os dados

Acesse https://datasebrae.com.br/perfil-dos-municipios-gauchos/ e selecione o município. Não há arquivo para download — os números de cada gráfico são lidos da página e digitados direto na célula de código correspondente.

## Requisitos

```bash
pip install matplotlib
```

## Antes de rodar

`os` é usado (`os.path.join(repopath, ...)`) mas nunca importado, e `repopath` não é definido em nenhuma célula. Adicione uma célula de setup antes de rodar qualquer gráfico:
```python
import os
repopath = r"..."   # pasta onde os PNGs serão salvos
```

## Como usar

Cada célula é independente e só precisa dos valores fixos atualizados para o município alvo:

| Seção | Gráfico | Dados a copiar do SEBRAE |
|---|---|---|
| Valor adicionado por setor | 2 roscas | % de Serviço/Indústria/Agropecuária em dois anos + VA total (R$ milhões) |
| Participação de empresas e VA | 2 roscas | % de empresas por setor, % do VA por setor |
| Índice Gini | Barras | Gini de 1991/2000/2010 |
| Renda domiciliar per capita | Barras horizontais | Renda (R$) de 1991/2000/2010 |
| Assistência à Saúde | Barras horizontais | Nº de enfermeiros, médicos, leitos, hospitais |
| Escolaridade | Rosca | População por nível de instrução |
| Energia elétrica | Linha | Nº de consumidores residenciais/não residenciais por ano |

## O que pode ser alterado

- Todos os valores fixos (`valores08`, `gini`, `renda`, `numero`, `quantidade`, `res`/`nres` etc.) — atualize por município/ano.
- Cores — cada gráfico define sua própria lista/hex (ex.: `coresn`, `cores`, `'#ED7D31'`).
- Nomes dos arquivos de saída — definidos em cada `plt.savefig(...)`.
- Estilo — tamanho do furo da rosca (raio do `plt.Circle`), posição da legenda (`bbox_to_anchor`), rótulos e títulos, tudo por célula.

## Saída

Um PNG por gráfico, salvo em `repopath`: `setor economico.png`, `setor economico - 2.png`, `gini_renda.png`, `renda_percapita.png`, `saude.png`, `instrução da população.png`, `energia.png`.
