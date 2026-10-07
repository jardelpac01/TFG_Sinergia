# Sinergia · Frontend

Interfaz web para explorar la producción científica, las redes de colaboración y exportar resultados.

## Stack

- React 18 + TypeScript
- Vite 5
- React Router 6
- TanStack Query 5
- Tailwind CSS 3

> Las versiones están fijadas para ser compatibles con Node 18.

## Requisitos

- Node.js 18 o superior
- Backend FastAPI en ejecución
- PostgreSQL levantado (`docker compose up -d` en `SinergIA/`)

## Puesta en marcha

```bash
npm install
npm run dev
```

La aplicación queda disponible en `http://localhost:5173`.



## Conexión con la API

En desarrollo, las peticiones a `/api` se redirigen a `http://127.0.0.1:8000`
mediante el proxy configurado en `vite.config.ts`, evitando problemas de CORS.

Para apuntar a otra API, define `VITE_API_BASE_URL` en un archivo `.env.local`:

```
VITE_API_BASE_URL=https://mi-api.example.com
```

## Scripts

| Comando | Descripción |
| --- | --- |
| `npm run dev` | Servidor de desarrollo |
| `npm run build` | Comprobación de tipos y build de producción |
| `npm run preview` | Sirve el build de producción |
| `npm run lint` | Análisis estático |

## Estructura

```text
src/
  api/          Cliente HTTP, endpoints y tipos de la API
  components/   Componentes compartidos (layout, paginación, estados)
  lib/          Utilidades (CSV, paginación, debounce)
  pages/        Pantallas enrutadas
```

## Funcionalidades

- Búsqueda de autores, publicaciones, instituciones y temas
- Ficha de autor con métricas, publicaciones y red de colaboración
- Filtrado por rango de años
- Paginación en todos los listados
- Exportación a CSV compatible con Excel
