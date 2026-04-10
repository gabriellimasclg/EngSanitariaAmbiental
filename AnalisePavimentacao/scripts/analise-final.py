# -*- coding: utf-8 -*-
"""
Created on Fri Mar 13 12:51:47 2026

Esse código serve para ajustar as extensões calculadas pelo QGis de forma a
ficarem coerentes com as encaminhadas pelo cliente


@author: gabriel.coimbra
"""

import pandas as pd
import os

repopath = r'C:\Users\gabriel.coimbra\Documents\GitHub\EngSanitariaAmbiental\AnalisePavimentacao\inputs'

rede = pd.read_csv(os.path.join(repopath,'ConcepcaoLinearAll_v4_Classificado.csv'))

rede_por_municipio = rede.groupby('nm_mun').sum()
rede_por_municipio = pd.DataFrame(rede_por_municipio['comp_surface_m'])

extensao_cliente = pd.read_excel(os.path.join(repopath,'historico qtds.xlsx'))

mesclado = rede_por_municipio.merge(extensao_cliente, left_on="nm_mun", right_on="Municipio")

mesclado['dif']=mesclado['Extensão']-mesclado['comp_surface_m']


mesclado['Extensão'].sum()
mesclado['comp_surface_m'].sum()
