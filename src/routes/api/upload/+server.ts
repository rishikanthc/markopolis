import type { RequestHandler } from '@sveltejs/kit';
import PocketBase from 'pocketbase';
import path from 'path';
import { compile } from 'mdsvex';
import { getAuthenticatedPocketBase } from '$lib/server/auth';

import { addFrontmatterToMarkdown } from '$lib/md'; // Updated to accept fileContent and url
import { visit } from 'unist-util-visit';
import remarkFootnotes from 'remark-footnotes';
import remarkTags from '$lib/remark-plugins/remarkTags';
import remarkHighlight from '$lib/remark-plugins/highlightSyn';
/* import rehypeMermaid from 'rehype-mermaid'; */
import remarkMermaid from '$lib/remark-plugins/mermaidDiag';
import remarkLogImages from '$lib/remark-plugins/imgRel';
/* import rehypeKatexSvelte from 'rehype-katex-svelte'; */
import rehypeKatex from 'rehype-katex';
import remarkMath from 'remark-math';
import rehypeCallouts from 'rehype-callouts';
import rehypeAutolinkHeadings from 'rehype-autolink-headings';
import wikiLink from 'remark-wiki-link';
import obsidianImagePlugin from '$lib/remark-plugins/obsidianImage';

import {
	POCKETBASE_ADMIN_PASSWORD,
	POCKETBASE_ADMIN_EMAIL,
	POCKETBASE_URL,
	API_KEY // Add this line to import the API_KEY
} from '$env/static/private';

function verifyApiKey(request: Request): boolean {
	const apiKey = request.headers.get('X-API-Key');
	return apiKey === API_KEY;
}

/**
 * Middleware to check API key before processing the request
 */
async function apiKeyMiddleware(request: Request, handler: (req: Request) => Promise): Promise {
	if (!verifyApiKey(request)) {
		return new Response(JSON.stringify({ message: 'Unauthorized' }), {
			status: 401,
			headers: { 'Content-Type': 'application/json' }
		});
	}
	return handler(request);
}

// Define interfaces for frontmatter and compiled markdown
interface Frontmatter {
	title?: string;
	[key: string]: any;
}

interface CompiledMD {
	code: string;
	data?: {
		fm?: Frontmatter;
	};
}

// Initialize PocketBase
const pb = await getAuthenticatedPocketBase();

/**
 * Custom WikiLink transformer for Markdown processing.
 */
function customWikiLink() {
	return function transformer(tree: any, file: any) {
		// Ensure file metadata exists
		if (!file || !file.data || !file.data.fm || !file.data.fm.mdpath) {
			throw new Error('File metadata with url is missing.');
		}

		const url = file.data.fm.mdpath; // e.g., '/writing/f2/test'

		visit(tree, 'wikiLink', (node: any) => {
			// Extract the link part before any pipe (e.g., [[link|alias]])
			const rawLink = node.value.trim().split('|')[0].trim(); // e.g., '../f1/test'

			// Resolve the absolute path based on the current file's directory
			const folder = path.dirname(url.split('.')[0]);

			const absPath = path.join(folder, rawLink); // e.g., 'mdpath/f1/test'

			node.data.permalink = `/${absPath}.md`;
			node.data.hProperties.href = `/${absPath}.md`;
		});
	};
}

function unescapeHtml(html: string): string {
	return html
		.replace(/&lt;/g, '<')
		.replace(/&gt;/g, '>')
		.replace(/&amp;/g, '&')
		.replace(/&quot;/g, '"')
		.replace(/&#39;/g, "'");
}

function processContent(content: string): string {
	// Adjusting the regex to correctly match the pattern {@html ...} and removing the surrounding spaces.
	const regex = /{@html\s+([\s\S]*?)\s*}/g;
	const stage1 = content.replace(regex, (match, p1) => {
		// Removing {@html } and unescaping the inner HTML
		return unescapeHtml(p1);
	});

	const backticksRemoved = stage1.replace(/`(<code[\s\S]*?<\/code>)`/g, (match, p1) => {
		return p1; // Remove the backticks around <code>...</code>
	});

	return unescapeHtml(backticksRemoved);
}
/**
 * Compile Markdown content using mdsvex with various plugins.
 */
async function compileMarkdown(fileContent: string, url: string): Promise {
	// Add or update frontmatter with the provided URL
	const processedContent = addFrontmatterToMarkdown(fileContent, url);

	const compiled: CompiledMD = await compile(processedContent, {
		extensions: ['.md', '.svx'],
		smartypants: {
			dashes: 'oldschool'
		},
		remarkPlugins: [
			remarkMath,
			remarkFootnotes,
			[
				wikiLink,
				{
					hrefTemplate: (permalink: string) => `/${permalink}.md`
				}
			],
			[customWikiLink],
			obsidianImagePlugin,
			remarkMermaid,
			remarkHighlight,
			remarkLogImages,
			remarkTags
		],
		rehypePlugins: [rehypeKatex, rehypeCallouts, rehypeAutolinkHeadings]
	});

	const frontmatter: Frontmatter = compiled.data?.fm || {};
	const fileName: string = path.parse(fileContent).name; // Adjusted as fdpath is now url
	const title: string = frontmatter.title || fileName;

	const node = { code: processContent(compiled.code), data: compiled.data };

	// Use the provided URL
	return { compiled: node, title, url };
}

async function ensureMdbaseCollection() {
	try {
		// Check if the collection exists
		const collection = await pb.collections.getOne('mdbase');
		console.log('Mdbase collection already exists');

		const linksFieldExists = collection.schema.some((field) => field.name === 'links');
		const backlinksFieldExists = collection.schema.some((field) => field.name === 'backlinks');
		const tagFieldExists = collection.schema.some((field) => field.name === 'tags');

		if (!linksFieldExists) {
			console.log('Adding links field to mdbase collection...');
			await pb.collections.update('mdbase', {
				schema: [
					...collection.schema,
					{
						name: 'links',
						type: 'relation',
						required: false,
						options: {
							collectionId: collection.id,
							cascadeDelete: false,
							maxSelect: null,
							displayFields: ['title']
						}
					}
				]
			});
			console.log('Links field added successfully');
		} else {
			console.log('Links field already exists');
		}

		if (!backlinksFieldExists) {
			console.log('Adding links field to mdbase collection...');
			await pb.collections.update('mdbase', {
				schema: [
					...collection.schema,
					{
						name: 'backlinks',
						type: 'relation',
						required: false,
						options: {
							collectionId: collection.id,
							cascadeDelete: false,
							maxSelect: null,
							displayFields: ['title']
						}
					}
				]
			});
			console.log('Backlinks field added successfully');
		} else {
			console.log('BackLinks field already exists');
		}

		if (!tagFieldExists) {
			const tagcol = await pb.collections.getOne('tags');
			console.log('Adding links field to mdbase collection...');
			await pb.collections.update('mdbase', {
				schema: [
					...collection.schema,
					{
						name: 'tags',
						type: 'relation',
						required: false,
						options: {
							collectionId: tagcol.id,
							cascadeDelete: false,
							maxSelect: null,
							displayFields: ['title']
						}
					}
				]
			});
			console.log('Tags field added successfully');
		} else {
			console.log('Tags field already exists');
		}

		// Check if the index exists
		const indexExists = collection.indexes.some((index) =>
			index.includes('CREATE INDEX `idx_url` ON `mdbase` (`url`)')
		);

		if (!indexExists) {
			console.log('Creating index on url field...');
			await pb.collections.update('mdbase', {
				indexes: [...collection.indexes, 'CREATE INDEX `idx_url` ON `mdbase` (`url`)']
			});
			console.log('Index created successfully');
		} else {
			console.log('Index on url field already exists');
		}
	} catch (error) {
		if (error.status === 404) {
			console.log('Mdbase collection does not exist. Creating...');
			try {
				await pb.collections.create({
					name: 'mdbase',
					type: 'base',
					schema: [
						{ name: 'title', type: 'text' },
						{ name: 'content', type: 'text' },
						{ name: 'url', type: 'text' },
						{
							name: 'mdfile',
							type: 'file',
							required: true,
							options: {
								maxSelect: 1,
								maxSize: 5242880 // 5MB max size
							}
						},
						{
							name: 'frontmatter',
							type: 'json',
							options: {
								maxSize: 5242880
							}
						}
					],
					indexes: ['CREATE INDEX `idx_url` ON `mdbase` (`url`)']
				});
				console.log('Mdbase collection created successfully with index on url field');
			} catch (createError) {
				console.error('Failed to create mdbase collection:', createError);
				throw createError;
			}
		} else {
			console.error('Error checking mdbase collection:', error);
			throw error;
		}
	}
}

function extractWikiLinks(htmlContent: string): string[] {
	const regex = /<a[^>]+href="([^"]+\.md)"[^>]*>/g;
	const matches = htmlContent.matchAll(regex);
	return Array.from(matches, (m) => m[1]);
}

async function updateLinks(recordId: string, content: string) {
	const mdbaseCollection = pb.collection('mdbase');

	// Extract wiki links from the content
	const wikiLinks = extractWikiLinks(content);
	console.log('WIKI =====>', wikiLinks);

	// Get the current record
	const currentRecord = await mdbaseCollection.getOne(recordId, { expand: 'links,backlinks' });
	const oldLinks = currentRecord.links || [];

	// Get IDs of linked documents
	const newLinkedRecordIds = [];
	for (const link of wikiLinks) {
		const linkedRecords = await mdbaseCollection.getList(1, 1, {
			filter: `url="${link.startsWith('/') ? link.slice(1) : link}"`
		});

		if (linkedRecords.items.length > 0) {
			newLinkedRecordIds.push(linkedRecords.items[0].id);
		}
	}

	// Update the current record's links
	await mdbaseCollection.update(recordId, {
		links: newLinkedRecordIds
	});

	// Update backlinks
	const linksToAdd = newLinkedRecordIds.filter((id) => !oldLinks.includes(id));
	const linksToRemove = oldLinks.filter((id) => !newLinkedRecordIds.includes(id));

	for (const id of linksToAdd) {
		await mdbaseCollection.update(id, {
			'backlinks+': recordId
		});
	}

	for (const id of linksToRemove) {
		await mdbaseCollection.update(id, {
			'backlinks-': recordId
		});
	}
}

async function ensureAttachmentsCollection() {
	try {
		// Check if the collection exists
		await pb.collections.getOne('attachments');
		console.log('Attachments collection already exists');
	} catch (error) {
		if (error.status === 404) {
			console.log('Attachments collection does not exist. Creating...');
			try {
				await pb.collections.create({
					name: 'attachments',
					type: 'base',
					schema: [
						{
							name: 'file',
							type: 'file',
							required: true,
							options: {
								maxSelect: 1,
								maxSize: 524288000
							}
						},
						{
							name: 'url',
							type: 'text',
							required: true
						}
					]
				});
				console.log('Attachments collection created successfully');
			} catch (createError) {
				console.error('Failed to create attachments collection:', createError);
				throw createError;
			}
		} else {
			console.error('Error checking attachments collection:', error);
			throw error;
		}
	}
}

async function ensureTagsCollection() {
	try {
		// Check if the collection exists
		await pb.collections.getOne('tags');
		console.log('Tags collection already exists');
	} catch (error) {
		if (error.status === 404) {
			console.log('Tags collection does not exist. Creating...');
			const collection = await pb.collections.getOne('mdbase');
			try {
				await pb.collections.create({
					name: 'tags',
					type: 'base',
					schema: [
						{
							name: 'tag',
							type: 'text',
							required: true
						},

						{
							name: 'links',
							type: 'relation',
							required: false,
							options: {
								collectionId: collection.id,
								cascadeDelete: false,
								maxSelect: null,
								displayFields: ['title']
							}
						}
					]
				});
				console.log('tags collection created successfully');
			} catch (createError) {
				console.error('Failed to create tags collection:', createError);
				throw createError;
			}
		} else {
			console.error('Error checking tags collection:', error);
			throw error;
		}
	}
}

interface Tag {
	id: string;
	name: string;
	links: string[];
}

async function parseTagsAndUpdatePocketBase(
	compiledMarkdown: string,
	frontmatter: Frontmatter,
	noteId: string,
	pb: PocketBase
) {
	const processedTags = new Set<string>();
	const noteTags: string[] = [];

	// Function to process a single tag
	async function processTag(tagName: string) {
		if (processedTags.has(tagName)) return;
		processedTags.add(tagName);

		try {
			let tag: Tag;
			try {
				tag = await pb.collection('tags').getFirstListItem(`tag="${tagName}"`);
				// If the tag exists, update it
				if (!tag.links.includes(noteId)) {
					await pb.collection('tags').update<Tag>(tag.id, {
						links: [...tag.links, noteId]
					});
					console.log(`Updated existing tag ${tagName} with new link to note ${noteId}`);
				} else {
					console.log(`Tag ${tagName} already linked to note ${noteId}`);
				}
			} catch (error) {
				// If the tag doesn't exist, create it
				tag = await pb.collection('tags').create<Tag>({
					tag: tagName,
					links: [noteId]
				});
				console.log(`Created new tag: ${tagName}`);
			}
			noteTags.push(tag.id);
		} catch (error) {
			console.error(`Error processing tag "${tagName}":`, error);
		}
	}

	// Process tags from compiled markdown
	const tagRegex = /<span class="tag">([^<]+)<\/span>/g;
	let match;
	while ((match = tagRegex.exec(compiledMarkdown)) !== null) {
		const tagName = match[1];
		await processTag(tagName);
	}

	// Process tags from frontmatter
	if (frontmatter.tags && Array.isArray(frontmatter.tags)) {
		for (const tag of frontmatter.tags) {
			await processTag(tag);
		}
	}

	// Update the note in mdbase collection with the tags
	try {
		const note = await pb.collection('mdbase').getOne(noteId);
		await pb.collection('mdbase').update(noteId, {
			tags: noteTags
		});
		console.log(`Updated note ${noteId} with tags: ${noteTags.join(', ')}`);
	} catch (error) {
		console.error(`Error updating note ${noteId} with tags:`, error);
	}
}

export const POST: RequestHandler = async ({ request }) => {
	return apiKeyMiddleware(request, async () => {
		try {
			await ensureAttachmentsCollection();
			await ensureMdbaseCollection();
			await ensureTagsCollection();

			const formData = await request.formData();
			const file = formData.get('file') as File | null;
			const url = formData.get('url') as string | null;

			if (!file) {
				return new Response(JSON.stringify({ message: 'No file uploaded' }), { status: 400 });
			}

			const fileName = file.name;
			const fileExtension = path.extname(fileName).toLowerCase();

			if (fileExtension === '.md') {
				if (!url) {
					return new Response(JSON.stringify({ message: 'URL is required for Markdown files' }), {
						status: 400
					});
				}

				const fileContent = await file.text();
				const { compiled, title, url: providedUrl } = await compileMarkdown(fileContent, url);
				const frontmatter = compiled.data?.fm || {};
				console.log('front', frontmatter);

				const mdbaseCollection = pb.collection('mdbase');
				const existingRecords = await mdbaseCollection.getList(1, 1, {
					filter: `url="${providedUrl}"`
				});

				let record;
				if (existingRecords.items.length > 0) {
					const existingRecord = existingRecords.items[0];
					record = await mdbaseCollection.update(existingRecord.id, {
						title,
						frontmatter,
						content: compiled.code,
						url: providedUrl,
						mdfile: file
					});
				} else {
					record = await mdbaseCollection.create({
						title,
						frontmatter,
						content: compiled.code,
						url: providedUrl,
						mdfile: file
					});
				}

				// Update links and backlinks
				await updateLinks(record.id, compiled.code);
				console.log('Updated bi-directional links');
				await parseTagsAndUpdatePocketBase(compiled.code, frontmatter, record.id, pb);
				console.log('Updated  tags');

				return new Response(
					JSON.stringify({ message: 'Markdown file uploaded successfully', record }),
					{ status: 200 }
				);
			} else if (['.png', '.jpg', '.svg', '.jpeg', '.gif', '.webp'].includes(fileExtension)) {
				console.log('Processing image file...');
				try {
					const attachmentsCollection = pb.collection('attachments');

					// Check if a record with the given URL already exists
					const existingRecords = await attachmentsCollection.getList(1, 1, {
						filter: `url="${url}"`
					});

					let attachmentRecord;
					if (existingRecords.items.length > 0) {
						// Update existing record
						const existingRecord = existingRecords.items[0];
						console.log('Updating existing attachment record...');
						attachmentRecord = await attachmentsCollection.update(existingRecord.id, {
							file: file,
							url: url
						});
					} else {
						// Create new record
						console.log('Creating new attachment record...');
						attachmentRecord = await attachmentsCollection.create({
							file: file,
							url: url
						});
					}

					const fileUrl = pb.getFileUrl(attachmentRecord, attachmentRecord.file);
					console.log('Generated file URL:', fileUrl);

					return new Response(
						JSON.stringify({
							message:
								existingRecords.items.length > 0
									? 'Image updated successfully'
									: 'Image uploaded successfully',
							record: attachmentRecord,
							url: fileUrl
						}),
						{ status: 200 }
					);
				} catch (imageError: any) {
					console.error('Error during image upload/update:', imageError);
					return new Response(
						JSON.stringify({
							message: 'Image upload/update failed',
							error: imageError.message || 'Unknown error during image upload/update',
							details: imageError.data ? JSON.stringify(imageError.data) : 'No additional details'
						}),
						{ status: 500 }
					);
				}
			} else {
				return new Response(JSON.stringify({ message: 'Unsupported file type' }), { status: 400 });
			}
		} catch (error: any) {
			console.error('Error in upload API:', error);
			return new Response(
				JSON.stringify({
					message: 'File upload failed',
					error: error.message || 'Unknown error',
					details: error.data ? JSON.stringify(error.data) : 'No additional details'
				}),
				{ status: 500 }
			);
		}
	});
};

export const DELETE: RequestHandler = async ({ request }) => {
	return apiKeyMiddleware(request, async () => {
		try {
			const { url } = await request.json();

			if (!url) {
				return new Response(JSON.stringify({ message: 'URL is required' }), { status: 400 });
			}

			const mdbaseCollection = pb.collection('mdbase');
			const attachmentsCollection = pb.collection('attachments');

			let deletedCount = 0;

			// Try to delete from mdbase collection
			try {
				const mdbaseRecords = await mdbaseCollection.getList(1, 1, { filter: `url="${url}"` });
				if (mdbaseRecords.items.length > 0) {
					await mdbaseCollection.delete(mdbaseRecords.items[0].id);
					console.log(`Deleted ${url} from mdbase collection`);
					deletedCount++;
				}
			} catch (error) {
				console.error(`Error deleting ${url} from mdbase collection:`, error);
			}

			// Try to delete from attachments collection
			try {
				const attachmentRecords = await attachmentsCollection.getList(1, 1, {
					filter: `url="${url}"`
				});
				if (attachmentRecords.items.length > 0) {
					await attachmentsCollection.delete(attachmentRecords.items[0].id);
					console.log(`Deleted ${url} from attachments collection`);
					deletedCount++;
				}
			} catch (error) {
				console.error(`Error deleting ${url} from attachments collection:`, error);
			}

			if (deletedCount > 0) {
				return new Response(JSON.stringify({ message: 'File deleted successfully' }), {
					status: 200
				});
			} else {
				return new Response(JSON.stringify({ message: 'File not found' }), { status: 404 });
			}
		} catch (error: any) {
			console.error('Error in delete API:', error);
			return new Response(
				JSON.stringify({
					message: 'File deletion failed',
					error: error.message || 'Unknown error',
					details: error.data ? JSON.stringify(error.data) : 'No additional details'
				}),
				{ status: 500 }
			);
		}
	});
};

export const GET: RequestHandler = async ({ request }) => {
	return apiKeyMiddleware(request, async () => {
		try {
			const mdbaseCollection = pb.collection('mdbase');
			const attachmentsCollection = pb.collection('attachments');

			const mdbaseRecords = await mdbaseCollection.getFullList({ fields: 'url' });
			const attachmentRecords = await attachmentsCollection.getFullList({ fields: 'url' });

			const allUrls = [
				...mdbaseRecords.map((record) => record.url),
				...attachmentRecords.map((record) => record.url)
			];

			return new Response(JSON.stringify(allUrls), {
				status: 200,
				headers: { 'Content-Type': 'application/json' }
			});
		} catch (error: any) {
			console.error('Error in list API:', error);
			return new Response(
				JSON.stringify({
					message: 'Failed to list files',
					error: error.message || 'Unknown error',
					details: error.data ? JSON.stringify(error.data) : 'No additional details'
				}),
				{
					status: 500,
					headers: { 'Content-Type': 'application/json' }
				}
			);
		}
	});
};

// Handle OPTIONS requests for CORS preflight
export const OPTIONS: RequestHandler = async () => {
	return new Response(null, {
		status: 204,
		headers: {
			'Access-Control-Allow-Origin': '*',
			'Access-Control-Allow-Methods': 'POST, DELETE, OPTIONS, GET',
			'Access-Control-Allow-Headers': 'Content-Type'
		}
	});
};
