from django.shortcuts import render
from django.shortcuts import render_to_response
from client_paramiko import ParamikoClient
# from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from models import hosts, Document, conf, Doc_select, logs
from forms import DocumentForm,  Ssh_exec
from psshthread import do_pscp,do_pssh
import os,time,re

# Create your views here.

def delfile(request):
    delf = request.GET.get("delf", "none")
    delf_name = str(delf)
    try:
        df = Document.objects.get(docfile=delf_name)
        df.delete()
        if os.path.isfile(delf_name):
            print "delete file", delf_name
            os.remove(delf_name)
        else:
            print "no such file!"
    except Exception,e:
        print Exception, ":", e
    documents = Document.objects.all()
    form = DocumentForm() # A empty, unbound form
    return render_to_response(
        'upload.html',
        {'documents': documents, 'form': form},
       #  context_instance=RequestContext(request)
    )

def pushfile(request):
    log_str = time.asctime().split()[3]
    host_list = []
    port_list = []
    host = hosts.objects.all()
    for h in host:
        host_list.append(h.hostip)
        port_list.append(h.port)
    conf_flag = conf.objects.all()
    flags = {}
    for c in conf_flag:
        flags["par"] = c.par
        flags["keyfile"] = c.keyfile
        flags["logdir"] = c.logdir + "/pscp/" + log_str
        flags["type"] = "pscp"
    pscp_logs = logs.objects.filter(logtype="pscp")
    if request.method == 'POST':
        # form = Doc_select(request.POST)
        # if form.is_valid():
        pfile = request.POST['pfile']
        username = request.POST['username']
        rpath = request.POST['rpath']
        # print pfile,username,rpath
        if not re.match("^/", rpath):
            print "Remote path %s must be an absolute path" % rpath
        pput = do_pscp(host_list, port_list, username, pfile, rpath, flags)
        return HttpResponseRedirect(reverse('ansi.views.pushfile'))
    else:
        form = Doc_select()
    #return render(request, "pushfile.html", {"host": host, "form":form, "pscp_logs":pscp_logs}, context_instance=RequestContext(request))
    return render(request, "pushfile.html", {"host": host, "form":form, "pscp_logs":pscp_logs})

def pssh(request):
    log_str = time.asctime().split()[3]
    host_list = []
    port_list = []
    host = hosts.objects.all()
    for h in host:
        host_list.append(h.hostip)
        port_list.append(h.port)
    conf_flag = conf.objects.all()
    flags = {}
    for c in conf_flag:
        flags["par"] = c.par
        flags["keyfile"] = c.keyfile
        flags["logdir"] = c.logdir + "/pssh/" + log_str
        flags["type"] = "pssh"
    pssh_logs = logs.objects.filter(logtype="pssh")
    if request.method == 'POST':
        form = Ssh_exec(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            cmd = form.cleaned_data['cmd_line']
            pexec = do_pssh(host_list, port_list, username, cmd, flags)
            return HttpResponseRedirect(reverse('ansi.views.pssh'))
    else:
        form = Ssh_exec()
    #return render(request, "pssh.html", {"host": host, "form":form, "pssh_logs":pssh_logs}, context_instance=RequestContext(request))
    return render(request, "pssh.html", {"host": host, "form":form, "pssh_logs":pssh_logs})

def upload(request):
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(docfile = request.FILES['docfile'])
            newdoc.save()

            # Redirect to the document list after POST
            return HttpResponseRedirect(reverse('ansi.views.upload'))
    else:
        form = DocumentForm() # A empty, unbound form

    # Load documents for the list page
    documents = Document.objects.all()

    # Render list page with the documents and the form
    return render_to_response(
        'upload.html',
        {'documents': documents, 'form': form},
        #context_instance=RequestContext(request)
    )

