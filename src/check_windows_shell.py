"""Aborta a build (exit code != 0) se não estiver rodando em cmd.exe ou PowerShell nativos do Windows."""

import ctypes
import os
import sys

RED = "\033[91m"
RESET = "\033[0m"


def enable_ansi_on_windows() -> None:
    kernel32 = ctypes.windll.kernel32
    handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
    mode = ctypes.c_uint32()
    if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
        kernel32.SetConsoleMode(handle, mode.value | 0x0004)  # ENABLE_VIRTUAL_TERMINAL_PROCESSING


def print_red(text: str) -> None:
    if os.name == "nt":
        try:
            enable_ansi_on_windows()
        except OSError:
            print(text)
            return
    print(f"{RED}{text}{RESET}")


def running_in_windows_native_shell() -> bool:
    if os.name != "nt":
        return False
    if "WSL_DISTRO_NAME" in os.environ or "WSL_INTEROP" in os.environ:
        return False
    if "MSYSTEM" in os.environ:  # Git Bash / MSYS2
        return False
    shell = os.environ.get("SHELL", "").lower()
    if "bash" in shell or "/sh" in shell:
        return False
    return True


if __name__ == "__main__":
    if running_in_windows_native_shell():
        print_red(
            "AVISO: Gerando executável `gen_fix_video` em um terminal Windows nativo"
        )        
        sys.exit(0)

    print_red(
        "AVISO: `gen_fix_video` precisa ser executado em um terminal Windows nativo "
        "(cmd ou PowerShell). Troque de terminal e rode novamente."
    )
    sys.exit(1)
