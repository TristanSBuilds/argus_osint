import ipinfo
from dotenv import load_dotenv
import os
import sys
import folium

class IpGeolocation:
    def __init__(self, access_token, ip_addr):
        self.access_token = access_token
        self.ip_addr = ip_addr

    @staticmethod
    def pintar_mapa(latitude, longitude, location, filename="map.html"):
        mapa = folium.Map(location=[latitude, longitude], zoom_start=9, tiles="CartoDB positron")
        folium.Marker([latitude, longitude], popup=location).add_to(mapa)
        mapa.save(filename)
        return os.path.abspath(filename)

    def get_ip_details(self): 
        try:
            handler = ipinfo.getHandler(self.access_token)
            details = handler.getDetails(self.ip_addr)
            return details.all
        except Exception as e:
            print(f"Error al obtener detalles de la IP: {e}")
            sys.exit(1)



# details = get_ip_details(IP_ADDR, ACCESS_TOKEN)

# for k, v in details.items():
#     print(f"{k} : {v}")

# latitude = details["latitude"]
# longitude = details["longitude"]
# location = details.get("region", "Ubicación desconocida")

# if latitude and longitude:
#     map_file_path = pintar_mapa(latitude, longitude, location)
#     print(f"Mapa guardado en: {map_file_path}")
# else:
#     print("[!] La IP consultada no proporciona coordenadas geográficas válidas.")