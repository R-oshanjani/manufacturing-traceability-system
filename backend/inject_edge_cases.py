from datetime import date

from django.db import connection

from manufacturing.models import (
    Defect,
    CorrectiveAction,
    InspectionResult,
    MaterialConsumption,
)


print("Starting edge-case injection...")


# =========================================================
# 1. Defect linked to nonexistent lot
# =========================================================
# The current Defect model does not contain a MaterialLot FK.
# Therefore this case is recorded separately in the ground truth
# table rather than corrupting the production database.

with connection.cursor() as cursor:
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS ground_truth_edge_cases (
            id SERIAL PRIMARY KEY,
            case_code VARCHAR(100) UNIQUE NOT NULL,
            description TEXT NOT NULL,
            entity_type VARCHAR(100) NOT NULL,
            entity_id VARCHAR(100),
            expected_behavior TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )


edge_cases = [
    (
        "EDGE-001",
        "Defect references a nonexistent material lot.",
        "DEFECT",
        "SIMULATED-NONEXISTENT-LOT",
        "Traceability query must detect the broken upstream lot reference.",
    ),
    (
        "EDGE-002",
        "BOM material is not consumed by a production order.",
        "MATERIAL_CONSUMPTION",
        "SIMULATED-MISSING-CONSUMPTION",
        "Material reconciliation must detect the missing consumption.",
    ),
    (
        "EDGE-003",
        "Corrective action closes before verification.",
        "CORRECTIVE_ACTION",
        "SIMULATED-EARLY-CLOSURE",
        "CAPA validation must reject closure without verification.",
    ),
    (
        "EDGE-004",
        "Defect quantity exceeds inspected quantity.",
        "DEFECT",
        "SIMULATED-QUANTITY-OVERFLOW",
        "Defect validation must flag the arithmetic inconsistency.",
    ),
    (
        "EDGE-005",
        "Traceability chain is broken.",
        "TRACEABILITY",
        "SIMULATED-BROKEN-CHAIN",
        "Traceability query must identify the missing upstream relationship.",
    ),
]


for case in edge_cases:

    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO ground_truth_edge_cases
            (
                case_code,
                description,
                entity_type,
                entity_id,
                expected_behavior
            )
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (case_code)
            DO UPDATE SET
                description = EXCLUDED.description,
                entity_type = EXCLUDED.entity_type,
                entity_id = EXCLUDED.entity_id,
                expected_behavior = EXCLUDED.expected_behavior
            """,
            case,
        )


print("Inserted labelled edge cases: 5")
print("Edge cases are stored separately from operational data.")