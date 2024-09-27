<script lang="ts">
	import { T } from '@threlte/core';
	import { Grid, OrbitControls, interactivity } from '@threlte/extras';
	import { spring } from 'svelte/motion';
	import { Vector3 } from 'three';
	interactivity();

	const scale = spring(1);
	let fromPosition = new Vector3(1, 1, 0);
	let toPosition = new Vector3(2, 2, 0);

	let edgeColor = 'red'; // Replace with your color logic

	// Define some sample graph data
	const nodes = [
		{ id: 1, position: [0, 0, 0] },
		{ id: 2, position: [2, 1, 1] },
		{ id: 3, position: [-1, 2, -1] },
		{ id: 4, position: [1, -1, 2] }
	];

	const edges = [
		{ from: 1, to: 2 },
		{ from: 1, to: 3 },
		{ from: 2, to: 4 },
		{ from: 3, to: 4 }
	];

	const nodeRadius = 0.3;
	const nodeColor = '#FE3D00';
</script>

<T.PerspectiveCamera
	makeDefault
	position={[10, 10, 10]}
	on:create={({ ref }) => {
		ref.lookAt(0, 0, 0);
	}}
>
	<OrbitControls />
</T.PerspectiveCamera>

<T.DirectionalLight position={[3, 10, 7]} intensity={Math.PI} />
<T.AmbientLight intensity={0.3} />

<T.Group scale={$scale} on:pointerenter={() => scale.set(1.2)} on:pointerleave={() => scale.set(1)}>
	{#each nodes as node}
		<T.Mesh position={node.position}>
			<T.SphereGeometry args={[nodeRadius]} />
			<T.MeshStandardMaterial color={nodeColor} toneMapped={false} />
		</T.Mesh>
	{/each}

	{#each edges as edge}
		<T.Line points={[fromPosition, toPosition]} color={edgeColor} lineWidth={2} />
	{/each}
</T.Group>

<Grid cellColor="#FE3D00" sectionColor="#FE3D00" />
