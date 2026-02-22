import os
import random
from PIL import Image, ImageOps, ImageDraw, ImageFont

# Configuración de dimensiones (Tamaño Carta a 300 DPI)
ANCHO_CARTA = 2550 
ALTO_CARTA = 3300
MARGEN = 100
ESPACIADO = 20

def generar_loterias(ruta_imagenes, carpeta_salida, cantidad_cartones=120):
    # 1. Cargar rutas de imágenes
    formatos=('.jpg', '.jpeg', '.png', '.bmp')
    imagenes = [os.path.join(ruta_imagenes, f) for f in os.listdir(ruta_imagenes) 
                if f.lower().endswith(formatos)]
    
    if len(imagenes) < 16:
        print("¡Error! Necesitas al menos 16 imágenes en la carpeta.")
        return

    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)

    # Calcular tamaño de cada celda (4x4)
    ancho_disponible = ANCHO_CARTA - (2 * MARGEN) - (3 * ESPACIADO)
    alto_disponible = ALTO_CARTA - (2 * MARGEN) - (3 * ESPACIADO)
    ancho_celda = ancho_disponible // 4
    alto_celda = alto_disponible // 4
    # Altura de la banda de texto (20% de la celda)
    alto_banda = int(alto_celda * 0.20)
    tamano_fuente = 60
    caracteres_texto = 15

    # Intentar cargar una fuente (Arial o similar). Si no, usa la default.
    try:
        # En Windows suele ser 'arial.ttf', en Mac 'Arial.ttf'
        fuente = ImageFont.truetype("arial.ttf", tamano_fuente)
    except:
        print('No se logró cargar fuente')
        fuente = ImageFont.load_default(tamano_fuente)

    for i in range(cantidad_cartones):
        # Crear lienzo transparente
        carton = Image.new('RGBA', (ANCHO_CARTA, ALTO_CARTA), (0, 0, 0, 0))
        draw = ImageDraw.Draw(carton)

        # Seleccionar 16 imágenes al azar sin repetir para este cartón
        seleccion = random.sample(imagenes, 16)
        
        for fila in range(4):
            for col in range(4):
                img_path = seleccion[fila * 4 + col]
                nombre_texto = os.path.splitext(os.path.basename(img_path))[0].replace("_", " ").upper()[:caracteres_texto]

                img = Image.open(img_path)

                img = img.convert('RGBA')
                
                # --- TRUCO DE RECORTE (CROP) ---
                # ImageOps.fit recorta y redimensiona para llenar el espacio exacto
                img_procesada = ImageOps.fit(img, (ancho_celda, alto_celda), Image.Resampling.LANCZOS)


                # 2. Crear la banda negra semitransparente
                # El color (0,0,0,128) es Negro con 50% de transparencia
                overlay = Image.new('RGBA', img_procesada.size, (0, 0, 0, 0))
                draw_ov = ImageDraw.Draw(overlay)
                # print(img_procesada.size)
                coords = [0, alto_celda - alto_banda ,ancho_celda,alto_celda]
                draw_ov.rectangle(coords, fill=(0, 0, 0, 160))

                # 3. Dibujar el texto sobre la banda
                bbox = draw_ov.textbbox((0, 0), nombre_texto, font=fuente)
                ancho_txt = bbox[2] - bbox[0]
                alto_txt = bbox[3] - bbox[1]
                
                x_txt = (ancho_celda - ancho_txt) // 2
                y_txt = (alto_celda - (alto_banda // 2)) - (alto_txt // 2) - 5
                
                draw_ov.text((x_txt, y_txt), nombre_texto, fill="white", font=fuente)
                
                # Combinar imagen y banda
                img_final = Image.alpha_composite(img_procesada, overlay)

                # Centrar la imagen en su celda
                x = MARGEN + col * (ancho_celda + ESPACIADO)
                y = MARGEN + fila * (alto_celda + ESPACIADO)
                # Pegar en el cartón
                carton.paste(img_final, (x, y))

        # Guardar resultado
        carton.save(f"{carpeta_salida}/carton_{i+1}.png")
        print(f"Generando cartón {i+1}/{cantidad_cartones}")

if __name__ == "__main__":
    generar_loterias("imagenes", "resultados")