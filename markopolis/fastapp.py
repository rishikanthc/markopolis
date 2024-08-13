import uvicorn
import fire
from fastapi import FastAPI, HTTPException, Depends, Header, Request, Path, Query
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

logger.add(sys.stdout, format="{time} {level} {message}", level="DEBUG")

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


@app.get("/notes/meta/{path:path}", response_model=D.NoteMeta)
async def get_note_metadata(
    path: str = Path(..., description="The path to the note, including nested folders"),
    api_key: str = Depends(verify_api_key),
):
    logger.info(f"NoteMetadataResource GET request received for path: {path}")
    try:
        metadata = F.get_metadata(path)
        if isinstance(metadata, D.Error):
            raise HTTPException(status_code=404, detail=metadata.error)
        return metadata
    except Exception as e:
        logger.error(f"Error retrieving metadata for path {path}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/notes/toc/{path:path}", response_model=D.ToC)
async def get_note_toc(
    path: str = Path(..., description="The path to the note, including nested folders"),
):
    logger.info(f"NoteToCResource GET request received for path: {path}")
    result = F.get_headings(path)
    if isinstance(result, D.Error):
        raise HTTPException(status_code=404, detail=result.error)
    return result


@app.get("/notes/search/full/{query}", response_model=D.NoteSearchFull)
async def search_notes_full_text(
    query: str = Path(..., description="The search query"),
    max_dist: int = Query(
        default=2, description="Maximum edit distance for fuzzy search"
    ),
):
    logger.info(
        f"Full text search GET request received with query: {query}, max_dist: {max_dist}"
    )
    results = F.search_full(query, max_dist)
    logger.info(f"Search completed. Number of results: {len(results.results)}")
    return results


@app.get("/notes/{path:path}/backlinks", response_model=D.BacklinkList)
async def get_note_backlinks(
    path: str = Path(..., description="The path to the note, including nested folders"),
):
    logger.info(f"NoteBacklinks GET request received for path: {path}")
    result = F.get_backlinks(path)
    if isinstance(result, D.BacklinkList):
        return result
    raise HTTPException(status_code=500, detail="Error retrieving backlinks")


@app.get("/notes/{path:path}/raw", response_model=D.Raw)
async def get_note_raw(
    path: str = Path(..., description="The path to the note, including nested folders"),
):
    logger.info(f"NoteRaw GET request received for path: {path}")
    result = F.get_raw(path)
    if "Error:" in result.contents:
        raise HTTPException(status_code=404, detail=result.contents)
    return result


@app.put("/notes/write")
async def write_notes(notes: D.WriteNotesInput, api_key: str = Depends(verify_api_key)):
    logger.info("WriteNotesResource PUT request received")
    try:
        result = F.write_files(notes.notes)
        if result.status == 200:
            return {"message": "Files created successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to create files")
    except Exception as e:
        logger.exception(f"Unexpected error in write_notes: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


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


@app.get("/{path:path}", response_class=HTMLResponse)
async def get_note_html(request: Request, path: str):
    logger.info(f"Accessing path: {path}")

    try:
        posts = F.list_md()
        meta = F.get_metadata(path)
        content = F.get_note(path)
        toc = F.get_headings(path)

        if isinstance(posts, D.Error):
            logger.warning(f"Error in posts: {posts.error}")
            posts = []
        else:
            posts = posts.files

        if isinstance(content, D.Error):
            logger.error(f"Error in content: {content.error}")
            raise HTTPException(
                status_code=404, detail=f"Content not found: {content.error}"
            )
        else:
            content = content.html

        if isinstance(toc, D.Error):
            logger.warning(f"Error in TOC: {toc.error}")
            toc = None

        if isinstance(meta, D.Error):
            logger.warning(f"Error in metadata: {meta.error}")
            meta = None

        return templates.TemplateResponse(
            "page.html",
            {
                "request": request,
                "posts": posts,
                "meta": meta,
                "content": content,
                "base_url": settings.domain,
                "toc": toc,
                "current_path": path,
            },
        )
    except Exception as e:
        logger.exception(f"Unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


class MarkopolisServer:
    @staticmethod
    def run(host: str = "0.0.0.0", port: int = 8000, reload: bool = True):
        """Run the FastAPI server using Uvicorn."""
        uvicorn.run("markopolis.fastapp:app", host=host, port=port, reload=reload)


def main():
    fire.Fire(MarkopolisServer)


if __name__ == "__main__":
    main()