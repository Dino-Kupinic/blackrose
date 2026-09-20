/**
 * Chat handler that decides before (and after) a fake streamed reply.
 *
 * Run: npm install && npm start -- "your prompt"
 * Requires TYPESAFE_API_KEY in the environment.
 */

import { Guard } from "blackrose";

function requireApiKey(): string {
  const key = process.env.TYPESAFE_API_KEY?.trim() ?? "";
  if (!key) {
    console.error(
      "Missing TYPESAFE_API_KEY.\n" +
        "Set it in your environment (see repo .env.example), then re-run.\n" +
        "Example: export TYPESAFE_API_KEY=ts_...",
    );
    process.exit(1);
  }
  return key;
}

async function* fakeStreamReply(userMessage: string): AsyncGenerator<string> {
  const reply =
    `Thanks for your message. You asked about: ${JSON.stringify(userMessage.slice(0, 120))}. ` +
    "Here is a short demo reply from a fake model.";
  for (const word of reply.split(" ")) {
    yield `${word} `;
    await new Promise((r) => setTimeout(r, 30));
  }
}

async function handleChat(userMessage: string): Promise<void> {
  const apiKey = requireApiKey();
  const guard = new Guard({ apiKey });

  console.log(`user> ${userMessage}`);
  const inbound = await guard.checkInput(userMessage);
  console.log(`input verdict: ${inbound.verdict}`);
  if (inbound.reasons.length) console.log(`  reasons: ${JSON.stringify(inbound.reasons)}`);
  if (Object.keys(inbound.scores).length) {
    console.log(`  scores:  ${JSON.stringify(inbound.scores)}`);
  }

  if (inbound.verdict === "block") {
    console.log("assistant> [blocked] I can't help with that request.");
    return;
  }
  if (inbound.verdict === "review") {
    console.log("note> input flagged for human review; demo still generates.");
  }

  const chunks: string[] = [];
  process.stdout.write("assistant> ");
  for await (const chunk of fakeStreamReply(userMessage)) {
    process.stdout.write(chunk);
    chunks.push(chunk);
  }
  process.stdout.write("\n");

  const fullReply = chunks.join("").trim();
  const outbound = await guard.checkOutput(fullReply);
  console.log(`output verdict: ${outbound.verdict}`);
  if (outbound.reasons.length) console.log(`  reasons: ${JSON.stringify(outbound.reasons)}`);
  if (Object.keys(outbound.scores).length) {
    console.log(`  scores:  ${JSON.stringify(outbound.scores)}`);
  }

  if (outbound.verdict === "block") {
    console.log("note> reply withheld after output check.");
  } else if (outbound.verdict === "review") {
    console.log("note> reply shown but queued for human review.");
  }
}

const prompt = process.argv.slice(2).join(" ").trim() || "What is the capital of Austria?";
handleChat(prompt).catch((err) => {
  console.error(err);
  process.exit(1);
});
