from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Robot
from orders.models import Order
from R4C import settings


@receiver(post_save, sender=Robot)
def notify_customers_when_robot_available(sender, instance, created, **kwargs):
    if created:
        try:
            orders = Order.objects.filter(robot_serial=instance.serial, is_waiting=True)

            for order in orders:
                try:
                    customer = order.customer

                    send_email_to_customer(customer, instance)

                    order.is_fulfilled = True
                    order.is_waiting = False
                    order.save()

                except Exception as e:
                    print(f"Error sending email to {order.customer}: {e}")
                    order.refresh_from_db()
        except Exception as e:
            print(f"Error: {e}")


def send_email_to_customer(customer, robot):
    subject = f"Робот {robot.model} {robot.version} теперь в наличии"
    message = f"Добрый день!\n\nНедавно вы интересовались нашим роботом модели " \
              f"{robot.model}, версии {robot.version}." \
              f"\nЭтот робот теперь в наличии. " \
              f"Если вам подходит этот вариант - пожалуйста, свяжитесь с нами."

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [customer.email],
    )
