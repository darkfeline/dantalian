---
layout: default
title: Dantalian
---

# Dantalian

Dantalian is a Python 3 library for file organization and tagging using hard
links.

In technical jargon, Dantalian can be described as a multi-dimensionally
hierarchical transparent lightweight file organization system.

## Features

* Organizes using the plain file system.
* Extremely flexible (no tag limit, no tag naming restrictions,
  hierarchical tags, no file naming restrictions, can tag all files and
  directories).
* Transparent to other applications, since it works directly with the
  file system.

## Recent news

<ul class="posts">
  {% for post in site.posts limit:2 %}
    <li>
      <span>{{ post.date | date_to_string }}</span>
      <a href="{{ site.baseurl }}{{ post.url }}">{{ post.title }}</a>
      {{ post.excerpt }}
    </li>
  {% endfor %}
  <li>
    (<a href="{{ site.baseurl }}/news.html">See more</a>)
  </li>
</ul>

## Links

Github repository
: <https://github.com/darkfeline/dantalian>

Bug tracker
: <https://github.com/darkfeline/dantalian/issues>

Documentation
: <http://dantalian.readthedocs.io>

Mailing list
: [dantalian-archiver-users@lists.sourceforge.net](https://lists.sourceforge.net/lists/listinfo/dantalian-archiver-users)
