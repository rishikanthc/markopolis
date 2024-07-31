import pytest
from unittest.mock import patch

# The function to be tested
from markpi import md as M

# Directory and file names for testing
mocked_files = [
    "implementing-deep-walk.md",
    "learning-lua.md",
    "pytorch-and-jax.md",
    "tools-for-productivity.md",
    "wezterm.md",
    "non-markdown.txt",
    "image.png",
]

# Expected output
expected_output = [
    "implementing-deep-walk",
    "learning-lua",
    "pytorch-and-jax",
    "tools-for-productivity",
    "wezterm",
]


@pytest.mark.md_funcs
@patch("os.path.exists")
@patch("os.listdir")
def test_list_markdown_files(mock_listdir, mock_exists):
    # Mock the os.path.exists to always return True
    mock_exists.return_value = True

    # Mock the os.listdir to return our mocked_files
    mock_listdir.return_value = mocked_files

    # Call the function with the mocked directory
    result = M.list_markdown_files()

    # Assert that the result matches the expected output
    assert result == expected_output
