from geo_utils import nettoyer_villes, convertir_en_geodf, faire_jointure_spatiale
import unittest
import pandas as pd
import geopandas as gpd

# =========================
# Tests unitaires
# =========================

class TestGeoAnalyse(unittest.TestCase):


    # Tests pour nettoyer_villes

    def test_nettoyer_villes_supprime_valeurs_manquantes(self):
        # Ici la 2e ligne a une latitude manquante -> doit être supprimée
        df = pd.DataFrame({
            "ville": ["A", "B"],
            "latitude": [10.0, None],
            "longitude": [20.0, 30.0],
            "pays": ["TestLand", "TestLand"],
            "population": [1000, 2000]
        })

        df_net = nettoyer_villes(df)

        self.assertEqual(len(df_net), 1)
        self.assertEqual(df_net.iloc[0]["ville"], "A")

    def test_nettoyer_villes_filtre_coordonnees_invalides(self):
        # latitude 200 est impossible -> la ligne B doit être supprimée
        df = pd.DataFrame({
            "ville": ["A", "B"],
            "latitude": [10.0, 200.0],
            "longitude": [20.0, 30.0],
            "pays": ["TestLand", "TestLand"],
            "population": [1000, 2000]
        })

        df_net = nettoyer_villes(df)

        self.assertEqual(len(df_net), 1)
        self.assertEqual(df_net.iloc[0]["ville"], "A")

    def test_nettoyer_villes_filtre_population_invalide(self):
        # population négative -> la ligne B doit être supprimée
        df = pd.DataFrame({
            "ville": ["A", "B"],
            "latitude": [10.0, 11.0],
            "longitude": [20.0, 21.0],
            "pays": ["TestLand", "TestLand"],
            "population": [1000, -5]
        })

        df_net = nettoyer_villes(df)

        self.assertEqual(len(df_net), 1)
        self.assertEqual(df_net.iloc[0]["ville"], "A")

    def test_nettoyer_villes_supprime_si_pays_manquant(self):
        # pays manquant -> la ligne B doit être supprimée
        df = pd.DataFrame({
            "ville": ["A", "B"],
            "latitude": [10.0, 11.0],
            "longitude": [20.0, 21.0],
            "pays": ["TestLand", None],
            "population": [1000, 2000]
        })

        df_net = nettoyer_villes(df)

        self.assertEqual(len(df_net), 1)
        self.assertEqual(df_net.iloc[0]["ville"], "A")


    # Tests pour convertir_en_geodf


    def test_convertir_en_geodf_cree_geometry_et_crs(self):
        df = pd.DataFrame({
            "ville": ["A"],
            "latitude": [10.0],
            "longitude": [20.0],
            "pays": ["TestLand"],
            "population": [1000]
        })

        gdf = convertir_en_geodf(df)

        self.assertIsInstance(gdf, gpd.GeoDataFrame)
        self.assertIn("geometry", gdf.columns)
        self.assertEqual(str(gdf.crs), "EPSG:4326")

        # Vérifier que c'est bien un point
        self.assertEqual(gdf.geometry.iloc[0].geom_type, "Point")


    # Tests pour faire_jointure_spatiale

    def test_jointure_spatiale_trouve_un_pays(self):
        # 1 ville au point (0,0)
        df = pd.DataFrame({
            "ville": ["A"],
            "latitude": [0.0],
            "longitude": [0.0],
            "pays": ["?"],
            "population": [1000]
        })
        villes_gdf = convertir_en_geodf(df)

        # 1 pays = un carré autour du point (0,0)
        # WKT = texte qui décrit un polygone
        poly = gpd.GeoSeries.from_wkt([
            "POLYGON((-1 -1, -1 1, 1 1, 1 -1, -1 -1))"
        ])
        pays_gdf = gpd.GeoDataFrame(
            {"nom_pays": ["TestLand"]},
            geometry=poly,
            crs="EPSG:4326"
        )

        res = faire_jointure_spatiale(villes_gdf, pays_gdf)

        # GeoPandas ajoute index_right si la jointure a eu lieu
        self.assertIn("index_right", res.columns)

        # la ville est dans le carré donc on doit trouver un pays
        self.assertFalse(pd.isna(res.loc[0, "index_right"]))

        # on vérifie que la colonne du pays est bien jointe
        self.assertEqual(res.loc[0, "nom_pays"], "TestLand")

    def test_jointure_spatiale_none_si_pas_dans_polygone(self):
        # Ville loin du polygone
        df = pd.DataFrame({
            "ville": ["A"],
            "latitude": [50.0],
            "longitude": [50.0],
            "pays": ["?"],
            "population": [1000]
        })
        villes_gdf = convertir_en_geodf(df)

        poly = gpd.GeoSeries.from_wkt([
            "POLYGON((-1 -1, -1 1, 1 1, 1 -1, -1 -1))"
        ])
        pays_gdf = gpd.GeoDataFrame(
            {"nom_pays": ["TestLand"]},
            geometry=poly,
            crs="EPSG:4326"
        )

        res = faire_jointure_spatiale(villes_gdf, pays_gdf)

        # la ville est en dehors donc index_right doit être NaN
        self.assertTrue(pd.isna(res.loc[0, "index_right"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
