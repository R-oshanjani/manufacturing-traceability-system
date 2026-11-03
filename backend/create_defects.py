from decimal import Decimal
from manufacturing.models import (
    InspectionResult,
    Defect,
)


inspection_results = list(
    InspectionResult.objects
    .select_related(
        "production_order",
        "inspection_plan",
        "inspection_plan__process_step",
    )
    .filter(
        failed_quantity__gt=0
    )
    .order_by("id")
)


defects = []

defect_types = [
    "DIMENSION_OUT_OF_SPEC",
    "SURFACE_DEFECT",
    "WEIGHT_VARIATION",
    "FUNCTIONAL_FAILURE",
    "MATERIAL_DEFECT",
]

severities = [
    "LOW",
    "MEDIUM",
    "HIGH",
    "CRITICAL",
]

defect_number = 1


for inspection in inspection_results:

    failed_quantity = (
        Decimal(str(inspection.failed_quantity))
        .quantize(Decimal("0.001"))
    )

    if failed_quantity <= Decimal("0.000"):
        continue

    # Split a failed inspection quantity into a realistic
    # defect quantity while never exceeding failed quantity.
    defect_quantity = (
        failed_quantity * Decimal("0.50")
    ).quantize(
        Decimal("0.001")
    )

    if defect_quantity <= Decimal("0.000"):
        defect_quantity = failed_quantity

    defect_type = defect_types[
        inspection.id % len(defect_types)
    ]

    severity = severities[
        inspection.id % len(severities)
    ]

    defects.append(
        Defect(
            defect_number=(
                f"DEF-2026-{defect_number:06d}"
            ),
            inspection_result=inspection,
            production_order=inspection.production_order,
            process_step=inspection.inspection_plan.process_step,
            defect_type=defect_type,
            severity=severity,
            quantity=defect_quantity,
            description=(
                f"{defect_type.replace('_', ' ').title()} "
                f"detected during "
                f"{inspection.inspection_plan.process_step.name}."
            ),
            status="OPEN",
            detected_at=inspection.inspected_at,
        )
    )

    defect_number += 1


Defect.objects.bulk_create(
    defects,
    batch_size=5000,
)

print(
    f"Created defects: {len(defects)}"
)