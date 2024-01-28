# SPDX-FileCopyrightText: 2024-present Ming Chung <73884404+minchus@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
import sys

if __name__ == "__main__":
    from scrape.cli import do_scrape

    sys.exit(do_scrape())
