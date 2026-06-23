import { getCoords } from './coords';
import type { BobRecord } from './bobs';

export interface Position {
	name: string;
	x: number;
	y: number;
	angle: number;
	status: string;
	isTraveling: boolean;
	lastDate: Date;
	path: { x: [number, number]; y: [number, number] } | null;
}

export interface JitteredPosition extends Position {
	displayX: number;
	displayY: number;
}

// Parity with app/data.py:35 (compute_positions)
export function computePositions(records: BobRecord[], selectedDate: Date): Position[] {
	const bobOrder: string[] = [];
	const byBob = new Map<string, BobRecord[]>();
	for (const r of records) {
		if (!byBob.has(r.bob)) {
			byBob.set(r.bob, []);
			bobOrder.push(r.bob);
		}
		byBob.get(r.bob)!.push(r);
	}

	const positions: Position[] = [];

	for (const bob of bobOrder) {
		const bobData = byBob.get(bob)!;
		const past = bobData.filter((r) => r.assumed_date <= selectedDate);
		const future = bobData.filter((r) => r.assumed_date > selectedDate);

		if (past.length === 0) continue;

		const lastEntry = past[past.length - 1];
		const prevCoords = getCoords(lastEntry.system);

		let x = prevCoords[0];
		let y = prevCoords[1];
		let angle = 0;
		let isTraveling = false;
		let path: Position['path'] = null;
		let status: string;

		if (future.length > 0) {
			const nextEntry = future[0];
			const nextCoords = getCoords(nextEntry.system);

			if (nextEntry.system !== lastEntry.system) {
				isTraveling = true;
				const timeDiff = nextEntry.assumed_date.getTime() - lastEntry.assumed_date.getTime();
				const elapsed = selectedDate.getTime() - lastEntry.assumed_date.getTime();
				const fraction = timeDiff > 0 ? elapsed / timeDiff : 0;

				x = prevCoords[0] + (nextCoords[0] - prevCoords[0]) * fraction;
				y = prevCoords[1] + (nextCoords[1] - prevCoords[1]) * fraction;

				const dx = nextCoords[0] - prevCoords[0];
				const dy = nextCoords[1] - prevCoords[1];
				angle = 90 - (Math.atan2(dy, dx) * 180) / Math.PI;

				path = {
					x: [prevCoords[0], nextCoords[0]],
					y: [prevCoords[1], nextCoords[1]]
				};
				status = `Traveling to ${nextEntry.system}`;
			} else {
				status = `Stationary at ${lastEntry.system}`;
			}
		} else {
			status = `Stationary at ${lastEntry.system}`;
		}

		positions.push({
			name: bob,
			x,
			y,
			angle,
			status,
			isTraveling,
			lastDate: lastEntry.assumed_date,
			path
		});
	}

	return positions;
}

// Parity with app/map.py:32 (anti-stacking orbit jitter in build_map)
export function applyJitter(positions: Position[]): JitteredPosition[] {
	const clusters = new Map<string, Position[]>();
	for (const p of positions) {
		const key = `${roundTo(p.x, 2)},${roundTo(p.y, 2)}`;
		const cluster = clusters.get(key);
		if (cluster) cluster.push(p);
		else clusters.set(key, [p]);
	}

	const result: JitteredPosition[] = [];
	for (const cluster of clusters.values()) {
		const n = cluster.length;
		cluster.forEach((p, idx) => {
			let displayX = p.x;
			let displayY = p.y;

			if (n > 1 && !p.isTraveling) {
				const offsetRadius = 0.7;
				const theta = (2 * Math.PI * idx) / n;
				displayX += offsetRadius * Math.cos(theta);
				displayY += offsetRadius * Math.sin(theta);
			}

			result.push({ ...p, displayX, displayY });
		});
	}

	return result;
}

function roundTo(value: number, digits: number): number {
	const factor = 10 ** digits;
	return Math.round(value * factor) / factor;
}
