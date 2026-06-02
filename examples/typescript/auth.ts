/**
 * Register, log in, and read the current user with the TypeScript SDK.
 */
import { SkillClient, SkillError } from '@ai-skill/sdk';

async function main(): Promise<number> {
  const baseUrl = process.env.SKILL_BASE_URL ?? 'http://localhost:8000';
  const email = process.env.SKILL_EMAIL ?? 'you@example.com';
  const password = process.env.SKILL_PASSWORD ?? 'SuperSecret123!';

  const client = new SkillClient({ baseUrl });

  // 1. Register (idempotent — swallows the 409 on a re-run)
  try {
    await client.register({
      email,
      username: email.split('@')[0],
      password,
      fullName: 'Example User',
    });
    console.log(`✓ Registered ${email}`);
  } catch (e) {
    if (e instanceof SkillError && e.statusCode === 409) {
      console.log(`… ${email} already exists, logging in`);
    } else {
      throw e;
    }
  }

  // 2. Log in
  const tokens = await client.login({ email, password });
  console.log(`✓ Logged in. access_token expires in ${tokens.expiresIn}s`);

  // 3. Read the current user
  const me = await client.getCurrentUser();
  console.log(`✓ Hello, ${me.fullName} (${me.email})`);

  // 4. Refresh the access token
  const refreshed = await client.refresh({ refreshToken: tokens.refreshToken });
  console.log(`✓ Refreshed access token, expires in ${refreshed.expiresIn}s`);

  // 5. Logout
  await client.logout();
  console.log('✓ Logged out');

  return 0;
}

main().then((code) => process.exit(code));
