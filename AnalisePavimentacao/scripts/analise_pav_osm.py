# ==========================================================
# OBJETIVO
# ----------------------------------------------------------
# Ler um shapefile linear de trechos, baixar vias do OSM
# na mesma área, comparar espacialmente os dois conjuntos
# e atribuir a cada trecho o tipo de superfície (surface)
# dominante no OSM, com base no MAIOR COMPRIMENTO DE
# SOBREPOSIÇÃO.
#
# Além disso, este script gera PLOTS ao longo do processo
# para você visualizar o que está acontecendo.
# ==========================================================

import warnings
warnings.filterwarnings("ignore")

import geopandas as gpd
import pandas as pd
import osmnx as ox
import matplotlib.pyplot as plt


# ==========================================================
# 1) CONFIGURAÇÕES PRINCIPAIS
# ----------------------------------------------------------
# Ajuste esses parâmetros antes de rodar.
# ==========================================================

ARQ_TRECHOS = r"C:\Users\gabriel.coimbra\Documents\GitHub\EngSanitariaAmbiental\AnalisePavimentacao\inputs\Lote24_semclass.gpkg"                     # shapefile de entrada
ARQ_SAIDA = r"C:\Users\gabriel.coimbra\Documents\GitHub\EngSanitariaAmbiental\AnalisePavimentacao\inputs\Lote24_class.gpkg"         # shapefile de saída
COL_ID = "id"                            # campo único do seu shape

BUFFER_BUSCA_M = 50                             # amplia a área para baixar vias do OSM
TOLERANCIA_MATCH_M = 15                         # buffer no trecho para reduzir erro de desalinhamento
MANTER_APENAS_VIAS_COM_SURFACE = False          # True = descarta vias sem surface antes do processamento
DISTANCIA_MAX_PROPAGACAO_M = 0
USAR_PROPAGACAO_SURFACE = False

# Controle dos plots
PLOTAR = True
TAMANHO_FIG = (10, 10)


# ==========================================================
# 2) FUNÇÕES AUXILIARES
# ==========================================================

def propagar_surface_por_proximidade(vias_osm, distancia_max=15):
    """
    Propaga o valor de 'surface' para vias OSM que estão sem esse atributo,
    usando a via com surface mais próxima, desde que:

    1. a distância seja menor ou igual a 'distancia_max' (em metros);
    2. o valor de 'highway' seja igual.

    Parâmetros
    ----------
    vias_osm : GeoDataFrame
        Camada de vias OSM já em CRS projetado (metros).

    distancia_max : float
        Distância máxima, em metros, para considerar a propagação.

    Retorno
    -------
    vias_resultado : GeoDataFrame
        Mesmo GeoDataFrame de entrada, mas com alguns valores de 'surface'
        preenchidos.

    Observação
    ----------
    Cria também:
    - surface_original : valor original vindo do OSM
    - surface_propagado : valor após tentativa de propagação
    - origem_surface : 'original', 'propagado' ou None
    """
    vias = vias_osm.copy()

    # Guardar o valor original para auditoria
    vias["surface_original"] = vias["surface"]

    # Separar vias com e sem surface
    com_surface = vias[vias["surface"].notna()].copy()
    sem_surface = vias[vias["surface"].isna()].copy()

    # Se não houver o que propagar, devolve como está
    if sem_surface.empty or com_surface.empty:
        vias["surface_propagado"] = vias["surface"]
        vias["origem_surface"] = vias["surface"].apply(
            lambda x: "original" if pd.notna(x) else None
        )
        return vias

    # Índice único temporário
    vias = vias.reset_index(drop=True)
    vias["idx_via"] = vias.index

    com_surface = vias[vias["surface"].notna()].copy()
    sem_surface = vias[vias["surface"].isna()].copy()

    # Vamos usar representative_point() para cada feição,
    # pois funciona melhor do que centroid em linhas estranhas.
    sem_surface_pts = sem_surface.copy()
    sem_surface_pts["geometry"] = sem_surface_pts.geometry.representative_point()

    com_surface_pts = com_surface.copy()
    com_surface_pts["geometry"] = com_surface_pts.geometry.representative_point()

    # Join espacial por nearest
    vizinhas = gpd.sjoin_nearest(
        sem_surface_pts[["idx_via", "highway", "geometry"]],
        com_surface_pts[["idx_via", "highway", "surface", "geometry"]],
        how="left",
        max_distance=distancia_max,
        distance_col="dist_m",
        lsuffix="sem",
        rsuffix="com"
    ).copy()

    # Após o sjoin_nearest, as colunas ficam algo como:
    # idx_via_sem, highway_sem, idx_via_com, highway_com, surface, dist_m
    # Dependendo da versão do geopandas, os nomes podem variar um pouco.
    # Vamos padronizar de forma defensiva.

    colunas = list(vizinhas.columns)

    # Descobrir nomes reais
    col_idx_sem = [c for c in colunas if c.startswith("idx_via") and c != "idx_via"][0] if any(c.startswith("idx_via") and c != "idx_via" for c in colunas) else "idx_via"
    col_highway_sem = [c for c in colunas if c.startswith("highway") and c != "highway"][0] if any(c.startswith("highway") and c != "highway" for c in colunas) else "highway"

    # Coluna da via vizinha
    possiveis_idx_com = [c for c in colunas if "idx_via" in c and c != col_idx_sem]
    possiveis_highway_com = [c for c in colunas if "highway" in c and c != col_highway_sem]

    if len(possiveis_idx_com) == 0 or len(possiveis_highway_com) == 0:
        # fallback seguro
        vias["surface_propagado"] = vias["surface"]
        vias["origem_surface"] = vias["surface"].apply(
            lambda x: "original" if pd.notna(x) else None
        )
        return vias

    col_idx_com = possiveis_idx_com[0]
    col_highway_com = possiveis_highway_com[0]

    # Manter apenas propagação quando highway for igual
    vizinhas_validas = vizinhas[
        vizinhas[col_highway_sem].fillna("") == vizinhas[col_highway_com].fillna("")
    ].copy()

    # Tabela de propagação: idx da via sem surface -> surface da vizinha
    propagacao = vizinhas_validas[[col_idx_sem, "surface", "dist_m"]].copy()
    propagacao = propagacao.rename(columns={col_idx_sem: "idx_via_sem", "surface": "surface_nova"})

    # Aplicar propagação
    vias = vias.merge(
        propagacao[["idx_via_sem", "surface_nova", "dist_m"]],
        left_on="idx_via",
        right_on="idx_via_sem",
        how="left"
    )

    # Surface final propagado
    vias["surface_propagado"] = vias["surface"]

    mask_preencher = vias["surface_propagado"].isna() & vias["surface_nova"].notna()
    vias.loc[mask_preencher, "surface_propagado"] = vias.loc[mask_preencher, "surface_nova"]

    # Origem do valor
    vias["origem_surface"] = None
    vias.loc[vias["surface_original"].notna(), "origem_surface"] = "original"
    vias.loc[vias["surface_original"].isna() & vias["surface_propagado"].notna(), "origem_surface"] = "propagado"

    # Atualizar surface principal
    vias["surface"] = vias["surface_propagado"]

    # Limpeza
    cols_drop = [c for c in ["idx_via_sem", "surface_nova", "dist_m"] if c in vias.columns]
    vias = vias.drop(columns=cols_drop, errors="ignore")

    return vias

def plotar_camadas(camadas, titulo, figsize=(10, 10)):
    """
    Plota várias camadas GeoPandas no mesmo eixo.

    Parâmetros
    ----------
    camadas : list
        Lista de dicionários, cada um com:
        {
            "gdf": GeoDataFrame,
            "color": "red",
            "linewidth": 1,
            "alpha": 0.7,
            "label": "nome da camada"
        }

    titulo : str
        Título do gráfico.
    """
    fig, ax = plt.subplots(1, 1, figsize=figsize)

    for camada in camadas:
        gdf = camada["gdf"]
        color = camada.get("color", "blue")
        linewidth = camada.get("linewidth", 1)
        alpha = camada.get("alpha", 1)
        label = camada.get("label", None)

        # Detecta se é polígono ou linha para plotar adequadamente
        tipos = set(gdf.geometry.geom_type.unique())

        if tipos.intersection({"Polygon", "MultiPolygon"}):
            gdf.plot(ax=ax, facecolor=color, edgecolor=color, alpha=alpha, label=label)
        else:
            gdf.plot(ax=ax, color=color, linewidth=linewidth, alpha=alpha, label=label)

    ax.set_title(titulo)
    ax.set_axis_off()

    # Monta legenda manual simples
    handles, labels = ax.get_legend_handles_labels()
    if labels:
        ax.legend()

    plt.show()


def explode_linhas(gdf):
    """
    Se houver MultiLineString, quebra em feições simples.
    Isso facilita interseções e cálculos de comprimento.
    """
    return gdf.explode(index_parts=False, ignore_index=True)


def normalizar_surface(valor):
    """
    Padroniza o valor do OSM para a lógica desejada:

    - se for pavimentado, mantém o tipo específico;
    - se não for pavimentado, classifica tudo como "Não pavimentado".
    """
    if pd.isna(valor):
        return None

    v = str(valor).strip().lower()

    mapa = {
        # ---------------------------
        # PAVIMENTADOS -> manter tipo
        # ---------------------------
        "asphalt": "Asfalto",
        "concrete": "Concreto",
        "concrete:lanes": "Concreto",
        "concrete:plates": "Concreto",
        "paving_stones": "Bloco/Paver",
        "sett": "Paralelepípedo",
        "cobblestone": "Paralelepípedo",
        "unhewn_cobblestone": "Paralelepípedo",
        "metal": "Metal",
        "wood": "Madeira",
        "grass_paver": "Bloco/Paver",

        # -----------------------------------
        # PAVIMENTADO, MAS TIPO NÃO ESPECÍFICO
        # -----------------------------------
        "paved": "Pavimentado",

        # -----------------------------------
        # NÃO PAVIMENTADOS -> tudo igual
        # -----------------------------------
        "unpaved": "Não pavimentado",
        "compacted": "Não pavimentado",
        "fine_gravel": "Não pavimentado",
        "gravel": "Não pavimentado",
        "pebblestone": "Não pavimentado",
        "dirt": "Não pavimentado",
        "earth": "Não pavimentado",
        "ground": "Não pavimentado",
        "sand": "Não pavimentado",
        "mud": "Não pavimentado",
        "grass": "Não pavimentado",
    }

    return mapa.get(v, v)


def imprimir_resumo_gdf(nome, gdf):
    """
    Imprime informações úteis sobre um GeoDataFrame.
    """
    print("\n" + "=" * 60)
    print(f"RESUMO: {nome}")
    print("=" * 60)
    print(f"Quantidade de feições: {len(gdf)}")
    print(f"CRS: {gdf.crs}")
    print(f"Tipos geométricos: {gdf.geometry.geom_type.value_counts().to_dict()}")
    print("=" * 60)


# ==========================================================
# 3) LEITURA DOS TRECHOS
# ==========================================================

trechos = gpd.read_file(ARQ_TRECHOS)

if trechos.empty:
    raise ValueError("O shapefile de trechos está vazio.")

if trechos.crs is None:
    raise ValueError("O shapefile de trechos está sem CRS definido.")

if COL_ID not in trechos.columns:
    raise ValueError(f"O campo '{COL_ID}' não existe no shapefile.")

# Mantém somente geometrias lineares
trechos = trechos[trechos.geometry.geom_type.isin(["LineString", "MultiLineString"])].copy()
trechos = explode_linhas(trechos)

if trechos.empty:
    raise ValueError("Não foram encontradas geometrias lineares válidas.")

imprimir_resumo_gdf("TRECHOS ORIGINAIS", trechos)

if PLOTAR:
    plotar_camadas(
        camadas=[
            {"gdf": trechos, "color": "blue", "linewidth": 1.2, "alpha": 0.9, "label": "Trechos"}
        ],
        titulo="1. Trechos originais"
    )


# ==========================================================
# 4) GARANTIR CRS PROJETADO
# ----------------------------------------------------------
# Para buffer e comprimento em metros, é melhor trabalhar
# em CRS projetado. Se o seu shape vier em geográfico
# (latitude/longitude), o OSMnx projeta automaticamente.
# ==========================================================

if trechos.crs.is_geographic:
    trechos_proj = ox.projection.project_gdf(trechos)
else:
    trechos_proj = trechos.copy()

imprimir_resumo_gdf("TRECHOS EM CRS PROJETADO", trechos_proj)


# ==========================================================
# 5) CRIAR ÁREA DE BUSCA PARA OSM
# ----------------------------------------------------------
# A ideia é criar um buffer ao redor dos trechos para
# garantir que o bbox de download pegue vias próximas.
# ==========================================================

area_busca_geom = trechos_proj.buffer(BUFFER_BUSCA_M).union_all()
area_busca = gpd.GeoDataFrame(geometry=[area_busca_geom], crs=trechos_proj.crs)

if PLOTAR:
    plotar_camadas(
        camadas=[
            {"gdf": area_busca, "color": "lightgray", "alpha": 0.4, "label": "Área de busca"},
            {"gdf": trechos_proj, "color": "blue", "linewidth": 1.2, "alpha": 1.0, "label": "Trechos"},
        ],
        titulo="2. Área de busca criada a partir dos trechos"
    )

# Converter para WGS84 para montar bbox do OSMnx
area_busca_wgs84 = area_busca.to_crs(4326)
minx, miny, maxx, maxy = area_busca_wgs84.total_bounds

# Formato esperado pelo OSMnx: (left, bottom, right, top)
bbox = (minx, miny, maxx, maxy)

print("\nBBox para consulta no OSM:")
print(f"left={minx}, bottom={miny}, right={maxx}, top={maxy}")


# ==========================================================
# 6) BAIXAR VIAS DO OSM
# ----------------------------------------------------------
# Aqui pedimos todas as feições com tag highway=*.
# Depois vamos filtrar geometrias lineares.
# ==========================================================

tags = {"highway": True}

vias_osm = ox.features_from_bbox(bbox=bbox, tags=tags)

if vias_osm.empty:
    raise ValueError("Nenhuma via OSM foi encontrada na área de busca.")

vias_osm = vias_osm.reset_index()

# Manter apenas linhas
vias_osm = vias_osm[vias_osm.geometry.geom_type.isin(["LineString", "MultiLineString"])].copy()
vias_osm = gpd.GeoDataFrame(vias_osm, geometry="geometry", crs=4326)
vias_osm = explode_linhas(vias_osm)

# Garantir colunas importantes
if "surface" not in vias_osm.columns:
    vias_osm["surface"] = None

if "highway" not in vias_osm.columns:
    vias_osm["highway"] = None

# Reprojetar para o mesmo CRS dos trechos
vias_osm = vias_osm.to_crs(trechos_proj.crs)

# Cortar novamente pela área de busca
vias_osm = vias_osm[vias_osm.intersects(area_busca_geom)].copy()

if MANTER_APENAS_VIAS_COM_SURFACE:
    vias_osm = vias_osm[vias_osm["surface"].notna()].copy()

if vias_osm.empty:
    raise ValueError("As vias OSM ficaram vazias após os filtros aplicados.")

imprimir_resumo_gdf("VIAS OSM", vias_osm)

print("\nTop 15 valores de surface no OSM:")
print(vias_osm["surface"].value_counts(dropna=False).head(15))

if PLOTAR:
    plotar_camadas(
        camadas=[
            {"gdf": area_busca, "color": "lightgray", "alpha": 0.25, "label": "Área de busca"},
            {"gdf": trechos_proj, "color": "red", "linewidth": 1.2, "alpha": 1.0, "label": "Trechos"},
            {"gdf": vias_osm, "color": "black", "linewidth": 0.8, "alpha": 0.7, "label": "Vias OSM"},
        ],
        titulo="3. Trechos sobrepostos às vias baixadas do OSM"
    )

if vias_osm.empty:
    raise ValueError("As vias OSM ficaram vazias após os filtros aplicados.")
    
    
# ==========================================================
# 6.1) PROPAGAR SURFACE ENTRE SEGMENTOS PRÓXIMOS
# ----------------------------------------------------------
# Muitas ruas no OSM estão divididas em vários segmentos,
# e o atributo 'surface' pode estar preenchido em apenas
# um deles. Aqui tentamos copiar esse valor para segmentos
# vizinhos sem surface, desde que:
# - estejam próximos;
# - e tenham o mesmo valor de 'highway'.
# ==========================================================

if USAR_PROPAGACAO_SURFACE:
    print("\nIniciando propagação de 'surface' entre segmentos OSM próximos...")

    qtd_antes = vias_osm["surface"].notna().sum()

    vias_osm = propagar_surface_por_proximidade(
        vias_osm=vias_osm,
        distancia_max=DISTANCIA_MAX_PROPAGACAO_M
    )

    qtd_depois = vias_osm["surface"].notna().sum()
    ganho = qtd_depois - qtd_antes

    print(f"Vias com surface antes da propagação: {qtd_antes}")
    print(f"Vias com surface depois da propagação: {qtd_depois}")
    print(f"Ganhos por propagação: {ganho}")

    if "origem_surface" in vias_osm.columns:
        print("\nOrigem do atributo surface:")
        print(vias_osm["origem_surface"].value_counts(dropna=False))
        
# ==========================================================
# ==========================================================
# 7) SEPARAR VIAS COM E SEM SURFACE
# ----------------------------------------------------------
# Isso ajuda a enxergar o quanto o OSM já está completo
# e quanto foi recuperado pela propagação.
# ==========================================================

vias_com_surface = vias_osm[vias_osm["surface"].notna()].copy()
vias_sem_surface = vias_osm[vias_osm["surface"].isna()].copy()

print("\nCobertura de 'surface' nas vias OSM baixadas:")
print(f"Vias com surface: {len(vias_com_surface)}")
print(f"Vias sem surface: {len(vias_sem_surface)}")

if "origem_surface" in vias_osm.columns:
    vias_surface_original = vias_osm[vias_osm["origem_surface"] == "original"].copy()
    vias_surface_propagado = vias_osm[vias_osm["origem_surface"] == "propagado"].copy()

    print("\nDetalhamento da origem do surface:")
    print(f"Surface original:   {len(vias_surface_original)}")
    print(f"Surface propagado:  {len(vias_surface_propagado)}")

if PLOTAR:
    fig, ax = plt.subplots(1, 1, figsize=(10, 5))
    pd.Series({
        "Com surface": len(vias_com_surface),
        "Sem surface": len(vias_sem_surface)
    }).plot(kind="bar", ax=ax)
    ax.set_title("4. Cobertura do atributo 'surface' nas vias OSM")
    ax.set_ylabel("Quantidade de feições")
    plt.show()

if PLOTAR and len(vias_com_surface) > 0:
    if "origem_surface" in vias_osm.columns:
        plotar_camadas(
            camadas=[
                {"gdf": vias_sem_surface, "color": "gray", "linewidth": 0.5, "alpha": 0.35, "label": "Sem surface"},
                {"gdf": vias_surface_original, "color": "green", "linewidth": 1.0, "alpha": 0.9, "label": "Surface original"},
                {"gdf": vias_surface_propagado, "color": "orange", "linewidth": 1.0, "alpha": 0.9, "label": "Surface propagado"},
                {"gdf": trechos_proj, "color": "red", "linewidth": 1.1, "alpha": 1.0, "label": "Trechos"},
            ],
            titulo="5. Surface original, propagado e trechos"
        )
    else:
        plotar_camadas(
            camadas=[
                {"gdf": vias_sem_surface, "color": "gray", "linewidth": 0.6, "alpha": 0.4, "label": "Vias sem surface"},
                {"gdf": vias_com_surface, "color": "green", "linewidth": 1.0, "alpha": 0.9, "label": "Vias com surface"},
                {"gdf": trechos_proj, "color": "red", "linewidth": 1.2, "alpha": 1.0, "label": "Trechos"},
            ],
            titulo="5. Onde o OSM tem e não tem surface"
        )

# ==========================================================
# 8) CRIAR BUFFER PEQUENO NOS TRECHOS
# ----------------------------------------------------------
# Isso serve para tolerar pequenos desalinhamentos entre
# seu shape e a geometria do OSM.
# ==========================================================

trechos_buf = trechos_proj[[COL_ID, "geometry"]].copy()
trechos_buf["geometry"] = trechos_buf.buffer(TOLERANCIA_MATCH_M)

if PLOTAR:
    plotar_camadas(
        camadas=[
            {"gdf": trechos_buf, "color": "orange", "alpha": 0.35, "label": "Buffer dos trechos"},
            {"gdf": trechos_proj, "color": "blue", "linewidth": 1.0, "alpha": 1.0, "label": "Trechos"},
            {"gdf": vias_osm, "color": "black", "linewidth": 0.8, "alpha": 0.6, "label": "Vias OSM"},
        ],
        titulo="6. Buffer de tolerância usado para encontrar candidatos"
    )


# ==========================================================
# 9) ENCONTRAR VIAS CANDIDATAS POR INTERSEÇÃO
# ----------------------------------------------------------
# Primeiro fazemos um sjoin com o buffer dos trechos.
# Isso reduz muito o volume de comparações.
# ==========================================================

vias_idx = vias_osm.reset_index(drop=True).copy()
vias_idx["via_idx"] = vias_idx.index

candidatos = gpd.sjoin(
    vias_idx[["via_idx", "surface", "highway", "geometry"]],
    trechos_buf[[COL_ID, "geometry"]],
    how="inner",
    predicate="intersects"
).copy()

if candidatos.empty:
    print("\nNenhuma correspondência encontrada.")
    print("Sugestão: aumentar TOLERANCIA_MATCH_M.")
    resultado = trechos.copy()
    resultado["surface_osm"] = None
    resultado["pavimento"] = None
    resultado["comp_surface_m"] = None
    resultado.to_file(ARQ_SAIDA)
    raise SystemExit

print("\nQuantidade de pares via-trecho candidatos:")
print(len(candidatos))


# A geometria ativa ainda é a da via OSM
candidatos = gpd.GeoDataFrame(candidatos, geometry="geometry", crs=trechos_proj.crs)

if PLOTAR:
    # Mostrar apenas uma amostra se ficar visualmente pesado
    candidatos_plot = candidatos.head(2000).copy()

    plotar_camadas(
        camadas=[
            {"gdf": vias_osm, "color": "lightgray", "linewidth": 0.5, "alpha": 0.5, "label": "Todas as vias"},
            {"gdf": candidatos_plot, "color": "purple", "linewidth": 1.2, "alpha": 0.9, "label": "Vias candidatas"},
            {"gdf": trechos_proj, "color": "red", "linewidth": 1.1, "alpha": 1.0, "label": "Trechos"},
        ],
        titulo="7. Vias candidatas após o filtro espacial"
    )


# ==========================================================
# 10) CALCULAR INTERSEÇÃO DA VIA OSM COM O BUFFER DO TRECHO
# ----------------------------------------------------------
# Agora não basta saber que elas estão próximas.
# Queremos a geometria real da parte sobreposta entre a
# via OSM e o trecho.
# ==========================================================
# trazer também a geometria do buffer do trecho

trechos_buf_temp = trechos_buf[[COL_ID, "geometry"]].rename(columns={"geometry": "geom_buffer"})

candidatos = candidatos.merge(
    trechos_buf_temp,
    on=COL_ID,
    how="left"
)

candidatos["geometry"] = candidatos.apply(
    lambda row: row["geometry"].intersection(row["geom_buffer"]),
    axis=1
)

intersec = gpd.GeoDataFrame(
    candidatos[[COL_ID, "via_idx", "surface", "highway", "geometry"]].copy(),
    geometry="geometry",
    crs=trechos_proj.crs
)

intersec = intersec[~intersec.geometry.is_empty].copy()
intersec = intersec[intersec.geometry.notna()].copy()

# Mantém apenas interseções lineares válidas
intersec = intersec[
    intersec.geometry.geom_type.isin(["LineString", "MultiLineString"])
].copy()

intersec["comp_intersec_m"] = intersec.length
intersec = intersec[intersec["comp_intersec_m"] > 0].copy()

if intersec.empty:
    print("\nHouve candidatos, mas nenhuma interseção linear com comprimento > 0.")
    resultado = trechos.copy()
    resultado["surface_osm"] = None
    resultado["pavimento"] = None
    resultado["comp_surface_m"] = None
    resultado.to_file(ARQ_SAIDA)
    raise SystemExit

imprimir_resumo_gdf("INTERSEÇÕES LINEARES", intersec)

if PLOTAR:
    intersec_plot = intersec.head(2000).copy()

    plotar_camadas(
        camadas=[
            {"gdf": trechos_proj, "color": "blue", "linewidth": 1.0, "alpha": 0.8, "label": "Trechos"},
            {"gdf": intersec_plot, "color": "limegreen", "linewidth": 2.0, "alpha": 1.0, "label": "Sobreposição real"},
        ],
        titulo="8. Interseções reais entre trechos e vias OSM"
    )

    fig, ax = plt.subplots(1, 1, figsize=(10, 5))
    intersec["comp_intersec_m"].plot(kind="hist", bins=30, ax=ax)
    ax.set_title("9. Distribuição do comprimento das interseções")
    ax.set_xlabel("Comprimento da interseção (m)")
    plt.show()


# ==========================================================
# 11) AGRUPAR POR TRECHO + SURFACE
# ----------------------------------------------------------
# Para cada trecho, somamos o comprimento de interseção
# por tipo de surface.
# Exemplo:
# trecho 101:
#   asphalt = 120 m
#   paved   = 35 m
# => dominante = asphalt
# ==========================================================

agg = (
    intersec.groupby([COL_ID, "surface"], dropna=False, as_index=False)["comp_intersec_m"]
    .sum()
    .sort_values([COL_ID, "comp_intersec_m"], ascending=[True, False])
)

print("\nTabela agregada (primeiras linhas):")
print(agg.head(20))

# Escolher o surface dominante por trecho
dominante = agg.drop_duplicates(subset=[COL_ID]).copy()
dominante = dominante.rename(columns={"surface": "surface_osm"})

# Criar classe padronizada
dominante["pavimento"] = dominante["surface_osm"].apply(normalizar_surface)
dominante["comp_surface_m"] = dominante["comp_intersec_m"]

print("\nResumo do resultado dominante:")
print(dominante.head(20))

if PLOTAR:
    fig, ax = plt.subplots(1, 1, figsize=(10, 5))
    dominante["surface_osm"].fillna("SEM_DADO").value_counts().head(15).plot(kind="bar", ax=ax)
    ax.set_title("10. Principais valores finais de surface atribuídos aos trechos")
    ax.set_ylabel("Quantidade de trechos")
    plt.show()

    fig, ax = plt.subplots(1, 1, figsize=(10, 5))
    dominante["pavimento"].fillna("SEM_DADO").value_counts().plot(kind="bar", ax=ax)
    ax.set_title("11. Classes padronizadas de pavimento")
    ax.set_ylabel("Quantidade de trechos")
    plt.show()


# ==========================================================
# 12) JUNTAR O RESULTADO AO SHAPE ORIGINAL
# ----------------------------------------------------------
# Agora cada trecho recebe:
# - surface_osm   -> valor bruto do OSM
# - pavimento     -> valor padronizado
# - comp_surface_m -> comprimento usado na decisão
# ==========================================================

resultado = trechos_proj.merge(
    dominante[[COL_ID, "surface_osm", "pavimento", "comp_surface_m"]],
    on=COL_ID,
    how="left"
)

# Voltar ao CRS original do shapefile
resultado = resultado.to_crs(trechos.crs)

# Salvar
resultado.to_file(ARQ_SAIDA, layer="trechos_com_pavimento", driver="GPKG")

print("\n" + "=" * 60)
print("PROCESSAMENTO CONCLUÍDO")
print("=" * 60)
print(f"Arquivo salvo em: {ARQ_SAIDA}")
print(f"Trechos totais: {len(resultado)}")
print(f"Trechos com surface atribuído: {resultado['surface_osm'].notna().sum()}")
print(f"Trechos sem surface atribuído: {resultado['surface_osm'].isna().sum()}")
print(f"Cobertura final (%): {resultado['surface_osm'].notna().mean() * 100:.2f}")
print("=" * 60)

if PLOTAR:
    # Separar trechos com e sem classificação final
    trechos_ok = resultado[resultado["surface_osm"].notna()].copy()
    trechos_nok = resultado[resultado["surface_osm"].isna()].copy()

    plotar_camadas(
        camadas=[
            {"gdf": trechos_nok, "color": "red", "linewidth": 1.8, "alpha": 0.9, "label": "Sem surface"},
            {"gdf": trechos_ok, "color": "green", "linewidth": 1.2, "alpha": 0.9, "label": "Com surface"},
        ],
        titulo="12. Resultado final: trechos classificados e não classificados"
    )

    # Mapa final por classe padronizada
    classes_plot = resultado[resultado["pavimento"].notna()].copy()

    if not classes_plot.empty:
        fig, ax = plt.subplots(1, 1, figsize=(10, 10))
        classes_plot.plot(
            ax=ax,
            column="pavimento",
            legend=True,
            linewidth=1.5
        )
        ax.set_title("13. Mapa final por classe de pavimento")
        ax.set_axis_off()
        plt.show()