# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TournamentHost'
        db.create_table('live_tournamenthost', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=25)),
        ))
        db.send_create_signal('live', ['TournamentHost'])

        # Adding model 'Tournament'
        db.create_table('live_tournament', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('running', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('host', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tournament', to=orm['live.TournamentHost'])),
        ))
        db.send_create_signal('live', ['Tournament'])

        # Adding model 'TournamentKey'
        db.create_table('live_tournamentkey', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('key_type', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('host', self.gf('django.db.models.fields.related.ForeignKey')(related_name='key', to=orm['live.TournamentHost'])),
        ))
        db.send_create_signal('live', ['TournamentKey'])

        # Adding model 'LiveStat'
        db.create_table('live_livestat', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pla', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['ratings.Player'])),
            ('plb', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['ratings.Player'])),
            ('sca', self.gf('django.db.models.fields.IntegerField')()),
            ('scb', self.gf('django.db.models.fields.IntegerField')()),
            ('tournament', self.gf('django.db.models.fields.related.ForeignKey')(related_name='live_stat', to=orm['live.Tournament'])),
        ))
        db.send_create_signal('live', ['LiveStat'])


    def backwards(self, orm):
        # Deleting model 'TournamentHost'
        db.delete_table('live_tournamenthost')

        # Deleting model 'Tournament'
        db.delete_table('live_tournament')

        # Deleting model 'TournamentKey'
        db.delete_table('live_tournamentkey')

        # Deleting model 'LiveStat'
        db.delete_table('live_livestat')


    models = {
        'live.livestat': {
            'Meta': {'object_name': 'LiveStat'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pla': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['ratings.Player']"}),
            'plb': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['ratings.Player']"}),
            'sca': ('django.db.models.fields.IntegerField', [], {}),
            'scb': ('django.db.models.fields.IntegerField', [], {}),
            'tournament': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'live_stat'", 'to': "orm['live.Tournament']"})
        },
        'live.tournament': {
            'Meta': {'object_name': 'Tournament'},
            'host': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tournament'", 'to': "orm['live.TournamentHost']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'running': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'live.tournamenthost': {
            'Meta': {'object_name': 'TournamentHost'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '25'})
        },
        'live.tournamentkey': {
            'Meta': {'object_name': 'TournamentKey'},
            'host': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'key'", 'to': "orm['live.TournamentHost']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'key_type': ('django.db.models.fields.CharField', [], {'max_length': '2'})
        },
        'ratings.period': {
            'Meta': {'db_table': "'period'", 'object_name': 'Period'},
            'computed': ('django.db.models.fields.BooleanField', [], {'db_index': 'True', 'default': 'False'}),
            'dom_p': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'dom_t': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'dom_z': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'end': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'needs_recompute': ('django.db.models.fields.BooleanField', [], {'db_index': 'True', 'default': 'False'}),
            'num_games': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'num_newplayers': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'num_retplayers': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'start': ('django.db.models.fields.DateField', [], {'db_index': 'True'})
        },
        'ratings.player': {
            'Meta': {'ordering': "['tag']", 'db_table': "'player'", 'object_name': 'Player'},
            'birthday': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True', 'db_index': 'True', 'null': 'True'}),
            'current_rating': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ratings.Rating']", 'null': 'True', 'blank': 'True', 'related_name': "'current'"}),
            'dom_end': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ratings.Period']", 'null': 'True', 'blank': 'True', 'related_name': "'player_dom_end'"}),
            'dom_start': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ratings.Period']", 'null': 'True', 'blank': 'True', 'related_name': "'player_dom_start'"}),
            'dom_val': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lp_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True', 'null': 'True'}),
            'mcnum': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True', 'default': 'None'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True', 'null': 'True'}),
            'race': ('django.db.models.fields.CharField', [], {'max_length': '1', 'db_index': 'True'}),
            'sc2c_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'sc2e_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '30', 'db_index': 'True'}),
            'tlpd_db': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'tlpd_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'ratings.rating': {
            'Meta': {'ordering': "['period']", 'db_table': "'rating'", 'object_name': 'Rating'},
            'bf_dev': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True', 'default': '1'}),
            'bf_dev_vp': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True', 'default': '1'}),
            'bf_dev_vt': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True', 'default': '1'}),
            'bf_dev_vz': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True', 'default': '1'}),
            'bf_rating': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'bf_rating_vp': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'bf_rating_vt': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'bf_rating_vz': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'comp_rat': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'comp_rat_vp': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'comp_rat_vt': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'comp_rat_vz': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'decay': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'dev': ('django.db.models.fields.FloatField', [], {}),
            'dev_vp': ('django.db.models.fields.FloatField', [], {}),
            'dev_vt': ('django.db.models.fields.FloatField', [], {}),
            'dev_vz': ('django.db.models.fields.FloatField', [], {}),
            'domination': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'period': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ratings.Period']"}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ratings.Player']"}),
            'position': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'position_vp': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'position_vt': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'position_vz': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'prev': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'related_name': "'prevrating'", 'to': "orm['ratings.Rating']"}),
            'rating': ('django.db.models.fields.FloatField', [], {}),
            'rating_vp': ('django.db.models.fields.FloatField', [], {}),
            'rating_vt': ('django.db.models.fields.FloatField', [], {}),
            'rating_vz': ('django.db.models.fields.FloatField', [], {})
        }
    }

    complete_apps = ['live']