"""
Kanban URLs
"""
from django.urls import path
from . import views

app_name = 'kanban'

urlpatterns = [
    # Boards
    path('boards/', views.BoardListCreateView.as_view(), name='boards-list'),
    path('boards/<int:pk>/', views.BoardDetailView.as_view(), name='board-detail'),

    # Columns
    path('boards/<int:board_id>/columns/', views.ColumnListCreateView.as_view(), name='columns-list'),

    # Cards
    path('cards/', views.CardListView.as_view(), name='cards-list'),
    path('cards/<int:pk>/', views.CardDetailView.as_view(), name='card-detail'),
    path('cards/<int:pk>/move/', views.MoveCardView.as_view(), name='card-move'),
]
