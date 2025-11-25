<script>
	import { onMount } from "svelte";
	import { fade, fly, slide } from "svelte/transition";
	import ThemeToggle from "$lib/components/ThemeToggle.svelte";

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
			const response = await fetch("http://127.0.0.1:8000/api/generate", {
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
				throw new Error("Failed to generate brands");
			}

			const data = await response.json();
			suggestions = data.suggestions;

			step = 4;
			loading = false;
		} catch (error) {
			console.error("Submission error:", error);
			alert("Something went wrong. Please try again.");
			loading = false;
		}
	}

	function downloadLogo(item) {
		// Existing download logic
		alert(`Downloading ${item.name}...`);
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
		<!-- Navigation -->
		<nav class="sticky top-0 z-50 glass border-b border-surface-200/50">
			<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
				<div class="flex justify-between items-center h-16">
					<div class="flex items-center gap-3">
						<div class="relative w-12 h-12">
							<img
								src="/logo01.png"
								alt="BrandPixy"
								class="w-full h-full object-contain"
							/>
						</div>
						<span
							class="text-xl font-display font-bold bg-clip-text text-transparent bg-gradient-to-r from-brand-600 to-brand-400"
						>
							BrandPixy
						</span>
					</div>

					<div class="hidden md:flex items-center gap-8">
						<a
							href="#features"
							class="text-sm font-medium text-surface-600 hover:text-brand-600 transition-colors"
							>Features</a
						>
						<a
							href="#pricing"
							class="text-sm font-medium text-surface-600 hover:text-brand-600 transition-colors"
							>Pricing</a
						>
						<ThemeToggle />
						<button
							class="btn btn-primary"
							onclick={() => (showApp = true)}
						>
							Launch Builder
						</button>
					</div>

					<div class="md:hidden flex items-center gap-4">
						<ThemeToggle />
						<button
							class="p-2 text-surface-600"
							onclick={() => (isMenuOpen = !isMenuOpen)}
							aria-label="Toggle menu"
						>
							<svg
								class="w-6 h-6"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d={isMenuOpen
										? "M6 18L18 6M6 6l12 12"
										: "M4 6h16M4 12h16M4 18h16"}
								/>
							</svg>
						</button>
					</div>
				</div>
			</div>

			<!-- Mobile Menu -->
			{#if isMenuOpen}
				<div
					class="md:hidden absolute top-20 left-0 w-full bg-white/95 dark:bg-surface-900/95 backdrop-blur-lg border-b border-surface-200 dark:border-surface-800 p-4 flex flex-col gap-4 shadow-xl animate-slide-up"
				>
					<a
						href="#features"
						class="text-lg font-medium text-surface-600 hover:text-brand-600 transition-colors py-2"
						onclick={() => (isMenuOpen = false)}>Features</a
					>
					<a
						href="#pricing"
						class="text-lg font-medium text-surface-600 hover:text-brand-600 transition-colors py-2"
						onclick={() => (isMenuOpen = false)}>Pricing</a
					>
					<button
						class="btn btn-primary w-full"
						onclick={() => {
							showApp = true;
							isMenuOpen = false;
						}}
					>
						Launch Builder
					</button>
				</div>
			{/if}
		</nav>

		<!-- Hero Section -->
		<main class="flex-grow">
			<div class="relative overflow-hidden pt-20 pb-32">
				<div
					class="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[500px] bg-brand-500/10 blur-[120px] rounded-full pointer-events-none"
				></div>

				<div
					class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center"
				>
					<div
						class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-brand-50 text-brand-700 text-sm font-medium mb-8 animate-fade-in"
					>
						<span class="relative flex h-2 w-2">
							<span
								class="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand-400 opacity-75"
							></span>
							<span
								class="relative inline-flex rounded-full h-2 w-2 bg-brand-500"
							></span>
						</span>
						AI-Powered Brand Generation v2.0
					</div>

					<h1
						class="text-5xl md:text-7xl font-bold tracking-tight mb-8 animate-slide-up"
						style="animation-delay: 0.1s"
					>
						Craft your brand identity <br />
						<span
							class="text-transparent bg-clip-text bg-gradient-primary"
							>in seconds, not weeks.</span
						>
					</h1>

					<p
						class="text-xl text-surface-600 max-w-2xl mx-auto mb-12 animate-slide-up"
						style="animation-delay: 0.2s"
					>
						Generate unique logos, color palettes, and brand stories
						tailored to your industry. Professional quality,
						instantly available.
					</p>

					<div
						class="flex flex-col sm:flex-row items-center justify-center gap-4 animate-slide-up"
						style="animation-delay: 0.3s"
					>
						<button
							class="btn text-lg px-10 py-5 w-full sm:w-auto bg-purple-600 text-white font-bold shadow-xl hover:shadow-2xl hover:scale-105 transition-all duration-300 rounded-xl hover:bg-purple-700"
							onclick={() => (showApp = true)}
						>
							Start Generating Free
						</button>
					</div>

					<!-- Stats -->
					<div
						class="grid grid-cols-2 md:grid-cols-4 gap-8 mt-24 border-t border-surface-200 pt-12 animate-fade-in"
						style="animation-delay: 0.5s"
					>
						<div>
							<div class="text-3xl font-bold text-surface-900">
								10k+
							</div>
							<div class="text-sm text-surface-500 mt-1">
								Brands Created
							</div>
						</div>
						<div>
							<div class="text-3xl font-bold text-surface-900">
								100%
							</div>
							<div class="text-sm text-surface-500 mt-1">
								AI Generated
							</div>
						</div>
						<div>
							<div class="text-3xl font-bold text-surface-900">
								&lt; 30s
							</div>
							<div class="text-sm text-surface-500 mt-1">
								Generation Time
							</div>
						</div>
						<div>
							<div class="text-3xl font-bold text-surface-900">
								4.9/5
							</div>
							<div class="text-sm text-surface-500 mt-1">
								User Rating
							</div>
						</div>
					</div>
				</div>
			</div>

			<!-- Features Grid -->
			<section id="features" class="py-24 bg-surface-50">
				<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
					<div class="text-center mb-16">
						<h2 class="text-3xl font-bold mb-4">
							Everything you need to launch
						</h2>
						<p class="text-surface-600 max-w-2xl mx-auto">
							From logo to brand guidelines, we generate a
							complete identity package.
						</p>
					</div>

					<div class="grid md:grid-cols-3 gap-8">
						<div
							class="card p-8 hover:-translate-y-1 transition-transform"
						>
							<img
								src="/logo01.png"
								alt="BrandPixy Logo"
								class="w-12 h-12 border-4 border-slate-900 dark:border-slate-100 object-cover mb-6"
							/>
							<h3 class="text-xl font-bold mb-3">
								Instant Generation
							</h3>
							<p class="text-surface-600 leading-relaxed">
								Get dozens of unique concepts in seconds.
								Iterate and refine until it's perfect.
							</p>
						</div>
						<div
							class="card p-8 hover:-translate-y-1 transition-transform"
						>
							<div
								class="w-12 h-12 rounded-lg bg-teal-100 text-teal-600 flex items-center justify-center text-2xl mb-6"
							>
								🎨
							</div>
							<h3 class="text-xl font-bold mb-3">
								Modern Aesthetics
							</h3>
							<p class="text-surface-600 leading-relaxed">
								Trained on the latest design trends to ensure
								your brand looks fresh and premium.
							</p>
						</div>
						<div
							class="card p-8 hover:-translate-y-1 transition-transform"
						>
							<div
								class="w-12 h-12 rounded-lg bg-purple-100 text-purple-600 flex items-center justify-center text-2xl mb-6"
							>
								📦
							</div>
							<h3 class="text-xl font-bold mb-3">Full Export</h3>
							<p class="text-surface-600 leading-relaxed">
								Download high-res PNGs, SVGs, and brand
								guideline documents instantly.
							</p>
						</div>
					</div>
				</div>
			</section>
		</main>

		<footer class="bg-white border-t border-surface-200 py-12">
			<div
				class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row justify-between items-center gap-6"
			>
				<div class="flex items-center gap-2">
					<img
						src="/logo01.png"
						alt="BrandPixy"
						class="w-8 h-8 object-contain"
					/>
					<span class="font-bold text-surface-900">BrandPixy</span>
				</div>
				<div class="flex gap-8 text-sm text-surface-500">
					<a href="#" class="hover:text-brand-600">Privacy</a>
					<a href="#" class="hover:text-brand-600">Terms</a>
					<a href="#" class="hover:text-brand-600">Contact</a>
				</div>
				<div class="text-sm text-surface-400">
					&copy; {new Date().getFullYear()} BrandPixy. All rights reserved.
				</div>
			</div>
		</footer>
	</div>
{:else}
	<div class="min-h-screen flex flex-col bg-surface-50">
		<!-- App Header -->
		<header class="sticky top-0 z-40 glass border-b border-surface-200/50">
			<div
				class="max-w-5xl mx-auto px-4 py-4 flex items-center justify-between"
			>
				<button
					class="flex items-center gap-2 font-bold text-surface-900 hover:text-brand-600 transition-colors"
					onclick={() => {
						showApp = false;
						step = 1;
					}}
				>
					<img
						src="/logo01.png"
						alt="BrandPixy"
						class="w-8 h-8 object-contain"
					/>
					<span>BrandPixy</span>
				</button>

				{#if step < 4}
					<div class="flex items-center gap-2">
						{#each [1, 2, 3] as idx}
							<div
								class={`h-2 w-12 rounded-full transition-all duration-300 ${step >= idx ? "bg-brand-500" : "bg-surface-200"}`}
							></div>
						{/each}
					</div>
				{:else}
					<button
						class="btn btn-secondary text-sm py-2"
						onclick={() => {
							step = 1;
							suggestions = [];
						}}
					>
						New Project
					</button>
				{/if}
			</div>
		</header>

		<main class="flex-1 w-full max-w-3xl mx-auto px-4 py-12">
			{#if step < 4}
				<div class="card p-8 md:p-12 animate-scale-in">
					{#if step === 1}
						<div class="space-y-8">
							<div class="text-center space-y-2">
								<span
									class="text-brand-600 font-medium text-sm tracking-wider uppercase"
									>Step 1 of 3</span
								>
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
								<span
									class="text-brand-600 font-medium text-sm tracking-wider uppercase"
									>Step 2 of 3</span
								>
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
								<span
									class="text-brand-600 font-medium text-sm tracking-wider uppercase"
									>Step 3 of 3</span
								>
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
								class="input text-lg py-4 pl-6"
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
							<div
								class="card overflow-hidden group"
								style="animation-delay: {i * 100}ms"
							>
								<div
									class="aspect-video bg-surface-50 flex items-center justify-center p-8 group-hover:bg-surface-100 transition-colors"
								>
									{#if s.logoUrl}
										<img
											src={s.logoUrl}
											alt={s.name}
											class="w-32 h-32 object-contain drop-shadow-lg"
										/>
									{:else}
										<div class="w-32 h-32 text-brand-600">
											{@html s.svg}
										</div>
									{/if}
								</div>
								<div class="p-6">
									<h3 class="text-2xl font-bold mb-1">
										{s.name}
									</h3>
									<p class="text-surface-500 text-sm mb-6">
										{s.tagline}
									</p>
									<button
										class="btn btn-secondary w-full group-hover:bg-brand-50 group-hover:text-brand-700 group-hover:border-brand-200"
										onclick={() => downloadLogo(s)}
									>
										Download Assets
									</button>
								</div>
							</div>
						{/each}

						<!-- Premium Card -->
						<div
							class="card overflow-hidden relative group border-brand-200"
						>
							<div
								class="absolute inset-0 bg-gradient-primary opacity-5 group-hover:opacity-10 transition-opacity"
							></div>
							<div
								class="p-8 h-full flex flex-col justify-center items-center text-center space-y-6"
							>
								<div
									class="w-16 h-16 rounded-full bg-brand-100 text-brand-600 flex items-center justify-center text-2xl"
								>
									💎
								</div>
								<div>
									<h3 class="text-xl font-bold">
										Unlock Full Brand Kit
									</h3>
									<p class="text-surface-600 mt-2 text-sm">
										Get social media templates, business
										cards, and brand guidelines.
									</p>
								</div>
								<button
									class="btn btn-primary w-full shadow-glow"
									onclick={() => (showUnlockModal = true)}
								>
									Upgrade for $29
								</button>
							</div>
						</div>
					</div>
				</div>
			{/if}
		</main>
	</div>
{/if}

<!-- Modal -->
{#if showUnlockModal}
	<div
		class="fixed inset-0 z-[100] flex items-center justify-center p-4"
		transition:fade={{ duration: 200 }}
	>
		<div
			class="absolute inset-0 bg-surface-900/60 backdrop-blur-sm"
			onclick={() => (showUnlockModal = false)}
		></div>
		<div
			class="relative card w-full max-w-lg p-8 shadow-2xl animate-scale-in"
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
