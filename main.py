""" miku.py - simple assembly bootleg thingamajig """
from __future__ import annotations

__author__ = "xJunko"
__github__ = "xJunko"

import sys

import cpu
import cpu.test


def main(argv: list[str]) -> int:
    if not argv:
        raise RuntimeError(
            "Not enough arguments, accepted arguments are [test, path_to_file]!",
        )

    if argv[0] == "test":
        # CPU
        cpu.test.cpu_test.run()
    else:
        runtime = cpu.core.CPU.from_file(argv[0])
        runtime.print_stats()

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
