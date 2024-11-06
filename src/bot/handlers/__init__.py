"""
Assistant manager handlers.
"""
from .. import callbacks
from .login import auth_method_phone_cb
from .login import auth_method_qr_code_cb
from .login import handle_login_request
from .logout import handle_logout_request
from .settings import handle_settings_request
from .start import handle_start
from .status import handle_status_request

CALLBACK_QUERY_HANDLERS = {
    rf"^{callbacks.AUTH_METHODS_QR_CODE}$": auth_method_qr_code_cb,
    rf"^{callbacks.AUTH_METHODS_PHONE}$": auth_method_phone_cb,
}
COMMAND_HANDLERS = {
    "start": handle_start,
    "login": handle_login_request,
    "logout": handle_logout_request,
    "status": handle_status_request,
    "settings": handle_settings_request,
}

__all__ = ["CALLBACK_QUERY_HANDLERS", "COMMAND_HANDLERS"]
