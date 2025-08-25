# -*- coding: utf-8 -*-
"""
Editor Spyder

Este é um arquivo de script temporário.
"""

import geopandas as gpd
import os
import zipfile
from simplekml import Kml
from shapely.geometry import Point
import unicodedata

# Função auxiliar para normalizar nomes de arquivos
def limpar_nome(texto):
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    return texto.replace(" ", "_").replace("/", "-")

# Caminhos de entrada
kmz_path = r"C:\Users\gabriel.coimbra\Downloads\pvs além do aero-rev.kmz"
shapefile_path = r"C:\Users\gabriel.coimbra\Desktop\Meus arquivos\Bombinhas\QGis - Bombinhas\bacias.shp"
output_dir = r"C:\Users\gabriel.coimbra\Desktop\Meus arquivos\Bombinhas\kmzs"
os.makedirs(output_dir, exist_ok=True)

# 1. Extrair KMZ para pegar o KML
with zipfile.ZipFile(kmz_path, 'r') as z:
    kml_filename = [f for f in z.namelist() if f.endswith('.kml')][0]
    z.extract(kml_filename, path=output_dir)

# 2. Carregar pontos do KML (em EPSG:4326)
kml_path = os.path.join(output_dir, kml_filename)
gdf_pontos = gpd.read_file(kml_path)
gdf_pontos.set_crs(epsg=4326, inplace=True)  # Define explicitamente como WGS84

# 3. Carregar os polígonos (SIRGAS 2000 UTM 22S - EPSG:31982)
gdf_poligonos = gpd.read_file(shapefile_path)

# 4. Filtrar pelas etapas desejadas
etapas_desejadas = ["3ª ETAPA", "4ª ETAPA", "5ª ETAPA"]
gdf_poligonos_filtrado = gdf_poligonos[gdf_poligonos["Etapa proj"].isin(etapas_desejadas)]

# 5. Reprojetar os pontos para o mesmo CRS dos polígonos
gdf_pontos_proj = gdf_pontos.to_crs(gdf_poligonos_filtrado.crs)

# 6. Fazer spatial join
gdf_join = gpd.sjoin(gdf_pontos_proj, gdf_poligonos_filtrado, how="inner", predicate='within')

# 7. Para cada polígono, exportar pontos contidos como KMZ (em coordenadas geográficas)
grupos = gdf_join.groupby(["Nome_2", "Etapa proj"])

for (nome2, etapa), grupo in grupos:
    kml = Kml()
    
    # Converter de volta para EPSG:4326 para exportar como KMZ (obrigatório)
    grupo_geo = grupo.to_crs(epsg=4326)
    
    for _, row in grupo_geo.iterrows():
        lon, lat = row.geometry.x, row.geometry.y
        kml.newpoint(name=row.get("Name", "Ponto"), coords=[(lon, lat)])
    
    nome_arquivo = f"{limpar_nome(nome2)}_{limpar_nome(etapa)}_PVs.kmz"
    kml_path = os.path.join(output_dir, nome_arquivo)
    kml.savekmz(kml_path)
    print(f"Exportado: {kml_path}")

