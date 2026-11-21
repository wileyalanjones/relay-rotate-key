# Requirement change: no writing to tickets

**New rule:** nothing from a key rotation may be written to any ticket, and the agent may not write to the ticket system at all. An audit trail must still exist.

## What changed

- **`skills/SKILL.md`:** removed the step that posted the request and response to a ticket. The agent now sends a short message to the development team chat (service, time, result only) and never writes to a ticket.
- **`helpers/rotate_key.py`:** no longer prints the request or response. It writes a record (time, service, user, result) to a central log before and after the call.
- **`decision_memo.md`:** added an update after the opening paragraph, and updated the changes, gave-up, needs and unverified sections.
- **`guardrails.md`, `rollout.md`:** replaced the ticket-comment audit design and watch items.
- **`unverified.md`:** added items 10 to 14 (the log, the chat, sending messages, the rule's scope, log-down behavior).

## What no longer holds

- The claim that the agent posts cleaned output to a ticket as the audit trail.
- The redaction fix now only cleans error text, so it matters less. The evidence that the original filter leaks still stands.

## What I gave up

- The ticket record that support and managers could see, and the request and response detail.
- A guaranteed record if the central log is down (there is no local copy).
- Tested coverage of the central log and chat, which exist only as assumptions.
