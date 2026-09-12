import whois

class WhoisEnumeration:
    def __init__(self, domain_name):
        self.domain_name = domain_name

    def busqueda_whois(self):
        try:
            res = whois.whois(self.domain_name)

            print(f"--- Análisis WHOIS para: {self.domain_name} ---")
            print(f"Registrador: {res.registrar}")
            print(f"Fecha de Creación: {res.creation_date}")
            print(f"Fecha de Expiración: {res.expiration_date}")
            print(f"Servidores DNS: {res.name_servers}")
            print(f"Emails de contacto: {res.emails}")

        except Exception as e:
            print(f"No se encontró informacion del dominio {self.domain_name} : {e}")