File tagging with hard links
============================

This section has nothing to do with Dantalian, surprisingly.  Instead,
it will be about organizing your files with hard links.  Dantalian is
merely a tool to assist in doing the former, so you need to first
understand tagging with hard links before using Dantalian, and
inversely, this will probably be useful to you even if you do not use
Dantalian.

You must understand what hard links are.  Here are some relevant
external resources:

* `In Unix, what is a hard link? <https://kb.iu.edu/d/aibc>`_
* `Hard link (Wikipedia) <https://en.wikipedia.org/wiki/Hard_link>`_
* `What is the difference between a hard link and a symbolic link?
  <http://askubuntu.com/questions/108771/>`_

Some terminology to avoid ambiguity or confusion:

.. glossary::

    pathname
        A string which describes a location in the file system, either
        relative or absolute.

    filename
        A directory entry, or the parts of a pathname that are separated
        by slashes.  For the pathname :file:`/foo/bar/baz`, :file:`foo`,
        :file:`bar`, :file:`baz` are all filenames.  When referring to
        the filename of a :term:`link`, the filename is the last
        component in the pathname.  For example, the filename of the
        link :file:`pictures/pic1.jpg` is :file:`pic1.jpg`.  Each link
        has exactly one filename.

    link
        A directory entry pointing to a file.

    file
        A file in the file system, comprising of its inode and
        corresponding data blocks.  Each file has at least one link
        pointing to it; when no more links exist, the file is considered
        deleted, and its space is marked for recycling.

    directory
        Informally known as folders.  A special case of :term:`files
        <file>`, above, in that they have inodes, and links pointing to
        them, but creating more than one link to a directory is
        generally forbidden, so the link to a directory can be thought
        of as the directory itself.

Organizing files with hard links
--------------------------------

What does it mean to organize files with hard links?  It means you
create links to files in directories that they belong in.  If you
organize your "files" (links to files, strictly speaking) in
directories, congratulations, you are already doing it.  However,
there's a lot more organizational power in file systems that lay
untapped by regular users.

For example, you have a report for project A, so you put the "file"
(again, the link to the file using the above definition) in the
directory :file:`project-A`.  But the report was also presented in a
meeting, and you like to keep all the meeting materials in a specific
directory for easy reference.  What do you do?

You could make a copy of the report in the meeting notes directory, but
this has disadvantages (or potentially advantages).  First, there would
be two files on disk, resulting in twice the space usage.  Second, if
you change one of the files, the other file won't be changed.  You have
to remember to change the other file as well if you want them to be the
same.  It may be that you want the copy in the meeting notes directory
to stay static, to preserve the file as it was at a certain point in
time, in which case making a copy is advantageous.  Conversely, you may
want the two copies to be the same.  If you also want the file in four
other directories, suddenly you are using up six times the disk space,
and you'll need to remember to edit six different files when you want to
change something.

Alternatively, you can make a new link to the report file in the meeting
notes directory.  Since there is still only one file, you do not use
significantly more disk space (each link requires a piddling amount of
extra space), and any changes to the file are, well, reflected in the
file.  You can access the file using either link, but it's still the
same file.

That's organizing files with hard links in a nutshell.  Put "files" in
the directory they belong in, using any organization scheme you like,
and if you want to use a different organization scheme at the same time,
or you simply want the file to be in more than one place at once, make a
new link to it.  Simple, yet powerful and flexible.

Creating, removing, and breaking links
--------------------------------------

Links can be created using ``ln``.  ``ln foo bar`` creates the
link :file:`bar` pointing at the same file as :file:`foo`.  The
corresponding system call is ``link()`` (see :manpage:`link(2)`).

Links can be renamed (or moved, the two actions are synonymous) using
``mv``.  ``mv foo bar`` moves the link :file:`foo` to
:file:`bar`.  The link will still be pointing at the same file.  The
corresponding system call is ``rename()`` (see :manpage:`rename(2)`).

Links can be removed (unlinked) using ``rm``.  Note that this
removes links, not files.  When a file no longer has any links, there is
no longer any way to access it, but programs using the file can continue
doing so.  If there are no programs using it either, the disk space will
be open for reuse, and the file can be considered deleted (barring
recovery attempts using special software).  The corresponding system
call is ``unlink()`` (see :manpage:`unlink(2)`).

Take care not to accidentally break links.  Consider two links
:file:`foo` and :file:`bar` pointing to the same file.  If I make a copy
of the file (``cp foo baz``), the new link :file:`baz` is *not* pointing
at the same file as :file:`foo` or :file:`bar`; it is pointing at a new
file with the same contents (a copy of the original file).  Likewise, if
you remove :file:`foo` and create a new file (not link), :file:`foo`
will no longer be pointing at the same file as :file:`bar`.  This last
point may seem obvious, but *be careful when editing files*, since many
programs actually do this when saving files (remove the existing link
and create a new file) instead of writing to the original file.  For
example, Emacs will by default move the link for the file you are
editing as a backup and save the buffer as a new file, breaking your
links.  Most text editors will not break links (vim, vi, nano, gedit,
etc.), but large, graphical editors of all sorts (office suites, photo
editors, etc.) behave less reliably (this is an unfortunate consequence
of laypeople conflating files and links, and questionable programming).
You should test programs to see if they break links before taking
advantage of hard link organization.

Tagging with hard links
-----------------------

Tagging with hard links is just a slight perspective shift from
organizing with links.  All the material in the previous section is
sufficient for organization, but instead of thinking of a file as having
links in directories :file:`A`, :file:`B`, and :file:`C`, it may be
helpful to instead think of the file as being tagged ``A``, ``B``, and
``C``.  This way, to find all of the files with a given tag, you just
open the corresponding directory.

It's also helpful to conceptually set a root for organization, so that
you aren't thinking of directories :file:`/home/foo/projects/working`
and :file:`/home/foo/projects/completed`, but the tags ``working`` and
``completed``, with :file:`/home/foo/projects` as the root.

If you're feeling adventurous, you can even include the filename in your
mental model (think of a file tagged ``project-foo/specs.doc``,
``project-specs/foo.doc``, and ``document/12345.doc``).
