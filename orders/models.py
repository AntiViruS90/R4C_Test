from django.db import models

from customers.models import Customer
from robots.models import Robot


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    robot_serial = models.CharField(max_length=5, blank=False, null=False)
    is_fulfilled = models.BooleanField(default=False)
    is_waiting = models.BooleanField(default=True)

    def __str__(self):
        return f"Order #{self.id} for {self.robot_serial}"
