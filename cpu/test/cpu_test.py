from __future__ import annotations

import traceback

from .. import core


def test_registers() -> None:
    print("[CPU] Registers:", end="")

    print(" handwritten,", end="")
    hw_cpu = core.CPU.create()
    core.fuckaround_registers(hw_cpu)
    print(" done,", end="")

    print(" interpreted,", end="")
    ip_cpu = core.CPU.create()
    ip_cpu.interpret(
        """
set r0, 69
set r1, 420
add r2, r0, r1
sub r3, r2, r1
mult r4, r3, r2
div r5, r4, r2
""",
    )

    print(" done, comparing values! \n", end="")

    assert hw_cpu.register == ip_cpu.register, (
        f"Registers are not the same! \n"
        + f"HW={hw_cpu.register} | IP={ip_cpu.register}"
    )

    assert hw_cpu.memory == ip_cpu.memory, (
        f"Memory are not the same! \n" + f"HW={hw_cpu.memory} | IP={ip_cpu.memory}"
    )
    print("[CPU] Registers: Checks out.")


def test_memory() -> None:
    print("[CPU] Memory:", end="")

    print(" handwritten,", end="")
    hw_cpu = core.CPU.create()
    core.fuckaround_memory(hw_cpu)
    print(" done,", end="")

    print(" interpreted,", end="")
    ip_cpu = core.CPU.create()
    ip_cpu.interpret(
        """
set r13, 2
add r15, r2, r3
store m0, r15
add r15, r15, r15
store m1, r15
div r15, r15, r13
load r15, m1
div r15, r15, r13
""",
    )
    print(" done, comparing values! \n", end="")

    assert hw_cpu.register == ip_cpu.register, (
        f"Registers are not the same! \n"
        + f"HW={hw_cpu.register} | IP={ip_cpu.register}"
    )

    assert hw_cpu.memory == ip_cpu.memory, (
        f"Memory are not the same! \n" + f"HW={hw_cpu.memory} | IP={ip_cpu.memory}"
    )
    print("[CPU] Memory: Checks out.")


def test_functions() -> None:
    print("[CPU] Function [cmp, jmp]:", end="")

    print(" handwritten,", end="")
    hw_cpu = core.CPU.create()
    core.fuckaround_compare(hw_cpu)
    print(" done,", end="")

    print(" interpreted,", end="")
    ip_cpu = core.CPU.create()
    ip_cpu.interpret(
        """
set r5, 420
set r10, 1
add r11, r11, r10
cmp r11, r5, 0b010
jmpeq 2
""",
    )

    print(" done, comparing values! \n", end="")

    assert hw_cpu.register == ip_cpu.register, (
        f"Registers are not the same! \n"
        + f"HW={hw_cpu.register} | IP={ip_cpu.register}"
    )

    assert hw_cpu.memory == ip_cpu.memory, (
        f"Memory are not the same! \n" + f"HW={hw_cpu.memory} | IP={ip_cpu.memory}"
    )
    print("[CPU] Loop: Checks out.")


def run() -> int:
    print("[CPU] Handwritten and Interpreted code test, start.")

    try:
        for test in [test_registers, test_memory, test_functions]:
            if ret_code := test():
                return ret_code
    except Exception as err:
        print(
            f"[CPU] Something fucked up:\n",
            "\n".join(traceback.format_exception(err)),
            "last known CPU state: ",
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(run())
