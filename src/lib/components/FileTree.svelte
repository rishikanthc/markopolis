<script lang="ts">
	import { onMount } from 'svelte';
	import { ChevronRight, ChevronDown, File } from 'lucide-svelte';

	interface FileNode {
		id: string;
		title: string;
		name: string;
		url: string;
		children: FileNode[];
	}

	export let fileTree: FileNode[] = [];

	/* onMount(async () => {
		try {
			const response = await fetch('/api/ls');
			if (!response.ok) {
				throw new Error('Failed to fetch file tree');
			}
			fileTree = await response.json();
		} catch (error) {
			console.error('Error fetching file tree:', error);
		}
	}); */

	export let node: FileNode | undefined = undefined;
	export let isExpanded = false;

	function toggleExpand() {
		isExpanded = !isExpanded;
	}

	$: isFolder = node && node.children.length > 0;
</script>

{#if node}
	<div class="file-node">
		<div
			class="flex cursor-pointer items-center rounded px-2 py-1 hover:bg-carbongray-100 dark:hover:bg-carbongray-700"
			on:click={toggleExpand}
			on:keydown={(e) => e.key === 'Enter' && toggleExpand()}
			role="button"
			tabindex="0"
		>
			{#if isFolder}
				{#if isExpanded}
					<ChevronDown class="mr-1 h-4 w-4 text-gray-500" />
				{:else}
					<ChevronRight class="mr-1 h-4 w-4 text-gray-500" />
				{/if}
			{:else}
				<File class="mr-1 h-4 w-4 text-gray-500" />
			{/if}

			{#if node.url}
				<a href={`/${node.url}`} class="text-carbongray-800 hover:underline">{node.title}</a>
			{:else}
				<span class="font-semibold">{node.title}</span>
			{/if}
		</div>

		{#if isFolder && isExpanded}
			<div class="children ml-4 mt-1 dark:bg-carbongray-700">
				{#each node.children as childNode}
					<svelte:self node={childNode} />
				{/each}
			</div>
		{/if}
	</div>
{:else}
	<div class="file-tree">
		{#each fileTree as rootNode}
			<svelte:self node={rootNode} />
		{/each}
	</div>
{/if}
