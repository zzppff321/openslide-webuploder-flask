# coding=utf-8
import copy
import json
import uuid
from datetime import datetime

from .. import *
from .. import bce_client_configuration
from .. import utils
from ..auth import bce_v1_signer
from ..auth.bce_credentials import BceCredentials
from ..http import bce_http_client
from ..http import handler
from ..http import http_methods
from ..services import bos
from ..services.bos.bos_client import BosClient


class BchInterfaceHandler:
    def __init__(self,ACCESS_KEY_ID,SECRET_ACCESS_KEY):
        self.service_id = "a.b.c"
        self.region_supported = False
        self.config = copy.deepcopy(bce_client_configuration.DEFAULT_CONFIG)
        self.config.credentials = BceCredentials(access_key_id=ACCESS_KEY_ID,secret_access_key=SECRET_ACCESS_KEY)
        if self.config is not None:
            self.config.merge_non_none_values(self.config)
        if self.config.endpoint is None:
            self.config.endpoint = self._compute_endpoint()
    def _compute_service_id(self):
        return self.__module__.split('.')[2]

    def _compute_endpoint(self):
        if self.config.endpoint:
            return self.config.endpoint
        if self.region_supported:
            return '%s://%s.%s.%s' % (
                self.config.protocol,
                self.service_id,
                self.config.region,
                DEFAULT_SERVICE_DOMAIN)
        else:
            return '%s://%s.%s' % (
                self.config.protocol,
                self.service_id,
                DEFAULT_SERVICE_DOMAIN)
    def _get_config_parameter(self, config, attr):
        result = None
        if config is not None:
            result = getattr(config, attr)
        if result is not None:
            return result
        return getattr(self.config, attr)

    @staticmethod
    def _get_path(config, bucket_name=None, key=None):
        return utils.append_uri(bos.URL_PREFIX, bucket_name, key)

    def _merge_config(self, config):
        if config is None:
            return self.config
        else:
            new_config = copy.copy(self.config)
            new_config.merge_non_none_values(config)
            return new_config

    def _send_request(self, http_method, bucket_name=None, key=None, body=None,
                      headers=None, params=None, config=None, body_parser=None):
        config = self._merge_config(config)
        path = BosClient._get_path(config, bucket_name, key)
        if body_parser is None:
            body_parser = handler.parse_json

        return bce_http_client.send_request(
            config, bce_v1_signer.sign, [handler.parse_error, body_parser],
            http_method, path, body, headers, params)

    def generate_auth_token(self):
        return str(uuid.uuid4())

    # ????????????
    def newhost(self, reqBody):
        bce_date = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        headers = {}

        headers["Host"] = HOST
        headers["x-bce-date"] = bce_date
        headers["Accept"] = ACCEPT
        headers["Authorization"] = Authorization
        bucket_name = '{0}/host'.format(URL_PREFIX)
        params = {}
        params["clientToken"] = self.generate_auth_token()
        response = self._send_request(http_methods.POST, bucket_name=bucket_name, key=None, body=reqBody, headers=headers, params=params)
        return response

    # ?????????
    # 1????????????????????????????????????15?????????
    # 2?????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
    # 3???????????????????????????????????????????????????????????????query string???????????????clientToken?????????
    # clientToken????????????????????????64??????ASCII????????????????????????????????????

    # ??????????????????
    def getHost(self, account):
        xbd = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        headers = {}
        headers['Host'] = HOST
        headers['x-bce-date'] = xbd
        headers['Accept'] = ACCEPT
        headers["Authorization"] = Authorization

        bucket_name = '{0}/host/{1}'.format(URL_PREFIX, account)
        params = {}
        params["clientToken"] = self.generate_auth_token()
        response = self._send_request(http_methods.GET, bucket_name=bucket_name, key=None, headers=headers, params=params)
        return response

    # ????????????
    def renewhost(self, account,renewLength):
        xbd = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        headers = {}
        headers['Host'] = HOST
        headers['x-bce-date'] = xbd
        headers['Accept'] = ACCEPT
        headers["Authorization"] = Authorization

        bucket_name = '{0}/host/{1}'.format(URL_PREFIX, account)
        params = {}
        params["renewhost"] = ""
        body = {}
        body["renewLength"] = renewLength
        response = self._send_request(http_methods.PUT, bucket_name=bucket_name, key=None, headers=headers, params=params,body=json.dumps(body))
        return response

    # ??????FTP??????
    def resetftppwd(self,account, password ):
        xbd = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        headers = {}
        headers['Host'] = HOST
        headers['x-bce-date'] = xbd
        headers['Accept'] = ACCEPT
        headers["Authorization"] = Authorization

        bucket_name = '{0}/host/{1}'.format(URL_PREFIX, account)
        params = {}
        params["resetftppwd"] = ""
        reqBody = {}
        reqBody["password"] = password
        response = self._send_request(http_methods.PUT, bucket_name=bucket_name, key=None, body=json.dumps(reqBody), headers=headers, params=params)
        return response

    # ????????????????????????
    def resetaccountpwd(self, account, password):
        xbd = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        headers = {}
        headers['Host'] = HOST
        headers['x-bce-date'] = xbd
        headers['Accept'] = ACCEPT
        headers["Authorization"] = Authorization

        bucket_name = '{0}/host/{1}'.format(URL_PREFIX, account)
        params = {}
        params["resetaccountpwd"] = ""
        reqBody = {}
        reqBody["password"] = password
        response = self._send_request(http_methods.PUT, bucket_name=bucket_name, key=None, body=json.dumps(reqBody), headers=headers, params=params)
        return response

    # ??????????????????
    def binddomains(self, account, domains):
        xbd = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        headers = {}
        headers['Host'] = HOST
        headers['x-bce-date'] = xbd
        headers['Accept'] = ACCEPT
        headers["Authorization"] = Authorization

        bucket_name = '{0}/host/{1}'.format(URL_PREFIX, account)
        params = {}
        params["binddomains"] = ""
        reqBody = {}
        reqBody["domains"] = domains
        response = self._send_request(http_methods.PUT, bucket_name=bucket_name, key=None, body=json.dumps(reqBody), headers=headers, params=params)
        return response


if __name__ == '__main__':
    bch = BchInterfaceHandler()

    # ????????????
    body = {}
    # body["account"] = "pg0001"
    # body["packageId"] = "VHost-FC01"
    # body["purchaseLength"] = "12"
    # body["hostName"] = u'????????????'
    # body["domains"] = ['pangu.us', 'pangu.cn']
    # body["recordName"] = u'shengyan pangu'
    # contact = {}
    # # ???????????????????????????????????????????????????
    # contact["name"] = u'zhuangyan'
    # contact["mobilePhone"] = u'13111112222'
    # contact["email"] = u'zhuangyan@pp.com'
    # body["hostContact"] = contact
    # bch.newhost(json.dumps(body))


    # result = bch.resetftppwd("sy000071","12345678")

    # ??????????????????
    bch.getHost("sy000075")

    # ??????FTP??????
    # body_resetftppwd = {}
    # body_resetftppwd["password"] = "test123"
    # body_resetftppwd["password"] = ""
    # bch.resetftppwd(json.dumps(body_resetftppwd))

    # ????????????????????????
    # body_resetaccountpwd = {}
    # body_resetaccountpwd["password"] = "test123"
    # body_resetaccountpwd["password"] = ""
    # bch.resetaccountpwd(json.dumps(body_resetaccountpwd))

    # ??????????????????
    # body_binddomains = []
    # body_binddomains = ['test123']
    # bch.binddomains(json.dumps(body_binddomains))