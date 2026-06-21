// Ported from app/data.py:7 (SYSTEM_COORDS)
export const SYSTEM_COORDS: Record<string, [number, number]> = {
	Sol: [0, 0],
	'Alpha Centauri': [4.37, 0.2],
	'Epsilon Eridani': [10.5, -2.1],
	'Omicron Eridani': [16.2, -5.8],
	'Delta Eridani': [29.5, 4.2],
	'82 Eridani': [19.7, -5.0],
	'Beta Hydri': [24.3, -14.5],
	'Sigma Draconis': [18.8, 12.1],
	'Tau Ceti': [11.9, -1.5],
	'Epsilon Indi': [11.8, -2.5]
};

export function getCoords(systemName: string): [number, number] {
	return SYSTEM_COORDS[systemName] ?? [0, 0];
}
