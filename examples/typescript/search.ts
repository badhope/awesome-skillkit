/**
 * Run a semantic search and pretty-print the top results.
 */
import { SkillClient } from '@ai-skill/sdk';

async function main(): Promise<number> {
  const baseUrl = process.env.SKILL_BASE_URL ?? 'http://localhost:8000';
  const query = process.argv[2] ?? 'React performance optimization hooks';
  const limit = Number(process.argv[3] ?? 10);

  const client = new SkillClient({ baseUrl });
  const results = await client.searchSkills({ query, limit, minScore: 0.5 });

  if (results.items.length === 0) {
    console.log(`No matches for ${JSON.stringify(query)}.`);
    return 0;
  }

  console.log(`Top ${results.items.length} results for ${JSON.stringify(query)}:\n`);
  for (const r of results.items) {
    const score = r.score !== undefined ? r.score.toFixed(3) : '  - ';
    console.log(`  ${score}  ${r.skill.name}  (${r.skill.slug})`);
    console.log(`          ${r.skill.description.slice(0, 100)}`);
    console.log();
  }
  return 0;
}

main().then((code) => process.exit(code));
