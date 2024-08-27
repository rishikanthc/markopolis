function toggleFolder(folderId, chevronId) {
  var folderContent = document.getElementById(folderId);
  var chevronIcon = document.getElementById(chevronId);
  var button = chevronIcon.closest('button'); // Find the closest button to the chevron icon

  if (folderContent.style.display === "none" || folderContent.style.display === "") {
    folderContent.style.display = "block";
    chevronIcon.style.transform = "rotate(180deg)";

    // Set focus on the button when the folder is expanded
    button.focus();

  } else {
    folderContent.style.display = "none";
    chevronIcon.style.transform = "rotate(0deg)";
    button.focus();
  }
}
