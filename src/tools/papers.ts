interface ArxivPaper {
  id: string;
  title: string;
  summary: string;
  published: string;
  updated: string;
  authors: string[];
  absUrl: string;
  pdfUrl: string;
}

const ARXIV_API = "https://export.arxiv.org/api/query";

export async function searchPapers(query: string, maxResults = 5): Promise<string> {
  const url = `${ARXIV_API}?search_query=all:${encodeURIComponent(query)}&start=0&max_results=${maxResults}`;
  const response = await fetch(url, {
    headers: {
      "user-agent": "zarathustra/0.1.0 (paper search)",
    },
  });

  if (!response.ok) {
    throw new Error(`ArXiv search failed: ${response.status} ${response.statusText}`);
  }

  const xml = await response.text();
  const papers = parseEntries(xml);
  return JSON.stringify(
    {
      query,
      source: "arxiv",
      count: papers.length,
      papers,
    },
    null,
    2,
  );
}

export async function fetchPaper(urlOrId: string): Promise<string> {
  const id = normalizeArxivId(urlOrId);
  const url = `${ARXIV_API}?id_list=${encodeURIComponent(id)}`;
  const response = await fetch(url, {
    headers: {
      "user-agent": "zarathustra/0.1.0 (paper fetch)",
    },
  });

  if (!response.ok) {
    throw new Error(`ArXiv fetch failed: ${response.status} ${response.statusText}`);
  }

  const xml = await response.text();
  const papers = parseEntries(xml);
  const paper = papers[0];

  if (!paper) {
    throw new Error(`No paper found for ${urlOrId}`);
  }

  return JSON.stringify(
    {
      source: "arxiv",
      paper,
    },
    null,
    2,
  );
}

function parseEntries(xml: string): ArxivPaper[] {
  const entries = xml.match(/<entry>([\s\S]*?)<\/entry>/g) ?? [];
  return entries.map((entry) => parseEntry(entry)).filter((paper): paper is ArxivPaper => paper !== null);
}

function parseEntry(entry: string): ArxivPaper | null {
  const id = extractTag(entry, "id");
  const title = cleanText(extractTag(entry, "title"));
  const summary = cleanText(extractTag(entry, "summary"));
  const published = extractTag(entry, "published");
  const updated = extractTag(entry, "updated");
  const authors = [...entry.matchAll(/<name>([\s\S]*?)<\/name>/g)].map((match) => cleanText(match[1] ?? ""));

  if (!id || !title) {
    return null;
  }

  const absUrl = id.trim();
  const normalizedId = normalizeArxivId(absUrl);

  return {
    id: normalizedId,
    title,
    summary,
    published,
    updated,
    authors,
    absUrl,
    pdfUrl: `https://arxiv.org/pdf/${normalizedId}.pdf`,
  };
}

function extractTag(input: string, tagName: string): string {
  const match = input.match(new RegExp(`<${tagName}>([\\s\\S]*?)<\\/${tagName}>`));
  return decodeXml(match?.[1] ?? "").trim();
}

function cleanText(input: string): string {
  return decodeXml(input).replace(/\s+/g, " ").trim();
}

function decodeXml(input: string): string {
  return input
    .replaceAll("&lt;", "<")
    .replaceAll("&gt;", ">")
    .replaceAll("&amp;", "&")
    .replaceAll("&quot;", "\"")
    .replaceAll("&#39;", "'");
}

function normalizeArxivId(urlOrId: string): string {
  const trimmed = urlOrId.trim();
  const urlMatch = trimmed.match(/arxiv\.org\/abs\/([^?#]+)/) ?? trimmed.match(/arxiv\.org\/pdf\/([^?#]+?)(?:\.pdf)?$/);
  return (urlMatch?.[1] ?? trimmed).replace(/\.pdf$/, "");
}
