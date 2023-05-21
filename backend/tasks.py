# feedback/tasks.py

from time import sleep
from django.core.mail import send_mail
from celery import shared_task
from yaml import load as load_yaml, Loader
from requests import get
import yaml


@shared_task()
def send_email_task(email_address, message):
    """Sends an email"""
    sleep(20)  # Simulate expensive operation(s) that freeze Django
    send_mail(
        'Good day',
        f"{message}",
        "support@example.com",
        [email_address],
        fail_silently=False,
    )


@shared_task()
def shop_data_task(url):
    try:
        stream = get(url).content
        data = load_yaml(stream, Loader=Loader)
    except:
        with open('./data/shop1.yaml') as data_shop:
            data = yaml.load(data_shop, Loader=yaml.FullLoader)
    return data
