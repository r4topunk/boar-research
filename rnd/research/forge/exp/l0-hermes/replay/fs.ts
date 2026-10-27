// expo-file-system/legacy stub for the replay: the g75 kit's two packs exist with their real sizes; nothing is read.
export const documentDirectory = "file:///app/";
export const cacheDirectory = "file:///app/cache/";
export const EncodingType = { UTF8: "utf8", Base64: "base64" };
const SIZES: Record<string, number> = { "boar-crypto.sqlite": 36093952, "boar-wikivoyage-en.sqlite": 351092736, "embedding.gguf": 36806944 };
export async function getInfoAsync(uri: string) {
  const n = uri.split("/").pop()!;
  return { exists: true, isDirectory: false, size: SIZES[n] ?? 1, modificationTime: 0, uri };
}
export async function readDirectoryAsync(uri: string) { return uri.endsWith("corpus/") ? Object.keys(SIZES).filter((n) => n.endsWith(".sqlite")) : []; }
const no = async () => { throw new Error("fs stub"); };
export const readAsStringAsync = no, writeAsStringAsync = no, copyAsync = no, moveAsync = no, downloadAsync = no;
export const makeDirectoryAsync = async () => {}, deleteAsync = async () => {};
export async function getFreeDiskStorageAsync() { return 50e9; }
export function createDownloadResumable() { throw new Error("fs stub"); }
export default { documentDirectory, cacheDirectory, EncodingType, getInfoAsync, readDirectoryAsync, readAsStringAsync, writeAsStringAsync, makeDirectoryAsync, deleteAsync, copyAsync, moveAsync, getFreeDiskStorageAsync, downloadAsync, createDownloadResumable };
