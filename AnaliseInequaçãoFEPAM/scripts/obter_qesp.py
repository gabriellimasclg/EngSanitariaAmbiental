# -*- coding: utf-8 -*-
"""
Created on Wed Apr 23 15:00:25 2025

@author: gabriel.coimbra
"""

def obter_qesp():
    print('\n',"Consulte a vazão específica correspondente neste documento:")
    print("https://www.sema.rs.gov.br/upload/arquivos/202110/19173633-nt-dipla-2021-004-disponibilidade-hidrica.pdf\n")

    while True:
        try:
            qesp_input = input('Digite a vazão específica (em m³/s.km² - ex: 0.0028): ').replace(',', '.')
            qesp = float(qesp_input)
            break
        except ValueError:
            print("Valor inválido! Digite um número (use ponto como separador decimal).")
    
    return qesp