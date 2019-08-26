import datetime as dt
import json
import os
import random
import re
from datetime import datetime, timedelta

import django
from django.core.mail import send_mail
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string

from royalframes.apps.authentication.utils import status_codes, swagger_body
from royalframes.apps.core.pagination import PaginateContent
from drf_yasg import openapi
from drf_yasg.inspectors import SwaggerAutoSchema
from drf_yasg.utils import swagger_auto_schema, swagger_serializer_method
from rest_framework import exceptions, generics, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.views import Response

from .models import Article, User
from .renderers import ArticleJSONRenderer
from .serializers import ArticleSerializer


class ArticleAPIView(generics.ListCreateAPIView):
    """
        Article endpoints
    """
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    def post(self, request):
        """
            POST /api/v1/articles/
        """
        permission_classes = (IsAuthenticated,)
        context = {"request": request}
        article = request.data.copy()
        article['slug'] = ArticleSerializer(
        ).create_slug(request.data['title'])
        serializer = self.serializer_class(data=article, context=context)
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def get(self, request):
        """
            GET /api/v1/articles/
        """
        perform_pagination = PaginateContent()
        objs_per_page = perform_pagination.paginate_queryset(
            self.queryset, request)
        serializer = ArticleSerializer(
            objs_per_page,
            context={
                'request': request
            },
            many=True
        )
        return perform_pagination.get_paginated_response(serializer.data)


class SpecificArticle(generics.RetrieveUpdateDestroyAPIView):
    """
        Specific article endpoint class
    """
    serializer_class = ArticleSerializer

    def get(self, request, slug, *args, **kwargs):
        """
            GET /api/v1/articles/<slug>/
        """
        try:
            article = Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            raise exceptions.NotFound({
                "message": 'not_found'
            })
        # this checks if an istance of read exists
        # if it doesn't then it creates a new one
        serializer = ArticleSerializer(
            article,
            context={
                'request': request
            }
        )
        return Response(serializer.data, status=200)

    def delete(self, request, slug, *args, **kwargs):
        """
            DELETE /api/v1/articles/<slug>/
        """
        permission_classes = (IsAuthenticated,)
        try:
            article = Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            raise exceptions.NotFound({
                "message": 'not_found'
            })
        article.delete()
        return Response({
            "article": 'article_delete'
        }, status=204)

    def put(self, request, slug, *args, **kwargs):
        """
            PUT /api/v1/articles/<slug>/
        """
        permission_classes = (IsAuthenticated,)
        article = get_object_or_404(Article.objects.all(), slug=slug)
        article_data = request.data
        article.updated_at = dt.datetime.utcnow()
        serializer = ArticleSerializer(
               instance=article,
               data=article_data,
               context={'request': request},
               partial=True
               )
        if serializer.is_valid():
                serializer.save()
                return Response(
                    [
                        serializer.data,
                        {"message": 'article_update'}
                    ], status=201
                )
        else:
            return Response(
                    serializer.errors,
                    status=400
                )


def get_article(slug):
    """
        Returns specific article using slug
    """
    article = Article.objects.all().filter(slug=slug).first()
    if article is None:
        raise exceptions.NotFound({
            "message": 'not_found'
        }, status.HTTP_404_NOT_FOUND)
    return article

