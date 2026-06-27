import uuid
from django.db import models


class Group(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255, blank=True)
    currency = models.CharField(max_length=10, default='₹')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def total_expenses(self):
        return sum(e.amount for e in self.expenses.all())

    def member_count(self):
        return self.members.count()


class Member(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='members')
    name = models.CharField(max_length=100)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.group.name})"

    class Meta:
        unique_together = ('group', 'name')


class Expense(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='expenses')
    paid_by = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='paid_expenses')
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    PROOF_NONE = 'none'
    PROOF_CASH = 'cash'
    PROOF_IMAGE = 'image'
    PROOF_CHOICES = [
        (PROOF_NONE, 'No Proof'),
        (PROOF_CASH, 'Paid in Cash'),
        (PROOF_IMAGE, 'Payment Screenshot'),
    ]
    proof_type = models.CharField(max_length=10, choices=PROOF_CHOICES, default=PROOF_NONE)
    proof_image = models.ImageField(upload_to='proofs/', blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.amount}"


class ExpenseSplit(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name='splits')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='splits')
    share_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.member.name} owes {self.share_amount} for {self.expense.title}"

    class Meta:
        unique_together = ('expense', 'member')


class Settlement(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='settlements')
    from_member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='payments_made')
    to_member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='payments_received')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    settled_at = models.DateTimeField(auto_now_add=True)
    notes = models.CharField(max_length=255, blank=True)

    PROOF_NONE = 'none'
    PROOF_CASH = 'cash'
    PROOF_IMAGE = 'image'
    PROOF_CHOICES = [
        (PROOF_NONE, 'No Proof'),
        (PROOF_CASH, 'Paid in Cash'),
        (PROOF_IMAGE, 'Payment Screenshot'),
    ]
    proof_type = models.CharField(max_length=10, choices=PROOF_CHOICES, default=PROOF_NONE)
    proof_image = models.ImageField(upload_to='settlement_proofs/', blank=True, null=True)

    def __str__(self):
        return f"{self.from_member.name} paid {self.to_member.name} ₹{self.amount}"


class IOU(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='ious')
    lender = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='ious_given')
    borrower = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='ious_taken')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    PROOF_NONE = 'none'
    PROOF_CASH = 'cash'
    PROOF_IMAGE = 'image'
    PROOF_CHOICES = [
        (PROOF_NONE, 'No Proof'),
        (PROOF_CASH, 'Paid in Cash'),
        (PROOF_IMAGE, 'Payment Screenshot'),
    ]
    proof_type = models.CharField(max_length=10, choices=PROOF_CHOICES, default=PROOF_NONE)
    proof_image = models.ImageField(upload_to='iou_proofs/', blank=True, null=True)

    def __str__(self):
        return f"{self.lender.name} lent {self.amount} to {self.borrower.name}"