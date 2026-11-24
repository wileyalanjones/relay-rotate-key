# Additional Question Answers

## 1. Redactor: which inputs would still get through?

My redactor (`helpers/redact_fixed.py`) only skips hyphens and line breaks (`\n`, `\r\n`, `\r`) inside a key, because those are the cases the instruction sheet mentioned. Any other character placed inside the key stops the match, so the key comes through unredacted.

I tried a key with one odd character in the middle (`helpers/test_redact_gaps.py`). All of these leaked:

| Character inserted | Result |
|---|---|
| space, tab, non-breaking space (NBSP) | leaked |
| Unicode hyphen (U+2010), en dash (U+2013) | leaked |
| zero-width space, soft hyphen, line separator (U+2028) | leaked |

Example: `rly_Ab3dE6gH9jK2‐mN5pQ8sT1vX4` (with a Unicode hyphen) comes out unchanged. The Unicode hyphen is the one I think is most likely in real use, because chat tools often swap `-` for a look-alike. Other things I didn't demo would also get through: a `+` or `**` inside the key, uppercase `RLY_`, and encoded or reversed keys.

**What I would change:**
- Widen the characters the pattern skips to all whitespace, all Unicode dashes and the invisible characters, and make it case-insensitive.
- Add one test per case above so they stay fixed.
- Accept that a regex can't catch encoded or deliberately obfuscated keys (base64, reversed). It is only a backstop.

**Why this is lower risk in my design:** `rotate_key.py` handles the key and the agent is never given it, and the agent has no reason to write to a ticket. So the redactor only matters if something goes wrong, for example a key showing up in an error message. The main protection is that structure, and question 3 covers how I would enforce it. The redactor is a second layer.

## 2. AI-use note: what made me sure I was right on the three overrules

**1. Bearer examples without `rly_`.** The packet says the relay key always starts with `rly_`, and the old skill sends it as `Authorization: Bearer $RELAY_KEY`. So the token after `Bearer` is always a `rly_` key. The AI's examples left the prefix off, so they didn't look like real traffic. I checked the packet, not my memory. The AI agreed when I pointed to it, and the corrected examples showed how the two patterns work together: the `rly_` pattern catches the unbroken case, and the Bearer pattern is the backup for hyphens and newlines.

**2. The AI rewrote `redact.py` before we talked about it.** I looked at what the change cost me. The original file is the evidence of where the fault is, and a report like this has to show it failing. The AI had overwritten it before running anything against it, so that evidence was gone. I had it restore the original, and `git status` confirmed a clean tree. I kept the original as `redact.py` so the tests can still show it failing. Its first draft did handle more cases than mine (any whitespace, Unicode dashes, zero-width characters). But without the real comment or the real endpoints I had no way to know which of those cases mattered. I chose the simplest cases first (hyphens and line breaks) and left expanding for later inspection of real data.

**3. Rare line breaks in the tests.** The AI tested 8 line-break types, including `\v`, `\f`, NEL and U+2028/2029. I looked at what the packet and incident note actually say. The packet only says keys are "line-wrapped by chat tools," and the incident note doesn't include the leaked string. Nothing says which character was used. The AI agreed the 8 types were "a defensive guess," not a fact. I cut the tests to `\n` and `\r\n` and logged the open question as item 1 in `unverified.md`. The cost of that choice is question 1: other characters can still get through.

## 3. Guardrails: what if the agent ignored SKILL.md completely?

**The short answer:** very little of my design is enforced against an agent that ignores the skill. The confirmation step and the "never write to a ticket" rule are only instructions. The protection I can point to is structural: the key and the response are handled by `rotate_key.py`, so the agent is never handed anything sensitive.

**What still holds today:**
- **Writing to a ticket:** the helper has no ticket code or ticket credentials, and it prints only a file path, never the request or response. So the agent is not given anything sensitive to post. This reduces the damage, but it does not block the agent from using some other ticket tool.
- **Skipping the confirmation:** nothing stops it. The helper does not ask for a "yes", so an agent could run `python3 helpers/rotate_key.py <service>` directly and it would rotate. This is the weakest point.
- **Going around the helper:** the audit record is written by the helper, so it only exists if the agent uses the helper. An agent that sent the request itself (for example with `curl`) would skip the record, the redaction and the key file.

**What I would add** (none of this is built or tested):

1. **Confirmation from the user when the helper runs.** Step 2 of the skill asks for a "yes", but that's the model asking, so an agent that ignores the skill skips it. I would move the confirmation into the helper. It would ask the user each time it runs and refuse to rotate without a "yes" from a person. The agent can't answer for the user, so calling the helper doesn't rotate anything on its own. This depends on the helper being able to show a prompt to the user in the agent's setup, which I haven't checked.

2. **Keep the key out of the agent's reach.** Right now `$RELAY_KEY` is in the environment the agent runs in. An agent that goes around the helper with `curl` could use it. I would make only the helper able to read the key, for example from a secrets store that releases it to the helper and not to the agent. The agent then can't send a valid request on its own, so going around the helper fails. I don't know whether a secrets store is available, so that is unverified.

3. **Ticket rule: the agent can't write to the ticket system at all.** The skill says never to write to a ticket, but that is only an instruction. I would remove the agent's ticket write access, so a write fails even if the model tries. The strongest version is on the Jira side: the account the agent uses doesn't have the "add comment" permission on the SUP project. The packet doesn't say how the agent reaches Jira, so I would check that first and add it to the unverified list.

4. **Backups, only where they apply.** Not the main idea, and the design should not depend on them:
   - If the platform allows it, block at the harness level: deny `curl` to the Relay host and reads of the key file.
   - Compare rotations recorded in Relay against the audit log. A rotation with no matching record means someone went around the helper.
