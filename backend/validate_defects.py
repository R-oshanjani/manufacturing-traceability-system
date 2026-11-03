from manufacturing.models import Defect


defects = Defect.objects.all()

quantity_mismatches = []

for defect in defects.iterator():

    inspection = defect.inspection_result

    if defect.quantity > inspection.failed_quantity:
        quantity_mismatches.append(
            defect.defect_number
        )


print(
    "Defects:",
    defects.count()
)

print(
    "Duplicate defect numbers:",
    defects.values("defect_number").count()
    - defects.values("defect_number")
    .distinct()
    .count()
)

print(
    "Defects without inspection result:",
    defects.filter(
        inspection_result__isnull=True
    ).count()
)

print(
    "Defects without production order:",
    defects.filter(
        production_order__isnull=True
    ).count()
)

print(
    "Defects without process step:",
    defects.filter(
        process_step__isnull=True
    ).count()
)

print(
    "Defect quantity exceeding failed quantity:",
    len(quantity_mismatches)
)

print(
    "Invalid defect quantities:",
    defects.filter(
        quantity__lte=0
    ).count()
)