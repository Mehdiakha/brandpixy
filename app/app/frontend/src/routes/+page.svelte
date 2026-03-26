<script>
	import { onMount } from "svelte";
	import { fade, fly, slide } from "svelte/transition";

	let industry = "";
	let vibe = "Modern";
	let values = "";
	let step = 1;
	let loading = false;
	let suggestions = [];
	let showApp = false;
	let generatingLogoFor = null;
	let showUnlockModal = false;
	let isMenuOpen = false;

	const vibes = [
		{
			id: "Modern",
			emoji: "🚀",
			desc: "Clean, sleek, and forward-thinking",
		},
		{ id: "Luxury", emoji: "💎", desc: "Elegant, premium, and exclusive" },
		{ id: "Fun", emoji: "🎨", desc: "Playful, energetic, and vibrant" },
		{ id: "Minimalist", emoji: "✨", desc: "Simple, essential, and pure" },
		{ id: "Tech", emoji: "⚡", desc: "Digital, innovative, and smart" },
		{
			id: "Classic",
			emoji: "🏛️",
			desc: "Timeless, trustworthy, and established",
		},
		{
			id: "Professional",
			emoji: "💼",
			desc: "Corporate, serious, and reliable",
		},
		{ id: "Eco", emoji: "🌿", desc: "Natural, organic, and sustainable" },
	];

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
			const response = await fetch("/api/generate", {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify({
					industry,
					vibe,
					values,
				}),
			});

			if (!response.ok) {
				const errData = await response.json().catch(() => ({}));
				throw new Error(errData.detail || "Failed to generate brands");
			}

			const data = await response.json();
			suggestions = data.suggestions;

			step = 4;
			loading = false;
			
			// Automatically generate HQ logos for all suggestions
			generateAllLogos();
		} catch (error) {
			console.error("Submission error details:", error);
			alert(`Error: ${error.message}. Check console for details.`);
			loading = false;
		}
	}

	function downloadLogo(item) {
		// Existing download logic
		alert(`Downloading ${item.name}...`);
	}

	async function generateAllLogos() {
		// Use a concurrency pool to generate logos efficiently
		// Reduced concurrency to 2 to avoid rate limiting
		const concurrency = 2;
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
</script>

<svelte:head>
	<title>BrandPixy | AI Brand Identity Generator</title>
	<meta
		name="description"
		content="Generate professional brand identities and logos instantly with AI."
	/>
</svelte:head>

{#if !showApp}
	<div class="min-h-screen flex flex-col">
		<!-- Minimal Navigation -->
		<nav class="border-b border-surface-200 bg-white sticky top-0 z-50">
			<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
				<div class="flex justify-between items-center h-16">
					<div class="flex items-center gap-2">
						<svg class="w-8 h-8 text-brand-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
						</svg>
						<span class="text-lg font-bold text-surface-900">BrandPixy</span>
					</div>
					<button
						class="px-6 py-2 bg-brand-600 text-white rounded-lg hover:bg-brand-700 transition-colors font-medium"
						onclick={() => (showApp = true)}
					>
						Launch Builder
					</button>
				</div>
			</div>
		</nav>

		<!-- Hero Section -->
		<main class="flex-grow">
			<div class="pt-20 pb-32">
				<div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
					<h1 class="text-5xl md:text-6xl font-bold tracking-tight mb-6">
						Create your brand identity instantly
					</h1>

					<p class="text-lg text-surface-600 max-w-2xl mx-auto mb-10">
						Generate unique logos and brand concepts powered by AI. 
						Get professional results in seconds.
					</p>

					<button
						class="px-8 py-3 bg-brand-600 text-white rounded-lg hover:bg-brand-700 transition-colors font-medium text-lg"
						onclick={() => (showApp = true)}
					>
						Start Creating
					</button>

					<!-- Stats -->
					<div class="grid grid-cols-3 gap-8 mt-24 border-t border-surface-200 pt-16">
						<div>
							<div class="text-3xl font-bold text-surface-900">10k+</div>
							<div class="text-sm text-surface-500 mt-2">Brands Created</div>
						</div>
						<div>
							<div class="text-3xl font-bold text-surface-900">&lt; 1min</div>
							<div class="text-sm text-surface-500 mt-2">Generation Time</div>
						</div>
						<div>
							<div class="text-3xl font-bold text-surface-900">100%</div>
							<div class="text-sm text-surface-500 mt-2">AI Powered</div>
						</div>
					</div>
				</div>
			</div>

			<!-- Features Section -->
			<section class="py-20 bg-surface-50">
				<div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
					<h2 class="text-3xl font-bold mb-12">How it works</h2>

					<div class="grid md:grid-cols-3 gap-8">
						<div class="bg-white p-8 rounded-lg border border-surface-200">
							<div class="text-4xl mb-4">🎯</div>
							<h3 class="text-xl font-bold mb-2">Describe Your Brand</h3>
							<p class="text-surface-600">Tell us about your industry, style, and values.</p>
						</div>

						<div class="bg-white p-8 rounded-lg border border-surface-200">
							<div class="text-4xl mb-4">⚡</div>
							<h3 class="text-xl font-bold mb-2">Get Instant Concepts</h3>
							<p class="text-surface-600">Receive multiple logo and design variations instantly.</p>
						</div>

						<div class="bg-white p-8 rounded-lg border border-surface-200">
							<div class="text-4xl mb-4">📥</div>
							<h3 class="text-xl font-bold mb-2">Download & Use</h3>
							<p class="text-surface-600">Export high-quality files ready for your business.</p>
						</div>
					</div>
				</div>
			</section>
		</main>

		<footer class="bg-white border-t border-surface-200 py-8">
			<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-surface-500 text-sm">
				&copy; {new Date().getFullYear()} BrandPixy. All rights reserved.
			</div>
		</footer>
	</div>
{:else}
	<div class="min-h-screen flex flex-col bg-white">
		<!-- App Header -->
		<header class="border-b border-surface-200 bg-white sticky top-0 z-40">
			<div class="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
				<button
					class="flex items-center gap-2 font-bold text-surface-900 hover:text-brand-600 transition-colors"
					onclick={() => {
						showApp = false;
						step = 1;
					}}
				>
					<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
					</svg>
					<span>BrandPixy</span>
				</button>

				{#if step < 4}
					<div class="flex items-center gap-3">
						{#each [1, 2, 3] as idx}
							<div class={`w-2 h-2 rounded-full ${step >= idx ? "bg-brand-600" : "bg-surface-200"}`}></div>
						{/each}
					</div>
				{/if}
			</div>
		</header>

		<main class="flex-1 w-full max-w-2xl mx-auto px-4 py-12">
			{#if step < 4}
				<div class="bg-white border border-surface-200 rounded-lg p-8">
					{#if step === 1}
						<div class="space-y-8">
							<div class="text-center space-y-2">
								<h2 class="text-3xl font-bold">
									What's your industry?
								</h2>
								<p class="text-surface-500">
									Tell us what space you're operating in.
								</p>
							</div>

							<div class="relative">
								<input
									type="text"
									bind:value={industry}
									placeholder="e.g. AI Startup, Coffee Shop, Fashion Brand"
									class="input text-lg py-4 pl-6"
									onkeydown={(e) =>
										e.key === "Enter" &&
										industry &&
										nextStep()}
									autofocus
								/>
								<button
									class="absolute right-2 top-2 bottom-2 btn btn-primary py-2 px-6"
									disabled={!industry}
									onclick={nextStep}
								>
									Next
								</button>
							</div>

							<div class="flex flex-wrap gap-3 justify-center">
								{#each ["Technology", "Food & Beverage", "Fashion", "Health", "Finance", "Education"] as hint}
									<button
										class="px-4 py-2 rounded-full bg-surface-100 text-surface-600 text-sm hover:bg-surface-200 hover:text-surface-900 transition-colors"
										onclick={() => {
											industry = hint;
											nextStep();
										}}
									>
										{hint}
									</button>
								{/each}
							</div>
						</div>
					{/if}

					{#if step === 2}
						<div class="space-y-8">
							<div class="text-center space-y-2">
								<h2 class="text-3xl font-bold">
									Choose your vibe
								</h2>
								<p class="text-surface-500">
									How should your brand feel?
								</p>
							</div>

							<div class="grid grid-cols-2 md:grid-cols-4 gap-4">
								{#each vibes as v}
									<button
										class={`p-4 rounded-xl border text-left transition-all duration-200 hover:shadow-md ${vibe === v.id ? "border-brand-500 bg-brand-50 ring-1 ring-brand-500" : "border-surface-200 hover:border-brand-300"}`}
										onclick={() => {
											vibe = v.id;
											nextStep();
										}}
									>
										<div class="text-3xl mb-3">
											{v.emoji}
										</div>
										<div class="font-bold text-surface-900">
											{v.id}
										</div>
										<p
											class="text-xs text-surface-500 mt-1"
										>
											{v.desc}
										</p>
									</button>
								{/each}
							</div>

							<div class="flex justify-start">
								<button
									class="text-surface-500 hover:text-surface-900 font-medium"
									onclick={prevStep}
								>
									← Back
								</button>
							</div>
						</div>
					{/if}

					{#if step === 3}
						<div class="space-y-8">
							<div class="text-center space-y-2">
								<h2 class="text-3xl font-bold">Core Values</h2>
								<p class="text-surface-500">
									Any specific keywords or values to
									emphasize? (Optional)
								</p>
							</div>

							<input
								type="text"
								bind:value={values}
								placeholder="e.g. sustainability, speed, trust"
								class="w-full px-4 py-3 border border-surface-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent"
								onkeydown={(e) => e.key === "Enter" && submit()}
								autofocus
							/>

							<div class="flex justify-between items-center pt-4">
								<button
									class="text-surface-500 hover:text-surface-900 font-medium"
									onclick={prevStep}
								>
									← Back
								</button>
								<button
									class="btn btn-primary px-8 py-4 text-lg shadow-glow"
									onclick={submit}
									disabled={loading}
								>
									{#if loading}
										<span class="animate-spin mr-2">⟳</span>
										Generating...
									{:else}
										Generate Brand Identity ✨
									{/if}
								</button>
							</div>
						</div>
					{/if}
				</div>
			{:else}
				<!-- Results View -->
				<div class="space-y-8 animate-fade-in">
					<div class="flex items-center justify-between">
						<div>
							<h2 class="text-3xl font-bold">
								Your Brand Concepts
							</h2>
							<p class="text-surface-500 mt-1">
								{industry} • {vibe}
							</p>
						</div>
						<button
							class="btn btn-secondary"
							onclick={() => {
								step = 1;
								suggestions = [];
							}}
						>
							Start Over
						</button>
					</div>

					<div class="grid md:grid-cols-2 gap-6">
						{#each suggestions as s, i}
							<div class="bg-white border border-surface-200 rounded-lg overflow-hidden">
								<div class="aspect-square bg-surface-50 flex items-center justify-center p-4">
									{#if s.logoUrl}
										<img
											src={s.logoUrl}
											alt={s.name}
											class="w-full h-full object-contain drop-shadow-sm"
										/>
									{:else}
										<div class="w-full h-full text-brand-600 p-2 flex items-center justify-center">
											{@html s.svg}
										</div>
									{/if}
									{#if s.generating}
										<div class="absolute bottom-2 left-0 right-0 text-center z-10">
											<span class="text-xs font-medium text-brand-600 animate-pulse bg-white/90 px-2 py-1 rounded-full shadow-sm">Generating HQ...</span>
										</div>
									{/if}
								</div>
								<div class="p-4">
									<h3 class="font-bold mb-2 truncate">{s.name}</h3>
									<p class="text-surface-500 text-sm mb-4 line-clamp-2">
										{s.tagline}
									</p>
									<button
										class="btn btn-secondary w-full text-sm py-2"
										onclick={() => downloadLogo(s)}
									>
										Download
									</button>
								</div>
							</div>
						{/each}

						<!-- Premium Card -->
						<div class="bg-white border border-surface-200 rounded-lg p-8 flex flex-col justify-center items-center text-center space-y-4">
							<div class="text-3xl">💎</div>
							<div>
								<h3 class="font-bold">Unlock Full Brand Kit</h3>
								<p class="text-surface-600 text-sm mt-1">Get templates & brand guidelines</p>
							</div>
							<button
								class="btn btn-primary w-full"
								onclick={() => (showUnlockModal = true)}
							>
								Upgrade for $29
							</button>
						</div>
					</div>
				</div>
			{/if}
		</main>
	</div>

<!-- Modal -->
{#if showUnlockModal}
	<div
		class="fixed inset-0 z-[100] flex items-center justify-center p-4"
		transition:fade={{ duration: 200 }}
	>
		<div class="absolute inset-0 bg-black/30">
		<div
			class="relative bg-white border border-surface-200 rounded-lg w-full max-w-lg p-8 shadow-lg"
		>
			<button
				class="absolute top-4 right-4 text-surface-400 hover:text-surface-900"
				onclick={() => (showUnlockModal = false)}
			>
				<svg
					class="w-6 h-6"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
					><path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M6 18L18 6M6 6l12 12"
					/></svg
				>
			</button>

			<div class="text-center mb-8">
				<div
					class="w-16 h-16 bg-brand-100 text-brand-600 rounded-2xl flex items-center justify-center text-3xl mx-auto mb-4"
				>
					🚀
				</div>
				<h2 class="text-2xl font-bold">Professional Brand Kit</h2>
				<p class="text-surface-500 mt-2">
					Everything you need to launch your brand today.
				</p>
			</div>

			<ul class="space-y-4 mb-8">
				{#each ["Social Media Templates", "Brand Guidelines PDF", "Business Card Designs", "Vector Source Files", "Font Licenses"] as item}
					<li class="flex items-center gap-3 text-surface-700">
						<svg
							class="w-5 h-5 text-green-500"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
							><path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M5 13l4 4L19 7"
							/></svg
						>
						{item}
					</li>
				{/each}
			</ul>

			<button class="btn btn-primary w-full py-4 text-lg shadow-glow">
				Get Instant Access - $29
			</button>
		</div>
	</div>
{/if}
