"""
Copyright (c) 2020, VRAI Labs and/or its affiliates. All rights reserved.

This software is licensed under the Apache License, Version 2.0 (the
"License") as published by the Apache Software Foundation.

You may not use this file except in compliance with the License. You may
obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.
"""

from os import environ, scandir, kill, remove
from signal import SIGTERM
from time import sleep
from yaml import dump, load, FullLoader
from shutil import copy, rmtree
from datetime import datetime, timezone
from subprocess import run, DEVNULL
from requests.models import Response
from http.cookies import SimpleCookie
from supertokens_fastapi.cookie_and_header import CookieConfig
from supertokens_fastapi.querier import Querier
from supertokens_fastapi.device_info import DeviceInfo
from supertokens_fastapi.handshake_info import HandshakeInfo

INSTALLATION_PATH = environ['SUPERTOKENS_PATH']
SUPERTOKENS_PROCESS_DIR = INSTALLATION_PATH + '/.started'
LICENSE_FILE_PATH = INSTALLATION_PATH + '/licenseKey'
CONFIG_YAML_FILE_PATH = INSTALLATION_PATH + '/config.yaml'
ORIGINAL_LICENSE_FILE_PATH = INSTALLATION_PATH + '/temp/licenseKey'
ORIGINAL_CONFIG_YAML_FILE_PATH = INSTALLATION_PATH + '/temp/config.yaml'
WEB_SERVER_TEMP_DIR = INSTALLATION_PATH + '/webserver-temp'
API_VERSION_TEST_NON_SUPPORTED_SV = ['0.0', '1.0', '1.1', '2.1']
API_VERSION_TEST_NON_SUPPORTED_CV = ['0.1', '0.2', '1.2', '2.0', '3.0']
API_VERSION_TEST_MULTIPLE_SUPPORTED_SV = ['0.0', '1.0', '1.1', '2.1']
API_VERSION_TEST_MULTIPLE_SUPPORTED_CV = ['0.1', '0.2', '1.1', '2.1', '3.0']
API_VERSION_TEST_MULTIPLE_SUPPORTED_RESULT = '2.1'
API_VERSION_TEST_SINGLE_SUPPORTED_SV = ['0.0', '1.0', '1.1', '2.0']
API_VERSION_TEST_SINGLE_SUPPORTED_CV = ['0.1', '0.2', '1.1', '2.1', '3.0']
API_VERSION_TEST_SINGLE_SUPPORTED_RESULT = '1.1'
API_VERSION_TEST_BASIC_RESULT = ['2.0', '2.1']
SUPPORTED_CORE_DRIVER_INTERFACE_FILE = './coreDriverInterfaceSupported.json'
TEST_ENABLE_ANTI_CSRF_CONFIG_KEY = 'enable_anti_csrf'
TEST_ACCESS_TOKEN_PATH_VALUE = '/test'
TEST_ACCESS_TOKEN_PATH_CONFIG_KEY = 'access_token_path'
TEST_REFRESH_TOKEN_PATH_KEY_VALUE = '/refresh'
TEST_REFRESH_TOKEN_PATH_KEY_VALUE_TEST_DECORATOR = '/refresh'
TEST_REFRESH_TOKEN_PATH_CONFIG_KEY = 'refresh_api_path'
TEST_SESSION_EXPIRED_STATUS_CODE_VALUE = 401
TEST_SESSION_EXPIRED_STATUS_CODE_CONFIG_KEY = 'session_expired_status_code'
TEST_COOKIE_DOMAIN_VALUE = 'test.supertokens.io'
TEST_COOKIE_DOMAIN_CONFIG_KEY = 'cookie_domain'
TEST_ACCESS_TOKEN_MAX_AGE_VALUE = 7200  # seconds
TEST_ACCESS_TOKEN_MAX_AGE_CONFIG_KEY = 'access_token_validity'
TEST_REFRESH_TOKEN_MAX_AGE_VALUE = 720  # minutes
TEST_REFRESH_TOKEN_MAX_AGE_CONFIG_KEY = 'refresh_token_validity'
TEST_COOKIE_SAME_SITE_VALUE = 'lax'
TEST_COOKIE_SAME_SITE_CONFIG_KEY = 'cookie_same_site'
TEST_COOKIE_SECURE_VALUE = False
TEST_COOKIE_SECURE_CONFIG_KEY = 'cookie_secure'
TEST_DRIVER_CONFIG_COOKIE_DOMAIN = 'supertokens.io'
TEST_DRIVER_CONFIG_COOKIE_SECURE = False
TEST_DRIVER_CONFIG_COOKIE_SAME_SITE = 'lax'
TEST_DRIVER_CONFIG_ACCESS_TOKEN_PATH = '/custom'
TEST_DRIVER_CONFIG_REFRESH_TOKEN_PATH = '/custom/refresh'
ACCESS_CONTROL_EXPOSE_HEADER = 'Access-Control-Expose-Headers'
ACCESS_CONTROL_EXPOSE_HEADER_ANTI_CSRF_ENABLE = 'id-refresh-token, anti-csrf'
ACCESS_CONTROL_EXPOSE_HEADER_ANTI_CSRF_DISABLE = 'id-refresh-token'
AUTH0_DOMAIN = "dev-3myi6b3e.us.auth0.com"
AUTH0_CLIENT_ID = "wQwadNYL58PoXDTIEiLeBmCe89BnMfiv"
AUTH0_CLIENT_SECRET = "46n7WEAScmrHXukA_w6v1C8uYlVXPvAqEwu5eAyJRD5Wu951BHhiuE_0cQpW5GiV"
TEST_ID_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9' \
                '.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ' \
                '.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c'


def set_key_value_in_config(key, value):
    f = open(CONFIG_YAML_FILE_PATH, 'r')
    data = load(f, Loader=FullLoader)
    f.close()
    data[key] = value
    f = open(CONFIG_YAML_FILE_PATH, 'w')
    dump(data, f)
    f.close()


def __stop_st(retry=50):
    process_ids = __get_list_of_process_ids()
    for pid in process_ids:
        kill(int(pid), SIGTERM)
    process_ids = __get_list_of_process_ids()
    if len(process_ids) != 0:
        if retry == 0:
            raise Exception('')
        sleep(0.5)
        __stop_st(retry - 1)
    sleep(1)


def start_st(host='localhost', port='3567'):
    pid_after = pid_before = __get_list_of_process_ids()
    run('cd ' + INSTALLATION_PATH + ' && java -Djava.security.egd=file:/dev/urandom -classpath '
                                    '"./core/*:./plugin-interface/*" io.supertokens.Main ./ DEV host='
        + host + ' port=' + str(port) + ' &', shell=True, stdout=DEVNULL)
    for _ in range(35):
        pid_after = __get_list_of_process_ids()
        if len(pid_after) != len(pid_before):
            break
        sleep(0.5)
    if len(pid_after) == len(pid_before):
        raise Exception('could not start ST process')


def setup_st():
    copy(ORIGINAL_LICENSE_FILE_PATH, LICENSE_FILE_PATH)
    copy(ORIGINAL_CONFIG_YAML_FILE_PATH, CONFIG_YAML_FILE_PATH)


def clean_st():
    try:
        remove(LICENSE_FILE_PATH)
    except FileNotFoundError:
        pass
    try:
        remove(CONFIG_YAML_FILE_PATH)
    except FileNotFoundError:
        pass
    try:
        rmtree(SUPERTOKENS_PROCESS_DIR)
    except FileNotFoundError:
        pass
    try:
        rmtree(WEB_SERVER_TEMP_DIR)
    except FileNotFoundError:
        pass


def __get_list_of_process_ids():
    process_ids = []
    try:
        processes = scandir(SUPERTOKENS_PROCESS_DIR)
        for process in processes:
            f = open(SUPERTOKENS_PROCESS_DIR + '/' + process.name, 'r')
            process_ids.append(f.read())
            f.close()
    except FileNotFoundError:
        pass
    return process_ids


def reset():
    __stop_st()
    HandshakeInfo.reset()
    DeviceInfo.reset()
    Querier.reset()
    CookieConfig.reset()


def get_cookie_from_response(response, cookie_name):
    cookies = extract_all_cookies(response)
    if cookie_name in cookies:
        return cookies[cookie_name]
    return None


def extract_all_cookies(response: Response):
    cookie_headers = SimpleCookie(response.headers.get('set-cookie'))
    cookies = dict()
    for key, morsel in cookie_headers.items():
        cookies[key] = {
            'value': morsel.value,
            'name': key
        }
        for k, v in morsel.items():
            if (k == 'secure' or k == 'httponly') and v == '':
                cookies[key][k] = None
            elif k == 'samesite':
                cookies[key][k] = v if v[-1] != ',' else v[:-1]
            else:
                cookies[key][k] = v
    return cookies


def get_unix_timestamp(expiry):
    return int(datetime.strptime(
        expiry, '%a, %d %b %Y %H:%M:%S GMT').replace(tzinfo=timezone.utc).timestamp())


def verify_within_5_second_diff(n1, n2):
    return -5 <= (n1 - n2) <= 5
