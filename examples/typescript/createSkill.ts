/**
 * Create a new skill with categories and tags.
 */
import { SkillClient, SkillError } from '@ai-skill/sdk';

async function main(): Promise<number> {
  const baseUrl = process.env.SKILL_BASE_URL ?? 'http://localhost:8000';
  const email = process.env.SKILL_EMAIL ?? 'you@example.com';
  const password = process.env.SKILL_PASSWORD ?? 'SuperSecret123!';

  const client = new SkillClient({ baseUrl });
  await client.login({ email, password });

  // Look up the frontend category id
  const categories = await client.listCategories();
  const frontend = categories.find((c) => c.slug === 'frontend');
  if (!frontend) throw new Error('frontend category not found');
  console.log(`Frontend category: ${frontend.id}`);

  // Create the skill
  try {
    const skill = await client.createSkill({
      name: 'React useMemo deep-dive',
      slug: 'react-usememo-deep-dive',
      description: 'A practical guide to React useMemo with examples',
      content: '# React useMemo\n\nuseMemo lets you cache...',
      categoryId: frontend.id,
      tags: ['react', 'performance'],
      version: '1.0.0',
      isPublic: true,
    });
    console.log(`✓ Created skill: ${skill.slug}  id=${skill.id}`);
  } catch (e) {
    if (e instanceof SkillError && e.statusCode === 409) {
      console.log('… skill already exists');
    } else {
      throw e;
    }
  }
  return 0;
}

main().then((code) => process.exit(code));
