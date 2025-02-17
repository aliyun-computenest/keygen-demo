
import hashlib
import datetime  # 添加导入datetime模块


def validate_token(request, key):
    # 获取所有GET参数，不包括token
    params = {k: v for k, v in request.args.items() if k != 'token'}
    # 按字典顺序排序参数
    sorted_params = sorted(params.items())
    # 将参数拼接成字符串，不使用urlencode
    query_string = '&'.join(f"{k}={v}" for k, v in sorted_params)
    # 拼接密钥
    query_string_with_key = f"{query_string}&key={key}"
    # 计算MD5哈希
    expected_token = hashlib.md5(query_string_with_key.encode()).hexdigest()
    # 获取请求中的token
    request_token = request.args.get('token')
    # 比较token
    return expected_token == request_token


# 添加获取当前UTC时间的函数
def get_current_utc_time():
    return datetime.datetime.utcnow().isoformat()
