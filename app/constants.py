import configparser
import os

class Constants:
    secret_key = ''
    keygen_token = ''
    keygen_policy_id = ''

    @classmethod
    def init(cls):
        config = configparser.ConfigParser()
        script_path = os.path.dirname(os.path.abspath(__file__))
        config_file = os.path.join(script_path, "../conf/env.properties")
        config.read(config_file)

        cls.keygen_token = config.get('DEFAULT', 'KeygenToken')
        cls.keygen_policy_id = config.get('DEFAULT', 'KeygenPolicyId')