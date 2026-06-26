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
	'Tau Ceti': [14.5, -0.3],
	'Epsilon Indi': [14.2, -3.2],
	'Eta Cassiopeiae': [19.4, -1.8],
	'Delta Pavonis': [19.9, -10.6],
	'Zeta Tucanae': [28.0, -20.5],
	'Gamma Pavonis': [30.2, -16.5],
	'Gliese 54': [20.3, -7.0],
	'Gliese 877': [23.5, -8.0],
	'HIP 14101': [49.3, 8.5]
};

export function getCoords(systemName: string): [number, number] {
	return SYSTEM_COORDS[systemName] ?? [0, 0];
}
