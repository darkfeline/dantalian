Hard Links Tutorial
===================

dantalian relies extensively on hard links, which is a concept some/many
people may not be familiar with.  Therefore, I have included a short
tutorial.  If you are already familiar with hard links and file systems,
you may safely skip this section.

First, you need to understand how a file system works.  All data stored
on a hard drive or any other device is strictly linear, like a book.  A
hard drive is also like a book in that there are "pages".  So, for
example, the data for a picture may be on pages 13-36 and 75-78.  As you
can see, there's no guarantee that all the data are contiguous.  It's as
messy as it sounds.  Thus, in order to organize files, we use "table of
contents" called directories and files.

So, a directory would look like:

* games table of contents (directory)

  * shooting  page 13 (<location on hard drive>)
  * puzzle  page 18 (<location on hard drive>)
  * other  page 30 (<location on hard drive>)

Directories are just simple lists mapping names to locations.  The
locations may either be other directories or files.  However, they won't
point directly to the file data on the disk, since we won't know what to
make of it (do we look at everything on page 30, or just the first
paragraph? or maybe it is split between multiple pages?).  So file
systems have what is called an *inode*, which is a single file which
contains all of this information, with which the file system can use to
access the file data proper.

So, the above example looks like this:

- games table of contents (directory)

  - shooting  page 13 (inode 13)
  - puzzle  page 18 (inode 18)
  - other  page 30 (inode 30)

- inode 13: Look at everything on pages 20-21.  This is in English.
- inode 18: Look at everything on pages 50-55 and pages 60-61.  These
  are crossword puzzles and sudoku puzzles.
- indoe 30: Look at the bottom half of page 35.  This is a note in
  Zimbabwean.

This leads to a few interesting things.  First, inodes do not contain
file names.  Remember that the name is defined in the directory, which
then points to a location (an inode).  Thus, a file named "hi" in a
directory will have an entry that says "the inode for hi is at XXX".
So, what's stopping you from having two entries in two directories point
to the same inode?  Nothing.  When you do so, it is called hard linking.
Files that are hard linked are essentially the same file, but it appears
in two different places with different names.  Basically, think of it as
having different names for the same file.  This allows us to organize a
file by putting it in multiple places and is insanely useful.
dantalian leverages that and puts it to use in a file-tagging system.
