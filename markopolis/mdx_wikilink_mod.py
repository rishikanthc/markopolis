"""
WikiLinkPlus Extension for Python-Markdown
===========================================

Converts [[WikiLinks]] to relative links.

See <https://github.com/neurobin/mdx_wikilink_plus> for documentation.

Copyright Md. Jahidul Hamid <jahidulhamid@yahoo.com>

License: [BSD](http://www.opensource.org/licenses/bsd-license.php)

"""

from urllib.parse import urlparse, urlunparse, ParseResult
from typing import Union
from markdown import Markdown
from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor
import xml.etree.ElementTree as etree
import re
import os
from typing import Dict, Any

WIKILINK_PLUS_RE = r"(!)?(?:\[\[\s*(?P<target>[^][|]+?)(\s*\|\s*(?P<label>[^][]+))?\s*\]\]|\[(?P<alt>[^][]*)?\]\((?P<url>[^)]+)\))"


def build_url(
    urlo: Union[str, ParseResult],
    base: str,
    end: str,
    url_whitespace: str,
    url_case: str,
) -> str:
    """Build and return a valid url."""
    if isinstance(urlo, str):
        urlo = urlparse(urlo)

    if not urlo.netloc:
        if not end:
            clean_target = re.sub(r"\s+", url_whitespace, urlo.path)
        else:
            clean_target = re.sub(r"\s+", url_whitespace, urlo.path.rstrip("/"))
            if clean_target.endswith(end):
                end = ""
        if base.endswith("/"):
            path = f"{base}{clean_target.lstrip('/')}{end}"
        elif base and not clean_target.startswith("/"):
            path = f"{base}/{clean_target}{end}"
        else:
            path = f"{base}{clean_target}{end}"
        if url_case == "lowercase":
            urlo = urlo._replace(path=path.lower())
        elif url_case == "uppercase":
            urlo = urlo._replace(path=path.upper())
        else:
            urlo = urlo._replace(path=path)
    return urlunparse(urlo)


def title(subject: str) -> str:
    """Return title cased version of the given subject string"""
    exceptions = [
        "a",
        "an",
        "the",
        "v",
        "vs",
        "am",
        "at",
        "and",
        "as",
        "but",
        "by",
        "en",
        "for",
        "if",
        "be",
        "in",
        "of",
        "on",
        "or",
        "to",
        "via",
    ]
    words = [word for word in re.split(r"[ \t]+", subject) if word]
    return " ".join(
        word
        if (re.match(r"^[^a-z]+$", word) or (word in exceptions and i != 0))
        else word.title()
        for i, word in enumerate(words)
    )


class WikiLinkPlusExtension(Extension):
    def __init__(self, **kwargs: Any):
        self.config = {
            "base_url": ["", "String to append to beginning or URL."],
            "end_url": ["", "String to append to end of URL."],
            "url_whitespace": ["-", "String to replace white space in the URL"],
            "label_case": ["titlecase", "Other valid values are: capitalize and none"],
            "url_case": ["none", "Other valid values are: lowercase and uppercase"],
            "html_class": ["wikilink", "CSS hook. Leave blank for none."],
            "image_class": ["wikilink-image", "CSS hook. Leave blank for none."],
            "build_url": [build_url, "Callable formats URL from label."],
        }
        super().__init__(**kwargs)
        print("wikilink plus extension")

    def extendMarkdown(self, md: Markdown) -> None:
        md.inlinePatterns.register(
            WikiLinkPlusPattern(self.getConfigs(), md), "wikilink_plus", 75
        )


class WikiLinkPlusPattern(InlineProcessor):
    def __init__(self, config: Dict[str, Any], md: Markdown):
        super().__init__(WIKILINK_PLUS_RE, md)
        self.config = config

    def handleMatch(self, m: re.Match, data: str) -> tuple:
        d = m.groupdict()
        is_explicit_image = bool(m.group(1))  # Check if the match starts with '!'
        target = d.get("target") or d.get("url")
        label = d.get("label") or d.get("alt") or ""
        print("wikilink handle match")

        if target:
            (
                base_url,
                end_url,
                url_whitespace,
                url_case,
                label_case,
                html_class,
                image_class,
            ) = self._getMeta()

            # Always parse the target URL
            urlo = urlparse(target)

            # Apply base_url if there's no scheme (relative URL)
            if not urlo.scheme:
                urlo = urlparse(f"{base_url.rstrip('/')}/{target.lstrip('/')}")

            clean_path = urlo.path.rstrip("/")

            if not label and clean_path:
                label = re.sub(
                    r"[\s_-]+", " ", re.sub(r"\..*$", "", os.path.basename(clean_path))
                ).strip()
                if label_case.lower() == "titlecase":
                    label = title(label)
                elif label_case.lower() == "capitalize":
                    label = label.capitalize()

            # Image Handling Logic (Standard Markdown Images)
            checkurl = urlo.path if urlo.path and urlo.path != "/" else urlo.netloc
            is_image = is_explicit_image or any(
                checkurl.lower().endswith(suffix)
                for suffix in [".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"]
            )

            # Always use build_url for consistency
            url = self.config["build_url"](
                urlo,
                base_url,
                end_url if not is_image else "",
                url_whitespace,
                url_case,
            )

            # Handling both types of links (WikiLinks and Standard Markdown Links)
            if not is_image:
                a = etree.Element("a")
                a.text = label or target
                a.set("href", url)
                if html_class:
                    a.set("class", html_class)
            else:
                a = etree.Element("img")
                a.set("alt", label)
                a.set("src", url)
                if image_class:
                    a.set("class", image_class)

            return a, m.start(0), m.end(0)

    def _getMeta(self):
        base_url = self.config["base_url"]
        end_url = self.config["end_url"]
        url_whitespace = self.config["url_whitespace"]
        label_case = self.config["label_case"]
        url_case = self.config["url_case"]
        html_class = self.config["html_class"]
        image_class = self.config["image_class"]

        # Safely get the Meta attribute, defaulting to an empty dict if it doesn't exist
        meta = getattr(self.md, "Meta", {})

        if meta:
            base_url = meta.get("wiki_base_url", [base_url])[0]
            end_url = meta.get("wiki_end_url", [end_url])[0]
            url_whitespace = meta.get("wiki_url_whitespace", [url_whitespace])[0]
            label_case = meta.get("wiki_label_case", [label_case])[0]
            url_case = meta.get("wiki_url_case", [url_case])[0]
            html_class = meta.get("wiki_html_class", [html_class])[0]
            image_class = meta.get("wiki_image_class", [image_class])[0]

        return (
            base_url,
            end_url,
            url_whitespace,
            url_case,
            label_case,
            html_class,
            image_class,
        )


def makeExtension(**kwargs) -> WikiLinkPlusExtension:
    return WikiLinkPlusExtension(**kwargs)


def test_wikilink_plus():
    from markdown import Markdown

    # Test configuration
    wikilink_config = {
        "base_url": "http://localhost:8000/api/",
        "end_url": "",
        "html_class": "wikilink",
        "image_class": "wikilink-image",
    }

    # Create a Markdown instance with our extension
    md = Markdown(extensions=[WikiLinkPlusExtension(**wikilink_config)])

    # Test cases
    test_cases = [
        # (
        #     "![[image.png]]",
        #     '<p><img alt="Image" class="wikilink-image" src="http://localhost:8000/api/image.png"></p>',
        # ),
        # (
        #     "![[test.webp]]",
        #     '<p><img alt="Test" class="wikilink-image" src="http://localhost:8000/api/test.webp"></p>',
        # ),
        (
            "![](image.png)",
            '<p><img alt="" class="wikilink-image" src="http://localhost:8000/api/image.png"></p>',
        ),
        (
            "![Alt text](image.jpg)",
            '<p><img alt="Alt text" class="wikilink-image" src="http://localhost:8000/api/image.jpg"></p>',
        ),
        # (
        #     "[[regular link]]",
        #     '<p><a class="wikilink" href="http://localhost:8000/api/regular link">Regular link</a></p>',
        # ),
    ]

    for input_text, expected_output in test_cases:
        result = md.convert(input_text)
        print(result)
        # assert (
        #     result.strip() == expected_output
        # ), f"Test failed for input: {input_text}\nExpected: {expected_output}\nGot: {result}"


if __name__ == "__main__":
    test_wikilink_plus()
