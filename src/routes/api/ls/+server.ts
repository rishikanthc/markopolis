import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { getAuthenticatedPocketBase } from '$lib/server/auth';

interface FileNode {
	id: string;
	name: string;
	url: string;
	children: FileNode[];
}

function buildFileTree(records: any[]): FileNode[] {
	const tree: FileNode[] = [];
	records.forEach((record) => {
		const pathParts = record.url.split('/').filter(Boolean);
		let currentLevel = tree;
		pathParts.forEach((part: string, index: number) => {
			let existingNode = currentLevel.find((node) => node.name === part);
			if (!existingNode) {
				existingNode = {
					id: record.id,
					name: part,
					url: index === pathParts.length - 1 ? record.url : '',
					children: []
				};
				currentLevel.push(existingNode);
			}
			currentLevel = existingNode.children;
		});
	});
	return tree;
}

export const GET: RequestHandler = async () => {
	try {
		const pb = await getAuthenticatedPocketBase();
		const pageSize = 200; // Adjust this value based on your needs
		let page = 1;
		let allRecords: any[] = [];

		while (true) {
			const result = await pb.collection('mdbase').getList(page, pageSize, {
				sort: 'url'
			});

			allRecords = allRecords.concat(result.items);

			if (!result.items.length || result.items.length < pageSize) {
				break;
			}

			page++;
		}

		const fileTree = buildFileTree(allRecords);
		return json(fileTree);
	} catch (error) {
		console.error('Error fetching records:', error);
		return json({ error: 'Failed to fetch file tree' }, { status: 500 });
	}
};
