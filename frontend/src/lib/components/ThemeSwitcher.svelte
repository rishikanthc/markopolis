<script>
	import { onMount } from 'svelte';

	let theme = 'light';
	let themeSwitcher;
	let themeText;

	onMount(() => {
		theme = localStorage.getItem('theme') || 'light';
		document.documentElement.setAttribute('data-theme', theme);
		updateThemeToggle(theme);
		updateHighlightTheme(theme);
	});

	function toggleTheme() {
		theme = theme === 'dark' ? 'light' : 'dark';
		document.documentElement.setAttribute('data-theme', theme);
		localStorage.setItem('theme', theme);
		updateThemeToggle(theme);
		updateHighlightTheme(theme);
	}

	function updateThemeToggle(currentTheme) {
		if (currentTheme === 'dark') {
			themeSwitcher.classList.add('dark');
			themeSwitcher.setAttribute('aria-label', 'Switch to light mode');
			themeText.textContent = 'Light mode';
		} else {
			themeSwitcher.classList.remove('dark');
			themeSwitcher.setAttribute('aria-label', 'Switch to dark mode');
			themeText.textContent = 'Dark mode';
		}
	}

	function updateHighlightTheme(currentTheme) {
		const lightTheme = document.getElementById('light-theme');
		const darkTheme = document.getElementById('dark-theme');
		if (lightTheme && darkTheme) {
			lightTheme.disabled = currentTheme === 'dark';
			darkTheme.disabled = currentTheme === 'light';
		}
	}

	function handleKeydown(e) {
		if (e.key === 'Enter' || e.key === ' ') {
			e.preventDefault();
			toggleTheme();
		}
	}

	$: isDarkTheme = theme === 'dark';
</script>

<div class="theme-toggle">
	<div
		bind:this={themeSwitcher}
		class="switcher"
		class:dark={isDarkTheme}
		role="button"
		tabindex="0"
		aria-label="Toggle dark mode"
		on:click={toggleTheme}
		on:touchend|preventDefault={toggleTheme}
		on:keydown={handleKeydown}
	>
		<span bind:this={themeText}>{isDarkTheme ? 'Light' : 'Dark'} mode</span>
		<span class="theme-icon">
			<i class="fas fa-sun"></i>
			<i class="fas fa-moon"></i>
		</span>
	</div>
</div>

<style>
	/* Theme Switcher */
	.switcher {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		cursor: pointer;
		padding: 0.5rem 1rem;
		border-radius: 20px;
		transition: background-color 0.3s ease;
		user-select: none;
	}
	.theme-icon {
		font-size: var(--text-02);
		display: flex;
		align-items: center;
		justify-content: center;
	}
	.theme-icon .fa-sun {
		display: none;
	}
	.theme-icon .fa-moon {
		display: inline-block;
	}
	.switcher.dark .fa-sun {
		display: inline-block;
	}
	.switcher.dark .fa-moon {
		display: none;
	}
</style>
