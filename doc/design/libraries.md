# Libraries

| Name                     | Description |
|--------------------------|-------------|
| *libqty_cli*         | RPC client functionality used by *qty-cli* executable |
| *libqty_common*      | Home for common functionality shared by different executables and libraries. Similar to *libqty_util*, but higher-level (see [Dependencies](#dependencies)). |
| *libqty_consensus*   | Stable, backwards-compatible consensus functionality used by *libqty_node* and *libqty_wallet* and also exposed as a [shared library](../shared-libraries.md). |
| *libqtyconsensus*    | Shared library build of static *libqty_consensus* library |
| *libqty_kernel*      | Consensus engine and support library used for validation by *libqty_node* and also exposed as a [shared library](../shared-libraries.md). |
| *libqtyqt*           | GUI functionality used by *qty-qt* and *qty-gui* executables |
| *libqty_ipc*         | IPC functionality used by *qty-node*, *qty-wallet*, *qty-gui* executables to communicate when [`--enable-multiprocess`](multiprocess.md) is used. |
| *libqty_node*        | P2P and RPC server functionality used by *qtyd* and *qty-qt* executables. |
| *libqty_util*        | Home for common functionality shared by different executables and libraries. Similar to *libqty_common*, but lower-level (see [Dependencies](#dependencies)). |
| *libqty_wallet*      | Wallet functionality used by *qtyd* and *qty-wallet* executables. |
| *libqty_wallet_tool* | Lower-level wallet functionality used by *qty-wallet* executable. |
| *libqty_zmq*         | [ZeroMQ](../zmq.md) functionality used by *qtyd* and *qty-qt* executables. |

## Conventions

- Most libraries are internal libraries and have APIs which are completely unstable! There are few or no restrictions on backwards compatibility or rules about external dependencies. Exceptions are *libqty_consensus* and *libqty_kernel* which have external interfaces documented at [../shared-libraries.md](../shared-libraries.md).

- Generally each library should have a corresponding source directory and namespace. Source code organization is a work in progress, so it is true that some namespaces are applied inconsistently, and if you look at [`libqty_*_SOURCES`](../../src/Makefile.am) lists you can see that many libraries pull in files from outside their source directory. But when working with libraries, it is good to follow a consistent pattern like:

  - *libqty_node* code lives in `src/node/` in the `node::` namespace
  - *libqty_wallet* code lives in `src/wallet/` in the `wallet::` namespace
  - *libqty_ipc* code lives in `src/ipc/` in the `ipc::` namespace
  - *libqty_util* code lives in `src/util/` in the `util::` namespace
  - *libqty_consensus* code lives in `src/consensus/` in the `Consensus::` namespace

## Dependencies

- Libraries should minimize what other libraries they depend on, and only reference symbols following the arrows shown in the dependency graph below:

<table><tr><td>

```mermaid

%%{ init : { "flowchart" : { "curve" : "basis" }}}%%

graph TD;

qty-cli[qty-cli]-->libqty_cli;

qtyd[qtyd]-->libqty_node;
qtyd[qtyd]-->libqty_wallet;

qty-qt[qty-qt]-->libqty_node;
qty-qt[qty-qt]-->libqtyqt;
qty-qt[qty-qt]-->libqty_wallet;

qty-wallet[qty-wallet]-->libqty_wallet;
qty-wallet[qty-wallet]-->libqty_wallet_tool;

libqty_cli-->libqty_util;
libqty_cli-->libqty_common;

libqty_common-->libqty_consensus;
libqty_common-->libqty_util;

libqty_kernel-->libqty_consensus;
libqty_kernel-->libqty_util;

libqty_node-->libqty_consensus;
libqty_node-->libqty_kernel;
libqty_node-->libqty_common;
libqty_node-->libqty_util;

libqtyqt-->libqty_common;
libqtyqt-->libqty_util;

libqty_wallet-->libqty_common;
libqty_wallet-->libqty_util;

libqty_wallet_tool-->libqty_wallet;
libqty_wallet_tool-->libqty_util;

classDef bold stroke-width:2px, font-weight:bold, font-size: smaller;
class qty-qt,qtyd,qty-cli,qty-wallet bold
```
</td></tr><tr><td>

**Dependency graph**. Arrows show linker symbol dependencies. *Consensus* lib depends on nothing. *Util* lib is depended on by everything. *Kernel* lib depends only on consensus and util.

</td></tr></table>

- The graph shows what _linker symbols_ (functions and variables) from each library other libraries can call and reference directly, but it is not a call graph. For example, there is no arrow connecting *libqty_wallet* and *libqty_node* libraries, because these libraries are intended to be modular and not depend on each other's internal implementation details. But wallet code is still able to call node code indirectly through the `interfaces::Chain` abstract class in [`interfaces/chain.h`](../../src/interfaces/chain.h) and node code calls wallet code through the `interfaces::ChainClient` and `interfaces::Chain::Notifications` abstract classes in the same file. In general, defining abstract classes in [`src/interfaces/`](../../src/interfaces/) can be a convenient way of avoiding unwanted direct dependencies or circular dependencies between libraries.

- *libqty_consensus* should be a standalone dependency that any library can depend on, and it should not depend on any other libraries itself.

- *libqty_util* should also be a standalone dependency that any library can depend on, and it should not depend on other internal libraries.

- *libqty_common* should serve a similar function as *libqty_util* and be a place for miscellaneous code used by various daemon, GUI, and CLI applications and libraries to live. It should not depend on anything other than *libqty_util* and *libqty_consensus*. The boundary between _util_ and _common_ is a little fuzzy but historically _util_ has been used for more generic, lower-level things like parsing hex, and _common_ has been used for qty-specific, higher-level things like parsing base58. The difference between util and common is mostly important because *libqty_kernel* is not supposed to depend on *libqty_common*, only *libqty_util*. In general, if it is ever unclear whether it is better to add code to *util* or *common*, it is probably better to add it to *common* unless it is very generically useful or useful particularly to include in the kernel.


- *libqty_kernel* should only depend on *libqty_util* and *libqty_consensus*.

- The only thing that should depend on *libqty_kernel* internally should be *libqty_node*. GUI and wallet libraries *libqtyqt* and *libqty_wallet* in particular should not depend on *libqty_kernel* and the unneeded functionality it would pull in, like block validation. To the extent that GUI and wallet code need scripting and signing functionality, they should be get able it from *libqty_consensus*, *libqty_common*, and *libqty_util*, instead of *libqty_kernel*.

- GUI, node, and wallet code internal implementations should all be independent of each other, and the *libqtyqt*, *libqty_node*, *libqty_wallet* libraries should never reference each other's symbols. They should only call each other through [`src/interfaces/`](`../../src/interfaces/`) abstract interfaces.

## Work in progress

- Validation code is moving from *libqty_node* to *libqty_kernel* as part of [The libqtykernel Project #24303](https://github.com/qty/qty/issues/24303)
- Source code organization is discussed in general in [Library source code organization #15732](https://github.com/qty/qty/issues/15732)
