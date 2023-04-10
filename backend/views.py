from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.validators import URLValidator
from django.db import IntegrityError
from django.db.models import Sum
import yaml
from rest_framework.decorators import action
from yaml import load as load_yaml, Loader
from requests import get
from rest_framework import status
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.authtoken.models import Token
from backend.models import Category, Product, Shop, ConfirmEmailToken, Order, Basket, Contact, ProductParameter
from backend.serializers import RegistrationSerializer, CategorySerializer, ProductSerializer, ShopSerializer, \
    OrderSerializer, BasketSerializer, ContactSerializer, OrderItemSerializer
from django.http import JsonResponse
from backend.signals import new_user_registered, new_order


class RegisterAccount(APIView):
    """
    Для регистрации покупателей
    """

    # Регистрация методом POST
    def post(self, request, *args, **kwargs):

        # проверяем обязательные аргументы
        if {'surname', 'name', 'patronymic', 'email', 'password', 'password_rep'}.issubset(request.data):
            errors = {}
            if self.request.data.get('password') != self.request.data.get('password_rep'):
                raise ValidationError({'Status': False, 'Errors': "You must confirm your password"})
            # проверяем пароль на сложность
            try:
                validate_password(request.data['password'])
            except Exception as password_error:
                error_array = []
                for item in password_error:
                    error_array.append(item)
                return JsonResponse({'Status': False, 'Errors': {'password': error_array}})
            else:
                # проверяем данные для уникальности имени пользователя
                request.data.update({})
                user_serializer = RegistrationSerializer(data=request.data)
                if user_serializer.is_valid():
                    # сохраняем пользователя
                    user = user_serializer.save()
                    user.set_password(request.data.get('password'))
                    user.save()
                    try:
                        new_user_registered.send(sender=self.__class__, user_id=user.id)
                    except:
                        raise PermissionDenied({'Status': True, 'Errors': 'Error sending mail'})
                    return JsonResponse({'Status': True})
                else:
                    return JsonResponse({'Status': False, 'Errors': user_serializer.errors})

        return JsonResponse({'Status': False, 'Errors': 'All necessary arguments are not specified'})


class ConfirmAccount(APIView):
    """
    Класс для подтверждения почтового адреса
    """

    # Регистрация методом POST
    def post(self, request, *args, **kwargs):
        # проверяем обязательные аргументы
        if {'email', 'token'}.issubset(request.data):

            token = ConfirmEmailToken.objects.filter(user__email=request.data.get('email'),
                                                     key=request.data.get('token')).first()
            if token:
                # token.user.is_active = True
                token.user.save()
                token.delete()
                return JsonResponse({'Status': True})
            else:
                return JsonResponse({'Status': False, 'Errors': 'Неправильно указан токен или email'})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class AccountDetails(APIView):
    """
    Класс для работы данными пользователя
    """

    # получить данные
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        serializer = RegistrationSerializer(request.user)
        return Response(serializer.data)

    # Редактирование методом POST
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        # проверяем обязательные аргументы

        if 'password' in request.data:
            errors = {}
            # проверяем пароль на сложность
            try:
                validate_password(request.data.get('password'))
            except Exception as password_error:
                error_array = []
                # noinspection PyTypeChecker
                for item in password_error:
                    error_array.append(item)
                return JsonResponse({'Status': False, 'Errors': {'password': error_array}})
            else:
                request.user.set_password(request.data.get('password'))

        # проверяем остальные данные
        user_serializer = RegistrationSerializer(request.user, data=request.data, partial=True)
        if user_serializer.is_valid():
            user_serializer.save()
            return JsonResponse({'Status': True})
        else:
            return JsonResponse({'Status': False, 'Errors': user_serializer.errors})


class LoginAccount(APIView):
    """
    Класс для авторизации пользователей (сделано)
    """

    # Авторизация методом POST
    def post(self, request, *args, **kwargs):
        if {'email', 'password'}.issubset(request.data):
            user = authenticate(request, username=request.data.get('email'), password=request.data.get('password'))
            if user is not None:
                # if user.is_active:
                token, _ = Token.objects.get_or_create(user=user)
                return JsonResponse({'Status': True, 'Token': token.key})
            return JsonResponse({'Status': False, 'Errors': 'Failed to authorize'})
        return JsonResponse({'Status': False, 'Errors': 'All necessary arguments are not specified'})


class CategoryViewSet(ModelViewSet):
    """
    Класс для просмотра категорий (сделано)
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if request.user.is_authenticated and request.user.type == 'shop':
            self.perform_create(serializer)
        else:
            raise PermissionDenied('Buyer not create category')

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ShopViewSet(ModelViewSet):
    """
    Класс для просмотра списка магазинов (сделано)
    """
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer

    @action(methods=['GET'], detail=True)
    def state(self, request, pk=None):
        shops = Shop.objects.get(pk=pk)
        return Response({'state': shops.state})

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user.id)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if request.user.is_authenticated and request.user.type == 'shop':
            self.perform_create(serializer)
        else:
            raise PermissionDenied('Buyer not create or update shop')

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ProductViewSet(ModelViewSet):
    """
    Класс для просмотра и создания списка продуктов
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filterset_fields = ['category', 'shop']


class BasketViewSet(ModelViewSet):
    """
    Класс для добавления в корзину продуктов
    """
    queryset = Basket.objects.all()
    serializer_class = BasketSerializer

    def perform_create(self, serializer):
        product_price = Product.objects.values().filter(id=self.request.data.get('product_id'))[0].get('price')
        sum_prise_product = product_price*self.request.data.get('quantity')
        serializer.save(user_id=self.request.user.id, sum_prise_product=sum_prise_product)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if request.user.is_authenticated and request.user.type == 'buyer':
            shop_state = Shop.objects.values().filter(id=self.request.data.get('shop_id'))[0].get('state')
            if shop_state:
                quantity_product = Product.objects.values().filter(id=self.request.data.get('product_id'))[0].get(
                    'quantity')
                if quantity_product >= self.request.data.get('quantity'):
                    try:
                        self.perform_create(serializer)
                    except:
                        raise PermissionDenied('This product is already in the cart')
                else:
                    raise PermissionDenied('Insufficient quantity of goods in stock, reduce the quantity of goods')
            else:
                raise PermissionDenied('Shop state not True')
        else:
            raise PermissionDenied('Shop not create basket')

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class OrderViewSet(ModelViewSet):
    """
    Класс для получения и размещения заказов пользователями (сделан кроме суммы и обновления статуса )
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def create(self, request, *args, **kwargs):
        global serializer
        if request.user.is_authenticated and request.user.type == 'buyer':
            basket_user = Basket.objects.values().filter(user_id=self.request.user.id)
            contact = Contact.objects.values().filter(user_id=self.request.user.id)
            if basket_user and contact:
                for item in basket_user:
                    serializer = self.get_serializer(data=request.data)
                    serializer.is_valid(raise_exception=True)
                    serializer.save(user_id=self.request.user.id,
                                    quantity=item.get('quantity'),
                                    contact_id=contact[0].get('id'),
                                    product_id=item.get('product_id'),
                                    shop_id=item.get('shop_id'),
                                    sum_prise_product=item.get('sum_prise_product')
                                    )
                order_product = Basket.objects.values().filter(user_id=self.request.user.id)
                for order in order_product:
                    products = Product.objects.values().filter(id=order.get('product_id'))
                    for product in products:
                        difference = product.get('quantity') - order.get('quantity')
                        Product.objects.values().filter(id=order.get('product_id')).update(quantity=difference)
                Basket.objects.filter(user_id=self.request.user.id).delete()
            else:
                raise PermissionDenied('The basket is empty or not contact user')
        else:
            raise PermissionDenied('Shop not create order')

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def list(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.type == 'buyer':
            order = Order.objects.filter(user_id=self.request.user.id)
            order_sum = Order.objects.filter(user_id=self.request.user.id).aggregate(
                total_sum_order=Sum('sum_prise_product'))
            serializer = OrderSerializer(order, many=True)
            return Response({'Total_sum_order': order_sum.get("total_sum_order"), 'orders': serializer.data},
                            status=status.HTTP_200_OK)
        elif request.user.is_authenticated and request.user.type == 'shop':
            order = Order.objects.filter(shop_id=self.request.user.id)
            order_sum = Order.objects.filter(user_id=self.request.user.id).aggregate(
                total_sum_order=Sum('sum_prise_product'))
            serializer = OrderSerializer(order, many=True)
            return Response({'Total_sum_order': order_sum.get("total_sum_order"), 'orders': serializer.data},
                            status=status.HTTP_200_OK)

    def perform_update(self, serializer):
        request = self.request
        if request.user.is_authenticated and request.user.type == 'shop':
            shop_id = Shop.objects.values().filter(user_id=self.request.user.id)[0].get('id')
            try:
                order_shop_id = Order.objects.values().filter(id=self.request.parser_context.get('kwargs').get('pk'))[0] \
                    .get('shop_id')
                if shop_id == order_shop_id:
                    serializer.save(status=self.request.data.get('status'))
                    new_order.send(sender=self.__class__, user_id=request.user.id)
                    return Response(status=status.HTTP_200_OK)
                else:
                    raise PermissionDenied('The order is not for your store')
            except IndexError as error:
                raise PermissionDenied(error)
        else:
            raise PermissionDenied("You don't have the rights to edit the order")

    def retrieve(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.type == 'buyer':
            order = Order.objects.filter(user_id=self.request.user.id).\
                filter(id=self.request.parser_context.get('kwargs').get('pk'))
            serializer = OrderItemSerializer(order, many=True)
            return Response({'orders': serializer.data}, status=status.HTTP_200_OK)
        elif request.user.is_authenticated and request.user.type == 'shop':
            order = Order.objects.filter(shop_id=self.request.user.id).\
                filter(id=self.request.parser_context.get('kwargs').get('pk'))
            serializer = OrderItemSerializer(order, many=True)
            return Response({'orders': serializer.data}, status=status.HTTP_200_OK)


class PartnerUpdate(APIView):
    """
    Класс для обновления прайса от поставщика
    """
    def shop_data_post(self, request, *args, **kwargs):
        url = request.data.get('url')
        if url:
            validate_url = URLValidator()
            try:
                validate_url(url)
            except ValidationError as e:
                return JsonResponse({'Status': False, 'Error': str(e)})
            else:
                try:
                    stream = get(url).content
                    data = load_yaml(stream, Loader=Loader)
                except:
                    with open('./data/shop1.yaml') as data_shop:
                        data = yaml.load(data_shop, Loader=yaml.FullLoader)
                return data

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if request.user.type != 'shop':
            return JsonResponse({'Status': False, 'Error': 'Only for stores'}, status=403)
        # url = request.data.get('url')
        # print(url)
        # if url:
        #     validate_url = URLValidator()
        #     try:
        #         validate_url(url)
        #     except ValidationError as e:
        #         return JsonResponse({'Status': False, 'Error': str(e)})
        #     else:
        #         stream = get(url).content
        #         data = load_yaml(stream, Loader=Loader)

        # with open('shop.yaml') as data_shop:
        #     data = yaml.load(data_shop, Loader=yaml.FullLoader)

        data = self.shop_data_post(request, *args, **kwargs)
        shop, _ = Shop.objects.get_or_create(name=data.get('shop'), user_id=request.user.id)
        try:
            for category in data.get('categories'):
                category_object, _ = Category.objects.get_or_create(id=category['id'], name=category.get('name'))
            for item in data.get('goods'):
                product, _ = Product.objects.get_or_create(model=item.get('model'),
                                                           name=item.get('name'),
                                                           quantity=item.get('quantity'),
                                                           price=item.get('price'),
                                                           price_rrc=item.get('price_rrc'),
                                                           category_id=item.get('category'),
                                                           shop_id=shop.id,
                                                           )

                for name, value in item.get('parameters').items():
                    product_parameter, _ = ProductParameter.objects.get_or_create(name=name,
                                                                                  value=value,
                                                                                  product_id=product.id)
        except IntegrityError as error:
            raise PermissionDenied(error)
        return JsonResponse({'Status': True})

        # return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class ContactView(APIView):
    """
    Класс для работы с контактами покупателей (в принципе рабочий, можно переписать)
    """

    # получить мои контакты
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        contact = Contact.objects.filter(
            user_id=request.user.id)
        serializer = ContactSerializer(contact, many=True)
        return Response(serializer.data)

    # добавить новый контакт
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if {'city', 'street', 'phone'}.issubset(request.data):
            contact = Contact.objects.filter(user_id=self.request.user.id)
            if not contact:
                request.data.update({'user': request.user.id})
                serializer = ContactSerializer(data=request.data)

                if serializer.is_valid():
                    serializer.save()
                    return JsonResponse({'Status': True})
                else:
                    JsonResponse({'Status': False, 'Errors': serializer.errors})
            else:
                return JsonResponse({'Status': False, 'Errors': 'This contact exists'})
        return JsonResponse({'Status': False, 'Errors': 'All necessary arguments are not specified'})

    # удалить контакт
    def delete(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        delete_contact = Contact.objects.filter(user_id=self.request.user.id)
        if delete_contact:
            delete_contact.delete()
            return JsonResponse({'Status': True})
        else:
            return JsonResponse({'Status': False, 'Error': 'Contact not found'})

    # редактировать контакт
    def put(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        contact = Contact.objects.filter(user_id=self.request.user.id).first()
        if contact:
            serializer = ContactSerializer(contact, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse({'Status': True})
            else:
                JsonResponse({'Status': False, 'Errors': serializer.errors})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})
