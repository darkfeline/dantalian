#!/usr/bin/env python
# encoding: utf-8

top = '.'
out = 'waf_build'
VERSION = '0.6'


def options(ctx):
    ctx.add_option('--man-prefix', action='store', default='/usr/share/man',
                   dest='man_prefix')


def configure(ctx):
    ctx.env['MAN_PREFIX'] = ctx.options.man_prefix


def build(ctx):
    ctx.recurse('man')
