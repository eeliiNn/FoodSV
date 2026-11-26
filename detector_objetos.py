import time
from ultralytics import YOLO

RUTA_MODELO_PROPIO = "modelo_alimentossv.pt"   
RUTA_MODELO_BASE = "yolo26s.pt"                

_modelo_propio = None
_modelo_base = None


def cargar_modelos():
    global _modelo_propio, _modelo_base
    if _modelo_propio is None:
        _modelo_propio = YOLO(RUTA_MODELO_PROPIO)
    if _modelo_base is None:
        _modelo_base = YOLO(RUTA_MODELO_BASE)
    return _modelo_propio, _modelo_base


def _ejecutar(modelo, ruta_imagen, confianza_minima=0.4):
    inicio = time.time()
    resultados = modelo.predict(source=ruta_imagen, conf=confianza_minima, verbose=False)
    tiempo_ms = round((time.time() - inicio) * 1000, 1)

    r = resultados[0]
    detecciones = []
    for caja in r.boxes:
        clase_id = int(caja.cls[0])
        nombre_clase = r.names[clase_id]
        confianza = float(caja.conf[0])
        detecciones.append((nombre_clase, round(confianza, 3)))

    imagen_anotada = r.plot()  
    return {
        "detecciones": detecciones,
        "tiempo_ms": tiempo_ms,
        "imagen_anotada": imagen_anotada,
    }


def detectar_alimentos(ruta_imagen, confianza_minima=0.4):

    modelo_propio, modelo_base = cargar_modelos()

    resultado_propio = _ejecutar(modelo_propio, ruta_imagen, confianza_minima)
    resultado_base = _ejecutar(modelo_base, ruta_imagen, confianza_minima)

    return {
        "propio": resultado_propio,
        "base": resultado_base,
    }
