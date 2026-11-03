# Manufacturing Traceability & Quality System

A manufacturing traceability system for connecting supplier materials, material lots, production orders, process steps, inspections, defects, and corrective actions.

The main goal is to answer a practical quality question:

> **When a defect is found, where did it come from, what production was affected, and what corrective action was taken?**

---

## 1. Project Overview

The system models the manufacturing and quality workflow from incoming supplier material through production and inspection to defect investigation and corrective action.

The main traceability chain is:

```text
Supplier
   ↓
Material Lot
   ↓
Material Consumption
   ↓
Production Order
   ↓
Process Step / Machine
   ↓
Inspection
   ↓
Defect
   ↓
Corrective Action
```

The application supports both:

- **Forward traceability** — from a production order to the materials, suppliers, inspections, defects, and corrective actions involved.
- **Reverse traceability** — from a material lot to the production orders and quality records affected by that lot.

The project uses synthetic data so that the complete workflow can be reproduced without using confidential manufacturing data.

---

## 2. Main Features

### Production Traceability

Given a production order, the system can identify:

- product;
- BOM;
- required materials;
- consumed material lots;
- suppliers;
- process steps;
- machines;
- inspection results;
- defects;
- corrective actions.

### Material Lot Traceability

Given a material lot, the system can identify:

- supplier;
- material;
- quantity;
- production orders where the lot was consumed;
- related inspections;
- defects;
- corrective actions.

### Quality Tracking

The system tracks:

- inspection quantities;
- passed quantities;
- failed quantities;
- defect quantities;
- defect severity;
- defect status;
- corrective-action status.

### Dashboard

The dashboard provides summary information from the underlying records, including inspection and defect metrics.

The defect rate is derived from inspection quantities:

```text
Defect Rate =
Failed Quantity / Inspected Quantity × 100
```

---

## 3. Technology Stack

### Backend

- Python
- Django
- Django REST Framework
- PostgreSQL

### Frontend

- React
- Vite
- Axios

### Database

PostgreSQL is used because the project depends heavily on relational integrity and traceability between multiple entities.

---

## 4. Project Structure

```text
manufacturing-traceability/
│
├── backend/
│   ├── manage.py
│   ├── manufacturing/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   └── migrations/
│   │
│   ├── create_additional_inspection_plans.py
│   ├── create_capa.py
│   ├── create_defects.py
│   ├── create_inspection_plans.py
│   ├── create_inspection_results.py
│   ├── inject_edge_cases.py
│   ├── validate_defects.py
│   └── validate_inspection_results.py
│
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
│
├── docs/
│   ├── AI_PROMPT_HISTORY.md
│   ├── ARCHITECTURE.md
│   ├── DATA_DICTIONARY.md
│   ├── VALIDATION.md
│   └── ASSUMPTIONS.md
│
├── .gitignore
└── README.md
```

---

# 5. Database Model

The main entities are:

| Entity | Purpose |
|---|---|
| Product | Finished/manufactured product |
| Supplier | Supplier providing materials |
| Machine | Manufacturing equipment |
| BOM | Bill of materials for a product |
| Material | Raw/component material |
| BOMComponent | Material requirement within a BOM |
| MaterialLot | Supplier-specific material batch |
| ProductionOrder | Manufacturing order |
| MaterialConsumption | Actual material lot consumption |
| ProcessStep | Manufacturing process step |
| InspectionPlan | Definition of an inspection |
| InspectionResult | Actual inspection result |
| Defect | Quality issue found during inspection |
| CorrectiveAction | Action taken to address a defect |

Relationships are implemented using foreign keys and bridge/event tables where required.

---

# 6. Dataset

The generated dataset is synthetic and uses a fixed random seed.

```text
Seed: 20261022
```

The main dataset contains approximately:

| Entity | Records |
|---|---:|
| Products | 200 |
| Suppliers | 50 |
| Materials | 200 |
| BOMs | 200 |
| BOM Components | 909 |
| Production Orders | 5,000 |
| Material Lots | 2,000 |
| Material Consumption | 24,265 |
| Machines | 10 |
| Process Steps | 12 |
| Inspection Plans | 800 |
| Inspection Results | 20,000 |
| Defects | 20,000 |

Corrective-action records are generated separately and should be verified using the database before making any claim about their final count.

---

# 7. Data Generation

The data is generated in dependency order.

```text
Products
   ↓
Suppliers
   ↓
Materials
   ↓
BOMs
   ↓
BOM Components
   ↓
Material Lots
   ↓
Production Orders
   ↓
Material Consumption
   ↓
Machines
   ↓
Process Steps
   ↓
Inspection Plans
   ↓
Inspection Results
   ↓
Defects
   ↓
Corrective Actions
```

This order ensures that dependent records can reference their parent records.

---

# 8. Validation

The project includes validation for:

- primary-key uniqueness;
- duplicate business identifiers;
- foreign-key integrity;
- production-order date ordering;
- material consumption;
- lot over-consumption;
- inspection quantity reconciliation;
- defect quantity validation;
- missing relationships;
- inspection-plan relationships;
- traceability relationships.

The baseline validation results include:

```text
Material requirement mismatches: 0
Lot over-consumption cases: 0
Invalid production-order dates: 0

Duplicate product SKUs: 0
Duplicate supplier codes: 0
Duplicate material codes: 0
Duplicate production-order numbers: 0
Duplicate material-lot numbers: 0

Inspection quantity mismatches: 0
Missing inspection plans/orders: 0
Invalid inspection quantities: 0

Defects exceeding failed quantity: 0
Missing defect relationships: 0
```

More detailed validation information is available in:

```text
docs/VALIDATION.md
```

---

# 9. Intentional Edge Cases

Five edge cases are included to test whether the system can identify broken or invalid traceability conditions.

| ID | Scenario |
|---|---|
| EDGE-001 | Defect references a nonexistent material lot |
| EDGE-002 | BOM material was not consumed |
| EDGE-003 | CAPA closes before verification |
| EDGE-004 | Defect quantity exceeds inspected quantity |
| EDGE-005 | Traceability chain is broken |

These cases are intentionally separated from the valid baseline dataset.

They are stored in the `ground_truth_edge_cases` table so that the expected abnormal conditions can be identified during testing.

---

# 10. Running the Backend

## Create and activate the virtual environment

From the project root:

### Windows PowerShell

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, the environment can also be activated through Command Prompt:

```cmd
venv\Scripts\activate.bat
```

---

## Install backend dependencies

```powershell
cd backend
pip install -r requirements.txt
```

---

## Configure PostgreSQL

Create a PostgreSQL database named:

```text
manufacturing_traceability
```

Configure the database connection using the Django settings/environment configuration used by the project.

Do not commit database passwords or other credentials to GitHub.

---

## Apply migrations

From the `backend` directory:

```powershell
python manage.py migrate
```

---

## Start Django

```powershell
python manage.py runserver
```

The backend runs by default at:

```text
http://127.0.0.1:8000/
```

---

# 11. Running the Frontend

Open another terminal.

```powershell
cd frontend
npm install
npm run dev
```

The frontend runs at:

```text
http://localhost:5173/
```

The Vite development server proxies `/api` requests to the Django backend.

---

# 12. Important API Endpoints

### Production Orders

```text
GET /api/production-orders/
```

### Material Lots

```text
GET /api/material-lots/
```

### Inspections

```text
GET /api/inspection-results/
```

### Defects

```text
GET /api/defects/
```

### Corrective Actions

```text
GET /api/corrective-actions/
```

### Production Order Traceability

```text
GET /api/traceability/<order_number>/
```

Example:

```text
GET /api/traceability/WO-2026-000001/
```

### Material Lot Traceability

```text
GET /api/lot-traceability/<lot_number>/
```

### Dashboard

```text
GET /api/dashboard/
```

The traceability endpoints are the main demonstration endpoints for the project.

---

# 13. Traceability Example

A production order can be followed through the system:

```text
Production Order
      │
      ├── Product
      ├── BOM
      │
      ├── Material Consumption
      │       └── Material Lot
      │              └── Supplier
      │
      ├── Process Steps
      │       └── Machine
      │
      ├── Inspection Results
      │       └── Defects
      │              └── Corrective Actions
      │
      └── Quality information
```

This allows an investigator to move from the finished production record back toward the incoming material source.

The reverse direction is also supported:

```text
Material Lot
     ↓
Production Orders
     ↓
Inspections
     ↓
Defects
     ↓
Corrective Actions
```

---

# 14. Reproducibility

The dataset generator uses a fixed seed:

```text
20261022
```

Using the same generator configuration and seed should produce reproducible data.

For a stronger reproducibility check, generation can be performed twice and the resulting row counts/checksums compared.

---

# 15. Documentation

Additional project documentation:

### Architecture

```text
docs/ARCHITECTURE.md
```

Describes the system structure, database relationships, traceability flow, API layer, and design tradeoffs.

### Data Dictionary

```text
docs/DATA_DICTIONARY.md
```

Documents entities, fields, relationships, constraints, and identifiers.

### Validation

```text
docs/VALIDATION.md
```

Documents validation checks and observed results.

### Assumptions

```text
docs/ASSUMPTIONS.md
```

Documents business and implementation assumptions that were not explicitly defined by the assignment.

### AI Prompt History

```text
docs/AI_PROMPT_HISTORY.md
```

Documents AI-assisted development, prompt history, review, and validation responsibilities.

---

# 16. AI-Assisted Development

AI tools were used during development for assistance with:

- project structure;
- database modeling discussions;
- implementation guidance;
- API design;
- frontend development;
- debugging;
- validation logic;
- documentation.

The implementation was reviewed and tested before inclusion in the repository.

The AI prompt history and development disclosure are documented separately in:

```text
docs/AI_PROMPT_HISTORY.md
```

The prompt-history document is a reconstructed record where an exact tool export was not available. It is not presented as an exact transcript.

---

# 17. Current Limitations

This is a candidate project rather than a production MES/QMS implementation.

Current limitations include:

- no authentication;
- no role-based access control;
- no real-time machine integration;
- no IoT/PLC integration;
- no production deployment;
- limited write workflows;
- no full enterprise audit-event system;
- synthetic rather than real manufacturing data.

These limitations are intentional and documented rather than hidden.

---

# 18. Verification Checklist

After starting the application, verify:

### Backend

```text
[ ] Django starts successfully
[ ] PostgreSQL connection works
[ ] API endpoints return data
[ ] Traceability endpoint returns related records
[ ] Lot traceability endpoint returns related records
[ ] Dashboard returns calculated metrics
```

### Frontend

```text
[ ] React application loads
[ ] Dashboard displays
[ ] Production order traceability works
[ ] Material lot traceability works
[ ] Nested API data renders correctly
```

### Data

```text
[ ] Primary keys are unique
[ ] Foreign keys are valid
[ ] Material consumption reconciles
[ ] Inspection quantities reconcile
[ ] Defect quantities are valid
[ ] Edge cases are identifiable
```

---

# 19. Final Verification

Before submission, the repository should be checked for:

```text
[ ] No passwords or API keys
[ ] No .env files containing secrets
[ ] No virtual environment
[ ] No node_modules
[ ] README is present
[ ] Documentation is present
[ ] Database migrations are present
[ ] Generator scripts are present
[ ] Validation scripts are present
[ ] AI prompt history is present
[ ] Git history contains meaningful commits
[ ] Repository is publicly accessible
```

---

## 20. Project Goal

The project is not intended to claim that it implements a complete industrial quality-management platform.

Its purpose is narrower:

> **Demonstrate a working relational traceability system that can connect a quality defect back through inspection, production, material consumption, material lot, and supplier information, while also identifying broken traceability and data-quality conditions.**