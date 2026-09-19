# 🖥️ PC PEDIA

### The Hardware Encyclopedia for PC Builders, Enthusiasts & Developers

> **PC PEDIA** is a data-driven PC hardware encyclopedia designed to make computer hardware easier to explore, compare, understand, and build around.

<p align="center">
  <strong>CPU • GPU • RAM • Motherboards • Storage • Power • Cooling • Cases</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Active%20Development-8B5CF6?style=for-the-badge" alt="Status">
  <img src="https://img.shields.io/badge/Frontend-React%20%2B%20Vite-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="Frontend">
  <img src="https://img.shields.io/badge/Backend-Flask-000000?style=for-the-badge&logo=flask" alt="Backend">
  <img src="https://img.shields.io/badge/Database-SQLite-003B57?style=for-the-badge&logo=sqlite" alt="Database">
</p>

---

## ✨ What is PC PEDIA?

PC PEDIA is being built as a **structured encyclopedia and catalog for computer hardware**.

Instead of relying on hardcoded product pages or scattered specification lists, PC PEDIA uses a structured catalog architecture:

```text
Category
   ↓
Manufacturer
   ↓
Family
   ↓
Series
   ↓
Generation
   ↓
Product
   ↓
Specifications + Provenance
```

The goal is simple:

> **Find a component → understand its specifications → compare it with alternatives → build better PCs.**

---

## 🚀 Current Catalog

The project is being expanded in controlled, verified phases rather than importing unverified hardware data in bulk.

### 📊 Current verified catalog

| Hardware | Verified Products | Coverage |
|---|---:|---|
| 🧠 CPU | **219 catalog records** | Multiple Intel & AMD generations |
| 🎮 GPU | **67** | NVIDIA + AMD + Intel Arc |
| 🧩 RAM | **26** | DDR4 + DDR5 Desktop UDIMM |
| 🖥️ Motherboard | In development | — |
| 💾 SSD | In development | — |
| ⚡ PSU | In development | — |
| ❄️ CPU Cooler | In development | — |
| 💧 AIO | In development | — |
| 🌪️ Fan | In development | — |
| 🏠 Case | In development | — |

> **Note:** The CPU catalog contains 219 catalog records; the production database may contain an additional legacy/demo record depending on the current development state.

### 🎮 GPU coverage

**NVIDIA — 43 verified**

- GTX 10 Series — 9
- GTX 16 Series — 7
- RTX 20 Series — 8
- RTX 30 Series — 10
- RTX 40 Series — 9

**AMD — 19 verified**

- RX 6000 Series — 12
- RX 7000 Series — 7

**Intel — 5 verified**

- Arc A-Series Desktop — 5

### 🧩 RAM coverage

**26 verified desktop UDIMMs**

- DDR4 — 12
- DDR5 — 14

Current verified RAM manufacturers include:

- Corsair
- Kingston
- G.Skill
- Crucial
- TeamGroup

---

# 🎯 Core Principles

PC PEDIA follows a few rules throughout the catalog.

### 1. 🔎 Verified data over fabricated data

Hardware specifications should come from manufacturer documentation wherever possible.

The project deliberately avoids filling missing values with guesses.

```text
Official source
      ↓
Verified specification
      ↓
Structured catalog
      ↓
Database
      ↓
API
      ↓
Frontend
```

### 2. 🧬 Structured hardware identity

Products are represented using canonical identities rather than arbitrary retailer listings.

This allows the same hardware to remain identifiable across:

- Search
- Product pages
- Comparisons
- Filters
- Database records
- Catalog imports

### 3. 📚 Provenance matters

Catalog records contain source information so specifications can be traced back to their origin.

The project uses:

- `DataSource`
- `ProductSource`
- `SpecificationSource`

### 4. 🔁 Idempotent imports

Running a catalog importer repeatedly should not create duplicate products.

```text
First import
    ↓
Create verified products

Second import
    ↓
0 unexpected duplicates
```

### 5. 🧪 Test before expansion

Each major catalog phase is validated before moving to the next one.

The project uses:

- Focused catalog tests
- Full backend regression tests
- Catalog validation
- Import/dry-run validation
- API verification
- Frontend production builds

---

# 🏗️ Architecture

```text
                 ┌──────────────────────┐
                 │      React + Vite    │
                 │      Frontend        │
                 └──────────┬───────────┘
                            │
                         Axios
                            │
                            ▼
                 ┌──────────────────────┐
                 │      Flask API       │
                 │      Backend         │
                 └──────────┬───────────┘
                            │
                       SQLAlchemy
                            │
                            ▼
                 ┌──────────────────────┐
                 │       SQLite         │
                 │      Database        │
                 └──────────────────────┘

             Catalog Data / Provenance
                       │
                       ▼
             Validation + Importers
                       │
                       ▼
                    Database
```

---

# 🛠️ Technology Stack

## Frontend

- **React**
- **Vite**
- **TypeScript**
- **React Router**
- **Tailwind CSS**
- **Axios**

## Backend

- **Python**
- **Flask**
- **Flask-SQLAlchemy**
- **Flask-Migrate**
- **SQLAlchemy**

## Database

- **SQLite**

## Development & Data Pipeline

- Python catalog builders
- JSON catalog files
- Structured specification definitions
- Catalog validation
- Provenance tracking
- Automated test suites
- Git-based version control

---

# 📁 Project Structure

```text
PC-Pedia/
│
├── backend/
│   ├── app/
│   │   ├── catalog/
│   │   ├── data/
│   │   ├── services/
│   │   └── ...
│   │
│   ├── data/
│   │   └── catalog/
│   │       ├── cpu/
│   │       ├── gpu/
│   │       └── ram/
│   │
│   ├── scripts/
│   │   ├── build_cpu_catalog.py
│   │   ├── build_gpu_catalog.py
│   │   └── build_ram_catalog.py
│   │
│   ├── seed_data/
│   ├── tests/
│   └── ...
│
├── frontend/
│   ├── public/
│   │   └── images/
│   │       └── hardware/
│   │           ├── cpu.svg
│   │           ├── gpu.svg
│   │           ├── ram.svg
│   │           ├── motherboard.svg
│   │           ├── ssd.svg
│   │           ├── psu.svg
│   │           ├── cooler.svg
│   │           ├── aio.svg
│   │           ├── fan.svg
│   │           └── case.svg
│   │
│   └── ...
│
└── README.md
```

---

# 🗂️ Catalog Pipeline

Every hardware category follows a controlled pipeline.

```text
Manufacturer Documentation
            │
            ▼
     Catalog Definition
            │
            ▼
       Validation
            │
            ▼
        Dry Run
            │
            ▼
       Database Import
            │
            ▼
      Reconciliation
            │
            ▼
       API Validation
            │
            ▼
      Frontend Validation
            │
            ▼
          Tests
```

This approach makes it possible to expand PC PEDIA without turning the database into an uncontrolled collection of scraped or duplicated products.

---

# 🔐 Data Provenance

PC PEDIA treats source provenance as part of the hardware data model.

```text
Product
 ├── ProductSource
 │      ├── Manufacturer
 │      ├── URL
 │      └── Source metadata
 │
 └── Specifications
        └── SpecificationSource
```

Official manufacturer sources used throughout the catalog include domains such as:

- `intel.com`
- `amd.com`
- `nvidia.com`
- `corsair.com`
- `kingston.com`
- `gskill.com`
- `crucial.com`
- `teamgroup.com`

The exact source is stored with the corresponding catalog/product data.

---

# 🎮 GPU Catalog

The GPU catalog is currently one of the most mature sections of PC PEDIA.

```text
GPU
├── NVIDIA
│   └── GeForce
│       ├── GTX 10
│       ├── GTX 16
│       ├── RTX 20
│       ├── RTX 30
│       └── RTX 40
│
├── AMD
│   └── Radeon RX
│       ├── RX 6000
│       └── RX 7000
│
└── Intel
    └── Arc
        └── A-Series
```

### GPU verification status

**67 verified products**

- 43 NVIDIA
- 19 AMD
- 5 Intel

The catalog has also undergone a cross-vendor audit covering:

- Catalog ↔ database parity
- Taxonomy
- Canonical slugs
- Variant representation
- Provenance
- Specifications
- API filters
- Search
- Import idempotency
- Legacy/demo reconciliation

---

# 🧩 RAM Catalog

The RAM catalog currently focuses on desktop UDIMM memory.

```text
RAM
└── Desktop Memory
    └── UDIMM
        ├── DDR4
        └── DDR5
```

Current verified catalog:

```text
DDR4 → 12
DDR5 → 14
──────────
Total → 26
```

The RAM model distinguishes concepts such as:

- Module capacity
- Total kit capacity
- Module count
- Rated data rate
- JEDEC speed
- CAS latency
- Timings
- Voltage
- XMP
- EXPO
- Form factor
- ECC/registered/buffered characteristics

The catalog intentionally leaves fields empty when official manufacturer documentation does not provide reliable information.

---

# 🧠 CPU Catalog

The CPU catalog follows the same verification-first approach.

It includes multiple Intel and AMD generations and uses structured specifications rather than hardcoded product pages.

The CPU pipeline includes:

- Canonical CPU slugs
- Manufacturer taxonomy
- Generation classification
- Specification definitions
- Official-source provenance
- Catalog validation
- Import idempotency
- Automated regression tests

---

# 🔍 Search & Discovery

PC PEDIA is designed around hardware discovery.

Users should be able to search by:

```text
Product name
Manufacturer
Family
Series
Generation
Part number
Specification
```

Example searches:

```text
RTX 4090
RX 7900 XTX
Arc A770
CMK32GX5M2B6000C30
KF556C40BBK2-32
```

Part numbers are particularly important for RAM because visually similar products can have completely different specifications.

---

# ⚖️ Hardware Comparison

PC PEDIA supports structured hardware comparison.

Instead of comparing arbitrary text descriptions, products can be compared through their structured specification data.

```text
┌──────────────────┬─────────────────┬─────────────────┐
│ Specification    │ Product A       │ Product B       │
├──────────────────┼─────────────────┼─────────────────┤
│ Manufacturer     │ ...             │ ...             │
│ Generation       │ ...             │ ...             │
│ Capacity         │ ...             │ ...             │
│ Speed            │ ...             │ ...             │
│ Architecture     │ ...             │ ...             │
│ Power            │ ...             │ ...             │
└──────────────────┴─────────────────┴─────────────────┘
```

Missing official specifications are kept missing rather than replaced with guesses.

---

# 🖼️ Hardware Visual System

PC PEDIA uses category-specific graphical fallbacks for hardware that does not have a verified product image.

```text
CPU          → cpu.svg
GPU          → gpu.svg
RAM          → ram.svg
Motherboard  → motherboard.svg
SSD          → ssd.svg
PSU          → psu.svg
Cooler       → cooler.svg
AIO          → aio.svg
Fan          → fan.svg
Case         → case.svg
```

This provides a consistent visual identity without relying on random scraped images.

---

# 🧪 Quality & Testing

PC PEDIA uses automated testing as part of catalog expansion.

### Catalog

- Schema validation
- Required fields
- Canonical slugs
- Duplicate detection
- Specification definitions
- Provenance

### Database

- Product creation
- Reconciliation
- Import idempotency
- Taxonomy
- Product relationships

### API

- Listing
- Search
- Filtering
- Pagination
- Product details
- Comparison

### Frontend

- Production builds
- Hardware rendering
- Catalog integration

---

# 🚦 Development Philosophy

PC PEDIA is intentionally being developed in **phases**.

A typical phase looks like:

```text
Research
   ↓
Official source verification
   ↓
Catalog construction
   ↓
Validation
   ↓
Import
   ↓
Reconciliation
   ↓
Testing
   ↓
Audit
   ↓
Next phase
```

This prevents rapid catalog expansion from compromising data quality.

---

# 🗺️ Roadmap

### ✅ Completed / Active

- [x] Core hardware catalog architecture
- [x] CPU catalog infrastructure
- [x] NVIDIA GPU catalog
- [x] AMD GPU catalog
- [x] Intel Arc GPU catalog
- [x] GPU cross-vendor audit
- [x] RAM catalog infrastructure
- [x] DDR4 desktop UDIMM catalog
- [x] DDR5 desktop UDIMM catalog

### 🔨 In Development

- [ ] RAM cross-generation audit
- [ ] Motherboard catalog
- [ ] SSD catalog
- [ ] PSU catalog
- [ ] CPU cooler catalog
- [ ] AIO catalog
- [ ] Fan catalog
- [ ] PC case catalog

### 🔮 Future

- [ ] Advanced PC Builder
- [ ] Compatibility analysis
- [ ] Build recommendations
- [ ] Performance-oriented comparisons
- [ ] More hardware generations
- [ ] More form factors
- [ ] Expanded hardware provenance
- [ ] Richer product imagery

---

# 💻 Local Development

## Clone

```bash
git clone https://github.com/shivangsaxena2211/PC-Pedia.git
cd PC-Pedia
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

For the backend, install the project's Python dependencies and start Flask using the commands/configuration defined by the current repository.

---

# 🤝 Contributing

Contributions are welcome around:

- Hardware data verification
- Catalog tooling
- API improvements
- Frontend UX
- Testing
- Documentation
- Hardware taxonomy

For new catalog data, follow the core rule:

> **If the specification cannot be verified, don't invent it.**

When adding hardware, provide:

1. Official manufacturer source
2. Correct manufacturer identity
3. Correct product/part number
4. Canonical slug
5. Verified specifications
6. Appropriate provenance
7. Tests where applicable

---

# 📜 Data Philosophy

PC PEDIA is not intended to be a giant list of numbers.

It is intended to become a **structured knowledge base for PC hardware**.

```text
Accuracy
   +
Structure
   +
Provenance
   +
Searchability
   +
Comparability
   =
PC PEDIA
```

When a manufacturer does not publish a specification clearly, PC PEDIA prefers:

> **Unknown**

over:

> **Made up**

---

# 👨‍💻 Project

**PC PEDIA**

A hardware encyclopedia and catalog for PC enthusiasts, builders, students, developers, and anyone who wants structured information about computer components.

### Built with ❤️ using

**React • TypeScript • Vite • Tailwind • Flask • Python • SQLAlchemy • SQLite**

---

<p align="center">
  <strong>PC PEDIA</strong><br>
  <em>Know your hardware. Build smarter.</em>
</p>
