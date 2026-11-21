# Rollout plan

*Updated for the new security rule: the skill no longer writes to a ticket. The watch items below changed because of that.*

1. **The current skill comes out of production.** It has been shown to be dangerous.
2. **Manual rotation covers real keys in the meantime.** A patched v0.3 is not an option, because the skill is too risky even with the comment step removed.
3. **The new skill is piloted alongside it, on a test service only.**
   - **Who goes first:** the development team or reviewers who know the systems well and can give good feedback on problems.
   - **What they rotate:** a test service, not a real one. The helper has only been tried against a fake server.
4. **How we know it's working:** stress test with many inputs and user prompts to see how it breaks.
   - Count each exit code separately, with exits 3 (outcome unknown) and 4 (key rotated but not saved) as the ones that matter.
   - Test the trigger and the confirmation, including prompts that should not rotate anything.
   - Check what the agent actually runs, to see whether it goes off-script.
   - Try hostile inputs, like instructions hidden in ticket text.
   - Check that a user can find the key file and that it is `600`.
5. **What to watch for:**
   - Any failure where a key may have been created or lost.
   - Any write to a ticket by the skill. There should be none.
   - Any rotation without a record in the central log, or without a message in the development team chat.
   - Any key-like string in a log record or message, including keys with hyphens or line breaks.
6. **Moving to real keys:** once the pilot meets the checks, the new skill takes over real rotations in stages. It goes first to the pilot group, then wider, a step at a time.
7. **Rollback:** go back to manual rotation, not to v0.3.
8. **With more time:** the manual runbook and its owner, and the pass criteria for moving to real keys, would be settled with the team.
