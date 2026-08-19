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
            desc: "Clean, sleek, and forward-thinking",
        },
        {
            id: "Luxury",
            desc: "Elegant, premium, and exclusive",
        },
        {
            id: "Fun",
            desc: "Playful, energetic, and vibrant",
        },
        {
            id: "Minimalist",
            desc: "Simple, essential, and pure",
        },
        {
            id: "Tech",
            desc: "Digital, innovative, and smart",
        },
        {
            id: "Classic",
            desc: "Timeless, trustworthy, and established",
        },
        {
            id: "Professional",
            desc: "Corporate, serious, and reliable",
        },
        {
            id: "Eco",
            desc: "Natural, organic, and sustainable",
        },
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

            generateAllLogos();
        } catch (error) {
            console.error("Submission error details:", error);
            alert(`Error: ${error.message}. Check console for details.`);
            loading = false;
        }
    }

    function downloadLogo(item) {
        alert(`Downloading ${item.name}...`);
    }

    async function generateAllLogos() {
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

        const workers = Array(concurrency)
            .fill(null)
            .map(() => worker());

        await Promise.all(workers);
    }

    async function generateHQLogo(index, name) {
        if (suggestions[index].logoUrl || suggestions[index].generating) return;

        suggestions[index].generating = true;
        suggestions = [...suggestions];

        try {
            const res = await fetch(
                `/api/generate-logo?name=${encodeURIComponent(name)}&vibe=${encodeURIComponent(vibe)}`,
                {
                    method: "POST",
                }
            );

            const data = await res.json();

            if (data.url) {
                suggestions[index].logoUrl = data.url;
            }
        } catch (e) {
            console.error(`Failed to generate logo for ${name}:`, e);
        } finally {
            suggestions[index].generating = false;
            suggestions = [...suggestions];
        }
    }
</script>

<svelte:head>
    <title>Brand Identity Generator</title>

    <meta
        name="description"
        content="Create a visual direction for your brand."
    />
</svelte:head>

{#if !showApp}

    <!-- LANDING PAGE -->
    <div
        class="min-h-screen text-white"
        style="background: linear-gradient(172deg, rgba(63, 94, 251, 1) 0%, rgba(237, 70, 252, 1) 100%);"
    >

        <!-- Navigation -->
        <header class="max-w-[1400px] mx-auto px-6 md:px-10 py-7">

            <div class="flex justify-between items-center">



 

            </div>

        </header>

        <main>

            <!-- HERO -->
            <section
                class="max-w-[1400px] mx-auto px-6 md:px-10 pt-24 md:pt-36 pb-32"
            >

                <div class="grid md:grid-cols-12 gap-10">

                    <div class="md:col-span-8">

                

                        <h1
                            class="text-[clamp(3.5rem,8vw,8rem)] leading-[0.86] tracking-[-0.07em] font-medium"
                        >
                            Give your<br />
                            brand a point<br />
                            of view.
                        </h1>

                    </div>

                    <div
                        class="md:col-span-3 md:col-start-10 md:pt-32"
                    >

                        <p
                            class="text-sm md:text-base leading-7 text-white/70"
                        >
                            A focused way to explore names, visual directions
                            and identities before you commit to one.
                        </p>

                        <button
                            class="mt-8 text-sm border-b border-white/70 pb-1 hover:border-white transition-colors"
                            onclick={() => (showApp = true)}
                        >
                            Try it now! →
                        </button>

                    </div>

                </div>

            </section>

            <!-- PROCESS -->
            <section
                class="border-y border-white/20"
            >

                <div
                    class="max-w-[1400px] mx-auto px-6 md:px-10"
                >

                    <div
                        class="grid md:grid-cols-4 divide-x divide-white/20"
                    >

                        <div class="p-7 md:p-10">



                            <div class="mt-12 text-sm text-white">
                                Explore the result.
                            </div>

                        </div>

                    </div>

                </div>

            </section>

            <!-- IDEA -->
            <section
                class="max-w-[1400px] mx-auto px-6 md:px-10 py-28"
            >

                <div class="grid md:grid-cols-12 gap-10">

                    <div class="md:col-span-4">

                        <div
                            class="text-[10px] uppercase tracking-[0.22em] text-white/50"
                        >
                            The idea
                        </div>

                    </div>

                    <div class="md:col-span-6">

                        <p
                            class="text-2xl md:text-4xl leading-[1.15] tracking-[-0.03em]"
                        >
                            Good identities usually begin with a simple
                            question:
                            <span class="text-white/50">
                                what should this feel like?
                            </span>
                        </p>

                    </div>

                </div>

            </section>

        </main>

        <!-- FOOTER -->
        <footer class="border-t border-white/20">

            <div
                class="max-w-[1400px] mx-auto px-6 md:px-10 py-7 flex justify-between"
            >

                <span
                    class="text-[10px] uppercase tracking-[0.18em] text-white/50"
                >
                    Brand identity builder
                </span>

                <span
                    class="text-[10px] uppercase tracking-[0.18em] text-white/50"
                >
                    {new Date().getFullYear()}
                </span>

            </div>

        </footer>

    </div>

{:else}

    <!-- BUILDER -->
    <div
        class="min-h-screen text-white"
        style="background: linear-gradient(172deg, rgba(63, 94, 251, 1) 0%, rgba(237, 70, 252, 1) 100%);"
    >

        <!-- HEADER -->
        <header class="border-b border-white/20">

            <div
                class="max-w-[1400px] mx-auto px-6 md:px-10 h-16 flex items-center justify-between"
            >

                <button
                    class="text-[10px] uppercase tracking-[0.2em] text-white/70 hover:text-white transition-colors"
                    onclick={() => {
                        showApp = false;
                        step = 1;
                    }}
                >
                    ← Exit
                </button>



      

            

            </div>

        </header>

        <main class="max-w-[1400px] mx-auto px-6 md:px-10 py-16 md:py-24">

            {#if step < 4}

                <div class="grid md:grid-cols-12 gap-10">

                    <!-- STEP INDEX -->
                    <aside class="md:col-span-2">

                        <div
                            class="text-[11px] uppercase tracking-[0.2em] text-white/50"
                        >
                            0{step}
                        </div>

     

                    </aside>

                    <!-- FORM -->
                    <section class="md:col-span-8 md:col-start-4">

                        {#if step === 1}

                            <div>

                                <h2
                                    class="text-5xl md:text-7xl tracking-[-0.06em] leading-[0.9] font-medium"
                                >
                                    What are<br />
                                    you building?
                                </h2>

                                <p
                                    class="mt-8 text-sm text-white/70 max-w-md leading-6"
                                >
                                    Tell us what kind of company, product,
                                    service or project this identity belongs to.
                                </p>

                                <div
                                    class="mt-14 border-b border-white/40 focus-within:border-white transition-colors"
                                >

                                    <input
                                        type="text"
                                        bind:value={industry}
                                        placeholder="e.g. independent coffee company"
                                        class="w-full bg-transparent py-4 text-xl md:text-2xl text-white placeholder:text-white/40 focus:outline-none"
                                        onkeydown={(e) =>
                                            e.key === "Enter" &&
                                            industry &&
                                            nextStep()}
                                        autofocus
                                    />

                                </div>

                                <div class="mt-8 flex flex-wrap gap-x-6 gap-y-3">

                                    {#each ["Technology", "Food & Beverage", "Fashion", "Health", "Finance", "Education"] as hint}

                                        <button
                                            class="text-xs text-white/60 hover:text-white transition-colors"
                                            onclick={() => {
                                                industry = hint;
                                                nextStep();
                                            }}
                                        >
                                            {hint}
                                        </button>

                                    {/each}

                                </div>

                                <div class="mt-14 flex justify-end">

                                    <button
                                        class="text-xs uppercase tracking-[0.16em] disabled:text-white/30 hover:underline"
                                        disabled={!industry}
                                        onclick={nextStep}
                                    >
                                        Continue →
                                    </button>

                                </div>

                            </div>

                        {:else if step === 2}

                            <div>

                                <h2
                                    class="text-5xl md:text-7xl tracking-[-0.06em] leading-[0.9] font-medium"
                                >
                                    How should<br />
                                    it feel?
                                </h2>

                                <p
                                    class="mt-8 text-sm text-white/70 max-w-md leading-6"
                                >
                                    Pick the direction that feels closest.
                                    There is no right answer.
                                </p>

                                <div
                                    class="mt-14 grid grid-cols-2 md:grid-cols-4 border-t border-l border-white/20"
                                >

                                    {#each vibes as v}

                                        <button
                                            class={`min-h-[125px] p-5 text-left border-r border-b border-white/20 transition-all ${
                                                vibe === v.id
                                                    ? "bg-white text-[#3F5EFB]"
                                                    : "bg-white/5 hover:bg-white/15"
                                            }`}
                                            onclick={() => {
                                                vibe = v.id;
                                                nextStep();
                                            }}
                                        >

                                            <div class="text-sm font-medium">
                                                {v.id}
                                            </div>

                                            <div
                                                class={`text-[11px] leading-5 mt-3 ${
                                                    vibe === v.id
                                                        ? "text-[#3F5EFB]/70"
                                                        : "text-white/60"
                                                }`}
                                            >
                                                {v.desc}
                                            </div>

                                        </button>

                                    {/each}

                                </div>

                                <div class="mt-10">

                                    <button
                                        class="text-xs uppercase tracking-[0.16em] text-white/60 hover:text-white"
                                        onclick={prevStep}
                                    >
                                        ← Back
                                    </button>

                                </div>

                            </div>

                        {:else if step === 3}

                            <div>

                                <h2
                                    class="text-5xl md:text-7xl tracking-[-0.06em] leading-[0.9] font-medium"
                                >
                                    What should<br />
                                    it stand for?
                                </h2>

                                <p
                                    class="mt-8 text-sm text-white/70 max-w-md leading-6"
                                >
                                    Add a few words, principles or qualities
                                    that should influence the identity.
                                </p>

                                <div
                                    class="mt-14 border-b border-white/40 focus-within:border-white transition-colors"
                                >

                                    <input
                                        type="text"
                                        bind:value={values}
                                        placeholder="e.g. trust, speed, simplicity"
                                        class="w-full bg-transparent py-4 text-xl md:text-2xl text-white placeholder:text-white/40 focus:outline-none"
                                        onkeydown={(e) =>
                                            e.key === "Enter" && submit()}
                                        autofocus
                                    />

                                </div>

                                <div
                                    class="mt-14 flex items-center justify-between"
                                >

                                    <button
                                        class="text-xs uppercase tracking-[0.16em] text-white/60 hover:text-white"
                                        onclick={prevStep}
                                    >
                                        ← Back
                                    </button>

                                    <button
                                        class="text-xs uppercase tracking-[0.16em] disabled:text-white/30 hover:underline"
                                        onclick={submit}
                                        disabled={loading}
                                    >
                                        {#if loading}
                                            Generating...
                                        {:else}
                                            Generate concepts →
                                        {/if}
                                    </button>

                                </div>

                            </div>

                        {/if}

                    </section>

                </div>

            {:else}

                <!-- RESULTS -->
                <div>

                    <div
                        class="grid md:grid-cols-12 gap-10 mb-16"
                    >

                        <div class="md:col-span-7">

                            <div
                                class="text-[10px] uppercase tracking-[0.2em] text-white/50 mb-6"
                            >
                                Generated direction
                            </div>

                            <h1
                                class="text-5xl md:text-7xl tracking-[-0.06em] leading-[0.9] font-medium"
                            >
                                {industry}
                            </h1>

                        </div>

                        <div
                            class="md:col-span-3 md:col-start-10 md:pt-10"
                        >

                            <div class="text-xs text-white/70 leading-6">

                                <div
                                    class="text-white/50 uppercase tracking-[0.16em] text-[10px] mb-2"
                                >
                                    Character
                                </div>

                                {vibe}

                                {#if values}

                                    <div class="mt-5">

                                        <div
                                            class="text-white/50 uppercase tracking-[0.16em] text-[10px] mb-2"
                                        >
                                            Values
                                        </div>

                                        {values}

                                    </div>

                                {/if}

                            </div>

                            <button
                                class="mt-8 text-xs uppercase tracking-[0.16em] border-b border-white/60 pb-1 hover:border-white transition-colors"
                                onclick={() => {
                                    step = 1;
                                    suggestions = [];
                                }}
                            >
                                Start over
                            </button>

                        </div>

                    </div>

                    <!-- RESULT GRID -->
                    <div
                        class="grid md:grid-cols-12 gap-px bg-white/20 border border-white/20"
                    >

                        {#each suggestions as s, i}

                            <article
                                class="md:col-span-6 bg-white/10 backdrop-blur-sm"
                            >

                                <div
                                    class="relative aspect-square bg-white/95 flex items-center justify-center p-12"
                                >

                                    {#if s.logoUrl}

                                        <img
                                            src={s.logoUrl}
                                            alt={s.name}
                                            class="w-full h-full object-contain"
                                        />

                                    {:else}

                                        <div
                                            class="w-full h-full flex items-center justify-center text-brand-600"
                                        >
                                            {@html s.svg}
                                        </div>

                                    {/if}

                                    {#if s.generating}

                                        <div
                                            class="absolute bottom-5 left-5 text-[10px] uppercase tracking-[0.15em] text-[#555]"
                                        >
                                            Generating high resolution
                                        </div>

                                    {/if}

                                </div>

                                <div class="p-6">

                                    <div
                                        class="flex justify-between items-start gap-6"
                                    >

                                        <div>

                                            <h3 class="text-base font-medium">
                                                {s.name}
                                            </h3>

                                            <p
                                                class="text-xs text-white/60 mt-2 max-w-sm leading-5"
                                            >
                                                {s.tagline}
                                            </p>

                                        </div>

                                        <span
                                            class="text-[9px] uppercase tracking-[0.18em] text-white/40"
                                        >
                                            0{i + 1}
                                        </span>

                                    </div>

                                    <button
                                        class="mt-6 text-[10px] uppercase tracking-[0.16em] border-b border-white/40 pb-1 hover:border-white transition-colors"
                                        onclick={() => downloadLogo(s)}
                                    >
                                        Download
                                    </button>

                                </div>

                            </article>

                        {/each}

                        <!-- BRAND KIT -->
                        <article
                            class="md:col-span-6 min-h-[450px] p-8 md:p-10 flex flex-col justify-between bg-white/10 backdrop-blur-md"
                        >

                            <div>

                                <div
                                    class="text-[10px] uppercase tracking-[0.2em] text-white/50"
                                >
                                    Next step
                                </div>

                                <h2
                                    class="text-3xl md:text-4xl tracking-[-0.04em] mt-10 max-w-sm font-medium"
                                >
                                    Turn one direction into a complete identity.
                                </h2>

                            </div>

                            <div>

                                <div
                                    class="border-t border-white/20 pt-5 mb-7 text-xs text-white/60 leading-6"
                                >
                                    Brand guidelines<br />
                                    Social templates<br />
                                    Business cards<br />
                                    Vector files<br />
                                    Font licenses
                                </div>

                                <button
                                    class="text-xs uppercase tracking-[0.16em] text-white border-b border-white/70 pb-1 hover:border-white transition-colors"
                                    onclick={() => (showUnlockModal = true)}
                                >
                                    View brand kit — $29
                                </button>

                            </div>

                        </article>

                    </div>

                </div>

            {/if}

        </main>

    </div>

{/if}


<!-- MODAL -->
{#if showUnlockModal}

    <div
        class="fixed inset-0 z-[100] flex items-center justify-center p-6"
        transition:fade={{ duration: 150 }}
    >

        <button
            class="absolute inset-0 bg-black/30 backdrop-blur-sm cursor-default"
            aria-label="Close modal"
            onclick={() => (showUnlockModal = false)}
        ></button>

        <div
            class="relative w-full max-w-lg p-8 md:p-10 bg-white text-[#171717] border border-white/20 shadow-2xl"
        >

            <button
                class="absolute top-7 right-7 text-[#888] hover:text-black"
                onclick={() => (showUnlockModal = false)}
                aria-label="Close"
            >
                <svg
                    class="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                >
                    <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="1.5"
                        d="M6 18L18 6M6 6l12 12"
                    />
                </svg>
            </button>

            <div
                class="text-[10px] uppercase tracking-[0.2em] text-[#999]"
            >
                Brand kit
            </div>

            <h2
                class="text-3xl tracking-[-0.04em] font-medium mt-6"
            >
                Everything after the concept.
            </h2>

            <p
                class="text-sm text-[#777] leading-6 mt-4 max-w-md"
            >
                A complete set of assets for putting your chosen direction
                into use.
            </p>

            <div class="mt-10 border-t border-[#ddd]">

                {#each [
                    "Social media templates",
                    "Brand guidelines PDF",
                    "Business card designs",
                    "Vector source files",
                    "Font licenses"
                ] as item}

                    <div
                        class="py-4 border-b border-[#ddd] flex justify-between items-center"
                    >

                        <span class="text-sm">
                            {item}
                        </span>

                        <span class="text-xs text-[#999]">
                            Included
                        </span>

                    </div>

                {/each}

            </div>

            <button
                class="w-full mt-8 bg-[#171717] text-white h-12 text-xs uppercase tracking-[0.16em] hover:bg-[#333] transition-colors"
            >
                Get the brand kit — $29
            </button>

        </div>

    </div>

{/if}