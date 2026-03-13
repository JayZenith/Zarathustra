#!/usr/bin/env bun
import { MemoryRepo } from "../memory/repo.js";
import { attachCommand } from "./commands/attach.js";
import { runCommand } from "./commands/run.js";
import { statusCommand } from "./commands/status.js";
import { tuiCommand } from "./commands/tui.js";
import { dbCommand } from "./commands/db.js";
import { paperSearchCommand } from "./commands/paper_search.js";
import { paperFetchCommand } from "./commands/paper_fetch.js";

async function main(): Promise<void> {
  const [, , command, ...args] = process.argv;
  const repo = new MemoryRepo();

  switch (command) {
    case "attach":
      requireArg(args[0], "attach requires a target config path");
      await attachCommand(repo, args[0]!);
      break;
    case "run":
      requireArg(args[0], "run requires a target name");
      await runCommand(repo, args[0]!, args[1] ? Number(args[1]) : undefined);
      break;
    case "status":
      statusCommand(repo);
      break;
    case "tui":
      tuiCommand(repo);
      break;
    case "db":
      requireArg(args[0], "db requires a SQL string");
      dbCommand(repo, args[0]!);
      break;
    case "paper-search":
      requireArg(args[0], "paper-search requires a query");
      await paperSearchCommand(args.join(" "));
      break;
    case "paper-fetch":
      requireArg(args[0], "paper-fetch requires an arXiv URL or id");
      await paperFetchCommand(args[0]!);
      break;
    default:
      printHelp();
  }
}

function requireArg(value: string | undefined, message: string): asserts value is string {
  if (!value) {
    throw new Error(message);
  }
}

function printHelp(): void {
  process.stdout.write(
    [
      "zarathustra",
      "",
      "commands:",
      "  attach <target.yaml>",
      "  run <target-name> [max-cycles]",
      "  status",
      "  tui",
      "  db \"<sql>\"",
      "  paper-search <query>",
      "  paper-fetch <url-or-id>"
    ].join("\n") + "\n",
  );
}

await main();
