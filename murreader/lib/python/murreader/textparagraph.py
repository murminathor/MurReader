#!/usr/bin/env python
# -*- mode: python; coding: koi8-r; -*-

class TextParagraph:
    def __init__(self, type='text'):

        self.type = type # text / title / subtitle / image / footnote
        self.data = ''

        self.styles = [] # [(begin, end, style), (begin, end, style), ...]
                         # style: emphasis / strong / superscript

        self.footnotes = []
        self.href = ''

        self.title_level = 0


