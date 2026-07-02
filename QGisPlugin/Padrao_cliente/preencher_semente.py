# -*- coding: utf-8 -*-
"""
Preencher Semente - Provider de Processamento
"""

from qgis.core import QgsProcessingProvider, QgsApplication, QgsMessageLog, Qgis

# Algoritmo
from .preenchimento_alg import PreencherDeSementeAlgorithm


class PadronizacaoProvider(QgsProcessingProvider):
    def id(self):
        # ID estável, sem espaços
        return "padronizacao_tools"

    def name(self):
        # Nome do grupo que aparece no Toolbox
        return "Ferramentas de Padronização"

    def longName(self):
        return self.name()

    def loadAlgorithms(self):
        # Registra seus algoritmos aqui
        self.addAlgorithm(PreencherDeSementeAlgorithm())


class PreencherSemente:
    """Classe principal do plugin (registrar/remover o provider)."""

    def __init__(self, iface):
        self.iface = iface
        self.provider = None

    def initGui(self):
        try:
            self.provider = PadronizacaoProvider()
            QgsApplication.processingRegistry().addProvider(self.provider)
            QgsMessageLog.logMessage(
                "Provider 'Ferramentas de Padronização' registrado.",
                "Preencher Semente", Qgis.Info
            )
        except Exception as e:
            QgsMessageLog.logMessage(
                f"Falha ao registrar provider: {e}",
                "Preencher Semente", Qgis.Critical
            )

    def unload(self):
        try:
            if self.provider:
                QgsApplication.processingRegistry().removeProvider(self.provider)
                QgsMessageLog.logMessage(
                    "Provider 'Ferramentas de Padronização' removido.",
                    "Preencher Semente", Qgis.Info
                )
        except Exception as e:
            QgsMessageLog.logMessage(
                f"Falha ao remover provider: {e}",
                "Preencher Semente", Qgis.Warning
            )
