# -*- coding: utf-8 -*-
"""
Editor Spyder

Este é um arquivo de script temporário.
"""

import pandas as pd

def analise_inequacao(qesp, area_km2):
    
    # Passo 2: Obter parâmetros do usuário
    classe = int(input('Classe do CHR (1, 2 ou 3): '))
    Qe = float(input('Vazão do efluente em L/s: '))
    
    # Valores padrão FEPAM
    dbo_eflu = None
    ecoli_eflu = None
    
    resposta = input('Você gostaria de alterar os parâmetros de DBO e eColi da FEPAM? (s/n): ')
    if resposta.lower() == 's':
        dbo_eflu = int(input('DBO do efluente (mg/L): '))
        ecoli_eflu = int(input('E. coli do efluente (NMP/100mL): '))
        
    def faixa_vazao(parametros, vazao_ls):
        Qe_convertido = vazao_ls * 86.4  # L/s -> m³/dia

        for _, row in parametros.iterrows():
            min_vazao = row['min_m3/dia']
            max_vazao = row['max_m3/dia']

            if pd.isna(max_vazao):
                if Qe_convertido >= min_vazao:
                    return row['dbo_mg/l'], row['eColi_NMP/100mL'], row['faixa']
            elif min_vazao <= Qe_convertido <= max_vazao:
                return row['dbo_mg/l'], row['eColi_NMP/100mL'], row['faixa']
        return None, None, None

    parametrosFEPAM = {
        'faixa': [1, 2, 3, 4, 5, 6],
        'min_m3/dia': [0, 200, 500, 1000, 2000, 10000],
        'max_m3/dia': [199, 499, 999, 1999, 9999, None],
        'dbo_mg/l': [120, 100, 80, 70, 60, 40],
        'dqo_mg/l': [330, 300, 260, 200, 180, 150],
        'sst_mg/l': [140, 100, 80, 70, 60, 50],
        'eColi_NMP/100mL': [None, 1000000, 100000, 100000, 10000, 1000],
        'Eficiência': [None, '90%', '95%', '95%', '95%', '95%']
        }
    
    parametros_classe = {
        'Classe': [1, 2, 3],
        'DBO': [3, 5, 10],
        'Coliformes': [200, 1000, 4000]
    }
    
    parametrosEA = pd.DataFrame(parametrosFEPAM)
    parametrosClasse = pd.DataFrame(parametros_classe)

    dbo_rio = parametrosClasse.loc[parametrosClasse.Classe == classe, 'DBO'].values[0]
    ecoli_rio = parametrosClasse.loc[parametrosClasse.Classe == classe, 'Coliformes'].values[0]
   
    dbo_fepam, ecoli_fepam, faixa_fepam = faixa_vazao(parametrosEA, Qe)
    
    # Só usa a função se dbo_eflu ou ecoli_eflu forem None
    if dbo_eflu is None or ecoli_eflu is None:
        dbo_eflu = dbo_fepam
        ecoli_eflu = ecoli_fepam

    Qchr = round(area_km2 * qesp * 1000,2)  # m³/s * 1000 -> L/s

    ineqQ = round(Qchr / Qe,2)
    ineqDBO = round(dbo_eflu / dbo_rio,2)
    ineqeColi = round(ecoli_eflu / ecoli_rio,2)  

    if (ineqQ >= ineqDBO) and (ineqQ >= ineqeColi):
        limitante = '-'
        atendimento = '✅ O efluente respeita a inequação.'
    elif (ineqQ < ineqDBO) and (ineqQ < ineqeColi):
        limitante = "DBO e eColi"
        atendimento = '❌ O efluente não respeita a inequação'
    elif (ineqQ < ineqDBO):
        limitante = "DBO"
        atendimento = '❌ O efluente não respeita a inequação'
    else:
        limitante = "eColi"
        atendimento = '❌ O efluente não respeita a inequação'
    
    resultado_ineq = {'qesp': qesp,
                      'dbo_efluente': dbo_eflu,
                      'ecoli_efluente': ecoli_eflu,
                      'dbo_padrao': dbo_rio,
                      'ecoli_padrao': ecoli_rio,
                      'Qmin': Qchr,
                      'Limitante': limitante,
                      'Inequação Vazão': round(Qchr/Qe,2),
                      'Inequação eColi': round(ecoli_eflu/ecoli_rio,2),
                      'Inequação DBO': round(dbo_eflu/dbo_rio,2),
                      'resultado_final': atendimento,
                      'dbo_fepam' : dbo_fepam,
                      'ecoli_fepam' : ecoli_fepam,
                      'faixa_fepam' : faixa_fepam,
                      'classe': classe,
                      'Qe': Qe
                      }
        
    return resultado_ineq