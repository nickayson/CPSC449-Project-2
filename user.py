from pydoc import doc
import databases
import collections
import dataclasses
import sqlite3
import textwrap
import toml

from quart import Quart, g, request, abort
from quart_schema import QuartSchema, RequestSchemaValidationError, validate_request

app = Quart(__name__)
QuartSchema(app)

app.config.from_file(f"./etc/{__name__}.toml", toml.load)


@dataclasses.dataclass
class User:
    first_name: str
    last_name: str
    user_name: str
    password: str


async def _connect_db():
    database = databases.Database(app.config["DATABASES"]["URL"])
    await database.connect()
    return database


def _get_db():
    if not hasattr(g, "sqlite_db"):
        g.sqlite_db = _connect_db()
    return g.sqlite_db


@app.teardown_appcontext
async def close_connection(exception):
    db = getattr(g, "_sqlite_db", None)
    if db is not None:
        await db.disconnect()

@app.route("/", methods=["GET"])
def index():
    return textwrap.dedent(
        """
        <h1>Wordle users microservice</h1>
        """
    )


@app.route("/users/", methods=["POST"])
@validate_request(User)
async def create_user(data):
    db = await _get_db()
    user = dataclasses.asdict(data)
    try:
        #Attempt to create new user in database
        id = await db.execute(
            """
            INSERT INTO user(fname, lname, username, passwrd)
            VALUES(:first_name, :last_name, :user_name, :password)
            """,
            user,
        )
    #Return 409 error if username is already in table
    except sqlite3.IntegrityError as e:
        abort(409, e)

    user["id"] = id
    return user, 201

# User authentication endpoint
@app.route("/user-auth/", methods=["GET"])
async def userAuth():
    auth = request.authorization
    db = await _get_db()
    if auth == None:
        return {"Error": "User not verified"}, 401, {'WWW-Authenticate': 'Basic realm = "Login required"'}
    # Selection query with raw queries
    select_query = "SELECT * FROM user WHERE username= :username AND passwrd= :password"
    values = {"username": auth["username"], "password": auth["password"]}

    # Run the command
    result = await db.fetch_one( select_query, values )

    # Is the user registered?
    if result:
        return { "authenticated": "true" }, 200
    else:
        return {"Error": "User not verified"}, 401, {'WWW-Authenticate': 'Basic realm = "Login required"'}


@app.errorhandler(409)
def conflict(e):
    return {"error": str(e)}, 409