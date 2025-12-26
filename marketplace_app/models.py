from django.db import models
from django.conf import settings


class Offer(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='offers')
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='offers/', blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def min_price(self):
        """Gibt den niedrigsten Preis aller Details zurück"""
        details = self.details.all()
        if details:
            return min(detail.price for detail in details)
        return None

    @property
    def min_delivery_time(self):
        """Gibt die kürzeste Lieferzeit aller Details zurück"""
        details = self.details.all()
        if details:
            return min(detail.delivery_time_in_days for detail in details)
        return None


class OfferDetail(models.Model):
    OFFER_TYPE_CHOICES = [
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
    ]
    
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='details')
    title = models.CharField(max_length=255)
    revisions = models.PositiveIntegerField()
    delivery_time_in_days = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list)
    offer_type = models.CharField(max_length=20, choices=OFFER_TYPE_CHOICES)

    def __str__(self):
        return f'{self.offer.title} - {self.title}'

class Order(models.Model):
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    offer_detail = models.ForeignKey(OfferDetail, on_delete=models.CASCADE, related_name='orders') 
    status = models.CharField(max_length=30, default='in_progress')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return f'Order #{self.id} - {self.offer_detail.title}'

class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review {self.rating} by {self.user}'
