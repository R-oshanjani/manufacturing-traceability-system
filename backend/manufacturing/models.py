from django.db import models


class Product(models.Model):
    sku = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    unit_of_measure = models.CharField(max_length=20, default="EA")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.sku} - {self.name}"

class Supplier(models.Model):
    supplier_code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.supplier_code} - {self.name}"
class Machine(models.Model):
    machine_code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    machine_type = models.CharField(max_length=100)
    location = models.CharField(max_length=200, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("ACTIVE", "Active"),
            ("MAINTENANCE", "Maintenance"),
            ("INACTIVE", "Inactive"),
        ],
        default="ACTIVE",
    )
    installed_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.machine_code} - {self.name}"
class BOM(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="boms",
    )
    version = models.PositiveIntegerField(default=1)
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["product", "version"],
                name="unique_product_bom_version",
            )
        ]

    def __str__(self):
        return f"{self.product.sku} - BOM v{self.version}"
class Material(models.Model):
    material_code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    unit_of_measure = models.CharField(max_length=20, default="EA")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.material_code} - {self.name}"
class BOMComponent(models.Model):
    bom = models.ForeignKey(
        BOM,
        on_delete=models.PROTECT,
        related_name="components",
    )
    material = models.ForeignKey(
        Material,
        on_delete=models.PROTECT,
        related_name="bom_components",
    )
    required_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=3,
    )
    scrap_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )
    sequence = models.PositiveIntegerField(default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["bom", "material"],
                name="unique_material_per_bom",
            )
        ]

    def __str__(self):
        return f"{self.bom} - {self.material.material_code}"
class MaterialLot(models.Model):
    lot_number = models.CharField(max_length=100, unique=True)
    material = models.ForeignKey(
        Material,
        on_delete=models.PROTECT,
        related_name="material_lots",
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name="material_lots",
    )
    received_quantity = models.DecimalField(
        max_digits=14,
        decimal_places=3,
    )
    received_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("AVAILABLE", "Available"),
            ("QUARANTINE", "Quarantine"),
            ("CONSUMED", "Consumed"),
            ("REJECTED", "Rejected"),
        ],
        default="AVAILABLE",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.lot_number
class ProductionOrder(models.Model):
    order_number = models.CharField(max_length=50, unique=True)

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="production_orders",
    )

    bom = models.ForeignKey(
        BOM,
        on_delete=models.PROTECT,
        related_name="production_orders",
    )

    planned_quantity = models.DecimalField(
        max_digits=14,
        decimal_places=3,
    )

    actual_quantity = models.DecimalField(
        max_digits=14,
        decimal_places=3,
        default=0,
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ("PLANNED", "Planned"),
            ("RELEASED", "Released"),
            ("IN_PROGRESS", "In Progress"),
            ("COMPLETED", "Completed"),
            ("CLOSED", "Closed"),
            ("CANCELLED", "Cancelled"),
        ],
        default="PLANNED",
    )

    planned_start = models.DateField()
    planned_end = models.DateField()

    actual_start = models.DateField(null=True, blank=True)
    actual_end = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.order_number
class MaterialConsumption(models.Model):
    production_order = models.ForeignKey(
        ProductionOrder,
        on_delete=models.PROTECT,
        related_name="material_consumptions",
    )

    material_lot = models.ForeignKey(
        MaterialLot,
        on_delete=models.PROTECT,
        related_name="production_consumptions",
    )

    consumed_quantity = models.DecimalField(
        max_digits=14,
        decimal_places=3,
    )

    consumed_at = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["production_order", "material_lot"],
                name="unique_order_material_lot_consumption",
            )
        ]

    def __str__(self):
        return f"{self.production_order.order_number} - {self.material_lot.lot_number}"
class ProcessStep(models.Model):
    process_code = models.CharField(
        max_length=50,
        unique=True,
    )

    name = models.CharField(
        max_length=200,
    )

    sequence = models.PositiveIntegerField()

    machine = models.ForeignKey(
        Machine,
        on_delete=models.PROTECT,
        related_name="process_steps",
    )

    description = models.TextField(
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"{self.process_code} - {self.name}"
class InspectionPlan(models.Model):
    inspection_code = models.CharField(
        max_length=50,
        unique=True,
    )

    name = models.CharField(
        max_length=200,
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="inspection_plans",
    )

    process_step = models.ForeignKey(
        ProcessStep,
        on_delete=models.PROTECT,
        related_name="inspection_plans",
    )

    inspection_type = models.CharField(
        max_length=50,
        choices=[
            ("VISUAL", "Visual"),
            ("DIMENSIONAL", "Dimensional"),
            ("WEIGHT", "Weight"),
            ("FUNCTIONAL", "Functional"),
            ("CHEMICAL", "Chemical"),
        ],
    )

    specification = models.TextField(
        blank=True,
    )

    sampling_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=100,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"{self.inspection_code} - {self.name}"
class InspectionResult(models.Model):
    inspection_number = models.CharField(
        max_length=100,
        unique=True,
    )

    inspection_plan = models.ForeignKey(
        InspectionPlan,
        on_delete=models.PROTECT,
        related_name="inspection_results",
    )

    production_order = models.ForeignKey(
        ProductionOrder,
        on_delete=models.PROTECT,
        related_name="inspection_results",
    )

    inspected_quantity = models.DecimalField(
        max_digits=14,
        decimal_places=3,
    )

    passed_quantity = models.DecimalField(
        max_digits=14,
        decimal_places=3,
        default=0,
    )

    failed_quantity = models.DecimalField(
        max_digits=14,
        decimal_places=3,
        default=0,
    )

    result = models.CharField(
        max_length=20,
        choices=[
            ("PASS", "Pass"),
            ("FAIL", "Fail"),
            ("PARTIAL", "Partial"),
        ],
    )

    inspected_at = models.DateTimeField()

    notes = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return self.inspection_number
class Defect(models.Model):
    defect_number = models.CharField(
        max_length=100,
        unique=True,
    )

    inspection_result = models.ForeignKey(
        InspectionResult,
        on_delete=models.PROTECT,
        related_name="defects",
    )

    production_order = models.ForeignKey(
        ProductionOrder,
        on_delete=models.PROTECT,
        related_name="defects",
    )

    process_step = models.ForeignKey(
        ProcessStep,
        on_delete=models.PROTECT,
        related_name="defects",
    )

    defect_type = models.CharField(
        max_length=100,
    )

    severity = models.CharField(
        max_length=20,
        choices=[
            ("LOW", "Low"),
            ("MEDIUM", "Medium"),
            ("HIGH", "High"),
            ("CRITICAL", "Critical"),
        ],
    )

    quantity = models.DecimalField(
        max_digits=14,
        decimal_places=3,
    )

    description = models.TextField(
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ("OPEN", "Open"),
            ("CONTAINED", "Contained"),
            ("RESOLVED", "Resolved"),
            ("CLOSED", "Closed"),
        ],
        default="OPEN",
    )

    detected_at = models.DateTimeField()

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return self.defect_number
class CorrectiveAction(models.Model):
    capa_number = models.CharField(
        max_length=100,
        unique=True,
    )

    defect = models.ForeignKey(
        Defect,
        on_delete=models.PROTECT,
        related_name="corrective_actions",
    )

    title = models.CharField(
        max_length=200,
    )

    description = models.TextField(
        blank=True,
    )

    root_cause = models.TextField(
        blank=True,
    )

    containment_action = models.TextField(
        blank=True,
    )

    corrective_action = models.TextField(
        blank=True,
    )

    preventive_action = models.TextField(
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ("OPEN", "Open"),
            ("IN_PROGRESS", "In Progress"),
            ("PENDING_VERIFICATION", "Pending Verification"),
            ("CLOSED", "Closed"),
        ],
        default="OPEN",
    )

    assigned_to = models.CharField(
        max_length=200,
        blank=True,
    )

    target_date = models.DateField(
        null=True,
        blank=True,
    )

    completed_date = models.DateField(
        null=True,
        blank=True,
    )

    verification_date = models.DateField(
        null=True,
        blank=True,
    )

    verified_by = models.CharField(
        max_length=200,
        blank=True,
    )

    verification_result = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return self.capa_number