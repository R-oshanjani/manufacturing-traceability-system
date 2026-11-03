# System Architecture

## 1. Overview

The Manufacturing Traceability & Quality System is a web application built to connect manufacturing and quality information in one traceable workflow.

The main goal is simple:

> If a defect is found, the system should help us identify which production order was affected, which material lot was used, which supplier provided that material, which process and machine were involved, and what corrective action was taken.

The application has three main parts:

```text
React + Vite
     |
     | HTTP / REST API
     v
Django + Django REST Framework
     |
     | Django ORM
     v
PostgreSQL
```

The frontend is responsible for displaying the information.

The Django backend contains the application logic and exposes the REST APIs.

PostgreSQL stores the manufacturing and quality data.

---

# 2. Why This Architecture

I chose Django, Django REST Framework, PostgreSQL, React, and Vite because the project is mainly a relational-data and traceability problem.

There are many relationships between the records. For example:

```text
Supplier
   ↓
Material Lot
   ↓
Material Consumption
   ↓
Production Order
   ↓
Inspection
   ↓
Defect
   ↓
Corrective Action
```

PostgreSQL is a good fit for this because these relationships need foreign keys and consistent data.

Django provides the database model and ORM layer, while Django REST Framework provides the API.

React was used for the user interface so the traceability information can be displayed without requiring users to work directly with database records.

---

# 3. Backend Architecture

The backend is a Django project.

```text
backend/
│
├── manage.py
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
└── manufacturing/
    ├── models.py
    ├── serializers.py
    ├── views.py
    ├── urls.py
    ├── admin.py
    ├── tests.py
    │
    ├── migrations/
    │
    └── management/
        └── commands/
            └── generate_data.py
```

### `models.py`

Contains the database models and relationships.

### `serializers.py`

Converts Django model instances into JSON responses used by the frontend.

### `views.py`

Contains the API viewsets and the main traceability and dashboard endpoints.

### `urls.py`

Maps API URLs to the appropriate views.

### `management/commands/generate_data.py`

Generates the synthetic manufacturing dataset.

---

# 4. Database Architecture

The database is PostgreSQL.

The main tables represent different parts of the manufacturing process.

```text
Product
   |
   +---- BOM
   |       |
   |       +---- BOMComponent ---- Material
   |
   +---- ProductionOrder
             |
             +---- MaterialConsumption ---- MaterialLot ---- Supplier
             |
             +---- InspectionResult
                       |
                       +---- Defect
                               |
                               +---- CorrectiveAction

ProductionOrder
      |
      +---- InspectionResult
                  |
                  +---- InspectionPlan
                           |
                           +---- ProcessStep ---- Machine
```

This structure keeps the relationships explicit instead of storing the complete traceability chain as duplicated text.

---

# 5. Core Entities

## Product

Represents the finished product being manufactured.

Important fields include:

- SKU
- name
- description
- unit of measure
- active status

---

## Material

Represents a raw material or component used to manufacture a product.

---

## BOM

Represents a version of the bill of materials for a product.

A product can have multiple BOM versions.

Each BOM has:

- product
- version
- effective start date
- effective end date
- active status

---

## BOMComponent

Connects a BOM to the materials required to manufacture the product.

It also stores:

- required quantity
- scrap percentage
- sequence

This is important because a BOM is not directly related to a material through a single field. One BOM can contain multiple materials.

---

## Supplier

Represents the supplier responsible for providing a material.

---

## MaterialLot

Represents a specific received lot of material.

A material lot is connected to:

- one material
- one supplier
- received quantity
- received date
- status

This is the starting point for supplier-level traceability.

---

## ProductionOrder

Represents a manufacturing order.

It connects:

- product
- BOM
- planned quantity
- actual quantity
- planned dates
- actual dates
- production status

---

## MaterialConsumption

Represents the actual consumption of a material lot by a production order.

This relationship is important because knowing that a material lot exists is not enough.

We need to know:

> Which production order actually used this lot?

The `MaterialConsumption` table provides that link.

---

## Machine

Represents a manufacturing machine.

---

## ProcessStep

Represents a step in the manufacturing process.

Each process step is connected to a machine and has a sequence number.

This allows a defect to be associated with a particular point in the manufacturing process.

---

## InspectionPlan

Defines what inspection should be performed.

It connects a product and process step with an inspection type and specification.

---

## InspectionResult

Represents an actual inspection performed against a production order.

It records:

- inspected quantity
- passed quantity
- failed quantity
- result
- inspection time

---

## Defect

Represents a quality problem detected during inspection.

A defect is connected to:

- inspection result
- production order
- process step

It also stores:

- defect type
- severity
- quantity
- description
- status

---

## CorrectiveAction

Represents the action taken to investigate and address a defect.

It contains information such as:

- root cause
- containment action
- corrective action
- preventive action
- assigned person
- target date
- completion date
- verification date
- verification result

---

# 6. Main Traceability Flow

The main investigation starts with a production order.

For example:

```text
WO-2026-000001
       |
       +---- Product
       |
       +---- BOM
       |       |
       |       +---- Material requirements
       |
       +---- Material Consumption
       |       |
       |       +---- Material Lot
       |               |
       |               +---- Supplier
       |
       +---- Inspection Results
               |
               +---- Process Step
               |       |
               |       +---- Machine
               |
               +---- Defects
                       |
                       +---- Corrective Actions
```

The API builds this relationship into a single traceability response.

This avoids forcing the frontend to make many separate requests just to understand one production order.

---

# 7. Reverse Traceability

The system also supports tracing forward from a material lot.

For example:

```text
Material Lot
     |
     +---- Production Order A
     |        |
     |        +---- Inspections
     |        +---- Defects
     |        +---- Corrective Actions
     |
     +---- Production Order B
              |
              +---- Inspections
              +---- Defects
              +---- Corrective Actions
```

This is useful when a supplier reports a problem with a material lot.

Instead of checking production orders manually, the system can identify where that lot was consumed.

---

# 8. API Layer

Django REST Framework is used for the API.

Most entity endpoints are read-only because the generated dataset is primarily being used for traceability analysis.

Examples:

```text
GET /api/products/
GET /api/material-lots/
GET /api/production-orders/
GET /api/inspection-results/
GET /api/defects/
```

The application also has purpose-built endpoints for the main workflows.

### Production order traceability

```text
GET /api/traceability/<order_number>/
```

### Material lot traceability

```text
GET /api/lot-traceability/<lot_number>/
```

### Dashboard

```text
GET /api/dashboard/
```

---

# 9. Query Optimization

Traceability requires several related records.

For example, one production order can have:

- multiple material consumptions
- multiple inspections
- multiple defects
- multiple corrective actions

If each relationship is loaded independently, the number of database queries can grow quickly.

The backend therefore uses Django ORM features such as:

```python
select_related()
```

for foreign-key relationships and:

```python
prefetch_related()
```

for collections of related records.

The goal is to retrieve the required traceability information efficiently rather than repeatedly querying the database for each related object.

---

# 10. Data Generation Architecture

The project uses synthetic data instead of real manufacturing data.

The generator creates the records in dependency order.

```text
Products
   ↓
Suppliers
   ↓
Materials
   ↓
BOMs / BOM Components
   ↓
Material Lots
   ↓
Production Orders
   ↓
Material Consumption
   ↓
Machines / Process Steps
   ↓
Inspection Plans
   ↓
Inspection Results
   ↓
Defects
   ↓
Corrective Actions
```

This order matters because dependent records require valid parent records.

For example, a material consumption record cannot be created before the material lot and production order exist.

---

# 11. Reproducibility

The synthetic data generator uses a fixed seed:

```text
20261022
```

The intention is that the same generation configuration produces a consistent dataset.

This makes debugging and validation easier because a particular generated scenario can be reproduced.

---

# 12. Validation Architecture

Validation is performed separately from data generation.

The general approach is:

```text
Generate baseline data
        ↓
Validate relationships
        ↓
Validate quantities
        ↓
Validate dates
        ↓
Validate identifiers
        ↓
Inject labelled edge cases
        ↓
Verify traceability
```

The baseline dataset is kept valid.

Intentional invalid scenarios are stored separately so they can be tested without breaking the normal operational data.

---

# 13. Edge-Case Design

Five labelled edge cases are maintained separately:

```text
EDGE-001
Defect references nonexistent material lot

EDGE-002
BOM material is not consumed

EDGE-003
Corrective action closes before verification

EDGE-004
Defect quantity exceeds inspected quantity

EDGE-005
Traceability chain is broken
```

These cases represent situations that should be detected by a robust traceability or validation process.

---

# 14. Frontend Architecture

The frontend is a React application created with Vite.

```text
frontend/
│
├── package.json
├── vite.config.js
│
└── src/
    ├── App.jsx
    ├── App.css
    ├── index.css
    └── main.jsx
```

The frontend uses Axios to communicate with the Django API.

The Vite development server proxies `/api` requests to the Django backend.

```text
Browser
   |
   v
React / Vite
   |
   | /api
   v
Django REST API
```

---

# 15. Dashboard

The dashboard provides a high-level view of the generated manufacturing and quality data.

It includes:

- master-data counts
- production-order count
- inspection count
- defect count
- failed quantity
- defect rate
- defect status
- defect severity
- corrective-action status

The defect rate is calculated from the inspection records:

```text
Defect Rate =
Failed Quantity / Inspected Quantity × 100
```

This value is derived from source data rather than generated independently.

---

# 16. Important Design Trade-offs

## Read-only API

The current API is intentionally read-oriented.

The primary purpose of the candidate project is to demonstrate traceability, data relationships, validation, and investigation rather than build a complete production manufacturing execution system.

## Synthetic Data

Synthetic data was chosen because there is no need to expose real supplier or manufacturing information.

## Separate Edge Cases

Invalid scenarios are kept outside the normal operational records.

This means the baseline dataset remains internally consistent while the project can still demonstrate how broken scenarios should be detected.

## Relational Database

A relational database was preferred over a document database because the project depends heavily on explicit relationships, foreign keys, quantities, and reconciliation.
