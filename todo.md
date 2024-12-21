# Bugs / things to improve

- Add a rule to avoid weird 3 character combinations (anrnv is currently considered a valid word combination and it shouldnt)
- Make brute force more eficient by copying strings the pythonic way( [2::] )
- When checking a string comination, make the dehasher to only hash once per type the current word to hash ( T7 for example uses the same hash algorithm for everything, currently each word gets hashed each time it checks a new hash type )
- Redo hashing alogrithms so a precomputed hash can be passed, this way we can save many cicles of CPU
- Make code more organized, there are old functions which are not used anymore, also importing only the used functions from libraries would be nice