<script lang="ts">
	import { bobRecords, minDate, maxDate } from '$lib/data/bobs';
	import { computePositions, applyJitter } from '$lib/data/positions';
	import Map from '$lib/Map.svelte';

	// Slider granularity: 1 day, parity with Streamlit's datetime slider
	// (chapter_selector.py — default min_date, MMM YYYY label).
	const DAY_MS = 86_400_000;
	const minMs = minDate.getTime();
	const maxMs = maxDate.getTime();

	// Pure client state — dragging mutates this, the map re-derives with no
	// reload and no network call. Default to the earliest date.
	let selectedMs = $state(minMs);

	const selectedDate = $derived(new Date(selectedMs));
	const positions = $derived(applyJitter(computePositions(bobRecords, selectedDate)));

	const sliderLabel = $derived(
		selectedDate.toLocaleDateString('en-US', { month: 'short', year: 'numeric', timeZone: 'UTC' })
	);

	// Parity with main.py:25 — `Tactical Status: <date>` + table of
	// Bob | Status | Last Log, built from the same cluster-ordered positions
	// the map renders. ISO date matches Streamlit's `selected_date.date()`.
	const isoDate = (d: Date) => d.toISOString().slice(0, 10);
	const statusDate = $derived(isoDate(selectedDate));
</script>

<main>
	<h1>🌌 Bobiverse Tactical Movement Map</h1>
	<div class="controls">
		<label for="timeline">Timeline Date</label>
		<input
			id="timeline"
			type="range"
			min={minMs}
			max={maxMs}
			step={DAY_MS}
			bind:value={selectedMs}
		/>
		<span class="slider-value">{sliderLabel}</span>
	</div>
	<div class="map-area">
		<Map {positions} />
	</div>
	<section class="status">
		<h2>Tactical Status: {statusDate}</h2>
		<table>
			<thead>
				<tr>
					<th>Bob</th>
					<th>Status</th>
					<th>Last Log</th>
				</tr>
			</thead>
			<tbody>
				{#each positions as p (p.name)}
					<tr>
						<td>{p.name}</td>
						<td>{p.status}</td>
						<td>{isoDate(p.lastDate)}</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</section>
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

	.controls {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		margin-bottom: 0.5rem;
		font-size: 0.85rem;
		color: #c0c0c0;
	}

	.controls label {
		font-weight: 600;
		white-space: nowrap;
	}

	.controls input[type='range'] {
		flex: 1;
		max-width: 480px;
		accent-color: #7aa2f7;
	}

	.slider-value {
		min-width: 5.5rem;
		font-variant-numeric: tabular-nums;
		color: #e0e0e0;
	}

	.map-area {
		flex: 1;
		min-height: 0;
	}

	.status {
		margin-top: 0.75rem;
	}

	.status h2 {
		margin: 0 0 0.5rem 0;
		font-size: 1rem;
		font-weight: 600;
		color: #e0e0e0;
	}

	.status table {
		width: 100%;
		border-collapse: collapse;
		font-size: 0.85rem;
		color: #c0c0c0;
	}

	.status th,
	.status td {
		text-align: left;
		padding: 0.35rem 0.5rem;
		border-bottom: 1px solid #333;
	}

	.status th {
		font-weight: 600;
		color: #e0e0e0;
	}

	.status td {
		font-variant-numeric: tabular-nums;
	}

	@media (max-width: 600px) {
		h1 {
			font-size: 0.95rem;
		}
	}
</style>
