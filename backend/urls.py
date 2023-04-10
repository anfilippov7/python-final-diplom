from django.urls import path
from django_rest_passwordreset.views import reset_password_request_token, reset_password_confirm
from rest_framework.routers import DefaultRouter

from backend.views import RegisterAccount, ConfirmAccount, LoginAccount, CategoryViewSet, ProductViewSet, ShopViewSet, \
    OrderViewSet, BasketViewSet, PartnerUpdate, ContactView

r = DefaultRouter()
r.register('category', CategoryViewSet)
r.register('shop', ShopViewSet)
r.register('products', ProductViewSet)
r.register('products', ProductViewSet)
r.register('order', OrderViewSet)
r.register('basket', BasketViewSet)


app_name = 'backend'
urlpatterns = [
    path('partner/update', PartnerUpdate.as_view(), name='partner-update'),
    path('user/register/', RegisterAccount.as_view(), name='user-register'),
    path('user/register/confirm/', ConfirmAccount.as_view(), name='user-register-confirm'),
    path('user/login/', LoginAccount.as_view(), name='user-login'),
    path('user/register/confirm/', ConfirmAccount.as_view(), name='user-register-confirm'),
    path('user/contact/', ContactView.as_view(), name='user-contact'),
    path('user/password_reset', reset_password_request_token, name='password-reset'),
    path('user/password_reset/confirm', reset_password_confirm, name='password-reset-confirm'),
] + r.urls
