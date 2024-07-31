import pytest
from unittest.mock import mock_open, patch

# The function to be tested
from markpi import md as M

# Mock YAML front matter content
mock_file_content = """---
title: Example Note
author: Alex
date: "2024-01-01"
tags:
  - tag1
  - tag2
---
# Example Note Content
This is the content of the example note.
"""

# Expected output
expected_metadata = {
    "title": "Example Note",
    "author": "Alex",
    "date": "2024-01-01",
    "tags": ["tag1", "tag2"],
}


@pytest.mark.md_funcs
@patch("os.path.exists")
@patch("builtins.open", new_callable=mock_open, read_data=mock_file_content)
def test_get_meta(mock_open, mock_exists):
    # Mock the os.path.exists to always return True
    mock_exists.return_value = True

    # Call the function with the mocked file
    note_title = "example-note"
    result = M.get_meta(note_title)

    # Assert that the result matches the expected metadata
    assert result == expected_metadata


@pytest.mark.md_funcs
@patch("os.path.exists")
def test_get_meta_file_not_found(mock_exists):
    # Mock the os.path.exists to return False
    mock_exists.return_value = False

    # Call the function with a non-existing file
    note_title = "non-existing-note"
    with pytest.raises(FileNotFoundError):
        M.get_meta(note_title)


@pytest.mark.md_funcs
@patch("os.path.exists")
@patch("builtins.open", new_callable=mock_open, read_data="# Invalid file content")
def test_get_meta_invalid_yaml(mock_open, mock_exists):
    # Mock the os.path.exists to always return True
    mock_exists.return_value = True

    # Call the function with an invalid YAML front matter file
    note_title = "invalid-yaml-note"
    with pytest.raises(ValueError):
        M.get_meta(note_title)
