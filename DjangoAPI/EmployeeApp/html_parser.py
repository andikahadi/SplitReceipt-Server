import AdvancedHTMLParser
import re


def parse_string(html_msg):
    # service = get_service()
    # user_id = 'me'
    # msg_id = '18455acd424512fd'
    #
    # html_msg = get_message(service, user_id, msg_id)

    parser = AdvancedHTMLParser.AdvancedHTMLParser()
    parser.parseStr(html_msg)

    spans = parser.getElementsByTagName('span')
    span_text = []

    for item in spans:
        span_text.append(item.innerText)

    links = parser.getElementsByTagName('a')
    link_text = []

    for item in links:
        link_text.append(item.innerText)

    # order_info = {"user_email": "", "vehicle_type": "", "vendor": "", "booking_code": "", "date": "", "total": "",
    #               "food_list": []}

    # j = 0
    # while j < len(link_text):
    #     if ("gmail" or "googlemail" or "google") in link_text[j]:
    #         order_info["user_email"] = re.sub(r'=', "", (re.search(r'([^\s]+)', link_text[j])).group(0))
    #
    #     j += 1

    order_info = {"receipt_type": "", "vendor": "", "receipt_code": "", "delivery_date": "", "receipt_total_fee": "",
                  "item": []}


    # vendor = ""
    # total = ""
    # date = ""
    # orders = []
    # booking_code = ""
    # vehicle_type = ""
    #
    # fees = ""
    # link = ""

    i = 0
    while i < len(span_text)-2:
        if order_info["delivery_date"] == "":
            date_match = re.search(r'([1-9]|([012][0-9])|(3[01])) (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) '
                                   r'\d\d \d\d:\d\d [+-]\d\d\d\d', span_text[i])
            if date_match is not None:
                order_info["delivery_date"] = date_match.group()
                order_info["receipt_total_fee"] = float(re.search(r'\d{1,4}.\d{2}', span_text[i-1]).group())
                i += 1
                continue

        if order_info["receipt_type"] == "" and span_text[i] == "Vehicle type:":
            order_info["receipt_type"] = span_text[i + 1]
            i += 2
            continue

        if order_info["receipt_code"] == "" and span_text[i] == "Booking code":
            order_info["receipt_code"] = span_text[i+1]
            i += 2
            continue

        if order_info["vendor"] == "" and span_text[i] == "Order from:":

            order_info["vendor"] = re.sub(r'&amp;', "&", (re.sub(r'\s+$', "", span_text[i + 1])))

            i += 2
            continue

        qty_match = re.search(r'(\d)x', span_text[i])
        price_match = re.search(r'\d{1,4}.\d{2}', span_text[i+2])
        if qty_match is not None and price_match is not None:
            qty = int(qty_match.group(1))
            price = float(price_match.group())
            item = re.sub(r'&amp;', "&",(re.sub(r'=\r\n', "", span_text[i+1])))
            order_info["item"].append({"name": item, "qty": qty, "total_item_price":price})
            i += 3
            continue

        i += 1

    return order_info
