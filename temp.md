

# Redistribution of responsibilities

  * Matching functionalities moved from SaltTest to TestAssistant class

## Matching procedure

  User enters some string
  The first keyword group is matched against the string
    If that fails.. the test is ignored
  But.. If that was a consequent query, where last match
    was partially successful. Then resume from where we stopped last time.

