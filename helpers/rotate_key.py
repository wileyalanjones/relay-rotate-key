"""Rotate a Relay service key.

Usage:  python3 rotate_key.py <service>

What it does:
  1. Reads the current key from $RELAY_KEY.
  2. Sends the rotate request (the key goes in a header, never on a command line).
  3. Saves the new key to a file only the user can read.
  4. Prints the file path and the request/response with all keys removed.

Exit codes:
  0  success
  2  failed and nothing changed (safe to fix the problem and ask again)
  3  OUTCOME UNKNOWN: a new key may exist. Do not retry. Check Relay.
  4  the key was rotated but could not be saved. Rotate again.
"""
import json
import os
import re
import socket
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from redact_fixed import redact

URL = "https://relay.example.internal/v1/keys/rotate"
KEY_FOLDER = Path.home() / "relay-keys"
TIMEOUT_SECONDS = 10
MAX_ATTEMPTS = 3
BACKOFF_SECONDS = 2  # waits 2s, then 4s between attempts

KEY_SHAPE = re.compile(r"rly_[A-Za-z0-9]{24}")
SERVICE_SHAPE = re.compile(r"[A-Za-z0-9_.-]{1,64}")

# Failures where the request never took effect, so trying again is safe.
RETRY_STATUS = {429, 503}


class RotateError(Exception):
    exit_code = 1


class NothingChanged(RotateError):
    """Failed, and retrying will not help. Nothing was rotated."""
    exit_code = 2


class OutcomeUnknown(RotateError):
    """A new key may exist. Retrying could create another one."""
    exit_code = 3


class SaveFailed(RotateError):
    """Relay rotated the key but we could not save the new one."""
    exit_code = 4


class _TryAgain(Exception):
    """Internal: this attempt failed in a way that is safe to retry."""


def _clean(text, *keys):
    """Remove exact known keys first, then anything shaped like a key."""
    for key in keys:
        if key:
            text = text.replace(key, "[REDACTED]")
    return redact(text)


def _send(service, old_key, url):
    """One attempt. Returns (status, body). Raises on any failure."""
    body = json.dumps({"service": service}).encode()
    request = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {old_key}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            return response.status, response.read().decode("utf-8", "replace")

    except urllib.error.HTTPError as error:
        text = _clean(error.read().decode("utf-8", "replace")[:200], old_key)
        if error.code in RETRY_STATUS:
            raise _TryAgain(f"Relay answered {error.code}: {text}")
        if 400 <= error.code < 500 and error.code != 408:
            raise NothingChanged(f"Relay rejected the request ({error.code}): {text}")
        raise OutcomeUnknown(
            f"Relay answered {error.code}, so the rotation may have happened. "
            f"Do not retry. Check Relay for extra keys. ({text})"
        )

    except (socket.timeout, TimeoutError):
        raise OutcomeUnknown(
            "The request timed out, so the rotation may have happened. "
            "Do not retry. Check Relay for extra keys."
        )

    except urllib.error.URLError as error:
        if isinstance(error.reason, (socket.timeout, TimeoutError)):
            raise OutcomeUnknown(
                "The request timed out, so the rotation may have happened. "
                "Do not retry. Check Relay for extra keys."
            )
        if isinstance(error.reason, (ConnectionRefusedError, socket.gaierror)):
            raise _TryAgain(f"Could not reach Relay: {error.reason}")
        raise OutcomeUnknown(
            f"The connection failed ({error.reason}), so the rotation may have "
            "happened. Do not retry. Check Relay for extra keys."
        )

    except OSError as error:
        # e.g. the connection dropped while reading the reply
        raise OutcomeUnknown(
            f"The connection failed ({error}), so the rotation may have "
            "happened. Do not retry. Check Relay for extra keys."
        )


def _save(service, new_key):
    """Write the key to a file only this user can read. Returns the path."""
    try:
        KEY_FOLDER.mkdir(mode=0o700, exist_ok=True)
        os.chmod(KEY_FOLDER, 0o700)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        # O_EXCL: never overwrite. 0o600 from the start: no moment where
        # other users could read it. If the name is taken, add a number.
        for number in range(100):
            suffix = "" if number == 0 else f"-{number}"
            path = KEY_FOLDER / f"{service}-{stamp}{suffix}.key"
            try:
                fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            except FileExistsError:
                continue
            with os.fdopen(fd, "w") as handle:
                handle.write(new_key + "\n")
            return path
        raise OSError("too many key files with the same name")
    except OSError as error:
        raise SaveFailed(
            f"Relay rotated the key but the new key could not be saved ({error}). "
            "The new key is lost. Rotate again."
        )


def rotate(service, url=URL, backoff=BACKOFF_SECONDS):
    """Rotate the key. Returns (saved_path, cleaned_request, cleaned_response)."""
    if not SERVICE_SHAPE.fullmatch(service):
        raise NothingChanged(
            "The service name may only use letters, digits, '_', '.' and '-' "
            "(1 to 64 characters)."
        )
    old_key = os.environ.get("RELAY_KEY", "").strip()
    if not old_key:
        raise NothingChanged("$RELAY_KEY is not set.")

    for attempt in range(MAX_ATTEMPTS):
        try:
            status, body = _send(service, old_key, url)
            break
        except _TryAgain as error:
            if attempt == MAX_ATTEMPTS - 1:
                raise NothingChanged(f"{error} (gave up after {MAX_ATTEMPTS} tries)")
            time.sleep(backoff * 2 ** attempt)

    match = KEY_SHAPE.search(body)
    if not match:
        raise OutcomeUnknown(
            "Relay accepted the request but no new key was found in the reply. "
            "Do not retry. Check Relay."
        )
    new_key = match.group(0)

    path = _save(service, new_key)

    request_text = (
        f"POST {url}\n"
        f"Authorization: Bearer {old_key}\n"
        f"{json.dumps({'service': service})}"
    )
    response_text = f"HTTP {status}\n{body}"
    return (
        path,
        _clean(request_text, old_key, new_key),
        _clean(response_text, old_key, new_key),
    )


def main(argv):
    if len(argv) != 2:
        print("Usage: python3 rotate_key.py <service>", file=sys.stderr)
        return 2
    try:
        path, request_text, response_text = rotate(argv[1])
    except RotateError as error:
        print(f"ERROR ({type(error).__name__}): {error}", file=sys.stderr)
        return error.exit_code

    print(f"New key saved to: {path}")
    print(f"To open the folder on a Mac: open {path.parent}")
    print()
    print("--- request (keys removed) ---")
    print(request_text)
    print()
    print("--- response (keys removed) ---")
    print(response_text)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
