# Pizza App

Aplicación Flask para la gestión de pedidos, ventas, productos y usuarios de una pizzería.

## Contenido

- `app/` - código principal de la aplicación
- `requirements.txt` - dependencias Python
- `run.py` - punto de entrada
- `.env.example` - plantilla de variables de entorno

## Configuración local

1. Crear un entorno virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate
```

2. Instalar dependencias:

```powershell
pip install -r requirements.txt
```

3. Copiar el archivo de ejemplo de configuración:

```powershell
copy .env.example .env
```

4. Completar las variables de entorno en `.env`.

5. Ejecutar la aplicación:

```powershell
python run.py
```

## GitHub

1. Inicializar el repositorio Git:

```powershell
git init
```

2. Añadir y confirmar archivos:

```powershell
git add .
git commit -m "Initial commit"
```

3. Conectar el repositorio remoto y subirlo a GitHub:

```powershell
git branch -M main
git remote add origin https://github.com/<usuario>/<repositorio>.git
git push -u origin main
```

> Reemplaza `<usuario>` y `<repositorio>` con tus datos de GitHub.
