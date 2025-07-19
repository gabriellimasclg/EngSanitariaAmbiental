# -*- coding: utf-8 -*-
"""
Created on Thu May 15 15:16:57 2025

@author: gabriel.coimbra
"""
import os
import geopandas as gpd
import rasterio
import numpy as np
import requests
from shapely.geometry import Point, LineString
from geopandas.tools import sjoin
from funcoes_utilitarias import buscar_cota_online, extrair_cota_com_fallback, interpolar_linha_em_pontos


# --- Geoprocessamento ---

def extrair_atributos_bacia(geometria, bacias):
    """
    Identifica a bacia que contém a geometria fornecida e retorna seus atributos.

    - Para geometrias lineares, considera o ponto inicial da linha.
    - Para pontos ou multipontos, usa diretamente a geometria.

    Argumentos:
        geometria (shapely geometry): ponto, linha ou multilinha a ser avaliada.
        bacias (GeoDataFrame): polígonos de bacia com campos 'nome' e 'etapa'.

    Retorna:
        Tuple[str, str]: nome e etapa da bacia correspondente, ou (None, None) se não encontrado.
    """
    if geometria is None or geometria.is_empty:
        return None, None
    if geometria.geom_type in ['LineString', 'MultiLineString']:
        ponto = Point(geometria.coords[0]) if geometria.geom_type == 'LineString' else Point(geometria.geoms[0].coords[0])
    else:
        ponto = geometria
    for _, bacia in bacias.iterrows():
        if ponto.within(bacia.geometry):
            return bacia['nome'], bacia['etapa']
    return None, None

def carregar_shapefile_com_bacia(caminho, bacias):
    """
    Lê um shapefile de pontos ou linhas e associa cada geometria à bacia correspondente.

    Adiciona duas colunas ao GeoDataFrame:
    - 'nome_bacia': nome da bacia onde a geometria está inserida.
    - 'etapa': etapa correspondente à bacia.

    Argumentos:
        caminho (str): caminho do shapefile a ser carregado.
        bacias (GeoDataFrame): bacias poligonais de referência.

    Retorna:
        GeoDataFrame: shapefile com colunas adicionais de bacia.
    """
    gdf = gpd.read_file(caminho)
    gdf['nome_bacia'], gdf['etapa'] = zip(*gdf['geometry'].apply(lambda geom: extrair_atributos_bacia(geom, bacias)))
    return gdf

def maior_cota_lr(lrs, mde_path):
    """
    Calcula a maior cota ao longo de cada linha de recalque (LR) com base no MDE.
    Se valores do MDE estiverem ausentes, usa API online como fallback.

    Para cada LR:
    - Interpola pontos ao longo da linha.
    - Extrai cota em cada ponto.
    - Identifica a maior cota e o ponto correspondente.

    Argumentos:
        lrs (GeoDataFrame): linhas de recalque com coluna 'nome_bacia'.
        mde_path (str): caminho para o arquivo raster (MDE).

    Retorna:
        GeoDataFrame: com colunas 'bacia_orig', 'cota' e 'geometry' do ponto de maior elevação.
    """
    with rasterio.open(mde_path) as src:
        resultados = []
        for _, lr in lrs.iterrows():
            geom = lr.geometry
            pontos = interpolar_linha_em_pontos(geom)
            cotas = [extrair_cota_com_fallback(p, src) for p in pontos]
            if all(np.isnan(cotas)):
                max_cota = np.nan
                max_ponto = None
            else:
                max_idx = np.nanargmax(cotas)
                max_cota = cotas[max_idx]
                max_ponto = pontos[max_idx]
            resultados.append({
                'bacia_orig': lr['nome_bacia'],
                'cota': max_cota,
                'geometry': Point(max_ponto) if max_ponto else None
            })
        return gpd.GeoDataFrame(resultados, crs=lrs.crs)

def adicionar_cota(gdf, mde_path):
    """
    Adiciona uma coluna 'cota' a um GeoDataFrame de pontos, com base em um MDE.

    Se a cota não estiver disponível no MDE, faz consulta online como fallback.

    Argumentos:
        gdf (GeoDataFrame): pontos (como EEBs) para os quais será atribuída a elevação.
        mde_path (str): caminho do MDE raster.

    Retorna:
        GeoDataFrame: com coluna 'cota' preenchida.
    """
    with rasterio.open(mde_path) as src:
        gdf['cota'] = gdf['geometry'].apply(lambda geom: extrair_cota_com_fallback(geom, src))
    return gdf

def processar_alternativa(df, bacias, lr, pl, sufixo):
    """
    Processa uma alternativa de linha de recalque e integra os dados ao DataFrame principal.

    Para cada bacia de origem:
    - Associa extensão da linha.
    - Cota máxima no trajeto da linha.
    - Bacia de destino (com base no ponto final da linha).

    Argumentos:
        df (DataFrame): tabela principal com as bacias (coluna 'nome').
        bacias (GeoDataFrame): polígonos de bacia.
        lr (GeoDataFrame): linhas de recalque da alternativa.
        pl (GeoDataFrame): pontos de maior cota por LR.
        sufixo (str): identificador da alternativa (ex: 'A1').

    Retorna:
        DataFrame: df atualizado com colunas da alternativa adicionadas.
    """
    ultimos_pontos = [Point(geom.coords[-1]) if geom and not geom.is_empty else None for geom in lr.geometry]
    ultimos_gdf = gpd.GeoDataFrame({'bacia_orig': lr['nome_bacia']}, geometry=ultimos_pontos, crs=lr.crs)
    ultimos_com_bacia = sjoin(ultimos_gdf, bacias, how='left', predicate='within')
    ultimos_com_bacia.rename(columns={'nome': f'bacia_destino_{sufixo}'}, inplace=True)
    lr['extensao_m'] = lr.geometry.length

    temp_df = pl[['bacia_orig', 'cota']].copy()
    temp_df = temp_df.merge(lr[['nome_bacia', 'extensao_m']], left_on='bacia_orig', right_on='nome_bacia', how='left').drop(columns='nome_bacia')
    temp_df = temp_df.merge(ultimos_com_bacia[['bacia_orig', f'bacia_destino_{sufixo}']], on='bacia_orig', how='left')

    temp_df.columns = ['bacia_orig', f'cota_pl_{sufixo}', f'extensao_lr_{sufixo}', f'bacia_destino_{sufixo}']
    df = df.merge(temp_df, left_on='nome', right_on='bacia_orig', how='left')
    return df.drop(columns=['bacia_orig'])