from django.db import models
from django.conf import settings


class SubscribedProduct(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscribed_products')
    product_id = models.CharField(max_length=255)  # product IDs are CHARACTERS
    product_name = models.CharField(max_length=255)  # To store product name for convenience
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product_name}"
