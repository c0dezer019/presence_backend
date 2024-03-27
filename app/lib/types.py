from typing import NewType, Tuple

FilterLevels = NewType('FilterLevels', tuple[int])

type filter_args = int | Tuple[int] | Tuple[int, int] | Tuple[int, int, int]
type ExceptionMsg = str
