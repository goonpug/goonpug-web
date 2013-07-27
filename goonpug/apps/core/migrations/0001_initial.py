# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Match'
        db.create_table(u'core_match', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
            ('server', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Server'])),
            ('season', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Season'])),
            ('team_a', self.gf('django.db.models.fields.related.ForeignKey')(related_name='match_team_a', to=orm['core.Team'])),
            ('team_b', self.gf('django.db.models.fields.related.ForeignKey')(related_name='match_team_b', to=orm['core.Team'])),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('paused', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('score_a', self.gf('django.db.models.fields.IntegerField')()),
            ('score_b', self.gf('django.db.models.fields.IntegerField')()),
            ('ruleset', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('config_ot', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('config_knife_round', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('config_password', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
            ('map_mode', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('current_map', self.gf('django.db.models.fields.IntegerField')()),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'core', ['Match'])

        # Adding model 'MatchMap'
        db.create_table(u'core_matchmap', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('match', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Match'])),
            ('map_name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('score_1', self.gf('django.db.models.fields.IntegerField')()),
            ('score_2', self.gf('django.db.models.fields.IntegerField')()),
            ('current_period', self.gf('django.db.models.fields.IntegerField')()),
            ('gotv_demo_file', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal(u'core', ['MatchMap'])

        # Adding model 'MatchMapScore'
        db.create_table(u'core_matchmapscore', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('match_map', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.MatchMap'])),
            ('score_type', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('score1_half1', self.gf('django.db.models.fields.IntegerField')()),
            ('score1_half2', self.gf('django.db.models.fields.IntegerField')()),
            ('score2_half1', self.gf('django.db.models.fields.IntegerField')()),
            ('score2_half2', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'core', ['MatchMapScore'])

        # Adding model 'Player'
        db.create_table(u'core_player', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('steam_id', self.gf('django.db.models.fields.BigIntegerField')(unique=True)),
            ('banned', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('reputation', self.gf('django.db.models.fields.IntegerField')()),
            ('rating', self.gf('django.db.models.fields.FloatField')(default=25.0)),
            ('rating_variance', self.gf('django.db.models.fields.FloatField')(default=8.333)),
        ))
        db.send_create_signal(u'core', ['Player'])

        # Adding model 'PlayerBan'
        db.create_table(u'core_playerban', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('player', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Player'])),
            ('start', self.gf('django.db.models.fields.DateField')()),
            ('end', self.gf('django.db.models.fields.DateField')()),
            ('reason', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('link', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal(u'core', ['PlayerBan'])

        # Adding model 'PlayerKill'
        db.create_table(u'core_playerkill', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('match', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Match'])),
            ('match_map', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.MatchMap'])),
            ('round', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Round'])),
            ('killer', self.gf('django.db.models.fields.related.ForeignKey')(related_name='playerkill_player_killer', to=orm['core.Player'])),
            ('killer_team', self.gf('django.db.models.fields.IntegerField')()),
            ('victim', self.gf('django.db.models.fields.related.ForeignKey')(related_name='playerkill_player_victim', to=orm['core.Player'])),
            ('victim_team', self.gf('django.db.models.fields.IntegerField')()),
            ('weapon', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('headshot', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'core', ['PlayerKill'])

        # Adding model 'PlayerMatch'
        db.create_table(u'core_playermatch', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('match', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Match'])),
            ('match_map', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.MatchMap'])),
            ('player', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Player'])),
            ('team', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('ip', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('first_side', self.gf('django.db.models.fields.IntegerField')()),
            ('current_side', self.gf('django.db.models.fields.IntegerField')()),
            ('nickname', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('kills', self.gf('django.db.models.fields.IntegerField')()),
            ('assists', self.gf('django.db.models.fields.IntegerField')()),
            ('deaths', self.gf('django.db.models.fields.IntegerField')()),
            ('score', self.gf('django.db.models.fields.IntegerField')()),
            ('hsp', self.gf('django.db.models.fields.FloatField')()),
            ('defuses', self.gf('django.db.models.fields.IntegerField')()),
            ('plants', self.gf('django.db.models.fields.IntegerField')()),
            ('tks', self.gf('django.db.models.fields.IntegerField')()),
            ('clutch_v1', self.gf('django.db.models.fields.IntegerField')()),
            ('clutch_v2', self.gf('django.db.models.fields.IntegerField')()),
            ('clutch_v3', self.gf('django.db.models.fields.IntegerField')()),
            ('clutch_v4', self.gf('django.db.models.fields.IntegerField')()),
            ('clutch_v5', self.gf('django.db.models.fields.IntegerField')()),
            ('k1', self.gf('django.db.models.fields.IntegerField')()),
            ('k2', self.gf('django.db.models.fields.IntegerField')()),
            ('k3', self.gf('django.db.models.fields.IntegerField')()),
            ('k4', self.gf('django.db.models.fields.IntegerField')()),
            ('k5', self.gf('django.db.models.fields.IntegerField')()),
            ('adr', self.gf('django.db.models.fields.FloatField')()),
            ('rws', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal(u'core', ['PlayerMatch'])

        # Adding model 'PlayerRound'
        db.create_table(u'core_playerround', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('round', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Round'])),
            ('player', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Player'])),
            ('ip', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('first_side', self.gf('django.db.models.fields.IntegerField')()),
            ('current_side', self.gf('django.db.models.fields.IntegerField')()),
            ('kills', self.gf('django.db.models.fields.IntegerField')()),
            ('assists', self.gf('django.db.models.fields.IntegerField')()),
            ('deaths', self.gf('django.db.models.fields.IntegerField')()),
            ('hsp', self.gf('django.db.models.fields.FloatField')()),
            ('defuses', self.gf('django.db.models.fields.IntegerField')()),
            ('plants', self.gf('django.db.models.fields.IntegerField')()),
            ('tks', self.gf('django.db.models.fields.IntegerField')()),
            ('clutch_v1', self.gf('django.db.models.fields.IntegerField')()),
            ('clutch_v2', self.gf('django.db.models.fields.IntegerField')()),
            ('clutch_v3', self.gf('django.db.models.fields.IntegerField')()),
            ('clutch_v4', self.gf('django.db.models.fields.IntegerField')()),
            ('clutch_v5', self.gf('django.db.models.fields.IntegerField')()),
            ('k1', self.gf('django.db.models.fields.IntegerField')()),
            ('k2', self.gf('django.db.models.fields.IntegerField')()),
            ('k3', self.gf('django.db.models.fields.IntegerField')()),
            ('k4', self.gf('django.db.models.fields.IntegerField')()),
            ('k5', self.gf('django.db.models.fields.IntegerField')()),
            ('adr', self.gf('django.db.models.fields.FloatField')()),
            ('rws', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal(u'core', ['PlayerRound'])

        # Adding model 'PlayerSeason'
        db.create_table(u'core_playerseason', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('player', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Player'])),
            ('season', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Season'])),
            ('kills', self.gf('django.db.models.fields.IntegerField')()),
            ('assists', self.gf('django.db.models.fields.IntegerField')()),
            ('deaths', self.gf('django.db.models.fields.IntegerField')()),
            ('score', self.gf('django.db.models.fields.IntegerField')()),
            ('hsp', self.gf('django.db.models.fields.FloatField')()),
            ('defuses', self.gf('django.db.models.fields.IntegerField')()),
            ('plants', self.gf('django.db.models.fields.IntegerField')()),
            ('tks', self.gf('django.db.models.fields.IntegerField')()),
            ('clutch_v1', self.gf('django.db.models.fields.IntegerField')()),
            ('clutch_v2', self.gf('django.db.models.fields.IntegerField')()),
            ('clutch_v3', self.gf('django.db.models.fields.IntegerField')()),
            ('clutch_v4', self.gf('django.db.models.fields.IntegerField')()),
            ('clutch_v5', self.gf('django.db.models.fields.IntegerField')()),
            ('k1', self.gf('django.db.models.fields.IntegerField')()),
            ('k2', self.gf('django.db.models.fields.IntegerField')()),
            ('k3', self.gf('django.db.models.fields.IntegerField')()),
            ('k4', self.gf('django.db.models.fields.IntegerField')()),
            ('k5', self.gf('django.db.models.fields.IntegerField')()),
            ('adr', self.gf('django.db.models.fields.FloatField')()),
            ('rws', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal(u'core', ['PlayerSeason'])

        # Adding model 'Round'
        db.create_table(u'core_round', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('match', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Match'])),
            ('match_map', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.MatchMap'])),
            ('round_number', self.gf('django.db.models.fields.IntegerField')()),
            ('bomb_planted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('bomb_defused', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('bomb_exploded', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('win_type', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('team_win', self.gf('django.db.models.fields.IntegerField')()),
            ('ct_win', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('t_win', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('score_a', self.gf('django.db.models.fields.IntegerField')()),
            ('score_b', self.gf('django.db.models.fields.IntegerField')()),
            ('backup_file_name', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal(u'core', ['Round'])

        # Adding model 'Season'
        db.create_table(u'core_season', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('event', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('start', self.gf('django.db.models.fields.DateField')()),
            ('end', self.gf('django.db.models.fields.DateField')()),
            ('link', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('logo', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'core', ['Season'])

        # Adding model 'Server'
        db.create_table(u'core_server', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('ip', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('port', self.gf('django.db.models.fields.IntegerField')(default=27015)),
            ('gotv_ip', self.gf('django.db.models.fields.CharField')(max_length=16, blank=True)),
            ('gotv_port', self.gf('django.db.models.fields.IntegerField')(default=27020)),
            ('rcon', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
        ))
        db.send_create_signal(u'core', ['Server'])

        # Adding model 'Team'
        db.create_table(u'core_team', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('shorthandle', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('link', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal(u'core', ['Team'])

        # Adding model 'TeamSeason'
        db.create_table(u'core_teamseason', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Team'])),
            ('season', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Season'])),
        ))
        db.send_create_signal(u'core', ['TeamSeason'])


    def backwards(self, orm):
        # Deleting model 'Match'
        db.delete_table(u'core_match')

        # Deleting model 'MatchMap'
        db.delete_table(u'core_matchmap')

        # Deleting model 'MatchMapScore'
        db.delete_table(u'core_matchmapscore')

        # Deleting model 'Player'
        db.delete_table(u'core_player')

        # Deleting model 'PlayerBan'
        db.delete_table(u'core_playerban')

        # Deleting model 'PlayerKill'
        db.delete_table(u'core_playerkill')

        # Deleting model 'PlayerMatch'
        db.delete_table(u'core_playermatch')

        # Deleting model 'PlayerRound'
        db.delete_table(u'core_playerround')

        # Deleting model 'PlayerSeason'
        db.delete_table(u'core_playerseason')

        # Deleting model 'Round'
        db.delete_table(u'core_round')

        # Deleting model 'Season'
        db.delete_table(u'core_season')

        # Deleting model 'Server'
        db.delete_table(u'core_server')

        # Deleting model 'Team'
        db.delete_table(u'core_team')

        # Deleting model 'TeamSeason'
        db.delete_table(u'core_teamseason')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'core.match': {
            'Meta': {'object_name': 'Match'},
            'config_knife_round': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'config_ot': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'config_password': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'current_map': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'map_mode': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'paused': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ruleset': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'score_a': ('django.db.models.fields.IntegerField', [], {}),
            'score_b': ('django.db.models.fields.IntegerField', [], {}),
            'season': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Season']"}),
            'server': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Server']"}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'team_a': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'match_team_a'", 'to': u"orm['core.Team']"}),
            'team_b': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'match_team_b'", 'to': u"orm['core.Team']"})
        },
        u'core.matchmap': {
            'Meta': {'object_name': 'MatchMap'},
            'current_period': ('django.db.models.fields.IntegerField', [], {}),
            'gotv_demo_file': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'map_name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'match': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Match']"}),
            'score_1': ('django.db.models.fields.IntegerField', [], {}),
            'score_2': ('django.db.models.fields.IntegerField', [], {})
        },
        u'core.matchmapscore': {
            'Meta': {'object_name': 'MatchMapScore'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'match_map': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.MatchMap']"}),
            'score1_half1': ('django.db.models.fields.IntegerField', [], {}),
            'score1_half2': ('django.db.models.fields.IntegerField', [], {}),
            'score2_half1': ('django.db.models.fields.IntegerField', [], {}),
            'score2_half2': ('django.db.models.fields.IntegerField', [], {}),
            'score_type': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'core.player': {
            'Meta': {'object_name': 'Player'},
            'banned': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rating': ('django.db.models.fields.FloatField', [], {'default': '25.0'}),
            'rating_variance': ('django.db.models.fields.FloatField', [], {'default': '8.333'}),
            'reputation': ('django.db.models.fields.IntegerField', [], {}),
            'steam_id': ('django.db.models.fields.BigIntegerField', [], {'unique': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        },
        u'core.playerban': {
            'Meta': {'object_name': 'PlayerBan'},
            'end': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Player']"}),
            'reason': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'start': ('django.db.models.fields.DateField', [], {})
        },
        u'core.playerkill': {
            'Meta': {'object_name': 'PlayerKill'},
            'headshot': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'killer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'playerkill_player_killer'", 'to': u"orm['core.Player']"}),
            'killer_team': ('django.db.models.fields.IntegerField', [], {}),
            'match': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Match']"}),
            'match_map': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.MatchMap']"}),
            'round': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Round']"}),
            'victim': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'playerkill_player_victim'", 'to': u"orm['core.Player']"}),
            'victim_team': ('django.db.models.fields.IntegerField', [], {}),
            'weapon': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        u'core.playermatch': {
            'Meta': {'object_name': 'PlayerMatch'},
            'adr': ('django.db.models.fields.FloatField', [], {}),
            'assists': ('django.db.models.fields.IntegerField', [], {}),
            'clutch_v1': ('django.db.models.fields.IntegerField', [], {}),
            'clutch_v2': ('django.db.models.fields.IntegerField', [], {}),
            'clutch_v3': ('django.db.models.fields.IntegerField', [], {}),
            'clutch_v4': ('django.db.models.fields.IntegerField', [], {}),
            'clutch_v5': ('django.db.models.fields.IntegerField', [], {}),
            'current_side': ('django.db.models.fields.IntegerField', [], {}),
            'deaths': ('django.db.models.fields.IntegerField', [], {}),
            'defuses': ('django.db.models.fields.IntegerField', [], {}),
            'first_side': ('django.db.models.fields.IntegerField', [], {}),
            'hsp': ('django.db.models.fields.FloatField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'k1': ('django.db.models.fields.IntegerField', [], {}),
            'k2': ('django.db.models.fields.IntegerField', [], {}),
            'k3': ('django.db.models.fields.IntegerField', [], {}),
            'k4': ('django.db.models.fields.IntegerField', [], {}),
            'k5': ('django.db.models.fields.IntegerField', [], {}),
            'kills': ('django.db.models.fields.IntegerField', [], {}),
            'match': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Match']"}),
            'match_map': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.MatchMap']"}),
            'nickname': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'plants': ('django.db.models.fields.IntegerField', [], {}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Player']"}),
            'rws': ('django.db.models.fields.FloatField', [], {}),
            'score': ('django.db.models.fields.IntegerField', [], {}),
            'team': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'tks': ('django.db.models.fields.IntegerField', [], {})
        },
        u'core.playerround': {
            'Meta': {'object_name': 'PlayerRound'},
            'adr': ('django.db.models.fields.FloatField', [], {}),
            'assists': ('django.db.models.fields.IntegerField', [], {}),
            'clutch_v1': ('django.db.models.fields.IntegerField', [], {}),
            'clutch_v2': ('django.db.models.fields.IntegerField', [], {}),
            'clutch_v3': ('django.db.models.fields.IntegerField', [], {}),
            'clutch_v4': ('django.db.models.fields.IntegerField', [], {}),
            'clutch_v5': ('django.db.models.fields.IntegerField', [], {}),
            'current_side': ('django.db.models.fields.IntegerField', [], {}),
            'deaths': ('django.db.models.fields.IntegerField', [], {}),
            'defuses': ('django.db.models.fields.IntegerField', [], {}),
            'first_side': ('django.db.models.fields.IntegerField', [], {}),
            'hsp': ('django.db.models.fields.FloatField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'k1': ('django.db.models.fields.IntegerField', [], {}),
            'k2': ('django.db.models.fields.IntegerField', [], {}),
            'k3': ('django.db.models.fields.IntegerField', [], {}),
            'k4': ('django.db.models.fields.IntegerField', [], {}),
            'k5': ('django.db.models.fields.IntegerField', [], {}),
            'kills': ('django.db.models.fields.IntegerField', [], {}),
            'plants': ('django.db.models.fields.IntegerField', [], {}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Player']"}),
            'round': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Round']"}),
            'rws': ('django.db.models.fields.FloatField', [], {}),
            'tks': ('django.db.models.fields.IntegerField', [], {})
        },
        u'core.playerseason': {
            'Meta': {'object_name': 'PlayerSeason'},
            'adr': ('django.db.models.fields.FloatField', [], {}),
            'assists': ('django.db.models.fields.IntegerField', [], {}),
            'clutch_v1': ('django.db.models.fields.IntegerField', [], {}),
            'clutch_v2': ('django.db.models.fields.IntegerField', [], {}),
            'clutch_v3': ('django.db.models.fields.IntegerField', [], {}),
            'clutch_v4': ('django.db.models.fields.IntegerField', [], {}),
            'clutch_v5': ('django.db.models.fields.IntegerField', [], {}),
            'deaths': ('django.db.models.fields.IntegerField', [], {}),
            'defuses': ('django.db.models.fields.IntegerField', [], {}),
            'hsp': ('django.db.models.fields.FloatField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'k1': ('django.db.models.fields.IntegerField', [], {}),
            'k2': ('django.db.models.fields.IntegerField', [], {}),
            'k3': ('django.db.models.fields.IntegerField', [], {}),
            'k4': ('django.db.models.fields.IntegerField', [], {}),
            'k5': ('django.db.models.fields.IntegerField', [], {}),
            'kills': ('django.db.models.fields.IntegerField', [], {}),
            'plants': ('django.db.models.fields.IntegerField', [], {}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Player']"}),
            'rws': ('django.db.models.fields.FloatField', [], {}),
            'score': ('django.db.models.fields.IntegerField', [], {}),
            'season': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Season']"}),
            'tks': ('django.db.models.fields.IntegerField', [], {})
        },
        u'core.round': {
            'Meta': {'object_name': 'Round'},
            'backup_file_name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'bomb_defused': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'bomb_exploded': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'bomb_planted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ct_win': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'match': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Match']"}),
            'match_map': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.MatchMap']"}),
            'round_number': ('django.db.models.fields.IntegerField', [], {}),
            'score_a': ('django.db.models.fields.IntegerField', [], {}),
            'score_b': ('django.db.models.fields.IntegerField', [], {}),
            't_win': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'team_win': ('django.db.models.fields.IntegerField', [], {}),
            'win_type': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'core.season': {
            'Meta': {'object_name': 'Season'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'end': ('django.db.models.fields.DateField', [], {}),
            'event': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'logo': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'start': ('django.db.models.fields.DateField', [], {})
        },
        u'core.server': {
            'Meta': {'object_name': 'Server'},
            'gotv_ip': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'gotv_port': ('django.db.models.fields.IntegerField', [], {'default': '27020'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'port': ('django.db.models.fields.IntegerField', [], {'default': '27015'}),
            'rcon': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'})
        },
        u'core.team': {
            'Meta': {'object_name': 'Team'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'shorthandle': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        u'core.teamseason': {
            'Meta': {'object_name': 'TeamSeason'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'season': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Season']"}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Team']"})
        }
    }

    complete_apps = ['core']