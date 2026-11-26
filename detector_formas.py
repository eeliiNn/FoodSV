"""
detector_formas.py
Cubre el criterio "Medición de distancia o detección de formas/contornos" (15%)
usando solamente OpenCV y Python (sin modelos de IA).

Hace dos cosas:
1. Detecta contornos y clasifica la forma geométrica de cada uno
   (círculo, triángulo, rectángulo, etc.) — útil por ejemplo para
   detectar el plato o el contorno general del alimento.
2. Mide el tamaño real (en cm) de cada contorno usando un OBJETO DE
   REFERENCIA de ancho conocido (por ejemplo una moneda o una tarjeta)
   que debe aparecer en la misma foto. Esto es lo que la rúbrica llama
   "medición de distancia" aplicada de forma simple con visión artificial
   clásica (sin redes neuronales).
"""

import cv2
import numpy as np


def clasificar_forma(contorno):
    """Devuelve el nombre de la forma según el número de vértices del contorno aproximado."""
    perimetro = cv2.arcLength(contorno, True)
    aprox = cv2.approxPolyDP(contorno, 0.04 * perimetro, True)
    vertices = len(aprox)

    if vertices == 3:
        return "Triangulo"
    elif vertices == 4:
        x, y, w, h = cv2.boundingRect(aprox)
        relacion = w / float(h)
        return "Cuadrado" if 0.95 <= relacion <= 1.05 else "Rectangulo"
    elif vertices == 5:
        return "Pentagono"
    elif vertices > 6:
        return "Circulo"
    else:
        return f"Poligono ({vertices} lados)"


def detectar_contornos(ruta_imagen, area_minima=500):
    """
    Detecta todos los contornos relevantes de la imagen.
    Devuelve: (imagen_anotada, lista_de_resultados)
    Cada resultado es un dict con: forma, area_px, bounding_box (x,y,w,h)
    """
    imagen = cv2.imread(ruta_imagen)
    if imagen is None:
        raise FileNotFoundError(f"No se pudo abrir la imagen: {ruta_imagen}")

    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    difuminada = cv2.GaussianBlur(gris, (5, 5), 0)
    bordes = cv2.Canny(difuminada, 50, 150)
    bordes = cv2.dilate(bordes, None, iterations=1)

    contornos, _ = cv2.findContours(bordes, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    resultados = []
    for contorno in contornos:
        area = cv2.contourArea(contorno)
        if area < area_minima:
            continue

        forma = clasificar_forma(contorno)
        x, y, w, h = cv2.boundingRect(contorno)

        cv2.drawContours(imagen, [contorno], -1, (0, 255, 0), 2)
        cv2.putText(imagen, forma, (x, max(y - 10, 0)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        resultados.append({
            "forma": forma,
            "area_px": area,
            "bounding_box": (x, y, w, h),
        })

    return imagen, resultados


def medir_con_referencia(ruta_imagen, ancho_real_referencia_cm, area_minima=500):
    """
    Igual que detectar_contornos, pero además calcula el ancho/alto REAL
    en centímetros de cada objeto, usando el contorno más grande de la
    imagen como el objeto de referencia (por ejemplo una tarjeta o moneda
    colocada junto al alimento).

    ancho_real_referencia_cm: el ancho real conocido del objeto de referencia.
    """
    imagen, resultados = detectar_contornos(ruta_imagen, area_minima)

    if not resultados:
        return imagen, resultados, None

    # el contorno con mayor area en pixeles se asume como la referencia
    referencia = max(resultados, key=lambda r: r["area_px"])
    _, _, ancho_ref_px, _ = referencia["bounding_box"]

    pixeles_por_cm = ancho_ref_px / float(ancho_real_referencia_cm)

    for resultado in resultados:
        x, y, w, h = resultado["bounding_box"]
        resultado["ancho_cm"] = round(w / pixeles_por_cm, 2)
        resultado["alto_cm"] = round(h / pixeles_por_cm, 2)

        cv2.putText(
            imagen,
            f"{resultado['ancho_cm']}x{resultado['alto_cm']}cm",
            (x, y + h + 20),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2
        )

    return imagen, resultados, pixeles_por_cm
