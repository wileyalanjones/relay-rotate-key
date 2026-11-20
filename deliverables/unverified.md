# Unverified

Things I believed or assumed but did not check.

1. **Which kind of line break the real comment used.** The packet only says keys are
   "sometimes line-wrapped by chat tools" and does not say which character was used
   (`\n`, `\r\n`, or something else). The incident note does not include the leaked string
   either. My tests cover `\n` and `\r\n` only. I did not check how the real dashboard
   stores or renders comment line breaks.
