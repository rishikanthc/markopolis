import { writable } from 'svelte/store';
import { mode } from 'mode-watcher';

function createHighlightStore() {
	const { subscribe, set } = writable('github');

	return {
		subscribe,
		setTheme: (isDark: boolean) => {
			set(isDark ? 'github-dark' : 'github');
		}
	};
}

export const highlightTheme = createHighlightStore();
