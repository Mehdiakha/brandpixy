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
		// Simple fade-in animation on mount
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
		console.log("Submitting generation request...", { industry, vibe, values });
		
		try {
			const res = await fetch('/api/generate', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ industry, vibe, values })
			});
			
			console.log("Response status:", res.status);
			
			if (!res.ok) {
				const errText = await res.text();
				console.error("API Error Body:", errText);
				throw new Error(`API Error: ${res.status} - ${errText}`);
			}

			const data = await res.json();
			console.log("Received data:", data);
			suggestions = data.suggestions || [];
			step = 4; // Move to results

			// Automatically generate HQ logos for all suggestions
			// We do this in batches to avoid overwhelming the browser/server
			generateAllLogos();

		} catch (e) {
			console.error("Submission error:", e);
			alert("Something went wrong. Please try again.");
			loading = false;
		}
	}

	async function generateAllLogos() {
		// Use a concurrency pool to generate logos efficiently
		// This prevents blocking the queue if one request is slow, and keeps 3 requests active at all times
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

		// Start workers
		const workers = Array(concurrency).fill(null).map(() => worker());
		await Promise.all(workers);
	}

	async function generateHQLogo(index, name) {
		// If already generated or generating, skip
		if (suggestions[index].logoUrl || suggestions[index].generating) return;

		suggestions[index].generating = true;
		suggestions = [...suggestions]; // Trigger reactivity

		try {
			const res = await fetch(`/api/generate-logo?name=${encodeURIComponent(name)}&vibe=${encodeURIComponent(vibe)}`, {
				method: 'POST'
			});
			const data = await res.json();
			if (data.url) {
				suggestions[index].logoUrl = data.url;
			}
		} catch (e) {
			console.error(`Failed to generate logo for ${name}:`, e);
		} finally {
			suggestions[index].generating = false;
			suggestions = [...suggestions]; // Trigger reactivity
		}
	}

	function downloadLogo(item) {
		const name = item.name.replace(/\s+/g, '_').toLowerCase();
		
		if (item.logoUrl) {
			// Download DALL-E Image
			const link = document.createElement('a');
			link.href = item.logoUrl;
			link.download = `${name}_logo.png`;
			link.target = '_blank';
			link.click();
		} else {
			// Download SVG as PNG
			const svgString = item.svg;
			const canvas = document.createElement('canvas');
			const ctx = canvas.getContext('2d');
			const img = new Image();
			
			// Parse SVG size
			const parser = new DOMParser();
			const doc = parser.parseFromString(svgString, 'image/svg+xml');
			const svg = doc.querySelector('svg');
			
			// Use aspect ratio from viewBox (0 0 200 200) -> 1:1
			const width = 1024; 
			const height = 1024;
			
			svg.setAttribute('width', width);
			svg.setAttribute('height', height);
			
			const data = (new XMLSerializer()).serializeToString(svg);
			const blob = new Blob([data], { type: 'image/svg+xml;charset=utf-8' });
			const url = URL.createObjectURL(blob);
			
			img.onload = () => {
				canvas.width = width;
				canvas.height = height;
				// Draw white background explicitly just in case
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
	<meta name="description" content="Generate professional brand identities and logos instantly with AI. Free to start, no sign up required. Perfect for startups and entrepreneurs." />
	<meta name="keywords" content="AI logo generator, brand identity, logo maker, startup branding, instant logos, free logo generator" />
	<meta name="robots" content="index, follow" />
	<link rel="canonical" href="https://brandpixy.com/" />

	<!-- Open Graph / Facebook -->
	<meta property="og:type" content="website" />
	<meta property="og:url" content="https://brandpixy.com/" />
	<meta property="og:title" content="Instant Brand Identities | AI Logo Generator" />
	<meta property="og:description" content="Generate professional brand identities and logos instantly with AI. Free to start, no sign up required." />
	<meta property="og:image" content="https://brandpixy.com/logo.jpg" />

	<!-- Twitter -->
	<meta property="twitter:card" content="summary_large_image" />
	<meta property="twitter:url" content="https://brandpixy.com/" />
	<meta property="twitter:title" content="Instant Brand Identities | AI Logo Generator" />
	<meta property="twitter:description" content="Generate professional brand identities and logos instantly with AI. Free to start, no sign up required." />
	<meta property="twitter:image" content="https://brandpixy.com/logo.jpg" />

	<!-- Schema.org JSON-LD -->
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
	<div class="min-h-screen bg-gradient-to-b from-white dark:from-slate-950 via-slate-50 dark:via-slate-900 to-white dark:to-slate-950 text-slate-900 dark:text-slate-50 overflow-hidden font-sans selection:bg-brand-purple selection:text-white">
		<!-- Navbar -->
		<nav class="fixed w-full z-50 top-0 left-0 border-b border-slate-200/40 dark:border-slate-700/40 bg-white/70 dark:bg-slate-950/70 backdrop-blur-md transition-colors duration-300">
			<div class="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
				<div class="flex items-center gap-3">
					<a href="https://brandpixy.com/" class="flex items-center gap-2">
						<img src="/logo.jpg" alt="BrandPixy Logo" class="w-12 h-12 rounded-full hover:scale-110 transition-transform duration-300" />
						<span class="text-xl font-bold tracking-tight text-slate-900 dark:text-white">BrandPixy</span>
					</a>
				</div>
				
				<!-- Desktop Menu -->
				<div class="hidden md:flex items-center gap-6 text-sm font-medium text-slate-600 dark:text-slate-300">
					<a href="#features" class="hover:text-brand-purple dark:hover:text-brand-purple transition-colors">Features</a>
					<button class="hover:text-brand-purple dark:hover:text-brand-purple transition-colors bg-transparent border-0 cursor-pointer">Pricing</button>
					<button class="hover:text-brand-purple dark:hover:text-brand-purple transition-colors bg-transparent border-0 cursor-pointer">About</button>
				</div>

				<div class="flex items-center gap-4">
					<ThemeToggle />
					<button 
						class="hidden md:block px-5 py-2 bg-gradient-to-r from-brand-purple to-brand-blue text-white text-sm font-bold rounded-full hover:shadow-lg hover:shadow-brand-purple/50 hover:-translate-y-1 transition-all shadow-md whitespace-nowrap"
						onclick={() => showApp = true}
					>
						Get Started
					</button>

					<!-- Mobile Hamburger -->
					<button 
						class="md:hidden p-2 text-slate-900 dark:text-white hover:bg-slate-100 dark:hover:bg-slate-800 rounded-full transition-colors"
						onclick={() => isMenuOpen = !isMenuOpen}
						aria-label="Menu"
					>
						<div class="w-6 h-5 relative flex flex-col justify-between">
							<span class="w-full h-0.5 bg-current rounded-full transition-all duration-300 {isMenuOpen ? 'rotate-45 translate-y-2' : ''}"></span>
							<span class="w-full h-0.5 bg-current rounded-full transition-all duration-300 {isMenuOpen ? 'opacity-0' : ''}"></span>
							<span class="w-full h-0.5 bg-current rounded-full transition-all duration-300 {isMenuOpen ? '-rotate-45 -translate-y-2.5' : ''}"></span>
						</div>
					</button>
				</div>
			</div>
		</nav>

			<!-- Mobile Menu Overlay -->
			{#if isMenuOpen}
				<div 
					class="absolute top-full left-4 right-4 mt-2 p-4 bg-white/90 dark:bg-slate-800/90 backdrop-blur-xl border border-slate-200/40 dark:border-slate-700/40 rounded-3xl shadow-xl flex flex-col gap-4 md:hidden origin-top z-40"
					in:slide={{ duration: 300, axis: 'y' }}
					out:slide={{ duration: 200, axis: 'y' }}
				>
					<a href="#features" class="p-3 text-slate-700 dark:text-slate-200 font-medium hover:bg-slate-100 dark:hover:bg-slate-700 rounded-xl transition-colors" onclick={() => isMenuOpen = false}>Features</a>
					<button class="p-3 text-slate-700 dark:text-slate-200 font-medium hover:bg-slate-100 dark:hover:bg-slate-700 rounded-xl transition-colors text-left w-full" onclick={() => isMenuOpen = false}>Pricing</button>
					<button class="p-3 text-slate-700 dark:text-slate-200 font-medium hover:bg-slate-100 dark:hover:bg-slate-700 rounded-xl transition-colors text-left w-full" onclick={() => isMenuOpen = false}>About</button>
					<button 
						class="w-full py-3 bg-gradient-to-r from-brand-purple to-brand-blue text-white font-bold rounded-xl shadow-md hover:shadow-lg transition-all"
						onclick={() => { isMenuOpen = false; showApp = true; }}
					>
						Get Started
					</button>
				</div>
			{/if}

		<!-- Hero Section -->
		<div class="flex-1 flex flex-col items-center justify-center p-6 text-center landing-content relative z-10 mt-32" in:fade={{ duration: 600 }}>
			<h1 class="text-6xl md:text-7xl font-black text-slate-900 dark:text-white mb-8 tracking-tight leading-tight">
				Instant <span class="text-transparent bg-clip-text bg-gradient-to-r from-brand-purple via-brand-blue to-brand-cyan">Brand Identities</span>
			</h1>
			<p class="text-xl md:text-2xl text-slate-600 dark:text-slate-300 max-w-2xl mx-auto mb-12 leading-relaxed font-light">
				Create stunning logos and brand names in seconds. Powered by AI, owned by you.
			</p>
			<button 
				class="group relative px-8 py-4 bg-gradient-to-r from-brand-purple to-brand-blue text-white text-lg font-bold rounded-full shadow-lg hover:shadow-xl hover:shadow-brand-purple/50 hover:-translate-y-1 transition-all duration-300 overflow-hidden cursor-pointer"
				onclick={() => showApp = true}
			>
				<span class="relative z-10 flex items-center gap-2">
					Start Creating
					<svg class="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6"/></svg>
				</span>
			</button>
		</div>

		<!-- Features Section -->
		<div id="features" class="py-24 bg-white dark:bg-slate-900 border-t border-slate-200/40 dark:border-slate-700/40 relative z-10">
			<div class="max-w-7xl mx-auto px-6">
				<h2 class="text-4xl font-bold text-center text-slate-900 dark:text-white mb-16">Why BrandPixy?</h2>
				<div class="grid md:grid-cols-3 gap-8 md:gap-12">
					<!-- Feature 1 -->
					<div class="text-center p-8 rounded-3xl bg-gradient-to-br from-brand-purple/10 dark:from-brand-purple/20 to-transparent border border-brand-purple/20 dark:border-brand-purple/30 shadow-sm hover:shadow-md hover:-translate-y-1 transition-all">
						<div class="text-5xl mb-6">⚡</div>
						<h3 class="text-xl font-bold mb-3 text-slate-900 dark:text-white">Lightning Fast</h3>
						<p class="text-slate-600 dark:text-slate-300 leading-relaxed">Get dozens of unique logos and brand names in seconds.</p>
					</div>
					<!-- Feature 2 -->
					<div class="text-center p-8 rounded-3xl bg-gradient-to-br from-brand-blue/10 dark:from-brand-blue/20 to-transparent border border-brand-blue/20 dark:border-brand-blue/30 shadow-sm hover:shadow-md hover:-translate-y-1 transition-all">
						<div class="text-5xl mb-6">🎨</div>
						<h3 class="text-xl font-bold mb-3 text-slate-900 dark:text-white">Fully Customizable</h3>
						<p class="text-slate-600 dark:text-slate-300 leading-relaxed">Choose from Modern, Luxury, Tech styles and more.</p>
					</div>
					<!-- Feature 3 -->
					<div class="text-center p-8 rounded-3xl bg-gradient-to-br from-brand-cyan/10 dark:from-brand-cyan/20 to-transparent border border-brand-cyan/20 dark:border-brand-cyan/30 shadow-sm hover:shadow-md hover:-translate-y-1 transition-all">
						<div class="text-5xl mb-6">💎</div>
						<h3 class="text-xl font-bold mb-3 text-slate-900 dark:text-white">Production Ready</h3>
						<p class="text-slate-600 dark:text-slate-300 leading-relaxed">Download high-quality PNG and SVG files instantly.</p>
					</div>
				</div>
			</div>
		</div>

		<!-- Footer -->
		<footer class="bg-slate-50 dark:bg-slate-900 text-slate-600 dark:text-slate-300 py-12 border-t border-slate-200/40 dark:border-slate-700/40 relative z-10">
			<div class="max-w-7xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-6">
				<div class="flex items-center gap-3">
					<img src="/logo.jpg" alt="BrandPixy" class="w-10 h-10 rounded-lg" />
					<span class="text-slate-900 dark:text-white font-bold text-xl">BrandPixy</span>
				</div>
				<div class="text-sm">
					&copy; {new Date().getFullYear()} BrandPixy. All rights reserved.
				</div>
				<div class="flex gap-6">
					<button class="hover:text-slate-900 dark:hover:text-white transition-colors bg-transparent border-0 cursor-pointer">Privacy</button>
					<button class="hover:text-slate-900 dark:hover:text-white transition-colors bg-transparent border-0 cursor-pointer">Terms</button>
					<button class="hover:text-slate-900 dark:hover:text-white transition-colors bg-transparent border-0 cursor-pointer">Contact</button>
				</div>
			</div>
		</footer>
	</div>
{:else}
	<div class="min-h-screen bg-gradient-to-b from-white dark:from-slate-950 via-slate-50 dark:via-slate-900 to-white dark:to-slate-950 font-sans text-slate-900 dark:text-slate-50 flex flex-col transition-colors duration-300">
		<!-- Floating Glassmorphism Navbar -->
		<div class="fixed top-6 left-0 right-0 z-50 flex justify-center px-4">
			<header class="bg-white/80 dark:bg-slate-800/80 backdrop-blur-xl border border-slate-200/50 dark:border-slate-700/50 shadow-md dark:shadow-xl rounded-full px-4 py-2 md:px-6 md:py-3 flex items-center justify-between gap-4 md:gap-8 max-w-2xl w-full transition-all duration-300 hover:shadow-lg dark:hover:shadow-xl hover:bg-white dark:hover:bg-slate-800">
				<div class="flex items-center gap-3 cursor-pointer group" onclick={() => { showApp = false; suggestions = []; industry = ''; step = 1; }} onkeydown={(e) => e.key === 'Enter' && (showApp = false)} role="button" tabindex="0">
					<span class="text-lg font-bold text-slate-900 dark:text-white tracking-tight">BrandPixy</span>
				</div>
				
				{#if step < 4}
					<div class="hidden sm:flex items-center gap-2 text-xs font-medium text-slate-500 dark:text-slate-400 bg-slate-100 dark:bg-slate-700 px-3 py-1.5 rounded-full">
						<span class="{step >= 1 ? 'text-brand-purple dark:text-brand-sky' : ''}">1. Industry</span>
						<span class="text-slate-300 dark:text-slate-600">/</span>
						<span class="{step >= 2 ? 'text-brand-purple dark:text-brand-sky' : ''}">2. Vibe</span>
						<span class="text-slate-300 dark:text-slate-600">/</span>
						<span class="{step >= 3 ? 'text-brand-purple dark:text-brand-sky' : ''}">3. Values</span>
					</div>
				{:else}
					<button 
						class="text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-brand-purple dark:hover:text-brand-cyan transition-colors"
						onclick={() => { step = 1; suggestions = []; }}
					>
						Start Over
					</button>
				{/if}
			</header>
		</div>

		<main class="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 w-full">
			
			{#if step < 4}
				<div class="max-w-2xl mx-auto">
					<!-- Enhanced Progress Bar with Indicator -->
					<div class="mb-12">
						<div class="h-1.5 w-full bg-slate-200 dark:bg-slate-700 rounded-full mb-4 overflow-hidden">
							<div class="h-full bg-gradient-to-r from-brand-purple to-brand-blue transition-all duration-500 ease-out shadow-lg shadow-brand-purple/50" style="width: {(step / 3) * 100}%"></div>
						</div>
						<div class="flex justify-between text-xs font-semibold text-slate-600 dark:text-slate-400">
							<span class="{step >= 1 ? 'text-brand-purple dark:text-brand-sky' : ''}">Step {Math.min(step, 3)} of 3</span>
							<span>{Math.round((step / 3) * 100)}%</span>
						</div>
					</div>

					<!-- Step 1: Industry -->
					{#if step === 1}
						<div in:fly={{ x: 20, duration: 300, delay: 100 }} out:fade class="space-y-6">
							<div class="text-center mb-12">
								<div class="inline-block mb-4 px-4 py-2 bg-brand-purple/10 dark:bg-brand-purple/20 border border-brand-purple/30 rounded-full">
									<span class="text-xs font-bold text-brand-purple dark:text-brand-sky uppercase tracking-widest">Step 1</span>
								</div>
								<h2 class="text-4xl font-bold text-slate-900 dark:text-white mb-3 animate-fade-in-up">What's your industry?</h2>
								<p class="text-slate-500 dark:text-slate-400 text-lg">Tell us what kind of business you're building.</p>
							</div>
							
							<div class="relative group">
								<input 
									type="text" 
									bind:value={industry}
									placeholder="e.g. Coffee Shop, AI Startup, Fashion Brand..."
									class="w-full px-6 py-4 text-lg rounded-2xl border-2 border-slate-200 dark:border-slate-600 dark:bg-slate-800 dark:text-white focus:border-brand-purple dark:focus:border-brand-cyan focus:ring-4 focus:ring-brand-purple/10 dark:focus:ring-brand-purple/20 outline-none transition-all shadow-sm hover:border-slate-300 dark:hover:border-slate-500"
									onkeydown={(e) => e.key === 'Enter' && industry && nextStep()}
								/>
								<button 
									class="absolute right-3 top-3 bottom-3 px-6 bg-gradient-to-r from-brand-purple to-brand-blue text-white rounded-xl font-medium hover:shadow-lg hover:shadow-brand-purple/50 hover:-translate-y-0.5 disabled:opacity-50 disabled:hover:bg-gradient-to-r disabled:hover:from-brand-purple disabled:hover:to-brand-blue disabled:hover:shadow-none disabled:hover:translate-y-0 transition-all"
									disabled={!industry}
									onclick={nextStep}
								>
									Next
								</button>
							</div>

							<div class="flex flex-wrap gap-2 justify-center mt-10">
								{#each ['Tech', 'Food', 'Fashion', 'Health', 'Finance', 'Education'] as hint}
									<button 
										class="px-4 py-2.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-full text-sm font-medium text-slate-600 dark:text-slate-300 hover:border-brand-purple dark:hover:border-brand-cyan hover:text-brand-purple dark:hover:text-brand-cyan hover:bg-brand-purple/5 dark:hover:bg-brand-purple/10 transition-all hover:shadow-md"
										onclick={() => { industry = hint; nextStep(); }}
									>
										{hint}
									</button>
								{/each}
							</div>
						</div>
					{/if}

					<!-- Step 2: Vibe -->
					{#if step === 2}
						<div in:fly={{ x: 20, duration: 300, delay: 100 }} out:fade class="space-y-6">
							<div class="text-center mb-12">
								<div class="inline-block mb-4 px-4 py-2 bg-brand-blue/10 dark:bg-brand-blue/20 border border-brand-blue/30 rounded-full">
									<span class="text-xs font-bold text-brand-blue dark:text-brand-cyan uppercase tracking-widest">Step 2</span>
								</div>
								<h2 class="text-4xl font-bold text-slate-900 dark:text-white mb-3 animate-fade-in-up">Choose your vibe</h2>
								<p class="text-slate-500 dark:text-slate-400 text-lg">How should your brand feel to customers?</p>
							</div>

							<div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
								{#each vibes as v, idx}
									<button 
										class="p-4 rounded-2xl border-2 text-left transition-all duration-200 hover:-translate-y-1 group {vibe === v.id ? 'border-brand-purple dark:border-brand-cyan bg-brand-purple/10 dark:bg-brand-purple/20 ring-2 ring-brand-purple/20 dark:ring-brand-cyan/20 shadow-lg shadow-brand-purple/30' : 'border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 hover:border-brand-purple dark:hover:border-brand-cyan hover:shadow-md dark:hover:shadow-lg dark:hover:shadow-slate-700'}"
										onclick={() => { vibe = v.id; nextStep(); }}
										in:fly={{ x: -20, delay: idx * 50, duration: 300 }}
									>
										<div class="text-4xl mb-3 group-hover:scale-125 transition-transform">{v.emoji}</div>
										<div class="font-bold text-slate-900 dark:text-white mb-1">{v.id}</div>
										<div class="text-xs text-slate-500 dark:text-slate-400 leading-tight">{v.desc}</div>
									</button>
								{/each}
							</div>

							<div class="flex justify-between mt-8">
								<button class="text-slate-400 dark:text-slate-500 hover:text-slate-600 dark:hover:text-slate-300 font-medium px-4 py-2 transition-colors" onclick={prevStep}>← Back</button>
							</div>
						</div>
					{/if}

					<!-- Step 3: Values -->
					{#if step === 3}
						<div in:fly={{ x: 20, duration: 300, delay: 100 }} out:fade class="space-y-6">
							<div class="text-center mb-12">
								<div class="inline-block mb-4 px-4 py-2 bg-brand-cyan/10 dark:bg-brand-cyan/20 border border-brand-cyan/30 rounded-full">
									<span class="text-xs font-bold text-brand-cyan dark:text-brand-sky uppercase tracking-widest">Step 3</span>
								</div>
								<h2 class="text-4xl font-bold text-slate-900 dark:text-white mb-3 animate-fade-in-up">Core Values</h2>
								<p class="text-slate-500 dark:text-slate-400 text-lg">What does your brand stand for? (Optional)</p>
							</div>

							<div class="relative group">
								<input 
									type="text" 
									bind:value={values}
									placeholder="e.g. Sustainability, Speed, Trust..."
									class="w-full px-6 py-4 text-lg rounded-2xl border-2 border-slate-200 dark:border-slate-600 dark:bg-slate-800 dark:text-white focus:border-brand-cyan dark:focus:border-brand-sky focus:ring-4 focus:ring-brand-cyan/10 dark:focus:ring-brand-cyan/20 outline-none transition-all shadow-sm hover:border-slate-300 dark:hover:border-slate-500"
									onkeydown={(e) => e.key === 'Enter' && submit()}
								/>
							</div>

							<div class="flex justify-between items-center mt-10">
								<button class="text-slate-400 dark:text-slate-500 hover:text-slate-600 dark:hover:text-slate-300 font-medium px-4 py-2 transition-colors" onclick={prevStep}>← Back</button>
								<button 
									class="px-8 py-4 bg-gradient-to-r from-brand-purple to-brand-blue text-white text-lg font-bold rounded-xl shadow-lg hover:shadow-xl hover:shadow-brand-purple/50 hover:-translate-y-1 transition-all flex items-center gap-2 disabled:opacity-50 disabled:hover:shadow-lg disabled:hover:translate-y-0"
									onclick={submit}
									disabled={loading}
								>
									{#if loading}
										<svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
											<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
											<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
										</svg>
										Generating Brand...
									{:else}
										Generate Brand
										<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
									{/if}
								</button>
							</div>
						</div>
					{/if}
				</div>
			{:else}
				<!-- Results Section -->
				<div in:fade={{ duration: 500 }}>
					<div class="flex flex-col md:flex-row justify-between items-center mb-12 gap-4">
						<div>
							<h2 class="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mb-2">Your Brand Identity Options</h2>
							<p class="text-slate-500 dark:text-slate-400">Generated for <span class="font-bold text-brand-purple dark:text-brand-cyan">{industry}</span> • {vibe} Vibe</p>
						</div>
						<button 
							class="px-6 py-2.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 font-medium rounded-xl hover:bg-slate-50 dark:hover:bg-slate-700 hover:border-brand-purple dark:hover:border-brand-cyan transition-all cursor-pointer shadow-sm"
							onclick={() => { step = 1; suggestions = []; }}
						>
							← Start Over
						</button>
					</div>

					{#if loading}
						<div class="flex flex-col items-center justify-center py-32">
							<div class="relative w-20 h-20 mb-8">
								<div class="absolute inset-0 bg-gradient-to-r from-brand-purple to-brand-blue rounded-full animate-spin blur-sm"></div>
								<div class="absolute inset-2 bg-white dark:bg-slate-950 rounded-full flex items-center justify-center">
									<div class="text-3xl animate-bounce">✨</div>
								</div>
							</div>
							<p class="text-xl text-slate-600 dark:text-slate-300 font-semibold">Brewing some magic...</p>
							<p class="text-sm text-slate-500 dark:text-slate-400 mt-2">This usually takes 10-20 seconds</p>
						</div>
					{:else}
						<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
							{#each suggestions as s, i}
								<div class="group bg-white dark:bg-slate-800 rounded-3xl border-2 border-slate-200 dark:border-slate-700 shadow-sm hover:shadow-2xl hover:shadow-brand-purple/20 dark:hover:shadow-brand-purple/30 hover:-translate-y-2 transition-all duration-300 overflow-hidden flex flex-col" in:fade={{ delay: i * 50, duration: 400 }}>
									<!-- Logo Area -->
									<div class="p-8 flex-1 flex flex-col items-center text-center relative bg-gradient-to-b from-slate-50/50 dark:from-slate-700/30 to-transparent group-hover:from-brand-purple/5 dark:group-hover:from-brand-purple/10 transition-colors">
										<div class="w-full aspect-square flex items-center justify-center mb-6 relative">
											{#if s.logoUrl}
												<img src={s.logoUrl} alt="{s.name} logo" class="w-4/5 h-4/5 object-contain drop-shadow-lg group-hover:drop-shadow-xl group-hover:scale-110 transition-all duration-300" in:fade />
											{:else}
												<div class="w-4/5 h-4/5 transform transition-transform duration-500 group-hover:scale-125 drop-shadow-sm flex items-center justify-center">
													{@html s.svg}
												</div>
											{/if}
										</div>
										<h3 class="text-2xl font-black text-slate-900 dark:text-white mb-2 tracking-tight leading-tight">{s.name}</h3>
										<p class="text-sm text-slate-600 dark:text-slate-300 leading-relaxed font-medium line-clamp-2">{s.tagline}</p>
									</div>

									<!-- Actions -->
									<div class="p-4 border-t border-slate-100 dark:border-slate-700 bg-slate-50/80 dark:bg-slate-700/50 grid grid-cols-1 gap-3">
										<button 
											class="py-2.5 px-4 bg-gradient-to-r from-brand-purple to-brand-blue text-white font-semibold rounded-xl text-sm hover:shadow-lg hover:shadow-brand-purple/50 hover:-translate-y-0.5 transition-all flex items-center justify-center gap-2 shadow-md cursor-pointer"
											onclick={() => downloadLogo(s)}
										>
											<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
											Download
										</button>
										{#if s.generating}
											<div class="text-xs text-center text-brand-purple dark:text-brand-cyan font-medium animate-pulse">
												✨ Generating AI Logo...
											</div>
										{/if}
									</div>
								</div>
							{/each}

							<!-- Unlock Full Brand Identity Card -->
							<div class="bg-gradient-to-br from-brand-purple to-brand-blue rounded-3xl shadow-xl hover:shadow-2xl hover:shadow-brand-purple/40 hover:-translate-y-2 transition-all duration-300 overflow-hidden group flex flex-col items-center justify-center text-center p-6 text-white cursor-pointer" 
								in:fade={{ delay: suggestions.length * 50, duration: 400 }}
								onclick={() => showUnlockModal = true}
								onkeydown={(e) => e.key === 'Enter' && (showUnlockModal = true)}
								role="button"
								tabindex="0"
							>
								<div class="w-14 h-14 bg-white/20 rounded-2xl flex items-center justify-center mb-4 backdrop-blur-md group-hover:scale-110 transition-transform">
									<svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>
								</div>
								<h3 class="text-xl font-bold mb-2">Unlock Full Brand</h3>
								<p class="text-white/80 mb-5 text-sm leading-relaxed">Get social media kits, business cards, and brand guidelines instantly.</p>
								<button class="px-5 py-2.5 bg-white text-brand-purple text-sm font-bold rounded-lg hover:bg-slate-100 transition-all hover:shadow-lg w-full transition-transform duration-200 group-hover:scale-105">
									Unlock Now
								</button>
							</div>
						</div>
					{/if}
				</div>
			{/if}
		</main>
	</div>
{/if}

{#if showUnlockModal}
	<div class="fixed inset-0 z-[100] flex items-center justify-center p-4" in:fade={{ duration: 200 }}>
		<!-- Backdrop -->
		<div class="absolute inset-0 bg-slate-900/60 dark:bg-slate-900/80 backdrop-blur-sm" onclick={() => showUnlockModal = false} onkeydown={(e) => e.key === 'Escape' && (showUnlockModal = false)} role="button" tabindex="0" aria-label="Close modal"></div>
		
		<!-- Modal Content -->
		<div class="bg-white dark:bg-slate-800 rounded-3xl shadow-2xl dark:shadow-2xl w-full max-w-lg relative z-10 overflow-hidden" in:fly={{ y: 20, duration: 300 }}>
			<div class="bg-gradient-to-r from-brand-purple to-brand-blue p-8 text-white text-center relative overflow-hidden">
				<div class="absolute top-0 left-0 w-full h-full bg-[url('/grid.svg')] opacity-10"></div>
				<button class="absolute top-4 right-4 text-white/70 hover:text-white hover:bg-white/10 rounded-full p-2 transition-colors" onclick={() => showUnlockModal = false} aria-label="Close">
					<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
				</button>
				<div class="w-16 h-16 bg-white/20 rounded-2xl flex items-center justify-center mx-auto mb-4 backdrop-blur-md">
					<span class="text-3xl">💎</span>
				</div>
				<h2 class="text-3xl font-bold mb-2">Unlock Full Brand Kit</h2>
				<p class="text-brand-sky">Take your brand to the next level.</p>
			</div>
			
			<div class="p-8">
				<div class="space-y-4 mb-8">
					<div class="flex items-center gap-4 p-4 rounded-xl bg-brand-purple/5 dark:bg-brand-purple/10 border border-brand-purple/20 dark:border-brand-purple/30">
						<div class="w-10 h-10 rounded-full bg-brand-purple/20 flex items-center justify-center text-brand-purple">
							<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
						</div>
						<div>
							<h4 class="font-bold text-slate-900 dark:text-white">Social Media Kit</h4>
							<p class="text-sm text-slate-500 dark:text-slate-400">Profile pics, covers, and post templates.</p>
						</div>
					</div>
					<div class="flex items-center gap-4 p-4 rounded-xl bg-brand-blue/5 dark:bg-brand-blue/10 border border-brand-blue/20 dark:border-brand-blue/30">
						<div class="w-10 h-10 rounded-full bg-brand-blue/20 flex items-center justify-center text-brand-blue">
							<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 114 0v1m-4 0c0 .884-.896 1.75-2.167 2.5h4.333c-1.27-.75-2.167-1.616-2.167-2.5z"/></svg>
						</div>
						<div>
							<h4 class="font-bold text-slate-900 dark:text-white">Business Cards</h4>
							<p class="text-sm text-slate-500 dark:text-slate-400">Print-ready designs for your team.</p>
						</div>
					</div>
					<div class="flex items-center gap-4 p-4 rounded-xl bg-brand-cyan/5 dark:bg-brand-cyan/10 border border-brand-cyan/20 dark:border-brand-cyan/30">
						<div class="w-10 h-10 rounded-full bg-brand-cyan/20 flex items-center justify-center text-brand-cyan">
							<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
						</div>
						<div>
							<h4 class="font-bold text-slate-900 dark:text-white">Brand Guidelines</h4>
							<p class="text-sm text-slate-500 dark:text-slate-400">Fonts, colors, and usage rules.</p>
						</div>
					</div>
				</div>
				
				<button class="w-full py-4 bg-gradient-to-r from-brand-purple to-brand-blue text-white font-bold rounded-xl hover:shadow-lg hover:shadow-brand-purple/50 transition-all shadow-md hover:-translate-y-0.5">
					Get Full Access - $29
				</button>
				<p class="text-center text-xs text-slate-500 dark:text-slate-400 mt-4">One-time payment. Lifetime access.</p>
			</div>
		</div>
	</div>
{/if}

<style>
	@keyframes blob {
		0% { transform: translate(0px, 0px) scale(1); }
		33% { transform: translate(30px, -50px) scale(1.1); }
		66% { transform: translate(-20px, 20px) scale(0.9); }
		100% { transform: translate(0px, 0px) scale(1); }
	}
</style>
