<script lang="ts">
	import { SYSTEM_COORDS } from './data/coords';
	import type { JitteredPosition } from './data/positions';
	import { colorForBob } from './colors';

	let { positions }: { positions: JitteredPosition[] } = $props();

	// SVG canvas (rendered responsively via viewBox + preserveAspectRatio).
	const WIDTH = 960;
	const HEIGHT = 720;
	const MARGIN = { top: 24, right: 24, bottom: 48, left: 60 };
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

	function ticks(min: number, max: number, count: number): number[] {
		const span = max - min;
		if (span <= 0) return [min];
		let step = 10 ** Math.floor(Math.log10(span / count));
		const err = span / count / step;
		if (err >= 7.5) step *= 10;
		else if (err >= 3.5) step *= 5;
		else if (err >= 1.5) step *= 2;
		const start = Math.ceil(min / step) * step;
		const out: number[] = [];
		for (let v = start; v <= max + step * 1e-9; v += step) {
			out.push(Math.round(v / step) * step);
		}
		return out;
	}

	const xTicks = $derived(ticks(xMin, xMax, 8));
	const yTicks = $derived(ticks(yMin, yMax, 6));

	const systems = Object.entries(SYSTEM_COORDS);

	// Triangle-up marker (points up by default), centered on origin; rotated by
	// `angle` degrees clockwise to face the direction of travel.
	const TRI = 'M 0,-8 L 7,6 L -7,6 Z';
</script>

<svg
	class="map"
	viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
	preserveAspectRatio="xMidYMid meet"
	role="img"
	aria-label="Bobiverse tactical movement map"
>
	<rect x="0" y="0" width={WIDTH} height={HEIGHT} fill="#111111" />

	<!-- Gridlines -->
	<g class="grid">
		{#each xTicks as tx (tx)}
			<line x1={scaleX(tx)} y1={MARGIN.top} x2={scaleX(tx)} y2={MARGIN.top + innerH} />
		{/each}
		{#each yTicks as ty (ty)}
			<line x1={MARGIN.left} y1={scaleY(ty)} x2={MARGIN.left + innerW} y2={scaleY(ty)} />
		{/each}
	</g>

	<!-- Axes -->
	<g class="axis">
		<line x1={MARGIN.left} y1={MARGIN.top + innerH} x2={MARGIN.left + innerW} y2={MARGIN.top + innerH} />
		<line x1={MARGIN.left} y1={MARGIN.top} x2={MARGIN.left} y2={MARGIN.top + innerH} />
		{#each xTicks as tx (tx)}
			<text x={scaleX(tx)} y={MARGIN.top + innerH + 18} text-anchor="middle">{tx}</text>
		{/each}
		{#each yTicks as ty (ty)}
			<text x={MARGIN.left - 8} y={scaleY(ty) + 4} text-anchor="end">{ty}</text>
		{/each}
		<text class="axis-title" x={MARGIN.left + innerW / 2} y={HEIGHT - 8} text-anchor="middle">
			LY (X)
		</text>
		<text
			class="axis-title"
			x={16}
			y={MARGIN.top + innerH / 2}
			text-anchor="middle"
			transform={`rotate(-90, 16, ${MARGIN.top + innerH / 2})`}
		>
			LY (Y)
		</text>
	</g>

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
				<path d={TRI} transform={`rotate(${p.angle})`} fill={colorForBob(p.name)} />
				<text class="bob-label" y="-12" text-anchor="middle" fill={colorForBob(p.name)}>
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

	.grid line {
		stroke: #333333;
		stroke-width: 1;
	}

	.axis line {
		stroke: #555555;
		stroke-width: 1;
	}

	.axis text {
		fill: #aaaaaa;
		font-size: 12px;
	}

	.axis-title {
		fill: #cccccc;
		font-size: 13px;
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
