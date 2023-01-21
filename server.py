
import socketserver
import pymongo
from celery import Celery
import argparse
import sys
import threading
from PIL import Image


# Inicializar Celery
app = Celery('tareas', broker='redis://localhost:6379/0')

# Manejar errores al conectarse a MongoDB
try:
    # Conectarse a MongoDB
    cliente = pymongo.MongoClient()
    db = cliente["Banco_De_Imagenes"]
except Exception as e:
    print("Error al conectarse a MongoDB: {}".format(e))
    sys.exit()

class Manejador_Imagen(socketserver.BaseRequestHandler):
    def handle(self):
        # Recibir nombre de carpeta
        nombre_carpeta = self.request.recv(1024).decode()
        # Verificar si la colección ya existe
        if nombre_carpeta not in db.list_collection_names():
            # Manejar errores al crear nueva colección
            try:
                # Crear nueva colección
                db.create_collection(nombre_carpeta)
            except Exception as e:
                print("Error al crear colección {}: {}".format(nombre_carpeta, e))
                sys.exit()
        # Seleccionar colección correspondiente
        self.coleccion = db[nombre_carpeta]
        # Enviar respuesta al cliente
        self.request.sendall("Carpeta verificada, comience a enviar imágenes".encode())
        while True:
            # Recibir primer paquete con la cantidad de paquetes totales que componen la imagen y id de imagen
            datos = self.request.recv(1024).decode()
            if not datos:
                break
            # Dividir datos
            paquetes_totales, id_img = datos.split(":")
            paquetes_totales = int(paquetes_totales)
            # Crear nuevo hilo
            t = threading.Thread(target=self.reensamblar_imagen, args=(paquetes_totales, id_img, nombre_carpeta))
            # Iniciar hilo
            t.start()

    # Función para reensamblar imagen a partir de paquetes
    def reensamblar_imagen(self, paquetes_totales, id_img, nombre_carpeta):
        paquetes = []
        while len(paquetes) < paquetes_totales:
            # Recibir paquete
            paquete = self.request.recv(1024)
            if paquete:
                paquetes.append(paquete)
        # Guardar imagen en MongoDB
        img = b"".join(paquetes)
        app.send_task('server.guardar_imagen', args=[img, id_img, nombre_carpeta], queue='cola_imagen', coleccion=self.coleccion)
    

# Tarea para guardar imagen en MongoDB
@app.task
def guardar_imagen(img, id_img, nombre_carpeta, coleccion):
    try:
        # Abrir imagen utilizando Pillow
        img = Image.open(img)
        # Convertir imagen a cadena binaria
        img_bytes = img.tobytes()
        # Crear documento
        documento = {"nombre_carpeta": nombre_carpeta, "imagen": img_bytes, "id_img": id_img}
        # Insertar documento en la colección
        coleccion.insert_one(documento)
    except Exception as e:
        print("Error al guardar imagen en MongoDB: {}".format(e))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Servidor de procesamiento de imágenes")
    parser.add_argument("-i", "--ip", help="Dirección IP", type=str, default='127.0.0.1')
    parser.add_argument("-p", "--puerto", help="Puerto", type=int, default='1234')
    args = parser.parse_args()
    server = socketserver.TCPServer((args.ip, args.puerto), Manejador_Imagen)
    print("Servidor escuchando en IP: {} y puerto: {}".format(args.ip, args.puerto))
    server.serve_forever()