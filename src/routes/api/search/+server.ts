// api/search/+server.ts
import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import uFuzzy from '@leeoniya/ufuzzy';
import { getAuthenticatedPocketBase } from '$lib/server/auth';

function extractSnippet(content: string, query: string, snippetLength: number = 150) {
	const lowerContent = content.toLowerCase();
	const lowerQuery = query.toLowerCase();
	const index = lowerContent.indexOf(lowerQuery);

	if (index === -1) return content.slice(0, snippetLength);

	const start = Math.max(0, index - snippetLength / 2);
	const end = Math.min(content.length, index + query.length + snippetLength / 2);

	let snippet = content.slice(start, end);

	if (start > 0) snippet = '...' + snippet;
	if (end < content.length) snippet = snippet + '...';

	return snippet;
}

export const GET: RequestHandler = async ({ url }) => {
	const query = url.searchParams.get('query');
	if (!query) {
		return json({ error: 'Query parameter is required' }, { status: 400 });
	}

	try {
		/* await authenticateAdmin(); */
		const pb = await getAuthenticatedPocketBase();

		const pbResults = await pb.collection('mdbase').getList(1, 1000, {
			fields: 'id,title,content,url'
		});
		console.log('searched');

		const haystack = pbResults.items.map((item) => item.title + ' ' + item.content);
		const uf = new uFuzzy();

		let idxs = uf.filter(haystack, query);

		if (idxs != null && idxs.length > 0) {
			let info = uf.info(idxs, haystack, query);
			let order = uf.sort(info, haystack, query);

			const results = order.map((i) => {
				const item = pbResults.items[info.idx[i]];
				return {
					title: item.title,
					url: `${item.url}`,
					snippet: extractSnippet(item.content, query)
				};
			});

			return json(results);
		} else {
			return json([]);
		}
	} catch (error) {
		console.error('Search error:', error);
		return json({ error: 'An error occurred during search' }, { status: 500 });
	}
};
