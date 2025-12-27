from django.db import models
from django.conf import settings


class Offer(models.Model):
    """
    Represents a marketplace offer created by a user.

    Attributes:
        owner: Reference to the user who created the offer.
        title: Short title of the offer.
        image: Optional image for the offer.
        description: Detailed description of the offer.
        created_at: Timestamp when the offer was created.
        updated_at: Timestamp when the offer was last updated.
    """
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
        """
        Compute the lowest price among all `OfferDetail` entries for this `Offer`.

        Returns:
            Decimal or None: The minimum `price` across related details, or
            `None` if no details exist.
        """
        details = self.details.all()
        if details:
            return min(detail.price for detail in details)
        return None

    @property
    def min_delivery_time(self):
        """
        Compute the shortest delivery time (in days) among related `OfferDetail`s.

        Returns:
            int or None: The minimum `delivery_time_in_days` across related
            details, or `None` if no details exist.
        """
        details = self.details.all()
        if details:
            return min(detail.delivery_time_in_days for detail in details)
        return None


class OfferDetail(models.Model):
    """
    Represents a pricing/detail tier for an `Offer` (e.g. basic/standard/premium).

    Fields:
        offer: ForeignKey to parent `Offer`.
        title: Title of this detail/tier.
        revisions: Number of included revisions.
        delivery_time_in_days: Delivery ETA in days.
        price: Price for this tier.
        features: JSON list describing included features.
        offer_type: One of the predefined OFFER_TYPE_CHOICES.
    """
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
    """
    Represents an order placed by a buyer for a specific `OfferDetail`.

    The `status` field is a free-form string used by application logic
    (e.g. 'in_progress', 'completed').
    """
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    offer_detail = models.ForeignKey(OfferDetail, on_delete=models.CASCADE, related_name='orders') 
    status = models.CharField(max_length=30, default='in_progress')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return f'Order #{self.id} - {self.offer_detail.title}'

class Review(models.Model):
    """
    A rating and optional text review that one user leaves for a business user.

    Fields:
        business_user: The reviewed business user.
        reviewer: The user who created the review.
        rating: Integer rating (expected 1-5).
        description: Optional textual feedback.
        created_at/updated_at: Timestamps for bookkeeping.
    """
    business_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_reviews')
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='given_reviews')
    rating = models.PositiveSmallIntegerField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Review {self.rating} by {self.reviewer.username} for {self.business_user.username}'