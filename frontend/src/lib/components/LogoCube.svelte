<script>
	import { onMount } from 'svelte';

	let { logoUrl = '/logo.jpg' } = $props();
	let container;
	let cube;
	let mouseX = 0;
	let mouseY = 0;
	let targetX = 0;
	let targetY = 0;

	onMount(() => {
		const handleMouseMove = (e) => {
			const rect = container.getBoundingClientRect();
			const x = (e.clientX - rect.left) / rect.width - 0.5;
			const y = (e.clientY - rect.top) / rect.height - 0.5;
			
			// subtle movement
			targetX = x * 30; 
			targetY = y * 30;
		};

		const handleMouseLeave = () => {
			targetX = 0;
			targetY = 0;
		};

		window.addEventListener('mousemove', handleMouseMove);
		
		let animationFrame;
		const animate = () => {
			// Smooth interpolation
			mouseX += (targetX - mouseX) * 0.1;
			mouseY += (targetY - mouseY) * 0.1;

			if (cube) {
				cube.style.transform = `rotateX(${-mouseY - 15}deg) rotateY(${mouseX + 25}deg)`;
			}
			animationFrame = requestAnimationFrame(animate);
		};
		animate();

		return () => {
			window.removeEventListener('mousemove', handleMouseMove);
			cancelAnimationFrame(animationFrame);
		};
	});
</script>

<div class="scene" bind:this={container}>
	<div class="cube-container">
		<div class="cube" bind:this={cube}>
			<div class="face front">
				<div class="content">
					<img src={logoUrl} alt="Logo" />
					<div class="glow"></div>
				</div>
			</div>
			<div class="face back">
				<div class="content">
					<img src={logoUrl} alt="Logo" />
					<div class="glow"></div>
				</div>
			</div>
			<div class="face right">
				<div class="content">
					<img src={logoUrl} alt="Logo" />
					<div class="glow"></div>
				</div>
			</div>
			<div class="face left">
				<div class="content">
					<img src={logoUrl} alt="Logo" />
					<div class="glow"></div>
				</div>
			</div>
			<div class="face top"></div>
			<div class="face bottom"></div>
		</div>
	</div>
</div>

<style>
	.scene {
		width: 160px;
		height: 160px;
		perspective: 1000px;
		margin: 0 auto;
	}

	.cube-container {
		width: 100%;
		height: 100%;
		transform-style: preserve-3d;
		animation: float 6s ease-in-out infinite;
	}

	.cube {
		width: 100%;
		height: 100%;
		position: relative;
		transform-style: preserve-3d;
		transition: transform 0.1s ease-out;
		/* Initial rotation handled by JS or default */
		transform: rotateX(-15deg) rotateY(25deg);
	}

	.face {
		position: absolute;
		width: 160px;
		height: 160px;
		background: rgba(255, 255, 255, 0.1);
		backdrop-filter: blur(10px);
		border: 1px solid rgba(255, 255, 255, 0.2);
		border-radius: 24px;
		display: flex;
		align-items: center;
		justify-content: center;
		backface-visibility: visible; /* Changed to visible for glass effect */
		overflow: hidden;
		box-shadow: 0 0 15px rgba(129, 140, 248, 0.1);
	}

	.content {
		width: 80%;
		height: 80%;
		position: relative;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.face img {
		width: 100%;
		height: 100%;
		object-fit: contain;
		border-radius: 12px;
		z-index: 2;
	}

	.glow {
		position: absolute;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		width: 100%;
		height: 100%;
		background: radial-gradient(circle, rgba(99, 102, 241, 0.4) 0%, transparent 70%);
		filter: blur(20px);
		animation: pulse 3s infinite;
		z-index: 1;
	}

	.front  { transform: translateZ(80px); }
	.back   { transform: rotateY(180deg) translateZ(80px); }
	.right  { transform: rotateY(90deg) translateZ(80px); }
	.left   { transform: rotateY(-90deg) translateZ(80px); }
	.top    { transform: rotateX(90deg) translateZ(80px); background: rgba(255, 255, 255, 0.15); }
	.bottom { transform: rotateX(-90deg) translateZ(80px); background: rgba(255, 255, 255, 0.15); }

	@keyframes float {
		0%, 100% { transform: translateY(0); }
		50% { transform: translateY(-20px); }
	}

	@keyframes pulse {
		0%, 100% { opacity: 0.5; transform: translate(-50%, -50%) scale(1); }
		50% { opacity: 1; transform: translate(-50%, -50%) scale(1.2); }
	}
</style>
