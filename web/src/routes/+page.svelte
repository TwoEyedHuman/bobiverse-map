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

	// Display-only relabel; underlying status strings stay parity-locked to Python.
	const statusLabel = (s: string) =>
		s.replace(/^Stationary at /, 'At ').replace(/^Traveling to /, 'Enroute to ');
</script>

<main>
	<div class="timebar">
		<span class="brand">🌌 BOBIVERSE</span>
		<label for="timeline">◤ TIMELINE ◢</label>
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
	<div class="content">
		<div class="map-area">
			<Map {positions} />
		</div>
		<aside class="status">
			<h2>Tactical Status<span class="status-date">{statusDate}</span></h2>
			<div class="status-scroll">
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
								<td>{statusLabel(p.status)}</td>
								<td>{isoDate(p.lastDate)}</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</aside>
	</div>
</main>

<style>
	main {
		display: flex;
		flex-direction: column;
		width: 100%;
		height: 100vh;
		padding: 0;
		gap: 0;
	}

	/* Sci-fi timeline bar across the whole top */
	.timebar {
		display: flex;
		align-items: center;
		gap: 1rem;
		width: 100%;
		padding: 0.6rem 1.25rem;
		background: linear-gradient(180deg, #0a1424 0%, #050a14 100%);
		border-bottom: 1px solid #1e3a5f;
		box-shadow: 0 0 12px rgba(34, 211, 238, 0.15);
	}

	.brand {
		font-weight: 700;
		font-size: 0.9rem;
		letter-spacing: 0.08em;
		color: #e0e0e0;
		white-space: nowrap;
	}

	.timebar label {
		font-family: 'Courier New', monospace;
		font-weight: 700;
		font-size: 0.8rem;
		letter-spacing: 0.2em;
		color: #22d3ee;
		text-shadow: 0 0 8px rgba(34, 211, 238, 0.6);
		white-space: nowrap;
	}

	.timebar input[type='range'] {
		flex: 1;
		appearance: none;
		-webkit-appearance: none;
		height: 4px;
		border-radius: 2px;
		background: linear-gradient(90deg, #22d3ee 0%, #1e3a5f 100%);
		box-shadow: 0 0 8px rgba(34, 211, 238, 0.4);
		outline: none;
		cursor: pointer;
	}

	.timebar input[type='range']::-webkit-slider-thumb {
		-webkit-appearance: none;
		appearance: none;
		width: 16px;
		height: 16px;
		border-radius: 50%;
		background: #e0fbff;
		border: 2px solid #22d3ee;
		box-shadow: 0 0 10px rgba(34, 211, 238, 0.9);
		cursor: pointer;
	}

	.timebar input[type='range']::-moz-range-thumb {
		width: 16px;
		height: 16px;
		border-radius: 50%;
		background: #e0fbff;
		border: 2px solid #22d3ee;
		box-shadow: 0 0 10px rgba(34, 211, 238, 0.9);
		cursor: pointer;
	}

	.slider-value {
		min-width: 6rem;
		text-align: right;
		font-family: 'Courier New', monospace;
		font-variant-numeric: tabular-nums;
		letter-spacing: 0.05em;
		color: #22d3ee;
		text-shadow: 0 0 8px rgba(34, 211, 238, 0.5);
	}

	/* Map (left, fills) + status table (right, narrow) */
	.content {
		display: flex;
		flex: 1;
		min-height: 0;
	}

	.map-area {
		flex: 1;
		min-width: 0;
	}

	.status {
		display: flex;
		flex-direction: column;
		width: 260px;
		min-height: 0;
		border-left: 1px solid #1e3a5f;
		background: #0a0f18;
	}

	.status h2 {
		display: flex;
		flex-direction: column;
		margin: 0;
		padding: 0.6rem 0.75rem;
		font-size: 0.9rem;
		font-weight: 600;
		color: #e0e0e0;
		border-bottom: 1px solid #1e3a5f;
	}

	.status-date {
		font-family: 'Courier New', monospace;
		font-size: 0.75rem;
		font-weight: 400;
		color: #22d3ee;
	}

	.status-scroll {
		flex: 1;
		min-height: 0;
		overflow-y: auto;
	}

	.status table {
		width: 100%;
		border-collapse: collapse;
		font-size: 0.78rem;
		color: #c0c0c0;
	}

	.status thead th {
		position: sticky;
		top: 0;
		background: #0a0f18;
		z-index: 1;
	}

	.status th,
	.status td {
		text-align: left;
		padding: 0.3rem 0.5rem;
		border-bottom: 1px solid #1a2330;
	}

	.status th {
		font-weight: 600;
		color: #e0e0e0;
	}

	.status td {
		font-variant-numeric: tabular-nums;
	}
</style>
