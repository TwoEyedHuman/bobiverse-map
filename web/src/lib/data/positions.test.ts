import { describe, expect, it } from 'vitest';
import { bobRecords } from './bobs';
import { applyJitter, computePositions } from './positions';

// Fixtures generated from app/data.py:compute_positions + app/map.py:build_map's
// jitter logic against the same data/bobs.json, to assert JS/Python parity.
const FIXTURES: Record<
	string,
	Array<{
		name: string;
		x: number;
		y: number;
		angle: number;
		status: string;
		is_traveling: boolean;
		last_date: string;
		path: [[number, number], [number, number]] | null;
		display_x: number;
		display_y: number;
	}>
> = {
	'2150-06-15': [
		{
			name: 'Bill',
			x: 10.5,
			y: -2.1,
			angle: 0,
			status: 'Stationary at Epsilon Eridani',
			is_traveling: false,
			last_date: '2145-12-01',
			path: null,
			display_x: 11.2,
			display_y: -2.1
		},
		{
			name: 'Garfield',
			x: 10.5,
			y: -2.1,
			angle: 0,
			status: 'Stationary at Epsilon Eridani',
			is_traveling: false,
			last_date: '2145-12-01',
			path: null,
			display_x: 9.8,
			display_y: -2.1
		},
		{
			name: 'Bob',
			x: 15.267119,
			y: -0.519324,
			angle: 71.655566,
			status: 'Traveling to Delta Eridani',
			is_traveling: true,
			last_date: '2145-07-01',
			path: [
				[10.5, 29.5],
				[-2.1, 4.2]
			],
			display_x: 15.267119,
			display_y: -0.519324
		},
		{
			name: 'Homer',
			x: 6.203013,
			y: -1.240603,
			angle: -78.690068,
			status: 'Traveling to Sol',
			is_traveling: true,
			last_date: '2145-12-01',
			path: [
				[10.5, 0],
				[-2.1, 0]
			],
			display_x: 6.203013,
			display_y: -1.240603
		},
		{
			name: 'Mario',
			x: 13.339377,
			y: -4.651324,
			angle: 131.941302,
			status: 'Traveling to Beta Hydri',
			is_traveling: true,
			last_date: '2145-07-01',
			path: [
				[10.5, 24.3],
				[-2.1, -14.5]
			],
			display_x: 13.339377,
			display_y: -4.651324
		},
		{
			name: 'Milo',
			x: 14.534806,
			y: -4.719085,
			angle: 122.988522,
			status: 'Traveling to Omicron Eridani',
			is_traveling: true,
			last_date: '2145-07-01',
			path: [
				[10.5, 16.2],
				[-2.1, -5.8]
			],
			display_x: 14.534806,
			display_y: -4.719085
		},
		{
			name: 'Riker',
			x: 5.977154,
			y: -1.195431,
			angle: -78.690068,
			status: 'Traveling to Sol',
			is_traveling: true,
			last_date: '2145-07-01',
			path: [
				[10.5, 0],
				[-2.1, 0]
			],
			display_x: 5.977154,
			display_y: -1.195431
		}
	],
	'2160-01-01': [
		{
			name: 'Arthur',
			x: 0,
			y: 0,
			angle: 0,
			status: 'Stationary at Sol',
			is_traveling: false,
			last_date: '2158-03-01',
			path: null,
			display_x: 0.7,
			display_y: 0.0
		},
		{
			name: 'Charles',
			x: 0,
			y: 0,
			angle: 0,
			status: 'Stationary at Sol',
			is_traveling: false,
			last_date: '2158-01-01',
			path: null,
			display_x: 0.0,
			display_y: 0.7
		},
		{
			name: 'Homer',
			x: 0,
			y: 0,
			angle: 0,
			status: 'Stationary at Sol',
			is_traveling: false,
			last_date: '2158-09-01',
			path: null,
			display_x: -0.7,
			display_y: 0.0
		},
		{
			name: 'Riker',
			x: 0,
			y: 0,
			angle: 0,
			status: 'Stationary at Sol',
			is_traveling: false,
			last_date: '2158-11-01',
			path: null,
			display_x: -0.0,
			display_y: -0.7
		},
		{
			name: 'Bill',
			x: 10.5,
			y: -2.1,
			angle: 0,
			status: 'Stationary at Epsilon Eridani',
			is_traveling: false,
			last_date: '2158-10-01',
			path: null,
			display_x: 11.2,
			display_y: -2.1
		},
		{
			name: 'Garfield',
			x: 10.5,
			y: -2.1,
			angle: 0,
			status: 'Stationary at Epsilon Eridani',
			is_traveling: false,
			last_date: '2145-12-01',
			path: null,
			display_x: 10.15,
			display_y: -1.493782
		},
		{
			name: 'Goku',
			x: 10.5,
			y: -2.1,
			angle: 0,
			status: 'Stationary at Epsilon Eridani',
			is_traveling: false,
			last_date: '2150-09-01',
			path: null,
			display_x: 10.15,
			display_y: -2.706218
		},
		{
			name: 'Bob',
			x: 24.451067,
			y: 2.52588,
			angle: 71.655566,
			status: 'Traveling to Delta Eridani',
			is_traveling: true,
			last_date: '2145-07-01',
			path: [
				[10.5, 29.5],
				[-2.1, 4.2]
			],
			display_x: 24.451067,
			display_y: 2.52588
		},
		{
			name: 'Calvin',
			x: 6.154571,
			y: -0.469578,
			angle: -69.433712,
			status: 'Traveling to Alpha Centauri',
			is_traveling: true,
			last_date: '2150-09-01',
			path: [
				[10.5, 4.37],
				[-2.1, 0.2]
			],
			display_x: 6.154571,
			display_y: -0.469578
		},
		{
			name: 'Linus',
			x: 11.332088,
			y: -2.356027,
			angle: 107.102729,
			status: 'Traveling to Epsilon Indi',
			is_traveling: true,
			last_date: '2150-09-01',
			path: [
				[10.5, 11.8],
				[-2.1, -2.5]
			],
			display_x: 11.332088,
			display_y: -2.356027
		},
		{
			name: 'Mario',
			x: 18.809492,
			y: -9.5665,
			angle: 131.941302,
			status: 'Traveling to Beta Hydri',
			is_traveling: true,
			last_date: '2145-07-01',
			path: [
				[10.5, 24.3],
				[-2.1, -14.5]
			],
			display_x: 18.809492,
			display_y: -9.5665
		},
		{
			name: 'Milo',
			x: 18.13635,
			y: -5.357406,
			angle: 77.124998,
			status: 'Traveling to 82 Eridani',
			is_traveling: true,
			last_date: '2153-02-01',
			path: [
				[16.2, 19.7],
				[-5.8, -5.0]
			],
			display_x: 18.13635,
			display_y: -5.357406
		}
	],
	'2133-06-01': [
		{
			name: 'Bob',
			x: 0,
			y: 0,
			angle: 0,
			status: 'Stationary at Sol',
			is_traveling: false,
			last_date: '2133-06-01',
			path: null,
			display_x: 0,
			display_y: 0
		}
	]
};

const TOLERANCE = 1e-5;

function check(jittered: ReturnType<typeof applyJitter>, dateKey: string) {
	const expected = FIXTURES[dateKey];
	expect(jittered).toHaveLength(expected.length);

	const byName = new Map(jittered.map((p) => [p.name, p]));

	for (const exp of expected) {
		const actual = byName.get(exp.name);
		expect(actual, `missing position for ${exp.name}`).toBeDefined();
		if (!actual) continue;

		expect(actual.x).toBeCloseTo(exp.x, 5);
		expect(actual.y).toBeCloseTo(exp.y, 5);
		expect(actual.angle).toBeCloseTo(exp.angle, 5);
		expect(actual.status).toBe(exp.status);
		expect(actual.isTraveling).toBe(exp.is_traveling);
		expect(actual.lastDate.toISOString().slice(0, 10)).toBe(exp.last_date);
		expect(actual.displayX).toBeCloseTo(exp.display_x, 5);
		expect(actual.displayY).toBeCloseTo(exp.display_y, 5);

		if (exp.path === null) {
			expect(actual.path).toBeNull();
		} else {
			expect(actual.path).not.toBeNull();
			expect(actual.path!.x[0]).toBeCloseTo(exp.path[0][0], TOLERANCE);
			expect(actual.path!.x[1]).toBeCloseTo(exp.path[0][1], TOLERANCE);
			expect(actual.path!.y[0]).toBeCloseTo(exp.path[1][0], TOLERANCE);
			expect(actual.path!.y[1]).toBeCloseTo(exp.path[1][1], TOLERANCE);
		}
	}
}

describe('computePositions + applyJitter (parity with Python)', () => {
	it.each(Object.keys(FIXTURES))('matches Python output for %s', (dateKey) => {
		const positions = computePositions(bobRecords, new Date(dateKey));
		const jittered = applyJitter(positions);
		check(jittered, dateKey);
	});

	it('interpolates a traveling bob with correct heading angle', () => {
		const positions = computePositions(bobRecords, new Date('2150-06-15'));
		const bob = positions.find((p) => p.name === 'Bob');
		expect(bob).toBeDefined();
		expect(bob!.isTraveling).toBe(true);
		expect(bob!.angle).toBeCloseTo(71.655566, 5);
	});

	it('gives co-located stationary bobs distinct jittered positions', () => {
		const positions = computePositions(bobRecords, new Date('2160-01-01'));
		const jittered = applyJitter(positions);
		const atSol = jittered.filter((p) => p.x === 0 && p.y === 0);
		const displayCoords = atSol.map((p) => `${p.displayX.toFixed(4)},${p.displayY.toFixed(4)}`);
		expect(new Set(displayCoords).size).toBe(atSol.length);
	});
});
