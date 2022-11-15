from django.shortcuts import render
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
# from users.models import NewUser
from .models import Vendor, Item, Receipt, Receipt_items
from .serializers import VendorSerializer, ItemSerializer, ReceiptSerializer, ReceiptItemsSerializer, FriendSerializer, ReceiptItemFriendSerializer
from splitwise import Splitwise
import re
from .email_stuff import get_service, get_message, search_messages
from .html_parser import parse_string


class SplitwiseAuthUrl(APIView):
    def get(self, request):
        consumer_key = "tHpxcE0JxqNQvHUN4Lf9Q4IjyZMM1vLEBpWnSROg"
        consumer_secret = "H3S0iJc2Vcchc3qMtfgZbSMNF9aryjM6E8n6AsFe"
        #
        sObj = Splitwise(consumer_key, consumer_secret)
        url, secret = sObj.getAuthorizeURL()
        # # departments = Departments.objects.all()
        # # serializer = DepartmentSerializer(departments, many=True) #will return a list since many=True
        return Response({"url":url, "secret":secret})

    def post(self, request):
        callbackUrl = request.data["callbackUrl"]
        secret = request.data["secret"]

        oauth_verifier = re.search(r'(?<=oauth_verifier=)(.*)$', callbackUrl).group(0)
        oauth_token = re.search(r'(?<=oauth_token=)(.*)(?=&oauth_verifier)', callbackUrl).group(0)

        consumer_key = "tHpxcE0JxqNQvHUN4Lf9Q4IjyZMM1vLEBpWnSROg"
        consumer_secret = "H3S0iJc2Vcchc3qMtfgZbSMNF9aryjM6E8n6AsFe"
        sObj = Splitwise(consumer_key, consumer_secret)

        access_token = sObj.getAccessToken(oauth_token, secret, oauth_verifier)
        return Response(access_token)


class SplitwiseFriend(APIView):
    def post(self, request):
        consumer_key = "tHpxcE0JxqNQvHUN4Lf9Q4IjyZMM1vLEBpWnSROg"
        consumer_secret = "H3S0iJc2Vcchc3qMtfgZbSMNF9aryjM6E8n6AsFe"

        sObj = Splitwise(consumer_key, consumer_secret)
        sObj.setAccessToken(request.data)

        friends = sObj.getFriends()
        friend_list = []
        for friend in friends :
            friend_list.append({"name": friend.getFirstName(), "id": friend.getId()})

        return Response(friend_list)


class GmailReceipt(APIView):
    def post(self, request):
        google_access_token = request.data["access_token"]
        user_id = 'me'
        search_string = 'after: 2022/11/01 Your Grab E-Receipt'

        service = get_service(google_access_token)
        message_id_list = search_messages(service, user_id, search_string)

        message = []
        for message_id in message_id_list:
            html_message = get_message(service, user_id, message_id)
            message.append(parse_string(html_message))

        return Response(message)
#
# class TaskDetails(APIView):
#     def get(self, request, pk):
#         department = Departments.objects.get(DepartmentId=pk)
#         serializer = DepartmentSerializer(department, many=False)
#         return Response(serializer.data)
#
#
# class TaskCreate(APIView):
#     def put(self, request):
#         serializer = DepartmentSerializer(data=request.data)
#         # deserializing data from frontend. can modify request.data first
#
#         if serializer.is_valid():  # validate if serializer is correct
#             serializer.save()
#             return Response(serializer.data)
#
#         else:
#             return Response(serializer.errors)

# {
#     "receipt_code": "82345678",
#     "receipt_type": "Grabfood",
#     "delivery_date": "22 Aug 22 17:27",
#     "receipt_total": 50.00,
#     "vendor": "Subway - 104AM",
#     "item": [{
#         "name": "wrap10",
#         "qty" : 3,
#         "total_item_price" : 9.9
#     },
#     {
#         "name": "wrap11",
#         "qty" : 2,
#         "total_item_price" : 8.9
#     }]
# }


class ReceiptCreate(APIView):
    # permission_classes = (IsAuthenticated,)
    def put(self, request):
        # vendor table
        with transaction.atomic():

            try:
                vendor = Vendor.objects.get(vendor=request.data["vendor"])
                vendor_id = vendor.id
            except ObjectDoesNotExist:
                vendor_data = {
                  "vendor": request.data["vendor"]
                }
                vendors_serializer = VendorSerializer(data=vendor_data)

                if vendors_serializer.is_valid():
                    vendors_serializer.save()
                else:
                    return Response(vendors_serializer.errors)
                vendor = Vendor.objects.get(vendor=request.data["vendor"])

            # item table
            for i in range(0, len(request.data["item"])):
              try:
                item = Item.objects.get(name=request.data["item"][i]["name"])
              except ObjectDoesNotExist:
                item_data = {
                    "name": request.data["item"][i]["name"]
                  }
                items_serializer = ItemSerializer(data=item_data)

                if items_serializer.is_valid():  # validate if serializer is correct
                    items_serializer.save()
                else:
                  return Response(items_serializer.errors)
                item = Item.objects.get(name=request.data["item"][i]["name"])

            #receipt table

            # user = NewUser.objects.get(email=request.data["email"])
            receipt_data = {
                "receipt_code": request.data["receipt_code"],
                "receipt_type": request.data["receipt_type"],
                "delivery_date": request.data["delivery_date"],
                "receipt_total_fee": request.data["receipt_total_fee"],
                "vendor": vendor.id,
                # "user": user.id
              }
            receipts_serializer = ReceiptSerializer(data=receipt_data)

            if receipts_serializer.is_valid():  # validate if serializer is correct
                receipts_serializer.save()
            else:
                return Response(receipts_serializer.errors)

            #receipt_items table
            receipt = Receipt.objects.get(receipt_code=request.data["receipt_code"])
            for i in range (0, len(request.data["item"])):
              item = Item.objects.get(name=request.data["item"][i]["name"])
              receiptitems_data = {
                  "quantity": request.data["item"][i]["qty"],
                  "total_item_price": request.data["item"][i]["total_item_price"],
                  "receipt": receipt.receipt_code,
                  "item": item.id
                }
              receiptitems_serializer = ReceiptItemsSerializer(data=receiptitems_data)

              if receiptitems_serializer.is_valid():  # validate if serializer is correct
                  receiptitems_serializer.save()
              else:
                return Response(receiptitems_serializer.errors)

            return Response("Receipt created")

# class TaskUpdate(APIView):
#     def patch(self, request, pk):
#         department = Departments.objects.get(DepartmentId=pk)
#
#         serializer = DepartmentSerializer(instance=department, data=request.data, partial=True)
#         # using task that you get, updating request data from frontend
#         # partial true allows to update one or many, if false need to send all fields back
#
#         if serializer.is_valid():
#             serializer.save()
#
#         return Response(serializer.data)
#
#
# class TaskDelete(APIView):
#     def delete(self, request, pk):
#         department = Departments.objects.get(DepartmentId=pk)
#         department.delete()
#
#         return Response('item deleted')
#

    