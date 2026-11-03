from decimal import Decimal
from django.utils import timezone

from manufacturing.models import (
    InspectionPlan,
    ProductionOrder,
    InspectionResult,
)


inspection_plans_db = list(
    InspectionPlan.objects
    .select_related("product", "process_step")
    .filter(is_active=True)
    .order_by("id")
)

production_orders_db = list(
    ProductionOrder.objects
    .select_related("product", "bom")
    .order_by("id")
)

inspection_results = []

inspection_number = 1

for order in production_orders_db:

    product_plans = [
        plan
        for plan in inspection_plans_db
        if plan.product_id == order.product_id
    ]

    selected_plans = product_plans[:4]

    for plan in selected_plans:

        inspected_quantity = (
            Decimal(str(order.planned_quantity))
            .quantize(Decimal("0.001"))
        )

        failure_rate = Decimal("0.03")

        failed_quantity = (
            inspected_quantity * failure_rate
        ).quantize(Decimal("0.001"))

        passed_quantity = (
            inspected_quantity - failed_quantity
        ).quantize(Decimal("0.001"))

        if failed_quantity == Decimal("0.000"):
            result_status = "PASS"
        elif passed_quantity == Decimal("0.000"):
            result_status = "FAIL"
        else:
            result_status = "PARTIAL"

        inspection_results.append(
            InspectionResult(
                inspection_number=(
                    f"INSP-{order.order_number}-"
                    f"{inspection_number:05d}"
                ),
                inspection_plan=plan,
                production_order=order,
                inspected_quantity=inspected_quantity,
                passed_quantity=passed_quantity,
                failed_quantity=failed_quantity,
                result=result_status,
                inspected_at=timezone.make_aware(
                    timezone.datetime(
                        2026, 1, 20, 10, 0, 0
                    )
                ),
                notes=(
                    f"Inspection performed for "
                    f"{order.order_number} at "
                    f"{plan.process_step.name}."
                ),
            )
        )

        inspection_number += 1


InspectionResult.objects.bulk_create(
    inspection_results,
    batch_size=5000,
)

print(
    f"Created inspection results: "
    f"{len(inspection_results)}"
)