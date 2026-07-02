# -*- coding: utf-8 -*-
"""
Created on Thu Apr 24 12:54:59 2025

Parte referente ao relatório criado ao final do processo

@author: gabriel.coimbra
"""
import os
from datetime import datetime

def criar_pasta_resultados():
    """Cria a estrutura de pastas para resultados de forma robusta"""
    repoPath = os.path.dirname(os.getcwd())  # Sobe um nível do diretório atual
    output_path = os.path.join(repoPath, 'Outputs')  # Corrigido os.path.join
    
    # Criar pasta principal de outputs se não existir
    os.makedirs(output_path, exist_ok=True)
    
    # Criar subpastas organizadas
    pastas = [
        'relatorios',
    ]
    
    for pasta in pastas:
        caminho = os.path.join(output_path, pasta)
        os.makedirs(caminho, exist_ok=True)
    
    return output_path

def gerar_relatorio(resultado: dict, dados_upg: dict, qesp: float) -> str:
    """Gera o relatório completo em formato texto"""
    relatorio = f"""
==================================================
         RELATÓRIO DE ANÁLISE FEPAM EA          
==================================================
Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}
Local: {dados_upg['Município']} (UPG {dados_upg['UPGRH']})
Ponto de Lançamento: {resultado['lat']},{resultado['lng']}

PARÂMETROS DA BACIA:
- Área de drenagem: {resultado['area_km2']:.2f} km²
- Vazão específica: {qesp:.4f} m³/s·km²
- Vazão de Referência: {resultado['Qmin']:.2f} L/s

PADRÕES DA CLASSE {resultado['classe']} (CONAMA 357/2005):
- DBO máximo permitido: {resultado['dbo_padrao']} mg/L
- Escherichia coli máximo permitido: {resultado['ecoli_padrao']} NMP/100mL

CARACTERÍSTICAS DO EFLUENTE:
- Vazão lançada (Qe): {resultado['Qe']} L/s (Faixa de vazão FEPAM = {resultado['faixa_fepam']})
- DBO do efluente: {resultado['dbo_efluente']} mg/L (Mínimo FEPAM p/ faixa = {resultado['dbo_fepam']} mg/L)
- Escherichia coli do efluente: {resultado['ecoli_efluente']} NMP/100mL (Mínimo FEPAM p/ faixa = {resultado['ecoli_fepam']} NMP/100mL)

ANÁLISE DAS INEQUAÇÕES:
1) RELAÇÃO DE VAZÕES (Qmin/Qe):
   {resultado['Qmin']:.2f}/{resultado['Qe']} → {resultado['Inequação Vazão']}

2) DBO (efluente/rio):
   {resultado['dbo_efluente']}/{resultado['dbo_padrao']} → {resultado['Inequação DBO']:.2f}

3) Escherichia coli (efluente/rio):
   {resultado['ecoli_efluente']}/{resultado['ecoli_padrao']} → {resultado['Inequação eColi']:.2f}

LIMITANTE: {resultado['Limitante']}

RESULTADO FINAL: {resultado['resultado_final']}
=================================================="""
    return relatorio.strip()

def salvar_relatorio(conteudo: str):
    """Salva o relatório na estrutura organizada de pastas"""
    output_path = criar_pasta_resultados()
    relatorios_path = os.path.join(output_path, 'relatorios')
    
    nome_arquivo = f"analise_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    caminho_completo = os.path.join(relatorios_path, nome_arquivo)
    
    with open(caminho_completo, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    
    print(f"\nRelatório salvo em: {caminho_completo}")
    return caminho_completo