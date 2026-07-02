# -*- coding: utf-8 -*-
"""
Algoritmo de processamento QGIS - Preencher e Padronizar (Modelo Semente)
Autor: Gabriel Coimbra / Nova Engevix
Compatível com QGIS 3.34+
Sem dependência de geopandas/fiona; usa pandas + shapely + PyQGIS
"""

from datetime import datetime, date, time
import pandas as pd

from qgis.PyQt.QtCore import QVariant
from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingParameterVectorLayer,
    QgsProcessingParameterString,
    QgsProcessingParameterFeatureSink,
    QgsProcessingException,
    QgsProcessing,
    QgsWkbTypes,
    QgsFields, QgsField, QgsFeature, QgsGeometry,
    QgsCoordinateTransform, QgsProject,           # <-- novo
    QgsMessageLog, Qgis
)

from shapely import wkb as shwkb
from shapely.geometry import (
    Point, MultiPoint, LineString, MultiLineString,
    Polygon, MultiPolygon
)


# ----------------------------------------------------------------------
# FUNÇÕES AUXILIARES
# ----------------------------------------------------------------------
def _clean_empty(v):
    """Converte valores 'vazios' para None: pd.NA, NaN, '', ' '."""
    try:
        import pandas as _pd
        if _pd.isna(v):
            return None
    except Exception:
        pass

    if v is None:
        return None
    if isinstance(v, float) and (v != v):  # NaN
        return None
    if isinstance(v, str) and v.strip() == "":
        return None
    return v


def _coerce_to_type(v, qvtype):
    """
    Converte valor Python para o tipo esperado pelo campo do QGIS (QVariant).
    Suporta:
      - Date: "2024" -> 2024-01-01 ; "03/2024" ou "2024-03" -> 2024-03-01
      - DateTime: idem, com 00:00:00
    """
    from datetime import datetime, date, time
    import re

    def _to_int(x):
        # cobre "2026", "2026.0", 2026.0
        try:
            if isinstance(x, str):
                x = x.replace(",", ".")
            f = float(x)
            return int(round(f))
        except Exception:
            return None

    def _parse_year_or_month_year_to_date(s):
        s = str(s).strip()
        # Ano puro (quatro dígitos)
        if re.fullmatch(r"\d{4}", s):
            return date(int(s), 1, 1)
        # "MM/AAAA" | "M/AAAA" | "AAAA-MM" | "AAAA-M"
        m = re.fullmatch(r"(\d{1,2})[/-](\d{4})", s)  # MM-AAAA ou MM/AAAA
        if m:
            mm, yyyy = int(m.group(1)), int(m.group(2))
            if 1 <= mm <= 12:
                return date(yyyy, mm, 1)
        m = re.fullmatch(r"(\d{4})[/-](\d{1,2})", s)  # AAAA-MM ou AAAA/M
        if m:
            yyyy, mm = int(m.group(1)), int(m.group(2))
            if 1 <= mm <= 12:
                return date(yyyy, mm, 1)
        return None

    v = _clean_empty(v)
    if v is None:
        return None

    try:
        # --- Inteiros / Doubles / Bool
        if qvtype in (QVariant.Int, QVariant.UInt, QVariant.LongLong, QVariant.ULongLong):
            iv = _to_int(v)
            return iv if iv is not None else None

        if qvtype in (QVariant.Double,):
            if isinstance(v, str):
                v = v.replace(",", ".")
            return float(v)

        if qvtype in (QVariant.Bool,):
            if isinstance(v, str):
                return v.strip().lower() in ("1", "true", "t", "yes", "y", "sim")
            return bool(v)

        # --- Date
        if qvtype in (QVariant.Date,):
            # já é date/datetime
            if isinstance(v, date) and not isinstance(v, datetime):
                return v
            if isinstance(v, datetime):
                return v.date()
            # ano puro ou mês/ano
            d = _parse_year_or_month_year_to_date(v)
            if d:
                return d
            # inteiro numérico (ex: 2026.0 vindo do Excel)
            iv = _to_int(v)
            if iv is not None and 1000 <= iv <= 9999:
                return date(iv, 1, 1)
            # formatos completos
            if isinstance(v, str):
                for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
                    try:
                        return datetime.strptime(v.strip(), fmt).date()
                    except Exception:
                        pass
            return None

        # --- DateTime
        if qvtype in (QVariant.DateTime,):
            if isinstance(v, datetime):
                return v
            if isinstance(v, date):
                return datetime(v.year, v.month, v.day)
            d = _parse_year_or_month_year_to_date(v)
            if d:
                return datetime(d.year, d.month, d.day)
            iv = _to_int(v)
            if iv is not None and 1000 <= iv <= 9999:
                return datetime(iv, 1, 1, 0, 0, 0)
            if isinstance(v, str):
                for fmt in ("%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M:%S", "%Y-%m-%dT%H:%M:%S",
                            "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
                    try:
                        dt = datetime.strptime(v.strip(), fmt)
                        if fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
                            return datetime(dt.year, dt.month, dt.day, 0, 0, 0)
                        return dt
                    except Exception:
                        pass
            return None

        # --- Time
        if qvtype in (QVariant.Time,):
            if isinstance(v, time):
                return v
            if isinstance(v, str):
                for fmt in ("%H:%M:%S", "%H:%M"):
                    try:
                        return datetime.strptime(v.strip(), fmt).time()
                    except Exception:
                        pass
            return None

        # --- Texto
        return str(v)

    except Exception:
        return None


def _ajustar_geom_para_tipo(g, geom_exp: str):
    """Converte a geometria shapely 'g' para o tipo 'geom_exp' quando possível."""
    if g is None:
        return None
    exp = (geom_exp or "").lower()
    gtype = (getattr(g, "geom_type", "") or "").lower()

    # Pontos
    if exp == "point":
        if gtype == "point":
            return g
        if gtype == "multipoint":
            geoms = list(g.geoms)
            return geoms[0] if geoms else None
        return g

    if exp == "multipoint":
        if gtype == "point":
            return MultiPoint([g])
        if gtype == "multipoint":
            return g
        return g

    # Linhas
    if exp == "linestring":
        if gtype == "linestring":
            return g
        if gtype == "multilinestring":
            geoms = list(g.geoms)
            return geoms[0] if geoms else None
        return g

    if exp == "multilinestring":
        if gtype == "linestring":
            return MultiLineString([g])
        if gtype == "multilinestring":
            return g
        return g

    # Polígonos
    if exp == "polygon":
        if gtype == "polygon":
            return g
        if gtype == "multipolygon":
            geoms = list(g.geoms)
            return max(geoms, key=lambda p: p.area) if geoms else None
        return g

    if exp == "multipolygon":
        if gtype == "polygon":
            return MultiPolygon([g])
        if gtype == "multipolygon":
            return g
        return g

    return g


def _layer_to_dataframe(vl, want_geometry=False):
    """Converte uma QgsVectorLayer em pandas.DataFrame. Se want_geometry=True,
    inclui coluna '__geometry__' com objetos shapely (ou None)."""
    fields = [f.name() for f in vl.fields()]
    rows = []
    for feat in vl.getFeatures():
        row = {name: feat[name] for name in fields}
        if want_geometry and feat.hasGeometry():
            try:
                row["__geometry__"] = shwkb.loads(bytes(feat.geometry().asWkb()))
            except Exception:
                row["__geometry__"] = None
        elif want_geometry:
            row["__geometry__"] = None
        rows.append(row)
    df = pd.DataFrame(rows)
    return df


def _expected_geom_from_layer(layer):
    """Retorna 'point'/'multipoint'/'linestring'/'multilinestring'/'polygon'/'multipolygon' para a camada dada."""
    wkb = layer.wkbType()
    is_multi = QgsWkbTypes.isMultiType(wkb)
    gtype = QgsWkbTypes.geometryType(wkb)

    if gtype == QgsWkbTypes.PointGeometry:
        return "multipoint" if is_multi else "point"
    if gtype == QgsWkbTypes.LineGeometry:
        return "multilinestring" if is_multi else "linestring"
    if gtype == QgsWkbTypes.PolygonGeometry:
        return "multipolygon" if is_multi else "polygon"
    return ""  # unknown / NoGeometry


def _pick(row, name):
    """Pega valor de 'name', lidando com colisões de merge (_x/_y)."""
    if name in row:
        return row[name]
    if f"{name}_x" in row and pd.notna(row[f"{name}_x"]):
        return row[f"{name}_x"]
    if f"{name}_y" in row and pd.notna(row[f"{name}_y"]):
        return row[f"{name}_y"]
    return None


# ----------------------------------------------------------------------
# CLASSE PRINCIPAL: O Algoritmo de Processamento
# ----------------------------------------------------------------------
class PreencherDeSementeAlgorithm(QgsProcessingAlgorithm):
    INPUT_LAYER = 'INPUT_LAYER'
    SEED_LAYER = 'SEED_LAYER'
    TABLE_LAYER = 'TABLE_LAYER'
    GIS_KEY = 'GIS_KEY'
    XLS_KEY = 'XLS_KEY'
    OUTPUT_GPKG = 'OUTPUT_GPKG'

    def name(self):
        return 'preencher_de_semente_core'

    def displayName(self):
        return 'Preencher e Padronizar (Modelo Semente)'

    def group(self):
        return 'Ferramentas de Padronização'

    def groupId(self):
        return 'padronizacao_tools'

    def createInstance(self):
        return PreencherDeSementeAlgorithm()

    # ------------------------------------------------------------------
    # Parâmetros do algoritmo (apenas camadas internas do QGIS)
    # ------------------------------------------------------------------
    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.INPUT_LAYER,
                'Camada Vetorial de Entrada (Geometria)',
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.SEED_LAYER,
                'Camada Semente (Modelo) - carregada no QGIS',
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.TABLE_LAYER,
                'Tabela de Atributos (CSV carregado no QGIS)',
                [QgsProcessing.TypeVector]  # inclui NoGeometry carregada como "Texto Delimitado"
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                self.GIS_KEY, 'Campo Chave na Camada GIS', defaultValue='NOME'
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                self.XLS_KEY, 'Campo Chave na Tabela (CSV)', defaultValue='NOME'
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT_GPKG, 'Saída (Camada Padronizada)'
            )
        )

    # ------------------------------------------------------------------
    # Lógica principal de execução
    # ------------------------------------------------------------------
    def processAlgorithm(self, parameters, context, feedback):
        # 1) Obter camadas
        vl_in = self.parameterAsVectorLayer(parameters, self.INPUT_LAYER, context)
        seed_layer = self.parameterAsVectorLayer(parameters, self.SEED_LAYER, context)
        tbl_layer = self.parameterAsVectorLayer(parameters, self.TABLE_LAYER, context)
        if vl_in is None:
            raise QgsProcessingException("Selecione a camada vetorial de entrada (INPUT_LAYER).")
        if seed_layer is None:
            raise QgsProcessingException("Selecione a camada Semente (SEED_LAYER).")
        if tbl_layer is None:
            raise QgsProcessingException("Selecione a Tabela (TABLE_LAYER).")

        chave_gis = self.parameterAsString(parameters, self.GIS_KEY, context)
        chave_xls = self.parameterAsString(parameters, self.XLS_KEY, context)

        # 2) Converter camadas para DataFrames
        feedback.pushInfo("Lendo camadas do QGIS (entrada, semente, tabela)...")
        df_in = _layer_to_dataframe(vl_in, want_geometry=True)
        df_tbl = _layer_to_dataframe(tbl_layer, want_geometry=False)

        if chave_gis not in df_in.columns:
            raise QgsProcessingException(f"O campo '{chave_gis}' não existe na camada de entrada.")
        if chave_xls not in df_tbl.columns:
            raise QgsProcessingException(f"O campo '{chave_xls}' não existe na tabela CSV.")

        # 3) Padronizar chaves e merge
        df_in["__key__"] = df_in[chave_gis].astype(str).str.strip()
        df_tbl["__key__"] = df_tbl[chave_xls].astype(str).str.strip()
        df_join = pd.merge(df_in, df_tbl, on="__key__", how="left")

        # 4) Esquema/tipo de geometria e CRS
        fields_out = seed_layer.fields()
        field_names = [f.name() for f in fields_out]

        seed_wkb = seed_layer.wkbType()
        in_wkb = vl_in.wkbType()

        # Se a semente não tiver geometria, usa o tipo da camada de entrada
        if QgsWkbTypes.geometryType(seed_wkb) in (QgsWkbTypes.NullGeometry,) or seed_wkb == QgsWkbTypes.NoGeometry:
            wkb_out = in_wkb
            geom_exp = _expected_geom_from_layer(vl_in)
            feedback.pushWarning(
                f"Semente sem geometria. Usando tipo da entrada: {QgsWkbTypes.displayString(in_wkb)}"
            )
        else:
            wkb_out = seed_wkb
            geom_exp = _expected_geom_from_layer(seed_layer)

        # **CRS de saída = CRS da CAMADA DE ENTRADA** (garantimos coerência)
        crs_in = vl_in.crs()
        crs_seed = seed_layer.crs()
        crs_out = crs_in

        feedback.pushInfo(
            "Geometrias/CRS — "
            f"Seed: {QgsWkbTypes.displayString(seed_wkb)} / {crs_seed.authid() or 'sem CRS'} | "
            f"Input: {QgsWkbTypes.displayString(in_wkb)} / {crs_in.authid() or 'sem CRS'} | "
            f"Saída: {QgsWkbTypes.displayString(wkb_out)} / {crs_out.authid() or 'sem CRS'}"
        )

        # 5) Criar FeatureSink de saída com o WKB e CRS definidos acima
        sink, dest_id = self.parameterAsSink(
            parameters, self.OUTPUT_GPKG, context,
            fields_out, wkb_out, crs_out
        )
        if sink is None:
            raise QgsProcessingException("Não foi possível criar a camada de saída.")

        # Transformador, se por algum motivo decidirmos transformar (aqui não precisa, out=crs_in)
        transformer = None
        if crs_in.isValid() and crs_out.isValid() and crs_in != crs_out:
            transformer = QgsCoordinateTransform(crs_in, crs_out, QgsProject.instance())

        sem_geom = 0
        total = len(df_join)

        # 6) Loop de features
        for i, row in enumerate(df_join.itertuples(index=False, name=None)):
            if feedback.isCanceled():
                break
            if total:
                feedback.setProgress(int(i / total * 100))

            row_dict = dict(zip(df_join.columns, row))

            # Geometria original vinda do INPUT
            shp = row_dict.get("__geometry__", None)

            # Ajustar para o tipo esperado na saída
            shp_adj = _ajustar_geom_para_tipo(shp, geom_exp)

            # Montar atributos convertendo tipos de acordo com o modelo
            attrs = []
            for fld in fields_out:
                name = fld.name()
                qvtype = fld.type()
                raw_val = _pick(row_dict, name)

                if raw_val in (None, "", " ") and name.upper() in ("OBJECTID", "ID", "OID"):
                    coerced = i + 1
                else:
                    coerced = _coerce_to_type(raw_val, qvtype)
                # nunca gravar "" em campos de data/tempo (vira NULL)
                if coerced == "" and qvtype in (QVariant.Date, QVariant.DateTime, QVariant.Time):
                    coerced = None
                # e, por via das dúvidas, nenhuma string vazia em qualquer tipo
                if coerced == "":
                    coerced = None
            
                attrs.append(coerced)


            feat = QgsFeature(fields_out)
            feat.setAttributes(attrs)

            # Construir e setar geometria
            if shp_adj is not None:
                try:
                    # corrige inválidas (auto-fix)
                    if hasattr(shp_adj, "is_valid") and not shp_adj.is_valid:
                        shp_adj = shp_adj.buffer(0)

                    # Construir a geometria por WKT (mais robusto aqui)
                    qgs_geom = QgsGeometry.fromWkt(shp_adj.wkt)

                    # Força multipart se a saída exigir
                    out_is_multi = QgsWkbTypes.isMultiType(wkb_out)
                    geom_is_multi = qgs_geom.isMultipart() if qgs_geom else False
                    if out_is_multi and qgs_geom and not geom_is_multi:
                        qgs_geom.convertToMultiType()

                    # (Opcional) transformar, mas crs_out == crs_in, então via de regra não precisa
                    if transformer and qgs_geom:
                        qgs_geom.transform(transformer)

                    if qgs_geom and not qgs_geom.isEmpty():
                        feat.setGeometry(qgs_geom)
                except Exception:
                    pass

            if not sink.addFeature(feat):
                sem_geom += 1
                continue

            if not feat.hasGeometry():
                sem_geom += 1

        if sem_geom:
            feedback.pushWarning(f"{sem_geom} feição(ões) foram gravadas sem geometria.")

        feedback.pushInfo("Concluído: camada padronizada gerada.")
        return {self.OUTPUT_GPKG: dest_id}
