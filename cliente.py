import math
import os
import socket
import threading
import argparse

# Función que ejecuta cada hilo para enviar imagen en paquetes
def enviar_imagen(ruta_img, s, tamaño_buffer, id_img):
    # Abrir imagen
    try:
        with open(ruta_img, "rb") as img:
            # Obtener el número total de paquetes
            paquetes_totales = math.ceil(os.path.getsize(ruta_img) / tamaño_buffer)
            # Enviar primer paquete con paquetes totales y id de imagen
            s.sendall(bytes(str(paquetes_totales) + ":" + id_img, 'utf-8'))
            # Recibir respuesta del servidor
            respuesta = s.recv(1024).decode()
            if respuesta == "Primer paquete recibido, envie el resto".decode():
                # Leer imagen en paquetes
                while True:
                    paquete = img.read(tamaño_buffer)
                    if not paquete:
                        break
                    # Enviar paquete con id de imagen
                    s.sendall(id_img.encode() + b":" + paquete)
                print("Imagen enviada con éxito")
                respuesta = s.recv(1024).decode()
                print(respuesta)
            else:
                print("Error del servidor al recibir el numero de paquetes y el id de la imagen")
    except Exception as e:
        print("Error al enviar imagen:", e)

# Función para enviar imágenes desde una carpeta
def sincronizacion_para_envio_imagenes(nombre_carpeta, s, tamaño_buffer):
    # envio nombre de la carpeta al servidor
    s.sendall(nombre_carpeta.encode())
    respuesta = s.recv(2024).decode()
    if respuesta == "Carpeta verificada, comience a enviar imágenes":
        # Crear una lista para almacenar todos los hilos
        hilos = []
        # recorro todas las imagenes de la carpeta
        for imagen in os.listdir(nombre_carpeta):
            # Obtener la ruta de cada imagen
            ruta_img = os.path.join(nombre_carpeta, imagen)
            # Obtener id de imagen
            id_img = os.path.splitext(imagen)[0]
            # Crear nuevo hilo por cada imagen
            t = threading.Thread(target=enviar_imagen, args=(ruta_img, s, tamaño_buffer, id_img))
            # Añadir hilo a la lista
            hilos.append(t)
            # Iniciar hilo
            t.start()
        # Esperar a que todos los hilos finalicen
        for t in hilos:
            t.join()
        print("Todas las imágenes enviadas")
    else:
        print("Error al verificar la carpeta")


# Función principal
if __name__ == "__main__":
    # Obtiene los argumentos de la línea de comandos
    pars = argparse.ArgumentParser(description="Cliente Procesamiento de imágenes")
    pars.add_argument("-i", "--ip", help="ip", type=str, default='127.0.0.1')
    pars.add_argument("-p", "--puerto", help="Puerto", type=int, default='1234')
    pars.add_argument("-f", "--carpeta", help="Carpeta de imágenes", type=str, default='img_to_learn')
    pars.add_argument("-bz", "--tamaño_buffer", type=int, default='1024')
    args = pars.parse_args()
    # Crear socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((args.ip, args.puerto))
    # Enviar imágenes desde la carpeta
    sincronizacion_para_envio_imagenes(args.carpeta, s, args.tamaño_buffer)
    s.close()
    