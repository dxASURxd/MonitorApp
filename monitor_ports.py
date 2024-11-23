# El fin de este programa es monitorear los dispositivos conectados a un equipo en Distribuidora Sucahersa
# Esto ayudara a que el departamento de TI este siempre notificado de fallas en algun puerto
import time
import json
import platform
import subprocess
from datetime import datetime
import psutil

LOG_FILE = "desconexiones.json"

def guardar_evento(tipo_puerto, nombre_puerto):
    evento = {
        "hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tipo_puerto": tipo_puerto,
        "nombre_puerto": nombre_puerto
    }
    try:
        with open(LOG_FILE, "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        data = []
    data.append(evento)
    with open(LOG_FILE, "w") as file:
        json.dump(data, file, indent=4)
    print(f"Evento registrado: {evento}")

def obtener_usb_macos():
    try:
        resultado = subprocess.check_output(["ioreg", "-p", "IOUSB", "-w0", "-l"], text=True)
        dispositivos = []
        for linea in resultado.splitlines():
            if '"Product Name"' in linea:
                dispositivos.append(linea.strip().split('"')[3])  # Extrae el nombre del dispositivo
        return set(dispositivos)
    except Exception as e:
        print(f"Error al ejecutar ioreg: {e}")
        return set()

def monitorear():
    sistema = platform.system()
    dispositivos_usb_previos = set()
    print("Iniciando monitoreo de puertos...")
    if sistema == "Darwin":
        dispositivos_usb_previos = obtener_usb_macos()
    elif sistema == "Windows":
        dispositivos_usb_previos = {dev.device for dev in psutil.disk_partitions()}
    
    while True:
        try:
            if sistema == "Darwin":
                dispositivos_usb_actuales = obtener_usb_macos()
            elif sistema == "Windows":
                dispositivos_usb_actuales = {dev.device for dev in psutil.disk_partitions()}
            
            desconectados_usb = dispositivos_usb_previos - dispositivos_usb_actuales
            if desconectados_usb:
                for dispositivo in desconectados_usb:
                    guardar_evento("USB", dispositivo)
            dispositivos_usb_previos = dispositivos_usb_actuales

            time.sleep(2)
        except KeyboardInterrupt:
            print("\nMonitoreo detenido.")
            break
        except Exception as e:
            print(f"Error durante el monitoreo: {e}")

if __name__ == "__main__":
    # print(f"Ejecutndo en {platform.system()}")
    monitorear()
