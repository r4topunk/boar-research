const total = () => 8 * 1024 ** 3;
export function getDeviceTotalRamBytes() { return total(); }
export function getAvailableRamBytes() { return total() / 2; }
export function getMemoryInfo() { return { rssBytes: 0, totalPssBytes: 0 }; }
export default { getDeviceTotalRamBytes, getAvailableRamBytes, getMemoryInfo };
