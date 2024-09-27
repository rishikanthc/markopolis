// src/routes/api/hello/+server.ts
import type { RequestHandler } from './$types';
import { getAuthenticatedPocketBase } from '$lib/server/auth';

export const GET: RequestHandler = async ({ request }) => {
	const pb = await getAuthenticatedPocketBase();

	// Ensure the server is authenticated
	if (!pb.authStore.isValid) {
		return new Response(JSON.stringify({ error: 'Unauthorized' }), { status: 401 });
	}

	// Example of accessing PocketBase data
	const users = await pb.collection('users').getFullList();

	return new Response(JSON.stringify({ data: users }), { status: 200 });
};
