"""
Overview
========

This module implements functionalities to find/replace patterns of text in an AreaVi instance
that has focus.

Usage
=====

In order to perform searches it is needed to press <Alt-slash> in NORMAL mode. It will show up
an input field where to insert tcl regex patterns. 

Once inserting the pattern then it is possible to find the next/previous occurrence
of the pattern by pressing <Alt-p>, <Alt-o> in the input text field
that is a Get widget.

For replacements, it is needed to first set a text in NORMAL mode by pressing <Alt-bracketright>.
Once the replacement is set then press <Alt-slash> to initiate the search process. Use <Alt-period>
to replace the current picked pattern of text and <Alt-comma> to replace all matched patterns.

It is possible to perform searches over selected regions of text, for such, select a region of text
then press <Alt-slash> and <Alt-slash> again to highligh all matched patterns in the region of text. In order
to replace all matched patterns inside a region of text, use <Alt-semicolon>.

Key-Commands
============

Mode: NORMAL
Event: <Alt-slash>
Description: Set a search pattern.

Mode: NORMAL
Event: <Alt-bracketright>
Description: Set a replacement pattern.

Mode: Get
Event: <Alt-o>
Description: Pick the previous pattern from the cursor position.

Mode: Get
Event: <Alt-comma>
Description: Replace all occurrences.

Mode: Get
Event: <Alt-p>
Description: Pick the next pattern from the cursor position.

Mode: Get
Event: <Alt-period>
Description: Replace the next matched pattern for the previously set replacement.

Mode: Get
Event: <Alt-slash>
Description: Highligh all matched patterns inside a selected region of text.

Mode: Get
Event: <Alt-semicolon>
Description: Replace all matched patterns inside a selected region of text for the
previously set replacement.

"""

from vyapp.ask import Get, Ask
from vyapp.app import root

class Find(object):
    def __init__(self, area, nolinestop=False, 
        regexp=True, nocase=True, exact=False, elide=False, 
        setup={'background':'green', 'foreground':'white'}):

        self.area  = area
        self.data  = ''
        self.index = None
        self.regex = ''

        area.tag_config('(CATCHED)', **setup)

        area.install(
        ('NORMAL', '<Alt-slash>', lambda event: self.start()), 
        ('NORMAL', '<Alt-bracketright>', lambda event: self.set_data()))

        self.opts = {'nolinestop': nolinestop, 'regexp': regexp,
        'nocase': nocase, 'exact': exact,'elide': elide}

    def start(self):
        self.index = ('insert', 'insert')
        get = Get(self.area, events={
        '<Alt-o>': self.up, '<Escape>': lambda wid: self.cancel(), 
        '<Alt-p>': self.down, '<Return>': self.set_regex,
        '<Alt-slash>':  self.pick_matches,
        '<Alt-period>': self.replace_on_cur,
        '<Alt-semicolon>': self.replace_on_selection, 
        '<Alt-comma>': self.replace_all_matches, 
        '<Control-n>': self.toggle_nocase_option,
        '<Control-e>': self.toggle_exact_option,
        '<Control-i>': self.toggle_elide_option,
        '<Control-l>': self.toggle_nolinestop_option},
        default_data=self.regex)

    def toggle_nocase_option(self, wid):
        self.opts['nocase'] = False if self.opts['nocase'] else True
        root.status.set_msg('nocase=%s' % self.opts['nocase'])

    def toggle_exact_option(self, wid):
        self.opts['exact'] = False if self.opts['exact'] else True
        root.status.set_msg('exact=%s' % self.opts['exact'])

    def toggle_elide_option(self, wid):
        self.opts['elide'] = False if self.opts['elide'] else True
        root.status.set_msg('elide=%s' % self.opts['elide'])

    def toggle_nolinestop_option(self, wid):
        self.opts['nolinestop'] = False if self.opts['nolinestop'] else True
        root.status.set_msg('nolinestop=%s' % self.opts['nolinestop'])

    def set_data(self):
        ask = Ask(self.area, default_data = self.data.encode('string_escape'))
        self.data = ask.data.decode('string_escape')

    def set_regex(self, wid):
        self.regex = wid.get()
        self.area.tag_remove('(CATCHED)', '1.0', 'end')
        return True

    def cancel(self):
        self.regex = ''
        self.area.tag_remove('(CATCHED)', '1.0', 'end')
        return True

    def up(self, wid):
        regex = wid.get()
        self.index = self.area.ipick('(CATCHED)', regex, index='insert', 
        stopindex='1.0', backwards=True, **self.opts)

    def down(self, wid):
        regex = wid.get()
        self.index = self.area.ipick('(CATCHED)', regex, index='insert', 
        stopindex='end', **self.opts)

    def pick_matches(self, wid):
        regex = wid.get()
        self.area.map_matches('(CATCHED)', 
        self.area.collect('sel', regex, **self.opts))

    def replace_on_cur(self, wid):
        regex = wid.get()
        self.area.replace(regex, self.data, self.index[0], **self.opts)

    def replace_on_selection(self, wid):
        regex = wid.get()
        self.area.replace_ranges('sel', regex, self.data, **self.opts)

    def replace_all_matches(self, wid):
        regex = wid.get()
        self.area.replace_all(regex, self.data, '1.0', 'end', **self.opts)

install = Find



