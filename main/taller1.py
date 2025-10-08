import re
import json
from datetime import datetime

REGIONES_CHILE = {
    "AP": "Arica y Parinacota", "TA": "Tarapacá", "AN": "Antofagasta", "AT": "Atacama",
    "CO": "Coquimbo", "VS": "Valparaíso", "RM": "Región Metropolitana de Santiago",
    "LI": "Libertador Bernardo O'Higgins", "ML": "Maule", "NB": "Ñuble",
    "BI": "Biobío", "AR": "La Araucanía", "LR": "Los Ríos", "LL": "Los Lagos",
    "AI": "Aysén", "MA": "Magallanes y Antártica Chilena"
}

ARCHIVO_JSON = "tokens.json"

def guardar_resultado_json(token, valido, tipo, derivacion=None):
    registro = {
        "token": token,
        "valido": valido,
        "tipo": tipo,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "derivacion": derivacion
    }

    try:
        with open(ARCHIVO_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    data.append(registro)

    with open(ARCHIVO_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def mostrar_registros():
    try:
        with open(ARCHIVO_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
        print("\n--- HISTORIAL DE TOKENS ---")
        for item in data:
            estado = "VÁLIDO" if item["valido"] else "INVÁLIDO"
            print(f"{item['fecha']} | {item['tipo'].upper():10} | {item['token']:20} | {estado}")
        print("-----------------------------")
    except FileNotFoundError:
        print("No hay tokens registrados.")
    except json.JSONDecodeError:
        print("Error al leer el archivo JSON.")

def afd_token(token):
    if len(token) != 14:
        print("Error: debe tener 14 caracteres.")
        return False

    estado = 0
    tiene_letra, tiene_digito = False, False

    for c in token:
        print(f"q{estado} --[{c}]--> ", end="")

        if estado in [0, 1, 2] and c.isupper():
            estado += 1
        elif estado == 3 and c.isdigit() and c != "0":
            estado = 4
        elif estado in [4, 5, 6] and c.isdigit():
            estado += 1
        elif estado == 7 and c == "_":
            estado = 8
        elif estado in [8, 9, 10, 11] and (c.islower() or c.isdigit()):
            if c.islower():
                tiene_letra = True
            if c.isdigit():
                tiene_digito = True
            estado += 1
            # cuando termina el bloque
            if estado == 12:
                if not (tiene_letra and tiene_digito):
                    print("qs (bloque sin letra o sin número)")
                    return False
                estado = 17
        elif estado == 17 and c.isupper():
            estado = 18
        elif estado == 18 and c.isupper():
            region = token[-2:]
            if region in REGIONES_CHILE:
                estado = 26
            else:
                print(f"qs (región '{region}' no válida)")
                return False
        else:
            print("qs (transición no válida)")
            return False

        print(f"q{estado}")

    valido = estado == 26 and tiene_letra and tiene_digito
    print("Resultado AFD:", "Válido" if valido else "Inválido")
    return valido

def derivacion_gramatical(token):
    patron = r"[A-Z]{3}[1-9]\d{3}_[a-z0-9]{4}[A-Z]{2}"
    valido = re.fullmatch(patron, token) is not None

    if not valido:
        print("El token no cumple la gramática.")
        return False

    sigla, anio, bloque, region = token[:3], token[3:7], token[8:12], token[12:]
    tiene_letra = any(c.islower() for c in bloque)
    tiene_digito = any(c.isdigit() for c in bloque)

    if not (tiene_letra and tiene_digito):
        print("El bloque no cumple: debe tener al menos una letra y un dígito.")
        return False

    pasos = [
        "S",
        "A B",
        f"{sigla[0]} C B",
        f"{sigla[0]} {sigla[1]} N B",
        f"{sigla} B",
        f"{sigla} D N N N C",
        f"{sigla} {anio} C",
        f"{sigla}{anio}_ E",
        f"{sigla}{anio}_ Z Z Z Z F",
        f"{sigla}{anio}_{' '.join(list(bloque))} F",
        f"{sigla}{anio}_{bloque} R R",
        f"{sigla}{anio}_{bloque}{region}"
    ]

    print("\n--- Derivación gramatical ---")
    for i, paso in enumerate(pasos, 1):
        print(f"({i}) {paso}")
    print("-----------------------------")
    print("Resultado gramatical: Válido")
    return True

def mostrar_regiones():
    print("\n--- Sufijos disponibles ---")
    for codigo, nombre in REGIONES_CHILE.items():
        print(f"{codigo}: {nombre}")
    print("---------------------------")

def crear_token(sigla, anio, bloque, sufijo):
    return f"{sigla}{anio}_{bloque}{sufijo}"

def menu():
    while True:
        print("\n--- MENÚ DE TOKENS ---")
        print("1. Crear token")
        print("2. Comprobar por AFD")
        print("3. Comprobar por gramática")
        print("4. Ver historial")
        print("5. Salir\n")

        opcion = input("Elige una opción: ").strip()

        if opcion == "1":
            sigla = input("Sigla (3 mayúsculas): ").strip().upper()
            anio = input("Año (4 dígitos, sin 0 al inicio): ").strip()
            bloque = input("Bloque (4 caracteres, al menos 1 letra y 1 dígito): ").strip()


            mostrar_regiones()
            sufijo = input("Sufijo (ej: RM, AN...): ").strip().upper()

            if sufijo not in REGIONES_CHILE:
                print("Sufijo no válido.")
                continue

            token = crear_token(sigla, anio, bloque, sufijo)
            print(f"\nToken creado: {token}")

            print("\n--- Verificación AFD ---")
            resultado_afd = afd_token(token)

            print("\n--- Verificación gramatical ---")
            resultado_gram = derivacion_gramatical(token)

            valido = resultado_afd and resultado_gram

            print("\n--- RESULTADO FINAL ---")
            print(f"AFD: {'Válido' if resultado_afd else 'Inválido'}")
            print(f"Gramática: {'Válido' if resultado_gram else 'Inválido'}")
            print(f"Token final: {'VÁLIDO' if valido else 'INVÁLIDO'}")
            print("-------------------------")

            guardar_resultado_json(token, valido, "creacion")

        elif opcion == "2":
            token = input("Token a comprobar por AFD: ").strip()
            print("\n--- AFD ---")
            resultado = afd_token(token)
            guardar_resultado_json(token, resultado, "AFD")

        elif opcion == "3":
            token = input("Token para derivar: ").strip()
            resultado = derivacion_gramatical(token)
            guardar_resultado_json(token, resultado, "gramatica")

        elif opcion == "4":
            mostrar_registros()

        elif opcion == "5":
            print("Saliendo...")
            break

        else:
            print("Opción inválida.")

if __name__ == "__main__":
    menu()
