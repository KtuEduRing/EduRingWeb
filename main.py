from datetime import datetime
import os

from flask import Flask, redirect, url_for, session, request
from flask import render_template  # , make_response, jsonify
from flask import send_from_directory, abort

from authlib.integrations.flask_client import OAuth
from flask_minify import Minify

import secrets
import pytz

from modules.loadconfig import Config
from modules.hash import sha512
from modules import decorators


def load_config() -> None:
    global SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, API_TOKEN_SHA256, FLASK_SECRET_KEY
    global FLASK_HOST, FLASK_PORT, GOOGLE_OAUTH_CLIENT_ID, GOOGLE_OAUTH_CLIENT_SECRET
    global GOOGLE_OAUTH_REDIRECT_URI, EMAIL_DOMAIN, TIMEZONE, GOOGLE

    print("\n-------------------------------------------------")
    print("             Loading config...")
    print("-------------------------------------------------")

    config = Config("config.json")

    # Assigning config values to global variables directly
    SPOTIFY_CLIENT_ID = config.spotify_client_id
    SPOTIFY_CLIENT_SECRET = config.spotify_client_secret
    API_TOKEN_SHA256 = config.api_token_sha256
    FLASK_SECRET_KEY = config.flask_secret_key
    FLASK_PORT = config.flask_port
    FLASK_HOST = config.flask_host
    GOOGLE_OAUTH_CLIENT_ID = config.google_oauth_client_id
    GOOGLE_OAUTH_CLIENT_SECRET = config.google_oauth_client_secret
    GOOGLE_OAUTH_REDIRECT_URI = config.google_oauth_redirect_uri
    EMAIL_DOMAIN = config.email_domain
    TIMEZONE = config.timezone

    # OAuth registration simplified
    GOOGLE = oauth.register(
        name="google",
        client_id=GOOGLE_OAUTH_CLIENT_ID,
        client_secret=GOOGLE_OAUTH_CLIENT_SECRET,
        access_token_url="https://accounts.google.com/o/oauth2/token",
        authorize_url="https://accounts.google.com/o/oauth2/auth",
        api_base_url="https://www.googleapis.com/oauth2/v1/",
        userinfo_endpoint="https://openidconnect.googleapis.com/v1/userinfo",
        client_kwargs={"scope": "email profile"},
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    )


app = Flask(__name__)
oauth = OAuth(app)
Minify(app=app, html=True, js=True, cssless=True)

app.config["MYSQL_USER"] = "user"
app.config["MYSQL_PASSWORD"] = "password"
app.config["MYSQL_DB"] = "database"

app.config["MYSQL_CURSORCLASS"] = "DictCursor"
app.config["MYSQL_CUSTOM_OPTIONS"] = {"ssl": {"ca": "/path/to/ca-file"}}

# 256bit secret key generated every time web server is started
app.secret_key = secrets.token_hex(256)

songs = [
    {"spotify_id": "1158ckiB5S4cpsdYHDB9IF", "votes": 420, "uploader": "GTDT"},
    {"spotify_id": "33tYADyL2aZctrvR59K1bQ", "votes": 69, "uploader": "GTDT"},
    {"spotify_id": "6zeE5tKyr8Nu882DQhhSQI", "votes": 0, "uploader": "GTDT"},
    {"spotify_id": "0g9rT6fMXZoZ2D69p571Q3", "votes": 0, "uploader": "GTDT"},
    {"spotify_id": "44AyOl4qVkzS48vBsbNXaC", "votes": 0, "uploader": "GTDT"},
]


@app.before_request
def handle_every_request():
    print(f"Request.url:  {request.url}\nRequest.form:")
    for key in request.form:
        print(f"  {key}: {request.form.get(key)}")

# -------------------------------------------- #

@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static", "icons"),
        "EduRingx32.ico",
        mimetype="image/vnd.microsoft.icon",
    )

# -------------------------------------------- #

@app.route("/")
def index():
    color_scheme = get_color_scheme()
    message = session.get("login_message", "")
    if "logged_in" not in session:
        return render_template("login.html", message=message, color_scheme=color_scheme)

    session.pop("login_message", None)
    return render_template("index.html", songs=songs, color_scheme=color_scheme)


# Temporary routes for dev
@app.route("/morning")
def morning(): return render_template("index.html", songs=songs, color_scheme="morning")

@app.route("/day")
def day(): return render_template("index.html", songs=songs, color_scheme="day")

@app.route("/evening")
def evening(): return render_template("index.html", songs=songs, color_scheme="evening")

@app.route("/night")
def night(): return render_template("index.html", songs=songs, color_scheme="night")

# -------------------------------------------- #


@app.route("/login")
def login():
    GOOGLE = oauth.create_client("google")
    redirect_uri = url_for("authorize", _external=True)
    return GOOGLE.authorize_redirect(redirect_uri)

@app.route("/authorize")
def authorize():
    GOOGLE = oauth.create_client("google")  # This line is redundant
    token = GOOGLE.authorize_access_token()
    resp = GOOGLE.get("userinfo", token=token)
    userinfo = resp.json()

    if userinfo["email"].endswith(EMAIL_DOMAIN):
        session.update({
            "user_info": userinfo,
            "logged_in": True
        })

        print(f"LOGGED_IN = True\nUSER_INFO: {session['user_info']}")

        return redirect("/")

    session["login_message"] = "Bad email."
    print(f"/authorize: {session['login_message']}")
    return redirect("/")

# -------------------------------------------- #
# ------------------API ROUTES---------------- #
# -------------------------------------------- #

@app.route("/api/v1/submit_song", methods=["POST"])
@decorators.login_required
def submit_song():
    if session.get("logged_in"):
        return abort(200, description="User is authenticated.")

@app.route("/api/v1/logout", methods=["GET", "POST"])
@decorators.login_required
def logout():
    session.clear()
    return render_template("login.html")


# -------------------------------------------- #
# -----------------ADMIN ROUTES--------------- #
# -------------------------------------------- #

@app.route("/api/v1/admin/reload_config", methods=["POST"])
def reload_config():
    token = request.form.get("token")
    if sha512(token.encode('utf-8')).hexdigest() == API_TOKEN_SHA256:
        load_config()
        return abort(200, description="Config reloaded.")
    return abort(404)

# -------------------------------------------- #


def get_color_scheme() -> str:
    # return "evening"
    hour = datetime.now(pytz.timezone(TIMEZONE)).hour
    if 5  <= hour < 12: return "morning"  # noqa: E701
    if 12 <= hour < 16: return "day"  # noqa: E701
    if 16 <= hour < 21: return "evening"  # noqa: E701
    return "night"


if __name__ == "__main__":
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    load_config()

    # file deepcode ignore RunWithDebugTrue: <This is a dev server>
    app.run(
        host=FLASK_HOST,
        port=FLASK_PORT,
        # ssl_context=("local.crt", "local.key"),
        debug=True,
        use_reloader=True,
    )