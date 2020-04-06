from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.template import RequestContext
from django.apps import apps
import hmac, base64, hashlib, binascii, os
import shopify
from django.http import HttpResponse,JsonResponse,HttpResponseRedirect
from .decorators import shop_login_required
from django.views.decorators.clickjacking import xframe_options_exempt
from .constants import *
import requests
def get_access_token(code,STORE_NAME):

    data = {
    'code': code,
    'client_id': SHOPIFY_API_KEY,
    'client_secret': SHOPIFY_API_SECRET
    }
    url = "https://{}.myshopify.com/admin/oauth/access_token"
    response = requests.post(url.format(STORE_NAME), data=data)
    return response

def login(request):

    if request.GET.get('shop'):
        request.session['store_name'] = request.GET.get('shop')
        return authenticate(request)
    return render(request, 'shopify_login.html', {})

def get_authroize_url(STORE_NAME):

   return "https://{shop}.myshopify.com/admin/oauth/authorize?client_id={api_key}&scope={scopes}&redirect_uri={redirect_uri}".format(shop=STORE_NAME,api_key=SHOPIFY_API_KEY,scopes=SHOPIFY_API_SCOPE,redirect_uri=REDIRECT_URI)
    

def authenticate(request):
    shop_name = request.GET.get('shop', request.POST.get('shop')).strip()
    if not shop_name:
        messages.error(request, "A shop param is required")
        return redirect(reverse(login))
    permission_url = get_authroize_url(shop_name)

    return redirect(permission_url)

def finalize(request):
    
    code = request.GET['code']
    access_token = get_access_token(code,request.session['store_name'])
    request.session['access_token'] = access_token
    return redirect(index)



@shop_login_required
def index(request):

    return render(request, 'shopify_index.html')

@xframe_options_exempt
def welcomeview(request):

    return render(request, 'shopify_index.html')


@xframe_options_exempt
def Dashboardview(request):
    return HttpResponseRedirect('https://app.karenapp.io/dashboard')