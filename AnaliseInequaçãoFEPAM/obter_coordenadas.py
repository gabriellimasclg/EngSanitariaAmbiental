# -*- coding: utf-8 -*-
"""
Created on Wed Apr 23 14:15:32 2025

@author: gabriel.coimbra
"""

def obter_coordenadas():
    while True:
        try:
            entrada = input("Digite a latitude e longitude (separadas por vírgula): ").strip()
            lat, lng = map(float, entrada.split(','))
            return lat, lng, {'lat':lat,'lng':lng}
        except ValueError:
            print("Formato inválido! Digite como no exemplo: -29.660047,-52.78465")