from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('group/<uuid:group_id>/', views.group_detail, name='group_detail'),
    path('group/<uuid:group_id>/join/', views.join_group, name='join_group'),
    path('group/<uuid:group_id>/add/', views.add_expense, name='add_expense'),
    path('group/<uuid:group_id>/expense/<int:expense_id>/delete/', views.delete_expense, name='delete_expense'),
    path('group/<uuid:group_id>/expense/<int:expense_id>/proof/', views.view_proof, name='view_proof'),
    path('group/<uuid:group_id>/iou/add/', views.add_iou, name='add_iou'),
    path('group/<uuid:group_id>/iou/<int:iou_id>/delete/', views.delete_iou, name='delete_iou'),
    path('group/<uuid:group_id>/settlements.json', views.settlements_json, name='settlements_json'),
]