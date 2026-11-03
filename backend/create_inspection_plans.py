from manufacturing.models import Product, ProcessStep, InspectionPlan


inspection_types = [
    "VISUAL",
    "DIMENSIONAL",
    "WEIGHT",
    "FUNCTIONAL",
    "CHEMICAL",
]


process_steps_db = list(
    ProcessStep.objects
    .filter(is_active=True)
    .order_by("sequence")
)


products_db = list(
    Product.objects
    .filter(is_active=True)
    .order_by("id")
)


inspection_plans = []

plan_number = 1


for product in products_db:

    selected_steps = process_steps_db[:2]

    for step_index, process_step in enumerate(
        selected_steps,
        start=1,
    ):

        inspection_type = inspection_types[
            (product.id + step_index)
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
                    f"inspection for "
                    f"{product.sku}."
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
    "Created inspection plans:",
    len(inspection_plans),
)