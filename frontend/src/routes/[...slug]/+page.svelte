<script>
	import { onMount, tick } from 'svelte';

	export let data;
	/* let base_url = 'http://localhost:5173/'; */
	$: ({ content, frontmatter, backlinks, frontend_url, error } = data);

	let contentRendered = false;

	$: if (content && content.html_content) {
		contentRendered = false;
		tick().then(() => {
			contentRendered = true;
		});
	}

	$: if (contentRendered) {
		tick().then(() => {
			if (typeof mermaid !== 'undefined') {
				mermaid.initialize({ startOnLoad: false });
				mermaid.init(undefined, document.querySelectorAll('.mermaid'));
			} else {
				console.error('Mermaid library not loaded');
			}

			hljs.highlightAll();
		});
	}

	onMount(() => {
		if (typeof mermaid === 'undefined') {
			console.error('Mermaid library not loaded');
		}
	});
</script>

<div class="title">
	{#if error}
		<p>Error: {error}</p>
	{:else if frontmatter}
		<h1>{frontmatter.title}</h1>
		<div class="tags">
			{#each frontmatter.tags as t}
				<div class="tag">{t}</div>
			{/each}
		</div>
	{:else}
		<p>Content not available</p>
	{/if}
</div>

<div class="content">
	{#if error}
		<p>Error: {error}</p>
	{:else if content && content.html_content}
		{@html content.html_content}
	{:else}
		<p>Content not available</p>
	{/if}
	<div class="backlinks">
		{#if error}
			<p>Error: {error}</p>
		{:else if backlinks && backlinks.backlinks && Array.isArray(backlinks.backlinks)}
			<h2>BACKLINKS</h2>
			{#each backlinks.backlinks as bl}
				<div class="backlink"><a href={frontend_url + '/' + bl.path}>{bl.title}</a></div>
			{/each}
		{:else}
			<p>No backlinks available</p>
		{/if}
	</div>
</div>

<style>
	.backlinks {
		display: flex;
		flex-direction: column;
		width: 100%;
		/* margin-left: 256px; */
		align-items: start;
		margin-bottom: var(--spacing-10);
	}
	.backlink {
		color: var(--text-primary);
	}
	.content {
		width: min(784px, 100%);
		height: 100%;
		padding: var(--spacing-05);
		box-sizing: border-box;
	}
	.title {
		display: flex;
		flex-direction: column;
		align-items: start;
		justify-content: end;
		gap: var(--spacing-03);
		width: 100%;
		/* background: #262626; */
		color: #f4f4f4;
		height: 12em;
		margin-top: calc(50px + var(--spacing-02));
		margin-bottom: var(--spacing-10);
		padding: var(--spacing-05);
		box-sizing: border-box;
	}
	.title h1 {
		color: #f4f4f4;
		color: var(--text-primary);
		margin: 0;
	}

	.tags {
		display: flex;
		gap: var(--spacing-05);
	}

	.tag {
		font-size: 14px;
		border-radius: 3px;
		/* background: var(--tag); */
		/* background: #161616; */
		padding: var(--spacing-02) var(--spacing-03);
		color: #c6c6c6;
		color: var(--text-secondary);

		/* box-shadow:
			inset 0 2px 2px #000,
			0 2px 0 hsla(30, 0%, 32%, 0.55); */

		box-shadow:
			inset 0 2px 2px var(--title-shadow-inset),
			0 2.2px 2px var(--title-shadow-bottom);
	}
	:global(th) {
		background: var(--layer-active-01);
	}

	:global(table) {
		min-width: 67.3%;
		width: 100%;
		line-height: 1.25;
		border-spacing: 0;
		border-collapse: collapse;
		color: var(--text-primary);
		margin: var(--spacing-08) 0;
	}

	:global(th, td) {
		padding: 1rem;
		line-height: 1.42857;
		text-align: left;
	}
	:global(tbody tr) {
		border-bottom: 1px solid var(--border-subtle-01);
		background: var(--layer-01);
	}

	.backlinks {
		display: flex;
		flex-direction: column;
		gap: var(--spacing-03);
	}

	@media screen and (min-width: 1280px) {
		.content {
			padding: 0;
			padding-left: calc(256px + 150px);
			margin-top: calc(50px + var(--spacing-02));
			box-sizing: content-box;
		}
		.title {
			padding-left: calc(256px + 150px);
		}
	}
</style>
