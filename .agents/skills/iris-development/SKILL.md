---
name: iris-development
description: Use when changing Iris code or instructions, evaluating its behavior, or updating an installed Hermes profile from this repository.
---

# Iris development

This is a Codex workflow for repeated repo-to-runtime changes. The root `skills/` directory
contains skills for Iris herself and is installed into the Hermes profile.

## Establish the current state

1. Read `AGENTS.md`, `docs/PRODUCT.md`, the current snapshot at the top of `docs/STATUS.md`,
   and the code or Iris skill relevant to the task. Treat dated plans and evaluation logs as
   evidence of earlier decisions, not instructions to continue them.
2. Check Git status and preserve existing user changes. For live work, inspect the installed
   profile separately: repository files and deployed files can differ.
3. State the requested behavior, the smallest useful change, and what observation would prove
   it. Resolve product direction with the owner when it is genuinely open; research technical
   facts yourself.

## Change and verify

1. Reuse Hermes capabilities and Iris's existing seams before adding a tool or script.
2. Test the affected behavior with the offline suite and repository validator in
   `docs/TESTING.md`. Use the relevant native Hermes evaluation cases for agent behavior;
   review answers and tool traces, since a completed run is not a behavioral pass.
3. If the change must reach the live profile, follow `docs/SETUP.md`'s existing-profile path.
   Back up the affected runtime files and state, transfer only intended files, and preserve
   sessions, memory, OAuth and scheduled job identities. Verify the installed revision and the
   affected live behavior. A repo test or successful file copy alone is not deployment proof.
4. When runtime behavior or verification changes, update the current snapshot in
   `docs/STATUS.md` with what was actually verified, what remains untested, and the date.
   Keep business outcomes separate from simulated or estimated impact.

Stop when the requested behavior and its evidence agree. Leave unrelated product direction and
historical plans unchanged.
