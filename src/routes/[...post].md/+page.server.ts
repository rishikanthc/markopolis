import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import PocketBase from 'pocketbase';
import { promises as fs } from 'fs';
import { getAuthenticatedPocketBase } from '$lib/server/auth';

const pb = await getAuthenticatedPocketBase();

async function getBacklinks(url) {
	const mdbaseCollection = pb.collection('mdbase');
	const documentUrl = url;
	try {
		if (!documentUrl) {
			return new Response(JSON.stringify({ message: 'URL parameter is required' }), {
				status: 400
			});
		}

		const documents = await mdbaseCollection.getList(1, 1, {
			filter: `url="${documentUrl}"`,
			expand: 'backlinks'
		});

		if (documents.items.length === 0) {
			return new Response(JSON.stringify({ message: 'Document not found' }), { status: 404 });
		}

		const document = documents.items[0];

		const backLinks = (document.expand?.backlinks || []).map((link) => ({
			id: link.id,
			title: link.title,
			url: link.url
		}));

		return backLinks;
	} catch (error: any) {
		console.error('Error in backlinks API:', error);
		return {};
	}
}

async function computeGraphData(fileUrl) {
	const currentPage = await pb.collection('mdbase').getFirstListItem(`url="${fileUrl}"`);
	const relatedPages = await pb.collection('mdbase').getList(1, 50, {
		filter: `id ?~ "${currentPage.backlinks}" || id ?~ "${currentPage.links}"`
	});

	// Use a Set to store unique node IDs
	const uniqueNodeIds = new Set([currentPage.id]);

	// Create nodes array with current page
	const nodes = [{ id: currentPage.id, label: currentPage.title, color: '#ff0000' }];

	// Add related pages to nodes array, avoiding duplicates
	relatedPages.items.forEach((p) => {
		if (!uniqueNodeIds.has(p.id)) {
			uniqueNodeIds.add(p.id);
			nodes.push({ id: p.id, label: p.title, color: '#00ff00' });
		}
	});

	// Create edges array
	const edges = [
		...currentPage.links.map((link) => ({ from: currentPage.id, to: link })),
		...currentPage.backlinks.map((backlink) => ({ from: backlink, to: currentPage.id }))
	];

	return { nodes, edges };
}
// Main load function
export async function load({ params, fetch, locals }) {
	try {
		// Step 1: Authenticate
		/* console.log(pb); */
		console.log(params.post);
		const post = await pb
			.collection('mdbase')
			.getFirstListItem(`url="${params.post}.md"`, { expand: 'tags' });
		const backlinks = await getBacklinks(`${params.post}.md`);
		const graphData = await computeGraphData(`${params.post}.md`);

		const tags = post.expand?.tags.map((tag) => {
			return {
				name: tag.tag
			};
		});
		console.log(tags);

		return { post, title: post.title, backlinks, tags };
	} catch (error) {
		console.error(`Failed to fetch post: ${error}`);
		return { message: `Failed to fetch post: ${error}` };
	}
}
