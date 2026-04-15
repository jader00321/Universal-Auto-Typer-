# -*- coding: utf-8 -*-

import pyautogui
import time
import random
import sys
import threading

# --- Variables Globales para Hilos ---
# Usamos un Lock para evitar problemas al modificar la lista de mensajes.
message_lock = threading.Lock()
# Evento para detener el hilo de envío de forma segura.
stop_event = threading.Event()
# Evento para pausar y reanudar el hilo de envío.
pause_event = threading.Event()

# --- Funciones Principales ---

def obtener_coordenadas(nombre_punto):
    """
    Pausa el script durante 5 segundos para que el usuario mueva el mouse
    a la posición deseada y luego captura y devuelve las coordenadas.
    """
    print(f"\nPreparando para capturar las coordenadas de '{nombre_punto}'...")
    print("Tienes 5 segundos para mover el mouse a la posición correcta.")
    for i in range(5, 0, -1):
        sys.stdout.write(f"\rComenzando en {i}...")
        sys.stdout.flush()
        time.sleep(1)
    print("\n¡Coordenadas capturadas!")
    posicion = pyautogui.position()
    return posicion

def enviar_mensaje_kick(coordenadas_chat, coordenadas_envio, mensaje):
    """
    Mueve el mouse a las coordenadas del chat, escribe el mensaje y lo envía.
    """
    try:
        pyautogui.click(coordenadas_chat.x, coordenadas_chat.y)
        time.sleep(0.5)
        pyautogui.typewrite(mensaje, interval=0.05)
        time.sleep(0.5)
        pyautogui.click(coordenadas_envio.x, coordenadas_envio.y)
    except Exception as e:
        # No imprimimos el error aquí para no saturar la consola
        pass

def bucle_de_envio(coords_chat, coords_enviar, time_settings, lista_mensajes):
    """
    Esta función se ejecuta en un hilo separado. Se encarga de enviar mensajes
    a intervalos aleatorios hasta que se lo indiquemos.
    """
    contador_mensajes = 0
    is_paused_message_shown = False
    while not stop_event.is_set():
        # Comprobar si el bot debe pausarse
        if pause_event.is_set():
            if not is_paused_message_shown:
                # Limpiamos la línea anterior y mostramos el mensaje de pausa
                sys.stdout.write("\r" + " " * 80 + "\r") # Limpia la línea
                sys.stdout.write("Bot pausado. Escribe 'resume' para continuar...")
                sys.stdout.flush()
                is_paused_message_shown = True
            time.sleep(0.5) # Espera un poco para no consumir CPU inútilmente
            continue # Vuelve al inicio del bucle while

        if is_paused_message_shown:
            print("\nBot reanudado.")
            is_paused_message_shown = False

        with message_lock: # Adquirimos el lock para leer la lista de forma segura
            if not lista_mensajes:
                time.sleep(2)
                continue
            mensaje_a_enviar = random.choice(lista_mensajes)

        enviar_mensaje_kick(coords_chat, coords_enviar, mensaje_a_enviar)
        contador_mensajes += 1
        
        # Leemos los valores de tiempo más recientes desde el diccionario compartido
        min_t = time_settings['min']
        max_t = time_settings['max']
        tiempo_espera = random.randint(min_t, max_t)
        
        # Imprimimos el estado en una nueva línea, como solicitaste
        print(f"Mensaje #{contador_mensajes} ('{mensaje_a_enviar}') enviado. Próximo en ~{tiempo_espera}s.")
        
        # Esperamos el tiempo, pero comprobando el stop_event para una salida rápida
        stop_event.wait(tiempo_espera)

# --- Inicio del Script ---

if __name__ == "__main__":
    print("--- Asistente de Chat para Kick (Interactivo) ---")
    print("ADVERTENCIA: El uso de bots puede ir en contra de los Términos de Servicio de Kick.")
    print("Úsalo bajo tu propia responsabilidad.\n")

    # --- Configuración Inicial ---
    coords_chat = obtener_coordenadas("Cuadro de texto del chat")
    coords_enviar = obtener_coordenadas("Botón de Enviar")

    print("\nEscribe los mensajes iniciales, separados por punto y coma (;).")
    entrada_mensajes = input("Introduce tus mensajes aquí: ")
    lista_mensajes = [msg.strip() for msg in entrada_mensajes.split(';') if msg.strip()]
    print(f"\nLista de mensajes actual: {lista_mensajes if lista_mensajes else 'Vacía'}")

    # Usamos un diccionario para poder modificar los tiempos desde el hilo principal
    time_settings = {'min': 0, 'max': 0}
    while True:
        try:
            min_intervalo = int(input("Introduce el tiempo MÍNIMO de espera (segundos): "))
            max_intervalo = int(input("Introduce el tiempo MÁXIMO de espera (segundos): "))
            if min_intervalo > 0 and max_intervalo >= min_intervalo:
                time_settings['min'] = min_intervalo
                time_settings['max'] = max_intervalo
                break
            else:
                print("Valores no válidos. El máximo debe ser >= al mínimo.")
        except ValueError:
            print("Por favor, introduce solo números.")

    # --- Iniciar el hilo de envío ---
    sender_thread = threading.Thread(target=bucle_de_envio, args=(coords_chat, coords_enviar, time_settings, lista_mensajes))
    sender_thread.start()
    
    print("\n--- ¡Bot activado! ---")
    print("Puedes usar los siguientes comandos mientras se ejecuta:")
    print("  'add <mensaje>'         - Añade un mensaje a la lista.")
    print("  'del <numero>'          - Borra un mensaje (ej: 'del 2').")
    print("  'list'                  - Muestra la lista de mensajes actual.")
    print("  'settime <min> <max>'   - Modifica el intervalo de tiempo (ej: 'settime 5 15').")
    print("  'pause'                 - Pausa el envío de mensajes.")
    print("  'resume'                - Reanuda el envío de mensajes.")
    print("  'stop'                  - Detiene el bot y sale.\n")

    # --- Bucle de Comandos del Usuario ---
    while True:
        try:
            comando = input()
            partes = comando.strip().split(' ', 2)
            accion = partes[0].lower()

            if accion == "add":
                if len(partes) > 1 and partes[1]:
                    with message_lock:
                        lista_mensajes.append(partes[1])
                    print(f"-> Mensaje añadido: '{partes[1]}'")
                else:
                    print("-> Uso: add <texto del mensaje>")

            elif accion == "del":
                if len(partes) > 1:
                    try:
                        index = int(partes[1]) - 1
                        with message_lock:
                            if 0 <= index < len(lista_mensajes):
                                eliminado = lista_mensajes.pop(index)
                                print(f"-> Mensaje eliminado: '{eliminado}'")
                            else:
                                print(f"-> Número fuera de rango. Hay {len(lista_mensajes)} mensajes.")
                    except ValueError:
                        print("-> Uso: del <numero de la lista>")
                else:
                    print("-> Uso: del <numero de la lista>")

            elif accion == "list":
                with message_lock:
                    if not lista_mensajes:
                        print("-> La lista de mensajes está vacía.")
                    else:
                        print("-> Lista de mensajes actual:")
                        for i, msg in enumerate(lista_mensajes):
                            print(f"  {i+1}: {msg}")
            
            elif accion == "settime":
                try:
                    # CORRECCIÓN: Ahora usamos partes[1] y partes[2] directamente.
                    if len(partes) != 3: raise ValueError
                    
                    nuevo_min = int(partes[1])
                    nuevo_max = int(partes[2])

                    if nuevo_min > 0 and nuevo_max >= nuevo_min:
                        time_settings['min'] = nuevo_min
                        time_settings['max'] = nuevo_max
                        print(f"-> Intervalo de tiempo actualizado a: Mínimo {nuevo_min}s, Máximo {nuevo_max}s.")
                    else:
                        print("-> Valores no válidos. El máximo debe ser >= al mínimo y ambos positivos.")
                except (ValueError, IndexError):
                    print("-> Uso: settime <min_segundos> <max_segundos>")

            elif accion == "pause":
                if not pause_event.is_set():
                    pause_event.set()
                else:
                    print("-> El bot ya está pausado.")

            elif accion == "resume":
                if pause_event.is_set():
                    pause_event.clear()
                else:
                    print("-> El bot no está pausado.")

            elif accion == "stop":
                print("\nDeteniendo el bot...")
                stop_event.set()
                break
            
            else:
                if accion:
                    print(f"-> Comando '{accion}' no reconocido.")

        except (KeyboardInterrupt, EOFError):
            print("\nDeteniendo el bot por interrupción...")
            stop_event.set()
            break
    
    # Esperar a que el hilo de envío termine completamente
    sender_thread.join()
    print("--- Script detenido. ¡Hasta luego! ---")
