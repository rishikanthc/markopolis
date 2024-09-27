<script lang="ts">
	import { Sun, Moon, User } from 'lucide-svelte';

	import { toggleMode } from 'mode-watcher';
	import FileTree from '$lib/components/FileTree.svelte';
	import SearchComponent from '$lib/components/SearchComponent.svelte';
	import { Button } from '$lib/components/ui/button/index.js';

	export let title;
</script>

<div class="mx-auto my-6 flex w-5/6 flex-col justify-start gap-3">
	<div class="stitle flex-shrink text-4xl uppercase text-carbonblue-400">
		{title}
	</div>
	<div class="gap-0.3 mb-8 flex flex-col justify-start text-sm">
		<div>Machine Learning / Self-Hosting</div>
		<div>Technology /</div>
	</div>

	<Button
		on:click={toggleMode}
		variant="ghost"
		size="icon"
		class="absolute right-2 top-2 h-[15px] w-[15px]"
	>
		<Sun
			class="h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0"
		/>
		<Moon
			class="absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100"
		/>
		<span class="sr-only">Toggle theme</span>
	</Button>

	<slot></slot>
</div>

<style>
	.stitle {
		font-family: 'Lombok';
	}
</style>
