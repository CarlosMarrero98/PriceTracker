# PriceTracker – Bot de Telegram para Seguir Precios de Acciones 

¡Bienvenido/a!   
PriceTracker es un bot de Telegram que permite a los usuarios seguir en tiempo real el 
precio de acciones, recibir alertas personalizadas, consultar estadísticas y exportar 
datos históricos. Todo ello de forma automatizada y configurable, directamente desde 
Telegram. 
**Aunque no tengas conocimientos de informática**.

---


# ¿Qué es esto? 

PriceTracker es un programa que pone a tu disposición un “robot” en Telegram. Con él podrás: - Consultar precios de acciones (empresas de Bolsa) - Recibir avisos si sube o baja una acción - Ver el historial de precios   
**¡Y todo desde tu móvil o PC, sin escribir comandos ni entender nada de programación!**

---


# Características principales

- Seguimiento de acciones con intervalos configurables. 
- Notificaciones automáticas por Telegram si el precio supera límites definidos. 
- Historial de precios con acceso a estadísticas (máximo, mínimo y media). 
- Generación de gráficos de evolución del precio. 
- Exportación de historial y favoritos en formato CSV. 
- Persistencia de datos mediante SQLite y Docker Volumes. 
- Preparado para despliegue con Docker y gestión CI/CD. 

---


# Requisitos 

- Un ordenador(Windows, Mac o Linux) 
- Conexión a Internet 
- Telegram(app gratis para móvil o PC) 
- Python(el programa que permite que funcione el bot, te enseño a instalarlo) 
- Unos minutos para instalar y configurar 

 ---


# Stack tecnológico

**Componente**              **Tecnología** 
Lenguaje                    Python 3.12 
Bot Telegram                python-telegram-bot (async) 
API de datos                TwelveData 
Base de datos               SQLite 
Gestión de dependencias     Poetry 
Contenedores                Docker + Docker Compose 
Gráficos                    Matplotlib 
Exportación CSV             Pandas 
CI/CD                       GitHub Actions 
Linter & Formateo           Ruff 
Tipado                      Mypy 
Testing                     Pytest, pytest-asyncio, Hypothesis 
Documentación               Pdoc

---


# Descargar el proyecto de GitHub 

- Entra en la web del proyecto: https://github.com/CarlosMarrero98/PriceTracker 
- Busca y pulsa el botón verde que pone “Code”. 
- Elige “Download ZIP”. 
- Guarda el archivo en tu ordenador. 

---


# Descomprimir el archivo ZIP

- Ve a la carpeta donde se descargó el archivo (normalmente “Descargas”). 
- Haz clic derecho sobre el archivo PriceTracker.zip y selecciona “Extraer aquí” o “Descomprimir”. 
- Se creará una carpeta llamada PriceTracker. 

--- 


# Instalar Python

**¿Ya tienes Python?** 
Puedes comprobarlo así: 
- Abre la terminal o símbolo del sistema. 
- Escribe:   

python --version 

Si aparece un número (por ejemplo, `Python 3.12.3`), ¡ya lo tienes! 

**¿No tienes Python?** 

- Descárgalo gratis de [python.org/downloads](https://www.python.org/downloads/) 
- MUY IMPORTANTE: Al instalar, marca la casilla que dice “Add Python to PATH”. 
- Finaliza la instalación (todo siguiente, siguiente). 

--- 


# Instalar Poetry

- Abre la terminal: 
    - Windows: Pulsa Inicio → Escribe “cmd” y pulsa Enter. 
    - Mac: Pulsa ⌘ + Espacio, escribe “Terminal” y pulsa Enter. 
    - Linux: Pulsa `Ctrl + Alt + T`. 

- Escribe este comando y pulsa Enter: 

pip install poetry 

- Si te da error, prueba: 

python -m pip install poetry 

---


# Instalar los componentes del bot

**Navega a la carpeta donde descomprimiste el proyecto:**

- Si está en Descargas: 
    - Windows: 

cd %HOMEPATH%\Descargas\PriceTracker 

    - Mac/Linux: 

cd ~/Descargas/PriceTracker 

Si lo pusiste en otro sitio, cámbialo por la ruta correcta (puedes arrastrar la carpeta a la terminal para escribir la ruta automáticamente). 

- Ahora instala todo con: 

poetry install 

- Esto descargará automáticamente todo lo necesario. 

---


# Conseguir la API Key (permiso para consultar precios)

- Entra en https://twelvedata.com/signup 
- Regístrate con tu correo. 
- Copia la API Key que te dan (es un código largo de letras y números). 

**Descarga el proyecto (como ya está explicado arriba).**

---


# Arranca el bot con Docker Compose

- Abre una terminal y entra en la carpeta del proyecto descomprimido (PriceTracker). 
- Ejecuta: 

docker compose up 

(Si tu sistema usa el comando antiguo, prueba docker-compose up) 
- El bot se iniciará y verás los mensajes en la terminal. 
- Deja la terminal abierta mientras quieras que el bot siga funcionando. 
- Para detener el bot, pulsa Ctrl+C en la terminal. 

**Opción avanzada: Usar Docker manual (si ya sabes)**

docker build -t pricetracker . 
docker run --rm -it pricetracker 

---


# TIP:

Si alguna vez quieres actualizar el bot, reemplaza la carpeta del proyecto y usa: 

docker compose up --build 

Si ves mensajes de “El bot ya está encendido” o algo similar, no te preocupes, puede que el bot esté funcionando ya (¡no hace falta volver a lanzarlo!).  

---


# Usar el bot en Telegram

- Abre Telegram en tu móvil o PC. 
- Busca este bot: http://t.me/PriceTrikerBot 
- Pulsa “Iniciar” para empezar a chatear. 

---


# ¿Cómo se usa?

El bot funciona por comandos que escribes en el chat, siempre empezando con una barra /. 
**Por ejemplo:**

- Muestra todos los comandos disponibles y explica para qué sirve cada uno. 
    /comandos 

- Añade la acción de Apple para hacer seguimiento (sustituye AAPL por el símbolo que quieras seguir):
    /añadir AAPL 

- Consulta el precio actual de la acción AAPL: 
    /precio AAPL 

- Configura una alerta para AAPL cada 30 minutos, si baja de 160 o sube de 500:
    /alerta AAPL 30 160 500 

- Muestra el historial de precios de la acción:
    /historial AAPL 

- Elimina el seguimiento de la acción AAPL:
    /borrar AAPL 

**Esto son ejemplos de comandos disponibles**

  ---


# Testing

- Ejecutar los tests con cobertura: 

poetry install 
poetry run pytest --cov=bot 

**Este proyecto cuenta con más de un 90% de cobertura, incluyendo pruebas unitarias y de integración con mocks y async.**

---


# Documentación técnica

Puedes generar la documentación HTML con: 

poetry run pdoc bot --html --output-dir docs 

Esto generará una carpeta docs/ con la documentación navegable. 

---


# UML y diseño 

Los diagramas de clases, componentes, secuencia y despliegue están disponibles en la carpeta docs/uml/.

---


# Estado del proyecto

- Seguimiento de acciones 
- Alertas automáticas 
- Historial de precios 
- Estadísticas por acción 
- Exportación CSV 
- CI/CD con GitHub Actions 
- Tests con >90% cobertura 
- Persistencia con Docker 
- Diagrama UML (en preparación) 
- API REST externa (idea futura) 
- Mejora del sistema de comprobaciones automáticas con Celery 
- Despliegue en un servidor como Render (pendiente)

---


# IMPORTANTE:

- No te preocupes por escribir mal, el bot te avisa si algo no está bien escrito. 
- Siempre escribe el comando tal como se indica, empezando por /. 

---


# FAQ: Dudas y Problemas Frecuentes

- ¿No puedes encender el bot? 
    - Asegúrate de que tu terminal está en la carpeta correcta. 
    - Si da error, puede ser porque ya está encendido. 
- Prueba a hablar con el bot en Telegram: 
    - Si responde, ¡ya está funcionando! 
    - Si no, revisa la terminal (debe estar abierta y sin errores rojos). 
    - ¿Cómo sé si Python/Poetry está bien instalado? 
    - Escribe en la terminal: 
    
      python --version 
      y 
      poetry --version 

    - Debe mostrar un número de versión. 
- ¿Se puede usar en móvil directamente? 
    - No, necesitas un ordenador para tener el bot “encendido”. 
- ¿Necesito tener el ordenador encendido siempre? 
    - Sí, el bot solo funciona mientras la terminal esté abierta y el bot funcionando. 
- ¿Y si cierro la terminal por error? 
    - Vuelve a seguir el paso de “encender el bot” (paso 7). 
- ¿Puedo añadir/eliminar acciones o alertas? 
    - “¡Claro! Todo desde los comandos del bot en Telegram.” 
- ¿Dónde se guarda mi información? 
    - Solo en tu propio ordenador, en un archivo llamado basedatos.db. 
- ¿Es gratis? 
    - Sí, el bot y la API de TwelveData tienen un plan gratuito. 

---


# ¿Cómo desinstalo todo?

- Solo borra la carpeta PriceTracker de tu ordenador. 
- Si quieres, puedes desinstalar Python y Poetry desde el panel de control. 

---


# Recomendaciones de seguridad y consejos

- No compartas tu API Key con desconocidos. 
- Usa siempre la última versión de Python. 
- Si tienes dudas, pide ayuda a alguien de confianza.

---


# Soporte

Si te atascas o tienes problemas, pide ayuda a la persona que te proporcionó este 
proyecto o contacta con [alejandroperezescobar@gmail.com, alu0101210995@ull.edu.es, jonathanborza02@gmail.com]. 

--- 


# Licencia 
MIT License – este proyecto es open source. 

---


**¡Listo!** 
Gracias por usar PriceTracker, tu bot para seguir acciones fáciles y sin complicaciones.