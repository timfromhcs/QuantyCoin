"""
QuantyCoin Core - Canonical Integer Money Type & Checked Arithmetic
Implements strict 64-bit integer monetary arithmetic with overflow/underflow protection.
Zero floating-point operations in consensus paths.
"""

from typing import Union
from .genesis_constants import MAX_MONEY_SATOSHIS

COIN = 100_000_000  # 1 QTY = 10^8 satoshis


class MoneyRangeError(ValueError):
    """Raised when an Amount violates consensus monetary bounds."""
    pass


class Amount:
    """
    Immutable canonical integer money type for QuantyCoin QTY4.
    Encapsulates satoshis as an exact 64-bit signed integer within [0, MAX_MONEY_SATOSHIS].
    """
    __slots__ = ('_satoshis',)

    def __init__(self, satoshis: Union[int, 'Amount']):
        if isinstance(satoshis, Amount):
            val = satoshis._satoshis
        elif isinstance(satoshis, int):
            val = satoshis
        else:
            raise TypeError(f"Amount value must be integer or Amount, got {type(satoshis).__name__}")

        if val < 0:
            raise MoneyRangeError(f"Negative amount is invalid: {val}")
        if val > MAX_MONEY_SATOSHIS:
            raise MoneyRangeError(f"Amount {val} exceeds MAX_MONEY_SATOSHIS ({MAX_MONEY_SATOSHIS})")

        object.__setattr__(self, '_satoshis', val)

    @property
    def satoshis(self) -> int:
        return self._satoshis

    @classmethod
    def from_qty(cls, qty: int) -> 'Amount':
        """Construct Amount from integer whole QTY coins."""
        if not isinstance(qty, int):
            raise TypeError("Whole QTY amount must be integer")
        return cls(qty * COIN)

    @classmethod
    def zero(cls) -> 'Amount':
        return cls(0)

    def to_qty_str(self) -> str:
        """Deterministic string display formatted as X.XXXXXXXX QTY."""
        whole = self._satoshis // COIN
        frac = self._satoshis % COIN
        return f"{whole}.{frac:08d}"

    def serialize(self) -> bytes:
        """8-byte signed little-endian binary representation."""
        import struct
        return struct.pack('<q', self._satoshis)

    @classmethod
    def deserialize(cls, data: bytes) -> 'Amount':
        """Deserialize 8-byte signed little-endian satoshis."""
        import struct
        if len(data) < 8:
            raise ValueError("Data too short for Amount (need 8 bytes)")
        val = struct.unpack('<q', data[:8])[0]
        return cls(val)

    # Checked Arithmetic Operations
    def __add__(self, other: Union['Amount', int]) -> 'Amount':
        other_val = other._satoshis if isinstance(other, Amount) else other
        res = self._satoshis + other_val
        if res > MAX_MONEY_SATOSHIS:
            raise MoneyRangeError(f"Monetary addition overflow: {self._satoshis} + {other_val} > {MAX_MONEY_SATOSHIS}")
        return Amount(res)

    def __radd__(self, other: Union['Amount', int]) -> 'Amount':
        return self.__add__(other)

    def __sub__(self, other: Union['Amount', int]) -> 'Amount':
        other_val = other._satoshis if isinstance(other, Amount) else other
        res = self._satoshis - other_val
        if res < 0:
            raise MoneyRangeError(f"Monetary subtraction underflow: {self._satoshis} - {other_val} < 0")
        return Amount(res)

    def __mul__(self, scalar: int) -> 'Amount':
        if not isinstance(scalar, int):
            raise TypeError("Amount can only be multiplied by integer scalars")
        if scalar < 0:
            raise MoneyRangeError(f"Negative multiplication scalar: {scalar}")
        res = self._satoshis * scalar
        if res > MAX_MONEY_SATOSHIS:
            raise MoneyRangeError(f"Monetary multiplication overflow: {res} > {MAX_MONEY_SATOSHIS}")
        return Amount(res)

    def __rmul__(self, scalar: int) -> 'Amount':
        return self.__mul__(scalar)

    def __floordiv__(self, divisor: int) -> 'Amount':
        if not isinstance(divisor, int):
            raise TypeError("Divisor must be an integer")
        if divisor <= 0:
            raise ZeroDivisionError("Divisor must be positive integer")
        return Amount(self._satoshis // divisor)

    def __rshift__(self, bits: int) -> 'Amount':
        """Integer right-shift for exact halving calculation."""
        if not isinstance(bits, int) or bits < 0:
            raise ValueError("Shift bits must be non-negative integer")
        return Amount(self._satoshis >> bits)

    # Comparison Operations
    def __eq__(self, other: object) -> bool:
        if isinstance(other, Amount):
            return self._satoshis == other._satoshis
        if isinstance(other, int):
            return self._satoshis == other
        return False

    def __lt__(self, other: Union['Amount', int]) -> bool:
        other_val = other._satoshis if isinstance(other, Amount) else other
        return self._satoshis < other_val

    def __le__(self, other: Union['Amount', int]) -> bool:
        other_val = other._satoshis if isinstance(other, Amount) else other
        return self._satoshis <= other_val

    def __gt__(self, other: Union['Amount', int]) -> bool:
        other_val = other._satoshis if isinstance(other, Amount) else other
        return self._satoshis > other_val

    def __ge__(self, other: Union['Amount', int]) -> bool:
        other_val = other._satoshis if isinstance(other, Amount) else other
        return self._satoshis >= other_val

    def __repr__(self) -> str:
        return f"Amount({self._satoshis} satoshis / {self.to_qty_str()} QTY)"

    def __int__(self) -> int:
        return self._satoshis
