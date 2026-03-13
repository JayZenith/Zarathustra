import { searchPapers } from "../../tools/papers.js";

export async function paperSearchCommand(query: string): Promise<void> {
  const output = await searchPapers(query);
  process.stdout.write(`${output}\n`);
}
