# AnaliseInequacaoFEPAM

Ferramenta de linha de comando que avalia a inequação da FEPAM (Estudo de Autodepuração / EA) para um ponto de lançamento de efluente no Rio Grande do Sul. A partir de coordenadas informadas, o programa identifica a Unidade de Gestão Hídrica e o município, delimita a bacia de drenagem, calcula a vazão de referência e verifica se o efluente atende aos padrões de DBO, E. coli e vazão conforme a CONAMA 357/2005 e as faixas de vazão da FEPAM.

## Requisitos

```bash
pip install pandas geopandas shapely requests
```

Também é preciso conexão com a internet — o programa consulta duas APIs públicas (ver abaixo).

## APIs e fontes de dados usadas

- **UPG e município:** serviço ArcGIS do SIGFEPAM/SEMA-RS (`hsig.sema.rs.gov.br`) — consultado por bounding box em torno do ponto.
- **Área de drenagem:** API do MGHydro (`mghydro.com/app/watershed_api`) — retorna a bacia a montante do ponto como GeoJSON.
- **Vazão específica (qesp):** não é automática — o programa aponta para a Nota Técnica DIPLA 2021-004 da SEMA-RS (https://www.sema.rs.gov.br/upload/arquivos/202110/19173633-nt-dipla-2021-004-disponibilidade-hidrica.pdf) e o usuário digita o valor manualmente.

## Como rodar

```bash
python main.py
```
O programa é interativo (pergunta tudo pelo terminal). O fluxo por análise é:
1. Digite latitude e longitude separadas por vírgula (ex.: `-29.660047,-52.78465`).
2. O programa busca a UPG/município e delimita a bacia, imprimindo a área de drenagem.
3. Confirme ou corrija a área (para bacias pequenas a API pode errar — dá para verificar em https://mghydro.com/watersheds/ e informar um valor calculado no QGIS).
4. Digite a vazão específica (consultada na Nota Técnica).
5. Informe a classe do corpo hídrico (1, 2 ou 3) e a vazão do efluente; opcionalmente sobrescreva DBO e E. coli do efluente.
6. O relatório é impresso e você escolhe se quer salvá-lo e se quer fazer nova análise.

## Estrutura dos arquivos

| Arquivo | Papel |
|---|---|
| `main.py` | Orquestra o fluxo completo; loop interativo de análises |
| `obter_coordenadas.py` | Lê e valida latitude/longitude do usuário |
| `upgrh_info.py` | Consulta UPG, bacia hidrográfica e município via API do SIGFEPAM |
| `area_drenagem.py` | Chama a API do MGHydro, delimita a bacia, calcula área (km²) e salva shapefiles |
| `obter_qesp.py` | Solicita a vazão específica ao usuário |
| `analise_inequacao.py` | Núcleo do cálculo: aplica padrões CONAMA por classe + faixas FEPAM e avalia as três inequações |
| `relatorio.py` | Monta e salva o relatório de texto final |

## O que pode ser alterado

- **Tabela de faixas FEPAM** (`parametrosFEPAM` em `analise_inequacao.py`) — faixas de vazão (m³/dia) e seus limites de DBO/DQO/SST/E. coli/eficiência. Ajuste se a norma mudar.
- **Padrões por classe** (`parametros_classe` em `analise_inequacao.py`) — DBO e coliformes por classe (1/2/3) conforme CONAMA 357/2005.
- **`delta`** em `upgrh_info.py` — meia-largura do bounding box da consulta; o código expande automaticamente (dobra até 0.5) se não achar feição no ponto.
- **`precision=high`** na URL do MGHydro (`area_drenagem.py`) — precisão da delimitação da bacia.
- **CRS de cálculo de área** — `ESRI:54009` (Mollweide) em `area_drenagem.py`.

## Saída

- Relatório de texto (`analise_AAAAMMDD_HHMMSS.txt`) salvo em `Outputs/relatorios/` (um nível acima do diretório de trabalho).
- Shapefiles do ponto de lançamento e da bacia, além do GeoJSON, em `outputs/arquivos_sig_<nome>_<data>/`.

## Alternativa manual: `ExcelAnaliseCompacta.xlsx`

Na mesma pasta há uma planilha (`ExcelAnaliseCompacta.xlsx`, aba única "Inequação FEPAM") que faz **a mesma análise da inequação, porém de forma manual** — útil quando não há internet, quando as APIs falham, ou para conferir/validar o resultado do código. Ela permite comparar até três lançamentos lado a lado (ex.: existente vs. cenários).

Funciona em duas partes:
- **"PREENCHER ABAIXO NO AZUL"** (topo) — você digita manualmente: vazão do efluente (L/s), classe do CHR, área da bacia (km²), vazão específica (para <10 km² e >10 km²), e opcionalmente DBO/eColi do tratamento adotado. Cada célula traz a fonte de onde tirar o dado (SEMA, Nota Técnica DIPLA 004/2021, SIOUT RS, site de exutório).
- **"AUTOMÁTICO ABAIXO"** — o restante calcula sozinho via fórmulas: Qchr, faixa de vazão FEPAM, as três inequações (Qchr/Qe, DBO, eColi), o parâmetro limitante e se atende ou não.

No rodapé ("BASE DE DADOS ABAIXO") ficam as duas tabelas de referência que o código também usa: as faixas de vazão da CONSEMA 355/2017 (DBO, coliformes, eficiência) e os padrões por classe da CONAMA 357/2005. Se atualizar esses valores no código (`parametrosFEPAM` / `parametros_classe`), atualize aqui também para os dois baterem.

## Observações

- O relatório é salvo em `../Outputs/relatorios/` (via `os.path.dirname(os.getcwd())`), enquanto os shapes vão para `outputs/...` relativo ao `repoPath` — repare que há **duas pastas de saída** com caminhos e capitalização diferentes (`Outputs` vs `outputs`). Isso está listado como melhoria pendente nos comentários do `main.py`.
- Depende de os serviços do SIGFEPAM e do MGHydro estarem no ar; sem internet ou se as APIs mudarem, as consultas falham e retornam `None`.
