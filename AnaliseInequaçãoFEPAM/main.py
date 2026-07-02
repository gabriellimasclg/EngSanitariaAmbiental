'''
criado por: gabriellimasclg

Esse código realiza a análise da inequação da fepam a partir d um ponto de lan-
çamento informado e parâmetros especificados.

Objetivos futuros:
    - arrumar pastar criadas na área de drenagem (ta criando mta subpasta)
    - retirar a pasta "relatórios" e deixar um nome mais parecido com o dos 
    shapes
    - Colocar comentários e descrições de boas práticas em cada função
    - Antes de pedir se quer mudar a área de drenagem, plotar mapa com ponto de
    laçamento para analisar necessidade de alteração
    - aprender a criar um executável para compartilhar aqui na engevix
'''

import os
from relatorio import criar_pasta_resultados, gerar_relatorio, salvar_relatorio
from analise_inequacao import analise_inequacao
from area_drenagem import area_drenagem
from upgrh_info import upgrh_info
from obter_coordenadas import obter_coordenadas
from obter_qesp import obter_qesp

def main():
    criar_pasta_resultados()
    
    while True:
        print('\n','='*50,'\n',
              'ANÁLISE DA INEQUAÇÃO FEPAM PARA EA'.center(50),
              '='*50,'\n')
        
        # Passo 1: Obter dados básicos
        repoPath = os.path.dirname(os.getcwd())
        
        #Pedir coordenadas
        lat, lng, coord = obter_coordenadas()
        
        #Obter informações da localização
        dados_upg = upgrh_info(lat, lng)
        
        #Obter área de drenagem
        area = area_drenagem(repoPath, lat, lng, dados_upg['Município'])
        
        #Obter vazão específica
        qesp = obter_qesp()
          
        # Rodar a análise
        resultado_ineq = analise_inequacao(qesp, area_km2 = area)
        
        # Organizar resultados para o relatório
        resultado = resultado_ineq | {'area_km2': area} | coord

        # Gerar e mostrar relatório
        relatorio = gerar_relatorio(resultado, dados_upg, qesp)
        print('\n' + relatorio)
        
        # Opção de salvar relatório
        if input('\nDeseja salvar o relatório? (s/n): ').lower() == 's':
            salvar_relatorio(relatorio)
        
        # Opção de nova análise
        if input('\nDeseja realizar nova análise? (s/n): ').lower() != 's':
            break

if __name__ == "__main__":
    main()