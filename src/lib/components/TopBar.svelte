<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import { Menu } from 'lucide-svelte';
	import { isSidebarVisible } from '$lib/stores/sidebarStore';

	function toggleSidebar() {
		isSidebarVisible.update((value) => !value);
	}
	export let title;
</script>

<div class="absolute left-0 top-0 z-30 flex h-[40px] items-center justify-between md:hidden">
	<Button variant="ghost" size="icon" on:click={toggleSidebar}
		><Menu class="text-carbongray-300" /></Button
	>
	{#if title}
		<div class="title text-2xl">{title}</div>
	{/if}
</div>

<style>
	.title {
		font-family: Megrim;
	}
</style>
