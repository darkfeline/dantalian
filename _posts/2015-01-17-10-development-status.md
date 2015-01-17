---
layout: post
title: 1.0 development status
date: 2015-01-17 07:33:13 +0000
---

I thought I would post an update since it's been a while since I've done so.

I'm currently working on version 1.0.  It's not quite done yet, but there are
some important changes I would like to point out beforehand.  A [dev branch] is
available to look at or play with.

[dev branch]: https://github.com/darkfeline/dantalian/tree/1.0

  - Directory tagging has been changed.  The old way involved placing
    directories in a Dantalian-specific location, and then hard linking
    symlinks as per regular file tagging.  This is bad as symlinks are fragile
    to path changes[^1], but more importantly, hard linking symlinks is not
    portable.  POSIX does not require it as far as I can tell; the fact that
    this is possible in ext4, the only one I've tried, is just an
    implementation detail than a feature, I would think.  The old way also
    involved ugly hacks for fixing symlinks when paths were changed.

    The new way still uses symlinks, but implicitly assumes that symlinks to
    the same directory are tags for that directory.  Also, tag information is
    stored in a special file in each directory so that each directory's
    symlinks can be regenerated, in case paths are changed or other file system
    restructuring happens.

    Migration: If you don't have a lot of tagged directories, you can use the
    new `revert` command in version 0.6 after untagging the directories using
    the old version, then retag them using the new version.  If you have a lot
    of tagged drectories, you can write a script to dump the tags, and then
    import them in the new version.

  - A handful of new commands for the new directory tagging method.

  - New import/export commands.  These aren't intended for backup, but for
    programmatically exporting/importing tags to/from other applications.

  - Removal of FUSE features.  After I've played with it a bit, I want to
    redesign it from scratch.  I also need to redesign it for the new directory
    tagging method.  These will be re-added sometime later in the 1.x branch.

  - The API has been completely broken, thanks to heavy refactoring.  Check the
    current branch to see what it looks like.

This release marks Dantalian's transition to stable development, for the 1.x
branch.  Mainly, this means that I will stop breaking APIs and such so that
everyone (myself included) can use Dantalian without having to worry about
stuff breaking.  Thus, the 1.x branch will be devoted solely to bug fixes and
new minor features, with no design or API changes.

[^1]: Hard links are completely invulnerable to name or path changes; this is
      one of Dantalian's advantages.
