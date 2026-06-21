<main>
	<h1>🌌 Bobiverse Tactical Movement Map</h1>
	<div class="map-area"></div>
</main>

<style>
	main {
		display: flex;
		flex-direction: column;
		width: 100%;
		height: 100vh;
		padding: 0.5rem 0.75rem;
	}

	h1 {
		margin: 0 0 0.5rem 0;
		font-size: 1.1rem;
		font-weight: 600;
		color: #e0e0e0;
	}

	.map-area {
		flex: 1;
		min-height: 0;
	}

	@media (max-width: 600px) {
		h1 {
			font-size: 0.95rem;
		}
	}
</style>
