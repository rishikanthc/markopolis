<script lang="ts">
	import { onMount } from 'svelte';
	import { fade } from 'svelte/transition';
	import { debounce } from 'lodash-es';
	import { Search, Loader, X } from 'lucide-svelte';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import * as Dialog from '$lib/components/ui/dialog/index.js';

	interface SearchResult {
		title: string;
		url: string;
		snippet: string;
	}

	let searchQuery = '';
	let searchResults: SearchResult[] = [];
	let isLoading = false;
	let isOpen = false;
	let selectedIndex = -1;

	const debouncedSearch = debounce(async () => {
		if (searchQuery.trim() === '') {
			searchResults = [];
			return;
		}
		isLoading = true;
		selectedIndex = -1;
		try {
			const response = await fetch(`/api/search?query=${encodeURIComponent(searchQuery)}`);
			if (response.ok) {
				const data = await response.json();
				searchResults = Array.isArray(data) ? data : [];
			} else {
				console.error('Search failed:', await response.text());
				searchResults = [];
			}
		} catch (error) {
			console.error('Search error:', error);
			searchResults = [];
		} finally {
			isLoading = false;
		}
	}, 300);

	$: {
		if (isOpen && searchQuery.trim() !== '') {
			debouncedSearch();
		}
	}

	function toggleSearch() {
		isOpen = !isOpen;
		if (!isOpen) {
			clearSearch();
		}
	}

	function clearSearch() {
		searchQuery = '';
		searchResults = [];
		selectedIndex = -1;
	}

	function handleResultClick(url: string) {
		isOpen = false;
		clearSearch();
		window.location.href = `/${url}`;
	}

	function highlightMatch(text: string, query: string) {
		if (!query.trim()) return text;
		const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
		return text.replace(
			regex,
			'<mark class="bg-yellow-200 text-gray-900 rounded px-0.5">$1</mark>'
		);
	}

	function handleKeydown(event: KeyboardEvent) {
		if (!isOpen) return;

		switch (event.key) {
			case 'ArrowDown':
				event.preventDefault();
				selectedIndex = (selectedIndex + 1) % searchResults.length;
				break;
			case 'ArrowUp':
				event.preventDefault();
				selectedIndex = (selectedIndex - 1 + searchResults.length) % searchResults.length;
				break;
			case 'Enter':
				if (selectedIndex >= 0 && selectedIndex < searchResults.length) {
					event.preventDefault();
					handleResultClick(searchResults[selectedIndex].url);
				}
				break;
			case 'Escape':
				event.preventDefault();
				toggleSearch();
				break;
		}
	}

	onMount(() => {
		const handleGlobalKeydown = (event: KeyboardEvent) => {
			if (event.key === 'k' && (event.ctrlKey || event.metaKey)) {
				event.preventDefault();
				toggleSearch();
			}
		};
		window.addEventListener('keydown', handleGlobalKeydown);
		return () => {
			window.removeEventListener('keydown', handleGlobalKeydown);
		};
	});
</script>

<svelte:window on:keydown={handleKeydown} />

<Dialog.Root bind:open={isOpen} on:close={clearSearch}>
	<Dialog.Trigger>
		<Button variant="ghost" size="icon" on:click={toggleSearch} aria-label="Open search">
			<Search size={20} />
		</Button>
	</Dialog.Trigger>

	<Dialog.Content class="sm:max-w-[560px]">
		<Dialog.Header>
			<Dialog.Title>Search</Dialog.Title>
		</Dialog.Header>

		<div class="relative">
			<Input type="text" bind:value={searchQuery} placeholder="Search..." class="pr-10" />
			<div class="absolute inset-y-0 right-0 flex items-center pr-3">
				{#if isLoading}
					<Loader size={20} class="animate-spin text-gray-400" />
				{:else if searchQuery}
					<button
						on:click={clearSearch}
						class="text-gray-400 hover:text-gray-600"
						aria-label="Clear search"
					>
						<X size={20} />
					</button>
				{:else}
					<Search size={20} class="text-gray-400" />
				{/if}
			</div>
		</div>

		{#if searchResults.length > 0}
			<div class="mt-4 max-h-[calc(60vh-2rem)] divide-y divide-carbongray-700 overflow-y-auto">
				{#each searchResults as result, index}
					<div
						class="p-2 py-3 transition-colors duration-150 ease-in-out hover:bg-carbongray-700 {index ===
						selectedIndex
							? 'bg-blue-50'
							: ''}"
					>
						<button
							on:click={() => handleResultClick(result.url)}
							class="w-full rounded text-left focus:outline-none focus:ring-2 focus:ring-blue-500"
						>
							<h3 class="mb-1 text-lg font-semibold">
								{@html highlightMatch(result.title, searchQuery)}
							</h3>
							<p class="line-clamp-2 text-sm">
								{@html highlightMatch(result.snippet, searchQuery)}
							</p>
						</button>
					</div>
				{/each}
			</div>
		{:else if searchQuery && !isLoading}
			<p class="mt-4 text-center text-sm text-gray-500">No results found</p>
		{/if}
	</Dialog.Content>
</Dialog.Root>
