<script>
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';
	import * as Card from '$lib/components/ui/card';

	let graphElement;
	let Graph;

	// Random tree
	const N = 300;
	const gData = {
		nodes: [...Array(N).keys()].map((i) => ({ id: i })),
		links: [...Array(N).keys()]
			.filter((id) => id)
			.map((id) => ({
				source: id,
				target: Math.round(Math.random() * (id - 1))
			})),
		id: [...Array(N).keys()]
	};

	onMount(async () => {
		if (browser) {
			const ForceGraph3D = (await import('3d-force-graph')).default;
			Graph = ForceGraph3D()(graphElement).graphData(gData).nodeLabel('id');
			Graph.width(300);
			Graph.height(300);
		}

		return () => {
			if (Graph) {
				Graph.pauseAnimation();
				Graph._destructor();
			}
		};
	});
</script>

<div class="fixed right-5 top-10 h-[300px] w-[300px]">
	{#if browser}
		<div bind:this={graphElement}></div>
	{/if}
</div>

<style>
</style>
