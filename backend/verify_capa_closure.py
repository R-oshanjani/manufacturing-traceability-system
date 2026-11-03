import os
import sys

import django
from django.db.models import Q

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from manufacturing.models import CorrectiveAction  # noqa: E402


def main():
    total = CorrectiveAction.objects.count()

    closed = CorrectiveAction.objects.filter(
        status="CLOSED"
    ).count()

    invalid_closed = CorrectiveAction.objects.filter(
        status="CLOSED"
    ).filter(
        Q(verification_date__isnull=True)
        | Q(verified_by__isnull=True)
        | Q(verification_result__isnull=True)
    ).count()

    print("=" * 70)
    print("CAPA CLOSURE VERIFICATION")
    print("=" * 70)

    print(f"Total CAPA: {total}")
    print(f"Closed CAPA: {closed}")
    print(f"Closed CAPA without verification: {invalid_closed}")
    print()

    if invalid_closed == 0:
        print("CAPA CLOSURE CHECK: PASS")
        print(
            "Every closed CAPA has verification date, verifier, "
            "and verification result."
        )
        return 0

    print("CAPA CLOSURE CHECK: FAIL")
    print(
        f"{invalid_closed} closed CAPA record(s) are missing "
        "required verification information."
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())