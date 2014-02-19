# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Game.is_live'
        db.add_column('live_game', 'is_live',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Game.is_live'
        db.delete_column('live_game', 'is_live')


    models = {
        'live.game': {
            'Meta': {'unique_together': "(['game_index', 'match'],)", 'object_name': 'Game'},
            'game_index': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_live': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'map': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'match': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['live.Match']"})
        },
        'live.livestat': {
            'Meta': {'unique_together': "(['update', 'player_index', 'game'],)", 'object_name': 'LiveStat'},
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
            'pla': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['ratings.Player']"}),
            'plb': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['ratings.Player']"}),
            'sca': ('django.db.models.fields.IntegerField', [], {}),
            'scb': ('django.db.models.fields.IntegerField', [], {}),
            'tournament': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['live.Tournament']"})
        },
        'live.tournament': {
            'Meta': {'object_name': 'Tournament'},
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
            'Meta': {'db_table': "'player'", 'object_name': 'Player', 'ordering': "['tag']"},
            'birthday': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'null': 'True', 'db_index': 'True', 'max_length': '2', 'blank': 'True'}),
            'current_rating': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'related_name': "'current'", 'to': "orm['ratings.Rating']", 'blank': 'True'}),
            'dom_end': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'related_name': "'player_dom_end'", 'to': "orm['ratings.Period']", 'blank': 'True'}),
            'dom_start': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'related_name': "'player_dom_start'", 'to': "orm['ratings.Period']", 'blank': 'True'}),
            'dom_val': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lp_name': ('django.db.models.fields.CharField', [], {'null': 'True', 'max_length': '200', 'blank': 'True'}),
            'mcnum': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'default': 'None', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'null': 'True', 'max_length': '100', 'blank': 'True'}),
            'race': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '1'}),
            'sc2c_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'sc2e_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'tag': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '30'}),
            'tlpd_db': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'tlpd_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'ratings.rating': {
            'Meta': {'db_table': "'rating'", 'object_name': 'Rating', 'ordering': "['period']"},
            'bf_dev': ('django.db.models.fields.FloatField', [], {'null': 'True', 'default': '1', 'blank': 'True'}),
            'bf_dev_vp': ('django.db.models.fields.FloatField', [], {'null': 'True', 'default': '1', 'blank': 'True'}),
            'bf_dev_vt': ('django.db.models.fields.FloatField', [], {'null': 'True', 'default': '1', 'blank': 'True'}),
            'bf_dev_vz': ('django.db.models.fields.FloatField', [], {'null': 'True', 'default': '1', 'blank': 'True'}),
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