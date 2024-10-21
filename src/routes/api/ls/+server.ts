import { json } from "@sveltejs/kit";
import type { RequestHandler } from "./$types";
import { getAuthenticatedPocketBase } from "$lib/server/auth";

interface FileNode {
  id: string;
  title: string;
  name: string;
  url: string;
  children: FileNode[];
}

function buildFileTree(records: any[]): FileNode[] {
  const tree: FileNode[] = [];

  records.forEach((record) => {
    const pathParts = record.url.split("/").filter(Boolean); // Split the URL into parts
    let currentLevel = tree;

    pathParts.forEach((part: string, index: number) => {
      let existingNode = currentLevel.find((node) => node.name === part);

      // If the node doesn't exist, create a new one
      if (!existingNode) {
        existingNode = {
          id: "", // Only set if it's a file (at the last level)
          title: "",
          name: part, // The name of the folder or file
          url: "", // Only set if it's a file (at the last level)
          children: [], // This will hold the children (for folders)
        };
        currentLevel.push(existingNode);
      }

      // If it's the last part of the path (a file), assign file properties
      if (index === pathParts.length - 1) {
        existingNode.id = record.id;
        existingNode.title = record.title;
        existingNode.url = record.url;
      }

      // Move to the next level in the tree
      currentLevel = existingNode.children;
    });
  });

  return tree;
}


export const GET: RequestHandler = async () => {
  try {
    const pb = await getAuthenticatedPocketBase();
    const pageSize = 200; // Adjust this value based on your needs
    let page = 1;
    let allRecords: any[] = [];

    while (true) {
      const result = await pb.collection("mdbase").getList(page, pageSize, {
        sort: "url",
      });

      allRecords = allRecords.concat(result.items);

      if (!result.items.length || result.items.length < pageSize) {
        break;
      }

      page++;
    }

    const fileTree = buildFileTree(allRecords);
    return json(fileTree);
  } catch (error) {
    console.error("Error fetching records:", error);
    return json({ error: "Failed to fetch file tree" }, { status: 500 });
  }
};
