import os
from rest_framework import status
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orders.settings')
django.setup()
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token


class AccountTests(APITestCase):

    def test_create_user(self):
        """
        Ensure we can create a new account object.
        """
        create_url = 'http://127.0.0.1:8000/api/v1/user/register/'
        data = {
            "surname": "Filippov",
            "name": "Aleksander",
            "patronymic": "Nicolaevich",
            "email": "sash.f@mail.ru",
            "password": "Daiojkghrth86g",
            "password_rep": "Daiojkghrth86g",
            "company": "techconsur",
            "position": "manager",
            "type": "shop"}
        response = self.client.post(create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_autorization(self):
        """
        Ensure we can get token account object.
        """
        url = 'http://127.0.0.1:8000/api/v1/user/login/'
        data = {
            "email": "sash.f@mail.ru",
            "password": "Daiojkghrth86g",
            }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = Token.objects.get(user=1)
        print(token)

    def test_create_contact(self):
        """
        Create contact user.
        """
        token = Token.objects.get(user__id=2)
        url = 'http://127.0.0.1:8000/api/v1/user/contact/'
        data = {
            "type": "buyer",
            "value": "gto",
            "city": "NN",
            "street": "Kerchenskaya",
            "phone": "89102362565"
            }
        response = self.client.post(url, data, format='json', HTTP_AUTHORIZATION='Token ' + token.key)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_contact(self):
        """
        Delete contact user.
        """
        token = Token.objects.get(user__id=2)
        url = 'http://127.0.0.1:8000/api/v1/user/contact/'
        response = self.client.delete(url, HTTP_AUTHORIZATION='Token ' + token.key)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_contact(self):
        """
        Get contact user.
        """
        token = Token.objects.get(user__id=2)
        url = 'http://127.0.0.1:8000/api/v1/user/contact/'
        response = self.client.get(url, HTTP_AUTHORIZATION='Token ' + token.key)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_put_contact(self):
        """
        PUT contact user.
        """

        token = Token.objects.get(user__id=2)
        url = 'http://127.0.0.1:8000/api/v1/user/contact/'
        data = {
            "type": "buyer",
            "value": "gto",
            "city": "NN3",
            "street": "Kerchenskaya",
            "phone": "89102362565"
            }
        response = self.client.put(url, data, format='json', HTTP_AUTHORIZATION='Token ' + token.key)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_post_price(self):
    #     """
    #     POST price shop.
    #     """
    #
    #     token = Token.objects.get(user__id=2)
    #     url = 'http://127.0.0.1:8000/api/v1/partner/update/'
    #     with open('/home/aleksander/python-final-diplom/data/shop1.yaml') as data_shop:
    #         data = yaml.load(data_shop, Loader=yaml.FullLoader)
    #     print(data)
        # response = self.client.post(url, data, format='json', HTTP_AUTHORIZATION='Token ' + token.key)
        # self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_shop(self):
        """
        Create shop.
        """

        token = Token.objects.get(user__id=6)
        url = 'http://127.0.0.1:8000/api/v1/shop/'
        print(token)
        data = {
            "name": "eldorado3",
            "url": "https://www.eldorado.ru"
            }
        response = self.client.post(url, data, format='json', HTTP_AUTHORIZATION='Token ' + token.key)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_shop(self):
        """
        Get shop data.
        """
        token = Token.objects.get(user__id=6)
        url = 'http://127.0.0.1:8000/api/v1/shop/'
        print(token)
        response = self.client.get(url, HTTP_AUTHORIZATION='Token ' + token.key)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_shop(self):
        """
        Update status shop.
        """
        token = Token.objects.get(user__id=6)
        url = 'http://127.0.0.1:8000/api/v1/shop/2/'
        print(token)
        data = {
            "state": "true"
            }
        response = self.client.patch(url, data, format='json',  HTTP_AUTHORIZATION='Token ' + token.key)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_state_shop(self):
        """
        Get status shop.
        """
        token = Token.objects.get(user__id=6)
        url = 'http://127.0.0.1:8000/api/v1/shop/2/state/'
        print(token)

        response = self.client.get(url, HTTP_AUTHORIZATION='Token ' + token.key)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_category(self):
        """
        Create category.
        """
        token = Token.objects.get(user__id=6)
        url = 'http://127.0.0.1:8000/api/v1/category/'
        print(token)
        data = {
            "name": "electronocs"
            }
        response = self.client.post(url, data, format='json',  HTTP_AUTHORIZATION='Token ' + token.key)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # def test_create_product(self):
    #     """
    #     Create product ().
    #     """
    #     token = Token.objects.get(user__id=6)
    #     url = 'http://127.0.0.1:8000/api/v1/products/write/'
    #     data = {
    #         "model": "Samsung25545",
    #         "name": "Phone",
    #         "shop": 2,
    #         "category": 2,
    #         "quantity": 2,
    #         "price": 50,
    #         "price_rrc": 55
    #     }
    #     response = self.client.post(url, data, format='json',  HTTP_AUTHORIZATION='Token ' + token.key)
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_products(self):
        """
        Get list products.
        """
        token = Token.objects.get(user__id=6)
        url = 'http://127.0.0.1:8000/api/v1/products/'
        print(token)
        response = self.client.get(url, HTTP_AUTHORIZATION='Token ' + token.key)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_product(self):
        """
        Get poduct in category.
        """
        token = Token.objects.get(user__id=6)
        url = 'http://127.0.0.1:8000/api/v1/products/?category=224&shop=1'
        print(token)
        response = self.client.get(url, HTTP_AUTHORIZATION='Token ' + token.key)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_basket(self):
        """
        Create basket with product.
        """
        token = Token.objects.get(user__id=8)
        url = 'http://127.0.0.1:8000/api/v1/basket/'
        print(token)
        data = {
            "product_id": 2,
            "shop_id": 1,
            "quantity": 0
        }
        response = self.client.post(url, data, format='json',  HTTP_AUTHORIZATION='Token ' + token.key)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_delete_basket(self):
        """
        Delete basket with product.
        """
        token = Token.objects.get(user__id=8)
        url = 'http://127.0.0.1:8000/api/v1/basket/9/'
        print(token)
        response = self.client.delete(url, HTTP_AUTHORIZATION='Token ' + token.key)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # def test_create_order(self):
    #     """
    #     Create order with product.
    #     """
    #     token = Token.objects.get(user__id=8)
    #     url = 'http://127.0.0.1:8000/api/v1/order/'
    #     print(token)
    #
    #     response = self.client.post(url, HTTP_AUTHORIZATION='Token ' + token.key)
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_order(self):
        """
        Get order with product.
        """
        token = Token.objects.get(user__id=8)
        url = 'http://127.0.0.1:8000/api/v1/order/4/'
        print(token)
        response = self.client.get(url, HTTP_AUTHORIZATION='Token ' + token.key)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_orders(self):
        """
        Get all orders.
        """
        token = Token.objects.get(user__id=8)
        url = 'http://127.0.0.1:8000/api/v1/order/'
        print(token)
        response = self.client.get(url, HTTP_AUTHORIZATION='Token ' + token.key)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch_orders(self):
        """
        Patch status order.
        """
        token = Token.objects.get(user__id=2)
        url = 'http://127.0.0.1:8000/api/v1/order/4/'
        print(token)
        data = {
            "status": "sent"
        }
        response = self.client.patch(url, data, format='json',  HTTP_AUTHORIZATION='Token ' + token.key)
        self.assertEqual(response.status_code, status.HTTP_200_OK)











