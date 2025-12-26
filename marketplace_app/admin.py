from django.contrib import admin
from .models import Offer,OfferDetail, Order, Review

class OfferDetailInline(admin.TabularInline):
    model = OfferDetail
    extra = 3
    min_num = 3
    max_num = 3


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'created_at', 'updated_at', 'min_price', 'min_delivery_time']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['title', 'description']
    inlines = [OfferDetailInline]


@admin.register(OfferDetail)
class OfferDetailAdmin(admin.ModelAdmin):
    list_display = ['offer', 'title', 'offer_type', 'price', 'delivery_time_in_days', 'revisions']
    list_filter = ['offer_type']


admin.site.register(Order)
admin.site.register(Review)
