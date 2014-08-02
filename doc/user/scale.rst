Performance and Scalability
===========================

Note that these are rough numbers and predictions based on theory.
These assume a Linux kernel compiled with common flags and an ext4 file
system.

Space cost
----------

Each tag for each file costs about 20-200B (completely unverified, but
should be about right).  This is the cost for each link, or each entry
in a directory.

Each directory (or new tag) costs an upfront 2kB or so, but that space
is used up by each link in it, covering for the costs mentioned above
for each link, so the net cost of each tag is minimal.

This space cost can be thought of as caching the results of single tag
file lookup queries.

Time cost
---------

File access is constant.  In fact it is no different than just opening a
file regularly.  Looking up all files with a given tag is linear to the
number of files with that tag;  this is the minimum theoretically
possible.  Looking up all of the tags of the file is much uglier,
requiring a full traversal of the directory tree.  However, in practice
this runs fairly quickly due to how file systems are designed.  I also
find that querying files based on tags is done much more commonly than
looking up the tags any given file has.

Hard limits
-----------

ext4 has a hard 65000 limit on links to inodes.  This means that each
file can have at most 65000 tags and each tag can have at most 64998
subtags (each directory can have at most 64998 subdirectories, as each
subdirectory has a link to the parent (:file:`..`), and each directory
has a link to itself (:file:`.`)).

Linux has a limit on how many levels of symbolic links there can be in a
single lookup.  I think this is 40, but can be different depending on
how the kernel was compiled.  This means that Dantalian only supports 40
(or however many your kernel supports) levels deep of converted
directories.

Practical considerations
------------------------

The first obstacle that you will likely encounter when scaling Dantalian
up is size constraints, since everything must reside on one file system.
This obstacle is encountered once the amount of data you are trying to
organize exceeds the amount of space of one storage device (say, a 1 TB
hard disk drive).  This can be circumvented by using LLVM and creating a
virtual file system that spans multiple physical storage devices.

Any time constraints can be ameliorated with additional caching if
required, but otherwise probably cannot be improved further due to
mathematical limits.

The only other tricky problem is the hard limits mentioned above.
Unless you are trying to organize truly vast amounts of data (where the
metadata exceeds the data [1]_), they probably won't be an issue.  If
they are, however (either more than 64998 subtags under a single tag, or
more than 40 levels of converted directories that you need to access),
then the workaround would be to use customized file systems or kernels
to bypass these hard limits.

.. [1]
    You should probably clarify in your head what exactly your needs
    are.  If you are storing vast amounts of metadata, so much so that
    the metadata itself can be considered data, you should definitely be
    using some sort of database instead.
