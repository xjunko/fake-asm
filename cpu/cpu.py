""" cpu.py - the real shit
    disclaimer:
        - i have no fucking clue how a real CPU works like, this is just me guessing.
        - lots of tech jargons are being used wrongly but it should get the point across.

    notes:
        - "byte" is not actually a byte.
        - number MUST be stored somewhere in registers even for one case use [except for SET]
        - compare = 0b000 | 001 - higher | 010 - lower | 100 - equal | 101 - not equal
        - compare only use the first "byte" of internal compare memory
        - cmp must has jmpeq or jmpneq after it else the first byte of compare memory will stay positive.
"""
from __future__ import annotations

import traceback
from dataclasses import dataclass
from enum import Enum
from typing import Self


class CompareType(Enum):
    HIGHER = 0b001
    LOWER = 0b010
    EQUAL = 0b100
    NOT_EQUAL = 0b101


class OperationType(Enum):
    SET = 0xA1
    ADD = 0xA2
    MINUS = 0xA3
    MULTIPLY = 0xA4
    DIVIDE = 0xA5
    AND = 0xA6
    OR = 0xA7
    MOD = 0xA8
    XOR = 0xA9

    COMPARE = 0xB1

    STORE = 0xC1
    LOAD = 0xC2

    JUMP = 0xD1
    JUMPEQ = 0xD2
    JUMPNEQ = 0xD3

    @staticmethod
    def from_str(text: str) -> OperationType:
        """return the matching enum from string"""

        return {
            # Math
            "set": OperationType.SET,
            "add": OperationType.ADD,
            "sub": OperationType.MINUS,
            "mult": OperationType.MULTIPLY,
            "div": OperationType.DIVIDE,
            "and": OperationType.AND,
            "or": OperationType.OR,
            "mod": OperationType.MOD,
            "xor": OperationType.XOR,
            # Function
            "cmp": OperationType.COMPARE,
            "jmp": OperationType.JUMP,
            "jmpeq": OperationType.JUMPEQ,
            "jmpneq": OperationType.JUMPNEQ,
            # Memory
            "store": OperationType.STORE,
            "load": OperationType.LOAD,
        }[
            text.lower()
        ]  # no need for .get() here.


@dataclass
class Operation:  # add r3, r1, r2
    action: OperationType
    inputs: list[int]
    destination: int


# Const
REGISTER_SIZE: int = 16
MEMORY_SIZE: int = 32


class CPU:
    def __init__(self) -> Self:
        self.register: list[int] = []
        self.memory: list[int] = []
        self.compare: list[int] = []

        self.operation_i: int = 0
        self.operations: list[Operation] = []

    # Internal
    def _initiate_cpu(self, *, reg_size: int, mem_size: int) -> None:
        self.register = [0 for _ in range(reg_size)]
        self.memory = [0 for _ in range(mem_size)]
        self.compare = [0 for _ in range(4)]

        self.operations = self.memory.copy()

    # Public
    def execute(
        self,
        op: Operation,
        *,
        debug: bool = False,
        manual: bool = False,
    ) -> int | None:
        if not op:
            return

        if manual:
            self.operations[self.operation_i] = op
            self.operation_i += 1

            return  # HACK: HACK HACK HACK

        if debug:
            print(
                f"[CPU] [{len(self.operations) - 1}] {op.action} inbound, {op.destination} - {op.inputs=}",
            )

        match op.action:
            # Register
            case OperationType.SET:
                self.register[op.destination] = op.inputs[0]

            case OperationType.ADD:
                self.register[op.destination] = (
                    self.register[op.inputs[0]] + self.register[op.inputs[1]]
                )

            case OperationType.MINUS:
                self.register[op.destination] = (
                    self.register[op.inputs[0]] - self.register[op.inputs[1]]
                )

            case OperationType.MULTIPLY:
                self.register[op.destination] = (
                    self.register[op.inputs[0]] * self.register[op.inputs[1]]
                )

            case OperationType.DIVIDE:
                self.register[op.destination] = (
                    self.register[op.inputs[0]] / self.register[op.inputs[1]]
                )

            case OperationType.AND:
                self.register[op.destination] = (
                    self.register[op.inputs[0]] & self.register[op.inputs[1]]
                )

            case OperationType.OR:
                self.register[op.destination] = (
                    self.register[op.inputs[0]] | self.register[op.inputs[1]]
                )

            case OperationType.MOD:
                self.register[op.destination] = (
                    self.register[op.inputs[0]] % self.register[op.inputs[1]]
                )

            case OperationType.XOR:
                self.register[op.destination] = (
                    self.register[op.inputs[0]] ^ self.register[op.inputs[1]]
                )

            # Memory
            case OperationType.STORE:
                self.memory[op.destination] = self.register[op.inputs[0]]

            case OperationType.LOAD:
                self.register[op.destination] = self.memory[op.inputs[0]]

            # Functions
            case OperationType.COMPARE:
                a: int = self.register[op.inputs[0]]
                b: int = self.register[op.inputs[1]]

                op.inputs[2] = CompareType(op.inputs[2])

                match op.inputs[2]:
                    case CompareType.HIGHER:
                        self.compare[0] = int(a > b)

                    case CompareType.LOWER:
                        self.compare[0] = int(a < b)

                    case CompareType.EQUAL:
                        self.compare[0] = int(a == b)

                    case CompareType.NOT_EQUAL:
                        self.compare[0] = int(a != b)

            # Jumps
            case OperationType.JUMP:
                self.execute(self.operations[op.destination])
                self.operation_i = op.destination

            case OperationType.JUMPEQ:
                if self.compare[0] == 0x1:
                    self.execute(self.operations[op.destination])
                    self.operation_i = op.destination

                self.compare[0] = 0x0

            case OperationType.JUMPNEQ:
                if self.compare[0] == 0x0:
                    self.execute(self.operations[op.destination])
                    self.operation_i = op.destination

            case _:
                print(f"[CPU] Unhandled operation: {op=}")

    def execute_all(self) -> None:
        self.operation_i = 0

        while self.operation_i < len(self.operations):
            self.execute(self.operations[self.operation_i])
            self.operation_i += 1

    def interpret(self, code: str) -> None:
        lines: list[str] = map(
            lambda x: x.strip().replace(",", ""),
            filter(lambda x: len(x) > 0, code.splitlines()),
        )

        for line in lines:
            items: list[str] = line.split(" ")

            items = [
                items[0],
                *map(lambda x: x.replace("r", "").replace("m", ""), items[1:]),
            ]

            operation = Operation(
                action=OperationType.SET,
                destination=0xB00B,
                inputs=[],
            )

            operation.action = OperationType.from_str(items[0])

            match items[0]:
                case "set":
                    operation.destination = int(items[1])
                    operation.inputs = [int(items[2])]

                case "add" | "sub" | "mult" | "div":
                    operation.destination = int(items[1])
                    operation.inputs = [int(items[2]), int(items[3])]

                case "cmp":
                    operation.destination = 0  # compare has its own memory
                    operation.inputs = [
                        int(items[1]),
                        int(items[2]),
                        int(eval(items[3])),
                    ]

                case "store" | "load":
                    operation.destination = int(items[1])
                    operation.inputs = [int(items[2])]

                case "jmp" | "jmpeq" | "jmpneq":
                    operation.destination = int(items[1])
                    operation.inputs = []

                case _:
                    print(f"[EVAL] Unhandled operator: OP={items[0]} - {items[1:]}")

            if operation.destination != 0xB00B:
                self.operations[self.operation_i] = operation
                self.operation_i += 1

        self.operation_i = 0
        self.execute_all()

    # Info
    def _print_list(self, input: list[int]) -> None:
        newline_every: int = 8

        for i, value in enumerate(input):
            if isinstance(value, Operation):
                value = str(value.action).split(".", 1)[-1]
            else:
                value = f"{int(value):02}"

            if i > 0 and (i + 1) % newline_every == 0:
                print("\t", value, "\t|", end="\n")
            else:
                print("\t", value, end="")

    def print_stats(self) -> None:
        print("\t\t\t-+ [REGISTER] +-")
        self._print_list(self.register)

        print("\t\t\t-+ [ MEMORY ] +-")
        self._print_list(self.memory)

        print("\t\t\t-+ [ COMPARE ] +-")
        self._print_list(self.compare)

    # Factory
    @classmethod
    def create(cls, *, reg_size: int = None, mem_size: int = None) -> Self:
        reg_size = reg_size or REGISTER_SIZE
        mem_size = mem_size or MEMORY_SIZE

        self = cls()
        self._initiate_cpu(reg_size=reg_size, mem_size=mem_size)

        return self


def fuckaround_registers(cpu: CPU) -> None:
    """registers only"""

    # set r0, 69
    cpu.execute(op=Operation(action=OperationType.SET, destination=0, inputs=[69]))

    # set r1, 420
    cpu.execute(op=Operation(action=OperationType.SET, destination=1, inputs=[420]))

    # add r2, r0, r1
    cpu.execute(op=Operation(action=OperationType.ADD, destination=2, inputs=[0, 1]))

    # sub r3, r2, r1
    cpu.execute(op=Operation(action=OperationType.MINUS, destination=3, inputs=[2, 1]))

    # mult r4, r3, r2
    cpu.execute(
        op=Operation(action=OperationType.MULTIPLY, destination=4, inputs=[3, 2]),
    )

    # div r5, r4, r2
    cpu.execute(op=Operation(action=OperationType.DIVIDE, destination=5, inputs=[4, 2]))


def fuckaround_memory(cpu: CPU) -> None:
    """memory and registers"""

    # set r13, 2 ; for dividing by two later on
    cpu.execute(op=Operation(action=OperationType.SET, destination=13, inputs=[2]))

    # add r15, r2, r3
    cpu.execute(op=Operation(action=OperationType.ADD, destination=15, inputs=[2, 3]))

    # store m0, r15
    cpu.execute(op=Operation(action=OperationType.STORE, destination=0, inputs=[15]))

    # add r15, r15, r15 ; equivalent to * 2
    cpu.execute(op=Operation(action=OperationType.ADD, destination=15, inputs=[15, 15]))

    # store m1, r15 ; this should equal to whatever the result is at the end.
    cpu.execute(op=Operation(action=OperationType.STORE, destination=1, inputs=[15]))

    # div r15, r15, r13 ; divide by two
    cpu.execute(
        op=Operation(action=OperationType.DIVIDE, destination=15, inputs=[15, 13]),
    )

    # load r15, m1
    cpu.execute(op=Operation(action=OperationType.LOAD, destination=15, inputs=[1]))

    # div r15, r15, r13 ; divide by two, again
    cpu.execute(
        op=Operation(action=OperationType.DIVIDE, destination=15, inputs=[15, 13]),
    )


def fuckaround_compare(cpu: CPU) -> ...:
    # stop loop at
    # set r5, 420
    cpu.execute(
        op=Operation(action=OperationType.SET, destination=5, inputs=[420]),
        manual=True,
    )

    # constant number for adding
    # set r10, 1
    cpu.execute(
        op=Operation(action=OperationType.SET, destination=10, inputs=[1]),
        manual=True,
    )

    # add r11, r11, r10
    cpu.execute(
        op=Operation(action=OperationType.ADD, destination=11, inputs=[11, 10]),
        manual=True,
    )

    # cmp r11, r15, 0b010
    cpu.execute(
        op=Operation(
            action=OperationType.COMPARE,
            destination=0,
            inputs=[11, 5, CompareType.LOWER],
        ),
        manual=True,
    )

    # jmpeq 2
    cpu.execute(
        op=Operation(action=OperationType.JUMPEQ, destination=2, inputs=[]),
        manual=True,
    )

    cpu.execute_all()


def emulate_local() -> int:
    cpu: CPU = CPU.create()

    try:
        fuckaround_registers(cpu=cpu)
        fuckaround_memory(cpu=cpu)
        fuckaround_compare(cpu=cpu)
    except Exception as err:
        print(
            f"[CPU] Something fucked up:\n",
            "\n".join(traceback.format_exception(err)),
            "last known CPU state: ",
        )

    cpu.print_stats()

    return 0


if __name__ == "__main__":
    raise SystemExit(emulate_local())
