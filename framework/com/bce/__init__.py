# coding=utf-8
# Copyright (c) 2014 Baidu.com, Inc. All Rights Reserved
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the
# License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions
# and limitations under the License.

"""
This module defines some common string constants.
"""

import protocol
SDK_VERSION = '0.0.1'
DEFAULT_SERVICE_DOMAIN = 'bch.bj.baidubce.com'#'bch.bj.bcebos.com'
URL_PREFIX = '/v1'
# POST = '/v{0}/host?clientToken={1} HTTP/1.1'.format(version, clientToken)
HOST = 'bch.bj.baidubce.com' # bch.bj.bcebos.com
URL = 'http://bch.bj.baidubce.com'
# ACCESS_KEY_ID = '2647e9da8eab431cbe58eaa6c1d46cdc'
# SECRET_ACCESS_KEY = '72c14ce4b2d2417c92dbe9828d45bd5a'
DEFAULT_ENCODING = 'UTF-8'
ACCEPT = 'application/json'


BCD_HOST = 'bcd.baidubce.com'
BCD_URL = 'http://bcd.baidubce.com'
# BCD_URL = 'http://bcd-api-sandbox.bigenemy.cn/'

BCD_ACCESS_KEY_ID = '2368f1fef2334b5b9159d1cbdf7a6792'
BCD_SECRET_ACCESS_KEY = '370625dc552d46f3ac76fc7dac8ecabe'

# bce-auth- v{version}/{accessKeyId}/{timestamp}/{expireTime}/{signedHeaders}/{signature}
Authorization = 'bce-auth-v1/f81d3b34e48048fbb2634dc7882d7e21/2015-08-11T04:17:29Z/3600/host;x-bce-date/74c506f68c65e26c633bfa104c863fffac5190fdec1ec24b7c03eb5d67d2e1de'