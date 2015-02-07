# CHANGES

## version 1.0

This version changes more things than not, so just re-read the documentation.

## version 0.6

* Commands can now take multiple arguments where applicable (e.g.,
  `mktag`).
* Add `revert` command for reverting ("unconverting") converted
  directories.  It only works on directories that only have one tag.
* `mktag` and `rmtag` are changed to only work on unique tag qualifiers,
  to avoid ambiguity.  The old functionality using paths can be done
  simply using `mkdir` and `rmdir` (or `rm -r`).
* New multi-tag, multi-file `tag` and `untag` commands using the `-t`
  and `-f` flags.
* Revamped command line argument parsing.
* Library initialization moved further down execution process.  Poorly
  formed commands should now fail faster, without initializing the
  library first.
* dantalian now uses `-print0` when calling `find`.  Thus, it should now
  be safe to use Dantalian with filenames and directory names that
  contain newlines.  You shouldn't use newlines in filenames ever, but
  now dantalian supports it.
* Added `--print0` option to `tags`, `find` commands.
* Rewrote documentation.

## version 0.5

* New FUSE mount tree/node system.  Nodes are made/deleted dynamically
  in a FUSE mounted library.  Changes are saved on unmount and loaded on
  mount.  Tree is dumped as a JSON file, so is editable by hand if
  necessary.
* Wrote FUSE syscall specifications.
* Added `rmnode` socket command.
* Added unit tests.
* Bugfixes.
* Documentation improvements.
* Added `mktag` and `rmtag` commands.

## version 0.4

* Wrote the library specification and revised the library module.
  Behavior should be better defined now in edge cases.
* Added multi-tag switch to `tag` and `untag` commands.
* Added `clean` command.
* Added socket/fuse commands.  Framework has been laid to interact
  directly with virtual mounted FUSE libraries.
* Added `mknode` command.
