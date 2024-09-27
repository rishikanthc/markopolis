<script lang="ts">
	import MDsvexRenderer from '$lib/components/MDsvexRenderer.svelte';
	import MDGraph from '$lib/components/MDGraph.svelte';
	import { CalendarDays } from 'lucide-svelte';

	export let data: { content: string };
	$: content = data.post?.content;
	$: tags = data?.tags;
	$: date = data.post?.created;
</script>

<div class="mb-10 mt-6 text-wrap md:w-[700px]">
	<div class="my-4 text-6xl md:text-8xl">
		{data.title}
	</div>

	<div class="flex flex-col justify-center gap-1">
		<div class="flex items-center gap-1">
			<CalendarDays class="text-carbongray-400" size={15} />
			<div class="text-base text-carbongray-400">{date.split(' ')[0]}</div>
		</div>
		{#if tags}
			<div class="flex flex-wrap gap-1">
				{#each tags as tag (tag.name)}
					<span class="mx-0.5 rounded-sm bg-[#fedc69] p-0.5 text-carbongray-900"
						><a class="text-carbongray-900 dark:text-carbongray-900" href="/tags/{tag.name}"
							>{tag.name}</a
						></span
					>
				{/each}
			</div>
		{/if}
	</div>
	<hr class="mt-6" />
</div>
<MDsvexRenderer bind:content />
<div>
	{#if data?.backlinks?.length > 0}
		<hr class="my-4 w-[700px]" />
		<div class="mb-2 mt-4 text-2xl font-light">BACKLINKS</div>
	{/if}
	{#each data?.backlinks || [] as bl (bl.id)}
		<div><a href={`/${bl.url.trim()}`} class="text-large">{bl.title}</a></div>
	{/each}
</div>

<style>
	:global(.tag a) {
		@apply mx-0.5 bg-[#fedc69] p-1 text-carbongray-900;
	}
</style>
