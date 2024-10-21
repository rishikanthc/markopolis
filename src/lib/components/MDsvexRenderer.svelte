<!-- MDsveXContentRenderer.svelte -->
<script lang="ts">
	import { onMount, tick } from "svelte";
	import { afterNavigate } from "$app/navigation";
	import mermaid from "mermaid";
	import hljs from "highlight.js"; // Import highlight.js
	// import 'highlight.js/styles/nnfx-dark.min.css'; // Import a default style for highlight.js
	import "highlight.js/styles/default.css";
	// import 'highlight.js/styles/github-dark.css';
	import { browser } from "$app/environment";

	export let content: string;

	// Function to initialize and render mermaid diagrams
	const renderMermaid = async () => {
		// Reinitialize Mermaid every time we want to render
		mermaid.initialize({ startOnLoad: false });
		await tick(); // Ensure DOM is updated
		mermaid.run({
			querySelector: ".mermaid", // Render all elements with the mermaid class
		});
	};

	const updateHighlightTheme = () => {
		if (browser) {
			const isDarkMode = window.matchMedia(
				"(prefers-color-scheme: dark)",
			).matches;
			document.documentElement.classList.toggle("theme-dark", isDarkMode);
			document.documentElement.classList.toggle("theme-light", !isDarkMode);
			hljs.highlightAll();
		}
	};

	const highlightCode = () => {
		hljs.highlightAll();
	};

	onMount(async () => {
		await renderMermaid();
		hljs.highlightAll();
		// updateHighlightTheme();

		// if (browser) {
		// 	const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
		// 	mediaQuery.addListener(updateHighlightTheme);

		// 	return () => mediaQuery.removeListener(updateHighlightTheme);
		// }
	});
	// Use the afterNavigate hook to re-render mermaid diagrams after every navigation
	afterNavigate(async () => {
		await renderMermaid();
		// highlightCode();
	});
</script>

<div class="text-lg leading-relaxed md:w-[700px]">
	{@html content}
</div>

<style>
	:global(pre) {
		@apply my-4 rounded bg-carbongray-100 p-2 shadow-sm dark:bg-carbongray-400;
		max-width: 100%;
		white-space: pre-wrap;
		word-wrap: break-word;
		overflow-wrap: break-word;
	}

	:global(pre code) {
		@apply font-mono text-base;
		font-family: monospace;
		white-space: pre-wrap;
		word-wrap: break-word;
		overflow-wrap: break-word;
	}

	:global(code) {
		@apply font-mono text-sm;
		max-width: 100%;
	}

	/* For inline code */
	:global(p code) {
		@apply bg-carbongray-100 rounded-sm px-1 py-0.5;
		white-space: normal;
		word-wrap: break-word;
		overflow-wrap: break-word;
	}
	:global(.mermaid) {
		text-align: center;
	}

	:global(.callout) {
		width: 100%;
	}
	:global(.mermaid) {
		@apply sm:w-[80svw] md:w-[65svw] xl:w-[80svw];
	}

	:global(table) {
		@apply my-8 w-full text-left text-sm text-gray-500 dark:text-gray-400 rtl:text-right;
	}
	:global(thead) {
		@apply bg-gray-50 text-xs uppercase text-gray-700 dark:bg-carbongray-600 dark:text-gray-400;
	}
	:global(th) {
		@apply px-6 py-3;
	}
	:global(tbody tr) {
		@apply border-b bg-white dark:border-carbongray-600 dark:bg-carbongray-700;
	}
	:global(tbody td) {
		@apply whitespace-nowrap border-l-0 border-r-0 border-t-0 p-4 px-6 align-middle text-xs;
	}

	:global(.task-list-item) {
		@apply flex list-none items-center py-2;
	}

	:global(.task-list-item input[type="checkbox"]),
	:global(input[type="checkbox"]) {
		@apply mr-2 h-4 w-4 cursor-pointer appearance-none border bg-white transition-all duration-200 ease-in-out;
		position: relative;
	}

	:global(.task-list-item input[type="checkbox"]:checked),
	:global(input[type="checkbox"]:checked) {
		@apply border-blue-500 bg-blue-500;
	}

	:global(.task-list-item input[type="checkbox"]:checked::before),
	:global(input[type="checkbox"]:checked::before) {
		content: "\2713";
		@apply absolute text-xs font-bold text-white;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
	}

	:global(.task-list-item input[type="checkbox"]:disabled),
	:global(input[type="checkbox"]:disabled) {
		@apply cursor-not-allowed border-carbongray-800;
	}

	:global(.task-list-item input[type="checkbox"]:disabled:checked),
	:global(input[type="checkbox"]:disabled:checked) {
		@apply border-carbongray-700 bg-carbongray-100 dark:bg-carbongray-600;
	}

	:global(.task-list-item input[type="checkbox"]:disabled:checked::before),
	:global(input[type="checkbox"]:disabled:checked::before) {
		@apply text-gray-500 dark:text-carbongray-100;
	}

	:global(.task-list-item),
	:global(input[type="checkbox"] + *) {
		@apply select-none text-lg;
	}

	:global(.task-list-item input[type="checkbox"]:disabled ~ *),
	:global(input[type="checkbox"]:disabled + *) {
		@apply text-gray-400;
	}

	:global(li) {
		@apply relative pb-2 pl-8 text-lg leading-relaxed;
		@apply flex flex-col items-start justify-start;
	}

	/* Unordered list styles with centered dot */
	:global(ul > li::before) {
		content: "";
		@apply absolute left-2 top-[35%] h-2 w-2 rounded-full bg-carbonblue-500;
	}

	/* Ordered list styles */
	/* :global(ol > li::before) {
		content: counter(list-counter);
		counter-increment: list-counter;
		@apply absolute left-0 top-[0.3em] flex h-5 w-5 items-center justify-center rounded-full bg-blue-100 text-xs font-semibold text-blue-500;
	} */

	:global(ol) {
		counter-reset: list-counter;
		list-style-type: none;
		padding-left: 0;
	}

	:global(ol > li) {
		counter-increment: list-counter;
		@apply relative pb-2 pl-8 text-lg leading-relaxed;
		@apply flex flex-col items-start justify-start;
	}

	:global(ol > li::before) {
		content: counter(list-counter);
		@apply absolute left-0 top-[0.3em] flex h-5 w-5 items-center justify-center rounded-full bg-blue-100 text-xs font-semibold text-blue-500;
	}

	/* Task list item specific adjustments */
	:global(.task-list-item) {
		@apply flex flex-row items-start pl-0;
	}

	:global(.task-list-item::before) {
		content: none;
	}

	:global(.task-list-item input[type="checkbox"]) {
		@apply mr-2 mt-1;
	}

	/* Checkbox styles */
	:global(.task-list-item input[type="checkbox"]),
	:global(input[type="checkbox"]) {
		@apply h-4 w-4 cursor-pointer appearance-none rounded border border-gray-300 bg-white transition-all duration-200 ease-in-out;
		position: relative;
	}

	:global(.task-list-item input[type="checkbox"]:checked),
	:global(input[type="checkbox"]:checked) {
		@apply border-blue-500 bg-blue-500;
	}

	:global(.task-list-item input[type="checkbox"]:checked::before),
	:global(input[type="checkbox"]:checked::before) {
		content: "\2713";
		@apply absolute text-xs font-bold text-white;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
	}

	:global(.task-list-item input[type="checkbox"]:disabled),
	:global(input[type="checkbox"]:disabled) {
		@apply cursor-not-allowed border-gray-200 bg-gray-100;
	}

	:global(.task-list-item input[type="checkbox"]:disabled:checked),
	:global(input[type="checkbox"]:disabled:checked) {
		@apply border-gray-300 bg-gray-300;
	}

	:global(.task-list-item input[type="checkbox"]:disabled:checked::before),
	:global(input[type="checkbox"]:disabled:checked::before) {
		@apply text-white;
	}
	:global(img) {
		max-width: 100%;
	}

	:global(blockquote) {
		@apply relative p-4;
	}

	:global(blockquote::before) {
		content: "";
		@apply absolute -left-8 -top-2 h-20 w-20 bg-carbongray-100 dark:bg-carbongray-600; /* Positioning, size, and color */
		mask: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="none"><path d="M7.39762 10.3C7.39762 11.0733 7.14888 11.7 6.6514 12.18C6.15392 12.6333 5.52552 12.86 4.76621 12.86C3.84979 12.86 3.09047 12.5533 2.48825 11.94C1.91222 11.3266 1.62421 10.4467 1.62421 9.29999C1.62421 8.07332 1.96459 6.87332 2.64535 5.69999C3.35231 4.49999 4.33418 3.55332 5.59098 2.85999L6.4943 4.25999C5.81354 4.73999 5.26369 5.27332 4.84476 5.85999C4.45201 6.44666 4.19017 7.12666 4.05926 7.89999C4.29491 7.79332 4.56983 7.73999 4.88403 7.73999C5.61716 7.73999 6.21938 7.97999 6.69067 8.45999C7.16197 8.93999 7.39762 9.55333 7.39762 10.3ZM14.6242 10.3C14.6242 11.0733 14.3755 11.7 13.878 12.18C13.3805 12.6333 12.7521 12.86 11.9928 12.86C11.0764 12.86 10.3171 12.5533 9.71484 11.94C9.13881 11.3266 8.85079 10.4467 8.85079 9.29999C8.85079 8.07332 9.19117 6.87332 9.87194 5.69999C10.5789 4.49999 11.5608 3.55332 12.8176 2.85999L13.7209 4.25999C13.0401 4.73999 12.4903 5.27332 12.0713 5.85999C11.6786 6.44666 11.4168 7.12666 11.2858 7.89999C11.5215 7.79332 11.7964 7.73999 12.1106 7.73999C12.8437 7.73999 13.446 7.97999 13.9173 8.45999C14.3886 8.93999 14.6242 9.55333 14.6242 10.3Z" fill="currentColor"/></svg>');
	}

	:global(blockquote p) {
		@apply relative z-10 text-xl font-light italic;
	}
	:global(.highlight) {
		@apply bg-[#ef538c] p-0.5 text-carbongray-900;
	}

	:global(.tag a) {
		@apply mx-0.5 rounded-sm bg-[#fedc69] p-0.5 text-carbongray-900;
	}
	:global(.hljs-light) {
		--hljs-theme: initial;
	}

	:global(.hljs-dark) {
		--hljs-theme: github-dark;
	}

	:global(.hljs) {
		background: var(--hljs-theme);
	}
</style>
