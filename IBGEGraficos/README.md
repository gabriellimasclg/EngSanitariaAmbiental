# IBGEGraficos

Gera gráficos populacionais (gráfico de rosca de população por sexo e pirâmide etária) para um município usando dados do Censo 2022 do portal panorama do IBGE.

## Como obter os dados

Acesse: https://censo2022.ibge.gov.br/panorama/ e selecione o município.

- **População por sexo** — leia os totais de população masculina/feminina direto da página e digite na célula de código (não precisa de arquivo).
- **Pirâmide etária** — baixe a tabela de faixas etárias (população masculina/feminina por grupo de idade) da página do panorama em CSV.

## Requisitos

```bash
pip install pandas matplotlib
```

## Como organizar os arquivos

Só a pirâmide etária precisa de um caminho de arquivo — não precisa de estrutura de pastas fixa, só aponte `caminho_csv` para onde você salvou:
```python
caminho_csv = r"...\piramide_<município>.csv"
```
O CSV deve ser delimitado por `;` e ter pelo menos estas colunas: `Grupo de idade`, `População masculina(pessoas)`, `População feminina(pessoas)`.

## Antes de rodar

`os` é usado (`os.path.join(repopath, ...)`) mas nunca importado, e `repopath` não é definido no notebook — adicione uma célula de setup antes de rodar:
```python
import os
repopath = r"..."   # pasta onde os PNGs serão salvos
```

## Como usar

**População por sexo:**
```python
h = 7098   # população masculina
m = 7597   # população feminina
```

**Pirâmide etária:**
```python
caminho_csv = r"...\piramide_tapes.csv"   # CSV de faixas etárias baixado
pop = 27498                                # população total do município (último censo)
```

## O que pode ser alterado

- `h` / `m` — valores de população masculina/feminina.
- `pop` — população total usada para calcular os rótulos de porcentagem da pirâmide.
- Cores — `colors = ['blue', 'red']` no gráfico de rosca; azul/vermelho também estão fixos para masculino/feminino na pirâmide.
- Deslocamentos `+ 500` / `-500` nas barras da pirâmide — pequeno respiro para os rótulos das faixas não sobreporem as barras; ajuste se os rótulos ficarem apertados ou muito espaçados para um município com população de tamanho diferente.
- Nomes dos arquivos de saída — definidos em cada chamada `plot_*` via `filename`/`save_path`.

## Saída

- `população_por_sexo.png` — gráfico de rosca, população masculina vs. feminina.
- `piramide_etaria.png` — pirâmide etária com % e população absoluta por faixa.
