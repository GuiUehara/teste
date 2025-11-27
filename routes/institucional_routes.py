from flask import Blueprint, render_template

institucional_bp = Blueprint('institucional', __name__)

@institucional_bp.route('/sobre')
def sobre():
    return render_template('sobre.html')

@institucional_bp.route('/contato')
def contato():
    return render_template('contato.html')

@institucional_bp.route('/termos')
def termos():
    return render_template('termos.html')

@institucional_bp.route('/privacidade')
def privacidade():
    return render_template('privacidade.html')