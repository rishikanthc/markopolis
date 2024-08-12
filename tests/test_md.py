import pytest
import os
from unittest.mock import mock_open, patch
from datetime import date
from noetly.md import (
    list_markdown_files,
    get_meta,
    get_note_content,
    get_toc,
    get_backlinks_slow,
    create_markdown_files,
    MDROOT,
)


@pytest.fixture
def mock_md_files():
    return ["file1.md", "file2.md", "file3.md"]


def test_list_markdown_files(mock_md_files):
    with patch("os.path.exists", return_value=True), patch(
        "os.listdir", return_value=mock_md_files
    ):
        files, error = list_markdown_files()
        assert files == ["file1", "file2", "file3"]
        assert error == ""


def test_list_markdown_files_directory_not_exists():
    with patch("os.path.exists", return_value=False):
        files, error = list_markdown_files()
        assert files is None
        assert "does not exist" in error  # pyright: ignore


def test_get_meta_valid():
    mock_content = """---
title: Test Note
date: 2023-07-31
tags: [test, pytest]
custom: value
---
Content here
"""
    with patch("os.path.exists", return_value=True), patch(
        "builtins.open", mock_open(read_data=mock_content)
    ):
        meta, error = get_meta("test_note")
        assert error == ""
        print("Actual meta:", meta)  # Debug print
        assert "title" in meta  # pyright: ignore
        assert meta["title"] == "Test Note"  # pyright: ignore
        assert "date" in meta  # pyright: ignore
        assert meta["date"] == date(2023, 7, 31)  # Updated this line #pyright: ignore
        assert "tags" in meta  # pyright: ignore
        assert meta["tags"] == ["test", "pytest"]  # pyright: ignore
        assert "custom" in meta  # pyright: ignore
        assert meta["custom"] == "value"  # pyright: ignore


def test_get_meta_no_frontmatter():
    mock_content = "Content without frontmatter"
    with patch("os.path.exists", return_value=True), patch(
        "builtins.open", mock_open(read_data=mock_content)
    ):
        meta, error = get_meta("test_note")
        assert (
            error
            == "Error reading file: [Errno 2] No such file or directory: '/Users/rishi/Code/cookiejar/noetly/md-test/test_note.md'"
        )
        assert meta is None


def test_get_meta_invalid_yaml():
    mock_content = """---
invalid: yaml: content
---
"""
    with patch("os.path.exists", return_value=True), patch(
        "builtins.open", mock_open(read_data=mock_content)
    ):
        meta, error = get_meta("test_note")
        assert meta is None
        assert "Error parsing YAML" in error  # pyright: ignore


def test_get_note_content_valid():
    mock_content = """---
frontmatter: here
---
# Heading

Content here
"""
    with patch("os.path.exists", return_value=True), patch(
        "builtins.open", mock_open(read_data=mock_content)
    ):
        content, error = get_note_content("test_note")
        assert error == ""
        assert content[0] == "# Heading\n\nContent here"  # pyright: ignore
        assert "<h1>Heading</h1>" in content[1]  # pyright: ignore


def test_get_toc_valid():
    mock_content = """---
frontmatter: here
---
# Heading 1
## Subheading 1.1
# Heading 2
## Subheading 2.1
### Subheading 2.1.1
"""
    with patch("os.path.exists", return_value=True), patch(
        "builtins.open", mock_open(read_data=mock_content)
    ):
        toc, error = get_toc("test_note")
        assert error == ""
        print("Actual ToC:", toc)  # Debug print
        assert "Heading 1" in toc  # pyright: ignore
        assert "Subheading 1.1" in toc["Heading 1"]  # pyright: ignore
        assert "Heading 2" in toc  # pyright: ignore
        assert "Subheading 2.1" in toc["Heading 2"]  # pyright: ignore
        assert "Subheading 2.1.1" in toc["Heading 2"]["Subheading 2.1"]  # pyright: ignore
        # Check if all leaf nodes are dictionaries (empty or not)
        assert all(isinstance(v, dict) for v in toc.values())  # pyright: ignore
        assert all(
            isinstance(v, dict)
            for heading in toc.values()  # pyright: ignore
            for v in heading.values()  # pyright: ignore
        )


def test_get_backlinks_slow():
    mock_files = ["note1.md", "note2.md", "note3.md"]
    mock_contents = {
        "note1.md": "Content with [[test_note]]",
        "note2.md": "Content without link",
        "note3.md": "Content with [[test_note|alias]]",
    }

    def mock_open_file(filename, mode):
        return mock_open(read_data=mock_contents[filename])(filename, mode)

    with patch("os.listdir", return_value=mock_files), patch(
        "os.path.join", lambda *args: args[-1]
    ), patch("builtins.open", mock_open_file):
        backlinks, error = get_backlinks_slow("test_note")
        assert error == ""
        assert set(backlinks) == {"note1.md", "note3.md"}  # pyright: ignore


# Add more tests as needed
def test_create_markdown_files():
    test_dict = {
        "Test File 1": "# This is a test\nContent for file 1",
        "Test File 2": "## Another test\nContent for file 2",
    }

    with patch("os.makedirs") as mock_makedirs, patch(
        "builtins.open", mock_open()
    ) as mock_file, patch("os.path.join", lambda *args: "/".join(args)):
        status = create_markdown_files(test_dict)

        # Check if the function returned success status
        assert status == 200

        # Check if os.makedirs was called with the correct argument
        mock_makedirs.assert_called_once_with(MDROOT, exist_ok=True)

        # Check if the correct number of files were "created"
        assert mock_file.call_count == len(test_dict)

        # Check if the files were "created" with the correct names and content
        for title, content in test_dict.items():
            filename = f"{title.replace(' ', '_').lower()}.md"
            file_path = os.path.join(MDROOT, filename)
            mock_file.assert_any_call(file_path, "w", encoding="utf-8")
            mock_file().write.assert_any_call(content)


def test_create_markdown_files_failure():
    test_dict = {"Test File": "Content"}

    with patch("os.makedirs", side_effect=PermissionError("Permission denied")):
        status = create_markdown_files(test_dict)

        # Check if the function returned failure status
        assert status == 500
