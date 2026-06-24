<script lang="ts">
	import { SYSTEM_COORDS } from './data/coords';
	import type { JitteredPosition } from './data/positions';

	// All bobs share one color (markers, labels, paths), distinct from the
	// grey star labels / white star markers.
	const BOB_COLOR = '#ffb454';

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

	function roundTo(value: number, digits: number): number {
		const factor = 10 ** digits;
		return Math.round(value * factor) / factor;
	}

	interface BobMarker {
		name: string;
		px: number;
		py: number;
		traveling: boolean;
		angle: number;
	}
	interface ClusterMarker {
		px: number;
		py: number;
		count: number;
		names: string[];
	}

	// Split into individually-labeled bobs vs. dense clusters. Travelers and
	// lone stationary bobs get a marker + name label. Co-located stationary bobs
	// (e.g. the whole crew parked at 82 Eridani) collapse to one marker with a
	// count badge — names show on hover — so the map doesn't scatter a ring of
	// labels around the star.
	const render = $derived.by(() => {
		const bobs: BobMarker[] = [];
		const stationaryGroups = new Map<string, JitteredPosition[]>();

		for (const p of positions) {
			if (p.isTraveling) {
				bobs.push({
					name: p.name,
					px: scaleX(p.displayX),
					py: scaleY(p.displayY),
					traveling: true,
					angle: p.angle
				});
			} else {
				const key = `${roundTo(p.x, 2)},${roundTo(p.y, 2)}`;
				const g = stationaryGroups.get(key);
				if (g) g.push(p);
				else stationaryGroups.set(key, [p]);
			}
		}

		const clusters: ClusterMarker[] = [];
		for (const g of stationaryGroups.values()) {
			// Anchor at the true system center, not the orbit-jittered position.
			const px = scaleX(g[0].x);
			const py = scaleY(g[0].y);
			if (g.length === 1) {
				bobs.push({ name: g[0].name, px, py, traveling: false, angle: 0 });
			} else {
				clusters.push({ px, py, count: g.length, names: g.map((b) => b.name) });
			}
		}

		return { bobs, clusters };
	});

	// Label de-collision. In-transit bobs interpolate freely, so their name
	// labels can land on top of each other. Greedily stack any colliding label
	// upward by a line.
	const LABEL_DX = 46; // px horizontal proximity that counts as a collision
	const LABEL_DY = 13; // line height to bump a colliding label
	const labelDy = $derived.by(() => {
		const placed: { x: number; y: number }[] = [];
		const offsets = new Map<string, number>();
		for (const b of render.bobs) {
			const baseY = b.py - 12;
			let y = baseY;
			while (placed.some((q) => Math.abs(q.x - b.px) < LABEL_DX && Math.abs(q.y - y) < LABEL_DY)) {
				y -= LABEL_DY;
			}
			placed.push({ x: b.px, y });
			offsets.set(b.name, y - baseY);
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
					stroke={BOB_COLOR}
					stroke-width="1.5"
					stroke-dasharray="4 4"
				/>
			{/if}
		{/each}
	</g>

	<!-- Bobs: travelers (triangle) + lone stationary (square), each labeled -->
	<g class="bobs">
		{#each render.bobs as b (b.name)}
			<g transform={`translate(${b.px}, ${b.py})`}>
				{#if b.traveling}
					<path d={TRI} transform={`rotate(${b.angle})`} fill={BOB_COLOR} />
				{:else}
					<rect x="-4" y="-4" width="8" height="8" fill={BOB_COLOR} />
				{/if}
				<text
					class="bob-label"
					y={-12 + (labelDy.get(b.name) ?? 0)}
					text-anchor="middle"
					fill={BOB_COLOR}
				>
					{b.name}
				</text>
			</g>
		{/each}
	</g>

	<!-- Dense stationary clusters: one marker + count badge, names on hover -->
	<g class="clusters">
		{#each render.clusters as c (`${c.px},${c.py}`)}
			<g class="cluster" transform={`translate(${c.px}, ${c.py})`}>
				<title>{c.names.join('\n')}</title>
				<rect x="-5" y="-5" width="10" height="10" fill={BOB_COLOR} />
				<text class="cluster-badge" x="8" y="-3" fill={BOB_COLOR}>{c.count}</text>
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

	.cluster {
		cursor: help;
	}

	.cluster-badge {
		font-size: 11px;
		font-weight: 700;
	}
</style>
