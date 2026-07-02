# Ferramentas de Engenharia Sanitária e Ambiental

Coleção de ferramentas em Python (e um plugin de QGIS) que apoiam estudos de saneamento e a elaboração de relatórios técnicos municipais: coleta e padronização de dados públicos, análises hidrossanitárias, geração de gráficos e fluxogramas, e conformidade ambiental. Cada ferramenta é independente e vive na sua própria pasta, com README e instruções próprias.

## Como começar

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```
Cada pasta tem seu próprio README com as fontes de dados, o passo a passo e o que pode ser customizado. Comece pelo README da ferramenta que for usar.

## Ferramentas

### Bacias e análises hidrossanitárias
- **PythonTool_PopulacaoBaciaSetorCensitario** — estima população e domicílios por bacia de esgoto cruzando setores censitários do IBGE, pontos do CNEFE e shapefiles de APS/bacias; calcula extensão de rede e área.
- **PythonTool_AnaliseEscoamentoBacias** — compila cotas de estações elevatórias (EEB), a maior cota ao longo de cada linha de recalque, extensão e bacia de destino, usando MDE.
- **PythonTool_GeradorFluxogramas** — gera fluxogramas (Graphviz) das ligações entre bacias de esgoto a partir de um Excel, com cores por tipo de escoamento e legenda.
- **PythonTool_AnaliseInequacaoFEPAM** — avalia a inequação da FEPAM (autodepuração) para um ponto de lançamento, delimitando bacia e vazão de referência; inclui uma planilha alternativa para cálculo manual.

### Dados públicos e indicadores
- **PythonTool_ExtratorIndicadoresSNIS** — extrai e compila indicadores do SNIS por município ao longo dos anos, com tabelas e gráficos de água e esgoto.
- **PythonTool_CompiladorEstacoesAnatel** — limpa e deduplica registros de estações de telefonia móvel (SMP) da ANATEL, exportando um CSV por município.
- **PythonTool_SintetizadorDadosClima** — compila normais climatológicas do INMET para uma estação e plota precipitação e temperatura.

### Gráficos para relatórios
- **PythonTool_IBGEGraficos** — gráficos de população por sexo e pirâmide etária (Censo 2022 do IBGE).
- **PythonTool_SEBRAEGraficos** — conjunto de gráficos do perfil econômico e social municipal (dados do SEBRAE).

### Utilidades
- **PythonTool_ExcelTabelaParaImagem** — converte abas de Excel em imagens recortadas das tabelas (Excel → PDF → JPG).
- **PythonTool_AnalisesSansys** — análise de dados extraídos do Sansys relacionados ao parque de hidrômetros, histórico de ordens de serviço e análise de ligações e economias.

### Plugin QGIS
- **QGisPlugin_PadronizacaoCSVeSIG** — plugin que integra uma camada de geometria, um CSV de atributos e uma camada-modelo ("semente"), padronizando o produto final num GeoPackage e calculando campos geométricos.

## Requisitos gerais

- Algumas ferramentas têm requisitos específicos, detalhados no README de cada pasta:
  - **PythonTool_ExcelTabelaParaImagem** — Windows com Microsoft Excel instalado.
  - **PythonTool_GeradorFluxogramas** — Graphviz instalado (além do pacote pip).
  - **PythonTool_AnaliseInequacaoFEPAM** e o preenchimento de bairro do plugin — dependem de APIs externas (internet).
  - **QGisPlugin_PadronizacaoCSVeSIG** — QGIS 3.20+ com pandas e shapely no ambiente do QGIS.
