# 📈 PriceTracker

Hola 👋

Este proyecto es un **asistente automático (bot)** que funciona dentro de la aplicación **Telegram**. Sirve para **avisarte cuando cambian los precios de las acciones** (como Apple, Tesla, etc.), sin que tengas que estar pendiente.

---

## 🧐 ¿Y esto para qué sirve?

Te ayuda a:

- Saber el precio actual de una acción (por ejemplo, de Apple)
- Recibir alertas si el precio sube o baja mucho
- Guardar las acciones que te interesan
- Ver un resumen diario de tus inversiones
- Usarlo todo desde Telegram, como si chatearas con alguien

---

## 📲 ¿Qué necesitas?

1. Un teléfono con la app **Telegram**
2. Un ordenador (Windows, Mac o Linux)
3. Conexión a Internet
4. Seguir esta guía paso a paso 🧓📘  
(No necesitas saber programar. Solo copiar, pegar y seguir instrucciones.)

---

## 🔧 ¿Cómo se empieza?

### Paso 1: Crear tu bot en Telegram

1. Abre Telegram y busca: `@BotFather`
2. Escríbele `/newbot` y sigue los pasos.
3. Telegram te dará un "código" llamado **token**.  
   📝 Guárdalo. Es como la llave de tu robot.

---

### Paso 2: Descargar este proyecto

1. Entra aquí: [https://github.com/CarlosMarrero98/PriceTracker](https://github.com/CarlosMarrero98/PriceTracker)
2. Haz clic en el botón verde que dice `Code`
3. Elige `Download ZIP`
4. Cuando se descargue, haz clic derecho y elige "Extraer todo" o "Descomprimir"

---

### Paso 3: Instalar lo necesario

#### 1. Instalar Python
- Entra a [https://www.python.org/downloads/](https://www.python.org/downloads/)
- Descarga la versión para tu ordenador
- Instálalo (como cualquier programa)

#### 2. Instalar Poetry
- Abre una ventana negra (terminal)
- Escribe esto y presiona Enter:

```bash
pip install poetry
````

---

### Paso 4: Configurar tus claves (token y API)

1. Crea un archivo nuevo llamado `.env` dentro de la carpeta del proyecto
2. Ábrelo con el Bloc de Notas
3. Pega esto (reemplazando por tus datos):

```
TELEGRAM_TOKEN=tu_token_de_telegram
TWELVEDATA_API_KEY=tu_api_key_de_twelvedata
```

✅ Importante: este archivo es privado. **No lo compartas.**

---

### Paso 5: Encender el robot 🤖

1. Abre la terminal (ventana negra)
2. Entra a la carpeta del proyecto:

```bash
cd PriceTracker
```

3. Instala lo necesario:

```bash
poetry install
```

4. Inicia el bot:

```bash
poetry run python bot/telegram_bot.py
```

✅ Si todo va bien, verás un mensaje como:
`✅ Bot iniciado...`

Ahora puedes ir a Telegram y escribirle a tu bot.

---

## 💬 ¿Qué puedo escribirle al bot?

| Comando      | Qué hace                                 |
| ------------ | ---------------------------------------- |
| `/start`     | Te da la bienvenida                      |
| `/login`     | Te registra como usuario                 |
| `/price`     | Te dice el precio actual de una acción   |
| `/alerta`    | Crea una alerta si sube o baja demasiado |
| `/portfolio` | Muestra las acciones que estás siguiendo |
| `/historial` | Muestra el precio de los últimos días    |
| `/ayuda`     | Explica todo lo que puedes hacer         |
| `/logout`    | Cierra tu sesión                         |

🧪 **Ejemplo:**

Si escribes esto en Telegram:

```
/price AAPL
```

El bot te responderá con el precio de Apple.

---

## ⛔ ¿Cómo apago el bot?

Ve a la ventana negra donde lo ejecutaste y presiona:

```
Ctrl + C
```

---

## ❓ Preguntas frecuentes

**¿Es peligroso?**
No. Solo tú puedes hablar con tu bot. Y tus datos están guardados en tu ordenador.

**¿Tengo que pagar algo?**
No. Todo es gratuito.

**¿Puedo usarlo desde el móvil?**
Sí. Lo instalas en tu ordenador, pero puedes hablarle desde Telegram en tu teléfono.

**¿Y si algo sale mal?**
Revisa esta guía desde el principio o pide ayuda. ¡No pasa nada!

---

## 👥 ¿Quién ha hecho esto?

Este proyecto fue creado por:

* [Carlos Marrero](https://github.com/CarlosMarrero98)
* [Alejandro Pérez](https://github.com/alepe03)
* [Jonathan Borza ](https://github.com/....)




