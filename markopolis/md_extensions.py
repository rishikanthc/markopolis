import markdown
from markdown.inlinepatterns import InlineProcessor
import xml.etree.ElementTree as etree
from markdown.preprocessors import Preprocessor
from markdown.postprocessors import Postprocessor
from markdown.extensions import Extension
import re
from loguru import logger
import sys

logger.remove()
logger.add(sys.stdout, level="DEBUG")


# Custom inline pattern for obsidian style images
class ObsidianImageInlineProcessor(InlineProcessor):
    def handleMatch(self, m, data):
        img_src = m.group(1).strip()
        img_tag = etree.Element("img")
        img_tag.set("src", f"/images/{img_src}")
        return img_tag, m.start(0), m.end(0)


class ObsidianImageExtension(markdown.extensions.Extension):
    def extendMarkdown(self, md):
        IMAGE_PATTERN = r"!\[\[(.+?)\]\]"
        image_processor = ObsidianImageInlineProcessor(IMAGE_PATTERN, md)
        md.inlinePatterns.register(image_processor, "obsidian_image", 175)


class StrikethroughInlineProcessor(InlineProcessor):
    def handleMatch(self, m, data):
        strikethrough_text = m.group(1).strip()
        del_tag = etree.Element("del")
        del_tag.text = strikethrough_text
        return del_tag, m.start(0), m.end(0)


class StrikethroughExtension(markdown.extensions.Extension):
    def extendMarkdown(self, md):
        STRIKE_PATTERN = r"~~(.*?)~~"
        strikethrough_processor = StrikethroughInlineProcessor(STRIKE_PATTERN, md)
        md.inlinePatterns.register(strikethrough_processor, "strikethrough", 175)


class HighlightInlineProcessor(InlineProcessor):
    def handleMatch(self, m, data):
        highlighted_text = m.group(1).strip()
        mark_tag = etree.Element("mark")
        mark_tag.text = highlighted_text
        return mark_tag, m.start(0), m.end(0)


class HighlightExtension(markdown.extensions.Extension):
    def extendMarkdown(self, md):
        HIGHLIGHT_PATTERN = r"==(.*?)=="
        highlight_processor = HighlightInlineProcessor(HIGHLIGHT_PATTERN, md)
        md.inlinePatterns.register(highlight_processor, "highlight", 175)


class FootnotePreprocessor(Preprocessor):
    def __init__(self, md):
        super().__init__(md)
        self.footnotes = {}

    def run(self, lines):
        new_lines = []
        footnote_pattern = re.compile(r"^\[\^([^\]]+)\]:\s*(.*)")

        current_footnote = None
        for line in lines:
            footnote_match = footnote_pattern.match(line)
            if footnote_match:
                current_footnote = footnote_match.group(1)
                self.footnotes[current_footnote] = footnote_match.group(2)
            elif current_footnote and line.startswith("  "):
                # Handle multiline footnotes
                self.footnotes[current_footnote] += "\n" + line.strip()
            else:
                current_footnote = None
                new_lines.append(line)

        return new_lines


class FootnotePostprocessor(Postprocessor):
    def __init__(self, md, footnotes):
        super().__init__(md)
        self.footnotes = footnotes

    def run(self, text):
        # Convert references to footnotes
        footnote_ref_pattern = re.compile(r"\[\^([^\]]+)\]")
        text = footnote_ref_pattern.sub(self.convert_reference, text)

        # Add footnotes at the end of the document
        if self.footnotes:
            text += "\n<hr>\n<div class='footnotes'>\n"
            for i, (_, note) in enumerate(self.footnotes.items(), start=1):
                text += f"<p id='fn-{i}'><sup>{i}</sup> {note}</p>\n"
            text += "</div>\n"
        return text

    def convert_reference(self, match):
        key = match.group(1)
        index = list(self.footnotes.keys()).index(key) + 1
        return f"<sup id='fnref-{index}'><a href='#fn-{index}'>{index}</a></sup>"


class FootnoteExtension(Extension):
    def extendMarkdown(self, md):
        # Preprocessor collects the footnotes
        footnote_preprocessor = FootnotePreprocessor(md)
        md.preprocessors.register(footnote_preprocessor, "footnote_preprocessor", 25)

        # Postprocessor converts the references and appends the footnotes
        footnote_postprocessor = FootnotePostprocessor(
            md, footnote_preprocessor.footnotes
        )
        md.postprocessors.register(footnote_postprocessor, "footnote_postprocessor", 25)


class MermaidPreprocessor(Preprocessor):
    def run(self, lines):
        new_lines = []
        is_mermaid_block = False
        mermaid_lines = []

        for line in lines:
            if line.strip() == "```mermaid":
                is_mermaid_block = True
                mermaid_lines = []
            elif line.strip() == "```" and is_mermaid_block:
                is_mermaid_block = False
                mermaid_content = "\n".join(mermaid_lines)
                mermaid_html = self.mermaid_to_html(mermaid_content)
                new_lines.append(mermaid_html)
            elif is_mermaid_block:
                mermaid_lines.append(line)
            else:
                new_lines.append(line)

        return new_lines

    def mermaid_to_html(self, mermaid_content):
        escaped_content = mermaid_content.replace('"', "&quot;")
        return f'<div class="mermaid">{escaped_content}</div>'


class MermaidExtension(Extension):
    def extendMarkdown(self, md):
        md.preprocessors.register(MermaidPreprocessor(md), "mermaid", 175)


# Regular expression to match Obsidian callout syntax
CalloutRegex = re.compile(
    r"^>\s*\[!(?P<type>[a-zA-Z]+)\](?P<collapsible>[\+\-])?\s*(?P<title>.*)$"
)

# Mapping of aliases to their primary callout types
CALLOUT_ALIASES = {
    "summary": "abstract",
    "tldr": "abstract",
    "check": "success",
    "done": "success",
    "help": "question",
    "faq": "question",
    "caution": "warning",
    "attention": "warning",
    "fail": "failure",
    "missing": "failure",
    "error": "danger",
    "cite": "quote",
}


class CalloutPreprocessor(Preprocessor):
    def run(self, lines):
        new_lines = []
        in_callout = False
        callout_type = ""
        is_collapsible = False
        is_expanded = False

        for line in lines:
            # Match the start of a callout block
            callout_match = CalloutRegex.match(line)
            if callout_match:
                callout_type = callout_match.group("type").lower()
                # Check if the callout type is an alias and replace it with the primary type
                callout_type = CALLOUT_ALIASES.get(callout_type, callout_type)

                collapsible = callout_match.group("collapsible")
                is_collapsible = collapsible is not None
                is_expanded = collapsible == "+"

                title = callout_match.group("title").strip()

                classes = f"callout {callout_type}"
                if is_collapsible:
                    classes += " collapsible"
                    if is_expanded:
                        classes += " expanded"

                new_lines.append(f'<div class="{classes}">')
                new_lines.append('<div class="callout-title">')
                if is_collapsible:
                    new_lines.append('<div class="callout-fold"></div>')
                if title:
                    new_lines.append(
                        f'<span class="callout-title-inner">{title}</span>'
                    )
                new_lines.append("</div>")
                new_lines.append('<div class="callout-content">')
                in_callout = True
            elif in_callout:
                if line.startswith("> "):
                    # Strip the '> ' and add the line to the callout content
                    content = line[2:].strip()
                    if content:
                        new_lines.append(content)
                else:
                    # End the callout block and append the current line outside the callout
                    new_lines.append("</div></div>")
                    new_lines.append(line)
                    in_callout = False
            else:
                new_lines.append(line)

        # Ensure any unclosed callout blocks are closed
        if in_callout:
            new_lines.append("</div></div>")

        return new_lines


class CalloutExtension(Extension):
    def extendMarkdown(self, md):
        md.preprocessors.register(CalloutPreprocessor(md), "callout", 35)


# Usage
if __name__ == "__main__":
    md_text = "Here is an image ![[image.png]]"
    md = markdown.Markdown(extensions=[ObsidianImageExtension()])
    html = md.convert(md_text)
    print(html)
