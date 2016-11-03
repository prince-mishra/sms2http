from tastypie import fields, utils
from tastypie.resources import ModelResource, ALL
from tastypie.authorization import Authorization
from tastypie.authentication import Authentication, ApiKeyAuthentication
from tastypie.cache import SimpleCache
from tastypie.utils.mime import determine_format, build_content_type
from tastypie import http

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned, ValidationError
from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.conf import settings

import urlparse
import json

from client.models import *

from tastypie.exceptions import Unauthorized
from tastypie.models import ApiKey

import base64
from Crypto.Cipher import AES
from Crypto import Random

BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS) 
unpad = lambda s : s[:-ord(s[len(s)-1:])]

class AESCipher:
    def __init__( self, key ):
        self.key = key

    def encrypt( self, raw ):
        raw = pad(raw)
        iv = Random.new().read( AES.block_size )
        cipher = AES.new( self.key, AES.MODE_CBC, iv )
        return base64.b64encode( iv + cipher.encrypt( raw ) ) 

    def decrypt( self, enc ):
        enc = base64.b64decode(enc)
        iv = enc[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv )
        return unpad(cipher.decrypt( enc[16:] ))


class UserObjectsOnlyAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        # This assumes a ``QuerySet`` from ``ModelResource``.
        return object_list.filter(user=bundle.request.user)

    def read_detail(self, object_list, bundle):
        # Is the requested object owned by the user?
        return bundle.obj.user == bundle.request.user

    def create_list(self, object_list, bundle):
        # Assuming they're auto-assigned to ``user``.
        return object_list

    def create_detail(self, object_list, bundle):
        return bundle.obj.user == bundle.request.user

    def update_list(self, object_list, bundle):
        allowed = []

        # Since they may not all be saved, iterate over them.
        for obj in object_list:
            if obj.user == bundle.request.user:
                allowed.append(obj)

        return allowed

    def update_detail(self, object_list, bundle):
        return bundle.obj.user == bundle.request.user

    def delete_list(self, object_list, bundle):
        # Sorry user, no deletes for you!
        raise Unauthorized("Sorry, no deletes.")

    def delete_detail(self, object_list, bundle):
        if bundle.obj.user == bundle.request.user:
            return object_list
        else:
            raise Unauthorized("Sorry, no deletes.")

class PhoneResource(ModelResource):
    class Meta:
        queryset = Phone.objects.all()
        resource_name = 'phone'
        authorization = UserObjectsOnlyAuthorization()
        authentication = ApiKeyAuthentication()
        always_return_data = True

class SMSResource(ModelResource):
    phone = fields.ForeignKey(PhoneResource, 'phone')
    class Meta:
        queryset = SMS.objects.all()
        resource_name = 'sms'
        authorization = UserObjectsOnlyAuthorization()
        authentication = ApiKeyAuthentication()
        always_return_data = True
        filtering = {
            'sender' : ALL,
            'created' : ALL,
            'phone' : ALL,
            'user'  : ALL,
        }

    def __get_api_key(self, user):
        key = ApiKey.objects.get(user=user)
        return key.key[2:34]

    def __encrypt(self, key, raw):
        cipher = AESCipher(key)
        return cipher.encrypt(raw)

    def __decrypt(self, key, enc):
        cipher = AESCipher(key)
        return cipher.decrypt(enc)

    def obj_create(self, bundle, **kwargs):
        kwargs['user_id'] = bundle.request.user.id
        kwargs['phone_id'] = int(bundle.request.GET['phone_id'])
        bundle = super(SMSResource, self).obj_create(bundle, **kwargs)
        return bundle

    def hydrate_body(self, bundle):
        user = bundle.request.user
        user_api_key = self.__get_api_key(user)
        bundle.data['body'] = self.__encrypt(user_api_key, bundle.data['body'])
        return bundle

    def dehydrate_body(self, bundle):
        user = bundle.request.user
        user_api_key = self.__get_api_key(user)
        return self.__decrypt(user_api_key, bundle.data['body']) 