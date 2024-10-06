import PocketBase from "pocketbase";
import { getAuthenticatedPocketBase } from "$lib/server/auth";

const pb = await getAuthenticatedPocketBase();

export async function load({ params }) {
  try {
    const mdbase = await pb.collections.getOne("mdbase");

    const records = await pb.collection("mdbase").getList(1, 1, {
      filter: "frontmatter.home = true",
      sort: "-created",
    });

    let post = null;
    if (records.items.length > 0) {
      post = records.items[0];
    }

    if (post) {
      const backlinks = await getBacklinks(`${post.frontmatter.mdpath}`);

      const tags = post.expand?.tags.map((tag) => {
        return {
          name: tag.tag,
        };
      });
      return { post, title: post.title, backlinks, tags };
    } else {
      return { post: null, title: "", backlinks: [], tags: [] };
    }
  } catch (error) {
    console.error(`Failed to fetch post: ${error}`);
    return { message: `Failed to fetch post: ${error}` };
  }
}

async function getBacklinks(url) {
  const mdbaseCollection = pb.collection("mdbase");
  const documentUrl = url;
  try {
    if (!documentUrl) {
      return new Response(
        JSON.stringify({ message: "URL parameter is required" }),
        {
          status: 400,
        },
      );
    }

    const documents = await mdbaseCollection.getList(1, 1, {
      filter: `url="${documentUrl}"`,
      expand: "backlinks",
    });

    if (documents.items.length === 0) {
      return new Response(JSON.stringify({ message: "Document not found" }), {
        status: 404,
      });
    }

    const document = documents.items[0];

    const backLinks = (document.expand?.backlinks || []).map((link) => ({
      id: link.id,
      title: link.title,
      url: link.url,
    }));

    return backLinks;
  } catch (error: any) {
    console.error("Error in backlinks API:", error);
    return {};
  }
}
