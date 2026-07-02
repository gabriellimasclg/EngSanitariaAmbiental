# ExtratorIndicadoresSNIS

Extrai indicadores selecionados do SNIS (Sistema Nacional de Informações sobre Saneamento) para um município escolhido, ao longo de vários anos, junta tudo em tabelas e gera gráficos de água e de esgoto.

## Como baixar os dados de origem

1. Acesse: https://www.gov.br/cidades/pt-br/acesso-a-informacao/acoes-e-programas/saneamento/snis/produtos-do-snis/diagnosticos-snis
2. Clique em **"Baixar Tabelas"** na seção de água e esgoto.
3. Caminho: `DIAGNOSTICO_TEMATICO_VISAO_GERAL_AE_SNIS_2023_ATUALIZADO` → `Planilhas_AE2022` → `Planilha_AE2022_Completa_Regionais.zip` → `Planilha_AE2022_Completa_Regionais` → *[seu prestador, ex.: `CORSAN`]*
4. Abra o arquivo `Planilha_AE_Indicadores_<PRESTADOR>-<CÓDIGO>` (ex.: `Planilha_AE_Indicadores_CORSAN-43149000`).
5. Para anos anteriores, clique em **"Acesse os Diagnósticos Anteriores"** na mesma página e siga um caminho parecido para achar os arquivos históricos do mesmo município/prestador.

## Como organizar os arquivos

Renomeie cada arquivo baixado só com o **ano**, e adicione **" Info"** para o arquivo de informações daquele ano. O código detecta o tipo do arquivo checando se `"Info"` aparece no nome, e extrai o ano com uma regex procurando um padrão de 4 dígitos `20XX` — então basta que os dois estejam presentes em algum lugar do nome.

Coloque um arquivo `Indicadores` e um `Info` por ano, todos na mesma pasta:
```
Antigo/
├── Resultado/          ← criada automaticamente, saída fica aqui
├── 2018.xlsx
├── 2018 Info.xlsx
├── 2019.xlsx
├── 2019 Info.xlsx
├── 2020.xlsx
├── 2020 Info.xlsx
├── 2021.xlsx
├── 2021 Info.xlsx
├── 2022.xlsx
└── 2022 Info.xlsx
```
Defina essa pasta como `DIRETORIO` no topo do notebook.

## O que o notebook gera

O notebook é dividido em seções, executadas de cima para baixo:

1. **ÁGUA — tabela geral** (`ge12a, ag001, ag021, ag003, ag005, in009, in022, in049`): só a tabela compilada por ano.
2. **ÁGUA — tabela + gráfico de perdas** (`ag006, ag010, ag011, ag024, in049, in013`): gráfico combinado, com **barras** de volumes de água (produzido, consumido, faturado, de serviço) em m³/ano no eixo esquerdo, e **linhas** dos índices de perdas (IN049 – perdas na distribuição %, IN013 – perdas no faturamento) num segundo eixo Y à direita.
3. **ESGOTO — tabela + gráfico** (`es005, es006, es007, es001, es026, in015, in016, es002, es003, es004`): gráfico de **barras agrupadas** por ano dos volumes de esgoto coletado (ES005), tratado (ES006) e faturado (ES007), em m³/ano, com os valores rotulados acima de cada barra.
4. **Resíduos** — seção marcada como *incompleta* no notebook.

## O que pode ser alterado

- `MUNICIPIO_SELECIONADO` — o município alvo (topo do notebook).
- `DIRETORIO` — caminho da pasta com os arquivos do SNIS.
- `INDICADORES_SELECIONADOS` — lista de códigos de indicadores puxados em cada seção. Adicione ou remova códigos conforme necessário; só os que existirem nos arquivos de origem serão mantidos. **Atenção:** os gráficos usam códigos fixos (ex.: `es005`, `ag006`, `in049`) — se remover esses da lista da seção correspondente, o gráfico daquela seção quebra.
- Cores das barras/linhas — definidas direto em cada bloco de gráfico (ex.: `color="lightblue"`, `color="navy"`).
- Posições das linhas de cabeçalho (`header_row_1`, `header_row_2`, `start_row`) — fixas por tipo de arquivo (Info vs Indicadores); ajuste se o layout de algum ano fugir do padrão do SNIS.

## Saída

Dentro de `DIRETORIO/Resultado/`:
- `{MUNICIPIO}_Dados-Agua-Tabela.xlsx` — tabela geral de água.
- `{MUNICIPIO}_Dados-Agua-Grafico.xlsx` + `{MUNICIPIO}_Gráfico-Agua.png` (gráfico de perdas).
- `{MUNICIPIO}_Dados-Esgoto-Tabela.xlsx` + `{MUNICIPIO}_Gráfico-Esgoto.png`.

## Limitação conhecida

Só lê o formato original do SNIS (até 2022). Ainda não trata arquivos do SINISA (2023 em diante), que usam um layout diferente. 