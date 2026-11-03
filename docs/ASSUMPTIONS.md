# Assumptions and Scope

## 1. Purpose

The assignment describes the goal and expected traceability workflow, but it does not define every manufacturing rule or database field.

Where a specific implementation detail was not provided, reasonable assumptions were made to create a complete working system.

This document records those assumptions so the implementation can be understood and reviewed fairly.

---

# 2. Application Scope

The system is treated as a manufacturing traceability and quality investigation system.

The main workflow is:

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

The project focuses on demonstrating this traceability chain rather than implementing a complete Manufacturing Execution System.

---

# 3. Synthetic Data

No real manufacturing, supplier, employee, or customer data is used.

The dataset is synthetic.

This was chosen because:

- the project needs enough records to demonstrate meaningful relationships;
- real industrial data may contain confidential information;
- synthetic data makes the project reproducible;
- edge cases can be deliberately created and tested.

The generator uses a fixed seed:

```text
20261022
```

---

# 4. Dataset Size

The target dataset was designed around the following volumes:

| Entity | Target |
|---|---:|
| Products | 200 |
| Suppliers | 50 |
| Material Lots | 2,000 |
| Production Orders | 5,000 |
| Inspections | 20,000 |
| Defects | 20,000 |

Additional supporting records are generated where required to maintain the relationships between these entities.

The actual generated counts should be treated as the source of truth when inspecting the database.

---

# 5. Product and SKU Assumption

Each product has a unique SKU.

The project uses readable synthetic identifiers such as:

```text
SKU-000001
SKU-000002
SKU-000003
```

The SKU is treated as the business identifier while Django's database `id` remains the primary database key.

---

# 6. BOM Assumptions

A product can have multiple BOM versions.

Each BOM has:

- a product;
- a version;
- an effective start date;
- an optional effective end date;
- an active flag.

A BOM contains one or more materials through `BOMComponent`.

The same material cannot appear twice in the same BOM.

The BOM version is associated with the production order so that the order retains the BOM context used for manufacturing.

---

# 7. Material Consumption Assumption

Material consumption is represented explicitly rather than being inferred from the BOM.

This distinction is important.

The BOM answers:

> What material should be required?

Material consumption answers:

> What material lot was actually used?

Therefore:

```text
BOM
   ↓
Expected material requirement

MaterialConsumption
   ↓
Actual material-lot usage
```

This allows the system to identify situations where the expected and actual material usage do not match.

---

# 8. Material Lot Assumption

A material lot represents a specific quantity of a particular material received from one supplier.

A lot can be consumed by multiple production orders.

The system therefore uses `MaterialConsumption` as a bridge between material lots and production orders.

This creates a many-to-many relationship:

```text
MaterialLot
     ↕
MaterialConsumption
     ↕
ProductionOrder
```

---

# 9. Supplier Traceability Assumption

Each material lot is associated with one supplier.

Therefore, supplier traceability follows:

```text
Supplier
   ↓
MaterialLot
   ↓
MaterialConsumption
   ↓
ProductionOrder
```

This makes it possible to investigate which production orders may have been affected by a supplier material lot.

---

# 10. Production Order Assumptions

A production order represents the manufacturing of one product against one BOM version.

The main lifecycle is:

```text
PLANNED
   ↓
RELEASED
   ↓
IN_PROGRESS
   ↓
COMPLETED
   ↓
CLOSED
```

`CANCELLED` is treated as an alternative terminal state.

The implementation does not attempt to enforce every possible real-world manufacturing transition.

---

# 11. Process Step Assumptions

A production process is represented using ordered process steps.

Each process step has:

- a unique process code;
- a sequence number;
- a machine;
- a name;
- an active status.

A process step can be associated with inspection plans and defects.

This provides manufacturing context when investigating a quality problem.

---

# 12. Machine Assumptions

Each process step is associated with one machine.

A machine can be used by multiple process steps.

The machine model contains a basic lifecycle:

```text
ACTIVE
MAINTENANCE
INACTIVE
```

Real machine telemetry, sensor data, downtime history, and IoT integration are outside the scope of this project.

---

# 13. Inspection Assumptions

Inspection plans define what should be inspected.

Inspection results record what actually happened.

An inspection result belongs to:

- one inspection plan;
- one production order.

The inspection result records:

```text
Inspected Quantity
Passed Quantity
Failed Quantity
Result
Inspection Time
```

The main quantity assumption is:

```text
Inspected Quantity =
Passed Quantity + Failed Quantity
```

This relationship is validated in the generated dataset.

---

# 14. Defect Assumptions

A defect is associated with an inspection result, production order, and process step.

The defect quantity represents the quantity affected by that defect.

The baseline dataset assumes:

```text
Defect Quantity <= Failed Quantity
```

This is treated as a validation rule for the generated baseline data.

The system supports four severity levels:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

---

# 15. Defect Lifecycle Assumption

Defects have the following available states:

```text
OPEN
CONTAINED
RESOLVED
CLOSED
```

These states represent a simplified quality workflow.

The project does not attempt to model every possible quality-management workflow used in industry.

---

# 16. Corrective Action Assumptions

A defect can have one or more corrective actions.

A corrective action contains:

- root cause;
- containment action;
- corrective action;
- preventive action;
- owner;
- target date;
- completion date;
- verification information.

The intended lifecycle is:

```text
OPEN
   ↓
IN_PROGRESS
   ↓
PENDING_VERIFICATION
   ↓
CLOSED
```

A corrective action should not be considered properly closed before verification.

This rule is represented by one of the intentional edge cases.

---

# 17. Edge Case Assumptions

The project intentionally includes five abnormal scenarios:

### EDGE-001 — Missing Material Lot

A defect references a material lot that does not exist.

This represents a broken upstream traceability relationship.

### EDGE-002 — Unconsumed BOM Material

A BOM requires a material that does not appear in the actual material-consumption records.

This represents a mismatch between planned material requirements and actual usage.

### EDGE-003 — CAPA Closed Before Verification

A corrective action is marked closed before the verification step has been completed.

This represents an invalid lifecycle transition.

### EDGE-004 — Defect Quantity Exceeds Inspection Quantity

A defect quantity is greater than the quantity inspected.

This represents an arithmetic/data-quality inconsistency.

### EDGE-005 — Broken Traceability Chain

A required relationship in the traceability path is missing.

This represents the type of issue the system is designed to help identify.

---

# 18. Why Edge Cases Are Stored Separately

The five edge cases are intentionally invalid.

They are stored separately from the baseline operational records.

This avoids deliberately corrupting the normal foreign-key-constrained dataset.

The separation also makes it clear which records represent valid manufacturing data and which records represent test scenarios.

---

# 19. Identifier Assumptions

Readable identifiers are used to make the system easier to investigate.

Examples include:

```text
SKU-000001
LOT-SUP-0001-2026-000001
WO-2026-000001
INSP-WO-2026-000001-001
DEF-2026-000001
CAPA-2026-000001
```

The exact generated identifier format may vary slightly depending on the generator implementation.

The database primary key remains the authoritative internal identifier.

---

# 20. Dates and Time

Synthetic dates are used for the manufacturing records.

The project assumes that:

- planned dates represent intended production timing;
- actual dates represent observed production timing;
- inspection timestamps represent when inspection occurred;
- material receipt dates represent when material entered the facility;
- corrective-action dates represent the investigation lifecycle.

The project does not attempt to model multiple plant time zones.

---

# 21. Quantities

Manufacturing quantities use decimal fields instead of floating-point values.

This is intentional because manufacturing quantities may require fractional values.

Examples include:

- material quantities;
- planned production quantities;
- actual production quantities;
- inspected quantities;
- failed quantities;
- defect quantities.

The generated data uses consistent units within each material/product context.

---

# 22. Defect Rate

The dashboard defect rate is calculated from inspection data.

The formula is:

```text
Defect Rate =
Failed Quantity / Inspected Quantity × 100
```

The value is therefore derived from source records.

It is not stored as a randomly generated independent value.

This prevents the dashboard from reporting a metric that does not match the underlying inspection records.

---

# 23. Data Generation Assumption

The data generator creates records in dependency order.

The general sequence is:

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

This reduces the chance of generating child records before their required parent records exist.

---

# 24. Derived Data

Derived values should be calculated from source records where possible.

Examples:

```text
Defect Rate
Failed Quantity
Production quality summaries
Material consumption reconciliation
```

The project avoids independently randomizing derived metrics.

This makes the generated dataset more internally consistent.

---

# 25. Public Repository Assumption

The project is intended to be published as a public GitHub repository for evaluation.

The repository should therefore contain:

- source code;
- database migrations;
- data-generation code;
- validation scripts;
- documentation;
- setup instructions;
- AI prompt history.

Secrets, passwords, API keys, private credentials, and real sensitive data should not be committed.

---

# 26. Authentication Scope

Authentication and role-based authorization are not implemented in the current candidate version.

The assignment focuses on the manufacturing traceability workflow.

A production implementation would normally introduce authentication and permissions for roles such as:

- plant operator;
- quality engineer;
- maintenance engineer;
- production planner;
- administrator.

---

# 27. Deployment Assumption

The application is designed and verified as a local development project.

The expected local setup is:

```text
React/Vite
     ↓
Django REST API
     ↓
PostgreSQL
```

Production deployment, cloud infrastructure, load balancing, monitoring, and high availability are outside the current scope.

---

# 28. Real-Time Data Assumption

The system does not receive real-time machine or production data.

Machines and process steps are represented as structured database records.

A future production implementation could connect these records to:

- PLC/SCADA systems;
- machine sensors;
- MES systems;
- event streaming platforms;
- IoT gateways.

These integrations are intentionally not included in the candidate implementation.

---

# 29. API Assumptions

The current API is primarily read-oriented.

The reason is that the candidate project is intended to demonstrate:

- relational data modeling;
- traceability;
- quality investigation;
- validation;
- reporting.

A production system would likely include authenticated create/update workflows with audit history.

---

# 30. Known Limitations

The following limitations are accepted in this version:

- no authentication;
- no role-based authorization;
- no real manufacturing data;
- no real machine integration;
- no real-time event processing;
- no enterprise audit trail;
- no production deployment;
- limited write workflows;
- no advanced analytics;
- no automated notification workflow.

These limitations are documented intentionally rather than hidden.

---

# 31. Future Improvements

If the project were extended beyond the candidate submission, the next improvements would be:

1. Add authentication and role-based permissions.
2. Add complete audit/event history.
3. Implement strict lifecycle transition validation.
4. Add automated validation for the five edge cases.
5. Add richer CAPA workflow management.
6. Add supplier quality metrics.
7. Add process and machine performance analytics.
8. Add real-time manufacturing events.
9. Add automated alerts for critical defects.
10. Add automated test coverage and CI.
11. Add production deployment configuration.
12. Add stronger database constraints for business rules that can be enforced at the database level.

---

# 32. Final Scope Statement

The project intentionally focuses on one core problem:

> Maintain a reliable chain from incoming supplier material through manufacturing and inspection to defects and corrective actions.

The implementation is therefore designed to demonstrate the traceability logic clearly rather than attempting to reproduce every feature of a commercial MES or QMS.

Where the assignment did not specify an exact business rule, the assumption was kept simple, documented, and testable.