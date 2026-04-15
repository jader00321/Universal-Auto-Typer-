<p align="center">
  <img src="bot-icono.ico" alt="Auto-Typer Logo" width="120">
</p>

<h1 align="center">Universal Auto-Typer v4.3</h1>

<p align="center">
  <strong>Herramienta de automatización de escritura universal con simulación de comportamiento humano e interfaz gráfica avanzada.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/PySide6-41CD52?style=for-the-badge&logo=qt&logoColor=white" alt="PySide6">
  <img src="https://img.shields.io/badge/Automation-HID-blue?style=for-the-badge" alt="Automation">
</p>

---

## 📖 Descripción del Proyecto

**Universal Auto-Typer** es una aplicación de escritorio desarrollada para automatizar tareas de escritura repetitivas en cualquier plataforma o campo de texto. A diferencia de los enviadores de texto simples, esta herramienta permite configurar intervalos, repeticiones y listas de mensajes, facilitando la interacción en chats de streaming (como Kick o Twitch) o el llenado de formularios masivos.

## ✨ Funcionalidades Clave

* **⌨️ Escritura Multi-Mensaje:** Permite cargar una lista de diferentes mensajes para rotar durante la ejecución.
* **⏱️ Control de Tiempo Preciso:** Configuración de intervalos de espera entre mensajes para simular un ritmo natural.
* **🔄 Repetición Infinita o Definida:** Opción para ejecutar el ciclo de escritura de forma constante o por un número específico de veces.
* **🖥️ Interfaz Intuitiva:** Desarrollada con `PySide6`, ofreciendo una experiencia de usuario limpia, ligera y profesional.
* **🛡️ Modo Seguro:** Estructura modular que permite integrar pausas para evitar bloqueos por spam en diversas plataformas.

---

## 🧠 Arquitectura y Lógica

El proyecto separa la experiencia de usuario de la ejecución lógica para garantizar estabilidad:

<details>
<summary><b>Estructura de Archivos</b></summary>

<br>

* **`kick_bot_gui.py`:** Gestiona toda la capa visual, validación de entradas de usuario y eventos de botones.
* **`kick_bot.py`:** Contiene el motor de automatización y la lógica de simulación de teclado.
* **`bot-icono.ico`:** Identidad visual de la aplicación para el sistema operativo.

</details>

---

## 🚀 Instalación y Uso

### 1. Pre-requisitos
* Python 3.8 o superior.
* Librerías de interfaz y automatización.

### 2. Configuración
    ```bash
    # Instalar dependencias necesarias
    pip install PySide6 pyautogui

### 3. Ejecución
    ```bash
    python kick_bot_gui.py


### ⚠️ Descargo de Responsabilidad

Esta herramienta fue creada con fines educativos y de productividad. El usuario es responsable de cumplir con los términos de servicio de las plataformas donde se utilice.

---

Desarrollado para simplificar la interacción digital mediante automatización inteligente.