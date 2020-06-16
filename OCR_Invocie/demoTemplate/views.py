from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from django.http import JsonResponse
from django.core import serializers
import re
import os
import sys
from .loader import chooseInput
from django.contrib.auth import authenticate
from .models import Auth
from .models import Customer
from  .models import Invoice
from uuid import uuid4
from datetime import datetime
import time
import smtplib
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.conf import settings
from django.template.loader import render_to_string



os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/totoro0098/Documents/OCR_Invoice/OCR_Invocie/weighty-opus-271403-21af4d24b84b.json"


# Create your views here.
def index(request):
    if request.method == "POST" and request.FILES['file']:
        customer_id = request.POST['customerId']
        rotate = request.POST['rotate']
        number = rotate_image(rotate)
        myfile = request.FILES['file']
        fs = FileSystemStorage()
        afilename = fs.save(myfile.name, myfile)
        filename = '/home/totoro0098/Documents/OCR_Invoice/OCR_Invocie/file/' + afilename

        if number != -1:
            filename = chooseInput(number, filename)
        res = detect_text_Okono(filename)
        print("*******")
        print(res)
        if Customer.objects.get(id_customer=customer_id) == "":
            return JsonResponse({"Status": "Fail"})
        else:
            if res.get('total') != "" and res.get('invoice number') != "":
                save_invoice(customer_id, res.get('invoice number'),res.get('total'), res.get('date'))
                return JsonResponse(str(res), content_type="application/json", safe=False)
            else:
                return JsonResponse({"Status": "Fail", "Error": "Cant not read image"})
    return JsonResponse({"Status": "Fail"})

#image to text GG Cloud Vision


def login(request):
    if request.method == "POST":
        data = request.POST.copy()
        user = authenticate(username=data['username'], password=data['password'])
        if user is not None:
            rand_token = uuid4()
            response = JsonResponse({'data': rand_token,
                                     'username': data['username']})
            list_auth = list(Auth.objects.values())
            for auth in list_auth:
                if auth['username'] == data['username']:
                    a = Auth.objects.get(id=auth['id'])
                    a.delete()
            auth = Auth()
            auth.token = rand_token
            auth.username = data['username']
            auth.save()
            return response
            # A backend authenticated the credentials
        else:
            return JsonResponse({'data': 'Fail'})
            # No backend authenticated the credentials
    return JsonResponse({"data": 'Login'})

def logout(request):
    if request.method == "GET":
        token = request.headers.get('Authorization')
        list_auth = list(Auth.objects.values())
        for auth in list_auth:
            if auth['token'] ==  token:
                a = Auth.objects.get(id = auth['id'])
                a.delete()
    return JsonResponse({'data':'Logout'})

def sign(request):
    d = datetime.now()
    id = str(time.mktime(d.timetuple())).replace(".0", "")

    if request.method == "POST":
        data = request.POST.copy()
        customer = Customer()
        customer.full_name = data['fullname']
        customer.email = data['email']
        customer.phone = data['phone']
        customer.birthday = data['birthday']
        customer.gender = data['gender']
        customer.id_customer = 'OKONO-' + id
        customer.save()

        sendEmail(customer.email, customer.full_name, customer.id_customer)
        return JsonResponse({'data': 'SUCCESS'})

    else:
        return JsonResponse({"data": 'Fail'})

def sendEmail(email, name, customerID):
    if email != '':
        to = [email]
        subject = 'Email from Okono'
        body = """
        Hi {}.
        Thanks for sending your invoice!
        This is your ID Customer: 
                {} 
        """.format(name, customerID)
        print(body)
        try:
            send_mail(subject, body,settings.EMAIL_HOST_USER, to)
        except:
            print(sys.exc_info()[0])
            print('Something went wrong...')
    else:
        print("No email")
    return JsonResponse({"Data": "Success"})

def save_invoice(customerID, id_invoice, total_invoice, date_invoice,):
    if Customer.objects.filter(id_customer = customerID):
        invoice = Invoice()

        invoice.id_customer = customerID
        invoice.id_invoice = id_invoice
        invoice.total_invocie = total_invoice
        invoice.date_invoice = date_invoice
        invoice.save()

        return True
    else:
        return False

def get_invocie_paging(request):
    if request.method == "GET":
        currentPage = request.GET.get['currentPage']
        limit = 10
        customerID = request.GET.get['customerID']
        if currentPage <= 0 or currentPage == "":
            currentPage = 0
        totalData = Invoice.objects.filter(id_customer = customerID).values()
        print(len(totalData))
        listRecord = []
        for record in range((currentPage * limit), ((currentPage + 1) * limit)):
            if record >= len(totalData):
                break
            else:
                listRecord.append(totalData[record])

        return listRecord
    return

def listInvoices(request):
    if request.method == "GET" :
        username = ''
        data = ''
        token = request.headers.get('Authorization')
        list_auth = list(Auth.objects.values())
        for auth in list_auth:
            if auth['token'] ==  token:
                username = auth['username']
        if username != '':
            data =  list(Invoice.objects.values())
        return JsonResponse({'data': data,'username': username})

def listCustomer(request):
    if request.method == "GET" :
        username = ''
        data = ''
        token = request.headers.get('Authorization')
        list_auth = list(Auth.objects.values())
        for auth in list_auth:
            if auth['token'] ==  token:
                username = auth['username']
        if username != '':
            data =  list(Customer.objects.values())
        print(data)
        return JsonResponse({'data': data,'username': username})



from google.cloud import vision
import io
from google.protobuf import json_format

def detect_text(path):
    print(path)
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations

    print('Texts:')
    listDescription = []
    listVertices = []
    verticetotal = []
    total = ""
    unit = ""


    for text in texts:
        # print('\n"{}"'.format(text.description))
        # vertices = ([(vertex.x, vertex.y)
        #             for vertex in text.bounding_poly.vertices])

        vertices = ([(vertex.y)
                     for vertex in text.bounding_poly.vertices])
        # regex total
        pattern = re.compile("total")
        if (pattern.search(text.description.lower())):
            verticetotal = vertices
        else:
            listVertices.append((vertices))
            listDescription.append(text.description)
        # print('bounds: {}'.format(','.join(vertices)))

    for i in range(len(listVertices)):
        # print(listVertices[i])
        for check in range(len(verticetotal)):
            if abs(verticetotal[check] - listVertices[i][check]) <= 10:
                if is_number(listDescription[i]):
                    total += str(listDescription[i])
                elif listDescription[i] != ":":
                    if extractNumber(listDescription[i]):
                        total += extractNumber(listDescription[i])
                        unit += re.sub(extractNumber(listDescription[i]),  '',    listDescription[i])
                    else:
                        unit += str(listDescription[i])
                break

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))
    # return format(texts[0].description)
    print(total)
    print(unit)
    return {'total': total, 'unit': unit}
#

def detect_text_Okono(path):
    print(path)
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations

    print('Texts:')
    total = ""
    invoice_number = ""
    date = ""

    for key, value in enumerate(texts):
        print('\n"{}"'.format(value.description))

        pattern_number = re.compile("số")
        if (pattern_number.search(value.description.lower()) and key != 0):
            if texts[key+1].description != "Ngày":
                invoice_number = texts[key + 1].description
                print(invoice_number)
            else:
                invoice_number = value.description.replace("SỐ:", "")



        pattern_date = re.compile("ngày")
        if (pattern_date.search(value.description.lower()) and key != 0):
            date = texts[key + 1].description
            print(date)

        pattern_total = re.compile("tổng")
        pattern_toan = re.compile("toán")
        partern_tien = re.compile("ti")

        if (pattern_total.search(value.description.lower()) and key != 0):
            print(texts[key + 3].description.lower())
            if partern_tien.search(texts[key+1].description) and texts[key+2].description == "thanh" and pattern_toan.search(texts[key+3].description.lower()):
                total = texts[key + 4].description
            print(total)


    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))
    # return format(texts[0].description)
    date = date.replace("/", "-")
    return {'invoice number': invoice_number, 'total': total, 'date': date}

# def get_number_invoice()
def is_number(s):

    try:
        float(s)
        return True
    except ValueError:
        return False
def extractNumber(s):
    number = ""
    for i in range(len(s)):
        if s[i].isdigit() or s[i] == "." or s[i] == ",":
            number += s[i]
    return number

def rotate_image(rotate):
    rotate = int(rotate)
    number = -1
    if rotate <= 45 and rotate >= 20:
        number = 3
    elif rotate >0 and rotate < 20:
        number = 2
    elif rotate >=315 and rotate <= 340:
        number = 0
    elif rotate > 340 and rotate < 360:
        number = 1
    return number

    # def save_information(customerId, total, unit):
    #
    #     customer.id_customer = customerId
    #     customer.total_invocie = total
    #     customer.name_customer = "Thanh"
    #     customer.unit_invoce = unit
    #     customer.date = datetime.now()
    #     customer.save()
    #     return True

