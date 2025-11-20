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
			const data = await res.json();
			suggestions = data.suggestions || [];
			step = 4; // Move to results
		} catch (e) {
			console.error(e);
		} finally {
			loading = false;
		}
	}

	async function generateHQLogo(index, name) {
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
			
			// Use aspect ratio from viewBox (0 0 140 84) -> 1.66
			const width = 1400; 
			const height = 840;
			
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
	<div class="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex flex-col items-center justify-center p-6 text-center landing-content relative overflow-hidden">
		<!-- Background Blobs -->
		<div class="absolute top-20 left-20 w-72 h-72 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob"></div>
		<div class="absolute top-20 right-20 w-72 h-72 bg-indigo-300 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob animation-delay-2000"></div>
		<div class="absolute -bottom-8 left-1/2 w-72 h-72 bg-pink-300 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob animation-delay-4000"></div>

		<div class="relative z-10 max-w-4xl mx-auto">
			<div class="mb-8 flex justify-center">
				<img src="/logo.jpg" alt="BrandPixy Logo" class="w-24 h-24 rounded-2xl shadow-2xl rotate-3 hover:rotate-0 transition-transform duration-500" />
			</div>
			<h1 class="text-6xl md:text-8xl font-black text-slate-900 mb-8 tracking-tight leading-tight">
				Brand<span class="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600">Pixy</span>
			</h1>
			<p class="text-xl md:text-2xl text-slate-600 max-w-2xl mx-auto mb-12 leading-relaxed font-light">
				Craft your entire brand identity in seconds. <br>
				<span class="font-medium text-slate-800">Names. Taglines. Logos.</span>
			</p>
			<button 
				class="group relative px-8 py-4 bg-slate-900 text-white text-lg font-bold rounded-full shadow-xl hover:shadow-2xl hover:-translate-y-1 transition-all duration-300 overflow-hidden"
				on:click={() => showApp = true}
			>
				<span class="relative z-10 flex items-center gap-2">
					Start Generating
					<svg class="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6"/></svg>
				</span>
				<div class="absolute inset-0 bg-gradient-to-r from-indigo-600 to-purple-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
			</button>
		</div>
	</div>
{:else}
	<div class="min-h-screen bg-slate-50 font-sans text-slate-900 flex flex-col">
		<!-- Header -->
		<header class="bg-white/80 backdrop-blur-md border-b border-slate-200 sticky top-0 z-50">
			<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
				<div class="flex items-center gap-3 cursor-pointer" on:click={() => { showApp = false; suggestions = []; industry = ''; step = 1; }}>
					<img src="/logo.jpg" alt="BrandPixy" class="w-8 h-8 rounded-lg shadow-sm" />
					<span class="text-xl font-bold text-slate-900 tracking-tight">BrandPixy</span>
				</div>
				{#if step < 4}
					<div class="flex items-center gap-2 text-sm font-medium text-slate-500">
						<span class="{step >= 1 ? 'text-indigo-600' : ''}">1. Industry</span>
						<span class="text-slate-300">/</span>
						<span class="{step >= 2 ? 'text-indigo-600' : ''}">2. Vibe</span>
						<span class="text-slate-300">/</span>
						<span class="{step >= 3 ? 'text-indigo-600' : ''}">3. Values</span>
					</div>
				{/if}
			</div>
		</header>

		<main class="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 w-full">
			
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
							class="px-6 py-2 bg-white border border-slate-200 text-slate-600 font-medium rounded-xl hover:bg-slate-50 transition-colors"
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
										<div class="w-full aspect-[4/3] flex items-center justify-center mb-4 relative">
											{#if s.logoUrl}
												<img src={s.logoUrl} alt="{s.name} logo" class="w-full h-full object-contain drop-shadow-md" in:fade />
											{:else}
												<div class="transform scale-110 transition-transform duration-500 group-hover:scale-125 drop-shadow-sm">
													{@html s.svg}
												</div>
											{/if}
										</div>
										<h3 class="text-2xl font-black text-slate-900 mb-2 tracking-tight">{s.name}</h3>
										<p class="text-sm text-slate-500 leading-relaxed font-medium">{s.tagline}</p>
									</div>

									<!-- Actions -->
									<div class="p-4 border-t border-slate-100 bg-slate-50/80 grid grid-cols-2 gap-3">
										<button 
											class="py-2.5 px-4 bg-white border border-slate-200 text-slate-700 font-semibold rounded-xl text-sm hover:bg-slate-50 hover:text-indigo-600 hover:border-indigo-200 transition-all flex items-center justify-center gap-2 shadow-sm"
											on:click={() => downloadLogo(s)}
										>
											<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
											Download
										</button>
										<button 
											class="py-2.5 px-4 bg-indigo-600 text-white font-semibold rounded-xl text-sm hover:bg-indigo-700 shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-2 disabled:opacity-70 disabled:cursor-not-allowed"
											on:click={() => generateHQLogo(i, s.name)}
											disabled={generatingLogoFor === i || s.logoUrl}
										>
											{#if generatingLogoFor === i}
												<svg class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
											{:else if s.logoUrl}
												<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
											{:else}
												<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
											{/if}
											{s.logoUrl ? 'Done' : 'HQ Icon'}
										</button>
									</div>
								</div>
							{/each}
						</div>
					{/if}
				</div>
			{/if}
		</main>
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
</style>


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
