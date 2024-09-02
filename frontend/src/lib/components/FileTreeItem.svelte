<script>
	import { onMount } from 'svelte';
	export let item;
	export let parentPath = '';
	export let expandedFolders;
	export let toggleFolder;
	export let isRoot = false;
	let folderRef;
	$: isFolder = 'folder_name' in item && Array.isArray(item.members);
	$: currentPath = parentPath
		? `${parentPath}/${isFolder ? item.folder_name : item.filename}`
		: isFolder
			? item.folder_name
			: item.filename;
	function handleToggle() {
		toggleFolder(currentPath);
		if (folderRef) {
			folderRef.focus();
		}
	}
	onMount(() => {
		if (isFolder && folderRef) {
			folderRef.tabIndex = 0;
		}
	});
</script>

{#if isFolder}
	<div class="folder-wrapper">
		<div
			bind:this={folderRef}
			class="folder-item"
			class:expanded={$expandedFolders[currentPath]}
			on:click={handleToggle}
			on:keydown={(e) => e.key === 'Enter' && handleToggle()}
			role="button"
			aria-expanded={$expandedFolders[currentPath] || false}
		>
			<svg
				version="1.1"
				id="icon"
				class="file-icon chevron"
				xmlns="http://www.w3.org/2000/svg"
				xmlns:xlink="http://www.w3.org/1999/xlink"
				x="0px"
				y="0px"
				width="32px"
				height="32px"
				viewBox="0 0 32 32"
				style="enable-background:new 0 0 32 32;"
				xml:space="preserve"
			>
				<style type="text/css">
					.st0 {
						fill: none;
					}
				</style>
				<title>caret--right</title>
				<polygon points="12,8 22,16 12,24 " />
				<rect class="st0" width="32" height="32" />
			</svg>
			<svg
				class="file-icon"
				id="icon"
				xmlns="http://www.w3.org/2000/svg"
				viewBox="0 0 32 32"
				width="20"
				height="20"
			>
				<path
					d="M11.17,6l3.42,3.41.58.59H28V26H4V6h7.17m0-2H4A2,2,0,0,0,2,6V26a2,2,0,0,0,2,2H28a2,2,0,0,0,2-2V10a2,2,0,0,0-2-2H16L12.59,4.59A2,2,0,0,0,11.17,4Z"
					transform="translate(0)"
				/>
			</svg>
			<div class="fname">{item.folder_name}</div>
		</div>
		{#if $expandedFolders[currentPath]}
			<div class="folder-contents">
				{#each item.members as subItem (subItem.filename || subItem.folder_name)}
					<svelte:self item={subItem} parentPath={currentPath} {expandedFolders} {toggleFolder} />
				{/each}
			</div>
		{/if}
	</div>
{:else}
	<div class="file-item" class:root={isRoot}>
		<svg
			class="file-icon"
			xmlns="http://www.w3.org/2000/svg"
			viewBox="0 0 32 32"
			width="1em"
			height="1em"
		>
			<path
				d="M25.7,9.3l-7-7C18.5,2.1,18.3,2,18,2H8C6.9,2,6,2.9,6,4v24c0,1.1,0.9,2,2,2h16c1.1,0,2-0.9,2-2V10C26,9.7,25.9,9.5,25.7,9.3
	z M18,4.4l5.6,5.6H18V4.4z M24,28H8V4h8v6c0,1.1,0.9,2,2,2h6V28z"
			/>
			<rect x="10" y="22" width="12" height="2" />
			<rect x="10" y="16" width="12" height="2" />
		</svg>
		<a href={item.link}>{item.title || item.filename}</a>
	</div>
{/if}

<style>
	.folder-wrapper {
		width: 100%;
		box-sizing: border-box;
	}
	.folder-item {
		cursor: pointer;
		display: flex;
		align-items: center;
		width: 100%;
		min-height: 2rem;
		padding: var(--spacing-03) var(--spacing-04);
		box-sizing: border-box;
		outline: none;
		color: var(--text-secondary);
	}
	.folder-item:hover,
	.folder-item:focus {
		background: var(--background-hover);
		color: var(--text-primary);
	}
	.folder-item:focus {
		outline: 2px solid var(--focus, #0f62fe);
		outline-offset: -2px;
	}
	.folder-item .fname {
		margin-left: var(--spacing-03);
		flex-grow: 1;
	}
	.chevron {
		margin-right: var(--spacing-03);
		transition: transform 0.3s ease;
	}
	.folder-item.expanded .chevron {
		transform: rotate(90deg);
	}
	.folder-contents {
		width: 100%;
		box-sizing: border-box;
		/* padding-left: var(--spacing-05); */
	}
	.file-item {
		display: flex;
		align-items: center;
		min-height: 2rem;
		padding: var(--spacing-02) var(--spacing-04);
		box-sizing: border-box;
		width: 100%;
	}
	.file-item a {
		text-decoration: none;
		color: var(--text-primary);
		font-size: 0.875rem;
		font-weight: 300;
		margin-left: var(--spacing-03);
	}
	.file-item:not(.root) {
		padding-left: calc(var(--spacing-03) + 50px);
	}
	.file-item:hover {
		background: var(--background-hover);
		color: var(--text-secondary);
	}
	.file-icon {
		fill: var(--text-primary);
		width: 1em;
		height: 1em;
		vertical-align: middle;
	}
</style>
