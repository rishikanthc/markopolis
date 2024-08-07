import falcon
from loguru import logger
from falcon_cors import CORS
import markpi.funcs as F
import json
from markpi import settings
from functools import wraps
import sys

allowed_origins = [settings.frontend_url + f":{settings.frontend_port}"]
# Configure CORS middleware
cors = CORS(
    allow_origins_list=allowed_origins,  # Replace with your SvelteKit dev server port
    allow_all_headers=True,
    allow_all_methods=True,
)


class AuthMiddleware:
    def process_request(self, req, resp):
        api_key = req.get_header("X-API-Key")
        if not api_key or not self.is_valid_api_key(api_key):
            raise falcon.HTTPUnauthorized("Authentication required")

    @staticmethod
    def is_valid_api_key(api_key):
        # Implement your API key validation logic here
        # For example, check against a database or a predefined list
        return api_key == settings.api_key  # Assume you've added this to your settings


def auth_required(func):
    @wraps(func)
    def wrapper(self, req, resp, *args, **kwargs):
        origin = req.get_header("Origin")
        if origin and origin in allowed_origins:
            return func(self, req, resp, *args, **kwargs)

        api_key = req.get_header("X-API-Key")
        if not api_key or not AuthMiddleware.is_valid_api_key(api_key):
            raise falcon.HTTPUnauthorized("Authentication required")
        return func(self, req, resp, *args, **kwargs)

    return wrapper


app = application = falcon.App(middleware=[cors.middleware])

# Configure Loguru logger
logger.add(sys.stdout, format="{time} {level} {message}", level="INFO")


class HelloWorld:
    @auth_required
    def on_get(self, req, resp):
        """Handles GET requests"""
        logger.info("HelloWorldResource GET request received")
        resp.media = {"message": "Hello, World!"}


# API Resources
class NotesListResource:
    @auth_required
    def on_get(self, req, resp):
        logger.info("NotesListResource GET request received")
        notes = F.list_md()
        if notes is not None:
            resp.text = notes.model_dump_json()
            resp.content_type = falcon.MEDIA_JSON
            resp.status = falcon.HTTP_200
        else:
            resp.text = json.dumps({"error": "Failed to retrieve notes list"})
            resp.content_type = falcon.MEDIA_JSON
            resp.status = falcon.HTTP_500


class NoteResource:
    def on_get(self, req, resp, title):
        logger.info(f"NoteResource GET request received for title: {title}")
        note = F.get_note(title)
        if note is not None:
            resp.text = note.model_dump_json()
            resp.content_type = falcon.MEDIA_JSON
            resp.status = falcon.HTTP_200
        else:
            resp.text = json.dumps({"error": f"Note '{title}' not found"})
            resp.content_type = falcon.MEDIA_JSON
            resp.status = falcon.HTTP_404


class NoteMetadataResource:
    def on_get(self, req, resp, title):
        logger.info(f"NoteMetadataResource GET request received for title: {title}")
        metadata = F.get_metadata(title)
        if metadata is not None:
            resp.text = metadata.model_dump_json()
            resp.content_type = falcon.MEDIA_JSON
            resp.status = falcon.HTTP_200
        else:
            resp.text = json.dumps({"error": f"Metadata for note '{title}' not found"})
            resp.content_type = falcon.MEDIA_JSON
            resp.status = falcon.HTTP_404


class NoteToCResource:
    def on_get(self, req, resp, title):
        logger.info(f"NoteToCResource GET request received for title: {title}")
        toc = F.get_headings(title)
        if toc is not None:
            resp.text = toc.model_dump_json()
            resp.content_type = falcon.MEDIA_JSON
            resp.status = falcon.HTTP_200
        else:
            resp.text = json.dumps(
                {"error": f"Table of contents for note '{title}' not found"}
            )
            resp.content_type = falcon.MEDIA_JSON
            resp.status = falcon.HTTP_404


class NoteSearch:
    def on_get(self, req, resp, query):
        logger.info(f"NoteSearch GET request received with query: {query}")
        matches = F.search(query, 1)

        resp.text = matches.model_dump_json()
        resp.content_type = falcon.MEDIA_JSON
        resp.status = falcon.HTTP_200


class NoteBacklinks:
    def on_get(self, req, resp, title):
        logger.info(f"NoteBacklinks GET request received with query: {title}")
        backlinks = F.get_backlinks(title)

        if backlinks is not None:
            resp.text = backlinks.model_dump_json()
            resp.content_type = falcon.MEDIA_JSON
            resp.status = falcon.HTTP_200


class NoteRaw:
    def on_get(self, req, resp, title):
        logger.info(f"NoteRaw GET request received with {title}")
        contents = F.get_raw(title)

        resp.text = contents.model_dump_json()
        resp.content_type = falcon.MEDIA_JSON
        resp.status = falcon.HTTP_200


# Routes
app.add_route("/hello", HelloWorld())
app.add_route("/notes/ls", NotesListResource())
app.add_route("/notes/{title}", NoteResource())
app.add_route("/notes/{title}/meta", NoteMetadataResource())
app.add_route("/notes/{title}/toc", NoteToCResource())
app.add_route("/notes/search/{query}", NoteSearch())
app.add_route("/notes/{title}/backlinks", NoteBacklinks())
app.add_route("/notes/{title}/raw", NoteRaw())
