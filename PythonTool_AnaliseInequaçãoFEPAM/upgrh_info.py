# -*- coding: utf-8 -*-
"""
Created on Thu Apr 17 14:51:14 2025

@author: gabriel.coimbra
"""
import requests

def upgrh_info(lat, lon, delta=0.005):
    bbox = f"{lon - delta},{lat - delta},{lon + delta},{lat + delta}"
    
    # URL para consulta da UPG (layer 5)
    url_upg = "https://hsig.sema.rs.gov.br/arcgis/rest/services/1_SIGFEPAM/Mapa_basico_SIGFEPAM/MapServer/5/query"
    
    # URL para consulta do município (layer 2)
    url_muni = "https://hsig.sema.rs.gov.br/arcgis/rest/services/1_SIGFEPAM/Mapa_basico_SIGFEPAM/MapServer/2/query"
    
    params = {
        "f": "json",
        "where": "1=1",
        "geometry": bbox,
        "geometryType": "esriGeometryEnvelope",
        "spatialRel": "esriSpatialRelIntersects",
        "inSR": "4326",
        "outFields": "*",  # Pega todos os campos disponíveis
        "returnGeometry": "false"
    }

    try:
        # Consulta da UPG (layer 5)
        r_upg = requests.get(url_upg, params=params, timeout=10)
        
        # Consulta do município (layer 2)
        r_muni = requests.get(url_muni, params=params, timeout=10)
        
        resultado = {}
        muni = None
        
        # Processa os dados do município
        if r_muni.status_code == 200:
            data_muni = r_muni.json()
            feats_muni = data_muni.get("features", [])
            if feats_muni:
                muni = feats_muni[0]["attributes"].get("NOME", "").strip()
        
        # Processa os dados da UPG
        if r_upg.status_code == 200:
            data_upg = r_upg.json()
            feats_upg = data_upg.get("features", [])
            
            if feats_upg:
                attrs = feats_upg[0]["attributes"]
                # Cria um dicionário formatado
                resultado = {
                    "UPGRH": attrs.get("UPG", "").strip(),
                    "Bacia Hidrográfica": attrs.get("BH", "").strip(),
                    "Código da Bacia": attrs.get("CODIGO_BH", "").strip(),
                    "Região Hidrográfica": attrs.get("RH", "").strip(),
                    "Nome Completo": attrs.get("NOME", "").strip(),
                    "Município": muni  # Adiciona o município ao resultado
                }
                
                # Formata a saída de maneira elegante
                print("\n" + "="*50)
                print("INFORMAÇÕES DA UNIDADE DE GESTÃO HÍDRICA".center(50))
                print("="*50)
                for chave, valor in resultado.items():
                    print(f"• {chave+':':<20} {valor}")
                print("="*50 + "\n")
                
                return resultado
                
            else:
                if delta < 0.5:
                    return upgrh_info(lat, lon, delta*2)  # Corrigido o nome da função
                print("\n⚠️ Nenhum resultado encontrado na área pesquisada")
                return None
                
        print(f"\n⚠️ Erro na consulta: HTTP {r_upg.status_code}")
        return None
        
    except Exception as e:
        print(f"\n⚠️ Erro na conexão: {str(e)}")
        return None
    
    print('\nPor favor, consulte o documento oficial para obter a vazão específica:')
    print('https://www.sema.rs.gov.br/upload/arquivos/202110/19173633-nt-dipla-2021-004-disponibilidade-hidrica.pdf\n')