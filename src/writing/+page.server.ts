import PocketBase from 'pocketbase';
import { getAuthenticatedPocketBase } from '$lib/server/auth';

const pb = await getAuthenticatedPocketBase();

export async function load({ params }) {
	try {
		const mdbase = await pb.collections.getOne('mdbase');

		const records = await pb.collection('mdbase').getList(1, 10, { sort: '-created' });
		const posts = Object.values(records.items).map((item) => ({
			title: item.title,
			id: item.id,
			date: item.created,
			url: item.url
		}));
		return { posts };
	} catch (error) {
		return { posts: [], err: error };
	}
}
