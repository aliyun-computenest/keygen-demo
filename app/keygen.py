import requests  # 添加requests库
import logging  # 添加logging库
import base64  # 添加base64库
import json
import exception
import constants
import utils
import warnings
import urllib3

url = "https://api.keygen.localhost"
verify_https = False

# 配置日志记录
logging.basicConfig(level=logging.INFO)
warnings.filterwarnings("ignore", category=urllib3.exceptions.InsecureRequestWarning)

def call_http_get(router, headers, params):
    # 记录输入参数
    logging.info(f"Input parameters: {params}")
    # 忽略SSL证书验证
    response = requests.get(url + router, json=params, headers=headers, verify=verify_https)
    if response.status_code == 200:
        if response.text.startswith("{"):
            result = json.loads(response.text)
        else:
            result = 'OK'
    else:
        raise exception.NonSuccessStatusCodeError(response.status_code,
                                                  response.reason)

    # 记录返回结果
    logging.info(f"Output result: {result}")
    return result


def call_http_post(router, headers, params):
    logging.info(f"Input parameters: {params}")
    # 忽略SSL证书验证
    response = requests.post(url + router, json=params, headers=headers, verify=verify_https)
    if response.status_code in [200, 201, 204]:
        result = response.json()
    else:
        raise exception.NonSuccessStatusCodeError(response.status_code,
                                                  response.reason)
    # 记录返回结果
    logging.info(f"Output result: {result}")

    return result


def call_http_patch(router, headers, params):
    logging.info(f"Input parameters: {params}")
    # 忽略SSL证书验证
    response = requests.patch(url + router, json=params, headers=headers, verify=verify_https)
    if response.status_code == 200:
        result = response.json()
    else:
        raise exception.NonSuccessStatusCodeError(response.status_code,
                                                  response.reason)
    # 记录返回结果
    logging.info(f"Output result: {result}")

    return result


def call_http_delete(router, headers):
    # 忽略SSL证书验证
    logging.info(f"Input headers: {headers}")

    response = requests.delete(url + router, headers=headers, verify=verify_https)

    if response.status_code == 204:
        return {}
    else:
        raise exception.NonSuccessStatusCodeError(response.status_code,
                                                  response.reason)


def basic_auth(username, password):
    # 生成Authorization Basic字段
    auth_string = f"{username}:{password}"
    auth_bytes = auth_string.encode('utf-8')
    base64_bytes = base64.b64encode(auth_bytes)
    base64_string = base64_bytes.decode('utf-8')
    return f"Basic {base64_string}"


def bearer_auth(token):
    return f"Bearer {token}"


def initialize_product(username, password, product_name, policy_name):
    r = call_http_post("/v1/tokens", {
        "Authorization": basic_auth(username, password)
    }, {})
    token = r.get('data').get('attributes').get('token')
    product = {"data": {
        "type": "product",
        "attributes": {"name": product_name}
    }}
    r = call_http_post("/v1/products", {
        "Authorization": bearer_auth(token),
        "Content-Type": "application/vnd.api+json",
        "Accept": "application/vnd.api+json"
    }, product)
    product_id = r.get("data").get("id")
    policy = {"data": {
        "type": "policy",
        "attributes": {
            "name": policy_name
        },
        "relationships": {
            "product": {
                "data": {
                    "type": "product",
                    "id": product_id
                }
            }
        }
    }}
    r = call_http_post("/v1/policies", {
        "Authorization": bearer_auth(token),
        "Content-Type": "application/vnd.api+json",
        "Accept": "application/vnd.api+json"
    }, policy)
    d = {
        "KeygenPolicyId": r.get("data").get("id"),
        "KeygenToken": token
    }
    return d


def create_license(token, policy_id, expiry):
    license = {
        "data": {
            "type": "license",
            "attributes": {
                "expiry": expiry
            },
            "relationships": {
                "policy": {
                    "data": {
                        "type": "policy",
                        "id": policy_id
                    }
                }
            }
        }
    }
    r = call_http_post("/v1/licenses", {
        "Authorization": bearer_auth(token),
        "Content-Type": "application/vnd.api+json",
        "Accept": "application/vnd.api+json"
    }, license)
    return r.get('data').get('id')


def delete_license(token, license_id):
    call_http_delete(f'/v1/licenses/{license_id}', {
        "Authorization": bearer_auth(token),
        "Content-Type": "application/vnd.api+json",
        "Accept": "application/vnd.api+json"
    })


def get_license(token, license_id):
    return call_http_get(f'/v1/licenses/{license_id}', {
        "Authorization": bearer_auth(token),
        "Content-Type": "application/vnd.api+json",
        "Accept": "application/vnd.api+json"
    }, {})


def update_license(token, license_id, expiry):
    license = {
        "data": {
            "type": "license",
            "attributes": {
                "expiry": expiry
            }
        }
    }
    return call_http_patch(f'/v1/licenses/{license_id}',{
        "Authorization": bearer_auth(token),
        "Content-Type": "application/vnd.api+json",
        "Accept": "application/vnd.api+json"
    }, license)


def validate_license(license_key):
    license_data = {
        "meta": {
            "key": license_key
        }
    }
    result = call_http_post('/v1/licenses/actions/validate-key',
        {
            "Content-Type": "application/vnd.api+json",
            "Accept": "application/vnd.api+json"
        },
        license_data)
    return result


if __name__ == '__main__':
    constants.Constants.init()

    token = constants.Constants.keygen_token
    policy_id = constants.Constants.keygen_policy_id

    # 创建许可证
    license_id = create_license(token, policy_id, "2025-10-28T00:00:00.000Z")
    print('Create license id: ' + license_id)

    # 获取许可证信息
    license = get_license(token, license_id)
    print(license)
    license_key = license.get('data').get('attributes').get('key')

    # 校验许可证（合法）
    result = validate_license(license_key)
    print('Validate license result code: ' + result.get('meta').get('code'))

    # 更改许可证为过期状态
    update_license(token, license_id, utils.get_current_utc_time())
    license = get_license(token, license_id)
    print(license)

    # 校验许可证（非法）
    result = validate_license(license_key)
    print('Validate license result code: ' + result.get('meta').get('code'))

    # 删除许可证
    delete_license(token, license_id)
