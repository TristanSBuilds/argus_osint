from dotenv import load_dotenv, set_key
import os
import sys
import argparse
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from shodansearch import ShodanSearch
from  whois_enumeration import WhoisEnumeration
from dns_enumeration import DnsResolver
from ip_geolocation import IpGeolocation
from phone_geolocation import PhoneGeolocation
from historicalsearch import HistoricalSearch
from metadata_analyser import extract_metadata


def env_config():
    """ solicita al ususario su clave de API y la guarda en el archivo .env"""
    api_key = input("Ingrese su clave de API de Shodan: ")
    set_key(".env", "SHODAN_API_KEY", api_key)

def load_env(configure_env):
    # verificamos si el .env existe
    env_exists = os.path.exists(".env")

    if not env_exists or configure_env:
        # si el .env no existe o se solicita configirar le pasamos la fun de configuración
        env_config()
        # salimos del programa para q el usuario vuelva a ejecutar
        sys.exit(1)

    # cargamos las variables del .env para obtener los nuevos valores de la API KEY
    load_dotenv()

    # obtenemos la API KEY de SerpApi desde el .env

    return {
        "shodan" : os.getenv("SHODAN_API_KEY"),
        "ipinfo" : os.getenv("ACCESS_TOKEN")
    }


def resultados_shodan(shodan_query, page, configure_env):
    SHODAN_API_KEY = load_env(configure_env=configure_env)["shodan"]

    ssearch = ShodanSearch(SHODAN_API_KEY)
    
    resultados = ssearch.search(shodan_query, page=page)

    t = time.perf_counter()

    workers = []

    # calculamos cuántos hilos lanzar de forma segura (máximo 5, o los que haya si son menos)
    total_matches = min(5, len(resultados['matches']))

    # abrimos la piscina de hilos y procesaremos hasta 5 resultados simultáneamente
    with ThreadPoolExecutor(max_workers=5) as executor:
        for i in range(total_matches):
            # executor.submit envía la función get_results a un hilo en segundo plano para que se ejecute
            # devuelve un objeto "Future"(una promesa de que habrá un resultado) que guardamos en la lista workers
            workers.append(executor.submit(ssearch.get_results, resultados['matches'][i], i))

    # as_completed nos va entregando los resultados de los hilos conforme van terminando, 
    # sin esperar a que acaben en el orden exacto en el que empezaron
    for worker in as_completed(workers):
        # .result() extrae el valor real que devolvió la función get_results dentro del hilo
        result = worker.result()
        print(result['data'])

    print(f"Tiempo de procesamiento: {time.perf_counter() - t:.2f} s")

def main(
        whois_domain, shodan_query, page, configure_env, dns_domain, 
        ip, phone, hs_url, years_ago, days_interval, metadata_path
    ):

    if configure_env:
            env_config()
            sys.exit(1)

    if whois_domain:
        whoisenum = WhoisEnumeration(whois_domain) # la variable whois tiene el dominio pasado por la terminal
        whoisenum.busqueda_whois()

    if shodan_query:
        resultados_shodan(shodan_query, page, configure_env)

    if dns_domain:
        respuesta = input("Pasa una lista de los record types dns que deseas obtener, en este formato: a,b,c...")
        record_types = respuesta.split(",")

        dns_resolver = DnsResolver(dns_domain, record_types)
        dns_resolver.resolver_dns() 

    if ip:
        ACCESS_TOKEN = load_env(configure_env=configure_env)["ipinfo"]
        ip_geo = IpGeolocation(ACCESS_TOKEN, ip)
        details = ip_geo.get_ip_details()

        for k, v in details.items():
            print(f"{k} : {v}")

        latitude = details["latitude"]
        longitude = details["longitude"]
        location = details.get("region", "Ubicación desconocida")

        if latitude and longitude:
            map_file_path = ip_geo.pintar_mapa(latitude, longitude, location)
            print(f"Mapa guardado en: {map_file_path}")
        else:
            print("[!] La IP consultada no proporciona coordenadas geográficas válidas.")

    if phone:
        phone_geo = PhoneGeolocation(phone)

        info = phone_geo.obtener_info_telefono()

        print(info)

    if hs_url:

        user_agent = "Mozilla/5.0 (Windows NT 5.1; rv:40.0) Gecko/20100101 Firefox/40.0" #esto podemos hacer que se pase por la terminal
        hs = HistoricalSearch(hs_url, user_agent)

        hs.search_snapshot(years_ago)

        hs.search_snapshots_by_extensions(years_ago, days_interval)

    if metadata_path:
        try:
            print(f"\n--- Analizando metadatos de: {metadata_path} ---")
            metadata = extract_metadata(metadata_path)
            for k, v in metadata.items():
                print(f"{k}: {v}")
        except Exception as e:
            print(f"[!] Error al extraer metadatos: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-c", "--configure", action="store_true")
    parser.add_argument("-w", "--whois", type=str)
    parser.add_argument("-sq", "--shodan", type=str)
    parser.add_argument("--page", type=int, default=1)
    parser.add_argument("-d", "--dns", type=str)
    parser.add_argument("--ip", type=str)
    parser.add_argument("--phone", type=str)
    parser.add_argument("-hs", "--historical", type=str)
    parser.add_argument("-ya", "--years-ago", type=int, default=1)
    parser.add_argument("-di", "--days-interval", type=int, default=30)
    parser.add_argument("-mp", "--metadata-path", type=str)

    args = parser.parse_args()

    main(
        configure_env=args.configure,
        whois_domain=args.whois,
        shodan_query=args.shodan,
        page=args.page,
        dns_domain=args.dns,
        ip=args.ip,
        phone=args.phone,
        hs_url=args.historical,
        years_ago=args.years_ago,
        days_interval=args.days_interval,
        metadata_path=args.metadata_path
    )