import psutil
import platform
import time
import os

def get_running_applications():
    """Obtiene una lista de aplicaciones visibles abiertas."""
    visible_apps = []
    system = platform.system()

    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            # Filtrar procesos que no son aplicaciones visibles
            if system == "Windows":
                import ctypes
                hwnd = ctypes.windll.user32.FindWindowW(None, proc.info['name'])
                if hwnd != 0 and proc.info['name'] not in visible_apps:
                    # Agregar solo aplicaciones visibles
                    visible_apps.append(proc.info['name'])

            elif system == "Darwin":  # macOS
                # Verificar si el ejecutable proviene del directorio /Applications
                if proc.info['exe'] and "/Applications/" in proc.info['exe']:
                    visible_apps.append(proc.info['name'])

            # Filtrar nombres de procesos del sistema como 'ioreg' y otros procesos secundarios
            if proc.info['name'] in ['ioreg', 'which', 'XPCKeychainSandboxCheck']:
                continue

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    return set(visible_apps)

def monitor_applications():
    """Monitorea las aplicaciones visibles abiertas y cerradas."""
    print("Monitoreando aplicaciones visibles... Presiona Ctrl+C para detener.")
    active_apps = get_running_applications()

    while True:
        try:
            current_apps = get_running_applications()

            # Detectar nuevas aplicaciones abiertas
            new_apps = current_apps - active_apps
            if new_apps:
                for app in new_apps:
                    print(f"[NUEVO] {app} abierto.")

            # Detectar aplicaciones cerradas
            closed_apps = active_apps - current_apps
            if closed_apps:
                for app in closed_apps:
                    print(f"[CERRADO] {app} cerrado.")

            # Actualizar lista de aplicaciones activas
            active_apps = current_apps

            # Intervalo de monitoreo
            time.sleep(1)
        except KeyboardInterrupt:
            print("\nMonitoreo detenido.")
            break
        except Exception as e:
            print(f"Error: {e}")
            break

if __name__ == "__main__":
    monitor_applications()
