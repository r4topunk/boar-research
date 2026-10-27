export const Platform = { OS: "node", select: (o: any) => o.node ?? o.default ?? o.native ?? o.ios };
export const NativeModules = {};
export default { Platform, NativeModules };
