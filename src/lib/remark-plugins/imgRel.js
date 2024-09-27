import { visit } from 'unist-util-visit';
import path from 'path';

export default function remarkLogImages() {
	return function transformer(tree, file) {
		if (!file || !file.data || !file.data.fm || !file.data.fm.mdpath) {
			throw new Error('File metadata with url is missing.');
		}


		const url = file.data.fm.mdpath; // e.g., '/writing/f2/test'

		visit(tree, 'image', (node) => {
			// Extract the link part before any pipe (e.g., [[link|alias]])
			const rawLink = node.url.trim(); // e.g., '../f1/test'

			console.log(node)

			if (!rawLink.includes('/api/img') && !rawLink.includes('://')) {
				const folder = path.dirname(url.split('.')[0]);
				const absPath = path.join(folder, rawLink); // e.g., 'mdpath/f1/test'
				console.log("============>", rawLink, absPath)
				node.url = `/api/img/${absPath}`;
			}


		});

	}
}
