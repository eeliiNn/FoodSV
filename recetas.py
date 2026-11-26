RECETAS = {

    "Desayuno tipico salvadoreño": [
        "huevos",
        "frijoles_rojos",
        "queso_fresco_duro_blando_y_requeson",
        "platano_maduro",
        "maiz_tortillas",
    ],

    "Casamiento con huevo": [
        "arroz_blanco_o_casamiento",
        "frijoles_rojos",
        "huevos",
        "queso_fresco_duro_blando_y_requeson",
    ],

    "Casamiento con platano": [
        "arroz_blanco_o_casamiento",
        "frijoles_rojos",
        "platano_maduro",
        "queso_fresco_duro_blando_y_requeson",
    ],

    "Casamiento con pollo": [
        "arroz_blanco_o_casamiento",
        "frijoles_rojos",
        "pollo",
        "tomate_cebolla",
    ],

    "Pollo guisado con arroz": [
        "pollo",
        "arroz_blanco_o_casamiento",
        "tomate_cebolla",
    ],

    "Pollo guisado con tortillas": [
        "pollo",
        "tomate_cebolla",
        "maiz_tortillas",
    ],

    "Pollo con casamiento": [
        "pollo",
        "arroz_blanco_o_casamiento",
        "frijoles_rojos",
        "tomate_cebolla",
    ],

    "Pollo con guisquil": [
        "pollo",
        "guisquil",
        "tomate_cebolla",
        "arroz_blanco_o_casamiento",
    ],

    "Pollo con tortillas y aguacate": [
        "pollo",
        "maiz_tortillas",
        "aguacate",
        "tomate_cebolla",
    ],

    "Guisquil con huevo": [
        "guisquil",
        "huevos",
        "tomate_cebolla",
    ],

    "Guisquil con queso": [
        "guisquil",
        "queso_fresco_duro_blando_y_requeson",
        "tomate_cebolla",
    ],

    "Guisquil relleno de queso": [
        "guisquil",
        "queso_fresco_duro_blando_y_requeson",
        "huevos",
        "tomate_cebolla",
    ],

    "Sopa de mora": [
        "mora_y_chipilin",
        "tomate_cebolla",
        "huevos",
    ],

    "Sopa de chipilin con arroz": [
        "mora_y_chipilin",
        "arroz_blanco_o_casamiento",
        "tomate_cebolla",
    ],

    "Chipilin con huevo": [
        "mora_y_chipilin",
        "huevos",
        "tomate_cebolla",
    ],

    "Frijoles fritos con queso": [
        "frijoles_rojos",
        "queso_fresco_duro_blando_y_requeson",
        "maiz_tortillas",
    ],

    "Frijoles con huevo": [
        "frijoles_rojos",
        "huevos",
        "maiz_tortillas",
    ],

    "Frijoles con aguacate y tortillas": [
        "frijoles_rojos",
        "aguacate",
        "maiz_tortillas",
        "queso_fresco_duro_blando_y_requeson",
    ],

    "Platano frito con frijoles": [
        "platano_maduro",
        "frijoles_rojos",
        "queso_fresco_duro_blando_y_requeson",
    ],

    "Platano frito con crema y queso": [
        "platano_maduro",
        "queso_fresco_duro_blando_y_requeson",
    ],

    "Platano con huevo y frijoles": [
        "platano_maduro",
        "huevos",
        "frijoles_rojos",
        "maiz_tortillas",
    ],

    "Huevos con tomate y cebolla": [
        "huevos",
        "tomate_cebolla",
        "maiz_tortillas",
    ],

    "Huevos con frijoles y queso": [
        "huevos",
        "frijoles_rojos",
        "queso_fresco_duro_blando_y_requeson",
        "maiz_tortillas",
    ],

    "Huevos con aguacate": [
        "huevos",
        "aguacate",
        "tomate_cebolla",
        "maiz_tortillas",
    ],

    "Tortillas con queso y frijoles": [
        "maiz_tortillas",
        "queso_fresco_duro_blando_y_requeson",
        "frijoles_rojos",
    ],

    "Tortillas con queso y aguacate": [
        "maiz_tortillas",
        "queso_fresco_duro_blando_y_requeson",
        "aguacate",
    ],

    "Ensalada de aguacate": [
        "aguacate",
        "tomate_cebolla",
    ],

    "Ensalada de aguacate con queso": [
        "aguacate",
        "tomate_cebolla",
        "queso_fresco_duro_blando_y_requeson",
    ],

    "Arroz con pollo": [
        "arroz_blanco_o_casamiento",
        "pollo",
        "tomate_cebolla",
    ],

    "Arroz con huevo": [
        "arroz_blanco_o_casamiento",
        "huevos",
        "tomate_cebolla",
    ],

    "Arroz con frijoles y aguacate": [
        "arroz_blanco_o_casamiento",
        "frijoles_rojos",
        "aguacate",
    ],

    "Casamiento con queso y aguacate": [
        "arroz_blanco_o_casamiento",
        "frijoles_rojos",
        "queso_fresco_duro_blando_y_requeson",
        "aguacate",
    ],

    "Casamiento con platano y huevo": [
        "arroz_blanco_o_casamiento",
        "frijoles_rojos",
        "platano_maduro",
        "huevos",
    ],
}

# Costos aproximados en USD por porcion/unidad usada en una receta.
# IMPORTANTE: son valores de referencia -- ajustalos con precios reales
# de mercado/supermercado en El Salvador antes de presentar el proyecto.
COSTOS_APROX_USD = {
    "aguacate": 0.33,
    "arroz_blanco_o_casamiento": 0.50,
    "frijoles_rojos": 1.25,
    "guisquil": 1.00,
    "huevos": 4.35,
    "maiz_tortillas": 0.25,
    "mora_y_chipilin": 0.50,
    "platano_maduro": 0.50,
    "pollo": 1.40,
    "queso_fresco_duro_blando_y_requeson": 0.75,
    "tomate_cebolla": 0.35,
}


def recomendar_recetas(ingredientes_detectados, presupuesto_max=None):
    """
    ingredientes_detectados: lista o set de nombres de clase detectados
        (ej: ["frijoles_rojos", "huevos"])
    presupuesto_max: si se da, solo se incluyen recetas cuyo costo de
        ingredientes FALTANTES sea menor o igual a ese monto.

    Devuelve una lista de dicts, ordenada de mayor a menor porcentaje
    de ingredientes que ya tienes, cada uno con:
        nombre, disponibles, faltantes, porcentaje_completo, costo_faltantes
    """
    detectados = set(ingredientes_detectados)
    resultados = []

    for nombre_receta, ingredientes_receta in RECETAS.items():
        ingredientes_receta_set = set(ingredientes_receta)
        disponibles = sorted(ingredientes_receta_set & detectados)
        faltantes = sorted(ingredientes_receta_set - detectados)

        porcentaje = round(len(disponibles) / len(ingredientes_receta_set) * 100, 1)
        costo_faltantes = round(sum(COSTOS_APROX_USD.get(i, 0) for i in faltantes), 2)

        if presupuesto_max is not None and costo_faltantes > presupuesto_max:
            continue

        resultados.append({
            "nombre": nombre_receta,
            "disponibles": disponibles,
            "faltantes": faltantes,
            "porcentaje_completo": porcentaje,
            "costo_faltantes": costo_faltantes,
        })

    resultados.sort(key=lambda r: (-r["porcentaje_completo"], r["costo_faltantes"]))
    return resultados
