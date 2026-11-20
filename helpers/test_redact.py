from redact import redact

# Fake key: "rly_" followed by 24 letters/digits
examples = {
    "unbroken": "key: rly_Ab3dE6gH9jK2mN5pQ8sT1vX4",
    "hyphen in middle": "key: rly_Ab3dE6gH9jK2-mN5pQ8sT1vX4",
    "newline in middle": "key: rly_Ab3dE6gH9jK2\nmN5pQ8sT1vX4",
    "bearer unbroken": "Authorization: Bearer rly_Ab3dE6gH9jK2mN5pQ8sT1vX4",
    "bearer hyphen in middle": "Authorization: Bearer rly_Ab3dE6gH9jK2mN5p-Q8sT1vX4",
    "bearer newline in middle": "Authorization: Bearer rly_Ab3dE6gH9jK2mN5pQ8sT\n1vX4",
    "bearer newline near beginning": "Authorization: Bearer rly_Ab3\ndE6gH9jK2mN5pQ8sT1vX4",
}

for name, text in examples.items():
    print(f"--- {name} ---")
    print("before:", repr(text))
    print("after: ", repr(redact(text)))
    print()
