<script>
	import Filetree from '$lib/components/Filetree.svelte';
	import ThemeSwitcher from '$lib/components/ThemeSwitcher.svelte';
	import Search from '$lib/components/Search.svelte';
	import { writable } from 'svelte/store';
	import { onMount, onDestroy } from 'svelte';

	export let data;

	let isSidebarVisible = false;
	let mounted = false;
	let loading = true;
	let fileTree = null;
	let error = null;

	$: if (data) {
		fileTree = data.filetree || null;
		error = data.error || null;
		loading = false;
	}
	// Function to toggle sidebar visibility
	function toggleSidebar() {
		isSidebarVisible = !isSidebarVisible;
	}

	// Function to close sidebar if clicking outside
	function handleClickOutside(event) {
		if (isSidebarVisible && !event.target.closest('.sidebar') && !event.target.closest('.menu')) {
			isSidebarVisible = false;
		}
	}

	// Add event listener on mount, remove it on destroy
	onMount(() => {
		mounted = true;
		if (typeof window !== 'undefined') {
			window.addEventListener('click', handleClickOutside);
		}
	});

	onDestroy(() => {
		if (typeof window !== 'undefined') {
			window.removeEventListener('click', handleClickOutside);
		}
	});
</script>

<svelte:window on:click={handleClickOutside} />

<div class="main">
	<div class="bar">
		<div class="left-bar">
			<div class="menu" on:click={toggleSidebar}>
				<svg id="icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"
					><defs
						><style>
							.cls-1 {
								fill: none;
							}
						</style></defs
					><title>menu</title><rect x="4" y="6" width="24" height="2" /><rect
						x="4"
						y="24"
						width="24"
						height="2"
					/><rect x="4" y="12" width="24" height="2" /><rect
						x="4"
						y="18"
						width="24"
						height="2"
					/><rect
						id="_Transparent_Rectangle_"
						data-name="&lt;Transparent Rectangle&gt;"
						class="cls-1"
						width="32"
						height="32"
					/></svg
				>
			</div>
			<div class="title">MARKOPOLIS</div>
		</div>
		<div class="right-bar">
			<Search />
			<ThemeSwitcher />
		</div>
	</div>
	{#if !loading && fileTree}
		<div class="sidebar" class:visible={isSidebarVisible}>
			<Filetree {fileTree} />
		</div>
	{:else if loading}
		<div class="sidebar">Loading file tree...</div>
	{:else if error}
		<div class="sidebar">Error loading file tree: {error}</div>
	{/if}
	<div class="content">
		<slot />
	</div>
</div>

<style>
	.main {
		padding: 0;
		margin: 0;
	}

	.bar {
		position: fixed;
		top: 0;
		width: 100%;
		font-family: 'IBM Plex Sans', sans-serif;
		background: #262626;
		color: #f4f4f4;
		height: 50px;
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: var(--spacing-02) var(--spacing-04);
		z-index: 1000;
		/* border-bottom: 1px solid #393939; */
	}

	.menu {
		width: 20px;
		height: 20px;
	}

	.left-bar {
		display: flex;
		gap: var(--spacing-05);
		fill: #f4f4f4;
	}

	.title {
		font-family: Megrim, sans-serif;
		font-size: 20px;
	}

	.sidebar {
		padding-top: calc(50px + var(--spacing-02));
		width: 256px;
		height: 100%;
		position: fixed;
		border-right: 1px solid var(--border-subtle-01);
		background: var(--layer-01);
		top: 0;
		left: -256px;
		transition: left 0.3s ease-in-out;
	}

	.sidebar.visible {
		left: 0;
	}

	.right-bar {
		display: flex;
		gap: var(--spacing-02);
		align-items: center;
		justify-content: center;
	}

	.content {
		width: 100%;
	}

	@media screen and (min-width: 1280px) {
		.menu {
			display: none;
		}

		.sidebar {
			left: 0;
		}
	}
</style>
