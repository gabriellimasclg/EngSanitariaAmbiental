from pathlib import Path
import geopandas as gpd
from shapely.geometry import Point
import requests
import os
from datetime import datetime

def area_drenagem(repoPath, lat, lng, name):
    try:
        # Sanitiza o nome para evitar erros no sistema de arquivos
        name_safe = "".join(c for c in name if c.isalnum() or c in (' ', '_')).strip().replace(' ', '_')
        
        # Converte repoPath para Path object se não for
        repo_path = Path(repoPath) if not isinstance(repoPath, Path) else repoPath
        
        # Cria estrutura de diretórios
        output_dir = repo_path / 'outputs'
        geojson_dir = output_dir / f'arquivos_sig_{name_safe}_{datetime.now().strftime("%d.%m.%Y %H.%M")}' / 'geojson'
        bacia_dir = output_dir / f'arquivos_sig_{name_safe}_{datetime.now().strftime("%d.%m.%Y %H.%M")}' / 'bacia_lancamento'
        ponto_dir = output_dir / f'arquivos_sig_{name_safe}_{datetime.now().strftime("%d.%m.%Y %H.%M")}' / 'ponto_lancamento'
        
        # Cria todos os diretórios necessários
        for directory in [output_dir, geojson_dir, bacia_dir, ponto_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        # 1. Cria o shapefile do ponto
        ponto = gpd.GeoDataFrame(
            {'nome': [name_safe]},
            geometry=[Point(lng, lat)],
            crs='EPSG:4326'
        )
        ponto_path = ponto_dir / f'ponto_{name_safe}.shp'
        
        # Tenta deletar arquivos existentes primeiro
        for ext in ['.shp', '.shx', '.dbf', '.prj']:
            old_file = ponto_path.with_suffix(ext)
            if old_file.exists():
                try:
                    os.remove(old_file)
                except PermissionError:
                    print(f"⚠️ Não foi possível remover arquivo existente: {old_file}")
                    return None
        
        ponto.to_file(ponto_path)

        # 2. Requisição à API
        url = f"https://mghydro.com/app/watershed_api?lat={lat}&lng={lng}&precision=high"
        r = requests.get(url=url, timeout=15)
        if r.status_code != 200:
            print(f"⚠️ Erro na API (HTTP {r.status_code})")
            return None
    
        # Salva o GeoJSON
        geojson_path = geojson_dir / f'{name_safe}.geojson'
        with open(geojson_path, 'w', encoding='utf-8') as f:
            f.write(r.text)

        # Processa a resposta
        watershed_gdf = gpd.GeoDataFrame.from_features(r.json()['features'])
        watershed_gdf.set_crs('EPSG:4326', inplace=True)
        watershed_gdf_proj = watershed_gdf.to_crs('ESRI:54009')
        area_km2 = watershed_gdf_proj.geometry.area.values[0] / 1e6
        print(f'A área de drenagem da bacia é: {round(area_km2,2)} km².\n')
        print('Para bacias pequenas, a área pode ser calculada incorretamente. Verificar no site https://mghydro.com/watersheds/ e, caso este esteja sendo calculado incorretamente, deve-se calcular via qgis a bacia e informar a área como entrada da função de análise da inequação')
        print('\n')
        
        alterarArea = input('Deseja alterar a área informada? (s/n): ')
        if alterarArea == 's':
            area_km2 = float(input('Área de Drenagem: '))
            
        # 4. Salva a bacia - primeiro remove arquivos existentes
        shp_path = bacia_dir / f'bacia_{name_safe}'
        
        # Remove arquivos existentes
        for ext in ['.shp', '.shx', '.dbf', '.prj']:
            old_file = shp_path.with_suffix(ext)
            if old_file.exists():
                try:
                    os.remove(old_file)
                except PermissionError:
                    print(f"⚠️ Não foi possível remover arquivo existente: {old_file}")
                    return None
        
        watershed_gdf.to_file(shp_path)
        
        return area_km2
          
    except PermissionError as e:
        print(f"❌ Erro de permissão: {e}")
        print("Por favor, verifique se os arquivos não estão abertos em outro programa.")
        return None
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return None