<script lang="ts">
	import MDsvexRenderer from '$lib/components/MDsvexRenderer.svelte';
	import MDGraph from '$lib/components/MDGraph.svelte';

	export let data: { content: string };
	$: content = data.post?.content;
	$: graphData = data.graphData;
</script>

<div class="mb-12 mt-6 text-wrap text-6xl md:w-[700px] md:text-8xl">
	{data.title}
</div>
<MDsvexRenderer bind:content />
<div>
	{#if data?.backlinks?.length > 0}
		<div class="mb-2 mt-12 text-2xl font-light">BACKLINKS</div>
	{/if}
	{#each data?.backlinks || [] as bl (bl.id)}
		<div><a href={`/writing/${bl.url.trim()}`} class="text-large">{bl.title}</a></div>
	{/each}
</div>
