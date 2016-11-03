import json
import requests
import sendgrid

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from django.http.response import HttpResponse

from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt

from tastypie.models import ApiKey

from client.models import *
# Create your views here.

sg = sendgrid.SendGridClient('<sendgrid_key_here>')

def send_email(receiver, subject, html, text, sender='noreply@example.com'):
    print 'Sending email to ', receiver
    message = sendgrid.Mail(to=receiver, subject=subject, html=html, text=text, from_email=sender)
    status, msg = sg.send(message)
    print status, msg


def signup_mail(params):
    subject = 'Your access to sms2http has been approved'
    html = """
    <html>
      <head></head>
      <body>
    Dear %(username)s,<br><br>

    This is an automated email from your sms2http administrator.<br>
    Your access to sms2http has been approved.<br><br>

    The details are as follows :<br><br>
    <table>
    <tr>    <td>email_id</td><td>%(email_id)s</td></tr>
    <tr>    <td>phone_number</td><td>%(phone_no)s</td></tr>
    <tr>    <td>username</td><td>%(username)s</td></tr>
    <tr>    <td>api_key</td><td>%(api_key)s</td></tr>
    <tr>    <td>phone_id</td><td>%(phone_id)s</td></tr>
    <tr>    <td>api_url</td><td>%(api_url)s</td></tr>
    </table>
    All your SMSs are encrypted using your api_key. Please keep it safe and out of reach of others.<br><br>

    Regards,<br>
    Team sms2http
    </body></html>
    """ % params

    text = """
    Dear %(username)s,

    This is an automated email from your sms2http administrator.
    Your access to sms2http has been approved.

    The details are as follows :

    email_id : %(email_id)s
    phone_number : %(phone_no)s
    username : %(username)s
    api_key : %(api_key)s
    phone_id : %(phone_id)s
    api_url : %(api_url)s

    All your SMSs are encrypted using your api_key. Please keep it safe and out of reach of others.

    Regards,
    Team sms2http
    """ % params
    return subject, text, html

@csrf_exempt
def signup(request):
    data        = json.loads(request.body)
    # Create User
    email_id    = data['Username'][0]
    username    = email_id.split('@')[0]
    password    = get_random_string(10)
    user        = User.objects.create_user(username, email_id, password)
    # Create API Key
    api_key_obj = ApiKey.objects.create(user=user)
    api_key     = api_key_obj.key
    # Create Phone
    phone_obj   = Phone.objects.create(user = user, number = data['mobile_no'][0])
    phone_no    = phone_obj.number
    phone_id    = phone_obj.id
    api_url     = request.scheme + '://' + request.META['HTTP_HOST'] + '/sms2http/api/v1/sms/?format=json&username=%(user)s&api_key=%(api_key)s&phone_id=%(phone_id)s' % {'user' : username, 'api_key' : api_key, 'phone_id' : phone_id}
    
    payload     = json.dumps({'sender' : 'System', 'body' : 'Hello World'})
    headers     = {'content-type' : 'application/json'}
    r           = requests.post(api_url, data = payload, headers = headers)
    r.raise_for_status()
    params = {
        'username'  : username,
        'email_id'  : email_id,
        'api_key'   : api_key,
        'api_url'   : api_url,
        'phone_no'  : phone_no,
        'phone_id'  : phone_id,

    }

    subject, text, html = signup_mail(params)
    send_email(email_id, subject, html, text)
    return HttpResponse(json.dumps({'status' : 0, 'msg' : 'User signed up successfully'}),content_type='application/json', status = 201)