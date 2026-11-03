# AI Prompt History

## 1. Purpose

This document records the use of AI assistance during development of the Manufacturing Traceability & Quality System.

YottaFlex AI permits the use of LLM and AI coding tools but requires transparent disclosure of AI usage, prompt history, and the developer's own review and validation.

AI assistance was used during architecture discussions, implementation, debugging, validation planning, documentation, and development workflow decisions.

---

# 2. AI Tool Used

Primary AI tool used:

- ChatGPT

AI assistance was used as a development and reasoning aid.

The final implementation was reviewed, executed, tested, and validated by the developer.

---

# 3. Prompt History

The following sections summarize the prompts and development requests used during the project.

## Prompt 1 — Project Understanding

**Purpose:** Understand the candidate assignment and identify the required manufacturing traceability workflow.

**Prompt/request:**

> Trace defects from inspection to production lot, machine, supplier batch and corrective action. Build a working end-to-end manufacturing traceability solution with multiple related entities, conditional rules, exception paths and measurable outputs.

**AI assistance:**

The AI helped break the problem into manufacturing master data, transactions, quality events, traceability relationships, validation rules, synthetic data generation, and exception scenarios.

**Developer review/action:**

The proposed workflow was reviewed and adapted to the project requirements before implementation.

---

## Prompt 2 — Technology Stack

**Purpose:** Select the application architecture.

**Prompt/request:**

> Build the manufacturing traceability project using Django, Django REST Framework, PostgreSQL, React and Vite.

**AI assistance:**

The AI helped define the separation between:

- React frontend
- Django REST API
- Django ORM
- PostgreSQL database

**Developer review/action:**

The stack was implemented locally and verified by running both the Django backend and React frontend.

---

## Prompt 3 — Database Modeling

**Purpose:** Design the relational manufacturing data model.

**Prompt/request:**

> Define the database models required to trace products, BOMs, suppliers, material lots, production orders, material consumption, machines, process steps, inspections, defects and corrective actions.

**AI assistance:**

The AI helped identify entities, relationships, foreign keys, lifecycle fields, quantities, status values and identifier conventions.

**Developer review/action:**

The models were implemented in Django and migrations were generated and applied against PostgreSQL.

---

## Prompt 4 — Manufacturing Master Data

**Purpose:** Establish the master-data layer.

**Prompt/request:**

> Create Product, Supplier, Material, BOM and BOMComponent models with appropriate relationships and constraints.

**AI assistance:**

The AI proposed Django model structures and relationship constraints.

**Developer review/action:**

The models were implemented and the resulting database structure was checked through Django migrations and validation.

---

## Prompt 5 — Material Lot and Supplier Traceability

**Purpose:** Connect incoming supplier material to production.

**Prompt/request:**

> Add MaterialLot and supplier relationships and track material consumption into production orders.

**AI assistance:**

The AI helped design:

- MaterialLot
- Supplier relationship
- MaterialConsumption
- production-order relationship
- quantity tracking

**Developer review/action:**

Material consumption generation and reconciliation were implemented and validated.

---

## Prompt 6 — Production and Process Modeling

**Purpose:** Represent manufacturing execution.

**Prompt/request:**

> Add ProductionOrder, Machine and ProcessStep entities and connect production processes to machines.

**AI assistance:**

The AI helped define production-order states, process sequences and machine relationships.

**Developer review/action:**

The models and generated data were tested in PostgreSQL and through the Django application.

---

## Prompt 7 — Inspection and Quality Modeling

**Purpose:** Connect production to quality inspection.

**Prompt/request:**

> Add inspection plans, inspection results and defects linked to production orders and process steps.

**AI assistance:**

The AI helped define:

- InspectionPlan
- InspectionResult
- Defect
- inspection quantities
- pass/fail quantities
- defect severity
- defect status

**Developer review/action:**

20,000 inspection results and 20,000 defects were generated and validated.

---

## Prompt 8 — Corrective Actions

**Purpose:** Connect defects to corrective and preventive actions.

**Prompt/request:**

> Create a CorrectiveAction/CAPA model linked to defects with root cause, containment, corrective action, preventive action and verification fields.

**AI assistance:**

The AI helped define the CAPA lifecycle and fields required to represent investigation and verification.

**Developer review/action:**

The model and CAPA generation approach were reviewed against the requirement that closure should require appropriate verification.

---

## Prompt 9 — Synthetic Dataset

**Purpose:** Generate a sufficiently large reproducible manufacturing dataset.

**Prompt/request:**

> Generate synthetic manufacturing data with 200 SKUs, 50 suppliers, 2,000 material lots, 5,000 production orders, 20,000 inspections and 20,000 defects using a fixed seed.

**AI assistance:**

The AI helped design parameterized generation logic and relationships between generated records.

**Developer review/action:**

The dataset was generated using seed `20261022`.

The generated baseline dataset was checked for relationship and quantity consistency.

---

## Prompt 10 — Data Integrity Validation

**Purpose:** Validate the generated dataset.

**Prompt/request:**

> Validate primary keys, foreign keys, quantity reconciliation, production dates, material consumption, inspection quantities and defect quantities.

**AI assistance:**

The AI helped identify validation rules and edge cases.

**Developer review/action:**

Validation scripts were executed against the generated PostgreSQL dataset.

Examples of validated conditions included:

- duplicate identifiers
- material-lot over-consumption
- material-consumption mismatches
- inspection quantity mismatches
- invalid inspection quantities
- defect quantity exceeding failed quantity
- missing related records

---

## Prompt 11 — Edge Cases

**Purpose:** Demonstrate failure and exception scenarios.

**Prompt/request:**

> Create labelled edge cases for broken traceability, unconsumed BOM material, CAPA closing before verification, defect quantity exceeding inspection quantity, and nonexistent material-lot references.

**AI assistance:**

The AI helped structure the edge-case scenarios and separate intentional invalid scenarios from the valid operational dataset.

**Developer review/action:**

Five labelled edge cases were inserted into a separate `ground_truth_edge_cases` PostgreSQL table.

---

## Prompt 12 — REST API

**Purpose:** Expose the manufacturing data through Django REST Framework.

**Prompt/request:**

> Create serializers and read-only API viewsets for the manufacturing entities and add a traceability endpoint.

**AI assistance:**

The AI helped design serializers, viewsets, optimized querysets, and traceability response structures.

**Developer review/action:**

The API was implemented and tested locally.

---

## Prompt 13 — Production Order Traceability

**Purpose:** Build the central traceability workflow.

**Prompt/request:**

> Create an endpoint that accepts a production order number and returns product, BOM, consumed material lots, suppliers, inspections, process steps, machines, defects and corrective actions.

**AI assistance:**

The AI helped design the nested traceability response and related ORM prefetch paths.

**Developer review/action:**

The endpoint was implemented and tested through the React application.

---

## Prompt 14 — Material Lot Traceability

**Purpose:** Support downstream traceability starting from a supplier material lot.

**Prompt/request:**

> Create a material-lot traceability endpoint that shows which production orders consumed a lot and the related inspection, defect and corrective-action records.

**AI assistance:**

The AI helped design the downstream relationship traversal.

**Developer review/action:**

The endpoint was added to the Django API and connected to the frontend.

---

## Prompt 15 — Dashboard

**Purpose:** Create a quality and production summary.

**Prompt/request:**

> Create a dashboard API showing products, suppliers, material lots, production orders, inspections, defects, defect rates and corrective-action status.

**AI assistance:**

The AI helped define aggregate queries and the response structure.

**Developer review/action:**

The dashboard endpoint was implemented and displayed through the React frontend.

Derived defect-rate values were calculated from inspection quantities rather than independently randomized.

---

## Prompt 16 — React Frontend

**Purpose:** Build a usable interface for the backend APIs.

**Prompt/request:**

> Create a React/Vite frontend for the manufacturing traceability system with dashboard metrics and production-order/material-lot traceability views.

**AI assistance:**

The AI helped structure React components, API calls, rendering logic and responsive styling.

**Developer review/action:**

The frontend was run locally through Vite and connected to the Django API.

---

## Prompt 17 — Frontend Debugging

**Purpose:** Resolve a rendering problem in the traceability interface.

**Prompt/request:**

> The React traceability page is blank because nested objects are being rendered directly. Fix the rendering logic.

**AI assistance:**

The AI identified that JavaScript objects such as machine/process-step objects cannot be rendered directly as React children and proposed a display helper.

**Developer review/action:**

The rendering logic was changed to convert nested objects into displayable values.

The frontend was rerun and verified successfully.

---

## Prompt 18 — Git Repository Preparation

**Purpose:** Prepare the project for public GitHub submission.

**Prompt/request:**

> Prepare the manufacturing traceability project for a public GitHub submission according to the YottaFlex candidate project requirements.

**AI assistance:**

The AI helped identify:

- `.gitignore`
- README
- documentation
- prompt history
- validation evidence
- repository structure
- Git commits
- public repository requirements

**Developer review/action:**

The Git repository was initialized at the project root and unwanted environment files were excluded.

---

# 4. AI-Assisted Development Areas

AI assistance was primarily used for:

- architecture discussion
- database design
- Django implementation guidance
- API design
- debugging
- validation design
- synthetic data generation logic
- frontend implementation guidance
- documentation
- Git workflow guidance

---

# 5. Developer Responsibilities

The developer remained responsible for:

- choosing the final technology stack
- creating and maintaining the project environment
- running commands
- configuring PostgreSQL
- applying Django migrations
- generating the dataset
- running validation scripts
- testing the API
- running the frontend
- reviewing generated implementation
- fixing development issues
- verifying traceability behavior
- preparing the final repository

AI suggestions were not treated as automatically correct.

Implementation decisions were reviewed against the project requirements and tested locally.

---

# 6. What Was Personally Reviewed and Validated

The following areas were personally reviewed and/or executed during development:

- Django project startup
- PostgreSQL database connectivity
- Django migrations
- database record generation
- material-consumption reconciliation
- inspection-result validation
- defect validation
- edge-case insertion
- REST API implementation
- traceability API behavior
- dashboard API behavior
- React frontend startup
- frontend/API integration
- Git repository structure
- `.gitignore` behavior

---

# 7. AI Limitations and Developer Verification

AI-generated suggestions can contain incorrect assumptions or implementation errors.

Examples encountered during development included:

- data-generation logic requiring correction
- duplicate inspection-plan generation requiring correction
- dependency/environment issues
- frontend rendering of nested objects requiring correction
- performance considerations for large related querysets

These issues were identified during implementation and testing rather than being accepted blindly.

---

# 8. Prompt History Limitation

This document is a reconstructed record of the AI-assisted development process based on the available project conversation and development history.

Where the AI interface did not provide an exportable transcript of every historical interaction, the prompts have been summarized rather than falsely claiming to reproduce exact wording.

The purpose is to provide transparent disclosure of how AI assistance was used while avoiding fabricated prompt records.

---

# 9. Final Disclosure

AI tools were used substantially during the development process.

The project is submitted with the understanding that the developer must be able to explain:

- the architecture
- the database relationships
- the traceability logic
- the validation rules
- the implementation choices
- the dependencies
- the limitations
- the reasons behind important design decisions

The developer accepts responsibility for the final implementation and its verification.