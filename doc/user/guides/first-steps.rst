First Steps
===========

.. warning::
   This guide may be out of date.

What is dantalian?
------------------

**What is dantalian?**

dantalian is a multi-dimensionally hierarchical tag-based file
organization system.

**A short description in English please.**

Sorry, I'll have to use a few diagrams too.  Say I love listening to
music and I have a bunch of music on my hard drive.  A common way to
organize music is like this::

   Genre/
      Artist/
         Album/
            song

The problem is, I have this song that's a single.  No problem, I can
just do this::

   Genre/
      Artist/
         single

But what if it's a collab between two different artists?  Or if the song
mixes genres?  Or if I like my songs grouped by where I listen to them
(in the car, at home, at work)?  I'm screwed, that's what.

A multi-dimensional hierarchy means that I can do this::

   Genres/
      Anime/
         traumerei.mp3
      Rock/
         traumerei.mp3
   Artists/
      Haruka Tomatsu/
         traumerei.mp3
         Gen'ei OP/
            traumerei.mp3
   Albums/
      Gen'ei OP/
         traumerei.mp3
      Anison Collection/
         traumerei.mp3
   Anime/
      Series/
         Gen'ei wo Kakeru Taiyou/
            Gen'ei OP/
               traumerei.mp3
   Rating/
      5/
         traumerei.mp3
      4/
      3/
      2/
      1/

**Wait, that looks like a pain to manage.  And you have like ten copies
of one song, doesn't that waste space?**

Actually, thanks to the magic of hard links, there's only one copy of
``traumerei.mp3``.  It takes up the space of one copy, and if you change
the song in any of the places it appears, all of them change.  They're
all the same file.

Don't worry, dantalian makes managing this easy as pie.

**Oh okay.  Wait, doesn't that look like metadata tags on .mp3 files?**

That's the tag-based part.  Normally, if you wanted to search for a song
with a tag, you'd have to open up a music manager like amaroK or iTunes.
With dantalian, if you want to find all songs tagged with the ``Pop``
genre, you just go to the folder ``Genres/Pop`` and all the files are
there.

**Cool.  What about multi-tag searches and such?**

dantalian can do that do, but that's a slightly more advanced feature
for a little later.

**So what can I use dantalian for?**

Everything.  All files, and even folders as well.  You can then organize
them however you want.  Knock yourself out.

**Holy cow, I will, thanks.  So how do I get started?**

Install dantalian (See :ref:`install`).  No further setup necessary.

Using dantalian
---------------

**Er, how do I use this thing?**

Let's run through an example.  Say you have a single song in your
``Music`` folder and want to organize it (hey, it's an example).

Making a library
^^^^^^^^^^^^^^^^

We start by making a library::

   ~ $ mkdir library
   ~ $ dantalian init library

Or you can do::

   ~ $ mkdir library
   ~ $ cd library
   library $ dantalian init

Right now our directories look like this::

   Music/
      song.mp3
   library/

Making tags and tagging
^^^^^^^^^^^^^^^^^^^^^^^

Let's make a bunch of directories for how we want to organize our song::

   library/
      Genres/
         Rock/
      Artists/
         Bob/
         Charlie/
      Albums/
         B&C's First Album/

Next, let's tag our song.  dantalian commands need to work on a library,
so you either need to be working in the library or indicate the library
with an optional argument (all of the following are identical)::

   library $ dantalian tag //Genres/Rock ../Music/song.mp3
   Genres $ dantalian tag //Genres/Rock ../../Music/song.mp3
   ~ $ dantalian --root library tag //Genres/Rock Music/song.mp3
   Music $ dantalian --root ~/library tag //Genres/Rock song.mp3

(You can do all of the above if you want.  dantalian doesn't do anything
if it sees that the file is already tagged.)

So let's tag our song::

   library $ dantalian tag //Genres/Rock ../Music/song.mp3
   library $ dantalian tag //Artists/Bob ../Music/song.mp3
   library $ dantalian tag //Artists/Charlie ../Music/song.mp3
   library $ dantalian tag //Albums/B&C's First Album ../Music/song.mp3

Now our library looks like this::

   library/
      Genres/
         Rock/
            song.mp3
      Artists/
         Bob/
            song.mp3
         Charlie/
            song.mp3
      Albums/
         B&C's First Album/
            song.mp3

That wasn't hard, was it?  Let's see what tags our song has::

   library $ dantalian tags ../Music/song.mp3
   //Genres/Rock
   //Artists/Bob
   //Artists/Charlie
   //Albums/B&C's First Album

Handy!

Some other things
^^^^^^^^^^^^^^^^^

If you want, you can add an alias for dantalian so you don't have to
type it every time::

   # for bash
   library $ alias d=dantalian
   library $ d untag /Artists/Bob Genres/Rock/song.mp3

Here we also see the untag command in action.  Note that we used
``Genres/Rock/song.mp3`` instead of ``../Music/song.mp3``.  Remember,
all of these tagged files are the same, so you can do
``Artists/Bob/song.mp3``, ``Artists/Charlie/song.mp3`` and
``"Albums/B&C's First Album/song.mp3"`` as well.

Check the :doc:`manpage </manpage>` for all of the available commands.
We'll be covering a few more of them below.

Tagging directories
^^^^^^^^^^^^^^^^^^^

We untagged ``song.mp3`` because it is Charlie's song, although the
album ``B&C's First Album`` is by both Bob and Charlie.  So, can we tag
the album with both artists?  (Remember I said you can do anything with
dantalian?)

First, you need to convert it because it's a directory::

   library $ d convert "/Albums/B&C's First Album"
   library $ d tag -s "Albums/B&C's First Album" //Artists/Bob //Artists/Charlie

Notice we used the ``-s`` switch to flip the tag and the file for the
``tag`` command.  Normally, you would give it one tag and one or more
files, but with the ``-s`` option you give it one file and one or more
tags.  You can use either for all of your tagging needs.

Closing
-------

**Wait, that's it?**

Nope.  dantalian has a few more very powerful features, but what we
covered is enough to get started and familiarize yourself with it.  But
dantalian by itself really is quite simple; it's more what you do with
it.  A hammer and a saw is just a lump of metal on a stick for hitting
things and a thin piece of metal for cutting, but you can build grand
structures with them.  It's the same with dantalian, so play around with
these basic features and see how you can make use of them.
