import uvicorn
import fire
from fastapi import FastAPI, HTTPException, Depends, Header, Path, Query
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import markopolis.dantic as D
import markopolis.md as M
from markopolis import settings
import os
from loguru import logger
import sys

logger.add(sys.stdout, format="{time} {level} {message}", level="DEBUG")

app = FastAPI(
    title="Markopolis API",
    description="API interface for markopolis",
    version="2.0.1",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        f"{settings.frontend_url}",
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "PUT", "OPTIONS", "DELETE"],
    allow_headers=["*"],
)


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
    if path == "":
        path = "home"
    try:
        # Fetch the frontmatter
        frontmatter = M.get_frontmatter(path)

        # Create an instance of the Frontmatter dataclass
        # frontmatter = D.Frontmatter(**frontmatter_data)

        return frontmatter

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
    # api_key: str = Depends(verify_api_key),
):
    if path == "":
        path = "home"
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
        # Fetch the HTML content
        html_content = M.get_note_html(path)

        # Return as a NoteHtml response model
        return D.NoteHtml(html_content=html_content)
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/{note_path:path}/delete", response_model=D.Status)
async def delete_note(note_path: str, api_key: str = Depends(verify_api_key)):
    # Verify API key using the Depends mechanism
    result = M.delete_file(note_path)

    # Check the deletion result
    if result.status == 0:
        return result
    else:
        raise HTTPException(status_code=404, detail="Note not found or deletion failed")


class MarkopolisServer:
    @staticmethod
    def run(host: str = "0.0.0.0", port: int = 8000, reload: bool = True):
        """Run the FastAPI server using Uvicorn."""
        print(app.openapi())
        uvicorn.run("markopolis.app:app", host=host, port=port, reload=reload)


def main():
    fire.Fire(MarkopolisServer)


if __name__ == "__main__":
    main()
