from django.contrib import admin
import models
# Register your models here.


class hosts_admin(admin.ModelAdmin):
    search_fields = ['hostip',]
    list_display = ('hostip', 'hostname', 'port', 'project',)

class conf_admin(admin.ModelAdmin):
    list_display = ('keyfile', 'logdir', 'par', )

admin.site.register(models.hosts, hosts_admin)
admin.site.register(models.conf, conf_admin)
