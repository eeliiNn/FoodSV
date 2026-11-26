import os
import time
import cv2
import flet as ft

import db
import detector_formas
import detector_objetos
import recetas

CARPETA_TEMPORAL = "temp_imagenes"
os.makedirs(CARPETA_TEMPORAL, exist_ok=True)

COLOR_PRIMARIO = "#FF6A3D"
COLOR_PRIMARIO_OSCURO = "#E5552A"
COLOR_FONDO = "#FFF8F2"
COLOR_TARJETA = "#FFFFFF"
COLOR_BADGE_BG = "#FFE7D9"
COLOR_TEXTO = "#2B2320"
COLOR_TEXTO_MUTED = "#8A7F78"
COLOR_BORDE = "#F0E2D8"


def capturar_foto_camara(nombre_archivo):

    camara = cv2.VideoCapture(0)
    if not camara.isOpened():
        camara.release()
        raise RuntimeError("No se detectó ninguna cámara conectada.")

    ok, frame = camara.read()
    camara.release()

    if not ok:
        raise RuntimeError("No se pudo capturar la imagen de la cámara.")

    ruta = os.path.join(CARPETA_TEMPORAL, nombre_archivo)
    cv2.imwrite(ruta, frame)
    return ruta


def badge(texto: str) -> ft.Container:
    """Pequeña etiqueta en mayúsculas tipo 'EXPLORE OUR MENU'."""
    return ft.Container(
        content=ft.Text(
            texto.upper(),
            size=12,
            weight=ft.FontWeight.BOLD,
            color=COLOR_PRIMARIO_OSCURO,
        ),
        bgcolor=COLOR_BADGE_BG,
        padding=ft.padding.symmetric(horizontal=12, vertical=6),
        border_radius=20,
    )


def encabezado_seccion(texto_badge: str, titulo: str, subtitulo: str = None) -> ft.Column:
    controles = [
        badge(texto_badge),
        ft.Text(titulo, size=22, weight=ft.FontWeight.BOLD, color=COLOR_TEXTO),
    ]
    if subtitulo:
        controles.append(ft.Text(subtitulo, size=13, color=COLOR_TEXTO_MUTED))
    return ft.Column(controles, spacing=6)


def tarjeta(contenido, padding=16) -> ft.Container:
    """Tarjeta blanca redondeada con sombra suave, fondo siempre claro."""
    return ft.Container(
        content=contenido,
        bgcolor=COLOR_TARJETA,
        border_radius=16,
        padding=padding,
        border=ft.border.all(1, COLOR_BORDE),
        shadow=ft.BoxShadow(
            blur_radius=16,
            spread_radius=0,
            color=ft.Colors.with_opacity(0.06, "#000000"),
            offset=ft.Offset(0, 4),
        ),
    )


def boton_primario(texto, icono, on_click=None) -> ft.ElevatedButton:
    return ft.ElevatedButton(
        texto,
        icon=icono,
        on_click=on_click,
        color=ft.Colors.WHITE,
        bgcolor=COLOR_PRIMARIO,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=24),
            padding=ft.padding.symmetric(horizontal=20, vertical=16),
            elevation=0,
        ),
    )


def boton_secundario(texto, icono, on_click=None) -> ft.OutlinedButton:
    return ft.OutlinedButton(
        texto,
        icon=icono,
        on_click=on_click,
        style=ft.ButtonStyle(
            color=COLOR_PRIMARIO_OSCURO,
            side=ft.BorderSide(1.5, COLOR_PRIMARIO),
            shape=ft.RoundedRectangleBorder(radius=24),
            padding=ft.padding.symmetric(horizontal=20, vertical=16),
        ),
    )


def marco_imagen(control_imagen: ft.Image) -> ft.Container:
    return ft.Container(
        content=control_imagen,
        bgcolor=COLOR_BADGE_BG,
        border_radius=14,
        padding=6,
        border=ft.border.all(1, COLOR_BORDE),
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
    )


def campo_estilizado(**kwargs) -> ft.TextField:
    return ft.TextField(
        border_radius=12,
        filled=True,
        bgcolor="#FFFDFB",
        border_color=COLOR_BORDE,
        focused_border_color=COLOR_PRIMARIO,
        cursor_color=COLOR_PRIMARIO,
        **kwargs,
    )


def main(page: ft.Page):
    page.title = "FoodSV - Detector de Alimentos Salvadoreños"
    page.window.width = 1000
    page.window.height = 750
    page.scroll = ft.ScrollMode.AUTO

    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = COLOR_FONDO
    page.theme = ft.Theme(
        color_scheme_seed=COLOR_PRIMARIO,
        use_material3=True,
    )
    page.padding = 0

    db.inicializar_db()

    estado = {"ruta_imagen_actual": None}

    encabezado_app = ft.Container(
        content=ft.Row(
            [
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.RESTAURANT, color=ft.Colors.WHITE, size=22),
                            bgcolor=COLOR_PRIMARIO,
                            border_radius=12,
                            padding=8,
                        ),
                        ft.Column(
                            [
                                ft.Text(
                                    spans=[
                                        ft.TextSpan("Food", ft.TextStyle(color=COLOR_TEXTO, weight=ft.FontWeight.BOLD, size=20)),
                                        ft.TextSpan("SV", ft.TextStyle(color=COLOR_PRIMARIO, weight=ft.FontWeight.BOLD, size=20)),
                                    ],
                                ),
                                ft.Text("Detección inteligente de alimentos salvadoreños", size=11, color=COLOR_TEXTO_MUTED),
                            ],
                            spacing=0,
                        ),
                    ],
                    spacing=10,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        bgcolor=COLOR_TARJETA,
        padding=ft.padding.symmetric(horizontal=24, vertical=16),
        border=ft.border.only(bottom=ft.BorderSide(1, COLOR_BORDE)),
    )



    imagen_formas = ft.Image(width=480, height=380, fit=ft.ImageFit.CONTAIN, visible=False, border_radius=10)
    texto_resultado_formas = ft.Text("Sube o toma una foto para ver los resultados aquí.", color=COLOR_TEXTO_MUTED, size=13)
    campo_ancho_referencia = campo_estilizado(
        label="Ancho real del objeto de referencia (cm)",
        value="8.5",
        width=320,
        hint_text="Ej: una tarjeta mide 8.5 cm de ancho",
    )

    def al_seleccionar_imagen_formas(e: ft.FilePickerResultEvent):
        if not e.files:
            return
        ruta = e.files[0].path
        estado["ruta_imagen_actual"] = ruta
        procesar_formas(ruta)

    def procesar_formas(ruta):
        try:
            ancho_ref = float(campo_ancho_referencia.value)
        except ValueError:
            ancho_ref = None

        if ancho_ref:
            imagen_cv, resultados, px_por_cm = detector_formas.medir_con_referencia(ruta, ancho_ref)
        else:
            imagen_cv, resultados = detector_formas.detectar_contornos(ruta)

        ruta_salida = os.path.join(CARPETA_TEMPORAL, f"formas_resultado_{int(time.time()*1000)}.png")
        cv2.imwrite(ruta_salida, imagen_cv)

        imagen_formas.src = ruta_salida
        imagen_formas.visible = True
        resumen = "\n".join(
            f"- {r['forma']}: {r.get('ancho_cm', '?')}x{r.get('alto_cm', '?')} cm"
            if "ancho_cm" in r else f"- {r['forma']} (area: {int(r['area_px'])}px)"
            for r in resultados
        )
        texto_resultado_formas.value = resumen or "No se detectaron contornos relevantes."
        texto_resultado_formas.color = COLOR_TEXTO
        page.update()

    selector_formas = ft.FilePicker(on_result=al_seleccionar_imagen_formas)
    page.overlay.append(selector_formas)

    def al_tomar_foto_formas(e):
        try:
            ruta = capturar_foto_camara("captura_formas.png")
            estado["ruta_imagen_actual"] = ruta
            procesar_formas(ruta)
        except RuntimeError as error:
            page.snack_bar = ft.SnackBar(ft.Text(str(error)), bgcolor=COLOR_PRIMARIO_OSCURO, open=True)
            page.update()

    tab_formas = ft.Container(
        content=ft.Column(
            [
                encabezado_seccion(
                    "OpenCV · Medición",
                    "Detección de formas y medición",
                    "Coloca un objeto de referencia de ancho conocido junto al alimento para medir en centímetros.",
                ),
                tarjeta(
                    ft.Column(
                        [
                            campo_ancho_referencia,
                            ft.Text(
                                "Puedes subir una foto que ya tengas, o tomar una nueva con la cámara.",
                                size=12,
                                color=COLOR_TEXTO_MUTED,
                            ),
                            ft.Row(
                                [
                                    boton_primario(
                                        "Subir foto",
                                        ft.Icons.UPLOAD_FILE,
                                        lambda _: selector_formas.pick_files(
                                            allow_multiple=False,
                                            file_type=ft.FilePickerFileType.IMAGE,
                                        ),
                                    ),
                                    boton_secundario("Tomar foto con cámara", ft.Icons.CAMERA_ALT, al_tomar_foto_formas),
                                ],
                                spacing=10,
                                wrap=True,
                            ),
                        ],
                        spacing=14,
                    )
                ),
                ft.Row(
                    [
                        marco_imagen(imagen_formas),
                        ft.Container(expand=True, content=tarjeta(
                            ft.Column(
                                [
                                    ft.Text("Resultados", weight=ft.FontWeight.BOLD, color=COLOR_TEXTO),
                                    texto_resultado_formas,
                                ],
                                spacing=8,
                            )
                        )),
                    ],
                    spacing=16,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    wrap=True,
                ),
            ],
            spacing=18,
        ),
        padding=24,
    )

    # ==================== PESTAÑA 2: OBJETOS / YOLO ====================

    imagen_propio = ft.Image(width=380, height=300, fit=ft.ImageFit.CONTAIN, visible=False, border_radius=10)
    imagen_base = ft.Image(width=380, height=300, fit=ft.ImageFit.CONTAIN, visible=False, border_radius=10)
    texto_propio = ft.Text("Sin resultados todavía.", size=12, color=COLOR_TEXTO_MUTED)
    texto_base = ft.Text("Sin resultados todavía.", size=12, color=COLOR_TEXTO_MUTED)
    boton_guardar = boton_primario("Guardar detección en base de datos", ft.Icons.SAVE_ALT)
    boton_guardar.visible = False
    ultima_deteccion = {"detecciones": [], "ruta": None}

    def al_seleccionar_imagen_objetos(e: ft.FilePickerResultEvent):
        if not e.files:
            return
        ruta = e.files[0].path
        procesar_objetos(ruta)

    def procesar_objetos(ruta):
        resultado = detector_objetos.detectar_alimentos(ruta)

        for etiqueta, datos, img_control, texto_control in [
            ("propio", resultado["propio"], imagen_propio, texto_propio),
            ("base", resultado["base"], imagen_base, texto_base),
        ]:
            ruta_salida = os.path.join(CARPETA_TEMPORAL, f"objetos_{etiqueta}_{int(time.time()*1000)}.png")
            cv2.imwrite(ruta_salida, datos["imagen_anotada"])
            img_control.src = ruta_salida
            img_control.visible = True

            if datos["detecciones"]:
                lista = "\n".join(f"- {c} ({p*100:.1f}%)" for c, p in datos["detecciones"])
            else:
                lista = "Sin detecciones."
            texto_control.value = f"Tiempo: {datos['tiempo_ms']} ms\n{lista}"
            texto_control.color = COLOR_TEXTO

        ultima_deteccion["detecciones"] = resultado["propio"]["detecciones"]
        ultima_deteccion["ruta"] = ruta
        boton_guardar.visible = bool(ultima_deteccion["detecciones"])
        page.update()

    def guardar_en_bd(e):
        db.guardar_detecciones_multiples(
            ultima_deteccion["detecciones"],
            modelo="modelo_alimentossv.pt",
            ruta_imagen=ultima_deteccion["ruta"],
        )
        page.snack_bar = ft.SnackBar(ft.Text("Detección guardada en la base de datos."), bgcolor=COLOR_PRIMARIO, open=True)
        actualizar_historial()
        page.update()

    boton_guardar.on_click = guardar_en_bd

    selector_objetos = ft.FilePicker(on_result=al_seleccionar_imagen_objetos)
    page.overlay.append(selector_objetos)

    def al_tomar_foto_objetos(e):
        try:
            ruta = capturar_foto_camara("captura_objetos.png")
            procesar_objetos(ruta)
        except RuntimeError as error:
            page.snack_bar = ft.SnackBar(ft.Text(str(error)), bgcolor=COLOR_PRIMARIO_OSCURO, open=True)
            page.update()

    def tarjeta_modelo(titulo, control_imagen, texto_control):
        return tarjeta(
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.SMART_TOY_OUTLINED, color=COLOR_PRIMARIO, size=18),
                            ft.Text(titulo, weight=ft.FontWeight.BOLD, color=COLOR_TEXTO),
                        ],
                        spacing=6,
                    ),
                    marco_imagen(control_imagen),
                    texto_control,
                ],
                spacing=10,
            ),
            padding=14,
        )

    tab_objetos = ft.Container(
        content=ft.Column(
            [
                encabezado_seccion(
                    "YOLO · Comparación de modelos",
                    "Detección de alimentos",
                    "Compara el modelo de FoodSV contra un modelo base preentrenado en COCO.",
                ),
                tarjeta(
                    ft.Column(
                        [
                            ft.Text(
                                "Puedes subir una foto que ya tengas, o tomar una nueva con la cámara.",
                                size=12,
                                color=COLOR_TEXTO_MUTED,
                            ),
                            ft.Row(
                                [
                                    boton_primario(
                                        "Subir foto",
                                        ft.Icons.UPLOAD_FILE,
                                        lambda _: selector_objetos.pick_files(
                                            allow_multiple=False,
                                            file_type=ft.FilePickerFileType.IMAGE,
                                        ),
                                    ),
                                    boton_secundario("Tomar foto con cámara", ft.Icons.CAMERA_ALT, al_tomar_foto_objetos),
                                ],
                                spacing=10,
                                wrap=True,
                            ),
                        ],
                        spacing=14,
                    )
                ),
                ft.Row(
                    [
                        tarjeta_modelo("Modelo propio (AlimentosSV)", imagen_propio, texto_propio),
                        tarjeta_modelo("Modelo base (COCO, sin entrenar)", imagen_base, texto_base),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                    spacing=16,
                    wrap=True,
                ),
                boton_guardar,
            ],
            spacing=18,
        ),
        padding=24,
    )


    campo_presupuesto = campo_estilizado(
        label="Presupuesto máximo para lo que falta (USD, opcional)",
        width=360,
        hint_text="Ej: 2.00",
    )
    lista_recetas = ft.Column(spacing=12)
    texto_ingredientes_detectados = ft.Text(
        "Aún no has detectado ningún alimento. Ve a la pestaña 'Detección de alimentos' primero.",
        size=13,
        color=COLOR_TEXTO_MUTED,
    )

    def mostrar_recetas(e=None):
        ingredientes = sorted({clase for clase, _ in ultima_deteccion["detecciones"]})

        if not ingredientes:
            texto_ingredientes_detectados.value = "Aún no has detectado ningún alimento. Ve a la pestaña 'Detección de alimentos' primero."
            lista_recetas.controls.clear()
            page.update()
            return

        texto_ingredientes_detectados.value = "Ingredientes detectados: " + ", ".join(ingredientes)
        texto_ingredientes_detectados.color = COLOR_TEXTO

        try:
            presupuesto = float(campo_presupuesto.value) if campo_presupuesto.value else None
        except ValueError:
            presupuesto = None

        recomendaciones = recetas.recomendar_recetas(ingredientes, presupuesto_max=presupuesto)

        lista_recetas.controls.clear()
        if not recomendaciones:
            lista_recetas.controls.append(
                tarjeta(ft.Text("Ninguna receta calza con tu presupuesto actual.", color=COLOR_TEXTO_MUTED))
            )
        for receta in recomendaciones:
            disponibles_texto = ", ".join(receta["disponibles"]) or "ninguno"
            faltantes_texto = ", ".join(receta["faltantes"]) or "¡nada, la tienes completa!"
            lista_recetas.controls.append(
                tarjeta(
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(receta["nombre"], weight=ft.FontWeight.BOLD, size=16, color=COLOR_TEXTO),
                                    ft.Container(
                                        content=ft.Text(
                                            f"{receta['porcentaje_completo']}% completa",
                                            size=12,
                                            weight=ft.FontWeight.BOLD,
                                            color=COLOR_PRIMARIO_OSCURO,
                                        ),
                                        bgcolor=COLOR_BADGE_BG,
                                        padding=ft.padding.symmetric(horizontal=10, vertical=4),
                                        border_radius=16,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Text(f"Ya tienes: {disponibles_texto}", size=13, color=COLOR_TEXTO),
                            ft.Text(f"Te falta: {faltantes_texto}", size=13, color=COLOR_TEXTO),
                            ft.Text(
                                f"Costo estimado de lo que falta: ${receta['costo_faltantes']}",
                                size=13,
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_PRIMARIO_OSCURO,
                            ),
                        ],
                        spacing=6,
                    )
                )
            )
        page.update()

    tab_recetas = ft.Container(
        content=ft.Column(
            [
                encabezado_seccion(
                    "Recetas sugeridas",
                    "Recomendación de recetas",
                    "Usa los ingredientes de tu última detección para sugerir qué puedes cocinar, qué te falta y cuánto costaría completarlo.",
                ),
                tarjeta(
                    ft.Column(
                        [
                            texto_ingredientes_detectados,
                            campo_presupuesto,
                            boton_primario("Recomendar recetas", ft.Icons.RESTAURANT, mostrar_recetas),
                        ],
                        spacing=14,
                    )
                ),
                lista_recetas,
            ],
            spacing=18,
        ),
        padding=24,
    )

    # ==================== PESTAÑA 4: HISTORIAL ====================

    tabla_historial = ft.DataTable(
        heading_row_color=COLOR_BADGE_BG,
        heading_text_style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=COLOR_PRIMARIO_OSCURO),
        data_text_style=ft.TextStyle(color=COLOR_TEXTO),
        border=ft.border.all(1, COLOR_BORDE),
        border_radius=12,
        horizontal_lines=ft.BorderSide(1, COLOR_BORDE),
        columns=[
            ft.DataColumn(ft.Text("Fecha")),
            ft.DataColumn(ft.Text("Alimento")),
            ft.DataColumn(ft.Text("Confianza")),
            ft.DataColumn(ft.Text("Modelo")),
        ],
        rows=[],
    )

    def actualizar_historial():
        tabla_historial.rows.clear()
        for fecha, clase, confianza, modelo, ruta in db.obtener_historial():
            tabla_historial.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(fecha)),
                ft.DataCell(ft.Text(clase)),
                ft.DataCell(ft.Text(f"{confianza*100:.1f}%")),
                ft.DataCell(ft.Text(modelo)),
            ]))
        page.update()

    tab_historial = ft.Container(
        content=ft.Column(
            [
                encabezado_seccion(
                    "Base de datos",
                    "Historial de detecciones guardadas",
                    "Aquí aparecen todas las detecciones que has guardado desde la pestaña de alimentos.",
                ),
                boton_secundario("Actualizar", ft.Icons.REFRESH, lambda _: actualizar_historial()),
                tarjeta(
                    ft.Row([tabla_historial], scroll=ft.ScrollMode.AUTO),
                    padding=8,
                ),
            ],
            spacing=18,
        ),
        padding=24,
    )

    # ==================== Navegación entre pestañas ====================
    tabs = ft.Tabs(
        selected_index=0,
        indicator_color=COLOR_PRIMARIO,
        label_color=COLOR_PRIMARIO_OSCURO,
        unselected_label_color=COLOR_TEXTO_MUTED,
        divider_color=ft.Colors.TRANSPARENT,
        overlay_color=ft.Colors.TRANSPARENT,
        tabs=[
            ft.Tab(text="Formas y medición", icon=ft.Icons.STRAIGHTEN, content=tab_formas),
            ft.Tab(text="Detección de alimentos", icon=ft.Icons.FASTFOOD, content=tab_objetos),
            ft.Tab(text="Recetas", icon=ft.Icons.MENU_BOOK, content=tab_recetas),
            ft.Tab(text="Historial", icon=ft.Icons.HISTORY, content=tab_historial),
        ],
        expand=True,
    )

    page.add(
        ft.Column(
            [
                encabezado_app,
                ft.Container(content=tabs, bgcolor=COLOR_FONDO, expand=True),
            ],
            spacing=0,
            expand=True,
        )
    )
    actualizar_historial()


if __name__ == "__main__":
    ft.app(target=main)