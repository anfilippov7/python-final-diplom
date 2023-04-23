from rest_framework import serializers
from backend.models import User, Category, Product, Shop, Order, Contact, Basket, ProductParameter


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ('city', 'street', 'house', 'structure', 'building', 'apartment', 'user', 'phone')
        read_only_fields = ('id',)
        extra_kwargs = {
            'user': {'write_only': True}
        }


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('surname', 'name', 'patronymic', 'email', 'password', 'password_rep',
                  'company', 'position', 'type')
        read_only_fields = ('id',)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name',)
        read_only_fields = ('id',)


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ('name', 'url', 'state', 'is_active', 'user')
        read_only_fields = ('id',)


class ProductParameterSerializer(serializers.ModelSerializer):
    parameter = serializers.StringRelatedField()

    class Meta:
        model = ProductParameter
        fields = ('name', 'value', 'parameter')
        read_only_fields = ('id',)


class ProductSerializer(serializers.ModelSerializer):
    parameter = ProductParameterSerializer(read_only=True, many=True)
    shop = serializers.StringRelatedField()
    category = serializers.StringRelatedField()

    class Meta:
        model = Product
        fields = ('name', 'shop', 'category', 'quantity', 'price', 'price_rrc', 'parameter')
        read_only_fields = ('id',)


class BasketSerializer(serializers.ModelSerializer):
    shop = ShopSerializer(read_only=True)
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Basket
        fields = ('id', 'product', 'shop', 'quantity', 'shop_id', 'product_id')
        read_only_fields = ('id',)
        extra_kwargs = {
            'shop_id': {'source': 'shop', 'write_only': True},
            'product_id': {'source': 'product', 'write_only': True},
        }


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ('id', 'dt', 'status')
        read_only_fields = ('id', 'sum_price_product')


class OrderItemSerializer(serializers.ModelSerializer):
    contact = serializers.StringRelatedField()
    product = serializers.StringRelatedField()

    class Meta:
        model = Order
        fields = ('sum_price_product', 'dt', 'status', 'product', 'contact', )
        read_only_fields = ('id',)
        extra_kwargs = {
            'order': {'write_only': True}
        }
