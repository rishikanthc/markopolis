import markdown
import string
from markdown.inlinepatterns import InlineProcessor
import xml.etree.ElementTree as etree
from markdown.preprocessors import Preprocessor
from markdown.postprocessors import Postprocessor
from markdown.extensions import Extension
import re


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


def strip_not_printable(text):
    """Remove non-printable characters from a string."""
    return "".join(filter(lambda x: x in string.printable, text))


# This regex matches the opening line for a mermaid code block in Obsidian's syntax.
MermaidRegex = re.compile(r"^```[\ \t]*[Mm]ermaid[\ \t]*$")


class MermaidPreprocessor(Preprocessor):
    def run(self, lines):
        new_lines = []
        in_mermaid_code = False
        is_mermaid = False

        for line in lines:
            if not in_mermaid_code:
                # Match the opening line of the mermaid code block
                if MermaidRegex.match(line):
                    in_mermaid_code = True
                    new_lines.append('<div class="mermaid">')
                    is_mermaid = True
                else:
                    new_lines.append(line)
            else:
                # Match the closing line of the mermaid code block
                if line.strip() == "```":
                    in_mermaid_code = False
                    new_lines.append("</div>")
                    new_lines.append("")
                else:
                    # Strip non-printable characters and add the mermaid code lines
                    new_lines.append(strip_not_printable(line).strip())

        if is_mermaid:
            # Add the mermaid.js initialization script to the bottom of the document if any mermaid diagrams were found.
            new_lines.append("")
            new_lines.append("""<script>
                function initializeMermaid() {
                    mermaid.initialize({startOnLoad: true});
                }
                if (document.readyState === "complete" || document.readyState === "interactive") {
                    setTimeout(initializeMermaid, 1);
                } else {
                    document.addEventListener("DOMContentLoaded", initializeMermaid);
                }
            </script>""")

        return new_lines


class MermaidExtension(Extension):
    def extendMarkdown(self, md):
        md.preprocessors.register(MermaidPreprocessor(md), "mermaid", 35)


# Usage
if __name__ == "__main__":
    md_text = "Here is an image ![[image.png]]"
    md = markdown.Markdown(extensions=[ObsidianImageExtension()])
    html = md.convert(md_text)
    print(html)
