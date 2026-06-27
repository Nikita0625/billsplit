from decimal import Decimal


def simplify_debts(members, expenses, ious=None):
    """
    Smart debt simplification algorithm.
    Includes both group expenses and personal IOUs.
    """
    balance = {m.id: Decimal('0') for m in members}

    # Group expenses
    for expense in expenses:
        balance[expense.paid_by_id] += expense.amount
        for split in expense.splits.all():
            balance[split.member_id] -= split.share_amount

    # Personal IOUs
    if ious:
        for iou in ious:
            balance[iou.lender_id] += iou.amount
            balance[iou.borrower_id] -= iou.amount

    member_map = {m.id: m.name for m in members}

    creditors = []
    debtors = []

    for uid, amt in balance.items():
        if amt > Decimal('0.01'):
            creditors.append([amt, uid])
        elif amt < Decimal('-0.01'):
            debtors.append([-amt, uid])

    creditors.sort(reverse=True)
    debtors.sort(reverse=True)

    transactions = []

    while creditors and debtors:
        credit_amt, creditor_id = creditors.pop(0)
        debt_amt, debtor_id = debtors.pop(0)

        settled = min(credit_amt, debt_amt)
        transactions.append({
            'from_name': member_map[debtor_id],
            'to_name': member_map[creditor_id],
            'amount': round(settled, 2),
        })

        remaining_credit = credit_amt - settled
        remaining_debt = debt_amt - settled

        if remaining_credit > Decimal('0.01'):
            creditors.insert(0, [remaining_credit, creditor_id])
        if remaining_debt > Decimal('0.01'):
            debtors.insert(0, [remaining_debt, debtor_id])

    return transactions


def get_member_balances(members, expenses, ious=None):
    """
    Returns each member's net balance including IOUs.
    """
    balance = {m.id: Decimal('0') for m in members}

    for expense in expenses:
        balance[expense.paid_by_id] += expense.amount
        for split in expense.splits.all():
            balance[split.member_id] -= split.share_amount

    if ious:
        for iou in ious:
            balance[iou.lender_id] += iou.amount
            balance[iou.borrower_id] -= iou.amount

    result = []
    for m in members:
        result.append({
            'member': m,
            'balance': round(balance[m.id], 2),
        })
    return result