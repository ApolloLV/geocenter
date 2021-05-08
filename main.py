import geopandas
import matplotlib
import numpy as np
from scipy.spatial import cKDTree
from shapely.geometry import Point, LineString, Polygon
import pandas as pd
import matplotlib.pyplot as plt


def ckdnearest(gdA, gdB):
    nA = np.array(list(gdA.geometry.apply(lambda x: (x.x, x.y))))
    nB = np.array(list(gdB.geometry.apply(lambda x: (x.x, x.y))))
    btree = cKDTree(nB)
    dist, idx = btree.query(nA, k=1)
    gdB_nearest = gdB.iloc[idx].reset_index(drop=True)
    gdf = pd.concat(
        [
            gdA.drop(columns="geometry").reset_index(drop=True),
            gdB_nearest,
            pd.Series(dist, name='dist')
        ],
        axis=1)

    return gdf

fig, ax = plt.subplots(figsize=(10, 15))
plt.tight_layout()

germany_gdf = geopandas.read_file("data/DEU_adm/DEU_adm0.shp")
switzerland_gdf = geopandas.read_file("data/CHE_adm/CHE_adm0.shp")
germany_bundesland_gdf = geopandas.read_file("data/DEU_adm/DEU_adm1.shp")
switzerland_kanton_gdf = geopandas.read_file("data/CHE_adm/CHE_adm1.shp")

germany_cities_df = pd.read_csv("data/DEU_cities.csv")
switzerland_cities_df = pd.read_csv("data/CHE_cities.csv")
cities_df = germany_cities_df.append(switzerland_cities_df)
cities_gdf = geopandas.GeoDataFrame(
    cities_df, crs="EPSG:4326", geometry=geopandas.points_from_xy(cities_df.lng, cities_df.lat))

selected_cities_list = ["Wuppertal", "Paderborn", "Bielefeld", "Berlin", "Munich", "Zürich"]
selected_cities_gdf = cities_gdf[cities_gdf.city.isin(selected_cities_list)]
centroid_df = selected_cities_gdf.mean()
centroid_gdf = geopandas.GeoDataFrame(geometry=geopandas.points_from_xy(x=[centroid_df.lng], y=[centroid_df.lat], crs="EPSG:4326"))
print(centroid_gdf)

closest_city_gdf = ckdnearest(centroid_gdf, cities_gdf)
print(closest_city_gdf)

#germany_gdf.to_crs("EPSG:3857")
germany_gdf.boundary.plot(ax=ax, color="black")
#switzerland_gdf.to_crs("EPSG:3857")
switzerland_gdf.boundary.plot(ax=ax, color="black")
#germany_bundesland_gdf.to_crs("EPSG:3857")
germany_bundesland_gdf.boundary.plot(ax=ax, color="grey")
#
switzerland_kanton_gdf.boundary.plot(ax=ax, color="grey")
#cities_gdf.to_crs("EPSG:3857")
cities_gdf.plot(ax=ax, column="population", label="Städte", cmap="Greens", norm=matplotlib.colors.LogNorm())
#selected_cities_gdf.to_crs("EPSG:3857")
selected_cities_gdf.plot(ax=ax, color="blue", label="Wohnorte")
#centroid_gdf.to_crs("EPSG:3857")
centroid_gdf.plot(ax=ax, color="yellow", label="Centroid")

#closest_city_gdf.to_crs("EPSG:3857")
closest_city_gdf.plot(ax=ax, color="red", label="Fulda")

ax.set_facecolor('0.9')

plt.legend(fontsize=20)

plt.savefig("map.png", dpi=fig.dpi)
plt.show()
