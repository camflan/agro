# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Entry'
        db.create_table('agro_entry', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('owner_user', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('source_type', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('allow_comments', self.gf('django.db.models.fields.NullBooleanField')(default=False, null=True, blank=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True, blank=True)),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('agro', ['Entry'])

        # Adding unique constraint on 'Entry', fields ['title', 'timestamp', 'source_type']
        db.create_unique('agro_entry', ['title', 'timestamp', 'source_type'])

        # Adding model 'Tweet'
        db.create_table('agro_tweet', (
            ('entry_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['agro.Entry'], unique=True, primary_key=True)),
            ('tweet_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('source', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('agro', ['Tweet'])

        # Adding model 'Photo'
        db.create_table('agro_photo', (
            ('entry_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['agro.Entry'], unique=True, primary_key=True)),
            ('photo_id', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('server', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('secret', self.gf('django.db.models.fields.CharField')(max_length=200, null=True)),
            ('original_secret', self.gf('django.db.models.fields.CharField')(max_length=200, null=True)),
            ('original_format', self.gf('django.db.models.fields.CharField')(max_length=4, null=True)),
            ('num_comments', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('taken_at', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('uploaded_at', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('exif', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('agro', ['Photo'])

        # Adding unique constraint on 'Photo', fields ['photo_id', 'server']
        db.create_unique('agro_photo', ['photo_id', 'server'])

        # Adding model 'Song'
        db.create_table('agro_song', (
            ('entry_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['agro.Entry'], unique=True, primary_key=True)),
            ('artist', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('album', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('song_mbid', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('artist_mbid', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('album_mbid', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('streamable', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('small_image', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('med_image', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('large_image', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal('agro', ['Song'])

        # Adding model 'Bookmark'
        db.create_table('agro_bookmark', (
            ('entry_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['agro.Entry'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('agro', ['Bookmark'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Photo', fields ['photo_id', 'server']
        db.delete_unique('agro_photo', ['photo_id', 'server'])

        # Removing unique constraint on 'Entry', fields ['title', 'timestamp', 'source_type']
        db.delete_unique('agro_entry', ['title', 'timestamp', 'source_type'])

        # Deleting model 'Entry'
        db.delete_table('agro_entry')

        # Deleting model 'Tweet'
        db.delete_table('agro_tweet')

        # Deleting model 'Photo'
        db.delete_table('agro_photo')

        # Deleting model 'Song'
        db.delete_table('agro_song')

        # Deleting model 'Bookmark'
        db.delete_table('agro_bookmark')


    models = {
        'agro.bookmark': {
            'Meta': {'ordering': "['-timestamp']", 'object_name': 'Bookmark', '_ormbases': ['agro.Entry']},
            'entry_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['agro.Entry']", 'unique': 'True', 'primary_key': 'True'})
        },
        'agro.entry': {
            'Meta': {'ordering': "['-timestamp']", 'unique_together': "[('title', 'timestamp', 'source_type')]", 'object_name': 'Entry'},
            'allow_comments': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'owner_user': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'source_type': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        'agro.photo': {
            'Meta': {'ordering': "['-uploaded_at']", 'unique_together': "[('photo_id', 'server')]", 'object_name': 'Photo', '_ormbases': ['agro.Entry']},
            'entry_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['agro.Entry']", 'unique': 'True', 'primary_key': 'True'}),
            'exif': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'num_comments': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'original_format': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True'}),
            'original_secret': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'photo_id': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'secret': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'server': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'taken_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'uploaded_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'agro.song': {
            'Meta': {'ordering': "['-timestamp']", 'object_name': 'Song', '_ormbases': ['agro.Entry']},
            'album': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'album_mbid': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'artist': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'artist_mbid': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'entry_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['agro.Entry']", 'unique': 'True', 'primary_key': 'True'}),
            'large_image': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'med_image': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'small_image': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'song_mbid': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'streamable': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'agro.tweet': {
            'Meta': {'ordering': "['-tweet_id']", 'object_name': 'Tweet', '_ormbases': ['agro.Entry']},
            'entry_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['agro.Entry']", 'unique': 'True', 'primary_key': 'True'}),
            'source': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'tweet_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['agro']
