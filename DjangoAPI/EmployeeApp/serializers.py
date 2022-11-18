from rest_framework import serializers
from .models import Vendor, Receipt, Item, Receipt_items


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = '__all__'


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'


class ReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipt
        fields = '__all__'


class ReceiptItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipt_items
        fields = '__all__'


# class FriendSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Friend
#         fields = '__all__'


# class ReceiptItemFriendSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ReceiptItem_Friend
#         fields = '__all__'
