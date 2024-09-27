<script lang="ts">
	import '../app.css';
	import { ModeWatcher } from 'mode-watcher';
	import { Separator } from '$lib/components/ui/separator';
	import Sidebar from '$lib/components/Sidebar.svelte';
	import FileTree from '$lib/components/FileTree.svelte';
	import { onMount } from 'svelte';
	import { Button } from '$lib/components/ui/button';
	import { Menu, Grip, SquareX } from 'lucide-svelte';
	import { beforeNavigate } from '$app/navigation';
	import SearchComponent from '$lib/components/SearchComponent.svelte';
	import TagBar from '$lib/components/TagBar.svelte';

	export let data;
	let showSidebar = false;
	let sidebarRef;
	let toggleButtonRef;
	$: fileTree = data?.filetree;
	$: siteTitle = data?.siteTitle;
	$: tags = data?.tags;

	// Toggle sidebar visibility
	function toggleSidebar() {
		showSidebar = !showSidebar;
	}

	// Close sidebar when clicking outside
	function handleClickOutside(event) {
		console.log('clicked');
		if (
			sidebarRef &&
			!sidebarRef.contains(event.target) &&
			toggleButtonRef &&
			!toggleButtonRef.contains(event.target)
		) {
			showSidebar = false;
		}
	}

	onMount(() => {
		document.addEventListener('click', handleClickOutside);
		return () => {
			document.removeEventListener('click', handleClickOutside);
		};
	});

	beforeNavigate(() => {
		showSidebar = false;
	});
</script>

<!-- Toggle button to control sidebar visibility -->
<div
	bind:this={toggleButtonRef}
	class="fixed left-0 top-0 flex w-[100%] flex-col items-start justify-center gap-2 bg-background lg:hidden"
>
	<div class="flex w-[100%] items-center justify-between">
		<div class="flex items-center justify-start">
			<Button class="z-20" on:click={toggleSidebar} variant="ghost" size="icon">
				<Grip />
			</Button>
			<div class="title text-2xl">{siteTitle}</div>
		</div>
		<div class="gap-0.1 flex">
			<TagBar {tags} />
			<SearchComponent />
		</div>
	</div>
</div>

<div class="fixed right-0 top-0 hidden w-[100%] items-center justify-end bg-background lg:flex">
	<TagBar {tags} />
	<SearchComponent />
</div>
<!-- Sidebar -->
<div
	bind:this={sidebarRef}
	class={`fixed left-0 top-0 z-30 flex h-svh w-72 justify-between bg-background transition-transform lg:translate-x-0 ${showSidebar ? '' : '-translate-x-full'}`}
>
	<Sidebar title={siteTitle} captions={data.captions}>
		{#if fileTree}
			<FileTree bind:fileTree />
		{:else}
			Loading...
		{/if}
	</Sidebar>
	<Separator orientation="vertical" class="h-full"></Separator>
</div>

<!-- Main content -->
<div class="z-10 w-[100%] p-2 pt-12 lg:pl-80 lg:pt-6">
	<ModeWatcher />
	<slot></slot>
</div>

<style>
	/* Ensure smooth transition when showing/hiding the sidebar */
	.transition-transform {
		transition: transform 0.2s ease-in-out;
	}
	.translate-x-full {
		transform: translateX(-100%);
	}
	.title {
		font-family: Megrim;
	}
</style>
