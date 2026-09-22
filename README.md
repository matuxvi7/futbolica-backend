# Futbolica Backend

Backend del MVP de **El Conector**, construido con Flask, PostgreSQL y WebSockets.

## Estructura

```text
src/
├── models/         # Entidades y modelos de persistencia
├── repositories/   # Acceso a datos
├── routes/         # Endpoints HTTP y WebSockets
├── services/       # Casos de uso y reglas de negocio
└── validators/     # Validacion de entradas y contratos
```

La aplicacion usa una app factory para mantener separadas la configuracion, las
extensiones y el registro de rutas.

## Desarrollo local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
pytest
ruff check .
black --check .
```

La API queda disponible en `http://localhost:5000/api/v1/health` al ejecutar
`flask --app app.py run`.

## Docker

Requiere Docker Engine y Docker Compose.

```bash
cp .env.example .env
docker compose up --build
```

Esto inicia dos servicios:

- `api`: la aplicacion Flask en `http://localhost:5000`.
- `db`: PostgreSQL 16 en el puerto `5432`.

La base de datos usa el volumen `postgres_data`, por lo que sus datos persisten
al detener los contenedores. Para detenerlos:

```bash
docker compose down
```

Para eliminar tambien los datos persistidos:

```bash
docker compose down -v
```
