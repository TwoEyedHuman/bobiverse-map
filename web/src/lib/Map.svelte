<script lang="ts">
	import { SYSTEM_COORDS } from './data/coords';
	import type { JitteredPosition } from './data/positions';
	import { colorForBob } from './colors';

	let { positions }: { positions: JitteredPosition[] } = $props();

	// SVG canvas (rendered responsively via viewBox + preserveAspectRatio).
	const WIDTH = 960;
	const HEIGHT = 720;
	const MARGIN = { top: 24, right: 24, bottom: 24, left: 24 };
	const innerW = WIDTH - MARGIN.left - MARGIN.right;
	const innerH = HEIGHT - MARGIN.top - MARGIN.bottom;

	// Domain from the star-system hull (+padding). Bobs interpolate between
	// systems so they stay inside this range — keeps axes stable over time.
	const xsCoords = Object.values(SYSTEM_COORDS).map((c) => c[0]);
	const ysCoords = Object.values(SYSTEM_COORDS).map((c) => c[1]);
	const padX = (Math.max(...xsCoords) - Math.min(...xsCoords)) * 0.08;
	const padY = (Math.max(...ysCoords) - Math.min(...ysCoords)) * 0.08;
	const xMin = Math.min(...xsCoords) - padX;
	const xMax = Math.max(...xsCoords) + padX;
	const yMin = Math.min(...ysCoords) - padY;
	const yMax = Math.max(...ysCoords) + padY;

	// Linear scales (data → pixel). Y is inverted: data grows up, SVG grows down.
	const scaleX = (x: number) => MARGIN.left + ((x - xMin) / (xMax - xMin)) * innerW;
	const scaleY = (y: number) => MARGIN.top + ((yMax - y) / (yMax - yMin)) * innerH;

	const systems = Object.entries(SYSTEM_COORDS);

	// Triangle-up marker (points up by default), centered on origin; rotated by
	// `angle` degrees clockwise to face the direction of travel.
	const TRI = 'M 0,-8 L 7,6 L -7,6 Z';

	// Label de-collision. In-transit bobs interpolate freely and aren't orbit-
	// jittered like co-located stationary ones, so their name labels can land on
	// top of each other. Greedily stack any colliding label upward by a line.
	const LABEL_DX = 46; // px horizontal proximity that counts as a collision
	const LABEL_DY = 13; // line height to bump a colliding label
	const labelDy = $derived.by(() => {
		const placed: { x: number; y: number }[] = [];
		const offsets = new Map<string, number>();
		for (const p of positions) {
			const px = scaleX(p.displayX);
			const baseY = scaleY(p.displayY) - 12;
			let y = baseY;
			while (placed.some((q) => Math.abs(q.x - px) < LABEL_DX && Math.abs(q.y - y) < LABEL_DY)) {
				y -= LABEL_DY;
			}
			placed.push({ x: px, y });
			offsets.set(p.name, y - baseY);
		}
		return offsets;
	});
</script>

<svg
	class="map"
	viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
	preserveAspectRatio="xMidYMid meet"
	role="img"
	aria-label="Bobiverse tactical movement map"
>
	<rect x="0" y="0" width={WIDTH} height={HEIGHT} fill="#111111" />

	<!-- Star systems -->
	<g class="systems">
		{#each systems as [name, coords] (name)}
			<circle cx={scaleX(coords[0])} cy={scaleY(coords[1])} r="6" fill="#ffffff" opacity="0.3" />
			<text class="system-label" x={scaleX(coords[0])} y={scaleY(coords[1]) + 18} text-anchor="middle">
				{name}
			</text>
		{/each}
	</g>

	<!-- Travel paths (dotted, in each bob's color) -->
	<g class="paths">
		{#each positions as p (p.name)}
			{#if p.path}
				<line
					x1={scaleX(p.path.x[0])}
					y1={scaleY(p.path.y[0])}
					x2={scaleX(p.path.x[1])}
					y2={scaleY(p.path.y[1])}
					stroke={colorForBob(p.name)}
					stroke-width="1.5"
					stroke-dasharray="4 4"
				/>
			{/if}
		{/each}
	</g>

	<!-- Bobs (rotated heading triangle + label) -->
	<g class="bobs">
		{#each positions as p (p.name)}
			<g transform={`translate(${scaleX(p.displayX)}, ${scaleY(p.displayY)})`}>
				{#if p.isTraveling}
					<path d={TRI} transform={`rotate(${p.angle})`} fill={colorForBob(p.name)} />
				{:else}
					<rect x="-6" y="-6" width="12" height="12" fill={colorForBob(p.name)} />
				{/if}
				<text
					class="bob-label"
					y={-12 + (labelDy.get(p.name) ?? 0)}
					text-anchor="middle"
					fill={colorForBob(p.name)}
				>
					{p.name}
				</text>
			</g>
		{/each}
	</g>
</svg>

<style>
	.map {
		width: 100%;
		height: 100%;
		display: block;
	}

	.system-label {
		fill: #888888;
		font-size: 11px;
	}

	.bob-label {
		font-size: 12px;
		font-weight: 600;
	}
</style>
