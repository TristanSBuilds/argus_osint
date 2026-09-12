from login_automation import has_valid_credentials

def main():
    print("[*] Iniciando prueba de login automatizado contra DVWA local...")
    
    # Llamamos directamente a la función de login local
    exito_login = has_valid_credentials()
    
    print(f"\nResultado de la prueba:")
    print(f"Credenciales por defecto (admin/password): {exito_login}")

if __name__ == "__main__":
    main()