# -*- coding: utf-8 -*-
"""
Created on Wed Nov 12 14:12:02 2025

@author: gabriel.coimbra
"""

# --- Trecho de Código para __init__.py (início) ---

# Este dicionário contém as bibliotecas externas necessárias.
# Key = nome do módulo para importação; Value = nome amigável para a mensagem de erro.
# -*- coding: utf-8 -*-
"""
Plugin QGIS - Preencher Semente
Autor: Gabriel Coimbra / Nova Engevix
Descrição: Adiciona algoritmo para preencher camada de bacias a partir de CSV.
"""

from qgis.core import Qgis, QgsMessageLog


def classFactory(iface):
    """
    Retorna a classe principal do plugin para o QGIS.
    Faz checagem leve das dependências apenas quando o algoritmo for executado.
    """
    # Importar aqui evita erros de carregamento se bibliotecas estiverem ausentes
    from .preencher_semente import PreencherSemente

    try:
        # Tentativa simples de import para verificar se o ambiente está preparado
        import importlib
        for lib in ["geopandas", "pandas", "fiona", "shapely"]:
            importlib.import_module(lib)
    except ImportError as e:
        # Mostra aviso no painel de mensagens do QGIS, mas permite carregar o plugin
        QgsMessageLog.logMessage(
            f"Aviso: biblioteca ausente ({e.name}). "
            f"Alguns algoritmos podem não funcionar até que ela seja instalada.\n"
            f"Instale no Python do QGIS: pip install {e.name}",
            "Preencher Semente",
            Qgis.Warning
        )

    return PreencherSemente(iface)
