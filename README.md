# FriendlyEats FastAPI — Sprint 1

Sistema para promocionar los restaurantes populares de la zona (Puebla y alrededores).
Este primer sprint entrega una **versión local funcional**: CRUD de restaurantes en
Firestore (emulador) desde una app FastAPI con vistas HTML.

**Fuera del alcance del Sprint 1** (se verá en sprints posteriores): autenticación,
reseñas, subida de imágenes y despliegue.

## Roles

| Rol | Qué hace | Estado en Sprint 1 |
|---|---|---|
| Visitante | Ver el listado, filtrar y abrir el detalle de un restaurante | Disponible |
| Administrador | Crear, editar y eliminar restaurantes | Disponible (sin login todavía) |
| Propietario | Gestionar solo sus restaurantes (`ownerId`) | Planeado para el Sprint 2 |

Como aún no hay autenticación, en este sprint todas las acciones están abiertas.

## Tecnologías

- Python 3.12 · FastAPI · Uvicorn · Jinja2 (vistas HTML)
- Pydantic v2 y pydantic-settings (validación y configuración)
- Firestore (emulador local) con `firebase-admin` / `google-cloud-firestore`
- pytest + httpx (pruebas)

## Estructura

```text
Producto_Sprint/
├── app/
│   ├── main.py                    # App, vistas HTML y /health
│   ├── core/
│   │   ├── config.py              # Variables de entorno (Settings)
│   │   └── firebase.py            # Cliente de Firestore
│   ├── domain/
│   │   ├── models.py              # Constantes del dominio
│   │   └── schemas.py             # Esquemas Pydantic (validaciones)
│   ├── repositories/
│   │   └── restaurant_repository.py   # Único acceso a Firestore
│   ├── services/
│   │   └── restaurant_service.py  # Reglas de negocio y errores 404/400
│   ├── api/v1/restaurants.py      # Endpoints REST
│   └── templates/                 # base, listado, detalle, formulario, error
├── static/ (css/styles.css, js/app.js, img/)
├── scripts/seed.py                # Datos semilla (10 restaurantes)
├── tests/                         # Pruebas del CRUD y las vistas
├── firebase.json · firestore.rules · firestore.indexes.json · .firebaserc
├── .env.example · requirements.txt · pytest.ini
└── README.md
```

Arquitectura por capas: **API/Vistas → Servicio → Repositorio → Firestore**.
Ninguna capa superior toca Firestore directamente.

## Requisitos

- Python 3.12+
- Node.js y Firebase CLI: `npm install -g firebase-tools`
- Java (lo necesita el emulador de Firestore)

## Instalación

```bash
python -m venv .venv

# Linux / macOS
source .venv/bin/activate
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

## Configuración

Copia el archivo de ejemplo y ajústalo:

```bash
cp .env.example .env        # Windows: copy .env.example .env
```

| Variable | Descripción |
|---|---|
| `FIREBASE_PROJECT_ID` | ID del proyecto. Debe coincidir con `firebase use` (`.firebaserc`) |
| `FIRESTORE_EMULATOR_HOST` | `127.0.0.1:8080` para usar el emulador |
| `FIREBASE_CREDENTIALS_PATH` | Opcional; no se necesita con el emulador |

El archivo `.env` y cualquier JSON de cuenta de servicio están en `.gitignore`:
**no se sube ninguna credencial a Git**.

Para vincular el proyecto de Firebase:

```bash
firebase use          # debe mostrar el proyecto de .firebaserc
# Si usas otro proyecto: firebase use --add
```

## Ejecución

Abre dos terminales en la raíz del proyecto.

```bash
# Terminal 1: emulador de Firestore (UI en http://localhost:4000)
firebase emulators:start --only firestore

# Terminal 2: aplicación (con el entorno virtual activo)
uvicorn app.main:app --reload
```

Abre <http://localhost:8000>.

Cargar los datos semilla (se puede repetir sin duplicar):

```bash
python -m scripts.seed
```

Los datos quedan visibles en la UI del emulador: <http://localhost:4000/firestore>
(colección `restaurants`).

## Pruebas

Con el emulador encendido:

```bash
pytest -v
```

Las pruebas **se detienen si el emulador no está activo** para no escribir nunca en
una base real. Cada prueba borra los documentos que crea.

Cubren: salud, crear (y validaciones de precio, campos obligatorios, textos vacíos y
URL), obtener (200/404), listar (límite, paginación, orden), filtros por ciudad,
categoría y precio, editar (solo campos permitidos, 400/404/422), eliminar (204/404)
y las vistas HTML.

## Endpoints de la API

| Método | Ruta | Descripción | Respuestas |
|---|---|---|---|
| GET | `/health` | Estado del servicio | 200 `{"status": "ok"}` |
| POST | `/api/v1/restaurants` | Crear restaurante | 201 con `id`; 422 si no valida |
| GET | `/api/v1/restaurants` | Listar (paginado) | 200 lista |
| GET | `/api/v1/restaurants/{id}` | Obtener uno | 200; 404 |
| PATCH | `/api/v1/restaurants/{id}` | Actualizar campos enviados | 200; 400 (vacío); 404; 422 |
| DELETE | `/api/v1/restaurants/{id}` | Eliminar | 204; 404 |

Parámetros de `GET /api/v1/restaurants`: `city`, `category`, `price` (1-3),
`order_by` (`name` o `avgRating`), `limit` (1-100, por defecto 20) y `start_after`
(ID del último documento de la página anterior).

Documentación interactiva: <http://localhost:8000/docs>

## Vistas HTML

| Ruta | Vista |
|---|---|
| `/` | Listado en tarjetas con filtros (ciudad, categoría, precio) y orden |
| `/restaurants/new` | Formulario para crear |
| `/restaurants/{id}` | Detalle con botones Editar y Eliminar |
| `/restaurants/{id}/edit` | Formulario para editar |

## Decisiones técnicas

- **IDs automáticos** al crear (`document()`); el seed usa `set()` con IDs fijos para ser repetible.
- **`avgRating` y `numRatings`** empiezan en 0 y no se pueden editar por la API.
- **Validación**: precio entre 1 y 3, textos sin espacios sobrantes ni vacíos, y `photoUrl`
  solo `http(s)` (evita URLs peligrosas como `javascript:`). Una URL vacía se guarda como `null`.
- **Orden**: por `name` ascendente y por `avgRating` descendente (mejor calificados primero).
- **Paginación** con cursor (`start_after`), 20 por página; la vista muestra "Siguiente página".
- **Errores**: la API responde JSON y las vistas HTML responden una página de error.
- **Índices**: el emulador no exige índices compuestos, pero Firestore real sí cuando se
  combinan filtros con orden; se definirán al desplegar.
- **Reglas de seguridad**: las reglas abiertas de `firestore.rules` son solo para desarrollo
  local (el Admin SDK las ignora). Se reemplazarán en el Sprint 2.

## Estado de la definición de terminado

- [x] Ejecutar con `uvicorn app.main:app --reload`
- [x] Ver el listado en `http://localhost:8000`
- [x] Crear un restaurante desde un formulario HTML
- [x] Ver el detalle
- [x] Editar y eliminar
- [x] Filtrar por ciudad, categoría o precio
- [x] Datos visibles en el emulador de Firestore
- [x] Pruebas básicas del CRUD

## Siguiente sprint

Firebase Authentication, control de propietario con `ownerId`, Security Rules y
reseñas con transacciones.
