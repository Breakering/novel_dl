#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Breakering"
# Date: 18-8-10


def write_file(file_path, info, pattern='w'):
    with open(file_path, pattern) as f:
        f.write(info)


def read_file(file_path, pattern='r'):
    with open(file_path, pattern) as f:
        return f.read()
