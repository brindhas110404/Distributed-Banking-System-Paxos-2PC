# Local setup

Double-click **Start Banking.command**. Enter **3** clusters and **3** servers per cluster for the included CSV data.

The menu lets you proceed to the next transaction set, print balances, inspect the datastore, and view performance. Press Control-C to stop.

The executable is `bin/banking`. A local Go toolchain and dependencies are in `.tools`; double-click **Rebuild.command** after changing the source. No separate database service is needed.

The application creates `db_S1.db` through `db_S9.db` in this folder. Balances persist between runs. For a fresh simulation, stop the application and move those database files into a backup folder before restarting.

This is a working copy of the project from Downloads.

## After cloning from GitHub

Install Go 1.23.2 or later and a C compiler (on macOS, Xcode Command Line Tools). Run `./Rebuild.command`, then `./"Start Banking.command"`. The toolchain, executable, and local databases are excluded from Git. The included sample data requires 3 clusters with 3 servers each.
