from django.urls import path

from .views import (ArticleAPIView, SpecificArticle)

app_name = "blog"

urlpatterns = [
    path('blog/', ArticleAPIView.as_view(), name="blog"),
    path('blog/<str:slug>/', SpecificArticle.as_view(),
         name="specific/blog"),
    path('blog/<str:slug>/',
         SpecificArticle.as_view(), name="specific_article"),
]
