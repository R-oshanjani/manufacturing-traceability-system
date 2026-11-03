from datetime import timedelta

from django.utils import timezone

from manufacturing.models import Defect, CorrectiveAction


defects = list(
    Defect.objects
    .select_related("production_order", "process_step")
    .order_by("id")
)

capas = []

base_date = timezone.datetime(
    2026,
    2,
    1,
).date()

for index, defect in enumerate(defects, start=1):

    if index % 4 == 0:
        status = "CLOSED"
        completed_date = base_date + timedelta(days=10)
        verification_date = completed_date + timedelta(days=2)
        verified_by = "Quality Engineer"
        verification_result = "Corrective action verified and effective."

    elif index % 4 == 1:
        status = "OPEN"
        completed_date = None
        verification_date = None
        verified_by = ""
        verification_result = ""

    elif index % 4 == 2:
        status = "IN_PROGRESS"
        completed_date = None
        verification_date = None
        verified_by = ""
        verification_result = ""

    else:
        status = "PENDING_VERIFICATION"
        completed_date = base_date + timedelta(days=10)
        verification_date = None
        verified_by = ""
        verification_result = ""

    capas.append(
        CorrectiveAction(
            capa_number=f"CAPA-2026-{index:06d}",
            defect=defect,
            title=f"Corrective Action for {defect.defect_number}",
            description=(
                f"Investigation and corrective action for "
                f"{defect.defect_type} detected at "
                f"{defect.process_step.name}."
            ),
            root_cause="Process variation identified during investigation.",
            containment_action="Affected material and production output contained.",
            corrective_action="Process parameters reviewed and corrected.",
            preventive_action="Additional process monitoring implemented.",
            status=status,
            assigned_to="Quality Engineer",
            target_date=base_date + timedelta(days=10),
            completed_date=completed_date,
            verification_date=verification_date,
            verified_by=verified_by,
            verification_result=verification_result,
        )
    )


CorrectiveAction.objects.bulk_create(
    capas,
    batch_size=5000,
)

print(f"Created corrective actions: {len(capas)}")