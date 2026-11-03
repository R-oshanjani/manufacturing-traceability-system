# Data Dictionary

## 1. Purpose

This document explains the main database entities used in the Manufacturing Traceability & Quality System.

The system is built around a relational model because the main requirement is to maintain reliable links between manufacturing, material, supplier, process, inspection, defect, and corrective-action records.

The relationships are important because traceability depends on being able to follow the data in both directions.

---

# 2. Entity Overview

| Entity | Purpose |
|---|---|
| Product | Defines the finished product |
| Material | Defines raw materials/components |
| Supplier | Defines material suppliers |
| BOM | Defines a version of a product's bill of materials |
| BOMComponent | Links materials to a BOM |
| MaterialLot | Represents a received supplier material lot |
| ProductionOrder | Represents a manufacturing order |
| MaterialConsumption | Records material-lot consumption by a production order |
| Machine | Defines manufacturing equipment |
| ProcessStep | Defines a manufacturing operation |
| InspectionPlan | Defines an inspection requirement |
| InspectionResult | Records an actual inspection |
| Defect | Records a quality defect |
| CorrectiveAction | Records the response to a defect |

---

# 3. Product

### Purpose

Represents the finished or manufactured product.

### Main fields

| Field | Type | Required | Description |
|---|---|---:|---|
| `id` | Integer | Yes | Primary key |
| `sku` | String | Yes | Unique product identifier |
| `name` | String | Yes | Product name |
| `description` | Text | No | Product description |
| `unit_of_measure` | String | Yes | Product unit of measure |
| `is_active` | Boolean | Yes | Whether the product is active |
| `created_at` | DateTime | Yes | Creation timestamp |
| `updated_at` | DateTime | Yes | Last update timestamp |

### Constraints

- `sku` is unique.

### Relationships

```text
Product 1 ──── N BOM
Product 1 ──── N ProductionOrder
Product 1 ──── N InspectionPlan
```

---

# 4. Material

### Purpose

Represents a raw material or component used during manufacturing.

### Main fields

| Field | Type | Required | Description |
|---|---|---:|---|
| `id` | Integer | Yes | Primary key |
| `material_code` | String | Yes | Unique material identifier |
| `name` | String | Yes | Material name |
| `description` | Text | No | Material description |
| `unit_of_measure` | String | Yes | Material unit |
| `is_active` | Boolean | Yes | Whether the material is active |
| `created_at` | DateTime | Yes | Creation timestamp |
| `updated_at` | DateTime | Yes | Last update timestamp |

### Constraints

- `material_code` is unique.

### Relationships

```text
Material 1 ──── N BOMComponent
Material 1 ──── N MaterialLot
```

---

# 5. Supplier

### Purpose

Represents a supplier that provides manufacturing materials.

### Main fields

| Field | Type | Required | Description |
|---|---|---:|---|
| `id` | Integer | Yes | Primary key |
| `supplier_code` | String | Yes | Unique supplier identifier |
| `name` | String | Yes | Supplier name |
| `contact_email` | Email | No | Supplier contact email |
| `contact_phone` | String | No | Supplier contact number |
| `address` | Text | No | Supplier address |
| `is_active` | Boolean | Yes | Whether the supplier is active |
| `created_at` | DateTime | Yes | Creation timestamp |
| `updated_at` | DateTime | Yes | Last update timestamp |

### Constraints

- `supplier_code` is unique.

### Relationships

```text
Supplier 1 ──── N MaterialLot
```

---

# 6. BOM

### Purpose

Represents a bill-of-materials version for a product.

A product can have more than one BOM version over time.

### Main fields

| Field | Type | Required | Description |
|---|---|---:|---|
| `id` | Integer | Yes | Primary key |
| `product_id` | Foreign Key | Yes | Product associated with the BOM |
| `version` | Integer | Yes | BOM version |
| `effective_from` | Date | Yes | Date the version becomes effective |
| `effective_to` | Date | No | Date the version stops being effective |
| `is_active` | Boolean | Yes | Whether the BOM is active |
| `created_at` | DateTime | Yes | Creation timestamp |
| `updated_at` | DateTime | Yes | Last update timestamp |

### Constraints

The combination of:

```text
product + version
```

must be unique.

### Relationships

```text
Product 1 ──── N BOM
BOM 1 ──── N BOMComponent
```

---

# 7. BOMComponent

### Purpose

Connects a BOM to the materials required to manufacture the product.

This table represents the many-to-many relationship between BOMs and materials.

### Main fields

| Field | Type | Required | Description |
|---|---|---:|---|
| `id` | Integer | Yes | Primary key |
| `bom_id` | Foreign Key | Yes | BOM |
| `material_id` | Foreign Key | Yes | Required material |
| `required_quantity` | Decimal | Yes | Required material quantity |
| `scrap_percentage` | Decimal | Yes | Expected scrap percentage |
| `sequence` | Integer | Yes | Component sequence |

### Constraints

The combination of:

```text
bom + material
```

must be unique.

### Relationships

```text
BOM 1 ──── N BOMComponent
Material 1 ──── N BOMComponent
```

---

# 8. MaterialLot

### Purpose

Represents a specific batch/lot of material received from a supplier.

This is one of the most important entities for supplier traceability.

### Main fields

| Field | Type | Required | Description |
|---|---|---:|---|
| `id` | Integer | Yes | Primary key |
| `lot_number` | String | Yes | Unique lot identifier |
| `material_id` | Foreign Key | Yes | Material in the lot |
| `supplier_id` | Foreign Key | Yes | Supplier that provided the lot |
| `received_quantity` | Decimal | Yes | Quantity received |
| `received_date` | Date | Yes | Date received |
| `expiry_date` | Date | No | Expiry date if applicable |
| `status` | Enum | Yes | Current lot status |
| `created_at` | DateTime | Yes | Creation timestamp |
| `updated_at` | DateTime | Yes | Last update timestamp |

### Lot status values

```text
AVAILABLE
QUARANTINE
CONSUMED
REJECTED
```

### Relationships

```text
Material 1 ──── N MaterialLot
Supplier 1 ──── N MaterialLot
MaterialLot 1 ──── N MaterialConsumption
```

---

# 9. ProductionOrder

### Purpose

Represents an order to manufacture a product.

### Main fields

| Field | Type | Required | Description |
|---|---|---:|---|
| `id` | Integer | Yes | Primary key |
| `order_number` | String | Yes | Unique production order |
| `product_id` | Foreign Key | Yes | Product being manufactured |
| `bom_id` | Foreign Key | Yes | BOM used |
| `planned_quantity` | Decimal | Yes | Planned production quantity |
| `actual_quantity` | Decimal | Yes | Actual completed quantity |
| `status` | Enum | Yes | Production lifecycle state |
| `planned_start` | Date | Yes | Planned start |
| `planned_end` | Date | Yes | Planned completion |
| `actual_start` | Date | No | Actual start |
| `actual_end` | Date | No | Actual completion |
| `created_at` | DateTime | Yes | Creation timestamp |
| `updated_at` | DateTime | Yes | Last update timestamp |

### Status values

```text
PLANNED
RELEASED
IN_PROGRESS
COMPLETED
CLOSED
CANCELLED
```

### Relationships

```text
Product 1 ──── N ProductionOrder
BOM 1 ──── N ProductionOrder

ProductionOrder 1 ──── N MaterialConsumption
ProductionOrder 1 ──── N InspectionResult
ProductionOrder 1 ──── N Defect
```

---

# 10. MaterialConsumption

### Purpose

Records the actual quantity of a specific material lot consumed by a production order.

This table is the bridge between incoming material and manufacturing execution.

### Main fields

| Field | Type | Required | Description |
|---|---|---:|---|
| `id` | Integer | Yes | Primary key |
| `production_order_id` | Foreign Key | Yes | Production order |
| `material_lot_id` | Foreign Key | Yes | Consumed material lot |
| `consumed_quantity` | Decimal | Yes | Quantity consumed |
| `consumed_at` | DateTime | Yes | Consumption timestamp |
| `created_at` | DateTime | Yes | Record creation timestamp |

### Constraints

The combination of:

```text
production_order + material_lot
```

must be unique.

### Relationships

```text
ProductionOrder 1 ──── N MaterialConsumption
MaterialLot 1 ──── N MaterialConsumption
```

---

# 11. Machine

### Purpose

Represents a manufacturing machine or piece of production equipment.

### Main fields

| Field | Type | Required | Description |
|---|---|---:|---|
| `id` | Integer | Yes | Primary key |
| `machine_code` | String | Yes | Unique machine identifier |
| `name` | String | Yes | Machine name |
| `machine_type` | String | Yes | Machine category |
| `location` | String | No | Physical location |
| `status` | Enum | Yes | Current machine status |
| `installed_date` | Date | No | Installation date |
| `created_at` | DateTime | Yes | Creation timestamp |
| `updated_at` | DateTime | Yes | Last update timestamp |

### Status values

```text
ACTIVE
MAINTENANCE
INACTIVE
```

### Relationships

```text
Machine 1 ──── N ProcessStep
```

---

# 12. ProcessStep

### Purpose

Represents an operation in the manufacturing process.

### Main fields

| Field | Type | Required | Description |
|---|---|---:|---|
| `id` | Integer | Yes | Primary key |
| `process_code` | String | Yes | Unique process identifier |
| `name` | String | Yes | Process name |
| `sequence` | Integer | Yes | Process order |
| `machine_id` | Foreign Key | Yes | Machine used |
| `description` | Text | No | Process description |
| `is_active` | Boolean | Yes | Whether active |
| `created_at` | DateTime | Yes | Creation timestamp |
| `updated_at` | DateTime | Yes | Last update timestamp |

### Relationships

```text
Machine 1 ──── N ProcessStep
ProcessStep 1 ──── N InspectionPlan
ProcessStep 1 ──── N Defect
```

---

# 13. InspectionPlan

### Purpose

Defines an inspection requirement for a product at a particular process step.

### Main fields

| Field | Type | Required | Description |
|---|---|---:|---|
| `id` | Integer | Yes | Primary key |
| `inspection_code` | String | Yes | Unique inspection identifier |
| `name` | String | Yes | Inspection name |
| `product_id` | Foreign Key | Yes | Product being inspected |
| `process_step_id` | Foreign Key | Yes | Process where inspection occurs |
| `inspection_type` | Enum | Yes | Type of inspection |
| `specification` | Text | No | Inspection specification |
| `sampling_percentage` | Decimal | Yes | Sampling percentage |
| `is_active` | Boolean | Yes | Whether active |
| `created_at` | DateTime | Yes | Creation timestamp |
| `updated_at` | DateTime | Yes | Last update timestamp |

### Inspection types

```text
VISUAL
DIMENSIONAL
WEIGHT
FUNCTIONAL
CHEMICAL
```

### Relationships

```text
Product 1 ──── N InspectionPlan
ProcessStep 1 ──── N InspectionPlan
InspectionPlan 1 ──── N InspectionResult
```

---

# 14. InspectionResult

### Purpose

Records an actual inspection performed during production.

### Main fields

| Field | Type | Required | Description |
|---|---|---:|---|
| `id` | Integer | Yes | Primary key |
| `inspection_number` | String | Yes | Unique inspection identifier |
| `inspection_plan_id` | Foreign Key | Yes | Inspection definition |
| `production_order_id` | Foreign Key | Yes | Production order inspected |
| `inspected_quantity` | Decimal | Yes | Quantity inspected |
| `passed_quantity` | Decimal | Yes | Quantity passed |
| `failed_quantity` | Decimal | Yes | Quantity failed |
| `result` | Enum | Yes | Overall result |
| `inspected_at` | DateTime | Yes | Inspection timestamp |
| `notes` | Text | No | Additional notes |
| `created_at` | DateTime | Yes | Creation timestamp |
| `updated_at` | DateTime | Yes | Last update timestamp |

### Result values

```text
PASS
FAIL
PARTIAL
```

### Important validation

The expected quantity relationship is:

```text
inspected_quantity =
passed_quantity + failed_quantity
```

### Relationships

```text
InspectionPlan 1 ──── N InspectionResult
ProductionOrder 1 ──── N InspectionResult
InspectionResult 1 ──── N Defect
```

---

# 15. Defect

### Purpose

Represents a quality defect identified during an inspection.

### Main fields

| Field | Type | Required | Description |
|---|---|---:|---|
| `id` | Integer | Yes | Primary key |
| `defect_number` | String | Yes | Unique defect identifier |
| `inspection_result_id` | Foreign Key | Yes | Inspection that identified the defect |
| `production_order_id` | Foreign Key | Yes | Related production order |
| `process_step_id` | Foreign Key | Yes | Process where defect was identified |
| `defect_type` | String | Yes | Defect category |
| `severity` | Enum | Yes | Defect severity |
| `quantity` | Decimal | Yes | Affected quantity |
| `description` | Text | No | Description |
| `status` | Enum | Yes | Defect lifecycle state |
| `detected_at` | DateTime | Yes | Detection timestamp |
| `created_at` | DateTime | Yes | Creation timestamp |
| `updated_at` | DateTime | Yes | Last update timestamp |

### Severity values

```text
LOW
MEDIUM
HIGH
CRITICAL
```

### Status values

```text
OPEN
CONTAINED
RESOLVED
CLOSED
```

### Important validation

A defect quantity should not exceed the failed quantity of its associated inspection.

### Relationships

```text
InspectionResult 1 ──── N Defect
ProductionOrder 1 ──── N Defect
ProcessStep 1 ──── N Defect
Defect 1 ──── N CorrectiveAction
```

---

# 16. CorrectiveAction

### Purpose

Represents corrective and preventive work associated with a defect.

### Main fields

| Field | Type | Required | Description |
|---|---|---:|---|
| `id` | Integer | Yes | Primary key |
| `capa_number` | String | Yes | Unique CAPA identifier |
| `defect_id` | Foreign Key | Yes | Related defect |
| `title` | String | Yes | CAPA title |
| `description` | Text | No | Description |
| `root_cause` | Text | No | Identified root cause |
| `containment_action` | Text | No | Immediate containment |
| `corrective_action` | Text | No | Corrective action |
| `preventive_action` | Text | No | Preventive action |
| `status` | Enum | Yes | CAPA lifecycle state |
| `assigned_to` | String | No | Person responsible |
| `target_date` | Date | No | Target completion |
| `completed_date` | Date | No | Completion date |
| `verification_date` | Date | No | Verification date |
| `verified_by` | String | No | Person who verified |
| `verification_result` | Text | No | Verification result |
| `created_at` | DateTime | Yes | Creation timestamp |
| `updated_at` | DateTime | Yes | Last update timestamp |

### Status values

```text
OPEN
IN_PROGRESS
PENDING_VERIFICATION
CLOSED
```

### Relationships

```text
Defect 1 ──── N CorrectiveAction
```

---

# 17. Relationship Cardinality

The main relationship cardinalities are:

| Parent | Child | Relationship |
|---|---|---|
| Product | BOM | 1:N |
| Product | ProductionOrder | 1:N |
| Product | InspectionPlan | 1:N |
| Material | BOMComponent | 1:N |
| Material | MaterialLot | 1:N |
| Supplier | MaterialLot | 1:N |
| BOM | BOMComponent | 1:N |
| BOM | ProductionOrder | 1:N |
| ProductionOrder | MaterialConsumption | 1:N |
| MaterialLot | MaterialConsumption | 1:N |
| Machine | ProcessStep | 1:N |
| ProcessStep | InspectionPlan | 1:N |
| InspectionPlan | InspectionResult | 1:N |
| ProductionOrder | InspectionResult | 1:N |
| InspectionResult | Defect | 1:N |
| ProcessStep | Defect | 1:N |
| ProductionOrder | Defect | 1:N |
| Defect | CorrectiveAction | 1:N |

---

# 18. Foreign-Key Protection

Important manufacturing records use protected relationships where deleting a parent record could destroy historical traceability.

For example:

```text
ProductionOrder
      ↓
MaterialConsumption
```

A production order should not be casually deleted while its material-consumption history still exists.

The same principle applies to:

- material lots
- suppliers
- inspections
- defects
- corrective actions
- process steps
- BOMs

The goal is to preserve historical relationships rather than silently breaking the traceability chain.

---

# 19. Identifier Conventions

The project uses readable identifiers for operational records.

Examples:

| Entity | Example |
|---|---|
| Product | `SKU-000001` |
| Material Lot | `LOT-SUP-0001-2026-000001` |
| Production Order | `WO-2026-000001` |
| Inspection | `INSP-WO-2026-000001-001` |
| Defect | `DEF-2026-000001` |
| CAPA | `CAPA-2026-000001` |

Readable identifiers make API testing and traceability investigations easier.

---

# 20. Traceability Dependencies

The complete upstream/downstream chain can be represented as:

```text
Supplier
   ↓
MaterialLot
   ↓
MaterialConsumption
   ↓
ProductionOrder
   ↓
InspectionResult
   ↓
Defect
   ↓
CorrectiveAction
```

Process context is connected through:

```text
ProductionOrder
   ↓
InspectionResult
   ↓
InspectionPlan
   ↓
ProcessStep
   ↓
Machine
```

Material requirements are connected through:

```text
ProductionOrder
   ↓
BOM
   ↓
BOMComponent
   ↓
Material
```

These three paths together provide the main traceability structure of the application.

---

# 21. Data Integrity Principles

The database and validation process follow several basic principles:

### 1. Every record has a primary key

This provides a stable database identity.

### 2. Relationships use foreign keys

Relationships should not depend only on manually entered text.

### 3. Quantities are stored as decimal values

Manufacturing quantities can require precision, so decimal fields are used instead of floating-point fields.

### 4. Lifecycle states use defined choices

Status fields use controlled values rather than arbitrary strings where appropriate.

### 5. Historical relationships are protected

Important parent records should not be deleted if doing so would break traceability.

### 6. Derived metrics use source records

For example, defect rate is calculated from inspection quantities rather than generated independently.

---

# 22. Data Flow Summary

The overall data flow is:

```text
Supplier
   │
   │ supplies
   ▼
Material Lot
   │
   │ consumed through
   ▼
Material Consumption
   │
   │ belongs to
   ▼
Production Order
   │
   ├──────────────► Product / BOM
   │
   │
   ▼
Inspection Result
   │
   ├──────────────► Process Step
   │                       │
   │                       ▼
   │                    Machine
   │
   ▼
Defect
   │
   ▼
Corrective Action
```

This structure is the foundation of the application's traceability functionality.