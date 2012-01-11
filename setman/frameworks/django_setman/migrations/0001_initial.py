# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Settings'
        db.create_table('setman_settings', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('data', self.gf('setman.backends.django.fields.JSONField')(default='', blank=True)),
            ('create_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('update_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('django_setman', ['Settings'])


    def backwards(self, orm):
        
        # Deleting model 'Settings'
        db.delete_table('setman_settings')


    models = {
        'django_setman.settings': {
            'Meta': {'object_name': 'Settings', 'db_table': "'setman_settings'"},
            'create_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'data': ('setman.backends.django.fields.JSONField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'update_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['django_setman']
