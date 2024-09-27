<script>
	import { onMount } from 'svelte';
	import { Canvas } from '@threlte/core';
	/* import Scene from '$lib/components/Scene.svelte'; */
	import Scene from '$lib/components/GraphScene.svelte';

	export let graphData;
	let nodes = [];
	let edges = [];
	let simulation;

	onMount(() => {
		if (graphData) {
			nodes = graphData.nodes.map((node) => ({ ...node, x: 0, y: 0, z: 0 }));
			edges = graphData.edges.map((edge) => ({
				source: nodes.find((node) => node.id === edge.from),
				target: nodes.find((node) => node.id === edge.to)
			}));

			simulation = forceSimulation(nodes)
				.force(
					'link',
					forceLink(edges)
						.id((d) => d.id)
						.distance(100)
				)
				.force('charge', forceManyBody().strength(-200))
				.force('center', forceCenter(0, 0, 0));

			simulation.on('tick', () => {
				nodes = [...nodes];
				edges = [...edges];
			});
		}
	});
</script>

<div class="h-[200px]">
	<div class="wrapper">
		<Canvas>
			<Scene />
		</Canvas>
	</div>
</div>

<style>
	div.wrapper {
		height: 100%;
	}
	div.description {
		position: absolute;
		bottom: 10px;
		left: 10px;
		z-index: 10;
		color: #fe3d00;
	}
</style>
