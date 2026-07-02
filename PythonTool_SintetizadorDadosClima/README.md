# SintetizadorDadosClima

Compila as normais climatológicas do INMET (Instituto Nacional de Meteorologia) para uma estação escolhida, a partir de vários arquivos Excel baixados, juntando tudo em uma tabela e gerando um gráfico de precipitação mensal + temperatura média.

## Como obter os dados climatológicos

1. Procure a estação convencional mais próxima do município em: https://mapas.inmet.gov.br/
2. Baixe os arquivos dessa estação no dox > [_CLIMA INMET](https://dox.novaengevix.com.br/Explorer?f=2b108a6d-6c4d-4bc7-aa49-b28b00e93e93) e use-os no relatório (base de dados: https://portal.inmet.gov.br/normais).

## Requisitos

```bash
pip install pandas matplotlib openpyxl
```

## Como organizar os arquivos

Coloque todos os `.xlsx` baixados da estação alvo numa mesma pasta — o notebook lê todo `.xlsx` em `input_folder` e filtra cada um por `station_code`. Não precisa renomear; cada arquivo só precisa estar no formato padrão do INMET (título na linha 2, cabeçalhos na linha 3, dados a partir da linha 4).

## Como usar

Defina estas três variáveis na célula de código:
```python
input_folder = ...      # pasta com os Excel do INMET baixados
station_code = 83997    # código da estação alvo (como aparece nos arquivos do INMET)
output_file  = ...      # onde salvar a tabela compilada
```
Depois rode a célula (Shift + Enter).

## O que pode ser alterado

- `station_code` — o único filtro aplicado; troque para compilar outra estação.
- Cores/estilo do gráfico — dentro de `gerar_grafico`, ex.: cor das barras `#a5bfe8`, cor da linha `#c46a79`.
- Caminho de saída do gráfico — atualmente salvo como `{input_folder}\{station_code}_gráfico.png`.

## Problema conhecido

A linha que salva a tabela compilada (`final_df.to_excel(output_file, index=False)`) está comentada — só o gráfico é salvo automaticamente. Descomente-a se quiser gravar também o Excel compilado em disco.
