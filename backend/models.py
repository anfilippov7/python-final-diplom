from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_rest_passwordreset.tokens import get_token_generator
from django.contrib.auth.base_user import BaseUserManager

STATE_CHOICES = (
    ('basket', 'Статус корзины'),
    ('new', 'Новый'),
    ('confirmed', 'Подтвержден'),
    ('assembled', 'Собран'),
    ('sent', 'Отправлен'),
    ('delivered', 'Доставлен'),
    ('canceled', 'Отменен'),
)

USER_TYPE_CHOICES = (
    ('shop', 'Магазин'),
    ('buyer', 'Покупатель'),
)


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Users require an email field')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):

    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'email'
    username_validator = UnicodeUsernameValidator()

    objects = UserManager()

    username = None
    first_name = None
    last_name = None
    surname = models.CharField(_('Фамилия'), max_length=50,
                               help_text=_('Required. 50 characters or fewer. Letters, digits and @/./+/-/_ only.'),
                               validators=[username_validator],
                               error_messages={
                                   'unique': _("A user with that surname already exists."),
                               }
                               )
    name = models.CharField(_('Имя'), max_length=50,
                            help_text=_('Required. 50 characters or fewer. Letters, digits and @/./+/-/_ only.'),
                            validators=[username_validator],
                            error_messages={
                                'unique': _("A user with that name already exists."),
                            }
                            )
    patronymic = models.CharField(_('Отчество'), max_length=50,
                                  help_text=_('Required. 50 characters or fewer. Letters, digits and @/./+/-/_ only.'),
                                  validators=[username_validator],
                                  error_messages={
                                      'unique': _("A user with that patronymic already exists."),
                                  }
                                  )
    email = models.EmailField(_('email адрес'), unique=True)
    password = models.CharField(verbose_name='Пароль', max_length=100)
    password_rep = models.CharField(verbose_name='Пароль (повтор)', max_length=100)
    company = models.CharField(verbose_name='Компания', max_length=50, blank=True)
    position = models.CharField(verbose_name='Должность', max_length=50, blank=True)
    type = models.CharField(verbose_name='Тип пользователя', choices=USER_TYPE_CHOICES, max_length=5, default='buyer')

    def __str__(self):
        return f'{self.email} {self.password}'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Список пользователей'
        ordering = ('email',)


class Shop(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название')
    url = models.URLField(verbose_name='Ссылка', null=True, blank=True)
    user = models.OneToOneField(User, verbose_name='Пользователь',
                                blank=True, null=True,
                                on_delete=models.CASCADE)
    state = models.BooleanField(verbose_name='статус работы магазина', default=True)

    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Список магазинов'
        ordering = ('-name',)

    def __str__(self):
        return f'{self.name} {self.id}'


class Category(models.Model):
    name = models.CharField(max_length=80, verbose_name='Название')
    shops = models.ManyToManyField(Shop, verbose_name='Магазины', related_name='categories')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Список категорий'
        ordering = ('-name',)

    def __str__(self):
        return self.name


class Product(models.Model):
    model = models.CharField(max_length=80, verbose_name='Модель', blank=True)
    name = models.CharField(max_length=80, verbose_name='Название продукта')
    category = models.ForeignKey(Category, verbose_name='Категория', related_name='products', on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, verbose_name='Магазин', related_name='products', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    price = models.PositiveIntegerField(verbose_name='Цена')
    price_rrc = models.PositiveIntegerField(verbose_name='Рекомендуемая розничная цена')

    class Meta:
        verbose_name = 'Информация о продукте'
        verbose_name_plural = 'Информационный список о продуктах'
        constraints = [
            models.UniqueConstraint(fields=['name', 'shop', 'price'], name='unique_product_info'),
        ]

    def __str__(self):
        return f'name: {self.name}, shop: {self.shop}'


class ProductParameter(models.Model):
    product = models.ForeignKey(Product, verbose_name='Информация о продукте',
                                related_name='product_parameters', blank=True,
                                on_delete=models.CASCADE)
    name = models.CharField(max_length=40, verbose_name='Название')
    value = models.CharField(verbose_name='Значение', max_length=100)

    class Meta:
        verbose_name = 'Параметр'
        verbose_name_plural = "Список параметров"
        constraints = [
            models.UniqueConstraint(fields=['product', 'name'], name='unique_product_parameter'),
        ]


class Basket(models.Model):
    product = models.ForeignKey(Product, verbose_name='Выбор продуктов для заказа', related_name='baskets',
                                on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, verbose_name='Выбор магазинов для заказа', related_name='baskets',
                             on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    user = models.ForeignKey(User, verbose_name='Пользователь',
                             related_name='baskets', on_delete=models.CASCADE)
    sum_price_product = models.PositiveIntegerField(verbose_name='Суммарная стоимость позиции')
    shop_email = models.EmailField(_('email адрес магазина'), default='sash31.f@mail.ru')

    class Meta:
        verbose_name = 'Заказанная позиция'
        verbose_name_plural = 'Заказанная позиция'
        constraints = [
            models.UniqueConstraint(fields=['shop', 'product'], name='unique_order_item'),
        ]

    def __str__(self):
        return str(self.product)


class Contact(models.Model):
    user = models.ForeignKey(User, verbose_name='Пользователь',
                             related_name='contacts', blank=True,
                             on_delete=models.CASCADE)
    type = models.CharField(max_length=50, verbose_name='Тип')
    value = models.CharField(max_length=50, verbose_name='Значение')
    city = models.CharField(max_length=50, verbose_name='Город')
    street = models.CharField(max_length=100, verbose_name='Улица')
    house = models.CharField(max_length=15, verbose_name='Дом', blank=True)
    structure = models.CharField(max_length=15, verbose_name='Корпус', blank=True)
    building = models.CharField(max_length=15, verbose_name='Строение', blank=True)
    apartment = models.CharField(max_length=15, verbose_name='Квартира', blank=True)
    phone = models.CharField(max_length=20, verbose_name='Телефон')

    class Meta:
        verbose_name = 'Контакты пользователя'
        verbose_name_plural = 'Список контактов пользователя'

    def __str__(self):
        return f'city: {self.city}, street: {self.street}, house: {self.house}, phone: {self.phone}'


class Order(models.Model):
    user = models.ForeignKey(User, verbose_name='Пользователь', related_name='orders', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name='Продукты в заказе', related_name='orders',
                                on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, verbose_name='Магазины для заказе', related_name='orders',
                             on_delete=models.CASCADE)
    dt = models.DateTimeField(auto_now_add=True)
    status = models.CharField(verbose_name='Статус', choices=STATE_CHOICES, default='new', max_length=15)
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    contact = models.ForeignKey(Contact, verbose_name='Контакт', on_delete=models.CASCADE)
    sum_price_product = models.PositiveIntegerField(verbose_name='Суммарная стоимость позиции')
    shop_email = models.EmailField(_('email адрес магазина'), default='sash31.f@mail.ru')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Список заказов'
        ordering = ('-dt',)

    def __str__(self):
        return str(self.dt)


class ConfirmEmailToken(models.Model):
    class Meta:
        verbose_name = 'Токен подтвеждения Email'
        verbose_name_plural = 'Токены подтвеждения Email'

    @staticmethod
    def generate_key():
        """ generates a pseudo random code using os.urandom and binascii.hexlify """
        return get_token_generator().generate_token()

    user = models.ForeignKey(
        User,
        related_name='confirm_email_tokens',
        on_delete=models.CASCADE,
        verbose_name=_("The User which is associated to this password reset token")
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("When was this token generated")
    )

    # Key field, though it is not the primary key of the model
    key = models.CharField(
        _('Key'),
        max_length=64,
        db_index=True,
        unique=True
    )

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(ConfirmEmailToken, self).save(*args, **kwargs)

    def __str__(self):
        return "Password reset token for user {user}".format(user=self.user)
