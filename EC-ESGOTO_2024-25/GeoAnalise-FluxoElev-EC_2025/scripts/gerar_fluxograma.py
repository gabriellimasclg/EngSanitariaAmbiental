# -*- coding: utf-8 -*-
"""
Created on Thu May 15 15:56:33 2025

@author: gabriel.coimbra
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from PIL import Image
from graphviz import Digraph
import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
    
def gerar_fluxograma(df, bacias, alt, repoPath):
    """
    Gera um fluxograma visual com cores por etapa de implantação, baseado em uma alternativa (ex: A1).

    Argumentos:
        df (DataFrame): tabela final com colunas 'nome', 'etapa_implantacao' e 'bacia_destino_<alt>'.
        bacias (GeoDataFrame): geometria das bacias com colunas 'nome' e 'etapa'.
        alt (str): nome da alternativa, ex: 'A1'.
        repoPath (str): caminho base do projeto (pasta onde estão 'inputs/' e 'outputs/').

    Saídas:
        Salva imagem 'fluxograma_<alt>_final.png' na pasta 'outputs/'.
    """
    # Configura Graphviz (caso esteja usando em Windows)
    graphviz_bin_path = os.path.join(repoPath, 'drivers', 'Graphviz-12.2.1-win64', 'bin')
    os.environ["PATH"] += os.pathsep + graphviz_bin_path

    # Garante etapa_implantacao no df
    if 'etapa_implantacao' not in df.columns:
        if 'etapa' not in bacias.columns:
            raise ValueError("Coluna 'etapa' não encontrada em bacias.")
        df = df.merge(
            bacias[['nome', 'etapa']].rename(columns={'etapa': 'etapa_implantacao'}),
            on='nome', how='left'
        )

    # Mapeia cores por etapa
    anos_unicos = df['etapa_implantacao'].dropna().unique()
    anos_unicos.sort()
    cores_disponiveis = ['gold','lightblue','lightgreen','pink','violet','orange','cyan','coral','orchid','khaki']
    mapa_ano_cor = {ano: cores_disponiveis[i % len(cores_disponiveis)] for i, ano in enumerate(anos_unicos)}

    a4_size = '16.5,11.7'  # A4 paisagem
    dpi = '300'

    # Criar o grafo com Graphviz
    dot = Digraph(comment=f'Fluxo Alternativa {alt}',
        format='png',
        engine='dot',
        graph_attr={
            'rankdir': 'LR',
            'splines': 'polyline',
            'size': a4_size,
            'dpi': dpi,
            'fontname': 'Arial Bold',
            'fontsize': '14',
            'labelloc': 't',
            'nodesep': '0.3',
            'ranksep': '0.4'
        },
        node_attr={
            'fontname': 'Arial Bold',
            'fontsize': '12',
            'shape': 'box',
            'style': 'filled',
            'width': '0.8',
            'height': '0.4'
        },
        edge_attr={
        'fontname': 'Arial',
        'fontsize': '10',
        'color': 'black',
        'arrowsize': '0.8',    # Aumentado
        'penwidth': '1.5'      # Engrossado
    })

    # Adiciona nós das bacias
    for _, row in df.iterrows():
        cor = mapa_ano_cor.get(row['etapa_implantacao'], 'white')
        dot.node(row['nome'], fillcolor=cor)

    # Adiciona nó da ETE
    dot.node('ETE', 'ETE',
             shape='doubleoctagon',
             width='1.0',
             height='0.6',
             fillcolor='lightgrey')

    # Adiciona arestas
    for _, row in df.iterrows():
        origem  = row['nome']
        destino = row.get(f'bacia_destino_{alt}', 'ETE')
        destino = destino if pd.notna(destino) else 'ETE'
        dot.edge(origem, str(destino))

    # Caminhos de saída
    output_base     = os.path.join(repoPath, 'outputs', f'fluxograma_{alt}')
    fluxograma_path = output_base + '.png'
    legenda_path    = os.path.join(repoPath, 'outputs', 'legenda_temp.png')
    final_path      = os.path.join(repoPath, 'outputs', f'fluxograma_{alt}_final.png')

    # Renderiza imagem do fluxograma
    dot.render(output_base, view=False)

    # Gera legenda com Matplotlib
    def gerar_legenda(mapa_ano_cor, legenda_path):
        
        handles = [
            mpatches.Patch(
                facecolor=cor,
                edgecolor='black',
                linewidth=1.0,
                label=str(ano)
            ) for ano, cor in sorted(mapa_ano_cor.items())
        ]
    
        fig, ax = plt.subplots(figsize=(2.5, len(handles) * 0.1))  # Aumenta o espaço vertical
        ax.axis('off')
    
        legenda = ax.legend(
            handles=handles,
            loc='center left',
            frameon=False,
            handlelength=1.7,     # Aumenta o comprimento da caixinha
            handleheight=1.2,     # Aumenta a altura da caixinha
            handletextpad=0.6,    # Espaço entre caixa e texto
            labelspacing=0.5,     # Espaço entre linhas
            borderaxespad=0
        )
    
        # Estilo do texto: negrito e maior
        for text in legenda.get_texts():
            text.set_fontsize(10)
            text.set_fontweight('bold')
    
        plt.savefig(legenda_path, dpi=300, bbox_inches='tight', transparent=True)
        plt.close()

        
    # Gera a legenda antes de combinar com a imagem
    gerar_legenda(mapa_ano_cor, legenda_path)
    
    # Combina imagens
    def combinar_fluxograma_legenda(fluxograma_path, legenda_path, output_final_path, posicao=(0, 0)):
        base    = Image.open(fluxograma_path).convert("RGBA")
        legenda = Image.open(legenda_path).convert("RGBA")
        bw, bh  = base.size
        lw, lh  = legenda.size
        x, y    = posicao
        if x + lw > bw or y + lh > bh:
            new_w = max(bw, x + lw + 10)
            new_h = max(bh, y + lh)
            canvas = Image.new("RGBA", (new_w, new_h), (255, 255, 255, 0))
            canvas.paste(base, (0, 0))
            base = canvas
        base.paste(legenda, posicao, legenda)
        base.save(output_final_path)

    combinar_fluxograma_legenda(fluxograma_path, legenda_path, final_path, posicao=(0, 0))

    print(f"Fluxograma {alt} finalizado em: {final_path}")


