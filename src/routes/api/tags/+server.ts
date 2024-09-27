// src/routes/api/hello/+server.ts
import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { getAuthenticatedPocketBase } from '$lib/server/auth';

export const GET: RequestHandler = async ({ request }) => {
	const pb = await getAuthenticatedPocketBase();

	const records = await pb.collection('tags').getFullList();
	const tags = records.map((tag) => {
		return {
			name: tag.tag
		};
	});

	return json(tags);
};
