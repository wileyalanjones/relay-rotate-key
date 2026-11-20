---
name: relay-rotate-key
description: Rotate a Relay service key when the user asks. Only for Relay keys, not any other kind of key.
---
# Rotate a Relay key
1. Check that the user is asking about a Relay key and has named the service. Keys from other systems are not for this skill. If you are not sure, ask.
2. Ask the user to confirm: "Rotate the Relay key for <service>? (yes/no)". Only proceed if the answer is in the affirmative.
3. Run: python3 helpers/rotate_key.py <service>. 
4. The helper reads the key from $RELAY_KEY, sends the request, and saves the new key to a file that only the user can read. It removes any keys from the full request and response. It prints the path of that file and the cleaned request and response.
5. Tell the user the file path so they can find their new key. Never print, show, or paste the key. Do not open the file.
6. If the helper reports an error, tell the user and stop. Do not retry or make the call yourself.
7. Post a summary of what you did, including the full request and response, as a comment on the ticket the user names, so there is an audit trail.
