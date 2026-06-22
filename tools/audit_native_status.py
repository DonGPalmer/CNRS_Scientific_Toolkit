#!/usr/bin/env python3
"""Print the CNRS native-status registry as a markdown table."""

from cnrs.native_status import status_table


def main() -> None:
    print(status_table())


if __name__ == "__main__":
    main()
