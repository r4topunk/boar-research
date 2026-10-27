// ram-monitor on Node for the exp-06 desktop answerer: the device's RAM is SIMULATED (KILN_RAM_BYTES), so the app's
// own code (defaultContextSize, model picking, low-RAM rules) decides as it would on that phone. Memory info is the
// Node process's (it is not the phone's footprint).
const total = () => Number(process.env.KILN_RAM_BYTES || 8 * 1024 ** 3);
export function getDeviceTotalRamBytes() { return total(); }
export function getAvailableRamBytes() { return Math.round(total() * Number(process.env.KILN_RAM_AVAILABLE_FRACTION || 0.5)); }
export function getMemoryInfo() { const m = process.memoryUsage(); return { rssBytes: m.rss, totalPssBytes: m.rss }; }
export default { getDeviceTotalRamBytes, getAvailableRamBytes, getMemoryInfo };
