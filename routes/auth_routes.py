from flask import Blueprint
from controllers.auth_controller import AuthController

auth_bp = Blueprint('auth', __name__)
auth_controller = AuthController()


@auth_bp.route('/login', methods=["GET", "POST"])
def login():
    return auth_controller.login()


@auth_bp.route('/logout')
def logout():
    return auth_controller.logout()


@auth_bp.route('/cadastro', methods=["GET", "POST"])
def cadastro():
    return auth_controller.cadastro()


@auth_bp.route('/verificacao', methods=["GET", "POST"])
def verificacao():
    return auth_controller.verificacao()
