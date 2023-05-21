from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, extend_schema_view, OpenApiResponse, \
    extend_schema_serializer
from drf_spectacular.types import OpenApiTypes
from rest_framework import status, viewsets
from rest_framework import serializers
from rest_framework.response import Response
from backend.models import Category
from backend.serializers import CategorySerializer


class DummyDetailSerializer(serializers.Serializer):
    status = serializers.IntegerField()


class DummyDetailAndStatusSerializer(serializers.Serializer):
    status = serializers.IntegerField()
    details = serializers.CharField()


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


@extend_schema(summary="Test description of retrieve method")
def retrieve(self, request, *args, **kwargs):

    # some logic

    return Response(status=status.HTTP_200_OK)


def destroy(self, request, *args, **kwargs):
    # третий пример через doc-string

    """Test description of destroy method"""

    return Response(status=status.HTTP_200_OK)

# @extend_schema(tags=["Posts"])
# @extend_schema_view(
#     retrieve=extend_schema(
#         summary="Детальная информация о посте",
#         responses={
#             status.HTTP_200_OK: CategorySerializer,
#             status.HTTP_400_BAD_REQUEST: DummyDetailSerializer,
#             status.HTTP_401_UNAUTHORIZED: DummyDetailSerializer,
#             status.HTTP_403_FORBIDDEN: DummyDetailAndStatusSerializer,
#             status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(
#                 response=None,
#                 description='Описание 500 ответа'),
#         },
#     ),


# update=extend_schema(
#     summary="Изменение существующей категрии",
#     request=CategorySerializer,
#     responses={
#         status.HTTP_200_OK: CategorySerializer,
#         status.HTTP_400_BAD_REQUEST: DummyDetailSerializer,
#         status.HTTP_401_UNAUTHORIZED: DummyDetailSerializer,
#         status.HTTP_403_FORBIDDEN: DummyDetailAndStatusSerializer,
#     },
#     parameters=[
#         OpenApiParameter(
#             name='some_new_parameter',
#             location=OpenApiParameter.QUERY,
#             description='some new parameter for update post',
#             required=False,
#             type=str
#         ),
#     ]
# ),

# create = extend_schema(
#     summary="Создание новой категории",
#     request=CategorySerializer,
#     responses={
#         status.HTTP_200_OK: CategorySerializer,
#         status.HTTP_400_BAD_REQUEST: DummyDetailSerializer,
#         status.HTTP_401_UNAUTHORIZED: DummyDetailSerializer,
#         status.HTTP_403_FORBIDDEN: DummyDetailAndStatusSerializer,
#     },
#     examples=[
#         OpenApiExample(
#             "Post example",
#             description="Test example for the post",
#             value=
#             {
#                 "name": "DNS",
#             },
#             status_codes=[str(status.HTTP_200_OK)],
#         ),
#     ],
# ),


@extend_schema_serializer(
    exclude_fields=('single',),  # schema ignore these fields
    examples=[
        OpenApiExample(
            'Valid example 1',
            summary='short summary',
            description='longer description',
            value={
                'songs': {'top10': True},
                'single': {'top10': True}
            },
            request_only=True,  # signal that example only applies to requests
            response_only=False,  # signal that example only applies to responses
        ),
    ]

)
class CategorySerializer(serializers.ModelSerializer):
    songs = CategorySerializer(many=True)
    single = CategorySerializer(read_only=True)

    class Meta:
        fields = '__all__'
        model = Category


class CategoryViewset(viewsets.ModelViewSet):
    serializer_class = CategorySerializer

    @extend_schema(
        request=CategorySerializer,
        responses={201: CategorySerializer},
    )
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return super().create(request)