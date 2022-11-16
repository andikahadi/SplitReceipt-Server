import json

from django.core import serializers
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
from users.models import NewUser
from .models import Vendor, Item, Receipt, Receipt_items, Friend
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
        # for friend in friends:
        #     friend_list.append({"name": friend.getFirstName(), "id": friend.getId()})
        #
        # for friend in friend_list:
        #     try:
        #         friend = Friend.objects.get(splitwise_friend_id=friend.name)
        #         friend_id = friend.id
        #     except ObjectDoesNotExist:
        #         user = NewUser.objects.get(email=request.data["email"])
        #         friend_data = {
        #             "name": friend.name,
        #             "splitwise_friend_id": friend.id,
        #             "user": user.id
        #         }
        #         friend_serializer = FriendSerializer(data=friend_data)
        #
        #         if friend_serializer.is_valid():
        #             friend_serializer.save()
        #         else:
        #             return Response(friend_serializer.errors)
        #         friend = Friend.objects.get(splitwise_friend_id=friend.name)

        return Response(friend_list)
#
# {
#         "receipt_type": "GrabFood",
#         "vendor": "Subway - 100AM",
#         "receipt_code": "100260235-C3VXNKJKCJ6ZGN",
#         "deliver_date": "11 Oct 22 12:28 +0800",
#         "receipt_total_fee": 29.84,
#         "item": [
# {
#         "receipt_type": "GrabFood",
#         "vendor": "Subway - 100AM",
#         "receipt_code": "100260235-C3VXNKJKCJ6ZGN",
#         "deliver_date": "11 Oct 22 12:28 +0800",
#         "receipt_total_fee": 29.84,
#         "item": [
#             {
#                 "name": "Meatball Marinara Melt",
#                 "qty": 1,
#                 "total_item_price": 13.5
#             },
#             {
#                 "name": "Roasted Chicken - Cookie Meal",
#                 "qty": 1,
#                 "total_item_price": 12.3
#             },
#             {
#                 "name": "Chunky Beef Steak &amp; Cheese",
#                 "qty": 1,
#                 "total_item_price": 11.5
#             }
#         ]
#     },
#     {
#         "receipt_type": "GrabFood",
#         "vendor": "Takagi Ramen - AMK",
#         "receipt_code": "A-3RCOR7FGWFQD",
#         "deliver_date": "16 Aug 22 19:19 +0800",
#         "receipt_total_fee": 19.4,
#         "item": [
#             {
#                 "name": "Buddy Meal (U.P. $34.50)",
#                 "qty": 1,
#                 "total_item_price": 22.9
#             }
#         ]
#     }
#             {
#                 "name": "Meatball Marinara Melt",
#                 "qty": 1,
#                 "total_item_price": 13.5
#             },
#             {
#                 "name": "Roasted Chicken - Cookie Meal",
#                 "qty": 1,
#                 "total_item_price": 12.3
#             },
#             {
#                 "name": "Chunky Beef Steak &amp; Cheese",
#                 "qty": 1,
#                 "total_item_price": 11.5
#             }
#         ]
#     },
#     {
#         "receipt_type": "GrabFood",
#         "vendor": "Takagi Ramen - AMK",
#         "receipt_code": "A-3RCOR7FGWFQD",
#         "deliver_date": "16 Aug 22 19:19 +0800",
#         "receipt_total_fee": 19.4,
#         "item": [
#             {
#                 "name": "Buddy Meal (U.P. $34.50)",
#                 "qty": 1,
#                 "total_item_price": 22.9
#             }
#         ]
#     }
class GetReceipt(APIView):
    def post(self, request):
        user = NewUser.objects.get(email=request.data['email'])
        receipts = Receipt.objects.select_related('vendor').filter(user_id=user.id)
        serialized_receipts = json.loads(serializers.serialize('json', receipts))

        receipt_fetch_arr = []

        for receipt in serialized_receipts:
            vendor = Vendor.objects.get(id=receipt['fields']['vendor'])
            serialized_vendor = json.loads(serializers.serialize('json', [vendor, ]))[0]["fields"]["vendor"]
            receipt['fields']['vendor_name'] = serialized_vendor

            # get item_arr
            receiptitems = Receipt_items.objects.filter(receipt_id=receipt['pk'])
            serialized_receiptitems = json.loads(serializers.serialize('json', receiptitems))
            item_arr = []
            for receiptitem in serialized_receiptitems:
                item = Item.objects.get(id=receiptitem['fields']['item'])
                serialized_item = json.loads(serializers.serialize('json', [item, ]))[0]['fields']['name']
                receiptitem['fields']['name'] = serialized_item
                item_data = {
                    'name': receiptitem['fields']['name'],
                    'qty': receiptitem['fields']['quantity'],
                    'total_item_price': receiptitem['fields']['total_item_price']
                    }
                item_arr.append(item_data)

            receipt['fields']['item']=item_arr
            receipt_fetch_template = {
                "receipt_code": receipt['pk'],
                "receipt_type": receipt['fields']['receipt_type'],
                "delivery_date": receipt['fields']['delivery_date'],
                "receipt_total": receipt['fields']['receipt_total_fee'],
                "vendor": receipt['fields']['vendor_name'],
                "is_assigned": receipt['fields']['is_assigned'],
                "assignment": receipt['fields']['assignment'],
                "item": receipt['fields']['item']
                }
            receipt_fetch_arr.append(receipt_fetch_template)
        return Response(receipt_fetch_arr)
# {
#         "model": "EmployeeApp.receipt",
#         "pk": "A-3RCOR7FGWFQD",
#         "fields": {
#             "receipt_type": "GrabFood",
#             "delivery_date": "16 Aug 22 19:19 +0800",
#             "receipt_total_fee": "19.40",
#             "user": 1,
#             "vendor": 10,
#             "is_assigned": false,
#             "assignment": null,
#             "vendor_name": "Takagi Ramen - AMK"
#         }
#     }



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

        # return Response(message)
        for messageItem in message:

            with transaction.atomic():

                try:
                    vendor = Vendor.objects.get(vendor=messageItem["vendor"])
                except ObjectDoesNotExist:
                    vendor_data = {
                        "vendor": messageItem["vendor"]
                    }
                    vendors_serializer = VendorSerializer(data=vendor_data)

                    if vendors_serializer.is_valid():
                        vendors_serializer.save()
                    else:
                        return Response(vendors_serializer.errors)
                    vendor = Vendor.objects.get(vendor=messageItem["vendor"])

                # item table
                for i in range(0, len(messageItem["item"])):
                    try:
                        item = Item.objects.get(name=messageItem["item"][i]["name"])
                    except ObjectDoesNotExist:
                        item_data = {
                            "name": messageItem["item"][i]["name"]
                        }
                        items_serializer = ItemSerializer(data=item_data)

                        if items_serializer.is_valid():  # validate if serializer is correct
                            items_serializer.save()
                        else:
                            return Response(items_serializer.errors)
                        item = Item.objects.get(name=messageItem["item"][i]["name"])

                # receipt table

                user = NewUser.objects.get(email=request.data["email"])
                receipt_data = {
                    "receipt_code": messageItem["receipt_code"],
                    "receipt_type": messageItem["receipt_type"],
                    "delivery_date": messageItem["delivery_date"],
                    "receipt_total_fee": messageItem["receipt_total_fee"],
                    "vendor": vendor.id,
                    "user": user.id
                }
                receipts_serializer = ReceiptSerializer(data=receipt_data)

                if receipts_serializer.is_valid():  # validate if serializer is correct
                    receipts_serializer.save()
                else:
                    return Response(receipts_serializer.errors)

                # receipt_items table
                receipt = Receipt.objects.get(receipt_code=messageItem["receipt_code"])
                for i in range(0, len(messageItem["item"])):
                    item = Item.objects.get(name=messageItem["item"][i]["name"])
                    receiptitems_data = {
                        "quantity": messageItem["item"][i]["qty"],
                        "total_item_price": messageItem["item"][i]["total_item_price"],
                        "receipt": receipt.receipt_code,
                        "item": item.id
                    }
                    receiptitems_serializer = ReceiptItemsSerializer(data=receiptitems_data)

                    if receiptitems_serializer.is_valid():  # validate if serializer is correct
                        receiptitems_serializer.save()
                    else:
                        return Response(receiptitems_serializer.errors)

        return Response("created")


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
    permission_classes = (IsAuthenticated,)
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

            user = NewUser.objects.get(email=request.data["email"])
            receipt_data = {
                "receipt_code": request.data["receipt_code"],
                "receipt_type": request.data["receipt_type"],
                "delivery_date": request.data["delivery_date"],
                "receipt_total_fee": request.data["receipt_total_fee"],
                "vendor": vendor.id,
                "user": user.id
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

    