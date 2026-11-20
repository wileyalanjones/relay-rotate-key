# Guardrail design

## Main idea

The model should never handle the key. The key is a secret, and a model can do the wrong thing with a secret by accident, as it did in the incident (the key ended up in a public ticket comment). So the key is handled by a tool, `helpers/rotate_key.py`, and not by the model or by instructions in the skill.

## Enforced by the tool (`rotate_key.py`), not by an instruction

- **Reading the key.** The helper reads `$RELAY_KEY` and sends the request itself. The skill does not tell the model to read the variable or run `curl`. The key is sent in a request header, so it never appears on a command line (this also fixes review item 1).
- **Saving the new key.** The helper writes the new key to a file only the user can read (`~/relay-keys/`, folder `700`, file `600`) and prints only the path. The user copies the key from there into their environment, so it never has to appear in the terminal or in the model's context.
- **Redaction.** The helper removes the keys from the request and response before it prints anything. It replaces the exact old and new keys first, then runs `redact_fixed.py` over the rest, which handles hyphens and line breaks. The model only ever receives text that has already been cleaned, so it cannot post a key when it writes the audit comment.
- **Errors and retries.** The helper decides what is safe to retry. It does not retry errors that retrying cannot fix, and it does not retry a timeout, where a key may already exist. It stops and reports the error to the agent with an exit code.

## Advisory (written in the skill, nothing enforces it)

- Check that the request is about a Relay key and that the user named the service.
- Ask the user to confirm before running the helper.
- Tell the user the file path, never show or open the key file, and stop on errors.
- Post only what the helper printed.

## What the design still can't catch

- **It depends on the agent following the skill.** The key is in the environment and the key file belongs to the same user who runs the agent. An agent that goes off-script could still read either. Blocking that would need tool-level rules (for example, permission rules that deny reading `~/relay-keys/` or printing `$RELAY_KEY`). I have not built or tested any.
- **The confirmation is only an instruction.** A platform permission prompt on the helper command would be stronger. I have not tested that.
- **Redaction can miss.** It covers the known key shape, hyphens and line breaks, and the exact known values. It would not catch a key that was encoded, or split across several comments.
- **The ticket audience.** The comment could still be posted publicly. Making the ticket accept only internal comments would have to be done on the Jira side, which I can't access (review item 4).
- **People.** A user can approve without reading, or paste the key somewhere themselves. Anything else running as the user can read the key file.
- **Everything was tested against a fake local server,** not against Relay.
