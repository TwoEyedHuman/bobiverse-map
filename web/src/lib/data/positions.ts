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
