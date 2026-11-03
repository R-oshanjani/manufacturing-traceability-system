from manufacturing.models import (
    Product,
    ProcessStep,
    InspectionPlan,
)


inspection_types = [
    "VISUAL",
    "DIMENSIONAL",
    "WEIGHT",
    "FUNCTIONAL",
    "CHEMICAL",
]

products_db = list(
    Product.objects
    .filter(is_active=True)
    .order_by("id")
)

process_steps_db = list(
    ProcessStep.objects
    .filter(is_active=True)
    .order_by("sequence")
)

existing_plan_count = InspectionPlan.objects.count()

inspection_plans = []

plan_number = existing_plan_count + 1

for product in products_db:

    existing_steps = set(
        InspectionPlan.objects
        .filter(product=product)
        .values_list("process_step_id", flat=True)
    )

    available_steps = [
        step
        for step in process_steps_db
        if step.id not in existing_steps
    ]

    selected_steps = available_steps[:2]

    for step_index, process_step in enumerate(
        selected_steps,
        start=1,
    ):

        inspection_type = inspection_types[
            (product.id + step_index + 2)
            % len(inspection_types)
        ]

        inspection_plans.append(
            InspectionPlan(
                inspection_code=(
                    f"INSP-PLAN-{plan_number:06d}"
                ),
                name=(
                    f"{product.sku} - "
                    f"{process_step.name} Inspection"
                ),
                product=product,
                process_step=process_step,
                inspection_type=inspection_type,
                specification=(
                    f"Standard "
                    f"{inspection_type.lower()} "
                    f"inspection for {product.sku}."
                ),
                sampling_percentage=100,
                is_active=True,
            )
        )

        plan_number += 1


InspectionPlan.objects.bulk_create(
    inspection_plans,
    batch_size=500,
)

print(
    f"Created additional inspection plans: "
    f"{len(inspection_plans)}"
)