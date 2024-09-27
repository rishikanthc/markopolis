import PocketBase from 'pocketbase';
import { getAuthenticatedPocketBase } from '$lib/server/auth';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params }) => {
	try {
		const pb = await getAuthenticatedPocketBase();
		const record = await pb.collection('tags').getFirstListItem(`tag="${params.tag}"`, {
			expand: 'links'
		});
		console.log('TAG =====>', record);

		// Extract the expanded 'links' data
		const posts =
			record.expand?.links?.map((link: any) => ({
				id: link.id,
				title: link.title,
				url: link.url
			})) || [];

		return {
			tag: record.tag,
			posts: posts,
			error: null
		};
	} catch (error) {
		console.error('Error fetching tag data:', error);
		return {
			tag: params.tag,
			posts: [],
			error: error instanceof Error ? error.message : 'An unknown error occurred'
		};
	}
};
