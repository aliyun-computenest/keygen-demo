import keygen
import constants
import utils


class ActionMeta(type):
    _action_handlers = {}

    def __new__(cls, name, bases, dct):
        new_class = super().__new__(cls, name, bases, dct)
        action_name = dct.get('action_name')
        if action_name:
            cls._action_handlers[action_name] = new_class()
        return new_class

    @classmethod
    def get_action_handlers(cls):
        return cls._action_handlers


class ActionContext:
    def __init__(self):
        constants.Constants.init()
        self.token = constants.Constants.keygen_token
        self.policy_id = constants.Constants.keygen_policy_id


class ActionHandler(metaclass=ActionMeta):
    def execute(self, context, args):
        raise NotImplementedError("Subclasses should implement this method.")


class CreateInstanceHandler(ActionHandler):
    action_name = 'createInstance'

    def execute(self, context, args):
        license_id = keygen.create_license(context.token,
                                           context.policy_id,
                                           args.get('expiredOn'))

        license = keygen.get_license(context.token,
                                     license_id)

        return {
            'instanceId': license.get('data').get('id'),
            'info': {
                'licenseKey':  license.get('data').get('attributes').get('key'),
                'expiredOn': license.get('data').get('attributes').get('expiry')
            }
        }


class RenewInstanceHandler(ActionHandler):
    action_name = 'renewInstance'

    def execute(self, context, args):
        keygen.update_license(context.token, args.get('instanceId'), args.get('expiredOn'))
        return {'success': True}


class ExpireInstanceHandler(ActionHandler):
    action_name = 'expiredInstance'

    def execute(self, context, args):
        keygen.update_license(context.token, args.get('instanceId'), utils.get_current_utc_time())
        return {
            'success': True
        }


class ReleaseInstanceHandler(ActionHandler):
    action_name = 'releaseInstance'

    def execute(self, context, args):
        keygen.delete_license(context.token, args.get('instanceId'))
        return {
            'success': True
        }