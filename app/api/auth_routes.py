from flask import Blueprint, jsonify, session, request
from app.models import User, db, Transaction
from app.forms import LoginForm
from app.forms import SignUpForm
from flask_login import current_user, login_user, logout_user, login_required
from functools import reduce

auth_routes = Blueprint('auth', __name__)


def validation_errors_to_error_messages(validation_errors):
    """
    Simple function that turns the WTForms validation errors into a simple list
    """
    errorMessages = []
    for field in validation_errors:
        for error in validation_errors[field]:
            errorMessages.append(f'{field} : {error}')
    return errorMessages


@auth_routes.route('/')
def authenticate():
    """
    Authenticates a user.
    """
    if current_user.is_authenticated:
        print("current_user",current_user)
        user = User.query.get(current_user.id)
        response = user.to_dict()
        response["assets"] = {asset.symbol: asset.to_dict()
                              for asset in user.assets}

        totalStock = sum(
            [asset.quantity * asset.avg_price for asset in user.assets])
        response["totalStock"] = totalStock
        print("response",response)
        return jsonify(response)
    return {'errors': ['Unauthorized']}


@ auth_routes.route('/login', methods=['POST'])
def login():
    """
    Logs a user in
    """
    form = LoginForm()
    # Get the csrf_token from the request cookie and put it into the
    # form manually to validate_on_submit can be used
    print("token......",request.cookies['csrf_token'])
    form['csrf_token'].data = request.cookies['csrf_token']
    if form.validate_on_submit():
        # Add the user to the session, we are logged in!
        user = User.query.filter(User.email == form.data['email']).first()
        login_user(user)

        response = user.to_dict()
        response["assets"] = {asset.symbol: asset.to_dict()
                              for asset in user.assets}

        totalStock = sum(
            [asset.quantity * asset.avg_price for asset in user.assets])

        response["totalStock"] = totalStock

        return jsonify(response)
    return {'errors': validation_errors_to_error_messages(form.errors)}, 401


@ auth_routes.route('/logout')
def logout():
    """
    Logs a user out
    """
    logout_user()
    return {'message': 'User logged out'}


@ auth_routes.route('/signup', methods=['POST'])
def sign_up():
    """
    Creates a new user and logs them in
    """
    form = SignUpForm()
    form['csrf_token'].data = request.cookies['csrf_token']
    if form.validate_on_submit():
        user = User(
            first_name=form.data["first_name"],
            last_name=form.data["last_name"],
            email=form.data['email'],
            password=form.data['password'],
            buying_power=form.data["buying_power"],
            username=form.data["username"]
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)

        response = user.to_dict()
        response["assets"] = {asset.symbol: asset.to_dict()
                              for asset in user.assets}

        totalStock = sum(
            [asset.quantity * asset.avg_price for asset in user.assets])

        response["totalStock"] = totalStock
        return response
    return {'errors': validation_errors_to_error_messages(form.errors)}, 401


@ auth_routes.route('/unauthorized')
def unauthorized():
    """
    Returns unauthorized JSON when flask-login authentication fails
    """
    return {'errors': ['Unauthorized']}, 401
