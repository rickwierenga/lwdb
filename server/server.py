import http
import json
import os
import uuid

from flask import Blueprint, jsonify, current_app, Flask, request, redirect, url_for, flash, render_template
from flask_bcrypt import Bcrypt
from flask_login import login_required, current_user, login_user, LoginManager
from flask_bcrypt import check_password_hash, generate_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Email, Length, ValidationError

import db
from models import LabwareDefinition, DefaultVersion, User

app = Flask(__name__, template_folder="templates", static_folder="static")
if "SECRET_KEY" in os.environ:
  app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
elif "SECRET_KEY_FILE" in os.environ:
  with open(os.environ["SECRET_KEY_FILE"], encoding="utf-8") as skf:
    app.config["SECRET_KEY"] = skf.read()
else:
  raise Exception("No secret key specified")
app.config["LABWARE_DIR"] = os.environ.get("LABWARE_DIR", "labware")
os.makedirs(app.config["LABWARE_DIR"], exist_ok=True)

dbs = db.get_session()

bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
  return User.query.get(user_id)

@login_manager.unauthorized_handler
def unauthorized():
  if request.headers.get("Accept") == "application/json":
    return jsonify({"error": "Unauthorized"}), http.HTTPStatus.UNAUTHORIZED
  return redirect(url_for('login'))


@app.route("/")
def index():
  return "<h1 style='background-color: #f3ce13'>LWDb</h1>"


api = Blueprint("api", __name__, url_prefix="/api/v1")


@api.route("/labware/<string:name>")
def get(name):
  # get default labware definition for this name
  default = DefaultVersion.query.filter_by(name=name).first()
  if default is None:
    return jsonify({"error": "Not found"}), http.HTTPStatus.NOT_FOUND
  ld = default.definition
  return jsonify(ld.serialize(base_dir="."))


NUM_PER_PAGE = 20
@api.route("/labware")
def get_all():
  page = int(request.args.get("page", 1))

  if page < 1:
    return jsonify({"error": "Invalid page number"}), 400

  # Get all default labware definitions
  base_query = dbs.query(DefaultVersion).order_by(DefaultVersion.updated_on)
  defaults = base_query.limit(NUM_PER_PAGE).offset((page - 1) * NUM_PER_PAGE).all()
  has_next = base_query.limit(1).offset(page * NUM_PER_PAGE).first() is not None

  return jsonify(
    labware=[d.definition.serialize(base_dir=".") for d in defaults],
    has_next=has_next)


@api.route("/labware", methods=["POST"])
@login_required
def create():
  data = request.get_json()

  name = data.get("name")
  if name is None:
    return jsonify({"error": "Missing name"}), 400

  definition = data.get("definition")
  if definition is None:
    return jsonify({"error": "Missing definition"}), 400

  # if user has already uploaded a definition for this labware, throw an error
  if dbs.query(LabwareDefinition) \
    .filter(LabwareDefinition.author_id == current_user.id) \
    .filter(LabwareDefinition.name == name).first() is not None:
    return jsonify({
      "error": "You have already uploaded a labware definition for this labware"
    }), 403

  # Always save as a variation
  id_ = str(uuid.uuid4())
  dirs = os.path.join(current_app.config["LABWARE_DIR"], name)
  os.makedirs(dirs, exist_ok=True)
  path = os.path.join(dirs, f"{id_}.json")
  with open(path, "w", encoding="utf-8") as f:
    f.write(json.dumps(definition, indent=2))

  ld = LabwareDefinition(
    id=id_,
    name=name,
    path=path,
    author_id=current_user.id
  )

  # If no default definition exists yet, create a labware definition for it
  if dbs.query(DefaultVersion).filter(DefaultVersion.name == ld.name).first() is None:
    default_version = DefaultVersion()
    default_version.name = ld.name
    default_version.definition = ld
    dbs.add(default_version)

  dbs.add(ld)

  try:
    dbs.commit()
    return jsonify(ld.serialize(base_dir="."))
  except Exception as e:
    current_app.logger.error(e)
    dbs.rollback()
    return jsonify({"error": str(e)}), 500


app.register_blueprint(api)


@app.route("/login", methods=["GET", "POST"])
def login():
  if request.method == "POST":
    if request.headers.get("Content-Type") == "application/json":
      data = request.json
      email = data.get("email")
      password = data.get("password")
    else:
      email = request.form.get("email")
      password = request.form.get("password")

    user = User.query.filter_by(email=email).first()
    if user is not None and check_password_hash(user.password_hash, password):
      login_user(user, remember=True)
      if request.headers.get("Accept") == "application/json":
        return jsonify(user.serialize())
      else:
        return "OK"

    if request.headers.get("Accept") == "application/json":
      return jsonify({"error": "Invalid email or password"}), 401
    else:
      flash("Invalid email or password", "danger")

  return render_template("login.html")


class SignUpForm(FlaskForm):
  # pylint: disable=no-self-argument

  email = StringField("Email", validators=[DataRequired(), Email(), Length(min=1, max=255)])
  password = StringField("Password", validators=[DataRequired(), Length(min=10)])

  def validate_email(form, email):
    if User.query.filter_by(email=email.data).count() > 0:
      raise ValidationError("Email already in use")


@app.route("/register", methods=["GET", "POST"])
def register():
  form = SignUpForm()

  if form.validate_on_submit():
    email = form.email.data
    password = form.password.data

    password_hash = generate_password_hash(password).decode("utf-8")
    user = User(
      email=email,
      password_hash=password_hash,
    )

    dbs.add(user)
    try:
      dbs.commit()
    except Exception as e:
      dbs.rollback()
      current_app.logger.error(e)
      return jsonify({"error": "Could not sign up user"}), 500

    login_user(user, remember=True)

    return "OK"
  else:
    print(form.errors)
    # will be rendered by the template

  return render_template("signup.html", form=form)
