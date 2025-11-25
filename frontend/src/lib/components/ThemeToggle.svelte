<script>
	import { onMount } from 'svelte';

	let isDark = $state(false);

	onMount(() => {
		// Check localStorage first, then system preference
		const savedTheme = localStorage.getItem('theme');
		
		if (savedTheme === 'dark') {
			isDark = true;
			document.documentElement.classList.add('dark');
		} else if (savedTheme === 'light') {
			isDark = false;
			document.documentElement.classList.remove('dark');
		} else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
			isDark = true;
			document.documentElement.classList.add('dark');
		} else {
			isDark = false;
			document.documentElement.classList.remove('dark');
		}
	});

	function toggleTheme() {
		isDark = !isDark;
		
		if (isDark) {
			document.documentElement.classList.add('dark');
			localStorage.setItem('theme', 'dark');
		} else {
			document.documentElement.classList.remove('dark');
			localStorage.setItem('theme', 'light');
		}
	}
</script>

<button
  onclick={toggleTheme}
  class="relative brut-btn flex items-center gap-2 px-4 py-2 rounded-none font-brut text-sm tracking-wide"
  aria-label="Toggle Dark Mode"
  title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
>
  <span class="inline-block w-3 h-3 border-3" class:rotate-2={isDark} class:rotate-1={!isDark}
    style="background: {isDark ? 'var(--brut-accent)' : 'var(--brut-accent-alt)'}; border-color: var(--brut-ink);"></span>
  {#if isDark}
    <span>LIGHT</span>
  {:else}
    <span>DARK</span>
  {/if}
</button>
