from manufacturing.models import InspectionResult


results = InspectionResult.objects.all()

quantity_mismatches = []

for result in results.iterator():

    calculated_total = (
        result.passed_quantity
        + result.failed_quantity
    )

    if calculated_total != result.inspected_quantity:
        quantity_mismatches.append(
            result.inspection_number
        )


print(
    "Inspection Results:",
    results.count()
)

print(
    "Duplicate inspection numbers:",
    results.values("inspection_number").count()
    - results.values("inspection_number")
    .distinct()
    .count()
)

print(
    "Quantity mismatches:",
    len(quantity_mismatches)
)

print(
    "Results without inspection plan:",
    results.filter(
        inspection_plan__isnull=True
    ).count()
)

print(
    "Results without production order:",
    results.filter(
        production_order__isnull=True
    ).count()
)

print(
    "Invalid inspected quantities:",
    results.filter(
        inspected_quantity__lte=0
    ).count()
)

print(
    "Invalid failed quantities:",
    results.filter(
        failed_quantity__lt=0
    ).count()
)

print(
    "Invalid passed quantities:",
    results.filter(
        passed_quantity__lt=0
    ).count()
)