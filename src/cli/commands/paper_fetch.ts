import { fetchPaper } from "../../tools/papers.js";

export async function paperFetchCommand(urlOrId: string): Promise<void> {
  const output = await fetchPaper(urlOrId);
  process.stdout.write(`${output}\n`);
}
