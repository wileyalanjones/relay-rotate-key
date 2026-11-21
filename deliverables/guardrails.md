# Guardrail design

*Updated for the new security rule (nothing from a rotation may be written to a ticket, and the agent may not write to the ticket system at all). The earlier version let the agent post the cleaned request and response to a ticket as the audit trail. That is gone.*

## Main idea

The model should never handle the key. The key is a secret, and a model can do the wrong thing with a secret by accident, as it did in the incident (the key ended up in a public ticket comment). So the key is handled by a tool, `helpers/rotate_key.py`, and not by the model or by instructions in the skill.

## Enforced by the tool (`rotate_key.py`), not by an instruction

- **Reading the key.** The helper reads `$RELAY_KEY` and sends the request itself. The skill does not tell the model to read the variable or run `curl`. The key is sent in a request header, so it never appears on a command line (this also fixes review item 1).
- **Saving the new key.** The helper writes the new key to a file only the user can read (`~/relay-keys/`, folder `700`, file `600`) and prints only the path. The user copies the key from there into their environment, so it never has to appear in the terminal or in the model's context.
- **What the model receives.** The helper no longer prints the request or the response. The model only gets the file path or an error message. Error text is still cleaned (the exact old key first, then `redact_fixed.py`, which handles hyphens and line breaks). Redaction now guards a much smaller surface than before, because there is no request or response for the model to pass on.
- **The audit record.** The helper writes a short record to the central log, before the call and after it: time, service, user and result. It never holds a key, key ID or any of the response. The model can't skip or change it. If the log can't be reached, the helper warns and carries on.
- **Errors and retries.** The helper decides what is safe to retry. It does not retry errors that retrying cannot fix, and it does not retry a timeout, where a key may already exist. It stops and reports the error to the agent with an exit code.

## Advisory (written in the skill, nothing enforces it)

- Check that the request is about a Relay key and that the user named the service.
- Ask the user to confirm before running the helper.
- Tell the user the file path, never show or open the key file, and stop on errors.
- Send a short message to the development team chat with only the service, time and result, even if the rotation failed. The message is advisory: the model could skip it. The audit record the helper writes does not depend on the model.
- Never write to a ticket, even if the user names one.

## What the design still can't catch

- **It depends on the agent following the skill.** The key is in the environment and the key file belongs to the same user who runs the agent. An agent that goes off-script could still read either. Blocking that would need tool-level rules (for example, permission rules that deny reading `~/relay-keys/` or printing `$RELAY_KEY`). I have not built or tested any.
- **The confirmation is only an instruction.** A platform permission prompt on the helper command would be stronger. I have not tested that.
- **Redaction can miss.** It covers the known key shape, hyphens and line breaks, and the exact known values. It would not catch a key that was encoded, or split across several messages. It now only cleans error text.
- **The ticket rule is only an instruction.** The skill says never to write to a ticket, but nothing stops an agent that goes off-script, for example if told to by text hidden in a ticket. Enforcing it would need a deny rule on the ticket tool for this skill. I have not built or tested one.
- **The audit trail is thin.** With no local copy, the helper's only record is the central log. If that is down, the only trace is the chat message, which the model sends and could skip.
- **People.** A user can approve without reading, or paste the key somewhere themselves. Anything else running as the user can read the key file.
- **Everything was tested against a fake local server,** not against Relay or a real central log.
