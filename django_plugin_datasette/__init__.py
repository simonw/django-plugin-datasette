import djp
import datasette
from datasette.utils import sqlite3


ds = None


def get_ds():
    from datasette.app import Datasette

    global ds
    if ds is None:
        from django.conf import settings

        dbs = []
        for database in settings.DATABASES.values():
            if database["ENGINE"] == "django.db.backends.sqlite3":
                dbs.append(str(database["NAME"]))
        ds = Datasette(
            dbs,
            settings={
                "base_url": "/-/datasette/",
            },
        ).app()
    return ds


def redact_password(action, table, column, db_name, trigger_name):
    if action != sqlite3.SQLITE_READ:
        return sqlite3.SQLITE_OK
    if table == "auth_user" and column == "password":
        return sqlite3.SQLITE_IGNORE
    else:
        return sqlite3.SQLITE_OK


@datasette.hookimpl
def prepare_connection(conn, database, datasette):
    conn.set_authorizer(redact_password)


@djp.hookimpl
def asgi_wrapper():
    return wrap


def wrap(app):
    async def wrapper(scope, receive, send):
        await datasette_hello_world_wrapper(scope, receive, send, app)

    return wrapper


async def datasette_hello_world_wrapper(scope, receive, send, app):
    if scope["type"] == "http" and scope["path"] == "/-/datasette":
        # Redirect
        await send(
            {
                "type": "http.response.start",
                "status": 302,
                "headers": [
                    [b"location", b"/-/datasette/"],
                ],
            }
        )
        await send(
            {
                "type": "http.response.body",
                "body": b"",
            }
        )
        return
    if scope["type"] == "http" and scope["path"].startswith("/-/datasette/"):
        ds = get_ds()
        await ds(scope, receive, send)
    else:
        await app(scope, receive, send)
