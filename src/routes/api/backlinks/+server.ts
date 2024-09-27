import type { RequestHandler } from '@sveltejs/kit';
import PocketBase from 'pocketbase';
import {
	POCKETBASE_ADMIN_PASSWORD,
	POCKETBASE_ADMIN_EMAIL,
	POCKETBASE_URL,
	API_KEY
} from '$env/static/private';
import { getAuthenticatedPocketBase } from '$lib/server/auth';

const pb = await getAuthenticatedPocketBase();

export const GET: RequestHandler = async ({ url, request }) => {
	try {
		const mdbaseCollection = pb.collection('mdbase');
		const documentUrl = url.searchParams.get('url');

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

		return new Response(JSON.stringify({ backLinks }), {
			status: 200,
			headers: { 'Content-Type': 'application/json' }
		});
	} catch (error: any) {
		console.error('Error in backlinks API:', error);
		return new Response(
			JSON.stringify({
				message: 'Failed to retrieve backlinks',
				error: error.message || 'Unknown error',
				details: error.data ? JSON.stringify(error.data) : 'No additional details'
			}),
			{ status: 500 }
		);
	}
};

export const OPTIONS: RequestHandler = async () => {
	return new Response(null, {
		status: 204,
		headers: {
			'Access-Control-Allow-Origin': '*',
			'Access-Control-Allow-Methods': 'GET, OPTIONS',
			'Access-Control-Allow-Headers': 'Content-Type, X-API-Key'
		}
	});
};
