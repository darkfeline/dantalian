---
layout: post
title: "Future plans"
date: 2014-07-29 22:16:02
---

Development of Dantalian has been somewhat bumpy as I was figuring out
how exactly it should be and what it should do, as well as figuring how
best to structure the project in terms of documentation, websites,
files, and info.  Now that I have most of it figured out and Dantalian
is relatively stable, here are my plans for the future:

1. Add caching to Dantalian.  With large libraries, doing tag searches
   becomes costly time-wise, and the cost is unavoidable.  However, the
   searching can be done in advance and cached, with the downside of
   requiring regular updating and not always being up to date.  The
   dynamic is similar to that of `find` and `locate` in GNU findutils.

2. Move FUSE features to a separate application, probably written in Go.
   Writing such a service in Python is unacceptable performance-wise,
   especially with CPython's poor threading.

Those are the most pressing and clearest goals, but there are some
other minor things as well (such as implementing `find` in Python to
remove the dependency on findutils and more comprehensive tests).
