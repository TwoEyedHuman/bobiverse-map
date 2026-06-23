import { bobRecords } from './data/bobs';

// Plotly default qualitative colorway (used by plotly_dark template).
// Parity with per-trace color cycling in app/map.py:66 (Bob icon traces).
export const PLOTLY_COLORWAY = [
	'#636efa',
	'#EF553B',
	'#00cc96',
	'#ab63fa',
	'#FFA15A',
	'#19d3f3',
	'#FF6692',
	'#B6E880',
	'#FF97FF',
	'#FECB52'
];

// Stable bob → color map keyed on first-appearance order in the data, so a
// bob keeps its color as the timeline moves. Colors cycle past 10 bobs,
// matching Plotly's colorway wraparound.
export const bobColors: Map<string, string> = (() => {
	const map = new Map<string, string>();
	let idx = 0;
	for (const r of bobRecords) {
		if (!map.has(r.bob)) {
			map.set(r.bob, PLOTLY_COLORWAY[idx % PLOTLY_COLORWAY.length]);
			idx += 1;
		}
	}
	return map;
})();

export function colorForBob(bob: string): string {
	return bobColors.get(bob) ?? PLOTLY_COLORWAY[0];
}
