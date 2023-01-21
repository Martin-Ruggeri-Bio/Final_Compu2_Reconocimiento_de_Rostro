import os
import socket
import threading
import argparse

# Función para enviar imagen en trozos
def enviar_imagen(ruta_img, s, tamaño_buffer, id_img):
    # Abrir imagen
    with open(ruta_img, "rb") as img:
        # Obtener el número total de trozos
        trozos_totales = (os.path.getsize(ruta_img) + tamaño_buffer - 1) // tamaño_buffer
        # Enviar primer paquete con trozos totales y id de imagen
        s.sendall(bytes(str(trozos_totales) + ":" + id_img, 'utf-8'))
        # Leer imagen en trozos
        while True:
            trozo = img.read(tamaño_buffer)
            if not trozo:
                break
            # Enviar trozo con id de imagen
            #s.sendall(bytes(id_img + ":" + trozo))
            s.sendall(id_img.encode() + b":" + trozo)
    print("Imagen enviada con éxito")

# Función para enviar imágenes desde una carpeta
def enviar_imagenes_de_carpeta(nombre_carpeta, s, tamaño_buffer):
    # Crear una lista para almacenar todos los hilos
    hilos = []
    for imagen in os.listdir(nombre_carpeta):
        # Obtener la ruta de la imagen
        ruta_img = os.path.join(nombre_carpeta, imagen)
        if os.path.isfile(ruta_img):
            # Obtener id de imagen
            id_img = os.path.splitext(imagen)[0]
            # Crear nuevo hilo
            t = threading.Thread(target=enviar_imagen, args=(ruta_img, s, tamaño_buffer, id_img))
            # Añadir hilo a la lista
            hilos.append(t)
            # Iniciar hilo
            t.start()
    # Esperar a que todos los hilos finalicen
    for t in hilos:
        t.join()
    print("Todas las imágenes enviadas")

# Función principal
if __name__ == "__main__":
    # Obtiene los argumentos de la línea de comandos
    pars = argparse.ArgumentParser(description="Cliente Procesamiento de imágenes")
    pars.add_argument("-i", "--ip", help="ip", type=str, default='127.0.0.1')
    pars.add_argument("-p", "--puerto", help="Puerto", type=int, default='1234')
    pars.add_argument("-f", "--carpeta", help="Carpeta de imágenes", type=str, default='img_to_learn')
    pars.add_argument("-bz", "--tamaño_buffer", type=int, default='512')
    args = pars.parse_args()
    # Crear socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((args.ip, args.puerto))
    # Enviar imágenes desde la carpeta
    enviar_imagenes_de_carpeta(args.carpeta, s, args.tamaño_buffer)
    s.close()