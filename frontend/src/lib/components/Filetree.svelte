<script>
	import { onMount } from 'svelte';
	import { writable } from 'svelte/store';
	// import fetchApiResponse from '../util.js'; // Adjust the path as needed
	import FileTreeItem from './FileTreeItem.svelte';

	export let fileTree = null;
	let loading = true;
	let error = null;
	const expandedFolders = writable({});

	/* onMount(async () => {
		try {
			const response = await fetchApiResponse('api/notes/ls');
			fileTree = typeof response === 'string' ? JSON.parse(response) : response;
			console.log('Parsed fileTree:', fileTree);
		} catch (err) {
			console.error('Error fetching or parsing file tree:', err);
			error = err.message;
		} finally {
			loading = false;
		}
	}); */

	function toggleFolder(folderPath) {
		expandedFolders.update((folders) => {
			folders[folderPath] = !folders[folderPath];
			return folders;
		});
	}
</script>

<div class="filetree">
	{#each fileTree.root.members as item (item.filename || item.folder_name)}
		<FileTreeItem {item} {expandedFolders} {toggleFolder} isRoot={true} />
	{/each}
</div>

<style>
	.filetree {
		margin-top: var(--spacing-08);
	}
</style>
