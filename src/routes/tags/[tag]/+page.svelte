<script lang="ts">
	export let data;
</script>

<div class="p-2 text-6xl font-bold lg:pt-6">
	Tag: {data.tag}
</div>

<div class="my-8 p-2">
	<div class="text-2xl">Posts tagged with {data.tag}</div>
	<div class="items-left mt-4 flex flex-col gap-3">
		{#each data.posts as post}
			<div class="text-lg"><a href="/{post.url}">{post.title}</a></div>
		{/each}
	</div>
</div>
