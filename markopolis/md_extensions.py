import markdown
from markdown.inlinepatterns import InlineProcessor
import xml.etree.ElementTree as etree


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


# Usage
if __name__ == "__main__":
    md_text = "Here is an image ![[image.png]]"
    md = markdown.Markdown(extensions=[ObsidianImageExtension()])
    html = md.convert(md_text)
    print(html)
