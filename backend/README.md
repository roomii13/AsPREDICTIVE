# Backend PostgreSQL + FastAPI

API FastAPI para autenticación, catálogos, incidentes, alertas y predicción de riesgo sobre PostgreSQL.

## 1. Instalar dependencias

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Configurar entorno

Copiar `backend/.env.example` a `backend/.env` y completar:

- `DATABASE_URL`
- `SECRET_KEY`
- `ACCESS_TOKEN_EXPIRE_MINUTES`

## 3. Entrenar modelo

```bash
python train_model.py
```

Si la base tiene suficientes incidentes etiquetados por `nivel_riesgo`, el modelo se entrena con PostgreSQL.
Si todavía no los tiene, se genera un modelo bootstrap inicial.

## 4. Levantar API

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 5. Endpoints

- `GET /health`
- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`
- `GET /catalogs/form-data`
- `GET /incidentes`
- `POST /incidentes`
- `PUT /incidentes/{id}`
- `GET /alertas`
- `POST /alertas`
- `POST /alertas/{id}/resolve`
- `GET /dashboard/summary`
- `POST /predict`
- `POST /train`

## 6. Usuario demo inicial

Si la base está vacía, al arrancar se crea automáticamente:

- `admin@aspredictive.local`
- `Admin12345`

## 7. Integración con frontend

En el `.env` del frontend:

```bash
VITE_API_URL=http://localhost:8000
VITE_PREDICTIVE_API_URL=http://localhost:8000
```

## 8. Deploy en Render

El repo ya incluye [render.yaml](/C:/Users/Hugo%20Celis/OneDrive/Escritorio/AsPREDICTIVE/render.yaml) para crear el Web Service automáticamente.

Campos ya preparados:

- `rootDir=backend`
- `buildCommand=pip install -r requirements.txt && python train_model.py`
- `startCommand=uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- `healthCheckPath=/health`

Variables esperadas:

- `DATABASE_URL`:
  Debes cargar aquí la URL de Neon.
- `SECRET_KEY`:
  Render la genera automáticamente.
- `ACCESS_TOKEN_EXPIRE_MINUTES=720`

Una vez desplegado, usa esa URL en Netlify:

- `VITE_API_URL=https://tu-servicio.onrender.com`
- `VITE_PREDICTIVE_API_URL=https://tu-servicio.onrender.com`

Con esta configuración, Render entrena el modelo automáticamente durante el deploy usando:

1. `data/processed/ntsb_training_base.csv` si existe
2. incidentes de PostgreSQL si no existe ese CSV
3. bootstrap sintético solo como último fallback
