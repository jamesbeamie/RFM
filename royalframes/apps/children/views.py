from django.shortcuts import render

# Create your views here.
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

from .models import Children, User
from .renderers import ChildrenJSONRenderer
from .serializers import ChildrenSerializer


class ChildrenAPIView(generics.ListCreateAPIView):
    """
        children endpoints
    """
    queryset = Children.objects.all()
    serializer_class = ChildrenSerializer

    def post(self, request):
        """
            POST /api/v1/childrens/
        """
        permission_classes = (IsAuthenticated,)
        context = {"request": request}
        children = request.data.copy()
        children['slug'] = ChildrenSerializer(
        ).create_slug(request.data['title'])
        serializer = self.serializer_class(data=children, context=context)
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
            GET /api/v1/childrens/
        """
        perform_pagination = PaginateContent()
        objs_per_page = perform_pagination.paginate_queryset(
            self.queryset, request)
        serializer = ChildrenSerializer(
            objs_per_page,
            context={
                'request': request
            },
            many=True
        )
        return perform_pagination.get_paginated_response(serializer.data)


class SpecificChild(generics.RetrieveUpdateDestroyAPIView):
    """
        Specific children endpoint class
    """
    serializer_class = ChildrenSerializer

    def get(self, request, slug, *args, **kwargs):
        """
            GET /api/v1/childrens/<slug>/
        """
        try:
            children = Children.objects.get(slug=slug)
        except Children.DoesNotExist:
            raise exceptions.NotFound({
                "message": 'not_found'
            })
        # this checks if an istance of read exists
        # if it doesn't then it creates a new one
        serializer = ChildrenSerializer(
            children,
            context={
                'request': request
            }
        )
        return Response(serializer.data, status=200)

    def delete(self, request, slug, *args, **kwargs):
        """
            DELETE /api/v1/childrens/<slug>/
        """
        permission_classes = (IsAuthenticated,)
        try:
            children = Children.objects.get(slug=slug)
        except Children.DoesNotExist:
            raise exceptions.NotFound({
                "message": 'not_found'
            })
        children.delete()
        return Response({
            "children": 'deleted'
        }, status=204)

    def put(self, request, slug, *args, **kwargs):
        """
            PUT /api/v1/childrens/<slug>/
        """
        permission_classes = (IsAuthenticated,)
        children = get_object_or_404(Children.objects.all(), slug=slug)
        children_data = request.data
        children.updated_at = dt.datetime.utcnow()
        serializer = ChildrenSerializer(
            instance=children,
            data=children_data,
            context={'request': request},
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                [
                    serializer.data,
                    {"message": 'children_update'}
                ], status=201
            )
        else:
            return Response(
                serializer.errors,
                status=400
            )


def get_children(slug):
    """
        Returns specific children using slug
    """
    children = Children.objects.all().filter(slug=slug).first()
    if children is None:
        raise exceptions.NotFound({
            "message": 'not_found'
        }, status.HTTP_404_NOT_FOUND)
    return children
