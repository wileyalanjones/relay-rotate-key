---
name: relay-rotate-key
description: Rotate a Relay service key when the user asks. Only for Relay keys, not any other kind of key.
---
# Rotate a Relay key
1. Check that the user is asking about a Relay key and has named the service. Keys from other systems are not for this skill. If you are not sure, ask.
2. Ask the user to confirm: "Rotate the Relay key for <service>? (yes/no)". Only proceed if the answer is in the affirmative.
3. Run: python3 helpers/rotate_key.py <service>. 
4. The helper reads the key from $RELAY_KEY, sends the request, and saves the new key to a file that only the user can read. It prints only the path of that file. It also writes a short record of the rotation (the time, the service, who ran it and the result) to the central log.
5. Tell the user the file path so they can find their new key. Never print, show, or paste the key. Do not open the file.
6. If the helper reports an error, or warns that the record could not be sent to the central log, tell the user. Do not retry or make the call yourself.
7. Send a short message to the development team chat saying how it went. Use only the service name, the time and the result, in one of these forms. Send it even if the rotation failed. Do not add anything else.
   - It worked: "Relay key rotation for <service> succeeded at <time>."
   - It failed and nothing changed (exit code 2): "Relay key rotation for <service> failed at <time>. No key was changed."
   - The result is unclear (exit code 3 or 4): "Relay key rotation for <service> may have created a key at <time>. Check Relay."
8. Never write to a ticket, even if the user names one. Never put a key, part of a key, a key ID, or anything from the response in a message.
