import uvicorn
import fire
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
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


class MarkopolisServer:
    @staticmethod
    def run(host: str = "0.0.0.0", port: int = 8000, reload: bool = True):
        """Run the FastAPI server using Uvicorn."""
        uvicorn.run("markopolis.app:app", host=host, port=port, reload=reload)


def main():
    fire.Fire(MarkopolisServer)


if __name__ == "__main__":
    main()
