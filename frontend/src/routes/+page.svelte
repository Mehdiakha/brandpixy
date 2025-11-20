<script>
	import { onMount } from 'svelte';
	import { fade, fly } from 'svelte/transition';
	import gsap from 'gsap';
	import { ScrollTrigger } from 'gsap/dist/ScrollTrigger';

	let industry = '';
	let vibe = 'Modern';
	let loading = false;
	let suggestions = [];
	let showApp = false;
	let generatingLogoFor = null;

	const vibes = ['Modern', 'Luxury', 'Fun', 'Minimalist', 'Tech', 'Classic', 'Professional'];

	onMount(() => {
		gsap.registerPlugin(ScrollTrigger);
		if (!showApp) {
			initLandingAnimations();
		}
	});

	function initLandingAnimations() {
		const tl = gsap.timeline();
		tl.from('.landing-content', { y: 50, opacity: 0, duration: 1, ease: 'power3.out' });
	}

	async function submit() {
		if (!industry) return;
		loading = true;
		suggestions = [];
		try {
			const res = await fetch('/api/generate', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ industry, vibe, values: '' })
			});
			const data = await res.json();
			suggestions = data.suggestions || [];
		} catch (e) {
			console.error(e);
		} finally {
			loading = false;
		}
	}

	async function generateLogo(index, name) {
		generatingLogoFor = index;
		try {
			const res = await fetch(`/api/generate-logo?name=${encodeURIComponent(name)}&vibe=${encodeURIComponent(vibe)}`, {
				method: 'POST'
			});
			const data = await res.json();
			if (data.url) {
				suggestions[index].logoUrl = data.url;
				suggestions = [...suggestions];
			}
		} catch (e) {
			console.error(e);
		} finally {
			generatingLogoFor = null;
		}
	}
</script>

{#if !showApp}
	<div class="min-h-screen bg-gradient-to-br from-indigo-50 to-purple-50 flex flex-col items-center justify-center p-6 text-center landing-content">
		<h1 class="text-5xl md:text-7xl font-extrabold text-indigo-900 mb-6 tracking-tight">
			Brand<span class="text-indigo-600">Pixy</span>
		</h1>
		<p class="text-xl text-slate-600 max-w-2xl mb-10 leading-relaxed">
			Generate unique brand identities, names, and logos in seconds using advanced AI.
		</p>
		<button 
			class="px-8 py-4 bg-indigo-600 text-white text-lg font-bold rounded-full shadow-lg hover:bg-indigo-700 hover:shadow-xl transition-all transform hover:-translate-y-1"
			on:click={() => showApp = true}
		>
			Start Generating
		</button>
	</div>
{:else}
	<div class="min-h-screen bg-slate-50 font-sans text-slate-900">
		<!-- Header -->
		<header class="bg-white border-b border-slate-200 sticky top-0 z-50">
			<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
				<div class="flex items-center gap-2 cursor-pointer" on:click={() => { showApp = false; suggestions = []; industry = ''; }}>
					<div class="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center text-white font-bold">B</div>
					<span class="text-xl font-bold text-slate-900">BrandPixy</span>
				</div>
			</div>
		</header>

		<main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
			<!-- Input Section -->
			<div class="max-w-3xl mx-auto bg-white rounded-2xl shadow-sm border border-slate-200 p-6 md:p-8 mb-12">
				<div class="grid grid-cols-1 md:grid-cols-12 gap-6">
					<div class="md:col-span-7">
						<label for="industry" class="block text-sm font-medium text-slate-700 mb-2">Industry</label>
						<input 
							type="text" 
							id="industry"
							bind:value={industry}
							placeholder="e.g. Coffee Shop, Tech Startup..."
							class="w-full px-4 py-3 rounded-xl border border-slate-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all"
						/>
					</div>
					<div class="md:col-span-3">
						<label for="vibe" class="block text-sm font-medium text-slate-700 mb-2">Style / Vibe</label>
						<select 
							id="vibe"
							bind:value={vibe}
							class="w-full px-4 py-3 rounded-xl border border-slate-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all bg-white"
						>
							{#each vibes as v}
								<option value={v}>{v}</option>
							{/each}
						</select>
					</div>
					<div class="md:col-span-2 flex items-end">
						<button 
							on:click={submit}
							disabled={loading || !industry}
							class="w-full py-3 px-4 bg-indigo-600 text-white font-semibold rounded-xl shadow-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center"
						>
							{#if loading}
								<svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
									<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
									<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
								</svg>
							{:else}
								Generate
							{/if}
						</button>
					</div>
				</div>
			</div>

			<!-- Results Section -->
			{#if suggestions.length > 0}
				<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
					{#each suggestions as s, i}
						<div class="bg-white rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition-all duration-300 overflow-hidden group flex flex-col" in:fade={{ delay: i * 50, duration: 300 }}>
							<div class="p-6 flex-1 flex flex-col items-center text-center">
								<div class="w-full aspect-video bg-slate-50 rounded-xl mb-4 flex items-center justify-center overflow-hidden relative group-hover:bg-indigo-50 transition-colors">
									{#if s.logoUrl}
										<img src={s.logoUrl} alt="{s.name} logo" class="w-full h-full object-contain p-4" in:fade />
									{:else}
										<div class="transform scale-75 opacity-80">
											{@html s.svg}
										</div>
									{/if}
								</div>
								<h3 class="text-xl font-bold text-slate-900 mb-1">{s.name}</h3>
								<p class="text-sm text-slate-500 leading-relaxed">{s.tagline}</p>
							</div>
							<div class="p-4 border-t border-slate-100 bg-slate-50/50">
								<button 
									class="w-full py-2 px-4 bg-white border border-slate-300 text-slate-700 font-medium rounded-lg text-sm hover:bg-slate-50 hover:text-indigo-600 hover:border-indigo-200 transition-all flex items-center justify-center gap-2"
									on:click={() => generateLogo(i, s.name)}
									disabled={generatingLogoFor === i || s.logoUrl}
								>
									{#if generatingLogoFor === i}
										<svg class="animate-spin h-4 w-4 text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
											<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
											<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
										</svg>
										<span>Creating...</span>
									{:else if s.logoUrl}
										<svg class="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
										<span>Logo Ready</span>
									{:else}
										<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
										<span>Generate Logo</span>
									{/if}
								</button>
							</div>
						</div>
					{/each}
				</div>
			{/if}
		</main>
	</div>
{/if}
