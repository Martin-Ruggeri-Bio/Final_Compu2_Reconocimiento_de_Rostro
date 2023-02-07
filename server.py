
import socketserver
import pymongo
from celery import Celery
import argparse
import sys
import threading
from PIL import Image


# Inicializar Celery
app = Celery('tareas', broker='redis://localhost:6380/0')

# Manejar errores al conectarse a MongoDB
try:
    # Conectarse a MongoDB
    cliente = pymongo.MongoClient("mongodb://mongodb:27017/")
    db = cliente["Banco_De_Imagenes"]

except Exception as e:
    print("Error al conectarse a MongoDB: {}".format(e))
    sys.exit()

class Manejador_Imagen(socketserver.BaseRequestHandler):
    def handle(self):
        # Recibir nombre de carpeta
        try:
            nombre_carpeta = self.request.recv(1024).decode()
            print(nombre_carpeta)
        except Exception as e:
            print("Error al recibir nombre de carpeta: {}".format(e))
            self.request.sendall("Error al recibir nombre de carpeta".encode())
            sys.exit()
        # Verificar si la colección ya existe
        if nombre_carpeta not in db.list_collection_names():
            # Manejar errores al crear nueva colección
            try:
                # Crear nueva colección
                db.create_collection(nombre_carpeta)
            except Exception as e:
                print("Error al crear colección {}: {}".format(nombre_carpeta, e))
                self.request.sendall("Error al crear colección".encode())
                sys.exit()
        # Seleccionar colección correspondiente
        self.coleccion = db[nombre_carpeta]
        # Enviar respuesta al cliente
        self.request.sendall("Carpeta verificada, envie primer paquete con la cantidad de paquetes totales y id ".encode())
        while True:
            # Crear nuevo hilo
            t = threading.Thread(target=self.reensamblar_imagen, args=(nombre_carpeta))
            # Iniciar hilo
            t.start()


    # Función para reensamblar imagen a partir de paquetes
    def reensamblar_imagen(self, nombre_carpeta):
        # Recibir primer paquete con la cantidad de paquetes totales que componen la imagen y id de imagen
        try:
            datos = self.request.recv(1024).decode()
            # Dividir datos
            paquetes_totales, id_img = datos.split(":")
            paquetes_totales = int(paquetes_totales)
            self.request.sendall("Primer paquete recibido, envie el resto".encode())
        except Exception as e:
            print("Error al recibir pel primer paquete: {}".format(e))
            self.request.sendall("Error al recibir pel primer paquete".encode())
            sys.exit()
        paquetes = []
        while len(paquetes) < paquetes_totales:
            try:
                # Recibir paquete
                paquete = self.request.recv(1024)
            except Exception as e:
                print("Error al recibir paquetes de imagen: {}".format(e))
                self.request.sendall("Error al recibir paquetes de imagen".encode())
            if paquete:
                paquetes.append(paquete)
        self.request.sendall("Todos los Paquetes recibidos".encode())
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