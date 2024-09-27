import { json } from '@sveltejs/kit';
import { getAuthenticatedPocketBase } from '$lib/server/auth';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ url, request }) => {
	const fileUrl = url.searchParams.get('url');
	console.log(fileUrl);

	if (!fileUrl) {
		return json({ error: 'Missing URL parameter' }, { status: 400 });
	}

	try {
		const pb = await getAuthenticatedPocketBase();
		const currentPage = await pb.collection('mdbase').getFirstListItem(`url="${fileUrl}"`);
		const graphData = await computeGraphData(currentPage);
		return json(graphData);
	} catch (error) {
		console.error('Error computing graph:', error);
		return json({ error: error }, { status: 500 });
	}
};

async function computeGraphData(currentPage) {
	const pb = await getAuthenticatedPocketBase();
	const relatedPages = await pb.collection('mdbase').getList(1, 50, {
		filter: `id ?~ "${currentPage.backlinks}" || id ?~ "${currentPage.links}"`
	});

	const nodes = [
		{ id: currentPage.id, label: currentPage.title, color: '#ff0000' }, // Current page (red)
		...relatedPages.items.map((p) => ({ id: p.id, label: p.title, color: '#00ff00' })) // Related pages (green)
	];

	const edges = [
		...currentPage.links.map((link) => ({ from: currentPage.id, to: link })),
		...currentPage.backlinks.map((backlink) => ({ from: backlink, to: currentPage.id }))
	];

	return { nodes, edges };
}
