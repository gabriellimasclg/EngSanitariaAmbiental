# -*- coding: utf-8 -*-
"""
Created on Thu May 15 15:02:15 2025

@author: gabriel.coimbra
"""

import os
import geopandas as gpd
from funcoes_geoprocessamento import carregar_shapefile_com_bacia, maior_cota_lr, adicionar_cota, processar_alternativa

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

    bacias = gpd.read_file(os.path.join(input_path, "BACIAS.shp"))
    eeb = carregar_shapefile_com_bacia(os.path.join(input_path, "EEB.shp"), bacias)
    mde_path = os.path.join(input_path, "MDE.tif")
    df = bacias[['nome']].copy()

    # Adiciona cota para EEBs
    eeb = adicionar_cota(eeb, mde_path)
    eeb_por_bacia = eeb[['nome_bacia', 'cota']].drop_duplicates().rename(columns={'cota': 'cota_eeb'})
    df = df.merge(eeb_por_bacia, left_on='nome', right_on='nome_bacia', how='left').drop(columns='nome_bacia')

    # Define alternativas a serem processadas: (nome_sufixo, nome_arquivo)
    alternativas = [
        ('A1', 'LR1.shp'),
        # Você pode adicionar ou remover linhas aqui conforme necessário
    ]

    for sufixo, nome_arquivo in alternativas:
        print(f"Processando alternativa {sufixo} com arquivo {nome_arquivo}...")
        caminho_lr = os.path.join(input_path, nome_arquivo)

        if not os.path.exists(caminho_lr):
            print(f"Arquivo não encontrado para {sufixo}: {caminho_lr}")
            continue

        lr = carregar_shapefile_com_bacia(caminho_lr, bacias)
        pl = maior_cota_lr(lr, mde_path)
        df = processar_alternativa(df, bacias, lr, pl, sufixo)

    # Exporta resultado - colocar o nome desejado para não subescrever
    df.to_csv(os.path.join(output_path, "resultado_bacias_esgoto_a1.csv"), index=False, sep=';', encoding='utf-8-sig', decimal=',')
    print("Planilha gerada com sucesso!")

if __name__ == "__main__":
    main()