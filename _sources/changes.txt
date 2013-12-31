Changelog
=========

version 0.5
-----------

- New FUSE mount tree/node system.  Nodes are made/deleted dynamically
  in a FUSE mounted library.  Changes are saved on unmount and loaded on
  mount.  Tree is dumped as a JSON file, so is editable by hand if
  necessary.
- Wrote FUSE syscall specifications.
- Added ``rmnode`` socket command.
- Added unit tests.
- Bugfixes.
- Documentation improvements.
- Added ``mktag`` and ``rmtag`` commands.

version 0.4
-----------

- Wrote the library specification and revised the library module.
  Behavior should be better defined now in edge cases.
- Added multi-tag switch to ``tag`` and ``untag`` commands.
- Added ``clean`` command
- Added socket/fuse commands.  Framework has been laid to interact
  directly with virtual mounted FUSE libraries.
- Added ``mknode`` command
