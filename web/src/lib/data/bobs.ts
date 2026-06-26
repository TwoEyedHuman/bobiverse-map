import rawRecords from './bobs.json';

export interface BobRecord {
	bob: string;
	system: string;
	assumed_date: Date;
	dead?: boolean;
}

interface RawRecord {
	bob: string;
	system: string;
	assumed_date: string;
	dead?: boolean;
}

// Parity with app/data.py:25 (load_data) — parse dates, sort by (bob, assumed_date)
function loadData(): BobRecord[] {
	const records: BobRecord[] = (rawRecords as RawRecord[]).map((r) => ({
		bob: r.bob,
		system: r.system,
		assumed_date: new Date(r.assumed_date),
		dead: r.dead
	}));

	records.sort((a, b) => {
		if (a.bob !== b.bob) return a.bob < b.bob ? -1 : 1;
		return a.assumed_date.getTime() - b.assumed_date.getTime();
	});

	return records;
}

export const bobRecords: BobRecord[] = loadData();

export const minDate: Date = bobRecords.reduce(
	(min, r) => (r.assumed_date < min ? r.assumed_date : min),
	bobRecords[0].assumed_date
);

export const maxDate: Date = bobRecords.reduce(
	(max, r) => (r.assumed_date > max ? r.assumed_date : max),
	bobRecords[0].assumed_date
);
