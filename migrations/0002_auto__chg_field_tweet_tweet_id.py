# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'Tweet.tweet_id'
        db.alter_column('agro_tweet', 'tweet_id', self.gf('django.db.models.fields.BigIntegerField')(null=True))


    def backwards(self, orm):
        
        # Changing field 'Tweet.tweet_id'
        db.alter_column('agro_tweet', 'tweet_id', self.gf('django.db.models.fields.IntegerField')(null=True))


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
            'tweet_id': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'})
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
