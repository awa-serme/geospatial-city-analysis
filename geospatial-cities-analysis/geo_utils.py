"""Fonctions de nettoyage et d'analyse géospatiale des villes."""
import pandas as pd
import geopandas as gpd

def nettoyer_villes(villes_df):
    # On enlève les lignes où il manque des infos essentielles
    villes_df = villes_df.dropna(subset=["latitude", "longitude", "pays","population"])

    # On enlève les coordonnées impossibles
    villes_df = villes_df[
        (villes_df["latitude"] >= -90) & (villes_df["latitude"] <= 90) &
        (villes_df["longitude"] >= -180) & (villes_df["longitude"] <= 180)
    ]

    # On enlève les populations incorrectes
    villes_df = villes_df[villes_df["population"] > 0]

    return villes_df


def convertir_en_geodf(villes_df):
    # Transforme le DataFrame en GeoDataFrame avec des points
    villes_gdf = gpd.GeoDataFrame(
        villes_df.copy(),
        geometry=gpd.points_from_xy(villes_df["longitude"], villes_df["latitude"]),
        crs="EPSG:4326"
    )
    return villes_gdf


def faire_jointure_spatiale(villes_gdf, pays_gdf):
    # Assurer le CRS pour éviter les problèmes
    if pays_gdf.crs is None:
        pays_gdf = pays_gdf.set_crs("EPSG:4326")
    else:
        pays_gdf = pays_gdf.to_crs(villes_gdf.crs)

    # Jointure spatiale: on veut savoir dans quel pays est chaque ville
    res = gpd.sjoin(villes_gdf, pays_gdf, how="left", predicate="within")
    return res
