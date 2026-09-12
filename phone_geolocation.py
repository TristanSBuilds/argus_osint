import phonenumbers as pn
from phonenumbers import geocoder, carrier, timezone
import folium
import os
from geopy.geocoders import Photon

class PhoneGeolocation:
    def __init__(self, num_tlf):
        self.geolocator = Photon(user_agent="phone_geolocation")
        self.num = pn.parse(num_tlf, "ES")


    def pintar_mapa(self, localization, filename="phone_map.html"):
        location = self.geolocator.geocode(localization)

        if not location:
            print(f"[!] No se pudieron obtener coordenadas para: {localization}")
            return None

        mapa = folium.Map(location=[location.latitude, location.longitude], zoom_start=10, tiles="CartoDB positron")

        folium.Marker([location.latitude, location.longitude], popup=location).add_to(mapa)

        mapa.save(filename)

        return os.path.abspath(filename)


    def obtener_info_telefono(self):
        zona_horaria = timezone.time_zones_for_number(self.num)

        pais = geocoder.description_for_number(self.num, "es")

        operador = carrier.name_for_number(self.num, "es")

        info = {
            "Número": pn.format_number(self.num, pn.PhoneNumberFormat.INTERNATIONAL),
            "País": pais, 
            "Operador": operador,
            "Zona Horaria": zona_horaria
        }

        return info