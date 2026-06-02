/**
 * Walk the full skill catalog page by page.
 */
import { SkillClient } from '@ai-skill/sdk';

async function main(): Promise<number> {
  const baseUrl = process.env.SKILL_BASE_URL ?? 'http://localhost:8000';
  const pageSize = 50;

  const client = new SkillClient({ baseUrl });
  let total = 0;
  for await (const skill of client.iterSkills({ pageSize, isPublic: true })) {
    total += 1;
    if (total <= 5 || total % 100 === 0) {
      console.log(`  [${String(total).padStart(5)}]  ${skill.slug}  (${skill.name})`);
    }
  }
  console.log(`\nTotal public skills: ${total}`);
  return 0;
}

main().then((code) => process.exit(code));
