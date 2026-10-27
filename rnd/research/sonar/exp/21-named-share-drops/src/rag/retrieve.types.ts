import type { ChunkRecord } from "./db.ts";

export interface RetrievedChunk extends ChunkRecord {
  /** Ranking score: after fusion, a normalized weighted sum, only meaningful relative to other chunks. */
  score: number;
  matchType: "lexical" | "semantic" | "hybrid";
  /**
   * Cosine similarity between the question's embedding and this chunk's (bge-small), when known:
   * the one number here that means the same thing for every question. gateByRelevance
   * (src/rag/pure.ts) decides on it, and the sources list shows it.
   */
  similarity?: number;
  /**
   * Format-2 packs only: the passage's section tells what to do (Treatment, First aid, Management, During…).
   * false for a lead or a background section; absent for sources without sections.
   */
  action?: boolean;
}
