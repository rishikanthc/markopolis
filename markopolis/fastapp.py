import uvicorn
import fire
from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import markopolis.funcs as F
import markopolis.data_dantic as D
from markopolis import settings
import os
import re
from jinja2 import Environment, FileSystemLoader
from loguru import logger
import sys

logger.add(sys.stdout, format="{time} {level} {message}", level="INFO")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[f"{settings.frontend_url}:{settings.frontend_port}"],
    allow_credentials=True,
    allow_methods=["GET", "PUT"],
    allow_headers=["*"],
)

package_dir = os.path.dirname(__file__)
static_dir = os.path.join(package_dir, "static")
fonts_dir = os.path.join(static_dir, "fonts/IBM_Plex")

app.mount("/static", StaticFiles(directory=static_dir), name="static")
app.mount("/fonts", StaticFiles(directory=fonts_dir), name="fonts")

templates_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = Environment(loader=FileSystemLoader(templates_dir))


def slugify(value: str) -> str:
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip()


def add_heading_ids(content: str) -> str:
    def replace(match):
        tag, title = match.groups()
        return f'<{tag} id="{slugify(title)}">{title}</{tag}>'

    pattern = r"<(h[1-6])>(.*?)</\1>"
    return re.sub(pattern, replace, content)


jinja_env.filters["slugify"] = slugify
jinja_env.filters["add_heading_ids"] = add_heading_ids

templates = Jinja2Templates(directory="templates")
templates.env = jinja_env


# Authentication
async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key


# API Routes
@app.get("/hello")
async def hello_world(api_key: str = Depends(verify_api_key)):
    logger.info("HelloWorld GET request received")
    return {"message": "Hello, World!"}


@app.get("/notes/ls", response_model=D.MarkdownFileList)
async def list_notes(api_key: str = Depends(verify_api_key)):
    logger.info("NotesListResource GET request received")
    return F.list_md()


@app.get("/notes/{title}", response_model=D.Note)
async def get_note(title: str):
    logger.info(f"NoteResource GET request received for title: {title}")
    return F.get_note(title)


@app.get("/notes/{title}/meta", response_model=D.NoteMeta)
async def get_note_metadata(title: str):
    logger.info(f"NoteMetadataResource GET request received for title: {title}")
    return F.get_metadata(title)


@app.get("/notes/{title}/toc", response_model=D.ToC)
async def get_note_toc(title: str):
    logger.info(f"NoteToCResource GET request received for title: {title}")
    return F.get_headings(title)


@app.get("/notes/search/{query}", response_model=D.NoteSearch)
async def search_notes(query: str):
    logger.info(f"NoteSearch GET request received with query: {query}")
    return F.search(query, 1)


@app.get("/notes/search/full/{query}", response_model=D.NoteSearchFull)
async def search_notes_full_text(query: str):
    logger.info(f"Full text search GET request received with query: {query}")
    return F.search_full(query, 1)


@app.get("/notes/{title}/backlinks", response_model=D.BacklinkList)
async def get_note_backlinks(title: str):
    logger.info(f"NoteBacklinks GET request received with query: {title}")
    return F.get_backlinks(title)


@app.get("/notes/{title}/raw", response_model=D.Raw)
async def get_note_raw(title: str):
    logger.info(f"NoteRaw GET request received with {title}")
    return F.get_raw(title)


@app.put("/notes/write")
async def write_notes(notes: D.WriteNotesInput, api_key: str = Depends(verify_api_key)):
    logger.info("WriteNotesResource PUT request received")
    result = F.write_files(notes.notes)
    if result.status == 200:
        return {"message": "Files created successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to create files")


@app.get("/healthcheck")
async def health_check():
    health_status = F.health()
    return JSONResponse(content=health_status)


# HTML Routes
@app.get("/", response_class=HTMLResponse)
async def load_page(request: Request):
    posts = F.list_md()
    meta = F.get_metadata("home")
    content = F.get_note("home")

    if not isinstance(posts, D.Error):
        posts = posts.files
    else:
        posts = []

    if not isinstance(content, D.Error):
        content = content.html
    else:
        content = "Error loading content"

    return templates.TemplateResponse(
        "page.html",
        {"request": request, "posts": posts, "meta": meta, "content": content},
    )


@app.get("/{title}", response_class=HTMLResponse)
async def get_note_html(request: Request, title: str):
    posts = F.list_md()
    meta = F.get_metadata(title)
    content = F.get_note(title)
    toc = F.get_headings(title)

    if not isinstance(posts, D.Error):
        posts = posts.files
    else:
        posts = []

    if not isinstance(content, D.Error):
        content = content.html
    else:
        content = content.error

    if isinstance(toc, D.Error):
        toc = toc.error

    return templates.TemplateResponse(
        "page.html",
        {
            "request": request,
            "posts": posts,
            "meta": meta,
            "content": content,
            "base_url": settings.domain,
            "toc": toc,
        },
    )


class MarkopolisServer:
    @staticmethod
    def run(host: str = "0.0.0.0", port: int = 8000, reload: bool = True):
        """Run the FastAPI server using Uvicorn."""
        uvicorn.run("markopolis.fastapp:app", host=host, port=port, reload=reload)


def main():
    fire.Fire(MarkopolisServer)


if __name__ == "__main__":
    main()
