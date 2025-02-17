import json
import logging
from flask import Flask, request

import exception
from actions import ActionMeta
from actions import ActionContext
import utils
import sys
import constants
import argparse
import keygen

app = Flask(__name__)

# 配置日志记录
logging.basicConfig(level=logging.INFO)

@app.before_request
def log_request_info():
    log_data = {
        "Request Method": request.method,
        "Request URL": request.url,
        "Request Headers": dict(request.headers),
        "Request Body": request.get_data(as_text=True)
    }
    logging.info(json.dumps(log_data, ensure_ascii=False))

@app.after_request
def log_response_info(response):
    log_data = {
        "Response Status": response.status,
        "Response Headers": dict(response.headers),
        "Response Body": response.get_data(as_text=True)
    }
    logging.info(json.dumps(log_data, ensure_ascii=False))
    return response


@app.route('/')
def home():
    # 使用结构体解析参数

    action = request.args.get('action')
    # 添加token校验
    constants.Constants.init()
    if not utils.validate_token(request, constants.Constants.secret_key):
        return json.dumps({"error": "Invalid token"}, ensure_ascii=False), 403

    action_handlers = ActionMeta.get_action_handlers()
    handler = action_handlers.get(action)
    if handler:
        context = ActionContext()
        try:
            response = handler.execute(context, request.args)
        except exception.NonSuccessStatusCodeError as e:
            response = {
                'success': 'False',
                'error': e.message
            }

    else:
        response = {
                    'success': False, ''
                    'error': 'Invalid action'
        }
    return json.dumps(response, ensure_ascii=False)


def parse_arguments():
    parser = argparse.ArgumentParser(description="Process some configuration parameters.")
    parser.add_argument('--username', type=str, help='Username (required)')
    parser.add_argument('--password', type=str, help='Password (required)')
    parser.add_argument('--product_name', type=str, default='default', help='Product Name (default: default)')
    parser.add_argument('--policy_name', type=str, default='default', help='Policy Name (default: default)')

    args = parser.parse_args()

    if not args.username:
        parser.error("Username is required.")
    if not args.password:
        parser.error("Password is required.")

    return args


if __name__ == '__main__':
    constants.Constants.init()

    if len(sys.argv) > 1:
        args = parse_arguments()
        result = keygen.initialize_product(args.username, args.password, args.product_name, args.policy_name)
        print(json.dumps(result))
    else:
        app.run(debug=True)


