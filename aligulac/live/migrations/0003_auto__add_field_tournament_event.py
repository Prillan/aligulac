# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Tournament.event'
        db.add_column('live_tournament', 'event',
                      self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['ratings.Event'], default=None),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Tournament.event'
        db.delete_column('live_tournament', 'event_id')


    models = {
        'live.game': {
            'Meta': {'object_name': 'Game', 'unique_together': "(['game_index', 'match'],)"},
            'game_index': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_live': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'map': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'match': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['live.Match']"})
        },
        'live.livestat': {
            'Meta': {'object_name': 'LiveStat', 'unique_together': "(['update', 'player_index', 'game'],)"},
            'game': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['live.Game']"}),
            'game_time': ('django.db.models.fields.IntegerField', [], {}),
            'gas_current': ('django.db.models.fields.IntegerField', [], {}),
            'gas_gathered': ('django.db.models.fields.IntegerField', [], {}),
            'gas_income': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'minerals_current': ('django.db.models.fields.IntegerField', [], {}),
            'minerals_gathered': ('django.db.models.fields.IntegerField', [], {}),
            'minerals_income': ('django.db.models.fields.IntegerField', [], {}),
            'player_index': ('django.db.models.fields.IntegerField', [], {}),
            'supply_army': ('django.db.models.fields.IntegerField', [], {}),
            'supply_cap': ('django.db.models.fields.IntegerField', [], {}),
            'supply_current': ('django.db.models.fields.IntegerField', [], {}),
            'supply_workers': ('django.db.models.fields.IntegerField', [], {}),
            'update': ('django.db.models.fields.IntegerField', [], {})
        },
        'live.match': {
            'Meta': {'object_name': 'Match'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pla': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ratings.Player']", 'related_name': "'+'"}),
            'plb': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ratings.Player']", 'related_name': "'+'"}),
            'sca': ('django.db.models.fields.IntegerField', [], {}),
            'scb': ('django.db.models.fields.IntegerField', [], {}),
            'tournament': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['live.Tournament']"})
        },
        'live.tournament': {
            'Meta': {'object_name': 'Tournament'},
            'event': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'to': "orm['ratings.Event']", 'default': 'None'}),
            'host': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['live.TournamentHost']"}),
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
            'host': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['live.TournamentHost']", 'related_name': "'key'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'key_type': ('django.db.models.fields.CharField', [], {'max_length': '2'})
        },
        'ratings.event': {
            'Meta': {'ordering': "['idx', 'latest', 'fullname']", 'db_table': "'event'", 'object_name': 'Event'},
            'big': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'category': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True', 'blank': 'True', 'null': 'True'}),
            'closed': ('django.db.models.fields.BooleanField', [], {'db_index': 'True', 'default': 'False'}),
            'earliest': ('django.db.models.fields.DateField', [], {'db_index': 'True', 'blank': 'True', 'null': 'True'}),
            'family': ('django.db.models.fields.related.ManyToManyField', [], {'through': "orm['ratings.EventAdjacency']", 'to': "orm['ratings.Event']", 'symmetrical': 'False'}),
            'fullname': ('django.db.models.fields.CharField', [], {'max_length': '500', 'default': "''"}),
            'homepage': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idx': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'latest': ('django.db.models.fields.DateField', [], {'db_index': 'True', 'blank': 'True', 'null': 'True'}),
            'lft': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True', 'default': 'None'}),
            'lp_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'noprint': ('django.db.models.fields.BooleanField', [], {'db_index': 'True', 'default': 'False'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'parent_event'", 'null': 'True', 'to': "orm['ratings.Event']", 'blank': 'True'}),
            'prizepool': ('django.db.models.fields.NullBooleanField', [], {'db_index': 'True', 'blank': 'True', 'null': 'True'}),
            'rgt': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True', 'default': 'None'}),
            'tl_thread': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'tlpd_db': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'tlpd_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'ratings.eventadjacency': {
            'Meta': {'db_table': "'eventadjacency'", 'object_name': 'EventAdjacency'},
            'child': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ratings.Event']", 'related_name': "'uplink'"}),
            'distance': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'default': 'None'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ratings.Event']", 'related_name': "'downlink'"})
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
            'country': ('django.db.models.fields.CharField', [], {'max_length': '2', 'db_index': 'True', 'blank': 'True', 'null': 'True'}),
            'current_rating': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'current'", 'null': 'True', 'to': "orm['ratings.Rating']", 'blank': 'True'}),
            'dom_end': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'player_dom_end'", 'null': 'True', 'to': "orm['ratings.Period']", 'blank': 'True'}),
            'dom_start': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'player_dom_start'", 'null': 'True', 'to': "orm['ratings.Period']", 'blank': 'True'}),
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
            'prev': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'to': "orm['ratings.Rating']", 'related_name': "'prevrating'"}),
            'rating': ('django.db.models.fields.FloatField', [], {}),
            'rating_vp': ('django.db.models.fields.FloatField', [], {}),
            'rating_vt': ('django.db.models.fields.FloatField', [], {}),
            'rating_vz': ('django.db.models.fields.FloatField', [], {})
        }
    }

    complete_apps = ['live']