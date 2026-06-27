from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.db import IntegrityError
from decimal import Decimal, InvalidOperation

from .models import Group, Member, Expense, ExpenseSplit, Settlement, IOU
from .utils import simplify_debts, get_member_balances


def home(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        currency = request.POST.get('currency', '₹').strip()
        creator_name = request.POST.get('creator_name', '').strip()

        if not name or not creator_name:
            messages.error(request, 'Group name and your name are required.')
            return render(request, 'core/home.html')

        group = Group.objects.create(name=name, description=description, currency=currency)
        member = Member.objects.create(group=group, name=creator_name)
        request.session[f'member_{group.id}'] = member.id
        return redirect('group_detail', group_id=group.id)

    return render(request, 'core/home.html')


def group_detail(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    members = group.members.all().order_by('joined_at')
    expenses = group.expenses.all().select_related('paid_by').prefetch_related('splits__member').order_by('-created_at')
    ious = group.ious.all().select_related('lender', 'borrower').order_by('-created_at')

    member_id = request.session.get(f'member_{group.id}')
    current_member = None
    if member_id:
        try:
            current_member = Member.objects.get(id=member_id, group=group)
        except Member.DoesNotExist:
            pass

    balances = get_member_balances(members, expenses, ious)
    settlements = simplify_debts(members, expenses, ious)

    context = {
        'group': group,
        'members': members,
        'expenses': expenses,
        'ious': ious,
        'balances': balances,
        'settlements': settlements,
        'current_member': current_member,
        'total_expenses': group.total_expenses(),
    }
    return render(request, 'core/group_detail.html', context)


def join_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if not name:
            messages.error(request, 'Please enter your name.')
            return redirect('group_detail', group_id=group.id)

        try:
            member, created = Member.objects.get_or_create(group=group, name=name)
            request.session[f'member_{group.id}'] = member.id
            if created:
                messages.success(request, f'Welcome, {name}! You joined the group.')
            else:
                messages.success(request, f'Welcome back, {name}!')
        except IntegrityError:
            messages.error(request, 'That name is already taken in this group.')

    return redirect('group_detail', group_id=group.id)


def add_expense(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    members = group.members.all().order_by('joined_at')

    member_id = request.session.get(f'member_{group.id}')
    if not member_id:
        messages.error(request, 'You must join the group first.')
        return redirect('group_detail', group_id=group.id)

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        amount_str = request.POST.get('amount', '').strip()
        paid_by_id = request.POST.get('paid_by', '').strip()
        split_type = request.POST.get('split_type', 'equal')
        included_members = request.POST.getlist('included_members')
        notes = request.POST.get('notes', '').strip()
        proof_type = request.POST.get('proof_type', 'none')
        proof_image = request.FILES.get('proof_image')

        errors = []
        if not title:
            errors.append('Expense title is required.')
        if not amount_str:
            errors.append('Amount is required.')
        if not paid_by_id:
            errors.append('Please select who paid.')
        if not included_members:
            errors.append('Select at least one member to split with.')
        if proof_type == 'image' and not proof_image:
            errors.append('Please upload a payment screenshot.')

        try:
            amount = Decimal(amount_str)
            if amount <= 0:
                errors.append('Amount must be greater than zero.')
        except (InvalidOperation, ValueError):
            errors.append('Enter a valid amount.')
            amount = None

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, 'core/add_expense.html', {
                'group': group, 'members': members, 'post': request.POST,
            })

        try:
            paid_by = Member.objects.get(id=paid_by_id, group=group)
        except Member.DoesNotExist:
            messages.error(request, 'Invalid payer selected.')
            return redirect('add_expense', group_id=group.id)

        expense = Expense.objects.create(
            group=group,
            paid_by=paid_by,
            title=title,
            amount=amount,
            notes=notes,
            proof_type=proof_type,
            proof_image=proof_image if proof_type == 'image' else None,
        )

        included = Member.objects.filter(id__in=included_members, group=group)

        if split_type == 'equal':
            count = included.count()
            share = round(amount / count, 2)
            total_assigned = share * count
            diff = amount - total_assigned
            for i, m in enumerate(included):
                adj = diff if i == 0 else Decimal('0')
                ExpenseSplit.objects.create(expense=expense, member=m, share_amount=share + adj)

        elif split_type == 'custom':
            total_custom = Decimal('0')
            custom_amounts = {}
            for m in included:
                val_str = request.POST.get(f'custom_{m.id}', '0').strip()
                try:
                    val = Decimal(val_str)
                except InvalidOperation:
                    val = Decimal('0')
                custom_amounts[m.id] = val
                total_custom += val

            if abs(total_custom - amount) > Decimal('0.02'):
                expense.delete()
                messages.error(request, f'Custom amounts ({total_custom}) must sum to {amount}.')
                return render(request, 'core/add_expense.html', {
                    'group': group, 'members': members, 'post': request.POST,
                })

            for m in included:
                ExpenseSplit.objects.create(
                    expense=expense,
                    member=m,
                    share_amount=custom_amounts[m.id]
                )

        messages.success(request, f'Expense "{title}" added successfully!')
        return redirect('group_detail', group_id=group.id)

    current_member_id = request.session.get(f'member_{group.id}')
    return render(request, 'core/add_expense.html', {
        'group': group,
        'members': members,
        'current_member_id': int(current_member_id) if current_member_id else None,
    })


def delete_expense(request, group_id, expense_id):
    group = get_object_or_404(Group, id=group_id)
    expense = get_object_or_404(Expense, id=expense_id, group=group)

    member_id = request.session.get(f'member_{group.id}')
    if not member_id:
        messages.error(request, 'You must be a member to delete expenses.')
        return redirect('group_detail', group_id=group.id)

    if request.method == 'POST':
        if expense.proof_image:
            expense.proof_image.delete()
        expense.delete()
        messages.success(request, 'Expense deleted.')

    return redirect('group_detail', group_id=group.id)


def view_proof(request, group_id, expense_id):
    group = get_object_or_404(Group, id=group_id)
    expense = get_object_or_404(Expense, id=expense_id, group=group)
    return render(request, 'core/view_proof.html', {'group': group, 'expense': expense})


def add_iou(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    members = group.members.all().order_by('joined_at')

    member_id = request.session.get(f'member_{group.id}')
    if not member_id:
        messages.error(request, 'You must join the group first.')
        return redirect('group_detail', group_id=group.id)

    if request.method == 'POST':
        lender_id = request.POST.get('lender_id', '').strip()
        borrower_id = request.POST.get('borrower_id', '').strip()
        amount_str = request.POST.get('amount', '').strip()
        reason = request.POST.get('reason', '').strip()
        notes = request.POST.get('notes', '').strip()
        proof_type = request.POST.get('proof_type', 'none')
        proof_image = request.FILES.get('proof_image')

        errors = []
        if not lender_id:
            errors.append('Select who lent the money.')
        if not borrower_id:
            errors.append('Select who borrowed the money.')
        if lender_id == borrower_id:
            errors.append('Lender and borrower cannot be the same person.')
        if not reason:
            errors.append('Reason is required.')
        if not amount_str:
            errors.append('Amount is required.')
        if proof_type == 'image' and not proof_image:
            errors.append('Please upload a payment screenshot.')

        try:
            amount = Decimal(amount_str)
            if amount <= 0:
                errors.append('Amount must be greater than zero.')
        except (InvalidOperation, ValueError):
            errors.append('Enter a valid amount.')
            amount = None

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, 'core/add_iou.html', {
                'group': group, 'members': members, 'post': request.POST,
            })

        try:
            lender = Member.objects.get(id=lender_id, group=group)
            borrower = Member.objects.get(id=borrower_id, group=group)
        except Member.DoesNotExist:
            messages.error(request, 'Invalid member selected.')
            return redirect('add_iou', group_id=group.id)

        IOU.objects.create(
            group=group,
            lender=lender,
            borrower=borrower,
            amount=amount,
            reason=reason,
            notes=notes,
            proof_type=proof_type,
            proof_image=proof_image if proof_type == 'image' else None,
        )

        messages.success(request, f'IOU recorded! {borrower.name} owes {lender.name} ₹{amount}.')
        return redirect('group_detail', group_id=group.id)

    current_member_id = request.session.get(f'member_{group.id}')
    return render(request, 'core/add_iou.html', {
        'group': group,
        'members': members,
        'current_member_id': int(current_member_id) if current_member_id else None,
    })


def delete_iou(request, group_id, iou_id):
    group = get_object_or_404(Group, id=group_id)
    iou = get_object_or_404(IOU, id=iou_id, group=group)

    member_id = request.session.get(f'member_{group.id}')
    if not member_id:
        messages.error(request, 'You must be a member to delete IOUs.')
        return redirect('group_detail', group_id=group.id)

    if request.method == 'POST':
        if iou.proof_image:
            iou.proof_image.delete()
        iou.delete()
        messages.success(request, 'IOU deleted.')

    return redirect('group_detail', group_id=group.id)


def settlements_json(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    members = group.members.all()
    expenses = group.expenses.all().prefetch_related('splits')
    ious = group.ious.all()
    settlements = simplify_debts(members, expenses, ious)
    return JsonResponse({'settlements': settlements})