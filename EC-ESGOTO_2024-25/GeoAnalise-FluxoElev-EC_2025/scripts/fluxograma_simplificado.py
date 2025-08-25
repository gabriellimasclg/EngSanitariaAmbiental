# -*- coding: utf-8 -*-
"""
Created on Wed Aug  6 13:45:09 2025

@author: gabriel.coimbra
"""
import os
from graphviz import Digraph
import pandas as pd

def gerar_fluxograma_simples(df, repoPath):
    """
    Gera fluxograma entre micro bacias e seus destinos, com cor de aresta
    baseada no tipo de encaminhamento e símbolo especial para ETEs.

    Argumentos:
        df (DataFrame): deve conter colunas 'MICRO BACIA', 'DESTINO', 'ENCAMINHAMENTO'.
        repoPath (str): caminho base do projeto onde será salva a imagem.
    """
    # Configura Graphviz (Windows)
    graphviz_bin_path = os.path.join(repoPath, 'drivers', 'Graphviz-12.2.1-win64', 'bin')
    os.environ["PATH"] += os.pathsep + graphviz_bin_path

    dot = Digraph(
        comment='Fluxograma Alternativa',
        format='png',
        engine='dot',
        graph_attr={
            'rankdir': 'LR',
            'splines': 'polyline',
            'size': '13.5,8.5',
            'dpi': '300',
            'fontname': 'Arial Bold',
            'fontsize': '14',
            'labelloc': 't',
            'nodesep': '0.2',
            'ranksep': '0.3'
        },
        node_attr={
            'fontname': 'Arial Bold',
            'fontsize': '11',
            'shape': 'box',
            'style': 'filled',
            'fillcolor': 'lightblue',
            'width': '0.6',
            'height': '0.3'
        },
        edge_attr={
            'fontname': 'Arial',
            'fontsize': '10',
            'arrowsize': '0.8',
            'penwidth': '1.5'
        }
    )

    for _, row in df.iterrows():
        origem = row['MICRO BACIA']
        destino = str(row['DESTINO']) if pd.notna(row['DESTINO']) else 'ETE'
        tipo_encaminhamento = str(row.get('ENCAMINHAMENTO', '')).strip().upper()

        # Cor da seta
        if tipo_encaminhamento == 'GRAVIDADE':
            cor = 'blue'
        elif tipo_encaminhamento == 'RECALQUE':
            cor = 'red'
        else:
            cor = 'black'

        # Adiciona nós
        dot.node(origem)  # Sempre padrão

        if destino.upper().startswith("ETE"):
            dot.node(destino, shape="ellipse", fillcolor='lightgrey')
        else:
            dot.node(destino)  # padrão

        # Adiciona aresta
        dot.edge(origem, destino, color=cor)

    # Exporta imagem
    output_path = os.path.join(repoPath, 'outputs', 'fluxograma_alt_3.png')
    dot.render(output_path, view=False)
    print(f"Fluxograma salvo em: {output_path}")



df_fluxo = pd.read_excel(
    r'C:\Users\gabriel.coimbra\Downloads\FLUXOGRAMA_ALTERNATIVA 01.xlsx',
    skiprows=1
)[['MICRO BACIA', 'DESTINO', 'ENCAMINHAMENTO']]

# Caminho base do projeto
repoPath = r'C:\Users\gabriel.coimbra\Documents\GitHub\EngSanitariaAmbiental\EC-ESGOTO_2024-25\GeoAnalise-FluxoElev-EC_2025'

# Executar a função
gerar_fluxograma_simples(df_fluxo, repoPath)


df_fluxo = pd.read_excel(
    r'C:\Users\gabriel.coimbra\Downloads\FLUXOGRAMA_ALTERNATIVA 03.xlsx',
    skiprows=1
)[['MICRO BACIA', 'DESTINO', 'ENCAMINHAMENTO']]

# Caminho base do projeto
repoPath = r'C:\Users\gabriel.coimbra\Documents\GitHub\EngSanitariaAmbiental\EC-ESGOTO_2024-25\GeoAnalise-FluxoElev-EC_2025'

# Executar a função
gerar_fluxograma_simples(df_fluxo, repoPath)

