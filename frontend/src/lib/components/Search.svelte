<script>
	import { onMount } from 'svelte';

	let isExpanded = false;
	let searchQuery = '';
	let searchResults = [];
	let selectedResultIndex = -1;
	let searchContainerElement;
	let searchWrapperElement;
	let searchInputElement;

	function toggleExpand() {
		isExpanded = !isExpanded;
		if (!isExpanded) {
			closeSearch();
		} else {
			setTimeout(() => {
				searchInputElement.focus();
			}, 0);
		}
	}

	function closeSearch() {
		isExpanded = false;
		searchQuery = '';
		searchResults = [];
		selectedResultIndex = -1;
	}

	let query = '';
	let search_response = [];

	async function handleInput(event) {
		searchQuery = event.target.value;
		if (searchQuery.length > 0) {
			try {
				const response = await fetch(`/notes/search?query=${encodeURIComponent(searchQuery)}`);
				if (!response.ok) {
					throw new Error('Network response was not ok');
				}
				search_response = await response.json();

				// Ensure search_response and search_response.results are valid
				if (search_response && Array.isArray(search_response.results)) {
					searchResults = search_response.results;
				} else {
					searchResults = []; // Clear results if response is invalid
				}
				selectedResultIndex = -1;
			} catch (error) {
				console.error('Error fetching search results:', error);
				searchResults = []; // Clear results on error
			}
		} else {
			searchResults = []; // Clear results if query is empty
		}
	}

	function handleKeydown(event) {
		if (searchResults.length === 0) return;

		if (event.key === 'ArrowDown') {
			event.preventDefault();
			selectedResultIndex = (selectedResultIndex + 1) % searchResults.length;
		} else if (event.key === 'ArrowUp') {
			event.preventDefault();
			selectedResultIndex = (selectedResultIndex - 1 + searchResults.length) % searchResults.length;
		} else if (event.key === 'Enter' && selectedResultIndex !== -1) {
			event.preventDefault();
			navigateToResult(searchResults[selectedResultIndex].file_path);
		}
	}

	function handleClickOutside(event) {
		if (isExpanded && searchWrapperElement && !searchWrapperElement.contains(event.target)) {
			closeSearch();
		}
	}

	function navigateToResult(filePath) {
		closeSearch();
		/* window.location.href = `http://localhost:5173/${filePath}`; */
		window.location.href = `${window.location.origin}/${filePath}`;
	}

	onMount(() => {
		document.addEventListener('keydown', handleKeydown);
		document.addEventListener('click', handleClickOutside);
		return () => {
			document.removeEventListener('keydown', handleKeydown);
			document.removeEventListener('click', handleClickOutside);
		};
	});
</script>

<div bind:this={searchWrapperElement} class="search-wrapper">
	<div bind:this={searchContainerElement} class="search-container" class:expanded={isExpanded}>
		<button on:click={toggleExpand} class="search-button">
			<svg
				class="icon"
				xmlns="http://www.w3.org/2000/svg"
				width="32"
				height="32"
				viewBox="0 0 32 32"
			>
				<defs>
					<style>
						.cls-1 {
							fill: none;
						}
					</style>
				</defs>
				<path
					d="M29,27.5859l-7.5521-7.5521a11.0177,11.0177,0,1,0-1.4141,1.4141L27.5859,29ZM4,13a9,9,0,1,1,9,9A9.01,9.01,0,0,1,4,13Z"
					transform="translate(0 0)"
				/>
				<rect
					id="_Transparent_Rectangle_"
					data-name="&lt;Transparent Rectangle&gt;"
					class="cls-1"
					width="32"
					height="32"
				/>
			</svg>
		</button>
		<input
			bind:this={searchInputElement}
			type="text"
			class="search-input"
			placeholder="Search..."
			bind:value={searchQuery}
			on:input={handleInput}
		/>
		{#if isExpanded}
			<button on:click={closeSearch} class="close-button">
				<svg
					class="close-icon"
					xmlns="http://www.w3.org/2000/svg"
					width="32"
					height="32"
					viewBox="0 0 32 32"
				>
					<defs>
						<style>
							.cls-1 {
								fill: none;
							}
						</style>
					</defs>
					<polygon
						points="17.4141 16 24 9.4141 22.5859 8 16 14.5859 9.4143 8 8 9.4141 14.5859 16 8 22.5859 9.4143 24 16 17.4141 22.5859 24 24 22.5859 17.4141 16"
					/>
					<g id="_Transparent_Rectangle_" data-name="&lt;Transparent Rectangle&gt;">
						<rect class="cls-1" width="32" height="32" />
					</g>
				</svg>
			</button>
		{/if}
	</div>

	{#if isExpanded && searchResults.length > 0}
		<div class="search-results">
			{#each searchResults as result, index}
				<a
					href="http://localhost:5173/{result.file_path}"
					class="search-result"
					class:selected={index === selectedResultIndex}
					on:click|preventDefault={() => navigateToResult(result.file_path)}
				>
					<div class="file-path">{result.file_path}</div>
					<div class="snippet">{result.snippet}</div>
				</a>
			{/each}
		</div>
	{/if}
</div>

<style>
	.search-wrapper {
		position: relative;
		display: inline-block;
	}
	.search-container {
		display: flex;
		gap: 0;
		justify-content: center;
		align-items: center;
		overflow: hidden;
	}
	.search-container.expanded {
		justify-content: center;
		box-shadow:
			inset 0 2px 3px #000,
			0 2px 0 hsla(30, 0%, 32%, 0.55);
	}
	.search-input {
		background: #393939;
		color: #f4f4f4;
		width: 0;
		height: 38px;
		opacity: 0;
		transition:
			width 0.3s ease-in-out,
			opacity 0.3s ease-in-out,
			margin-left 0.3s ease-in-out;
		border: none;
		outline: none;
	}
	.expanded .search-input {
		width: 300px;
		opacity: 1;
		padding: 0 0.5rem;
	}
	.search-button,
	.close-button {
		background: none;
		border: none;
		padding: 0;
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: center;
		transition: transform 0.3s ease-in-out;
		height: 38px;
		width: 38px;
	}
	.expanded .search-button {
		transform: translateX(0);
		background: #393939;
	}
	.expanded .close-button {
		background: #393939;
	}
	.icon,
	.close-icon {
		width: 20px;
		height: 20px;
		fill: #f4f4f4;
		padding: 0.5em;
	}
	.icon:hover,
	.close-icon:hover {
		background: #161616;
	}
	.search-results {
		position: absolute;
		top: 100%;
		left: 0;
		right: 0;
		background: #161616;
		border-top: 1px solid #4a4a4a;
		max-height: 300px;
		overflow-y: auto;
		box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
		z-index: 10;
		scrollbar-width: thin;
		scrollbar-color: #393939 #161616;
	}
	.search-results::-webkit-scrollbar {
		width: 6px;
	}
	.search-results::-webkit-scrollbar-track {
		background: #161616;
	}
	.search-results::-webkit-scrollbar-thumb {
		background-color: #393939;
		border-radius: 3px;
		border: 2px solid #161616;
	}
	.search-result {
		display: block;
		padding: 10px;
		color: #f4f4f4;
		text-decoration: none;
		border-bottom: 1px solid #4a4a4a;
	}
	.search-result:hover,
	.search-result.selected {
		background: #393939;
	}
	.file-path {
		font-weight: bold;
		margin-bottom: 5px;
	}
	.snippet {
		font-size: 0.9em;
		color: #ccc;
	}

	/* Media query for mobile devices */
	@media (max-width: 784px) {
		.expanded .search-input {
			width: 200px; /* Reduced width for mobile */
		}
		.search-results {
			width: 100%; /* Full width on mobile */
			max-width: 300px; /* Limit maximum width */
			left: 50%;
			transform: translateX(-50%);
		}
	}
</style>
