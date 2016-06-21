# -*- coding: utf-8 -*-
from django import  forms
import os


class DocumentForm(forms.Form):
    docfile = forms.FileField(label='Select a file')


class Ssh_exec(forms.Form):
    username = forms.CharField(max_length=64, label=u'传输使用帐号:')
    cmd_line  = forms.CharField(max_length=256, label=u'命令:')
