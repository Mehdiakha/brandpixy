<script>
	import { onMount } from 'svelte';
	import { fade, fly, slide } from 'svelte/transition';
	import gsap from 'gsap';
	import { ScrollTrigger } from 'gsap/dist/ScrollTrigger';

	let industry = '';
	let vibe = 'Modern';
	let values = '';
	let step = 1;
	let loading = false;
	let suggestions = [];
	let showApp = false;
	let generatingLogoFor = null;
	let showUnlockModal = false;

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
		gsap.registerPlugin(ScrollTrigger);
		if (!showApp) {
			initLandingAnimations();
		}
	});

	function initLandingAnimations() {
		const tl = gsap.timeline();
		tl.from('.landing-content', { y: 50, opacity: 0, duration: 1, ease: 'power3.out' });
		
		// Cube animation: Drop from top with bounce
		gsap.fromTo('.cube-container', 
			{ y: -500, opacity: 0 },
			{ y: 0, opacity: 1, duration: 1.5, ease: 'bounce.out', delay: 0.5 }
		);

		// Interactive Mouse Movement
		const handleMouseMove = (e) => {
			const x = (e.clientX / window.innerWidth - 0.5) * 2;
			const y = (e.clientY / window.innerHeight - 0.5) * 2;

			gsap.to('.cube', {
				rotationY: x * 50 + 25, // Subtle rotation following mouse
				rotationX: -y * 50 - 25,
				duration: 1,
				ease: 'power2.out'
			});
		};

		window.addEventListener('mousemove', handleMouseMove);

		// Cleanup function (though onMount runs once, good practice)
		return () => window.removeEventListener('mousemove', handleMouseMove);
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
			console.error("Generation failed:", e);
			alert(`Error: ${e.message}. Check console for details.`);
		} finally {
			loading = false;
		}
	}

	async function generateAllLogos() {
		// Process in chunks of 4 to ensure faster completion while respecting rate limits
		const chunk = 4;
		for (let i = 0; i < suggestions.length; i += chunk) {
			const batch = suggestions.slice(i, i + chunk).map((s, idx) => {
				// Calculate actual index in the main array
				const realIndex = i + idx;
				return generateHQLogo(realIndex, s.name);
			});
			await Promise.all(batch);
		}
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

{#if !showApp}
	<div class="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex flex-col relative overflow-hidden">
		<!-- Background Blobs -->
		<div class="absolute top-20 left-20 w-72 h-72 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob"></div>
		<div class="absolute top-20 right-20 w-72 h-72 bg-indigo-300 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob animation-delay-2000"></div>
		<div class="absolute -bottom-8 left-1/2 w-72 h-72 bg-pink-300 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob animation-delay-4000"></div>

		<!-- Landing Navbar -->
		<div class="fixed top-6 left-0 right-0 z-50 flex justify-center px-4">
			<nav class="bg-white/10 backdrop-blur-md border border-white/20 shadow-lg rounded-full px-6 py-3 flex items-center justify-between gap-8 max-w-5xl w-full transition-all duration-300 hover:bg-white/20">
				<div class="flex items-center gap-3 cursor-pointer">
					<img src="/logo.jpg" alt="BrandPixy" class="w-8 h-8 rounded-lg shadow-sm" />
					<span class="text-lg font-bold text-slate-900 tracking-tight">BrandPixy</span>
				</div>
				<div class="hidden md:flex items-center gap-6 text-sm font-medium text-slate-600">
					<a href="#features" class="hover:text-indigo-600 transition-colors">Features</a>
					<a href="#" class="hover:text-indigo-600 transition-colors">Pricing</a>
					<a href="#" class="hover:text-indigo-600 transition-colors">About</a>
				</div>
				<button 
					class="px-5 py-2 bg-slate-900 text-white text-sm font-bold rounded-full hover:bg-slate-800 transition-colors shadow-md"
					on:click={() => showApp = true}
				>
					Get Started
				</button>
			</nav>
		</div>

		<!-- Hero Section -->
		<div class="flex-1 flex flex-col items-center justify-center p-6 text-center landing-content relative z-10 mt-20">
			<div class="mb-16 flex justify-center perspective-container cube-container">
				<div class="cube">
					<div class="face front">
						<img src="/logo.jpg" alt="BrandPixy Logo" class="w-full h-full object-cover rounded-xl" />
					</div>
					<div class="face back">
						<img src="/logo.jpg" alt="BrandPixy Logo" class="w-full h-full object-cover rounded-xl" />
					</div>
					<div class="face right">
						<img src="/logo.jpg" alt="BrandPixy Logo" class="w-full h-full object-cover rounded-xl" />
					</div>
					<div class="face left">
						<img src="/logo.jpg" alt="BrandPixy Logo" class="w-full h-full object-cover rounded-xl" />
					</div>
					<div class="face top"></div>
					<div class="face bottom"></div>
				</div>
			</div>
			<h1 class="text-6xl md:text-8xl font-black text-slate-900 mb-8 tracking-tight leading-tight">
				Brand<span class="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600">Pixy</span>
			</h1>
			<p class="text-xl md:text-2xl text-slate-600 max-w-2xl mx-auto mb-12 leading-relaxed font-light">
				Craft your entire brand identity in seconds.
			</p>
			<button 
				class="group relative px-8 py-4 bg-slate-900 text-white text-lg font-bold rounded-full shadow-xl hover:shadow-2xl hover:-translate-y-1 transition-all duration-300 overflow-hidden cursor-pointer"
				on:click={() => showApp = true}
			>
				<span class="relative z-10 flex items-center gap-2">
					Start Generating
					<svg class="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6"/></svg>
				</span>
				<div class="absolute inset-0 bg-gradient-to-r from-indigo-600 to-purple-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
			</button>
		</div>

		<!-- Features Section -->
		<div id="features" class="py-24 bg-white/30 backdrop-blur-xl border-t border-white/20 relative z-10">
			<div class="max-w-7xl mx-auto px-6">
				<h2 class="text-4xl font-bold text-center text-slate-900 mb-16">Why BrandPixy?</h2>
				<div class="grid md:grid-cols-3 gap-8 md:gap-12">
					<div class="text-center p-8 rounded-3xl bg-white/60 backdrop-blur-md border border-white/40 shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all">
						<div class="text-5xl mb-6">⚡</div>
						<h3 class="text-xl font-bold mb-3 text-slate-900">Instant Generation</h3>
						<p class="text-slate-600 leading-relaxed">Get dozens of unique brand names and logos in seconds.</p>
					</div>
					<div class="text-center p-8 rounded-3xl bg-white/60 backdrop-blur-md border border-white/40 shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all">
						<div class="text-5xl mb-6">🎨</div>
						<h3 class="text-xl font-bold mb-3 text-slate-900">Tailored Vibes</h3>
						<p class="text-slate-600 leading-relaxed">Choose from Modern, Luxury, Tech, and more styles.</p>
					</div>
					<div class="text-center p-8 rounded-3xl bg-white/60 backdrop-blur-md border border-white/40 shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all">
						<div class="text-5xl mb-6">💎</div>
						<h3 class="text-xl font-bold mb-3 text-slate-900">Production Ready</h3>
						<p class="text-slate-600 leading-relaxed">Download high-quality PNG logos instantly.</p>
					</div>
				</div>
			</div>
		</div>

		<!-- Footer -->
		<footer class="bg-slate-900 text-slate-400 py-12 relative z-10">
			<div class="max-w-7xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-6">
				<div class="flex items-center gap-3">
					<img src="/logo.jpg" alt="BrandPixy" class="w-8 h-8 rounded-lg opacity-80" />
					<span class="text-white font-bold text-xl">BrandPixy</span>
				</div>
				<div class="text-sm">
					&copy; {new Date().getFullYear()} BrandPixy. All rights reserved.
				</div>
				<div class="flex gap-6">
					<a href="#" class="hover:text-white transition-colors">Privacy</a>
					<a href="#" class="hover:text-white transition-colors">Terms</a>
					<a href="#" class="hover:text-white transition-colors">Contact</a>
				</div>
			</div>
		</footer>
	</div>
{:else}
	<div class="min-h-screen bg-slate-50 font-sans text-slate-900 flex flex-col">
		<!-- Floating Glassmorphism Navbar -->
		<div class="fixed top-6 left-0 right-0 z-50 flex justify-center px-4">
			<header class="bg-white/70 backdrop-blur-xl border border-white/20 shadow-lg rounded-full px-6 py-3 flex items-center justify-between gap-8 max-w-2xl w-full transition-all duration-300 hover:shadow-xl hover:bg-white/80">
				<div class="flex items-center gap-3 cursor-pointer group" on:click={() => { showApp = false; suggestions = []; industry = ''; step = 1; }}>
					<img src="/logo.jpg" alt="BrandPixy" class="w-8 h-8 rounded-lg shadow-sm group-hover:scale-105 transition-transform" />
					<span class="text-lg font-bold text-slate-900 tracking-tight">BrandPixy</span>
				</div>
				
				{#if step < 4}
					<div class="hidden sm:flex items-center gap-2 text-xs font-medium text-slate-500 bg-slate-100/50 px-3 py-1.5 rounded-full">
						<span class="{step >= 1 ? 'text-indigo-600' : ''}">1. Industry</span>
						<span class="text-slate-300">/</span>
						<span class="{step >= 2 ? 'text-indigo-600' : ''}">2. Vibe</span>
						<span class="text-slate-300">/</span>
						<span class="{step >= 3 ? 'text-indigo-600' : ''}">3. Values</span>
					</div>
				{:else}
					<button 
						class="text-sm font-medium text-slate-600 hover:text-indigo-600 transition-colors"
						on:click={() => { step = 1; suggestions = []; }}
					>
						Start Over
					</button>
				{/if}
			</header>
		</div>

		<main class="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 w-full">
			
			{#if step < 4}
				<div class="max-w-2xl mx-auto">
					<!-- Progress Bar -->
					<div class="h-1 w-full bg-slate-100 rounded-full mb-12 overflow-hidden">
						<div class="h-full bg-indigo-600 transition-all duration-500 ease-out" style="width: {(step / 3) * 100}%"></div>
					</div>

					<!-- Step 1: Industry -->
					{#if step === 1}
						<div in:fly={{ x: 20, duration: 300, delay: 100 }} out:fade class="space-y-6">
							<div class="text-center mb-10">
								<h2 class="text-3xl font-bold text-slate-900 mb-3">What's your industry?</h2>
								<p class="text-slate-500">Tell us what kind of business you're building.</p>
							</div>
							
							<div class="relative">
								<input 
									type="text" 
									bind:value={industry}
									placeholder="e.g. Coffee Shop, AI Startup, Fashion Brand..."
									class="w-full px-6 py-4 text-lg rounded-2xl border-2 border-slate-200 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10 outline-none transition-all shadow-sm"
									on:keydown={(e) => e.key === 'Enter' && industry && nextStep()}
									autofocus
								/>
								<button 
									class="absolute right-3 top-3 bottom-3 px-6 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-700 disabled:opacity-50 disabled:hover:bg-indigo-600 transition-colors"
									disabled={!industry}
									on:click={nextStep}
								>
									Next
								</button>
							</div>

							<div class="flex flex-wrap gap-2 justify-center mt-8">
								{#each ['Tech', 'Food', 'Fashion', 'Health', 'Finance', 'Education'] as hint}
									<button 
										class="px-4 py-2 bg-white border border-slate-200 rounded-full text-sm font-medium text-slate-600 hover:border-indigo-300 hover:text-indigo-600 hover:bg-indigo-50 transition-all"
										on:click={() => { industry = hint; nextStep(); }}
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
							<div class="text-center mb-10">
								<h2 class="text-3xl font-bold text-slate-900 mb-3">Choose your vibe</h2>
								<p class="text-slate-500">How should your brand feel to customers?</p>
							</div>

							<div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
								{#each vibes as v}
									<button 
										class="p-4 rounded-2xl border-2 text-left transition-all duration-200 hover:-translate-y-1 {vibe === v.id ? 'border-indigo-600 bg-indigo-50 ring-2 ring-indigo-600/20' : 'border-slate-200 bg-white hover:border-indigo-300 hover:shadow-md'}"
										on:click={() => { vibe = v.id; nextStep(); }}
									>
										<div class="text-3xl mb-3">{v.emoji}</div>
										<div class="font-bold text-slate-900 mb-1">{v.id}</div>
										<div class="text-xs text-slate-500 leading-tight">{v.desc}</div>
									</button>
								{/each}
							</div>

							<div class="flex justify-between mt-8">
								<button class="text-slate-400 hover:text-slate-600 font-medium px-4 py-2" on:click={prevStep}>Back</button>
							</div>
						</div>
					{/if}

					<!-- Step 3: Values -->
					{#if step === 3}
						<div in:fly={{ x: 20, duration: 300, delay: 100 }} out:fade class="space-y-6">
							<div class="text-center mb-10">
								<h2 class="text-3xl font-bold text-slate-900 mb-3">Core Values</h2>
								<p class="text-slate-500">What does your brand stand for? (Optional)</p>
							</div>

							<div class="relative">
								<input 
									type="text" 
									bind:value={values}
									placeholder="e.g. Sustainability, Speed, Trust..."
									class="w-full px-6 py-4 text-lg rounded-2xl border-2 border-slate-200 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10 outline-none transition-all shadow-sm"
									on:keydown={(e) => e.key === 'Enter' && submit()}
									autofocus
								/>
							</div>

							<div class="flex justify-between items-center mt-8">
								<button class="text-slate-400 hover:text-slate-600 font-medium px-4 py-2" on:click={prevStep}>Back</button>
								<button 
									class="px-8 py-4 bg-indigo-600 text-white text-lg font-bold rounded-xl shadow-lg hover:bg-indigo-700 hover:shadow-xl hover:-translate-y-1 transition-all flex items-center gap-2"
									on:click={submit}
									disabled={loading}
								>
									{#if loading}
										<svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
											<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
											<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
										</svg>
										Generating...
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
					<div class="flex flex-col md:flex-row justify-between items-center mb-8 gap-4">
						<div>
							<h2 class="text-2xl font-bold text-slate-900">Your Brand Identity Options</h2>
							<p class="text-slate-500">Generated for <span class="font-medium text-indigo-600">{industry}</span> • {vibe} Vibe</p>
						</div>
						<button 
							class="px-6 py-2 bg-white border border-slate-200 text-slate-600 font-medium rounded-xl hover:bg-slate-50 transition-colors cursor-pointer"
							on:click={() => { step = 1; suggestions = []; }}
						>
							Start Over
						</button>
					</div>

					{#if loading}
						<div class="flex flex-col items-center justify-center py-20">
							<div class="w-16 h-16 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin mb-6"></div>
							<p class="text-lg text-slate-600 font-medium">Brewing some magic...</p>
						</div>
					{:else}
						<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
							{#each suggestions as s, i}
								<div class="bg-white rounded-2xl border border-slate-200 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-300 overflow-hidden group flex flex-col" in:fade={{ delay: i * 50, duration: 300 }}>
									<!-- Logo Area -->
									<div class="p-8 flex-1 flex flex-col items-center text-center relative bg-slate-50/50 group-hover:bg-white transition-colors">
										<div class="w-full aspect-square flex items-center justify-center mb-4 relative">
											{#if s.logoUrl}
												<img src={s.logoUrl} alt="{s.name} logo" class="w-full h-full object-contain drop-shadow-md" in:fade />
											{:else}
												<div class="w-full h-full transform transition-transform duration-500 group-hover:scale-110 drop-shadow-sm flex items-center justify-center">
													{@html s.svg}
												</div>
											{/if}
										</div>
										<h3 class="text-2xl font-black text-slate-900 mb-2 tracking-tight">{s.name}</h3>
										<p class="text-sm text-slate-500 leading-relaxed font-medium">{s.tagline}</p>
									</div>

									<!-- Actions -->
									<div class="p-4 border-t border-slate-100 bg-slate-50/80 grid grid-cols-1 gap-3">
										<button 
											class="py-2.5 px-4 bg-white border border-slate-200 text-slate-700 font-semibold rounded-xl text-sm hover:bg-slate-50 hover:text-indigo-600 hover:border-indigo-200 transition-all flex items-center justify-center gap-2 shadow-sm cursor-pointer"
											on:click={() => downloadLogo(s)}
										>
											<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
											Download Logo
										</button>
										{#if s.generating}
											<div class="text-xs text-center text-indigo-600 font-medium animate-pulse">
												Generating AI Logo...
											</div>
										{/if}
									</div>
								</div>
							{/each}

							<!-- Unlock Full Brand Identity Card -->
							<div class="bg-gradient-to-br from-indigo-600 to-purple-700 rounded-2xl shadow-xl hover:shadow-2xl hover:-translate-y-1 transition-all duration-300 overflow-hidden group flex flex-col items-center justify-center text-center p-6 text-white cursor-pointer" 
								in:fade={{ delay: suggestions.length * 50, duration: 300 }}
								on:click={() => showUnlockModal = true}
							>
								<div class="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center mb-4 backdrop-blur-sm group-hover:scale-110 transition-transform">
									<svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>
								</div>
								<h3 class="text-xl font-bold mb-2">Unlock Full Brand</h3>
								<p class="text-indigo-100 mb-4 text-xs">Get social media kits, business cards, and brand guidelines.</p>
								<button class="px-4 py-2 bg-white text-indigo-600 text-sm font-bold rounded-lg hover:bg-indigo-50 transition-colors w-full">
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
		<div class="absolute inset-0 bg-slate-900/60 backdrop-blur-sm" on:click={() => showUnlockModal = false}></div>
		
		<!-- Modal Content -->
		<div class="bg-white rounded-3xl shadow-2xl w-full max-w-lg relative z-10 overflow-hidden" in:fly={{ y: 20, duration: 300 }}>
			<div class="bg-gradient-to-r from-indigo-600 to-purple-600 p-8 text-white text-center relative overflow-hidden">
				<div class="absolute top-0 left-0 w-full h-full bg-[url('/grid.svg')] opacity-20"></div>
				<button class="absolute top-4 right-4 text-white/70 hover:text-white transition-colors" on:click={() => showUnlockModal = false}>
					<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
				</button>
				<div class="w-16 h-16 bg-white/20 rounded-2xl flex items-center justify-center mx-auto mb-4 backdrop-blur-md">
					<span class="text-3xl">💎</span>
				</div>
				<h2 class="text-3xl font-bold mb-2">Unlock Full Brand Kit</h2>
				<p class="text-indigo-100">Take your brand to the next level.</p>
			</div>
			
			<div class="p-8">
				<div class="space-y-4 mb-8">
					<div class="flex items-center gap-4 p-4 rounded-xl bg-slate-50 border border-slate-100">
						<div class="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-600">
							<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
						</div>
						<div>
							<h4 class="font-bold text-slate-900">Social Media Kit</h4>
							<p class="text-sm text-slate-500">Profile pics, covers, and post templates.</p>
						</div>
					</div>
					<div class="flex items-center gap-4 p-4 rounded-xl bg-slate-50 border border-slate-100">
						<div class="w-10 h-10 rounded-full bg-purple-100 flex items-center justify-center text-purple-600">
							<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 114 0v1m-4 0c0 .884-.896 1.75-2.167 2.5h4.333c-1.27-.75-2.167-1.616-2.167-2.5z"/></svg>
						</div>
						<div>
							<h4 class="font-bold text-slate-900">Business Cards</h4>
							<p class="text-sm text-slate-500">Print-ready designs for your team.</p>
						</div>
					</div>
					<div class="flex items-center gap-4 p-4 rounded-xl bg-slate-50 border border-slate-100">
						<div class="w-10 h-10 rounded-full bg-pink-100 flex items-center justify-center text-pink-600">
							<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
						</div>
						<div>
							<h4 class="font-bold text-slate-900">Brand Guidelines</h4>
							<p class="text-sm text-slate-500">Fonts, colors, and usage rules.</p>
						</div>
					</div>
				</div>
				
				<button class="w-full py-4 bg-slate-900 text-white font-bold rounded-xl hover:bg-slate-800 transition-all shadow-lg hover:shadow-xl hover:-translate-y-1">
					Get Full Access - $29
				</button>
				<p class="text-center text-xs text-slate-400 mt-4">One-time payment. Lifetime access.</p>
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
	.animate-blob {
		animation: blob 7s infinite;
	}
	.animation-delay-2000 {
		animation-delay: 2s;
	}
	.animation-delay-4000 {
		animation-delay: 4s;
	}

	/* Cube Animation Styles */
	.perspective-container {
		perspective: 1000px;
		width: 120px;
		height: 120px;
	}

	.cube {
		width: 100%;
		height: 100%;
		position: relative;
		transform-style: preserve-3d;
		transform: rotateX(-25deg) rotateY(25deg);
	}

	.face {
		position: absolute;
		width: 120px;
		height: 120px;
		background: rgba(255, 255, 255, 0.95);
		border: 1px solid rgba(255, 255, 255, 0.2);
		border-radius: 1rem;
		display: flex;
		align-items: center;
		justify-content: center;
		box-shadow: 0 0 30px rgba(0,0,0,0.15);
		backface-visibility: hidden;
		overflow: hidden;
	}

	.face img {
		width: 100%;
		height: 100%;
		object-fit: cover;
	}

	.front  { transform: rotateY(0deg) translateZ(60px); }
	.back   { transform: rotateY(180deg) translateZ(60px); }
	.right  { transform: rotateY(90deg) translateZ(60px); }
	.left   { transform: rotateY(-90deg) translateZ(60px); }
	.top    { transform: rotateX(90deg) translateZ(60px); background: #e0e7ff; }
	.bottom { transform: rotateX(-90deg) translateZ(60px); background: #e0e7ff; }
</style>
