# Validation and Verification

## 1. Purpose

The purpose of validation was to make sure that the generated manufacturing dataset and the traceability relationships are internally consistent.

The project was not validated only by checking whether the application starts.

The database was checked for:

- duplicate identifiers
- missing relationships
- incorrect quantities
- invalid dates
- material over-consumption
- inspection inconsistencies
- defect inconsistencies
- broken traceability scenarios
- reproducibility considerations

The validation process was performed against the PostgreSQL database used by the application.

---

# 2. Dataset Size

The generated baseline dataset contains:

| Entity | Records |
|---|---:|
| Products | 200 |
| Suppliers | 50 |
| Materials | 200 |
| BOMs | 200 |
| BOM Components | 909 |
| Material Lots | 2,000 |
| Production Orders | 5,000 |
| Material Consumption | 24,265 |
| Machines | 10 |
| Process Steps | 12 |
| Inspection Plans | 800 |
| Inspection Results | 20,000 |
| Defects | 20,000 |

The dataset was generated using the fixed seed:

```text
20261022
```

---

# 3. Master Data Validation

The following uniqueness checks were performed.

| Check | Expected | Result |
|---|---:|---:|
| Duplicate product SKUs | 0 | 0 |
| Duplicate supplier codes | 0 | 0 |
| Duplicate material codes | 0 | 0 |
| Duplicate production-order numbers | 0 | 0 |
| Duplicate material-lot numbers | 0 | 0 |
| Duplicate inspection-plan codes | 0 | 0 |
| Duplicate inspection numbers | 0 | 0 |
| Duplicate defect numbers | 0 | 0 |

All checked identifiers were unique.

---

# 4. Material Consumption Validation

Material consumption is one of the most important parts of the traceability chain.

The validation checked whether the generated consumption records matched the expected material demand for each production order.

### Result

```text
Order-level material consumption requirement mismatches: 0
```

This means no production order was found with an unexpected total material consumption when compared with its generated requirement.

---

# 5. Material Lot Validation

Material lots were checked to make sure that the consumed quantity did not exceed the received quantity.

### Result

```text
Lot over-consumption: 0
```

This means the generated baseline data does not contain a material lot where:

```text
consumed quantity > received quantity
```

---

# 6. Production Order Date Validation

Production orders were checked for invalid planned dates.

The main condition checked was that the planned end date should not be before the planned start date.

### Result

```text
Invalid planned/actual production dates: 0
```

The generated production orders therefore passed the date-ordering validation performed during dataset verification.

---

# 7. BOM Validation

BOMs and BOM components were checked for valid relationships.

The dataset contains:

```text
200 BOMs
909 BOM components
```

Each BOM component is linked to:

- one BOM
- one material

The model also prevents duplicate material entries within the same BOM through a uniqueness constraint on:

```text
bom + material
```

---

# 8. Inspection Plan Validation

The generated inspection-plan dataset contains:

```text
800 inspection plans
```

The validation checked:

- duplicate inspection codes
- missing products
- missing process steps
- expected plan distribution across products

### Results

```text
Inspection plans: 800
Duplicate inspection codes: 0
Plans without product: 0
Plans without process step: 0
```

The dataset contains four inspection plans per product.

---

# 9. Inspection Result Validation

The generated dataset contains:

```text
20,000 inspection results
```

The validation checked:

- duplicate inspection numbers
- missing inspection plans
- missing production orders
- quantity reconciliation
- invalid quantity values

### Results

```text
Inspection results: 20,000
Duplicate inspection numbers: 0
Quantity mismatches: 0
Missing inspection plan: 0
Missing production order: 0
Invalid inspected/failed/passed quantities: 0
```

The main quantity relationship checked was:

```text
inspected_quantity =
passed_quantity + failed_quantity
```

---

# 10. Defect Validation

The generated dataset contains:

```text
20,000 defects
```

The validation checked:

- duplicate defect numbers
- missing inspection results
- missing production orders
- missing process steps
- invalid defect quantities
- defect quantities exceeding failed quantities

### Results

```text
Defects: 20,000
Duplicate defect numbers: 0
Missing inspection result: 0
Missing production order: 0
Missing process step: 0
Invalid defect quantities: 0
Defect quantity exceeding failed quantity: 0
```

This is important because a defect should have a valid inspection context and should not report more affected quantity than the inspection reported as failed.

---

# 11. Foreign-Key Integrity

The Django models use foreign keys for the main relationships.

Examples include:

```text
ProductionOrder → Product
ProductionOrder → BOM

BOMComponent → BOM
BOMComponent → Material

MaterialLot → Material
MaterialLot → Supplier

MaterialConsumption → ProductionOrder
MaterialConsumption → MaterialLot

InspectionResult → InspectionPlan
InspectionResult → ProductionOrder

Defect → InspectionResult
Defect → ProductionOrder
Defect → ProcessStep

CorrectiveAction → Defect
```

The database therefore maintains explicit relationships rather than relying only on text identifiers.

The baseline dataset was generated through these relationships and passed the relationship checks described above.

---

# 12. Traceability Validation

The central functional requirement is the ability to follow a defect through the manufacturing chain.

The expected relationship is:

```text
Defect
   ↓
Inspection Result
   ↓
Production Order
   ↓
Material Consumption
   ↓
Material Lot
   ↓
Supplier
```

Process context is available through:

```text
Defect
   ↓
Process Step
   ↓
Machine
```

Corrective-action context is available through:

```text
Defect
   ↓
Corrective Action
```

The production-order traceability API combines these related records into one response.

The material-lot traceability API provides the reverse direction:

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

# 13. Dashboard Validation

The dashboard does not generate independent quality metrics.

For example, the defect rate is calculated from inspection data.

```text
Defect Rate =
Failed Quantity / Inspected Quantity × 100
```

This means the dashboard metric is derived from the underlying inspection records.

The dashboard also reports:

- production-order count
- inspection count
- defect count
- inspected quantity
- failed quantity
- defect rate
- defect status
- defect severity
- corrective-action status

---

# 14. Edge Cases

The project includes five intentionally labelled edge cases.

These are kept separately from the valid operational dataset.

| ID | Scenario |
|---|---|
| EDGE-001 | Defect references a nonexistent material lot |
| EDGE-002 | BOM material is not consumed |
| EDGE-003 | Corrective action closes before verification |
| EDGE-004 | Defect quantity exceeds inspected quantity |
| EDGE-005 | Traceability chain is broken |

These scenarios are intentionally invalid.

They are not mixed into the normal production records because doing so would corrupt the baseline foreign-key-constrained dataset.

The separate edge-case table allows these situations to be demonstrated and tested without destroying the validity of the normal dataset.

---

# 15. Corrective Action Verification Rule

A corrective action has a lifecycle that includes:

```text
OPEN
   ↓
IN_PROGRESS
   ↓
PENDING_VERIFICATION
   ↓
CLOSED
```

The intended business rule is that closure should not occur before verification.

The edge-case dataset includes:

```text
EDGE-003
Corrective action closes before verification
```

This represents a lifecycle violation that a production implementation should reject or flag.

---

# 16. Reproducibility

The data generator uses a fixed seed:

```text
20261022
```

The purpose of the fixed seed is to make the synthetic dataset reproducible.

The intended reproducibility check is:

```text
Run generator with seed 20261022
        ↓
Record row counts/checksums
        ↓
Regenerate with seed 20261022
        ↓
Compare results
```

This allows differences in generated data to be identified instead of relying on random datasets that change every time.

---

# 17. Validation Scripts

The repository contains validation scripts used during development.

Examples include:

```text
backend/validate_inspection_results.py
backend/validate_defects.py
```

Additional validation was also performed through Django/PostgreSQL queries during development.

The scripts and database checks were used to verify the generated dataset before building the final traceability workflow.

---

# 18. Application Verification

The application itself was also verified locally.

### Backend

The Django development server was successfully started using:

```text
python manage.py runserver
```

The backend was available at:

```text
http://127.0.0.1:8000/
```

### Frontend

The React/Vite development server was successfully started and connected to the Django API.

The frontend uses:

```text
http://localhost:5173/
```

### API integration

The frontend communicates with the backend through the `/api` routes configured in the Vite development proxy.

---

# 19. Frontend Traceability Verification

The traceability interface was tested with nested API responses containing:

- production-order information
- BOM information
- material lots
- supplier information
- inspection results
- process steps
- machines
- defects
- corrective actions

During development, a rendering issue occurred when nested JavaScript objects were passed directly to React.

The issue was corrected by converting nested objects into displayable values before rendering.

The traceability interface was then verified successfully.

---

# 20. Performance Considerations

The dataset contains thousands of related records, so loading relationships individually can create unnecessary database queries.

The Django backend uses:

```python
select_related()
```

and:

```python
prefetch_related()
```

where appropriate for traceability queries.

This is particularly important for:

- material consumption
- material lots
- suppliers
- inspection results
- defects
- corrective actions

The project does not claim to be production-scale optimized, but the main high-volume relationships were considered during implementation.

---

# 21. What Was Not Claimed

The validation does not claim that the system is a complete production MES/QMS.

The following areas were outside the scope of this candidate implementation:

- real manufacturing equipment integration
- real-time production events
- production authentication and authorization
- enterprise audit logging
- distributed deployment
- high-availability architecture
- automated CI/CD
- large-scale performance benchmarking

The validation results therefore describe the behavior and consistency of this candidate implementation rather than a production manufacturing deployment.

---

# 22. Validation Summary

The baseline dataset passed the main validation checks performed during development.

Key results:

```text
Products:                         200
Suppliers:                         50
Materials:                        200
Material Lots:                  2,000
Production Orders:              5,000
Material Consumption:          24,265
Inspection Plans:                800
Inspection Results:           20,000
Defects:                      20,000

Material consumption mismatches:   0
Lot over-consumption:              0
Duplicate identifiers:             0
Inspection quantity mismatches:    0
Invalid inspection quantities:     0
Invalid defect quantities:         0
Defects exceeding failed qty:      0
```

The five intentional edge cases are maintained separately so that invalid scenarios can be demonstrated without corrupting the valid baseline dataset.

---

# 23. Conclusion

The validation approach focused on the actual risks of this project:

1. Can the records be related correctly?
2. Can material consumption be reconciled?
3. Can inspection quantities be trusted?
4. Can defects be traced to their inspection and production context?
5. Can defects be connected to process steps and machines?
6. Can supplier material be traced into production?
7. Can corrective actions be connected back to defects?
8. Can intentionally broken scenarios be identified separately?

The baseline dataset passed the implemented validation checks, and the application was verified locally through the Django API and React frontend.