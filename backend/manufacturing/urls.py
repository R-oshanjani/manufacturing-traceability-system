from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    ProductViewSet,
    SupplierViewSet,
    MaterialViewSet,
    BOMViewSet,
    MaterialLotViewSet,
    ProductionOrderViewSet,
    MaterialConsumptionViewSet,
    MachineViewSet,
    ProcessStepViewSet,
    InspectionPlanViewSet,
    InspectionResultViewSet,
    DefectViewSet,
    CorrectiveActionViewSet,
    traceability,
     dashboard_summary,
        lot_traceability,
)


router = DefaultRouter()

router.register("products", ProductViewSet, basename="product")
router.register("suppliers", SupplierViewSet, basename="supplier")
router.register("materials", MaterialViewSet, basename="material")
router.register("boms", BOMViewSet, basename="bom")
router.register("material-lots", MaterialLotViewSet, basename="material-lot")

router.register(
    "production-orders",
    ProductionOrderViewSet,
    basename="production-order",
)

router.register(
    "material-consumptions",
    MaterialConsumptionViewSet,
    basename="material-consumption",
)

router.register(
    "machines",
    MachineViewSet,
    basename="machine",
)

router.register(
    "process-steps",
    ProcessStepViewSet,
    basename="process-step",
)

router.register(
    "inspection-plans",
    InspectionPlanViewSet,
    basename="inspection-plan",
)

router.register(
    "inspection-results",
    InspectionResultViewSet,
    basename="inspection-result",
)

router.register(
    "defects",
    DefectViewSet,
    basename="defect",
)

router.register(
    "corrective-actions",
    CorrectiveActionViewSet,
    basename="corrective-action",
)


urlpatterns = [
    path(
        "traceability/<str:order_number>/",
        traceability,
        name="traceability",
    ),
      path(
        "dashboard/",
        dashboard_summary,
        name="dashboard-summary",
    ),
    path(
    "lot-traceability/<str:lot_number>/",
    lot_traceability,
    name="lot-traceability",
),
] + router.urls