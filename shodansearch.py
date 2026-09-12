import ataque_local.shodan as shodan
from login_automation import has_valid_credentials

class ShodanSearch:
    def __init__(self, api_key):
        self.client = shodan.Shodan(api_key)

    def search(self, query, page=1):
        try:
            results = self.client.search(query, page=page)
            return results
        except Exception as e:
            print(f"Error al realizar la búsqueda en Shodan: {e}")

    def get_results(self, resultados, index):
        results = {
            "index" : index,
            "data" : f"\nResultado {index + 1}\n" + 
                    f"Dirección IP: {resultados['ip_str']}\n" + 
                    f"Hostname: {resultados['hostnames']}\n" + 
                    f"Localización: {resultados['location']}\n" + 
                    f"Credenciales por defecto: {has_valid_credentials(resultados)}"
        }
        return results