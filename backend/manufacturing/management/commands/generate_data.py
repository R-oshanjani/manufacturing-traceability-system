import random
from decimal import Decimal
from django.utils import timezone
from django.core.management.base import BaseCommand

from manufacturing.models import (
    Product,
    Supplier,
    Material,
    BOM,
    BOMComponent,
    MaterialLot,
    ProductionOrder,
    MaterialConsumption,
)


class Command(BaseCommand):
    help = "Generate synthetic manufacturing traceability data"

    def handle(self, *args, **options):
        random.seed(20261022)

        # =========================================================
        # Products
        # =========================================================

        products = []

        product_types = [
            "Motor",
            "Pump",
            "Valve",
            "Controller",
            "Sensor",
            "Gearbox",
            "Actuator",
            "Compressor",
            "Generator",
            "Industrial Panel",
        ]

        for i in range(1, 201):
            product_type = random.choice(product_types)

            products.append(
                Product(
                    sku=f"SKU-{i:06d}",
                    name=f"{product_type} Model {i:04d}",
                    description=f"Synthetic {product_type.lower()} product",
                    unit_of_measure="EA",
                    is_active=True,
                )
            )

        Product.objects.bulk_create(
            products,
            ignore_conflicts=True,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {len(products)} products."
            )
        )

        # =========================================================
        # Suppliers
        # =========================================================

        suppliers = []

        supplier_types = [
            "Components",
            "Electronics",
            "Metals",
            "Plastics",
            "Industrial",
            "Mechanical",
            "Electrical",
            "Automation",
        ]

        for i in range(1, 51):
            supplier_type = random.choice(supplier_types)

            suppliers.append(
                Supplier(
                    supplier_code=f"SUP-{i:04d}",
                    name=f"{supplier_type} Supplier {i:03d}",
                    contact_email=f"supplier{i:03d}@example.com",
                    contact_phone=f"+91-90000{i:05d}",
                    address=f"Industrial Area {i:03d}",
                    is_active=True,
                )
            )

        Supplier.objects.bulk_create(
            suppliers,
            ignore_conflicts=True,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {len(suppliers)} suppliers."
            )
        )

        # =========================================================
        # Materials
        # =========================================================

        materials = []

        material_types = [
            "Steel",
            "Aluminum",
            "Copper",
            "Plastic",
            "Electronic",
            "Bearing",
            "Fastener",
            "Cable",
            "Sensor",
            "Connector",
        ]

        for i in range(1, 201):
            material_type = random.choice(material_types)

            materials.append(
                Material(
                    material_code=f"MAT-{i:06d}",
                    name=f"{material_type} Material {i:04d}",
                    description=(
                        f"Synthetic "
                        f"{material_type.lower()} "
                        f"manufacturing material"
                    ),
                    unit_of_measure="EA",
                    is_active=True,
                )
            )

        Material.objects.bulk_create(
            materials,
            ignore_conflicts=True,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {len(materials)} materials."
            )
        )

        # =========================================================
        # BOMs
        # =========================================================

        boms = []

        products_db = list(
            Product.objects.order_by("id")
        )

        for product in products_db:
            boms.append(
                BOM(
                    product=product,
                    version=1,
                    effective_from="2026-01-01",
                    effective_to=None,
                    is_active=True,
                )
            )

        BOM.objects.bulk_create(
            boms,
            ignore_conflicts=True,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {len(boms)} BOMs."
            )
        )

        # =========================================================
        # BOM Components
        # =========================================================

        materials_db = list(
            Material.objects.order_by("id")
        )

        boms_db = list(
            BOM.objects
            .select_related("product")
            .order_by("id")
        )

        bom_components = []

        for bom in boms_db:

            component_count = random.randint(
                3,
                6,
            )

            selected_materials = random.sample(
                materials_db,
                component_count,
            )

            for sequence, material in enumerate(
                selected_materials,
                start=1,
            ):

                bom_components.append(
                    BOMComponent(
                        bom=bom,
                        material=material,
                        required_quantity=round(
                            random.uniform(1, 10),
                            3,
                        ),
                        scrap_percentage=round(
                            random.uniform(0, 5),
                            2,
                        ),
                        sequence=sequence,
                    )
                )

        BOMComponent.objects.bulk_create(
            bom_components,
            ignore_conflicts=True,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {len(bom_components)} BOM components."
            )
        )

        # =========================================================
        # Production Orders
        #
        # Production Orders are created BEFORE Material Lots
        # because Material Lots are calculated from actual demand.
        # =========================================================

        products_db = list(
            Product.objects.order_by("id")
        )

        production_orders = []

        for i in range(1, 5001):

            product = random.choice(
                products_db
            )

            bom = (
                BOM.objects
                .filter(
                    product=product,
                    is_active=True,
                )
                .order_by("-version")
                .first()
            )

            planned_quantity = round(
                random.uniform(50, 500),
                3,
            )

            planned_start_month = random.randint(
                1,
                12,
            )

            planned_start_day = random.randint(
                1,
                20,
            )

            production_orders.append(
                ProductionOrder(
                    order_number=f"WO-2026-{i:06d}",
                    product=product,
                    bom=bom,
                    planned_quantity=planned_quantity,
                    actual_quantity=0,
                    status="PLANNED",
                    planned_start=(
                        f"2026-"
                        f"{planned_start_month:02d}-"
                        f"{planned_start_day:02d}"
                    ),
                    planned_end=(
                        f"2026-"
                        f"{planned_start_month:02d}-"
                        f"{min(planned_start_day + 7, 28):02d}"
                    ),
                    actual_start=None,
                    actual_end=None,
                )
            )

        ProductionOrder.objects.bulk_create(
            production_orders,
            ignore_conflicts=True,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {len(production_orders)} production orders."
            )
        )

        # =========================================================
        # Material Lots
        #
        # Material inventory is calculated from actual demand.
        #
        # demand = BOM quantity × production quantity
        # target inventory = demand × 1.20
        #
        # Exactly 2,000 lots are created.
        # =========================================================

        materials_db = list(
            Material.objects.order_by("id")
        )

        suppliers_db = list(
            Supplier.objects.order_by("id")
        )

        production_orders_db = list(
            ProductionOrder.objects
            .select_related(
                "product",
                "bom",
            )
            .order_by("id")
        )

        # ---------------------------------------------------------
        # Calculate actual material demand.
        # Use Decimal throughout so that the demand used to create
        # inventory is exactly the same demand used for consumption.
        # ---------------------------------------------------------

        material_demand = {
            material.id: Decimal("0.000")
            for material in materials_db
        }

        for order in production_orders_db:

            components = list(
                BOMComponent.objects
                .filter(
                    bom=order.bom,
                )
                .select_related("material")
                .order_by("sequence")
            )

            for component in components:

                required_quantity = (
                    Decimal(str(component.required_quantity))
                    * Decimal(str(order.planned_quantity))
                ).quantize(
                    Decimal("0.001")
                )

                material_demand[component.material_id] += (
                    required_quantity
                )

        total_demand = sum(
            material_demand.values(),
            Decimal("0.000"),
        )

        # ---------------------------------------------------------
        # Add 20% safety stock.
        # ---------------------------------------------------------

        material_target = {
            material_id: (
                demand * Decimal("1.20")
            ).quantize(
                Decimal("0.001")
            )
            for material_id, demand
            in material_demand.items()
        }

        total_inventory_target = sum(
            material_target.values(),
            Decimal("0.000"),
        )

        # ---------------------------------------------------------
        # Allocate exactly 2,000 lots.
        #
        # Every material with demand gets at least one lot.
        # Remaining lots are distributed according to demand.
        # ---------------------------------------------------------

        TOTAL_LOTS = 2000

        lot_counts = {
            material.id: 1
            for material in materials_db
            if material_demand.get(
                material.id,
                Decimal("0.000"),
            ) > Decimal("0.000")
        }

        remaining_lots = (
            TOTAL_LOTS
            - sum(lot_counts.values())
        )

        if remaining_lots > 0 and total_demand > 0:

            fractional_allocations = []

            for material in materials_db:

                demand = material_demand.get(
                    material.id,
                    Decimal("0.000"),
                )

                if demand <= Decimal("0.000"):
                    continue

                exact_additional = (
                    demand
                    / total_demand
                    * Decimal(remaining_lots)
                )

                additional_lots = int(
                    exact_additional
                )

                lot_counts[material.id] += additional_lots

                fractional_allocations.append(
                    (
                        exact_additional
                        - Decimal(additional_lots),
                        material.id,
                    )
                )

            allocated_lots = sum(
                lot_counts.values()
            )

            leftover_lots = (
                TOTAL_LOTS
                - allocated_lots
            )

            fractional_allocations.sort(
                reverse=True
            )

            for _, material_id in (
                fractional_allocations[:leftover_lots]
            ):

                lot_counts[material_id] += 1

        # ---------------------------------------------------------
        # Create the 2,000 material lots.
        # ---------------------------------------------------------

        material_lots = []
        lot_sequence = 1

        for material in materials_db:

            target_quantity = material_target.get(
                material.id,
                Decimal("0.000"),
            )

            number_of_lots = lot_counts.get(
                material.id,
                0,
            )

            if number_of_lots <= 0:
                continue

            quantity_per_lot = (
                target_quantity
                / Decimal(number_of_lots)
            ).quantize(
                Decimal("0.001")
            )

            allocated_quantity = Decimal("0.000")

            for lot_index in range(number_of_lots):

                supplier = random.choice(
                    suppliers_db
                )

                # Put the rounding remainder into the final lot.
                if lot_index == number_of_lots - 1:

                    received_quantity = (
                        target_quantity
                        - allocated_quantity
                    ).quantize(
                        Decimal("0.001")
                    )

                else:

                    received_quantity = quantity_per_lot

                allocated_quantity = (
                    allocated_quantity
                    + received_quantity
                ).quantize(
                    Decimal("0.001")
                )

                material_lots.append(
                    MaterialLot(
                        lot_number=(
                            f"LOT-"
                            f"{supplier.supplier_code}"
                            f"-2026-"
                            f"{lot_sequence:06d}"
                        ),
                        material=material,
                        supplier=supplier,
                        received_quantity=received_quantity,
                        received_date=(
                            f"2026-"
                            f"{random.randint(1, 12):02d}-"
                            f"{random.randint(1, 28):02d}"
                        ),
                        expiry_date=None,
                        status="AVAILABLE",
                    )
                )

                lot_sequence += 1

        MaterialLot.objects.bulk_create(
            material_lots,
            ignore_conflicts=True,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {len(material_lots)} material lots."
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Total material demand: "
                f"{total_demand:,.3f}"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Total inventory target: "
                f"{total_inventory_target:,.3f}"
            )
        )

        # =========================================================
        # Material Consumption
        #
        # Every production-order + BOM-component requirement
        # must be completely satisfied by material lots.
        #
        # Consumption is stored at 3 decimal places.
        # =========================================================

        production_orders_db = list(
            ProductionOrder.objects
            .select_related(
                "product",
                "bom",
            )
            .order_by("id")
        )

        material_lots_db = list(
            MaterialLot.objects
            .select_related(
                "material",
            )
            .filter(
                status="AVAILABLE",
            )
            .order_by("id")
        )

        # ---------------------------------------------------------
        # Track remaining quantity for every material lot.
        # ---------------------------------------------------------

        remaining_quantity = {
            lot.id: Decimal(str(lot.received_quantity)).quantize(
                Decimal("0.001")
            )
            for lot in material_lots_db
        }

        # ---------------------------------------------------------
        # Group lots by material.
        # ---------------------------------------------------------

        lots_by_material = {}

        for lot in material_lots_db:

            lots_by_material.setdefault(
                lot.material_id,
                [],
            ).append(lot)

        material_consumptions = []

        # ---------------------------------------------------------
        # Fixed timestamp for deterministic generated data.
        # ---------------------------------------------------------

        consumption_timestamp = timezone.make_aware(
            timezone.datetime(
                2026,
                1,
                15,
                10,
                0,
                0,
            )
        )

        # ---------------------------------------------------------
        # Consume material against each production order.
        # ---------------------------------------------------------

        for order in production_orders_db:

            components = list(
                BOMComponent.objects
                .filter(
                    bom=order.bom,
                )
                .select_related(
                    "material",
                )
                .order_by("sequence")
            )

            for component in components:

                # -------------------------------------------------
                # Calculate the requirement for THIS production
                # order and THIS BOM component.
                # -------------------------------------------------

                required_quantity = (
                    Decimal(str(component.required_quantity))
                    * Decimal(str(order.planned_quantity))
                ).quantize(
                    Decimal("0.001")
                )

                remaining_requirement = required_quantity

                # -------------------------------------------------
                # Get only lots belonging to this material.
                # -------------------------------------------------

                lots = lots_by_material.get(
                    component.material_id,
                    [],
                )

                # -------------------------------------------------
                # Consume lots until requirement is satisfied.
                # -------------------------------------------------

                for lot in lots:

                    if remaining_requirement <= Decimal("0.000"):
                        break

                    available_quantity = (
                        remaining_quantity.get(
                            lot.id,
                            Decimal("0.000"),
                        )
                    ).quantize(
                        Decimal("0.001")
                    )

                    if available_quantity <= Decimal("0.000"):
                        continue

                    # -------------------------------------------------
                    # Consume the smaller of the remaining requirement
                    # and the remaining quantity in this lot.
                    # -------------------------------------------------

                    consumed_quantity = min(
                        remaining_requirement,
                        available_quantity,
                    ).quantize(
                        Decimal("0.001")
                    )

                    if consumed_quantity <= Decimal("0.000"):
                        continue

                    # -------------------------------------------------
                    # Create consumption record.
                    # -------------------------------------------------

                    material_consumptions.append(
                        MaterialConsumption(
                            production_order=order,
                            material_lot=lot,
                            consumed_quantity=consumed_quantity,
                            consumed_at=consumption_timestamp,
                        )
                    )

                    # -------------------------------------------------
                    # Reduce remaining quantity of the material lot.
                    # -------------------------------------------------

                    remaining_quantity[lot.id] = (
                        available_quantity
                        - consumed_quantity
                    ).quantize(
                        Decimal("0.001")
                    )

                    # -------------------------------------------------
                    # Reduce remaining requirement.
                    # -------------------------------------------------

                    remaining_requirement = (
                        remaining_requirement
                        - consumed_quantity
                    ).quantize(
                        Decimal("0.001")
                    )

                # -----------------------------------------------------
                # Safety check: inventory must fully satisfy the BOM
                # requirement for this production order.
                # -----------------------------------------------------

                if remaining_requirement > Decimal("0.000"):

                    raise ValueError(
                        "Material shortage detected: "
                        f"Production Order="
                        f"{order.order_number}, "
                        f"Material="
                        f"{component.material.material_code}, "
                        f"Required="
                        f"{required_quantity}, "
                        f"Remaining="
                        f"{remaining_requirement}"
                    )

                # -----------------------------------------------------
                # Exact reconciliation check.
                # -----------------------------------------------------

                if remaining_requirement != Decimal("0.000"):

                    raise ValueError(
                        "Consumption reconciliation failed: "
                        f"Production Order="
                        f"{order.order_number}, "
                        f"Material="
                        f"{component.material.material_code}, "
                        f"Required="
                        f"{required_quantity}, "
                        f"Remaining="
                        f"{remaining_requirement}"
                    )

        # ---------------------------------------------------------
        # Save all consumption records.
        # ---------------------------------------------------------

        MaterialConsumption.objects.bulk_create(
            material_consumptions,
            batch_size=5000,
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Created "
                f"{len(material_consumptions)} "
                "material consumption records."
            )
        )
        # =========================================================
# Machines
# =========================================================

        machine_definitions = [
            ("MACH-CNC", "CNC Machining Center", "CNC"),
            ("MACH-MILL", "Milling Machine", "MILLING"),
            ("MACH-LATHE", "CNC Lathe", "LATHE"),
            ("MACH-PRESS", "Hydraulic Press", "PRESS"),
            ("MACH-WELD", "Welding Station", "WELDING"),
            ("MACH-ASSY", "Assembly Station", "ASSEMBLY"),
            ("MACH-PAINT", "Paint Booth", "PAINTING"),
            ("MACH-HEAT", "Heat Treatment Unit", "HEAT_TREATMENT"),
            ("MACH-TEST", "Functional Test Station", "TESTING"),
            ("MACH-PACK", "Packaging Station", "PACKAGING"),
        ]

        machines = []

        for index, (code, name, machine_type) in enumerate(
            machine_definitions,
            start=1,
        ):
            machines.append(
                Machine(
                    machine_code=code,
                    name=name,
                    machine_type=machine_type,
                    location=f"PLANT-{((index - 1) % 3) + 1}",
                    status="ACTIVE",
                    installed_date=timezone.datetime(
                        2023,
                        1,
                        1,
                    ).date(),
                )
            )

        Machine.objects.bulk_create(
            machines,
            batch_size=100,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {len(machines)} machines."
            )
        )


        # =========================================================
        # Process Steps
        # =========================================================

        process_definitions = [
            (
                "PROC-001",
                "Incoming Material Inspection",
                1,
                "MACH-TEST",
            ),
            (
                "PROC-002",
                "CNC Machining",
                2,
                "MACH-CNC",
            ),
            (
                "PROC-003",
                "Milling",
                3,
                "MACH-MILL",
            ),
            (
                "PROC-004",
                "Turning",
                4,
                "MACH-LATHE",
            ),
            (
                "PROC-005",
                "Pressing",
                5,
                "MACH-PRESS",
            ),
            (
                "PROC-006",
                "Welding",
                6,
                "MACH-WELD",
            ),
            (
                "PROC-007",
                "Assembly",
                7,
                "MACH-ASSY",
            ),
            (
                "PROC-008",
                "Painting",
                8,
                "MACH-PAINT",
            ),
            (
                "PROC-009",
                "Heat Treatment",
                9,
                "MACH-HEAT",
            ),
            (
                "PROC-010",
                "Functional Testing",
                10,
                "MACH-TEST",
            ),
            (
                "PROC-011",
                "Final Inspection",
                11,
                "MACH-TEST",
            ),
            (
                "PROC-012",
                "Packaging",
                12,
                "MACH-PACK",
            ),
        ]

        machines_by_code = {
            machine.machine_code: machine
            for machine in Machine.objects.all()
        }

        process_steps = []

        for code, name, sequence, machine_code in process_definitions:
            process_steps.append(
                ProcessStep(
                    process_code=code,
                    name=name,
                    sequence=sequence,
                    machine=machines_by_code[machine_code],
                    description=(
                        f"Standard manufacturing process step: "
                        f"{name}."
                    ),
                    is_active=True,
                )
            )

        ProcessStep.objects.bulk_create(
            process_steps,
            batch_size=100,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {len(process_steps)} process steps."
            )
        )
        # =========================================================
# Inspection Plans
# =========================================================

        inspection_types = [
            "VISUAL",
            "DIMENSIONAL",
            "WEIGHT",
            "FUNCTIONAL",
            "CHEMICAL",
        ]

        process_steps_db = list(
            ProcessStep.objects
            .select_related("machine")
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

            # Create 2 inspection plans for each product.
            selected_steps = process_steps_db[
                :2
            ]

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
                            f"Standard {inspection_type.lower()} "
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

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {len(inspection_plans)} inspection plans."
            )
        )
        # =========================================================
# Inspection Results
# =========================================================

        inspection_plans_db = list(
            InspectionPlan.objects
            .select_related(
                "product",
                "process_step",
            )
            .filter(is_active=True)
            .order_by("id")
        )

        production_orders_db = list(
            ProductionOrder.objects
            .select_related(
                "product",
                "bom",
            )
            .order_by("id")
        )

        inspection_results = []

        inspection_number = 1

        for order in production_orders_db:

            matching_plans = [
                plan
                for plan in inspection_plans_db
                if plan.product_id == order.product_id
            ]

            for plan in matching_plans:

                inspected_quantity = Decimal(
                    str(order.planned_quantity)
                ).quantize(
                    Decimal("0.001")
                )

                failure_probability = (
                    Decimal("0.03")
                )

                failed_quantity = (
                    inspected_quantity
                    * failure_probability
                ).quantize(
                    Decimal("0.001")
                )

                passed_quantity = (
                    inspected_quantity
                    - failed_quantity
                ).quantize(
                    Decimal("0.001")
                )

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
                                2026,
                                1,
                                20,
                                10,
                                0,
                                0,
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

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {len(inspection_results)} "
                "inspection results."
            )
        )
        # =========================================================
# Inspection Results
# =========================================================

        inspection_plans_db = list(
            InspectionPlan.objects
            .select_related(
                "product",
                "process_step",
            )
            .filter(is_active=True)
            .order_by("id")
        )

        production_orders_db = list(
            ProductionOrder.objects
            .select_related(
                "product",
                "bom",
            )
            .order_by("id")
        )

        inspection_results = []

        inspection_number = 1

        for order in production_orders_db:

            # Select exactly 4 inspection plans for the product.
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

                # Base failure rate: 3%
                failure_rate = Decimal("0.03")

                failed_quantity = (
                    inspected_quantity * failure_rate
                ).quantize(
                    Decimal("0.001")
                )

                passed_quantity = (
                    inspected_quantity - failed_quantity
                ).quantize(
                    Decimal("0.001")
                )

                # Determine inspection result.
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
                                2026,
                                1,
                                20,
                                10,
                                0,
                                0,
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

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {len(inspection_results)} inspection results."
            )
        )