from django.db.models import Sum
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import (
    Product,
    Supplier,
    Material,
    BOM,
    MaterialLot,
    ProductionOrder,
    MaterialConsumption,
    Machine,
    ProcessStep,
    InspectionPlan,
    InspectionResult,
    Defect,
    CorrectiveAction,
)

from .serializers import (
    ProductSerializer,
    SupplierSerializer,
    MaterialSerializer,
    BOMSerializer,
    MaterialLotSerializer,
    ProductionOrderSerializer,
    MaterialConsumptionSerializer,
    MachineSerializer,
    ProcessStepSerializer,
    InspectionPlanSerializer,
    InspectionResultSerializer,
    DefectSerializer,
    CorrectiveActionSerializer,
)


# ============================================================
# MASTER DATA / READ-ONLY API
# ============================================================

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all().order_by("id")
    serializer_class = ProductSerializer


class SupplierViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Supplier.objects.all().order_by("id")
    serializer_class = SupplierSerializer


class MaterialViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Material.objects.all().order_by("id")
    serializer_class = MaterialSerializer


class BOMViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        BOM.objects
        .select_related("product")
        .prefetch_related("components")
        .order_by("id")
    )
    serializer_class = BOMSerializer


class MaterialLotViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        MaterialLot.objects
        .select_related("material", "supplier")
        .order_by("id")
    )
    serializer_class = MaterialLotSerializer


class ProductionOrderViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        ProductionOrder.objects
        .select_related("product", "bom")
        .order_by("id")
    )
    serializer_class = ProductionOrderSerializer


class MaterialConsumptionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        MaterialConsumption.objects
        .select_related("production_order", "material_lot")
        .order_by("id")
    )
    serializer_class = MaterialConsumptionSerializer


class MachineViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Machine.objects.all().order_by("id")
    serializer_class = MachineSerializer


class ProcessStepViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        ProcessStep.objects
        .select_related("machine")
        .order_by("sequence")
    )
    serializer_class = ProcessStepSerializer


class InspectionPlanViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        InspectionPlan.objects
        .select_related("product", "process_step")
        .order_by("id")
    )
    serializer_class = InspectionPlanSerializer


class InspectionResultViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        InspectionResult.objects
        .select_related("inspection_plan", "production_order")
        .order_by("id")
    )
    serializer_class = InspectionResultSerializer


class DefectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        Defect.objects
        .select_related(
            "inspection_result",
            "production_order",
            "process_step",
        )
        .order_by("id")
    )
    serializer_class = DefectSerializer


class CorrectiveActionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        CorrectiveAction.objects
        .select_related("defect")
        .order_by("id")
    )
    serializer_class = CorrectiveActionSerializer


# ============================================================
# PRODUCTION ORDER TRACEABILITY
# ============================================================

@api_view(["GET"])
def traceability(request, order_number):
    try:
        order = (
            ProductionOrder.objects
            .select_related(
                "product",
                "bom",
            )
            .prefetch_related(
                "bom__components__material",
                "material_consumptions__material_lot__material",
                "material_consumptions__material_lot__supplier",
                "inspection_results__inspection_plan__process_step__machine",
                "inspection_results__defects__corrective_actions",
            )
            .get(order_number=order_number)
        )

    except ProductionOrder.DoesNotExist:
        return Response(
            {
                "error": f"Production order '{order_number}' not found."
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    # --------------------------------------------------------
    # BOM COMPONENTS
    # --------------------------------------------------------

    bom_components = []

    for component in order.bom.components.all():
        bom_components.append(
            {
                "material_code": component.material.material_code,
                "material_name": component.material.name,
                "required_quantity": str(
                    component.required_quantity
                ),
                "scrap_percentage": str(
                    component.scrap_percentage
                ),
                "sequence": component.sequence,
            }
        )

    # --------------------------------------------------------
    # MATERIAL TRACEABILITY
    # --------------------------------------------------------

    material_traceability = []

    for consumption in order.material_consumptions.all():
        lot = consumption.material_lot

        material_traceability.append(
            {
                "material_code": lot.material.material_code,
                "material_name": lot.material.name,
                "lot_number": lot.lot_number,
                "supplier_code": lot.supplier.supplier_code,
                "supplier_name": lot.supplier.name,
                "received_quantity": str(
                    lot.received_quantity
                ),
                "received_date": lot.received_date,
                "consumed_quantity": str(
                    consumption.consumed_quantity
                ),
                "consumed_at": consumption.consumed_at,
            }
        )

    # --------------------------------------------------------
    # INSPECTION / DEFECT / CAPA
    # --------------------------------------------------------

    quality_traceability = []

    for inspection in order.inspection_results.all():

        defects = []

        for defect in inspection.defects.all():

            corrective_actions = []

            for capa in defect.corrective_actions.all():

                corrective_actions.append(
                    {
                        "capa_number": capa.capa_number,
                        "title": capa.title,
                        "status": capa.status,
                        "root_cause": capa.root_cause,
                        "containment_action": capa.containment_action,
                        "corrective_action": capa.corrective_action,
                        "preventive_action": capa.preventive_action,
                        "assigned_to": capa.assigned_to,
                        "target_date": capa.target_date,
                        "completed_date": capa.completed_date,
                        "verification_date": capa.verification_date,
                        "verified_by": capa.verified_by,
                        "verification_result": capa.verification_result,
                    }
                )

            defects.append(
                {
                    "defect_number": defect.defect_number,
                    "defect_type": defect.defect_type,
                    "severity": defect.severity,
                    "quantity": str(defect.quantity),
                    "description": defect.description,
                    "status": defect.status,
                    "detected_at": defect.detected_at,
                    "process_step": {
                        "code": defect.process_step.process_code,
                        "name": defect.process_step.name,
                        "sequence": defect.process_step.sequence,
                    },
                    "machine": {
                        "code": defect.process_step.machine.machine_code,
                        "name": defect.process_step.machine.name,
                        "type": defect.process_step.machine.machine_type,
                    },
                    "corrective_actions": corrective_actions,
                }
            )

        quality_traceability.append(
            {
                "inspection_number": inspection.inspection_number,
                "inspection_code": (
                    inspection.inspection_plan.inspection_code
                ),
                "inspection_type": (
                    inspection.inspection_plan.inspection_type
                ),
                "inspected_quantity": str(
                    inspection.inspected_quantity
                ),
                "passed_quantity": str(
                    inspection.passed_quantity
                ),
                "failed_quantity": str(
                    inspection.failed_quantity
                ),
                "result": inspection.result,
                "inspected_at": inspection.inspected_at,
                "process_step": {
                    "code": (
                        inspection.inspection_plan
                        .process_step
                        .process_code
                    ),
                    "name": (
                        inspection.inspection_plan
                        .process_step
                        .name
                    ),
                },
                "machine": {
                    "code": (
                        inspection.inspection_plan
                        .process_step
                        .machine
                        .machine_code
                    ),
                    "name": (
                        inspection.inspection_plan
                        .process_step
                        .machine
                        .name
                    ),
                },
                "defects": defects,
            }
        )

    # --------------------------------------------------------
    # FINAL RESPONSE
    # --------------------------------------------------------

    response_data = {
        "production_order": {
            "order_number": order.order_number,
            "product": {
                "sku": order.product.sku,
                "name": order.product.name,
            },
            "bom_version": order.bom.version,
            "planned_quantity": str(
                order.planned_quantity
            ),
            "actual_quantity": str(
                order.actual_quantity
            ),
            "status": order.status,
            "planned_start": order.planned_start,
            "planned_end": order.planned_end,
            "actual_start": order.actual_start,
            "actual_end": order.actual_end,
        },
        "bom": {
            "version": order.bom.version,
            "effective_from": order.bom.effective_from,
            "effective_to": order.bom.effective_to,
            "components": bom_components,
        },
        "material_traceability": material_traceability,
        "quality_traceability": quality_traceability,
    }

    return Response(response_data)


# ============================================================
# DASHBOARD SUMMARY
# ============================================================

@api_view(["GET"])
def dashboard_summary(request):

    total_products = Product.objects.count()
    total_suppliers = Supplier.objects.count()
    total_materials = Material.objects.count()
    total_material_lots = MaterialLot.objects.count()
    total_production_orders = ProductionOrder.objects.count()
    total_inspections = InspectionResult.objects.count()
    total_defects = Defect.objects.count()
    total_capa = CorrectiveAction.objects.count()

    # --------------------------------------------------------
    # DEFECT STATUS
    # --------------------------------------------------------

    open_defects = Defect.objects.filter(
        status="OPEN"
    ).count()

    contained_defects = Defect.objects.filter(
        status="CONTAINED"
    ).count()

    resolved_defects = Defect.objects.filter(
        status="RESOLVED"
    ).count()

    closed_defects = Defect.objects.filter(
        status="CLOSED"
    ).count()

    # --------------------------------------------------------
    # DEFECT SEVERITY
    # --------------------------------------------------------

    critical_defects = Defect.objects.filter(
        severity="CRITICAL"
    ).count()

    high_defects = Defect.objects.filter(
        severity="HIGH"
    ).count()

    # --------------------------------------------------------
    # CAPA STATUS
    # --------------------------------------------------------

    capa_open = CorrectiveAction.objects.filter(
        status="OPEN"
    ).count()

    capa_in_progress = CorrectiveAction.objects.filter(
        status="IN_PROGRESS"
    ).count()

    capa_pending_verification = CorrectiveAction.objects.filter(
        status="PENDING_VERIFICATION"
    ).count()

    capa_closed = CorrectiveAction.objects.filter(
        status="CLOSED"
    ).count()

    # --------------------------------------------------------
    # INSPECTION TOTALS
    # --------------------------------------------------------

    inspection_totals = InspectionResult.objects.aggregate(
        inspected=Sum("inspected_quantity"),
        failed=Sum("failed_quantity"),
    )

    inspected_quantity = (
        inspection_totals["inspected"] or 0
    )

    failed_quantity = (
        inspection_totals["failed"] or 0
    )

    if inspected_quantity:
        defect_rate = (
            float(failed_quantity)
            / float(inspected_quantity)
        ) * 100
    else:
        defect_rate = 0

    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return Response(
        {
            "master_data": {
                "products": total_products,
                "suppliers": total_suppliers,
                "materials": total_materials,
                "material_lots": total_material_lots,
            },
            "production": {
                "production_orders": total_production_orders,
            },
            "quality": {
                "inspections": total_inspections,
                "defects": total_defects,
                "inspected_quantity": str(
                    inspected_quantity
                ),
                "failed_quantity": str(
                    failed_quantity
                ),
                "defect_rate_percent": round(
                    defect_rate,
                    2,
                ),
                "defects_by_status": {
                    "open": open_defects,
                    "contained": contained_defects,
                    "resolved": resolved_defects,
                    "closed": closed_defects,
                },
                "defects_by_severity": {
                    "critical": critical_defects,
                    "high": high_defects,
                },
            },
            "corrective_actions": {
                "total": total_capa,
                "open": capa_open,
                "in_progress": capa_in_progress,
                "pending_verification": (
                    capa_pending_verification
                ),
                "closed": capa_closed,
            },
        }
    )


# ============================================================
# MATERIAL LOT TRACEABILITY
# ============================================================

@api_view(["GET"])
def lot_traceability(request, lot_number):

    try:
        lot = (
            MaterialLot.objects
            .select_related(
                "material",
                "supplier",
            )
            .prefetch_related(
                "production_consumptions__production_order__product",
                "production_consumptions__production_order__bom",
                (
                    "production_consumptions__production_order"
                    "__inspection_results__inspection_plan"
                    "__process_step__machine"
                ),
                (
                    "production_consumptions__production_order"
                    "__inspection_results__defects"
                    "__corrective_actions"
                ),
            )
            .get(lot_number=lot_number)
        )

    except MaterialLot.DoesNotExist:

        return Response(
            {
                "error": (
                    f"Material lot '{lot_number}' "
                    "not found."
                )
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    production_orders = []

    for consumption in lot.production_consumptions.all():

        order = consumption.production_order

        inspections = []

        for inspection in order.inspection_results.all():

            defects = []

            for defect in inspection.defects.all():

                capas = []

                for capa in defect.corrective_actions.all():

                    capas.append(
                        {
                            "capa_number": capa.capa_number,
                            "title": capa.title,
                            "status": capa.status,
                            "root_cause": capa.root_cause,
                            "corrective_action": (
                                capa.corrective_action
                            ),
                            "verification_date": (
                                capa.verification_date
                            ),
                            "verified_by": capa.verified_by,
                            "verification_result": (
                                capa.verification_result
                            ),
                        }
                    )

                defects.append(
                    {
                        "defect_number": defect.defect_number,
                        "defect_type": defect.defect_type,
                        "severity": defect.severity,
                        "quantity": str(
                            defect.quantity
                        ),
                        "status": defect.status,
                        "process_step": (
                            defect.process_step.name
                        ),
                        "machine": (
                            defect.process_step
                            .machine
                            .machine_code
                        ),
                        "corrective_actions": capas,
                    }
                )

            if defects:

                inspections.append(
                    {
                        "inspection_number": (
                            inspection.inspection_number
                        ),
                        "result": inspection.result,
                        "failed_quantity": str(
                            inspection.failed_quantity
                        ),
                        "defects": defects,
                    }
                )

        production_orders.append(
            {
                "order_number": order.order_number,
                "product_sku": order.product.sku,
                "product_name": order.product.name,
                "order_status": order.status,
                "planned_quantity": str(
                    order.planned_quantity
                ),
                "actual_quantity": str(
                    order.actual_quantity
                ),
                "consumed_quantity": str(
                    consumption.consumed_quantity
                ),
                "consumed_at": consumption.consumed_at,
                "inspections_with_defects": inspections,
            }
        )

    return Response(
        {
            "material_lot": {
                "lot_number": lot.lot_number,
                "material_code": (
                    lot.material.material_code
                ),
                "material_name": lot.material.name,
                "supplier_code": (
                    lot.supplier.supplier_code
                ),
                "supplier_name": lot.supplier.name,
                "received_quantity": str(
                    lot.received_quantity
                ),
                "received_date": lot.received_date,
                "status": lot.status,
            },
            "downstream_traceability": production_orders,
        }
    )