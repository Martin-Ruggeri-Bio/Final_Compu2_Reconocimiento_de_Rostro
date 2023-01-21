import argparse


def crear_parseador_de_reconocimiento_facial():
    pars = argparse.ArgumentParser(description="Procesamiento de imagenes")
    pars.add_argument("-i", "--ip", help="ip", type=str, default='127.0.0.1')
    pars.add_argument("-p", "--puerto", help="Puerto", type=int, default='1234')
    pars.add_argument("-o", "--operation",help="learn or predict", type=str, default="learn")
    pars.add_argument(
        "-imga", "--img_to_learn", help="Directorio con las imagenes para aprender",
        type=str, default="/home/martin/Facultad/Compu 2/Final_Compu_2/img_to_learn"
    )
    pars.add_argument(
        "-imgp", "--img_to_predict", help="Directorio con las imagenes para predecir",
        type=str, default="/home/martin/Facultad/Compu 2/Final_Compu_2/img_to_predict"
    )
    pars.add_argument(
        "-g", "--graphs", help="Directorio con las graficas",
        type=str, default="/home/martin/Facultad/Compu 2/Final_Compu_2/graphs"
    )
    args = pars.parse_args()
    return args
