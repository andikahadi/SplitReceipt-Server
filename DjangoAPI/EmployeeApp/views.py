import json
from splitwise.expense import Expense
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
from splitwise.user import ExpenseUser
from datetime import datetime
from users.models import NewUser
from .models import Vendor, Item, Receipt, Receipt_items
from .serializers import VendorSerializer, ItemSerializer, ReceiptSerializer, ReceiptItemsSerializer
from splitwise import Splitwise
import re
from .email_stuff import get_service, get_message, search_messages
from .html_parser import parse_string
from django.db.models import Q
import time
from decouple import config


# 'api/user-read/' POST is to get current user info. GET is to get list of all user for admin.
class UserInfo(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = NewUser.objects.get(email=request.data['email'])
        if user.last_email_fetch is not None:
            date_time = datetime.fromtimestamp(int(user.last_email_fetch)).strftime('%Y-%m-%d %H:%M:%S')
        else:
            date_time = None
        response_data = {
            "email": user.email,
            "user_name": user.user_name,
            "is_admin": user.is_admin,
            "last_email_fetch": date_time
        }
        return Response(response_data)

    def get(self, request):
        current_user_username = request.user
        current_user = NewUser.objects.get(user_name=current_user_username)

        #  return users list if is_admin==true
        if current_user.is_admin:
            users = NewUser.objects.all()
            serialized_users = json.loads(serializers.serialize('json', users))

            usersArr = []
            for user in serialized_users:
                user_template = {
                    "id": user['pk'],
                    "email": user['fields']["email"],
                    "user_name": user['fields']["user_name"],
                    "date_joined": user['fields']["date_joined"],
                    "last_login": user['fields']["last_login"],
                    "last_email_fetch": user['fields']["last_email_fetch"]
                }
                usersArr.append(user_template)

            return Response(usersArr)

        # return warning if is_admin == false
        else:
            return Response("You don't have permission to access the data")


# 'api/user-delete/' POST to delete user for admin
class UserDelete(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        current_user_username = request.user
        current_user = NewUser.objects.get(user_name=current_user_username)
        #  delete selected user if current user.is_admin==true
        if current_user.is_admin:
            user = NewUser.objects.get(pk=request.data["user_id"])
            user.delete()
            return Response('user deleted')
        else:
            return Response('You dont have the permission')


# 'api/splitwise/' GET to get authorization url, POST to get splitwise access token
class SplitwiseAuthUrl(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        consumer_key = config('consumer_key')
        consumer_secret = config('consumer_secret')

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
        # oauth_verifier = re.search(r'(?<=oauth_verifier=)(.*)$', callbackUrl)
        # oauth_token = re.search(r'(?<=oauth_token=)(.*)(?=&oauth_verifier)', callbackUrl)
        
        consumer_key = config('consumer_key')
        consumer_secret = config('consumer_secret')
        
        sObj = Splitwise(consumer_key, consumer_secret)

        access_token = sObj.getAccessToken(oauth_token, secret, oauth_verifier)
        return Response(access_token)


# 'api/splitwise-friend/' POST to get user Splitwise friends list
class SplitwiseFriend(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        consumer_key = config('consumer_key')
        consumer_secret = config('consumer_secret')

        sObj = Splitwise(consumer_key, consumer_secret)
        sObj.setAccessToken(request.data)

        friends = sObj.getFriends()
        friend_list = []
        for friend in friends:
            friend_list.append({"name": friend.getFirstName(), "id": friend.getId()})

        return Response(friend_list)


# 'api/post-expense/' POST to call Splitwise API creating expense
class SplitwiseExpense(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        consumer_key = config('consumer_key')
        consumer_secret = config('consumer_secret')

        access_token = request.data["access_token"]

        s = Splitwise(consumer_key, consumer_secret, access_token)
        u = s.getCurrentUser()
        my_id = u.getId()
        expense_data = request.data["expenseData"]

        for user_data in expense_data:
            if user_data["name"] != "You":
                owe_amount = str(round(user_data["owedWithFee"], 2))
                expense = Expense()
                expense.setCost(owe_amount)
                expense.setDescription(request.data["vendor"])

                user1 = ExpenseUser()
                user1.setId(my_id)
                user1.setPaidShare(owe_amount)
                user1.setOwedShare('0.00')
                user2 = ExpenseUser()
                user2.setId(user_data["splitwiseId"])
                user2.setPaidShare('0.00')
                user2.setOwedShare(owe_amount)
                expense.addUser(user1)
                expense.addUser(user2)
                nExpense, errors = s.createExpense(expense)
                print(nExpense.getId())

        ## This code is in progress, to have only expense ID if there are more than 2 person involved
        # owe_amount = str(request.data["receipt_total"])
        # print(owe_amount)
        # expense = Expense()
        # expense.setCost(owe_amount)
        # expense.setDescription(request.data["vendor"])

        # for userExpense in expense_data:
        #     if userExpense["name"] == "Me":
        #         user = ExpenseUser()
        #         user.setId(my_id)
        #         user.setPaidShare(owe_amount)
        #         user.setOwedShare(str(round(userExpense["owedWithFee"],2)))
        #     else:
        #         user = ExpenseUser()
        #         user.setId(userExpense['splitwiseId'])
        #         user.setPaidShare('0.00')
        #         user.setOwedShare(str(round(userExpense["owedWithFee"],2)))
        #         print(str(round(userExpense["owedWithFee"],2)))
        #     expense.addUser(user)
        #
        # nExpense, errors = s.createExpense(expense)
        # if errors is not None:
        #     print(errors.getErrors())
        #
        # print(nExpense)
        # print(nExpense.getId())
        return Response("created expense")


# 'api/get-receipt/' POST to get receipt from database
class GetReceipt(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        user = NewUser.objects.get(email=request.data['email'])
        criterion1 = Q(user_id=user)
        criterion2 = Q(is_assigned=request.data["is_assigned"])
        receipts = Receipt.objects.select_related('vendor').filter(criterion1 & criterion2)
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


# 'api/gmail-receipt/' POST : get receipt email from inbox based on user.last_email_fetch ,
# decode it into html, regex to get information, push to database.

class GmailReceipt(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        now = datetime.now()
        print(now)
        epochNow = int(now.strftime('%s')) # in string format
        print(epochNow)

        user = NewUser.objects.get(email=request.data["email"])

        google_access_token = request.data["access_token"]
        user_id = 'me'
        if user.last_email_fetch is None:
            print("empty email fetch")
            search_string = f'after:{epochNow - (4 * 604800)} label:inbox Your Grab E-Receipt Food'
        else:
            print("there is email fetch")
            print(user.last_email_fetch)
            search_string = f'after:{user.last_email_fetch} label:inbox Your Grab E-Receipt Food'
            print(search_string)

        service = get_service(google_access_token)
        message_id_list = search_messages(service, user_id, search_string)

        user.last_email_fetch = str(epochNow)
        user.save()

        message = []
        for message_id in message_id_list:
            html_message = get_message(service, user_id, message_id)
            message.append(parse_string(html_message))
        print(message)
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

        return Response(message)


# 'api/receipt-update/' patch to update user.is_assigned and user.assignment when user assigned the receipt
class ReceiptUpdate(APIView):
    permission_classes = (IsAuthenticated,)

    def patch(self, request):
        receipt = Receipt.objects.get(receipt_code= request.data["receipt_code"])
        receipt.is_assigned = True
        receipt.assignment = request.data["assignment"]
        receipt.save()
        return Response("Update done")


# 'api/receipt-create/' PUT : testing purpose creating using postman
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


    