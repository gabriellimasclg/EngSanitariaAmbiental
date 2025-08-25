# -*- coding: utf-8 -*-
"""
Created on Thu May 15 15:02:15 2025

@author: gabriel.coimbra
"""

import os
import geopandas as gpd
from funcoes_geoprocessamento import carregar_shapefile_com_bacia, maior_cota_lr, adicionar_cota, processar_alternativa
from gerar_fluxograma import gerar_fluxograma
# Caminho base
repoPath = os.path.dirname(os.getcwd())
input_path = os.path.join(repoPath, 'inputs')
output_path = os.path.join(repoPath, 'outputs')

# --- Execução ---

def main():
    """
    Este script processa arquivos geográficos para analisar bacias hidrográficas e 
    alternativas de linhas de recalque.

    Entrada esperada (na pasta 'inputs/'):
        - BACIAS.shp: polígonos com campos 'nome' e 'etapa'.
        - EEB.shp: pontos das estações elevatórias (sem campos obrigatórios).
        - MDE.tif: modelo digital de elevação cobrindo a área de estudo.
        - Um ou mais arquivos LR*.shp: linhas de recalque (LineString ou MultiLineString).

    Saída (em 'outputs/resultado_bacias_esgoto.csv'):
        - Para cada bacia: cota da EEB, maior cota ao longo de cada linha de recalque,
        extensão da linha, e bacia de destino da linha.
        - O número de alternativas (LRs) pode variar livremente.

    O script associa automaticamente os dados às bacias e usa o MDE (com fallback
    online) para calcular elevações.
    """
    # Carrega dados principais
    bacias = gpd.read_file(os.path.join(input_path, "BACIAS.shp"))
    eeb = carregar_shapefile_com_bacia(os.path.join(input_path, "EEB.shp"), bacias)
    mde_path = os.path.join(input_path, "MDE.tif")
    caminho_lr = os.path.join(input_path, "LR2.shp")
    
    # Define o nome da alternativa e monta o caminho da linha de recalque
    alt_nome = input("Digite o nome da alternativa (ex: A1): ").strip()

    if not os.path.exists(caminho_lr):
        print(f"Arquivo de linha de recalque não encontrado: {caminho_lr}")
        return

    # DataFrame base com bacias
    df = bacias[['nome', 'etapa']].copy()

    # Cotas das EEBs
    eeb = adicionar_cota(eeb, mde_path)
    eeb_por_bacia = eeb[['nome_bacia', 'cota']].drop_duplicates().rename(columns={'cota': 'cota_eeb'})
    df = df.merge(eeb_por_bacia, left_on='nome', right_on='nome_bacia', how='left').drop(columns='nome_bacia')

    # Processa linha de recalque
    lr = carregar_shapefile_com_bacia(caminho_lr, bacias)
    pl = maior_cota_lr(lr, mde_path)
    df = processar_alternativa(df, bacias, lr, pl, alt_nome)

    # Salva CSV
    df.to_csv(
        os.path.join(output_path, f"resultado_bacias_esgoto_{alt_nome}.csv"),
        index=False,
        sep=';',
        encoding='utf-8-sig',
        decimal=','
    )

    print("Planilha gerada com sucesso!")


if __name__ == "__main__":
    main()
    
gerar_fluxograma()