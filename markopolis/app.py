import uvicorn
import fire
from fastapi import FastAPI, HTTPException, Depends, Header, Path, Request, Query
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import markopolis.dantic as D
import markopolis.md as M
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
    allow_origins=[f"{settings.frontend_url}"],
    allow_credentials=True,
    allow_methods=["GET", "PUT", "OPTIONS"],
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


@app.get("/api/notes/ls", response_model=D.FileTree)
async def list_all_notes():
    return M.list_notes()


@app.put("/api/upload/md")
async def upload_md(mdfiles: D.MDFile, api_key: str = Depends(verify_api_key)):
    md_file_dict = mdfiles.model_dump()
    result = M.write_md_files(md_file_dict)

    if result == 0:
        return {"message": "Files written"}
    else:
        raise HTTPException(status_code=500, detail="Failed to write markdown file")


@app.put("/api/upload/img")
async def upload_img(img_files: D.ImageFile, api_key: str = Depends(verify_api_key)):
    img_file_dict = img_files.model_dump()
    result = M.write_images(img_file_dict)

    if result == 0:
        return {"message": "Files written"}
    else:
        raise HTTPException(status_code=500, detail="Failed to write markdown file")


@app.get("/api/search/{query}", response_model=D.NoteSearchFull)
async def search_notes_full_text(
    query: str = Path(..., description="The search query"),
    max_dist: int = Query(
        default=2, description="Maximum edit distance for fuzzy search"
    ),
):
    logger.info(
        f"Full text search GET request received with query: {query}, max_dist: {max_dist}"
    )
    results = M.fuzzy_search_in_text(query, max_dist)
    logger.info(f"Search completed. Number of results: {len(results.results)}")
    return results


@app.get("/api/{path:path}/frontmatter", response_model=D.Frontmatter)
async def get_frontmatter(
    path: str = Path(..., description="The path to the note, including nested folders"),
    api_key: str = Depends(verify_api_key),
):
    try:
        # Fetch the frontmatter
        frontmatter_data = M.get_frontmatter(path)

        # Create an instance of the Frontmatter dataclass
        frontmatter = D.Frontmatter(**frontmatter_data)

        return JSONResponse(content=frontmatter.model_dump_json())
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/{note_path:path}/backlinks", response_model=D.Backlinks)
async def get_backlinks(note_path: str):
    try:
        # Check if the file exists
        # if not os.path.isfile(note_path + ".md"):
        #     raise HTTPException(status_code=404, detail="Note not found")

        # Call find_backlinks to get the backlinks for the note
        backlinks_object = M.find_backlinks(note_path)

        # Return the backlinks as a JSON response
        return backlinks_object

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/{path:path}/toc", response_model=D.ToC)
async def get_toc_endpoint(
    path: str = Path(..., description="The path to the note, including nested folders"),
    api_key: str = Depends(verify_api_key),
):
    try:
        # Fetch the Table of Contents
        toc_data = M.get_toc(path)

        # Create an instance of the ToC dataclass
        toc = D.ToC(headings=toc_data.headings)

        return JSONResponse(content=toc.model_dump_json())
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/{path:path}", response_model=D.NoteHtml)
async def get_note_html(
    path: str = Path(..., description="The path to the note, including nested folders"),
    api_key: str = Depends(verify_api_key),
):
    try:
        # Fetch the HTML content
        html_content = M.get_note_html(path)

        # Return as a NoteHtml response model
        return D.NoteHtml(html_content=html_content)
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/{path:path}", response_class=HTMLResponse)
async def load_page(request: Request, path: str):
    _cond = (
        path.endswith(".png")
        or path.endswith(".jpg")
        or path.endswith(".jpeg")
        or path.endswith(".gif")
        or path.endswith(".svg")
        or path.endswith(".webp")
    )
    if _cond:
        img_pth = os.path.join(settings.md_path, path)
        return FileResponse(img_pth)
    try:
        frontmatter = M.get_frontmatter(path)
        html_content = M.get_note_html(path)
        notes_list = M.list_notes().model_dump()
        backlinks = M.find_backlinks(path).model_dump()
        toc = M.get_toc(path).model_dump()

        return templates.TemplateResponse(
            "page.html",
            {
                "request": request,
                "frontmatter": frontmatter,
                "content": html_content,
                "site_title": settings.title,
                "notes_list": notes_list,
                "backlinks": backlinks,
                "base_url": settings.domain,
                "toc": toc,
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class MarkopolisServer:
    @staticmethod
    def run(host: str = "0.0.0.0", port: int = 8000, reload: bool = True):
        """Run the FastAPI server using Uvicorn."""
        uvicorn.run("markopolis.app:app", host=host, port=port, reload=reload)


def main():
    fire.Fire(MarkopolisServer)


if __name__ == "__main__":
    main()
