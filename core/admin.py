from django.contrib import admin
from .models import Group, Member, Expense, ExpenseSplit

admin.site.register(Group)
admin.site.register(Member)
admin.site.register(Expense)
admin.site.register(ExpenseSplit)
