from array import array

class SeenKeys:
    """Open-addressed set of 64-bit keys, 8 bytes per slot.

    A Python `set` of the same hashes costs ~72 bytes per entry (the int objects
    plus the table); this holds the keys unboxed in an `array("q")` and linear
    probes, for 13-27 bytes per key depending on where the power-of-two table
    size lands — about a third of the `set`, for roughly 20% more CPU.

    The table doubles when it passes `MAX_LOAD`, and `expect` presizes it so a
    run whose size is known in advance never rehashes. Beyond ~0.6, linear
    probing degrades quickly (an unsuccessful lookup averages
    `(1 + 1/(1-load)**2)/2` probes: 2.5 at 0.5, 3.6 at 0.6, 8.5 at 0.75), which
    is why the table is kept below that rather than filled.

    Key 0 marks an empty slot, so a key that hashes to 0 is stored as 1 — one
    key in 2**64 is thereby merged with another, which is far below the
    collision rate of the 64-bit hash itself.
    """

    MAX_LOAD = 0.6

    def __init__(self, expect=0):
        bits = 22
        while (1 << bits) * self.MAX_LOAD < expect:
            bits += 1
        self._size_table(bits)
        self.size = 0

    def _size_table(self, bits):
        self.bits = bits
        self.mask = (1 << bits) - 1
        self.limit = int((1 << bits) * self.MAX_LOAD)
        # Repeating a one-element array builds the buffer directly; passing
        # `bytes(8 << bits)` would materialize a second full-size buffer for the
        # constructor to copy, doubling peak memory at gigabyte table sizes.
        self.table = array("q", [0]) * (1 << bits)

    def add(self, key):
        """Insert `key`; return True if it was new, False if already present."""
        if key == 0:
            key = 1
        t, mask = self.table, self.mask
        i = key & mask
        while True:
            cur = t[i]
            if cur == 0:
                t[i] = key
                self.size += 1
                if self.size > self.limit:
                    self._grow()
                return True
            if cur == key:
                return False
            i = (i + 1) & mask

    def _grow(self):
        old = self.table
        self._size_table(self.bits + 1)
        t, mask = self.table, self.mask
        for key in old:
            if key:
                i = key & mask
                while t[i]:
                    i = (i + 1) & mask
                t[i] = key

    def __len__(self):
        return self.size
