# Final_Compu2_Reconocimiento_de_Rostro

Este proyecto contiene dos scripts: un cliente y un servidor, que se utilizan para enviar y recibir imágenes respectivamente.

## Cliente

El script "cliente.py" se utiliza para enviar imágenes desde una carpeta específica a un servidor a través de un socket. Utiliza los siguientes argumentos de línea de comando:

-   `-i` o `--ip`: Dirección IP del servidor al que se enviarán las imágenes. (por defecto: `127.0.0.1`)
-   `-p` o `--puerto`: Puerto del servidor al que se enviarán las imágenes. (por defecto: `1234`)
-   `-f` o `--carpeta`: Carpeta que contiene las imágenes a enviar. (por defecto: `img_to_learn`)
-   `-bz` o `--tamaño_buffer`: Tamaño del buffer utilizado para enviar las imágenes en trozos. (por defecto: `512`)

Para ejecutar el script, utilice el siguiente comando:

Copy code

`python cliente.py` 

## Servidor

El script "server.py" se utiliza para recibir las imágenes enviadas por el cliente. Utiliza los siguientes argumentos de línea de comando:

-   `-p` o `--puerto`: Puerto en el que escuchar las conexiones de socket. (por defecto: `1234`)

Para ejecutar el script, utilice el siguiente comando:

Copy code

`python server.py` 

Una vez que se ejecuta el script, las imágenes recibidas se almacenan en una base de datos MongoDB y se procesan utilizando tareas en segundo plano con Celery.

## Dependencias

Este proyecto requiere las siguientes dependencias:

-   socket
-   threading
-   argparse
-   pymongo
-   celery
-   PIL
