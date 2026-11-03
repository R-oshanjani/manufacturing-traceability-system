from rest_framework import serializers

from .models import (
    Product,
    Supplier,
    Material,
    BOM,
    BOMComponent,
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


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = "__all__"


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = "__all__"


class BOMComponentSerializer(serializers.ModelSerializer):
    material_code = serializers.CharField(
        source="material.material_code",
        read_only=True,
    )

    class Meta:
        model = BOMComponent
        fields = [
            "id",
            "bom",
            "material",
            "material_code",
            "required_quantity",
            "scrap_percentage",
            "sequence",
        ]


class BOMSerializer(serializers.ModelSerializer):
    product_sku = serializers.CharField(
        source="product.sku",
        read_only=True,
    )

    components = BOMComponentSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = BOM
        fields = "__all__"


class MaterialLotSerializer(serializers.ModelSerializer):
    material_code = serializers.CharField(
        source="material.material_code",
        read_only=True,
    )

    supplier_code = serializers.CharField(
        source="supplier.supplier_code",
        read_only=True,
    )

    class Meta:
        model = MaterialLot
        fields = "__all__"


class ProductionOrderSerializer(serializers.ModelSerializer):
    product_sku = serializers.CharField(
        source="product.sku",
        read_only=True,
    )

    class Meta:
        model = ProductionOrder
        fields = "__all__"


class MaterialConsumptionSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(
        source="production_order.order_number",
        read_only=True,
    )

    lot_number = serializers.CharField(
        source="material_lot.lot_number",
        read_only=True,
    )

    class Meta:
        model = MaterialConsumption
        fields = "__all__"


class MachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = "__all__"


class ProcessStepSerializer(serializers.ModelSerializer):
    machine_code = serializers.CharField(
        source="machine.machine_code",
        read_only=True,
    )

    class Meta:
        model = ProcessStep
        fields = "__all__"


class InspectionPlanSerializer(serializers.ModelSerializer):
    product_sku = serializers.CharField(
        source="product.sku",
        read_only=True,
    )

    process_name = serializers.CharField(
        source="process_step.name",
        read_only=True,
    )

    class Meta:
        model = InspectionPlan
        fields = "__all__"


class InspectionResultSerializer(serializers.ModelSerializer):
    inspection_code = serializers.CharField(
        source="inspection_plan.inspection_code",
        read_only=True,
    )

    order_number = serializers.CharField(
        source="production_order.order_number",
        read_only=True,
    )

    class Meta:
        model = InspectionResult
        fields = "__all__"


class DefectSerializer(serializers.ModelSerializer):
    inspection_number = serializers.CharField(
        source="inspection_result.inspection_number",
        read_only=True,
    )

    order_number = serializers.CharField(
        source="production_order.order_number",
        read_only=True,
    )

    process_name = serializers.CharField(
        source="process_step.name",
        read_only=True,
    )

    class Meta:
        model = Defect
        fields = "__all__"


class CorrectiveActionSerializer(serializers.ModelSerializer):
    defect_number = serializers.CharField(
        source="defect.defect_number",
        read_only=True,
    )

    class Meta:
        model = CorrectiveAction
        fields = "__all__"