from django.db import models
from django.forms import ModelForm
from django import forms

# Create your models here.


class hosts(models.Model):
    hostip = models.IPAddressField()
    hostname = models.CharField(max_length=64, default="unknow")
    port = models.IntegerField(max_length=16, default=22)
    project = models.CharField(max_length=64, default="unknow")

class Document(models.Model):
    docfile = models.FileField(upload_to='documents/%Y/%m/%d')

    def __unicode__(self):
        return self.docfile

class conf(models.Model):
    keyfile = models.CharField(max_length=64, default="/home/foura/.ssh/id_rsa")
    logdir = models.CharField(max_length=64, default="/home/foura/pssh/pscp")
    # max number of parallel threads
    par = models.IntegerField(max_length=16, default=32)

class logs(models.Model):
    progress = models.CharField(max_length=16)
    stime = models.CharField(max_length=32)
    tstamp = models.CharField(max_length=32)
    hostip = models.IPAddressField()
    status = models.CharField(max_length=32)
    exc = models.CharField(max_length=256)
    logtype = models.CharField(max_length=256)

class Doc_select(ModelForm):
    pfile = forms.ModelChoiceField(queryset=Document.objects.all(),to_field_name="docfile", label='choice a file')
    username = forms.CharField(max_length=64, label='user')
    rpath = forms.CharField(max_length=64, label='remote path')

    class Meta:
        model = Document
