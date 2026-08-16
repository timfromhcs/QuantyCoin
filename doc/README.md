QTY Core
=============

Setup
---------------------
QTY Core is the original QTY client and it builds the backbone of the network. It downloads and, by default, stores the entire history of QTY transactions, which requires a few hundred gigabytes of disk space. Depending on the speed of your computer and network connection, the synchronization process can take anywhere from a few hours to a day or more.

To download QTY Core, visit [qtycore.org](https://qtycore.org/en/download/).

Running
---------------------
The following are some helpful notes on how to run QTY Core on your native platform.

### Unix

Unpack the files into a directory and run:

- `bin/qty-qt` (GUI) or
- `bin/qtyd` (headless)

### Windows

Unpack the files into a directory, and then run qty-qt.exe.

### macOS

Drag QTY Core to your applications folder, and then run QTY Core.

### Need Help?

* See the documentation at the [QTY Wiki](https://en.qty.it/wiki/Main_Page)
for help and more information.
* Ask for help on [QTY StackExchange](https://qty.stackexchange.com).
* Ask for help on #qty on Libera Chat. If you don't have an IRC client, you can use [web.libera.chat](https://web.libera.chat/#qty).
* Ask for help on the [QTYTalk](https://qtytalk.org/) forums, in the [Technical Support board](https://qtytalk.org/index.php?board=4.0).

Building
---------------------
The following are developer notes on how to build QTY Core on your native platform. They are not complete guides, but include notes on the necessary libraries, compile flags, etc.

- [Dependencies](dependencies.md)
- [macOS Build Notes](build-osx.md)
- [Unix Build Notes](build-unix.md)
- [Windows Build Notes](build-windows.md)
- [FreeBSD Build Notes](build-freebsd.md)
- [OpenBSD Build Notes](build-openbsd.md)
- [NetBSD Build Notes](build-netbsd.md)
- [Android Build Notes](build-android.md)

Development
---------------------
The QTY repo's [root README](/README.md) contains relevant information on the development process and automated testing.

- [Developer Notes](developer-notes.md)
- [External Audit Briefing](audit-briefing.md)
- [Productivity Notes](productivity.md)
- [Release Process](release-process.md)
- [Source Code Documentation (External Link)](https://doxygen.qtycore.org/)
- [Translation Process](translation_process.md)
- [Translation Strings Policy](translation_strings_policy.md)
- [JSON-RPC Interface](JSON-RPC-interface.md)
- [Unauthenticated REST Interface](REST-interface.md)
- [Shared Libraries](shared-libraries.md)
- [BIPS](bips.md)
- [Dnsseed Policy](dnsseed-policy.md)
- [Benchmarking](benchmarking.md)
- [Internal Design Docs](design/)

### Resources
* Discuss on the [QTYTalk](https://qtytalk.org/) forums, in the [Development & Technical Discussion board](https://qtytalk.org/index.php?board=6.0).
* Discuss project-specific development on #qty-core-dev on Libera Chat. If you don't have an IRC client, you can use [web.libera.chat](https://web.libera.chat/#qty-core-dev).

### Miscellaneous
- [Assets Attribution](assets-attribution.md)
- [qty.conf Configuration File](qty-conf.md)
- [CJDNS Support](cjdns.md)
- [Files](files.md)
- [Fuzz-testing](fuzzing.md)
- [I2P Support](i2p.md)
- [Init Scripts (systemd/upstart/openrc)](init.md)
- [Managing Wallets](managing-wallets.md)
- [Multisig Tutorial](multisig-tutorial.md)
- [P2P bad ports definition and list](p2p-bad-ports.md)
- [PSBT support](psbt.md)
- [Reduce Memory](reduce-memory.md)
- [Reduce Traffic](reduce-traffic.md)
- [Tor Support](tor.md)
- [Transaction Relay Policy](policy/README.md)
- [ZMQ](zmq.md)

License
---------------------
Distributed under the [MIT software license](/COPYING).
