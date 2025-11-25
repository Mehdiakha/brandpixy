<script>
	import { onMount } from 'svelte';
	import { fade, fly, slide } from 'svelte/transition';
	import ThemeToggle from '$lib/components/ThemeToggle.svelte';

	let industry = '';
	let vibe = 'Modern';
	let values = '';
	let step = 1;
	let loading = false;
	let suggestions = [];
	let showApp = false;
	let generatingLogoFor = null;
	let showUnlockModal = false;
	let isMenuOpen = false;

	const vibes = [
		{ id: 'Modern', emoji: '🚀', desc: 'Clean, sleek, and forward-thinking' },
		{ id: 'Luxury', emoji: '💎', desc: 'Elegant, premium, and exclusive' },
		{ id: 'Fun', emoji: '🎨', desc: 'Playful, energetic, and vibrant' },
		{ id: 'Minimalist', emoji: '✨', desc: 'Simple, essential, and pure' },
		{ id: 'Tech', emoji: '⚡', desc: 'Digital, innovative, and smart' },
		{ id: 'Classic', emoji: '🏛️', desc: 'Timeless, trustworthy, and established' },
		{ id: 'Professional', emoji: '💼', desc: 'Corporate, serious, and reliable' },
		{ id: 'Eco', emoji: '🌿', desc: 'Natural, organic, and sustainable' }
	];

	onMount(() => {
		if (!showApp) {
			initLandingAnimations();
		}
	});

	function initLandingAnimations() {
		// Placeholder for future brutalist animation hooks
	}

	function nextStep() {
		if (step < 3) step++;
	}

	function prevStep() {
		if (step > 1) step--;
	}

	async function submit() {
		if (!industry) return;
		loading = true;
		suggestions = [];

		try {
			const res = await fetch('/api/generate', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ industry, vibe, values })
			});

			if (!res.ok) {
				const errText = await res.text();
				throw new Error(`API Error: ${res.status} - ${errText}`);
			}

			const data = await res.json();
			suggestions = data.suggestions || [];
			step = 4;

			await generateAllLogos();
			loading = false;
		} catch (error) {
			console.error('Submission error:', error);
			alert('Something went wrong. Please try again.');
			loading = false;
		}
	}

	async function generateAllLogos() {
		const concurrency = 3;
		const queue = suggestions.map((_, index) => index);

		const worker = async () => {
			while (queue.length > 0) {
				const index = queue.shift();
				if (index !== undefined) {
					await generateHQLogo(index, suggestions[index].name);
				}
			}
		};

		const workers = Array(concurrency)
			.fill(null)
			.map(() => worker());
		await Promise.all(workers);
	}

	async function generateHQLogo(index, name) {
		const target = suggestions[index];
		if (!target) return;
		if (target.logoUrl || target.generating) return;

		target.generating = true;
		suggestions = [...suggestions];

		try {
			const res = await fetch(`/api/generate-logo?name=${encodeURIComponent(name)}&vibe=${encodeURIComponent(vibe)}`, {
				method: 'POST'
			});
			const data = await res.json();
			if (data.url) {
				target.logoUrl = data.url;
			}
		} catch (error) {
			console.error(`Failed to generate logo for ${name}:`, error);
		} finally {
			target.generating = false;
			suggestions = [...suggestions];
		}
	}

	function downloadLogo(item) {
		const name = item.name.replace(/\s+/g, '_').toLowerCase();

		if (item.logoUrl) {
			const link = document.createElement('a');
			link.href = item.logoUrl;
			link.download = `${name}_logo.png`;
			link.target = '_blank';
			link.click();
		} else {
			const svgString = item.svg;
			const canvas = document.createElement('canvas');
			const ctx = canvas.getContext('2d');
			const img = new Image();

			const parser = new DOMParser();
			const doc = parser.parseFromString(svgString, 'image/svg+xml');
			const svg = doc.querySelector('svg');

			const width = 1024;
			const height = 1024;

			svg.setAttribute('width', width);
			svg.setAttribute('height', height);

			const data = new XMLSerializer().serializeToString(svg);
			const blob = new Blob([data], { type: 'image/svg+xml;charset=utf-8' });
			const url = URL.createObjectURL(blob);

			img.onload = () => {
				canvas.width = width;
				canvas.height = height;
				ctx.fillStyle = 'white';
				ctx.fillRect(0, 0, width, height);
				ctx.drawImage(img, 0, 0, width, height);

				const pngUrl = canvas.toDataURL('image/png');
				const link = document.createElement('a');
				link.href = pngUrl;
				link.download = `${name}_logo.png`;
				link.click();
				URL.revokeObjectURL(url);
			};

			img.src = url;
		}
	}
</script>

<svelte:head>
	<title>Instant Brand Identities | AI Logo Generator</title>
	<meta
		name="description"
		content="Generate professional brand identities and logos instantly with AI. Free to start, no sign up required. Perfect for startups and entrepreneurs."
	/>
	<meta
		name="keywords"
		content="AI logo generator, brand identity, logo maker, startup branding, instant logos, free logo generator"
	/>
	<meta name="robots" content="index, follow" />
	<link rel="canonical" href="https://brandpixy.com/" />

	<meta property="og:type" content="website" />
	<meta property="og:url" content="https://brandpixy.com/" />
	<meta property="og:title" content="Instant Brand Identities | AI Logo Generator" />
	<meta property="og:description" content="Generate professional brand identities and logos instantly with AI. Free to start, no sign up required." />
	<meta property="og:image" content="https://brandpixy.com/logo.jpg" />

	<meta property="twitter:card" content="summary_large_image" />
	<meta property="twitter:url" content="https://brandpixy.com/" />
	<meta property="twitter:title" content="Instant Brand Identities | AI Logo Generator" />
	<meta property="twitter:description" content="Generate professional brand identities and logos instantly with AI. Free to start, no sign up required." />
	<meta property="twitter:image" content="https://brandpixy.com/logo.jpg" />

	<script type="application/ld+json">
	{
		"@context": "https://schema.org",
		"@type": "SoftwareApplication",
		"name": "Instant Brand Identities",
		"applicationCategory": "DesignApplication",
		"operatingSystem": "Web",
		"offers": {
			"@type": "Offer",
			"price": "0",
			"priceCurrency": "USD"
		},
		"description": "Generate professional brand identities and logos instantly with AI."
	}
	</script>
</svelte:head>

{#if !showApp}
	<div class="min-h-screen bg-slate-100 dark:bg-slate-900 text-slate-900 dark:text-slate-100 font-brut selection:bg-brand-purple selection:text-white">
		<div class="max-w-6xl mx-auto px-4 sm:px-6 py-10 flex flex-col gap-16">
			<nav class="sticky top-4 z-40" in:fade={{ duration: 200 }}>
				<div class="border-4 border-slate-900 dark:border-slate-100 bg-white dark:bg-slate-900 brut-shadow px-5 py-4 flex items-center justify-between gap-6">
					<a href="https://brandpixy.com/" class="flex items-center gap-4">
						<img src="/logo.jpg" alt="BrandPixy Logo" class="w-12 h-12 border-4 border-slate-900 dark:border-slate-100 object-cover" />
						<span class="text-xl font-black tracking-tight uppercase">BrandPixy</span>
					</a>
					<div class="hidden md:flex items-center gap-6 text-xs uppercase tracking-[0.35em]">
						<a href="#features" class="brut-link hover:text-brand-purple">Features</a>
						<button class="brut-link bg-transparent border-0 cursor-pointer hover:text-brand-purple">Pricing</button>
						<button class="brut-link bg-transparent border-0 cursor-pointer hover:text-brand-purple">About</button>
					</div>
					<div class="flex items-center gap-3">
						<ThemeToggle />
						<button class="hidden md:inline-flex brut-btn px-6 py-3 uppercase tracking-widest" on:click={() => showApp = true}>Launch Builder</button>
						<button
							class="md:hidden border-4 border-slate-900 dark:border-slate-100 px-3 py-2 brut-shadow bg-white dark:bg-slate-900"
							on:click={() => isMenuOpen = !isMenuOpen}
							aria-label="Menu"
						>
							<div class="w-6 h-5 flex flex-col justify-between">
								<span class={`block h-0.5 bg-current transition-transform ${isMenuOpen ? 'rotate-45 translate-y-1.5' : ''}`}></span>
								<span class={`block h-0.5 bg-current transition-opacity ${isMenuOpen ? 'opacity-0' : 'opacity-100'}`}></span>
								<span class={`block h-0.5 bg-current transition-transform ${isMenuOpen ? '-rotate-45 -translate-y-1.5' : ''}`}></span>
							</div>
						</button>
					</div>
				</div>
			</nav>

			{#if isMenuOpen}
				<div class="md:hidden border-4 border-slate-900 dark:border-slate-100 bg-white dark:bg-slate-900 brut-shadow px-5 py-6 flex flex-col gap-4 text-sm uppercase tracking-[0.25em]" in:slide={{ duration: 200, axis: 'y' }} out:slide={{ duration: 200, axis: 'y' }}>
					<a href="#features" class="brut-link" on:click={() => isMenuOpen = false}>Features</a>
					<button class="brut-link bg-transparent border-0 text-left" on:click={() => isMenuOpen = false}>Pricing</button>
					<button class="brut-link bg-transparent border-0 text-left" on:click={() => isMenuOpen = false}>About</button>
					<button class="brut-btn px-5 py-3" on:click={() => { isMenuOpen = false; showApp = true; }}>Launch Builder</button>
				</div>
			{/if}

			<section class="grid md:grid-cols-[1.4fr,0.6fr] gap-8 items-start" in:fade={{ duration: 300 }}>
				<div class="border-4 border-slate-900 dark:border-slate-100 bg-white dark:bg-slate-900 brut-shadow px-8 py-10 flex flex-col gap-6">
					<span class="text-xs uppercase tracking-[0.45em]">AI Brand Forge</span>
					<h1 class="text-4xl md:text-6xl font-black leading-tight uppercase">
						Stop shipping safe logos.
						<span class="inline-block bg-slate-900 dark:bg-brand-purple text-white px-3 -rotate-1">Start shipping brutal brands.</span>
					</h1>
					<p class="text-lg md:text-xl leading-relaxed max-w-2xl">
						BrandPixy tears down bland identities and rebuilds them with unapologetic geometry, loud typography, and expressive palettes. Three prompts. Twelve bold directions. Full ownership.
					</p>
					<div class="flex flex-wrap gap-4">
						<button class="brut-btn px-6 py-3 uppercase tracking-[0.35em]" on:click={() => showApp = true}>Start the Builder</button>
						<button class="border-4 border-slate-900 dark:border-slate-100 px-6 py-3 font-bold uppercase tracking-[0.3em] bg-slate-100 dark:bg-slate-900 brut-shadow hover:-translate-y-1" on:click={() => showApp = true}>See Flow</button>
					</div>
					<div class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs uppercase tracking-[0.3em]">
						<div class="border-4 border-slate-900 dark:border-slate-100 px-4 py-6 bg-slate-100 dark:bg-slate-900 brut-shadow">
							<span class="text-4xl font-black">30</span>
							<p>seconds to first draft</p>
						</div>
						<div class="border-4 border-slate-900 dark:border-slate-100 px-4 py-6 bg-slate-100 dark:bg-slate-900 brut-shadow">
							<span class="text-4xl font-black">∞</span>
							<p>variations unlocked</p>
						</div>
					</div>
				</div>
				<aside class="border-4 border-slate-900 dark:border-slate-100 bg-slate-100 dark:bg-slate-900 brut-shadow px-6 py-8 flex flex-col gap-6">
					<h2 class="text-xl font-black uppercase tracking-[0.25em]">How it works</h2>
					<ol class="space-y-4 text-sm uppercase tracking-[0.25em]">
						<li class="flex gap-3">
							<span class="border-4 border-slate-900 dark:border-slate-100 px-3 py-1">1</span>
							<p>Describe your industry and mood.</p>
						</li>
						<li class="flex gap-3">
							<span class="border-4 border-slate-900 dark:border-slate-100 px-3 py-1">2</span>
							<p>Preview wild naming + identity routes.</p>
						</li>
						<li class="flex gap-3">
							<span class="border-4 border-slate-900 dark:border-slate-100 px-3 py-1">3</span>
							<p>Export high-res logos with one click.</p>
						</li>
					</ol>
					<div class="border-4 border-slate-900 dark:border-slate-100 bg-white dark:bg-slate-900 px-4 py-5 brut-shadow text-xs uppercase tracking-[0.3em]">
						<span class="block font-black">Bonus</span>
						<p>Includes social kits + brand guides.</p>
					</div>
				</aside>
			</section>

			<section id="features" class="grid md:grid-cols-3 gap-6">
				<article class="brut-card space-y-3">
					<span class="text-3xl">⚡</span>
					<h3 class="text-2xl font-black uppercase">Speed-Run Strategy</h3>
					<p class="text-sm leading-relaxed">
						Generate brutalist-ready names, taglines, and visual references before your coffee cools. Every batch leans into loud personality.
					</p>
				</article>
				<article class="brut-card space-y-3">
					<span class="text-3xl">🧱</span>
					<h3 class="text-2xl font-black uppercase">Heavyweight Forms</h3>
					<p class="text-sm leading-relaxed">
						Hard edges, thick strokes, and unapologetic contrast by default. No gradients unless you say so.
					</p>
				</article>
				<article class="brut-card space-y-3">
					<span class="text-3xl">📦</span>
					<h3 class="text-2xl font-black uppercase">Delivery Included</h3>
					<p class="text-sm leading-relaxed">
						Export PNG + SVG instantly and unlock extended kits when you need pitch decks, cards, and socials.
					</p>
				</article>
			</section>

			<footer class="border-4 border-slate-900 dark:border-slate-100 bg-white dark:bg-slate-900 brut-shadow px-6 py-5 flex flex-col md:flex-row items-center justify-between gap-4 text-sm uppercase tracking-[0.2em]">
				<div class="flex items-center gap-4">
					<img src="/logo.jpg" alt="BrandPixy" class="w-10 h-10 border-4 border-slate-900 dark:border-slate-100" />
					<span class="font-black">BrandPixy</span>
				</div>
				<span>&copy; {new Date().getFullYear()} All noise, no filler.</span>
				<div class="flex gap-5">
					<button class="brut-link bg-transparent border-0 cursor-pointer">Privacy</button>
					<button class="brut-link bg-transparent border-0 cursor-pointer">Terms</button>
					<button class="brut-link bg-transparent border-0 cursor-pointer">Contact</button>
				</div>
			</footer>
		</div>
	</div>
{:else}
	<div class="min-h-screen bg-slate-100 dark:bg-slate-950 text-slate-900 dark:text-slate-100 font-brut flex flex-col">
		<div class="sticky top-6 z-40 px-4">
			<header class="max-w-4xl mx-auto border-4 border-slate-900 dark:border-slate-100 bg-white dark:bg-slate-900 brut-shadow px-5 py-4 flex items-center justify-between gap-4">
				<button
					class="flex items-center gap-2 font-black uppercase tracking-[0.35em] border-4 border-slate-900 dark:border-slate-100 px-4 py-2 bg-slate-100 dark:bg-slate-900 brut-shadow"
				on:click={() => { showApp = false; suggestions = []; industry = ''; step = 1; }}
				>
					<span>BrandPixy</span>
				</button>

				{#if step < 4}
					<div class="grid grid-cols-3 gap-3 text-xs uppercase tracking-[0.25em]">
						{#each [1, 2, 3] as idx}
							<div class={`border-4 border-slate-900 dark:border-slate-100 px-4 py-3 brut-shadow transition-all ${step >= idx ? 'bg-slate-900 text-white dark:bg-brand-purple dark:text-white' : 'bg-white dark:bg-slate-900'}`}>
								<span class="block text-[0.6rem]">Step {idx}</span>
								<span class="text-base font-black">
									{idx === 1 ? 'Industry' : idx === 2 ? 'Vibe' : 'Values'}
								</span>
							</div>
						{/each}
					</div>
				{:else}
					<button class="brut-btn px-5 py-2 text-xs tracking-[0.3em]" on:click={() => { step = 1; suggestions = []; loading = false; }}>
						Start Over
					</button>
				{/if}
			</header>
		</div>

		<main class="flex-1 w-full max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-24 space-y-12">
			{#if step < 4}
				<section class="space-y-10" in:fade>
					{#if step === 1}
						<div class="border-4 border-slate-900 dark:border-slate-100 bg-white dark:bg-slate-900 brut-shadow px-8 py-10 space-y-8" in:fly={{ x: 18, duration: 250 }}>
							<header class="space-y-2 text-center">
								<span class="inline-flex border-4 border-slate-900 dark:border-slate-100 px-4 py-1 text-xs uppercase tracking-[0.35em] brut-shadow">Step 1</span>
								<h2 class="text-4xl font-black uppercase">Name the arena</h2>
								<p class="text-sm md:text-base max-w-xl mx-auto">
									Drop the industry you want to dominate. We weaponize it into brand language.
								</p>
							</header>

							<div class="relative">
								<input
									type="text"
									bind:value={industry}
									placeholder="e.g. AI agency, coffee lab, fashion collective"
									class="w-full border-4 border-slate-900 dark:border-slate-100 bg-white dark:bg-slate-900 px-6 py-4 text-lg outline-none"
									on:keydown={(e) => e.key === 'Enter' && industry && nextStep()}
								/>
								<button class="brut-btn absolute right-2 top-2 bottom-2 px-6" disabled={!industry} on:click={nextStep}>Next</button>
							</div>

							<div class="flex flex-wrap gap-3 justify-center">
								{#each ['Tech', 'Food', 'Fashion', 'Health', 'Finance', 'Education'] as hint}
									<button class="border-4 border-slate-900 dark:border-slate-100 px-4 py-2 text-xs font-black uppercase tracking-[0.3em] bg-slate-100 dark:bg-slate-900 brut-shadow" on:click={() => { industry = hint; nextStep(); }}>
										{hint}
									</button>
								{/each}
							</div>
						</div>
					{/if}

					{#if step === 2}
						<div class="border-4 border-slate-900 dark:border-slate-100 bg-white dark:bg-slate-900 brut-shadow px-8 py-10 space-y-8" in:fly={{ x: 18, duration: 250 }} out:fade>
							<header class="space-y-2 text-center">
								<span class="inline-flex border-4 border-slate-900 dark:border-slate-100 px-4 py-1 text-xs uppercase tracking-[0.35em] brut-shadow">Step 2</span>
								<h2 class="text-4xl font-black uppercase">Select the energy</h2>
								<p class="text-sm md:text-base max-w-xl mx-auto">
									Tap a vibe. We translate it into type, palettes, and geometry.
								</p>
							</header>

							<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
								{#each vibes as v, idx}
									<button
										class={`border-4 border-slate-900 dark:border-slate-100 bg-white dark:bg-slate-900 px-4 py-5 text-left brut-shadow transition-transform ${vibe === v.id ? 'translate-y-[-6px] bg-slate-900 text-white dark:bg-brand-purple dark:text-white' : ''}`}
										on:click={() => { vibe = v.id; nextStep(); }}
										in:fly={{ y: 12, delay: idx * 40, duration: 200 }}
									>
										<div class="text-3xl mb-3">{v.emoji}</div>
										<div class="text-lg font-black uppercase">{v.id}</div>
										<p class="text-xs leading-relaxed mt-1 uppercase tracking-[0.2em]">{v.desc}</p>
									</button>
								{/each}
							</div>

							<div class="flex justify-between">
								<button class="border-4 border-slate-900 dark:border-slate-100 px-4 py-2 font-black uppercase tracking-[0.3em] bg-slate-100 dark:bg-slate-900 brut-shadow" on:click={prevStep}>Back</button>
							</div>
						</div>
					{/if}

					{#if step === 3}
						<div class="border-4 border-slate-900 dark:border-slate-100 bg-white dark:bg-slate-900 brut-shadow px-8 py-10 space-y-8" in:fly={{ x: 18, duration: 250 }} out:fade>
							<header class="space-y-2 text-center">
								<span class="inline-flex border-4 border-slate-900 dark:border-slate-100 px-4 py-1 text-xs uppercase tracking-[0.35em] brut-shadow">Step 3</span>
								<h2 class="text-4xl font-black uppercase">Load the values</h2>
								<p class="text-sm md:text-base max-w-xl mx-auto">
									Optional keywords help us steer composition and story.
								</p>
							</header>

							<input
								type="text"
								bind:value={values}
								placeholder="e.g. sustainability, velocity, trust"
								class="w-full border-4 border-slate-900 dark:border-slate-100 bg-white dark:bg-slate-900 px-6 py-4 text-lg outline-none"
								on:keydown={(e) => e.key === 'Enter' && submit()}
							/>

							<div class="flex justify-between items-center">
								<button class="border-4 border-slate-900 dark:border-slate-100 px-4 py-2 font-black uppercase tracking-[0.3em] bg-slate-100 dark:bg-slate-900 brut-shadow" on:click={prevStep}>Back</button>
								<button class={`brut-btn px-6 py-3 uppercase tracking-[0.35em] flex items-center gap-3 ${loading ? 'opacity-70' : ''}`} on:click={submit} disabled={loading}>
									{#if loading}
										<span class="w-4 h-4 border-4 border-white border-b-transparent animate-spin"></span>
										<span>Generating</span>
									{:else}
										<span>Generate</span>
									{/if}
								</button>
							</div>
						</div>
					{/if}
				</section>
			{:else}
				<section class="space-y-10" in:fade>
					<div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
						<div>
							<h2 class="text-3xl md:text-4xl font-black uppercase">Brutal directions ready</h2>
							<p class="text-sm uppercase tracking-[0.25em]">{industry} • {vibe} vibe</p>
						</div>
						<button class="border-4 border-slate-900 dark:border-slate-100 px-5 py-2 font-black uppercase tracking-[0.3em] bg-slate-100 dark:bg-slate-900 brut-shadow" on:click={() => { step = 1; suggestions = []; loading = false; }}>
							Restart Flow
						</button>
					</div>

					{#if loading}
						<div class="border-4 border-slate-900 dark:border-slate-100 bg-white dark:bg-slate-900 brut-shadow px-8 py-16 text-center flex flex-col items-center gap-6">
							<div class="w-20 h-20 border-4 border-slate-900 dark:border-slate-100 flex items-center justify-center">
								<span class="text-4xl animate-pulse">✨</span>
							</div>
							<p class="text-lg font-black uppercase tracking-[0.3em]">Brewing the loud stuff...</p>
							<p class="text-xs uppercase tracking-[0.2em]">This takes around 15 seconds.</p>
						</div>
					{:else}
						<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
							{#each suggestions as s, i}
								<article class="border-4 border-slate-900 dark:border-slate-100 bg-white dark:bg-slate-900 brut-shadow flex flex-col" in:fade={{ delay: i * 50, duration: 250 }}>
									<div class="px-6 py-6 flex-1 flex flex-col items-center text-center gap-4">
										<div class="w-full aspect-square border-4 border-slate-900 dark:border-slate-100 flex items-center justify-center bg-slate-100 dark:bg-slate-900">
											{#if s.logoUrl}
												<img src={s.logoUrl} alt={`${s.name} logo`} class="w-4/5 h-4/5 object-contain" />
											{:else}
												<div class="w-4/5 h-4/5">{@html s.svg}</div>
											{/if}
										</div>
										<h3 class="text-2xl font-black uppercase tracking-tight">{s.name}</h3>
										<p class="text-xs uppercase tracking-[0.25em] leading-relaxed">{s.tagline}</p>
									</div>
									<div class="px-6 py-4 border-t-4 border-slate-900 dark:border-slate-100 bg-slate-100 dark:bg-slate-900 grid gap-3">
										<button class="brut-btn w-full py-2 text-xs tracking-[0.3em]" on:click={() => downloadLogo(s)}>Download</button>
										{#if s.generating}
											<p class="text-xs text-center uppercase tracking-[0.25em]">✨ Rendering HQ logo...</p>
										{/if}
									</div>
								</article>
							{/each}

							<button type="button" class="border-4 border-slate-900 dark:border-slate-100 bg-slate-900 text-white dark:bg-brand-purple brut-shadow flex flex-col items-start justify-between px-6 py-6 text-left" on:click={() => showUnlockModal = true}>
								<div class="space-y-3">
									<span class="text-xs uppercase tracking-[0.35em]">Upgrade</span>
									<h3 class="text-2xl font-black uppercase">Unlock full brand kit</h3>
									<p class="text-xs uppercase tracking-[0.25em] leading-relaxed text-white/80">Social kits, brand book, mockups, and more. One-click export.</p>
								</div>
								<span class="mt-6 inline-flex border-4 border-white px-4 py-2 font-black uppercase tracking-[0.35em] bg-white text-slate-900">Open Modal</span>
							</button>
						</div>
					{/if}
				</section>
			{/if}
		</main>
	</div>
{/if}

{#if showUnlockModal}
	<div class="fixed inset-0 z-[100] flex items-center justify-center p-4" in:fade={{ duration: 150 }}>
		<button type="button" class="absolute inset-0 bg-slate-900/70" on:click={() => showUnlockModal = false} aria-label="Close modal"></button>
		<div class="relative border-4 border-slate-900 dark:border-slate-100 bg-white dark:bg-slate-900 brut-shadow w-full max-w-xl p-8 space-y-6" in:fly={{ y: 18, duration: 200 }}>
			<div class="flex items-start justify-between">
				<div>
					<h2 class="text-3xl font-black uppercase">Full Brand Kit</h2>
					<p class="text-xs uppercase tracking-[0.3em]">Everything styled for launch.</p>
				</div>
				<button class="border-4 border-slate-900 dark:border-slate-100 px-3 py-1 font-black" on:click={() => showUnlockModal = false}>Close</button>
			</div>
			<ul class="space-y-4 text-sm uppercase tracking-[0.2em]">
				<li class="border-4 border-slate-900 dark:border-slate-100 px-4 py-3 bg-slate-100 dark:bg-slate-900">Social media kit + templates</li>
				<li class="border-4 border-slate-900 dark:border-slate-100 px-4 py-3 bg-slate-100 dark:bg-slate-900">Brand guidelines PDF</li>
				<li class="border-4 border-slate-900 dark:border-slate-100 px-4 py-3 bg-slate-100 dark:bg-slate-900">Business card + deck exports</li>
			</ul>
			<button class="brut-btn w-full py-3 text-xs tracking-[0.35em]">Get it for $29</button>
		</div>
	</div>
{/if}
