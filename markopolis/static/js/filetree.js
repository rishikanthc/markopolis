function toggleFolder(folderId) {
  var folderContent = document.getElementById(folderId);
  if (
    folderContent.style.display === "none" ||
    folderContent.style.display === ""
  ) {
    folderContent.style.display = "block";
  } else {
    folderContent.style.display = "none";
  }
}
