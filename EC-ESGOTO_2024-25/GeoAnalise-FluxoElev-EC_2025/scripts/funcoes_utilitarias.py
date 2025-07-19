# -*- coding: utf-8 -*-
"""
Created on Thu May 15 15:15:32 2025

@author: gabriel.coimbra
"""
import os
import geopandas as gpd
import rasterio
import numpy as np
import requests
from shapely.geometry import Point, LineString
from geopandas.tools import sjoin

# --- Funções utilitárias ---

def buscar_cota_online(x, y):
    """
    Consulta a API do OpenTopodata para obter a cota (elevação) de um ponto (x, y)
    quando os dados não estão disponíveis no MDE local.

    Retorna:
        float: valor da elevação em metros ou np.nan se a consulta falhar.
    """
    try:
        response = requests.get(f"https://api.opentopodata.org/v1/srtm90m?locations={y},{x}")
        if response.status_code == 200:
            results = response.json().get('results')
            if results and results[0].get('elevation') is not None:
                return results[0]['elevation']
    except Exception:
        pass
    return np.nan

def extrair_cota_com_fallback(ponto, src):
    """
    Extrai a cota (elevação) de um ponto a partir do MDE raster.
    Se não houver valor válido no MDE ou ocorrer erro, tenta obter a cota via API online.

    Argumentos:
        ponto (shapely.geometry.Point ou MultiPoint): ponto a ser avaliado.
        src (rasterio.DatasetReader): MDE aberto para leitura.

    Retorna:
        float: cota extraída ou np.nan em caso de falha.
    """
    if ponto.is_empty:
        return np.nan

    try:
        if ponto.geom_type == 'MultiPoint':
            x, y = ponto.geoms[0].x, ponto.geoms[0].y
        elif ponto.geom_type == 'Point':
            x, y = ponto.x, ponto.y
        else:
            return np.nan  # Tipo não suportado

        row, col = src.index(x, y)
        valor = src.read(1, window=((row, row+1), (col, col+1)))[0, 0]

        if valor == src.nodata or np.isnan(valor):
            return buscar_cota_online(x, y)
        return valor

    except Exception:
        # Se deu erro antes de x, y, tenta recuperar de novo se possível
        try:
            if ponto.geom_type == 'MultiPoint':
                x, y = ponto.geoms[0].x, ponto.geoms[0].y
            elif ponto.geom_type == 'Point':
                x, y = ponto.x, ponto.y
            else:
                return np.nan
            return buscar_cota_online(x, y)
        except Exception:
            return np.nan


def interpolar_linha_em_pontos(geom, n_amostras=1000):
    """
    Interpola pontos ao longo de uma geometria do tipo LineString ou MultiLineString.
    Converte MultiLineString em LineString contínua e gera uma amostragem uniforme.

    Argumentos:
        geom (shapely.geometry.LineString ou MultiLineString): geometria da linha.
        n_amostras (int): número mínimo de amostras ao longo da linha.

    Retorna:
        list[Point]: lista de pontos interpolados ao longo da linha.
    """
    if geom.geom_type == 'MultiLineString':
        geom = LineString([pt for line in geom for pt in line.coords])
    if not geom.geom_type == 'LineString':
        return []
    n = max(n_amostras, int(geom.length))
    return [geom.interpolate(float(i)/n, normalized=True) for i in range(n + 1)]