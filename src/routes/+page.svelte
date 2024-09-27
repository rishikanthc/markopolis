<script>
	export let data;

	function formatDate(dateString) {
		const date = new Date(dateString);
		// Format the date as DD MMM YYYY
		return date.toLocaleDateString('en-GB', {
			day: '2-digit',
			month: 'short',
			year: 'numeric'
		});
	}
</script>

<div class="mb-6 text-4xl font-bold">Latest</div>
<div class="flex flex-col items-start justify-center gap-4">
	{#if data && data.posts.length > 0}
		{#each data.posts as p, id (id)}
			<div class="flex flex-col items-start justify-center gap-0.5">
				<div class="text-xl"><a href="/{p.url}">{p.title}</a></div>
				<div class="text-sm text-gray-400">{formatDate(p.date)}</div>
			</div>
		{/each}
	{:else}
		<div class="text-lg">Please upload markdown files to begin</div>
	{/if}
</div>
