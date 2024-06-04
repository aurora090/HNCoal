from django.urls import path
from KnowledgeExtraction import views

urlpatterns = [
    # path('extract_text/', views.extract_text, name='extract_text'),
    path('ke',views.ke),
]
