import hashlib
import json
import os
import sys

import django


# Allow the script to run from the project root.
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from manufacturing.models import (  # noqa: E402
    Product,
    Supplier,
    Material,
    BOM,
    BOMComponent,
    MaterialLot,
    ProductionOrder,
    MaterialConsumption,
)


SEED = 20261022


def model_fingerprint(model, fields):
    """
    Create a deterministic SHA-256 fingerprint from selected database fields.
    Records are ordered by primary key so the same database state produces
    the same fingerprint.
    """
    rows = model.objects.order_by("id").values_list(*fields)

    digest = hashlib.sha256()
    count = 0

    for row in rows:
        normalized = json.dumps(
            [str(value) if value is not None else None for value in row],
            separators=(",", ":"),
        )
        digest.update(normalized.encode("utf-8"))
        digest.update(b"\n")
        count += 1

    return count, digest.hexdigest()


MODELS = [
    (
        "Product",
        Product,
        ["id", "sku", "name", "unit_of_measure", "is_active"],
    ),
    (
        "Supplier",
        Supplier,
        ["id", "supplier_code", "name", "contact_email", "is_active"],
    ),
    (
        "Material",
        Material,
        ["id", "material_code", "name", "unit_of_measure", "is_active"],
    ),
    (
        "BOM",
        BOM,
        ["id", "product_id", "version", "effective_from", "effective_to", "is_active"],
    ),
    (
        "BOMComponent",
        BOMComponent,
        [
            "id",
            "bom_id",
            "material_id",
            "required_quantity",
            "scrap_percentage",
            "sequence",
        ],
    ),
    (
        "MaterialLot",
        MaterialLot,
        [
            "id",
            "lot_number",
            "material_id",
            "supplier_id",
            "received_quantity",
            "received_date",
            "expiry_date",
            "status",
        ],
    ),
    (
        "ProductionOrder",
        ProductionOrder,
        [
            "id",
            "order_number",
            "product_id",
            "bom_id",
            "planned_quantity",
            "actual_quantity",
            "status",
            "planned_start",
            "planned_end",
            "actual_start",
            "actual_end",
        ],
    ),
    (
        "MaterialConsumption",
        MaterialConsumption,
        [
            "id",
            "production_order_id",
            "material_lot_id",
            "consumed_quantity",
            "consumed_at",
        ],
    ),
]


def collect_fingerprint():
    results = {}

    for name, model, fields in MODELS:
        count, checksum = model_fingerprint(model, fields)

        results[name] = {
            "row_count": count,
            "sha256": checksum,
        }

    return results


def main():
    print("=" * 70)
    print("MANUFACTURING TRACEABILITY REPRODUCIBILITY CHECK")
    print("=" * 70)
    print(f"Fixed generator seed: {SEED}")
    print()

    print("Collecting fingerprint - Run 1...")
    run_1 = collect_fingerprint()

    print("Collecting fingerprint - Run 2...")
    run_2 = collect_fingerprint()

    print()
    print("-" * 70)
    print("RESULTS")
    print("-" * 70)

    all_match = True

    for name in run_1:
        count_1 = run_1[name]["row_count"]
        count_2 = run_2[name]["row_count"]

        hash_1 = run_1[name]["sha256"]
        hash_2 = run_2[name]["sha256"]

        count_match = count_1 == count_2
        hash_match = hash_1 == hash_2

        status = "PASS" if count_match and hash_match else "FAIL"

        if status == "FAIL":
            all_match = False

        print(f"{name}: {status}")
        print(f"  Run 1 rows : {count_1}")
        print(f"  Run 2 rows : {count_2}")
        print(f"  SHA-256    : {hash_1}")
        print(f"  Match      : {hash_match}")
        print()

    print("-" * 70)

    if all_match:
        print("REPRODUCIBILITY CHECK: PASS")
        print("Both fingerprint runs produced identical row counts and checksums.")
        print(f"Seed recorded by generator: {SEED}")
        return 0

    print("REPRODUCIBILITY CHECK: FAIL")
    print("One or more row counts or checksums differ.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())