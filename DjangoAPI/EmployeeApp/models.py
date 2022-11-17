from django.db import models
from django.conf import settings
from users.models import NewUser

# Create your models here.


class Vendor(models.Model):
    vendor = models.CharField(max_length=30, unique=True)


class Item(models.Model):
    name = models.CharField(max_length=30, unique=True)


class Receipt(models.Model):
    RECEIPT_TYPE = (
      ('GrabFood', 'GrabFood'),
      ('Foodpanda', 'Foodpanda')
    )
    receipt_code = models.CharField(max_length=30, primary_key=True, blank=False)
    receipt_type = models.CharField(max_length=30, choices=RECEIPT_TYPE, blank=True)
    delivery_date = models.CharField(max_length=30, blank=False)
    receipt_total_fee = models.DecimalField(max_digits=6, decimal_places=2, blank=False)
    user = models.ForeignKey(NewUser, null=True, on_delete=models.SET_NULL)
    vendor = models.ForeignKey(Vendor, null=True, on_delete=models.SET_NULL)
    is_assigned = models.BooleanField(default=False)
    assignment = models.CharField(max_length=30, null=True)
    split_description = models.CharField(max_length=600, null=True, blank=True)


class Receipt_items(models.Model):
    quantity = models.IntegerField(blank = False)
    total_item_price =models.DecimalField(max_digits=6, decimal_places=2 , blank = False)
    receipt = models.ForeignKey(Receipt,null=True, on_delete=models.SET_NULL)
    item = models.ForeignKey(Item,null=True, on_delete=models.SET_NULL)


# class Friend(models.Model):
#     name = models.CharField(max_length=30, blank=False)
#     splitwise_friend_id = models.CharField(max_length=30, blank=False, unique=True)
#     user = models.ForeignKey(NewUser, null=True, on_delete=models.SET_NULL)
#
#
# class ReceiptItem_Friend(models.Model):
#     friend = models.ForeignKey(Friend, blank=True, null=True, on_delete=models.SET_NULL)
#     receipt_items = models.ForeignKey(Receipt_items, blank=True, null=True, on_delete=models.SET_NULL)
#

