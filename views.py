from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.template import RequestContext
from django.apps import apps
import hmac, base64, hashlib, binascii, os
import shopify
from django.http import HttpResponse,JsonResponse,HttpResponseRedirect
from .decorators import shop_login_required
import requests
from django.views.decorators.clickjacking import xframe_options_exempt
from .constants import *

def _new_session(shop_url):
    api_version = SHOPIFY_API_VERSION
    return shopify.Session(shop_url, api_version)

def authenticate(request):
    shop_url = request.session['shop']
    if not shop_url:
        messages.error(request, "A shop param is required")
        return redirect(reverse(login))
    scope = SHOPIFY_API_SCOPE
    redirect_uri = request.build_absolute_uri(reverse(finalize))
    state = binascii.b2a_hex(os.urandom(15)).decode("utf-8")
    request.session['shopify_oauth_state_param'] = state
    permission_url = _new_session(shop_url).create_permission_url(scope, redirect_uri, state)
    #permission_url = "https://karenappteststore.myshopify.com/admin/oauth/authorize?client_id={}&scope=read_products%2Cread_orders&redirect_uri=https%3A%2F%2F34a1dae0.ngrok.io%2Ffinalize&state=ca5f75eda5fe5285dd18f53947fd61".format(SHOPIFY_API_KEY)
    return redirect(permission_url)

def login(request):

    if request.POST.get('shop'):
        request.session['shop'] = request.POST.get('shop')
        print(request.session['shop'])
        return authenticate(request)
    return render(request, 'shopify_login.html', {})
def get_access_token(code,STORE_NAME):

    data = {
    'code': code,
    'client_id': SHOPIFY_API_KEY,
    'client_secret': SHOPIFY_API_SECRET
    }
    url = "https://{}.myshopify.com/admin/oauth/access_token"
    response = requests.post(url.format(STORE_NAME), data=data)
    return response.json()
def finalize(request):
    
    hmac = request.GET.get('hmac')
    code = request.GET.get('code')
    if code:
            response = get_access_token(code,request.session['shop'])

            request.session['shopify'] = {
                'store_name' : request.session['shop'],
                'access_token' : response['access_token']
            }
            print(request.session['shopify'])
            return HttpResponseRedirect('https://karenapp.io')
    return redirect(request.session.get('return_to', reverse('root_path')))
    
def logout(request):
    request.session.pop('shopify', None)
    messages.info(request, "Successfully logged out.")
    return redirect(reverse(login))



#@shop_login_required
@xframe_options_exempt
def index(request):
    
    return render(request, 'shopify_index.html')


@xframe_options_exempt
def Dashboardview(request):
    return HttpResponseRedirect('https://app.karenapp.io/dashboard')