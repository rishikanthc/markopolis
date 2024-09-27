import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { superValidate } from 'sveltekit-superforms';
import { formSchema } from '$lib/components/schema';
import { zod } from 'sveltekit-superforms/adapters';
import { TITLE } from '$env/static/private';

export async function load({ fetch, params }) {
	const ftree = await fetch('/api/ls');
	const tagresp = await fetch('/api/tags');
	const tags = await tagresp.json();
	const filetree = await ftree.json();
	const siteTitle = TITLE;

	return { filetree, siteTitle, tags };
}
