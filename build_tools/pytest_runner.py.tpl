"""The pytest entry point."""
import signal
import sys

import pytest


def quit_pytest(signum: int, _) -> None:
    sys.exit(signum)

if __name__ == '__main__':
    signal.signal(signal.SIGTERM, quit_pytest)

    sys.argv = sys.argv + [{args}]  # pylint: disable=line-too-long

    raise SystemExit(pytest.console_main())
