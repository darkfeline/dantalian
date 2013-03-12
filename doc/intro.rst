Introduction
============

dantalian is a tag-based file organization system.  It uses hard links, by
creating hard links in subdirectories ("tags").  This provides a very flexible
and transparent system.  It provides a number of distinct advantages over
common database/metadata-based tagging system implementations.

#) Tag data is "stored" in the directory structure.  dantalian need not be
   installed to interact with it; dantalian merely provides a number of useful
   commands and scripts for interacting with it.  dantalian libraries can be
   freely copied to other systems.
#) Data does not need to be recalculated.  Everything follows tagged files
   dynamically, even if (a hard link of) the file is moved elsewhere on the
   file system.
#) Files do not need to have unique names.  (How well dantalian behaves with
   names is well-defined, but tricky.  Refer to :ref:`name-conflicts` for
   details.)
#) Tagging is file-type oblivious.  Even directories can be tagged, using
   symlinks.
#) Tags can be read on the file system level, so finding files in other
   applications, e.g. uploading a file in a web browser, opening a file in its
   respective editor, is trivial.
#) Certain tag operations are *extremely* cheap, namely tagging, untagging, and
   retrieving all files with a given tag.
#) Database-based tagging systems have a few ugly realities that they are
   forced to deal with.  First, unless it implements an entirely new file
   system altogether, it'll need to rely on having the file in a traditional
   hierarchical directory file system.  So, you'll still need to find a way to
   organize your files irrespective of tagging, whether that be throwing
   everything in one folder or somehow coming up with another organization
   scheme.  Often, this means that moving the files or renaming them ruins the
   tagging.  The other choice would be for the system to keep files organized
   internally, in which case the system often requires *every single file* have
   a unique filename (which, if I remember correctly, is what Tagsistant does,
   and one of the reasons I decided to create dantalian).

Unfortunately, there are also a few disadvantages.

#) Certain tag operations are relatively expensive, depending on library size.
#) Tagging doesn't follow the file, only the library.

I will be looking into adding some form of caching, as will as scripts to flush
metadata to files, to dantalian to minimize its disadvantages, thus keeping the
best of both worlds of data/metadata-based tagging and hard-link-based tagging.

.. note::
   dantalian uses hard links heavily.  Make sure you are familiar with how hard
   links work.  They are very powerful, but can be messy and/or dangerous if
   you are not familiar with them.  Especially take care not to accidently
   break hard links, e.g. by copying and removing files.  dantalian
   leverages the advantages hard links provide, but won't protect you from
   yourself!
