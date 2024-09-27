import { error } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import PocketBase from 'pocketbase';
import { getAuthenticatedPocketBase } from '$lib/server/auth';

export const GET: RequestHandler = async ({ params }) => {
	try {
		const pb = await getAuthenticatedPocketBase();
		const imagePath = params.path;
		console.log('Requested image path:', imagePath);

		const record = await pb.collection('attachments').getFirstListItem(`url="${imagePath}"`);
		console.log('Found record:', record);

		if (!record) {
			throw error(404, 'Image not found');
		}

		const fileUrl = pb.files.getUrl(record, record.file);
		console.log('File URL:', fileUrl);

		const fileResponse = await fetch(fileUrl);

		if (!fileResponse.ok) {
			throw error(500, 'Failed to fetch the image file');
		}

		const contentType = fileResponse.headers.get('content-type') || getContentType(imagePath);
		console.log('Content Type:', contentType);

		// Get the filename from the record or use a default
		const filename = record.filename || 'image';

		return new Response(fileResponse.body, {
			status: 200,
			headers: {
				'Content-Type': contentType,
				'Content-Disposition': `attachment; filename="${filename}"`,
				'Cache-Control': 'public, max-age=3600'
			}
		});
	} catch (err) {
		console.error('Error serving image:', err);
		throw error(500, 'Internal server error');
	}
};

function getContentType(filename: string): string {
	const ext = filename.split('.').pop()?.toLowerCase();
	switch (ext) {
		case 'webp':
			return 'image/webp';
		case 'jpg':
		case 'jpeg':
			return 'image/jpeg';
		case 'png':
			return 'image/png';
		case 'gif':
			return 'image/gif';
		case 'svg':
			return 'image/svg+xml';
		default:
			return 'application/octet-stream';
	}
}
