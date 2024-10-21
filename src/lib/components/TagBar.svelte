<script lang="ts">
	import { afterNavigate, beforeNavigate } from "$app/navigation";
	import { Tags } from "lucide-svelte";
	import { Button } from "$lib/components/ui/button";
	import { ScrollArea } from "$lib/components/ui/scroll-area/index.js";

	export let tags;
	let hidden = true;

	function toggle() {
		hidden = !hidden;
	}

	beforeNavigate(() => {
		hidden = true;
	});
</script>

<Button variant="ghost" size="icon" on:click={toggle}>
	<Tags />
</Button>

<ScrollArea
	class={`${hidden ? "hidden" : ""} fixed right-4 top-9 h-[500px] w-[200px] rounded-sm bg-carbongray-50 dark:bg-carbongray-700 p-2 shadow`}
>
	<div class="flex flex-col justify-center gap-2 p-2">
		<div class="my-2 text-base font-bold">TAGS</div>
		{#each tags as tag (tag.name)}
			<div>
				<a
					class="text-primary hover:bg-carbongray-100 w-full p-1 rounded-sm dark:hover:bg-carbongray-600"
					href="/tags/{tag.name}">#{tag.name}</a
				>
			</div>
		{/each}
	</div>
</ScrollArea>
