# PC Pedia — PC Hardware Database

A scalable searchable encyclopedia for computer hardware. Built with React (Vite + TypeScript) and Flask (Python) REST API with PostgreSQL.

## Architecture

```
                    PC PEDIA
                       │
                React + Vite
                       │
                  REST / JSON
                       │
                     Flask
                       │
                  SQLAlchemy
                       │
                  PostgreSQL
                       │
        ┌──────────────┴──────────────┐
        │                             │
   Hardware Taxonomy            Specifications
        │                             │
 Category → Manufacturer       Flexible Definitions
 → Family → Series             + Product Values
 → Generation → Product
```

### Hardware Taxonomy

```
Category → Manufacturer → Family → Series → Generation → Product → Specifications
```

Not every level is required for every product. For example, an SSD may skip Generation; a PSU may use Family → Series only.

## Project Structure

```
pc-hardware-database/
├── frontend/          # React + Vite + TypeScript + Tailwind CSS
├── backend/           # Flask REST API + SQLAlchemy
│   ├── app/
│   │   ├── models/    # Category, Manufacturer, Family, Series, Generation, Product, etc.
│   │   ├── routes/    # REST API endpoints
│   │   ├── services/  # product_service, taxonomy_service, import_service, admin_service
│   │   ├── schemas/
│   │   └── utils/     # validation, responses, helpers
│   ├── seed_data/     # Taxonomy and spec definition seed modules
│   ├── migrations/    # Flask-Migrate / Alembic
│   ├── tests/         # pytest API tests
│   └── seed.py        # Database seeder
└── README.md
```

## Prerequisites

- Node.js 18+ and npm
- Python 3.10+
- PostgreSQL 14+ (SQLite supported for local dev)

## Backend Setup

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env   # configure DATABASE_URL
```

### Database Migrations

```bash
cd backend
set FLASK_APP=run.py        # Windows
export FLASK_APP=run.py     # macOS/Linux

python -m flask db upgrade  # apply migrations
python seed.py              # seed taxonomy + demo products
python seed.py --reset      # drop and reseed (dev only)
```

### Run Flask

```bash
cd backend
python run.py
```

API: `http://localhost:5000`

## Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Frontend: `http://localhost:5173`

## API Documentation

### Response Format

List endpoints return:
```json
{ "data": [...] }
```

Paginated endpoints return:
```json
{
  "data": [...],
  "pagination": { "page": 1, "limit": 24, "total": 100, "pages": 5 }
}
```

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/home` | Popular, latest, manufacturers |
| GET | `/api/categories` | All categories (for navbar) |
| GET | `/api/categories/<slug>` | Category detail |
| GET | `/api/categories/<slug>/families` | Families in category |
| GET | `/api/categories/<slug>/series` | Series in category |
| GET | `/api/categories/<slug>/generations` | Generations in category |
| GET | `/api/categories/<slug>/specification-definitions` | Spec field definitions |
| GET | `/api/manufacturers` | Manufacturers (`?category=cpu`) |
| GET | `/api/products` | All products with filters |
| GET | `/api/products/<id>` | Product by ID |
| GET | `/api/products/by-slug/<slug>` | Product by slug |
| GET | `/api/products/<category>/<manufacturer>/<slug>` | Product by URL path |
| GET | `/api/cpus` … `/api/cases` | Category product listings |
| GET | `/api/search?q=<query>` | Global search |
| GET | `/api/compare?products=slug1,slug2` | Compare products (same category) |

### Query Parameters (product listings)

| Parameter | Description |
|-----------|-------------|
| `page` | Page number (default: 1) |
| `limit` | Items per page (default: 24, max: 100) |
| `category` | Category slug |
| `manufacturer` | Manufacturer slug |
| `family` | Family slug |
| `series` | Series slug |
| `generation` | Generation slug |
| `search` | Search term |
| `sort` | Sort field (`name`, `release_date`, `created_at`; prefix `-` for desc) |
| `order` | `asc` or `desc` |
| `spec_<key>` | Filter by specification value |

### Admin API (`/api/admin/*`)

CRUD for categories, manufacturers, families, series, generations, products, specification definitions. Bulk import via `POST /api/admin/import` with JSON array.

## URL Structure

| Pattern | Example |
|---------|---------|
| `/cpu` | CPU category page |
| `/cpu/amd/ryzen-7-7800x3d` | Product detail page |
| `/compare` | Comparison tool |
| `/admin` | Admin panel |

## Testing

```bash
cd backend
python -m pytest tests/ -v
```

```bash
cd frontend
npm run build
```

## Environment Variables

**Backend (`backend/.env`):**
```
DATABASE_URL=postgresql://user:pass@localhost:5432/pc_hardware_db
SECRET_KEY=your-secret-key
```

**Frontend (`frontend/.env`):**
```
VITE_API_URL=http://localhost:5000/api
```

## Data Import

Future hardware imports use `backend/app/services/import_service.py`:

```python
from app.services.import_service import HardwareImportService
service = HardwareImportService()
result = service.import_batch(records)  # JSON or CSV-derived records
```

The service resolves taxonomy (manufacturer → family → series → generation), validates specifications, and avoids duplicate products.
