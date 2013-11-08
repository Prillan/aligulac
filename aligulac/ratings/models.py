# {{{ Imports
import datetime
from math import sqrt

from django.contrib.auth.models import User
from django.db import (
    models,
    transaction,
)
from django.db.models import (
    F,
    Max,
    Min,
    Q,
)

from aligulac.settings import start_rating

from currency import ExchangeRates

from countries import (
    transformations,
    data,
)
# }}}

# List of countries
# This is used in a couple of models, although it adds a bit of overhead, it would be better to do this
# statically in the country module.
countries = [(code, transformations.cc_to_cn(code)) for code in data.ccn_to_cca2.values()]
countries.sort(key=lambda a: a[1])

# {{{ Various enum-types
TLPD_DB_WOLKOREAN        = 0b00001
TLPD_DB_WOLINTERNATIONAL = 0b00010
TLPD_DB_HOTS             = 0b00100
TLPD_DB_HOTSBETA         = 0b01000
TLPD_DB_WOLBETA          = 0b10000
TLPD_DBS = [
    (TLPD_DB_WOLBETA,          'WoL Beta'),
    (TLPD_DB_WOLKOREAN,        'WoL Korean'),
    (TLPD_DB_WOLINTERNATIONAL, 'WoL International'),
    (TLPD_DB_HOTSBETA,         'HotS Beta'),
    (TLPD_DB_HOTS,             'HotS'),
]

CAT_INDIVIDUAL = 'individual'
CAT_TEAM       = 'team'
CAT_FREQUENT   = 'frequent'
EVENT_CATEGORIES = [
    (CAT_INDIVIDUAL, 'Individual'),
    (CAT_TEAM,       'Team'),
    (CAT_FREQUENT,   'Frequent'),
]

TYPE_CATEGORY = 'category'
TYPE_EVENT    = 'event'
TYPE_ROUND    = 'round'
EVENT_TYPES = [
    (TYPE_CATEGORY, 'Category'),
    (TYPE_EVENT,    'Event'),
    (TYPE_ROUND,    'Round'),
]

P, T, Z, R, S = 'PTZRS'
RACES = [
    (P, 'Protoss'),
    (T, 'Terran'),
    (Z, 'Zerg'),
    (R, 'Random'),
    (S, 'Switcher'),
]
MRACES = RACES[:-1]

WOL  = 'WoL'
HOTS = 'HotS'
LOTV = 'LotV'
GAMES = [
    (WOL,  'Wings of Liberty'),
    (HOTS, 'Heart of the Swarm'),
    (LOTV, 'Legacy of the Void'),
]

TYPE_INFO    = 'info'
TYPE_WARNING = 'warning'
TYPE_ERROR   = 'error'
TYPE_SUCCESS = 'success'
MESSAGE_TYPES = [
    (TYPE_INFO,    'info'),
    (TYPE_WARNING, 'warning'),
    (TYPE_ERROR,   'error'),
    (TYPE_SUCCESS, 'success'),
]
# }}}

# {{{ Periods
class Period(models.Model):
    class Meta:
        db_table = 'period'

    start = models.DateField('Start date', null=False, db_index=True)
    end = models.DateField('End date', null=False, db_index=True)
    computed = models.BooleanField('Computed', null=False, default=False, db_index=True)
    needs_recompute = models.BooleanField('Requires recomputation', null=False, default=False, db_index=True)
    num_retplayers = models.IntegerField('# returning players', default=0)
    num_newplayers = models.IntegerField('# new players', default=0)
    num_games = models.IntegerField('# games', default=0)
    dom_p = models.FloatField('Protoss OP value', null=True)
    dom_t = models.FloatField('Terran OP value', null=True)
    dom_z = models.FloatField('Zerg OP value', null=True)

    # {{{ String representation
    def __str__(self):
        return 'Period #' + str(self.id) + ': ' + str(self.start) + ' to ' + str(self.end)
    # }}}

    # {{{ is_preview: Checks whether this period is still a preview
    def is_preview(self):
        return self.end >= datetime.date.today()
    # }}}
# }}}

# {{{ Events
class Event(models.Model):
    class Meta:
        ordering = ['idx', 'latest', 'fullname']
        db_table = 'event'

    name = models.CharField('Name', max_length=100)
    parent = models.ForeignKey('Event', null=True, blank=True, related_name='parent_event')
    lft = models.IntegerField('Left', null=True, blank=True, default=None)
    rgt = models.IntegerField('Right', null=True, blank=True, default=None)
    idx = models.IntegerField('Index', null=False, blank=False, db_index=True)
    closed = models.BooleanField('Closed', default=False, db_index=True)
    big = models.BooleanField('Big', default=False)
    noprint = models.BooleanField('No print', default=False, db_index=True)
    fullname = models.CharField('Full name', max_length=500, default='')
    homepage = models.CharField('Homepage', blank=True, null=True, max_length=200)
    lp_name = models.CharField('Liquipedia title', blank=True, null=True, max_length=200)

    # tlpd_db contains information in binary form on which TLPD databases to use:
    # 1 for Korean, 10 for International, 100 for HotS, 1000 for Hots beta, 10000 for WoL beta
    # So a value of 5 (00101 in binary) would correspond to a link to the Korean and HotS TLPD.  
    # Use bitwise AND (&) with the flags to check.
    tlpd_id = models.IntegerField('TLPD ID', blank=True, null=True)
    tlpd_db = models.IntegerField('TLPD Databases', blank=True, null=True)
    tl_thread = models.IntegerField('Teamliquid.net thread ID', blank=True, null=True)

    prizepool = models.NullBooleanField('Has prize pool', blank=True, null=True, db_index=True)

    earliest = models.DateField('Earliest match', blank=True, null=True, db_index=True)
    latest = models.DateField('Latest match', blank=True, null=True, db_index=True)

    category = models.CharField(
        'Category', max_length=50, null=True, blank=True, choices=EVENT_CATEGORIES, db_index=True)
    type = models.CharField(max_length=50, null=False, choices=EVENT_TYPES, db_index=True)

    family = models.ManyToManyField('Event', through='EventAdjacency')

    # {{{ open_events: Not used... is this useful?
    @staticmethod
    def open_events():
        qset = (
            Event.objects.filter(closed=False)
                .exclude(downlink__distance__gt=0)
                .order_by('idx', 'fullname')
                .values('id', 'fullname')
        )
        for e in qset:
            yield (e['id'], e['fullname'])
    # }}}

    # {{{ String representation
    def __str__(self):
        return self.fullname
    # }}}

    # {{{ get_parent(): Returns the parent, or null
    def get_parent(self):
        try:
            return self.uplink.get(distance=1).parent
        except:
            return None
    # }}}

    # {{{ get_ancestors(id=False): Returns a queryset containing the ancestors
    # If id=True, the queryset contains the object itself.
    def get_ancestors(self, id=False):
        if not id:
            qset = Event.objects.filter(downlink__child=self, downlink__distance__gt=0)
        else:
            qset = Event.objects.filter(downlink__child=self)
        return qset.order_by('-downlink__distance')
    # }}}

    # {{{ get_ancestors_print: Returns a queryset containing the printable ancestors
    def get_ancestors_print(self, id=True):
        return self.get_ancestors(id=id).filter(noprint=False)
    # }}}

    # {{{ get_ancestors_event: Returns a queryset containing printable ancestors of type event or category
    def get_ancestors_event(self):
        return self.get_ancestors(id=True).filter(type__in=[TYPE_CATEGORY, TYPE_EVENT])
    # }}}

    # {{{ get_root: Returns the farthest removed ancestor
    def get_root(self):
        return self.get_ancestors(id=True).first()
    # }}}

    # {{{ get_children(types=[category,event,round], id=False): Returns a queryset containing the children
    # of this event, with the matching criteria
    def get_children(self, types=[TYPE_CATEGORY, TYPE_EVENT, TYPE_ROUND], id=False):
        if not id:
            qset = Event.objects.filter(uplink__parent=self, uplink__distance__gt=0)
        else:
            qset = Event.objects.filter(uplink__parent=self)
        return qset.filter(type__in=types)
    # }}}

    # {{{ get_immediate_children: Returns a queryset of immediate children
    def get_immediate_children(self):
        return Event.objects.filter(uplink__parent=self, uplink__distance=1)
    # }}}

    # {{{ has_children: Returns true if this event has children, false if not
    def has_children(self):
        return self.downlink.filter(distance__gt=0).exists()
    # }}}

    # {{{ update_name: Refreshes the fullname field (must be called after changing name of ancestors)
    def update_name(self, newname=None):
        if newname is not None:
            self.name = newname
            self.save()

        ancestors = self.get_ancestors_print()
        self.fullname = ' '.join([e.name for e in ancestors])
        self.save()
    # }}}

    # {{{ get_event_fullname: Returns the fullname of the nearest ancestor of type event or category
    # This is not cached and will query the DB!
    def get_event_fullname(self):
        return self.get_ancestors_event().last().fullname
    # }}}

    # {{{ get_event: Returns the nearest ancestor of type event or category
    def get_event_event(self):
        return self.get_ancestors_event().last()
    # }}}
    
    # {{{ get_homepage: Returns the URL if one can be found, None otherwise
    # This is not cached and will query the DB!
    def get_homepage(self):
        try:
            return self.get_ancestors(id=True).filter(homepage__isnull=False).last().homepage
        except:
            return None
    # }}}

    # {{{ get_lp_name: Returns the Liquipedia title if one can be found, None otherwise
    # This is not cached and will query the DB!
    def get_lp_name(self):
        try:
            return self.get_ancestors(id=True).filter(lp_name__isnull=False).last().lp_name
        except:
            return None
    # }}}

    # {{{ get_tl_thread: Returns the ID of the TL thread if one can be found, None otherwise
    def get_tl_thread(self):
        try:
            return self.get_ancestors(id=True).filter(tl_thread__isnull=False).last().tl_thread
        except:
            return None
    # }}}

    # {{{ get_matchset: Returns a queryset of matches
    def get_matchset(self):
        return Match.objects.filter(eventobj__uplink__parent=self)
    # }}}

    # {{{ get_immediate_matchset: Returns a queryset of matches attached to this event only. (May be faster
    # leaves.)
    def get_immediate_matchset(self):
        return self.match_set.all()
    # }}}

    # {{{ update_dates: Updates the fields earliest and latest
    def update_dates(self):
        res = self.get_matchset().aggregate(Max('date'), Min('date'))
        self.latest = res['date__max']
        self.earliest = res['date__min']
        self.save()
    # }}}

    # {{{ change_type(type): Modifies the type of this event, and possibly all ancestors and events
    def change_type(self, type):
        self.type = type
        self.save()

        # If EVENT or ROUND, children must be ROUND
        if type == TYPE_EVENT or type == TYPE_ROUND:
            self.get_children(id=False).update(type=TYPE_ROUND)

        # If EVENT or CATEGORY, parents must be CATEGORY
        if type == TYPE_EVENT or type == TYPE_CATEGORY:
            self.get_ancestors(id=False).update(type=TYPE_CATEGORY)
    # }}}

    # {{{ Standard setters
    def set_big(self, big):
        self.big = big
        self.save()

    def set_prizepool(self, prizepool):
        self.prizepool = prizepool
        self.save()

    def set_homepage(self, homepage):
        self.homepage = homepage if homepage != '' else None
        self.save()

    def set_lp_name(self, lp_name):
        self.lp_name = lp_name if lp_name != '' else None
        self.save()

    def set_tlpd_id(self, tlpd_id):
        self.tlpd_id = tlpd_id
        self.save()

    def set_tlpd_db(self, tlpd_db):
        self.tlpd_db = tlpd_db
        self.save()

    def set_tl_thread(self, tl_thread):
        self.tl_thread = tl_thread if tl_thread != '' else None
        self.save()

    def set_earliest(self, date):
        self.earliest = date
        self.save()

    def set_latest(self, date):
        self.latest = date
        self.save()

    def set_idx(self, idx):
        self.idx = idx
        self.save()
    # }}}

    # {{{ add_child(name, type, noprint=False, closed=False): Adds a new child to the right of all existing
    # children
    @transaction.atomic
    def add_child(self, name, type, big=False, noprint=False):
        idx = self.get_children(id=True).aggregate(Max('idx'))['idx__max'] + 1
        new = Event(name=name, parent=self, big=big, noprint=noprint, idx=idx)
        new.save()

        links = [
            EventAdjacency(parent_id=l.parent_id, child=new, distance=l.distance+1) 
            for l in self.uplink.all()
        ]
        EventAdjacency.objects.bulk_create(links)
        EventAdjacency.objects.create(parent=new, child=new, distance=0)

        new.update_name()
        new.change_type(type)

        return new
    # }}}

    # {{{ add_root(name, type, big=False, noprint=False): Adds a new root node
    @staticmethod
    @transaction.atomic
    def add_root(name, type, big=False, noprint=False):
        idx = Event.objects.aggregate(Max('idx'))['idx__max'] + 1
        new = Event(name=name, big=big, noprint=noprint, idx=idx)
        new.save()

        EventAdjacency.objects.create(parent=new, child=new, distance=0)

        new.update_name()
        new.change_type(type)

        return new
    # }}}

    # {{{ close: Closes this event and all children
    def close(self):
        self.get_children(id=True).update(closed=True)
    # }}}

    # {{{ open: Opens this event and all ancestors
    def open(self):
        self.get_ancestors(id=True).update(closed=False)
    # }}}

    # {{{ delete_earnings(ranked=True): Deletes earnings objects associated to this event fulfilling the
    # criteria.
    def delete_earnings(self, ranked=True):
        if ranked:
            Earnings.objects.filter(event=self).exclude(placement__exact=0).delete()
        else:
            Earnings.objects.filter(event=self, placement__exact=0).delete()
    # }}}

    # {{{ move_earnings(new_event): Moves earnings from this event to the new event
    # Will update the type of the new event to EVENT.
    def move_earnings(self, new_event):
        Earnings.objects.filter(event=self).update(event=new_event)
        self.set_prizepool(None)
        new_event.set_prizepool(True)
        new_event.change_type(Event.EVENT)
    # }}}
# }}}

# {{{ EventAdjacencies
class EventAdjacency(models.Model):
    class Meta:
        db_table = 'eventadjacency'

    parent = models.ForeignKey(Event, null=False, db_index=True, related_name='downlink')
    child = models.ForeignKey(Event, null=False, db_index=True, related_name='uplink')
    distance = models.IntegerField(null=True, default=None)

    # {{{ String representation
    def __str__(self):
        return str(self.parent) + ' -> ' + str(self.child) + ' (' + str(self.distance) + ')'
    # }}}
# }}}

# {{{ Players
class Player(models.Model):
    class Meta:
        ordering = ['tag']
        db_table = 'player'

    tag = models.CharField('In-game name', max_length=30, null=False, db_index=True)
    name = models.CharField('Full name', max_length=100, blank=True, null=True)
    birthday = models.DateField('Birthday', blank=True, null=True)
    mcnum = models.IntegerField('MC number', blank=True, null=True, default=None)

    # tlpd_db contains information in binary form on which TLPD databases to use:
    # 1 for Korean, 10 for International, 100 for HotS, 1000 for Hots beta, 10000 for WoL beta
    # So a value of 5 (00101 in binary) would correspond to a link to the Korean and HotS TLPD.  
    # Use bitwise AND (&) with the flags to check.
    tlpd_id = models.IntegerField('TLPD ID', blank=True, null=True)
    tlpd_db = models.IntegerField('TLPD Databases', blank=True, null=True)

    lp_name = models.CharField('Liquipedia title', blank=True, null=True, max_length=200)
    sc2c_id = models.IntegerField('SC2Charts.net ID', blank=True, null=True)
    sc2e_id = models.IntegerField('SC2Earnings.com ID', blank=True, null=True)

    country = models.CharField(
        'Country', max_length=2, choices=countries, blank=True, null=True, db_index=True)

    race = models.CharField('Race', max_length=1, choices=RACES, null=False, db_index=True)

    current_rating = models.ForeignKey('Rating', blank=True, null=True, related_name='current')

    # Domination fields (for use in the hall of fame)
    dom_val = models.FloatField('Domination', blank=True, null=True)
    dom_start = models.ForeignKey(Period, blank=True, null=True, related_name='player_dom_start')
    dom_end   = models.ForeignKey(Period, blank=True, null=True, related_name='player_dom_end')

    # {{{ String representation
    def __str__(self):
        if self.country != None and self.country != '':
            return self.tag + ' (' + self.race + ', ' + self.country + ')'
        else:
            return self.tag + ' (' + self.race + ')'
    # }}}

    # {{{ Standard setters
    def set_tag(self, tag):
        self.tag = tag
        self.save()

    def set_race(self, race):
        self.race = race
        self.save()
    
    def set_country(self, country):
        self.country = country
        self.save()
    
    def set_name(self, name):
        self.name = None if name == '' else name
        self.save()
    
    def set_birthday(self, birthday):
        self.birthday = None if birthday == '' else birthday
        self.save()

    def set_sc2c_id(self, sc2c_id):
        self.sc2c_id = None if sc2c_id == '' else sc2c_id
        self.save()

    def set_tlpd_id(self, tlpd_id):
        self.tlpd_id = tlpd_id
        self.save()

    def set_tlpd_db(self, tlpd_db):
        self.tlpd_db = tlpd_db
        self.save()

    def set_sc2e_id(self, sc2e_id):
        self.sc2e_id = None if sc2e_id == '' else sc2e_id
        self.save()

    def set_lp_name(self, lp_name):
        self.lp_name = None if lp_name == '' else lp_name
        self.save()
    # }}}

    # {{{ Adding and removing TLPD databases
    def add_tlpd_db(self, tlpd_db):
        self.tlpd_db |= tlpd_db
        self.save()

    def remove_tlpd_db(self, tlpd_db):
        self.tlpd_db -= self.tlpd_db & tlpd_db
        self.save()

    def set_tlpd_db(self, tlpd_db):
        self.tlpd_db = tlpd_db
        self.save()
    # }}}

    # {{{ set_aliases: Set aliases
    # Input: An array of string aliases, which are compared to existing aliases.
    # New ones are added, existing superfluous ones are removed. Returns True if something changed.
    def set_aliases(self, aliases):
        if aliases:
            old = []
            changed = False

            for alias in Alias.objects.filter(player=self):
                if alias.name not in aliases:
                    alias.delete()
                    changed = True
                else:
                    old.append(alias.name)

            new = [x for x in aliases if x not in old]

            for alias in new:
                Alias.add_player_alias(self, alias)
                changed = True

            return changed

        else:
            old = Alias.objects.filter(player=self)
            if old.exists():
                old.delete()
                return True
            return False
    # }}}

    # {{{ get_aliases: Returns all aliases as a list
    def get_aliases(self):
        return [a.name for a in self.alias_set.all()]
    # }}}

    # {{{ get_current_teammembership: Gets the current team membership object of this player, if any.
    def get_current_teammembership(self):
        try:
            return self.groupmembership_set.filter(current=True, group__is_team=True).first()
        except:
            return None
    # }}}

    # {{{ get_current_team: Gets the current team object of this player, if any.
    def get_current_team(self):
        try:
            return (
                self.groupmembership_set
                    .filter(current=True, group__is_team=True)
                    .select_related('group')
                    .first().group
            )
        except:
            return None
    # }}}

    # {{{ get_current_rating: Gets the current rating, if any.
    def get_current_rating(self):
        try:
            return (
                self.rating_set
                    .filter(period__computed=True)
                    .latest('period')
            )
        except:
            return None
    # }}}

    # {{{ get_latest_rating_update: Gets the latest rating of this player with decay zero, or None.
    def get_latest_rating_update(self):
        try:
            return self.rating_set.filter(decay=0).latest('period')
        except:
            return None
    # }}}

    # {{{ has_earnings: Checks whether the player has any earnings.
    def has_earnings(self):
        return self.earnings_set.exists()
    # }}}

    # {{{ get_matchset: Returns a queryset of all this player's matches.
    def get_matchset(self, related=[]):
        qset = Match.objects.filter(Q(pla=self) | Q(plb=self))

        if len(related) > 0:
            qset = qset.select_related(*related)
        qset = qset.prefetch_related('message_set')

        return qset.order_by('-date', '-id')
     # }}}
# }}}

# {{{ Stories
class Story(models.Model):
    class Meta:
        db_table = 'story'
        verbose_name_plural = 'stories'

    player = models.ForeignKey(Player, null=False)
    text = models.CharField('Text', max_length=200, null=False)
    date = models.DateField('Date', null=False)
    event = models.ForeignKey(Event, null=True)

    # {{{ String representation
    def __str__(self):
        return '%s - %s on %s' % (self.player.tag, self.text, str(self.date))
    # }}}
# }}}

# {{{ Groups
class Group(models.Model):
    class Meta:
        db_table = 'group'

    name = models.CharField('Name', max_length=100, null=False, db_index=True)
    shortname = models.CharField('Short name', max_length=25, null=True, blank=True)
    members = models.ManyToManyField(Player, through='GroupMembership')
    scoreak = models.FloatField('AK score', null=True, default=0.0)
    scorepl = models.FloatField('PL score', null=True, default=0.0)
    meanrating = models.FloatField('Rating', null=True, default=0.0)
    founded = models.DateField('Date founded', null=True, blank=True)
    disbanded = models.DateField('Date disbanded', null=True, blank=True)
    active = models.BooleanField('Active', null=False, default=True, db_index=True)
    homepage = models.CharField('Homepage', null=True, blank=True, max_length=200)
    lp_name = models.CharField('Liquipedia title', null=True, blank=True, max_length=200) 

    is_team = models.BooleanField('Team', null=False, default=True, db_index=True)
    is_manual = models.BooleanField('Manual entry', null=False, default=True)

    # {{{ String representation
    def __str__(self):
        return self.name
    # }}}

    # {{{ Standard setters
    def set_name(self, name):
        self.name = name
        self.save()
    
    def set_shortname(self, shortname):
        self.shortname = None if shortname == '' else shortname
        self.save()

    def set_homepage(self, homepage):
        self.homepage = None if homepage == '' else homepage
        self.save()
    
    def set_lp_name(self, lp_name):
        self.lp_name = None if lp_name == '' else lp_name
        self.save()    
    # }}}
    
    # {{{ set_aliases: Set aliases
    # Input: An array of string aliases, which are compared to existing aliases.
    # New ones are added, existing superfluous ones are removed.
    def set_aliases(self, aliases):
        if aliases:
            old = []

            for alias in Alias.objects.filter(group=self):
                if alias.name not in aliases:
                    alias.delete()
                else:
                    old.append(alias.name)

            new = [x for x in aliases if x not in old]

            for alias in new:
                Alias.add_group_alias(self, alias)

        else:
            Alias.objects.filter(group=self).delete()
    # }}}

    # {{{ get_aliases: Returns all aliases as a list
    def get_aliases(self):
        return [a.name for a in self.alias_set.all()]
    # }}}
# }}}

# {{{ GroupMemberships
class GroupMembership(models.Model):
    class Meta:
        db_table = 'groupmembership'

    player = models.ForeignKey(Player, null=False)
    group = models.ForeignKey(Group, null=False)

    start = models.DateField('Date joined', blank=True, null=True)
    end = models.DateField('Date left', blank=True, null=True)
    current = models.BooleanField('Current', default=True, null=False, db_index=True)
    playing = models.BooleanField('Playing', default=True, null=False, db_index=True)
    
    # {{{ String representation
    def __str__(self):
        return (
            'Player: %s Group: %s (%s - %s)' % 
            (self.player.tag, self.group.name, str(self.start), str(self.end))
        )
    # }}}
# }}}

# {{{ Aliases
class Alias(models.Model):
    class Meta:
        verbose_name_plural = 'aliases'
        db_table = 'alias'

    name = models.CharField('Alias', max_length=100, null=False)
    player = models.ForeignKey(Player, null=True)
    group = models.ForeignKey(Group, null=True)

    # {{{ String representation
    def __str__(self):
        return self.name
    # }}}
    
    # {{{ Standard adders
    @staticmethod
    def add_player_alias(player, name):
        new = Alias(player=player, name=name)
        new.save()

    @staticmethod
    def add_group_alias(group, name):
        new = Alias(group=group, name=name)
        new.save()
    # }}}
# }}}

# {{{ Matches
class Match(models.Model):
    class Meta:
        verbose_name_plural = 'matches'
        db_table = 'match'

    period = models.ForeignKey(Period, null=False)
    date = models.DateField('Date played', null=False)
    pla = models.ForeignKey(Player, related_name='match_pla', verbose_name='Player A', null=False)
    plb = models.ForeignKey(Player, related_name='match_plb', verbose_name='Player B', null=False)
    sca = models.SmallIntegerField('Score for player A', null=False, db_index=True)
    scb = models.SmallIntegerField('Score for player B', null=False, db_index=True)

    rca = models.CharField(max_length=1, choices=MRACES, null=False, verbose_name='Race A', db_index=True)
    rcb = models.CharField(max_length=1, choices=MRACES, null=False, verbose_name='Race B', db_index=True)

    treated = models.BooleanField('Computed', default=False, null=False)
    event = models.CharField('Event text (deprecated)', max_length=200, default='', blank=True)
    eventobj = models.ForeignKey(Event, null=True, blank=True, verbose_name='Event')
    submitter = models.ForeignKey(User, null=True, blank=True, verbose_name='Submitter')

    game = models.CharField(
        'Game', max_length=10, default=WOL, blank=False, null=False, choices=GAMES, db_index=True)
    offline = models.BooleanField('Offline', default=False, null=False, db_index=True)

    # Helper fields for fast loading of frequently accessed information
    rta = models.ForeignKey('Rating', related_name='rta', verbose_name='Rating A', null=True)
    rtb = models.ForeignKey('Rating', related_name='rtb', verbose_name='Rating B', null=True)

    # {{{ populate_orig: Populates the original data fields, to check later if anything changed.
    def populate_orig(self):
        try:
            self.orig_pla    = self.pla_id
            self.orig_plb    = self.plb_id
            self.orig_rca    = self.rca
            self.orig_rcb    = self.rcb
            self.orig_sca    = self.sca
            self.orig_scb    = self.scb
            self.orig_date   = self.date
            self.orig_period = self.period_id
        except:
            self.orig_pla    = None
            self.orig_plb    = None
            self.orig_rca    = None
            self.orig_rcb    = None
            self.orig_sca    = None
            self.orig_scb    = None
            self.orig_date   = None
            self.orig_period = None
    # }}}

    # {{{ changed_effect: Returns true if an effective change (requiring recomputation) has been made.
    def changed_effect(self):
        return (
              self.orig_pla != self.pla_id or self.orig_plb != self.plb_id
            or self.orig_rca != self.rca    or self.orig_rcb != self.rcb
            or self.orig_sca != self.sca    or self.orig_scb != self.scb
        )
    # }}}

    # {{{ changed_date: Returns true if the date has been changed.
    def changed_date(self):
        return self.orig_date != self.date
    # }}}

    # {{{ changed_period: Returns true if the period has been changed.
    def changed_period(self):
        return self.orig_period != self.period_id
    # }}}

    # {{{ __init__: Has been overloaded to call populate_orig.
    def __init__(self, *args, **kwargs):
        super(Match, self).__init__(*args, **kwargs)
        self.populate_orig()
    # }}}

    # {{{ save: Has been overloaded to check for effective changes, flagging a period as needing recomputation
    # if necessary.
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        # Check if the date have been changed. If it has, move to a different period if necessary.
        # Also prepare to update the earliest and latest fields of event objects.
        update_dates = False
        if self.changed_date():
            self.set_period()

            if self.eventobj:
                update_dates = True

        # If the period has been changed, or another effective change has been made, flag period(s).
        if self.changed_period() or self.changed_effect():
            try:
                self.orig_period.needs_recompute = True
                self.orig_period.save()
            except:
                pass

            try:
                self.period.needs_recompute = True
                self.period.save()
            except:
                pass

            self.treated = False

        # Save to DB and repopulate original fields.
        super(Match, self).save(force_insert, force_update, *args, **kwargs)
        self.populate_orig()

        if update_dates:
            for event in self.eventobj.get_ancestors(id=True):
                if self.date < event.earliest:
                    event.set_earliest(self.date)
                if self.date > event.latest:
                    event.set_latest(self.date)
    # }}}

    # {{{ delete: Has been overloaded to check for effective changes, flagging a period as needing
    # recomputation if necessary.
    def delete(self,  *args, **kwargs):
        self.period.needs_recompute = True
        self.period.save()

        eventobj = self.eventobj
        super(Match, self).delete(*args, **kwargs)

        # This is very slow if used for many matches, but that should rarely happen. 
        if eventobj:
            for event in self.eventobj.get_ancestors(id=True):
                event.update_dates()
    # }}}

    # {{{ set_period: Sets the correct period for this match depending on the date.
    def set_period(self):
        pers = Period.objects.filter(start__lte=self.date).filter(end__gte=self.date)
        self.period = pers[0]
    # }}}

    # {{{ set_ratings: Sets the ratings of the players if they exist.
    def set_ratings(self):
        try:
            self.rta = Rating.objects.get(player=self.pla, period_id=self.period_id-1)
        except:
            pass

        try:
            self.rtb = Rating.objects.get(player=self.plb, period_id=self.period_id-1)
        except:
            pass
    # }}}

    # {{{ set_date(date): Exactly what it says on the tin.
    def set_date(self, date):
        self.date = date
        self.save()
    # }}}

    # {{{ set_event(event): Updates the earliest and latest fields for both new and old event.
    def set_event(self, event):
        old = self.eventobj
        self.eventobj = event
        self.save()

        for e in event.get_ancestors(id=True):
            if self.date < e.earliest:
                e.set_earliest(self.date)
            if self.date > e.latest:
                e.set_latest(self.date)

        # This is very slow if used for many matches, but that should rarely happen.
        if oldevent:
            for event in oldevent.get_ancestors(id=True):
                event.update_dates()
    # }}}

    # {{{ String representation 
    def __str__(self):
        return '%s %s %s - %s %s' % (str(self.date), self.pla.tag, self.sca, self.scb, self.plb.tag)
    # }}}

    # {{{ get_winner: Returns the winner of this match, or None if tie.
    def get_winner(self):
        if self.sca > self.scb:
            return self.pla
        elif self.scb > self.sca:
            return self.plb
        return None
    # }}}

    # {{{ get_winner_score: Returns the score of the winner.
    def get_winner_score(self):
        return max(self.sca, self.scb)
    # }}}

    # {{{ get_loser_score: Returns the score of the loser.
    def get_loser_score(self):
        return min(self.sca, self.scb)
    # }}}

    # {{{ event_fullpath: Returns the full event name, taken from event object if available, or event text if
    # not. Can be None.
    def event_fullpath(self):
        return self.event if self.eventobj is None else self.eventobj.fullname
    # }}}

    # {{{ event_partpath: Returns the partial event name (up to the nearest non-ROUND ancestor), taken from
    # event object if available, or event text if not. Can be None.
    def event_partpath(self):
        return self.event if self.eventobj is None else self.eventobj.get_event_fullname()
    # }}}
# }}}

# {{{ Messages
class Message(models.Model):
    class Meta:
        db_table = 'message'

    type = models.CharField('Type', max_length=10, choices=MESSAGE_TYPES)

    title = models.CharField('Title', max_length=100, null=True)
    text = models.TextField('Text')

    player = models.ForeignKey(Player, null=True)
    event = models.ForeignKey(Event, null=True)
    group = models.ForeignKey(Group, null=True)
    match = models.ForeignKey(Match, null=True)
# }}}

# {{{ Earnings
class Earnings(models.Model):
    class Meta:
        db_table = 'earnings'

    event = models.ForeignKey(Event, verbose_name='Event', null=False)
    player = models.ForeignKey(Player, verbose_name='Player', null=False)
    earnings = models.IntegerField('Earnings (USD)', null=True, blank=True)
    origearnings = models.IntegerField('Earnings (original currency)')
    currency = models.CharField('Original currency', max_length=30)
    placement = models.IntegerField('Place')

    # {{{ set_earnings(event, payouts, currency): Sets earnings for a given event.
    # Payouts is a list of dicts with keys 'player', 'prize' and 'placement'.
    # TODO: Probably should be more subtle and not delete everything on change
    @staticmethod
    def set_earnings(event, payouts, currency, ranked):
        # Delete existent earnings of the given type
        if Earnings.objects.filter(event=event).exists():
            event.delete_earnings(ranked=ranked)

        for payout in payouts:
            new = Earnings(
                event=event,
                player=payout['player'],
                placement=payout['placement']+1,
                origearnings=payout['prize'],
                currency=currency,
            )
            new.save()

        Earnings.convert_earnings(event)

        event.set_prizepool(True)
    # }}}

    # {{{ convert_earnings(event): Performs currency conversion for all earnings associated to an event.
    @staticmethod
    def convert_earnings(event):
        earningobjs = Earnings.objects.filter(event=event)
        event.update_dates()
        date = event.latest

        for earning in earningobjs:
            if earning.currency == 'USD':
                earning.earnings = earning.origearnings
            else:
                exchangerates = ExchangeRates(date)
                earning.earnings = round(exchangerates.convert(earning.origearnings, earning.currency))
            earning.save()
    # }}}

    # {{{ String representation
    def __str__(self):
        return '#%i at %s: %s $%s' % (self.placement, self.event.fullname, self.player.tag, self.earnings)
    # }}}
# }}}

# {{{ PreMatchGroups
class PreMatchGroup(models.Model):
    class Meta:
        db_table = 'prematchgroup'
        verbose_name_plural = 'Prematch Groups'
        verbose_name = 'Prematch Group'

    date = models.DateField('Date')
    event = models.CharField('Event', max_length=200, default='', null=False, blank=True)
    source = models.CharField('Source', max_length=500, default='', null=True, blank=True)
    contact = models.CharField('Contact', max_length=200, default='', null=True, blank=True)
    notes = models.TextField('Notes', default='', null=True, blank=True)

    game = models.CharField('Game', max_length=10, default='wol', blank=False, null=False, choices=GAMES)
    offline = models.BooleanField(default=False, null=False)

    # {{{ String representation
    def __str__(self):
        return str(self.date) + ' ' + self.event
    # }}}
# }}}

# {{{ PreMatches
class PreMatch(models.Model):
    class Meta:
        db_table = 'prematch'
        verbose_name_plural = 'prematches'

    group = models.ForeignKey(PreMatchGroup, null=False, blank=False, verbose_name='Group')
    pla = models.ForeignKey(
        Player, related_name='prematch_pla', verbose_name='Player A', null=True, blank=True)
    plb = models.ForeignKey(
        Player, related_name='prematch_plb', verbose_name='Player B', null=True, blank=True)
    pla_string = models.CharField('Player A (str)', max_length=200, default='', null=True, blank=True)
    plb_string = models.CharField('Player A (str)', max_length=200, default='', null=True, blank=True)
    sca = models.SmallIntegerField('Score for player A', null=False)
    scb = models.SmallIntegerField('Score for player B', null=False)
    date = models.DateField('Date', null=False)

    rca = models.CharField(max_length=1, choices=MRACES, null=True, verbose_name='Race A')
    rcb = models.CharField(max_length=1, choices=MRACES, null=True, verbose_name='Race B')

    # {{{ String representation
    def __str__(self):
        ret = '(' + self.group.event + ') '
        ret += self.pla.tag if self.pla else self.pla_string
        ret += ' %i-%i ' % (self.sca, self.scb)
        ret += self.plb.tag if self.plb else self.plb_string
        return ret
    # }}}

    # {{{ event_fullpath and event_partpath: For compatibility with Match objects, where needed
    def event_fullpath(self):
        return self.group.event

    def event_partpath(self):
        return self.group.event
    # }}}

    # {{{ is_valid: Checks if this can be turned into a Match.
    def is_valid(self):
        print(self.pla, self.plb, self.rca, self.rcb)
        return self.pla is not None and self.plb is not None
    # }}}
# }}}

# {{{ Ratings
class Rating(models.Model):
    class Meta:
        ordering = ['period']
        db_table = 'rating'

    period = models.ForeignKey(Period, null=False, verbose_name='Period')
    player = models.ForeignKey(Player, null=False, verbose_name='Player')

    # Helper fields for fast loading of frequently accessed information
    prev = models.ForeignKey('Rating', related_name='prevrating', verbose_name='Previous rating', null=True)

    # Standard rating numbers
    rating = models.FloatField('Rating', null=False)
    rating_vp = models.FloatField('R-del vP', null=False)
    rating_vt = models.FloatField('R-del vT', null=False)
    rating_vz = models.FloatField('R-del vZ', null=False)

    # Standard rating deviations
    dev = models.FloatField('RD', null=False)
    dev_vp = models.FloatField('RD vP', null=False)
    dev_vt = models.FloatField('RD vT', null=False)
    dev_vz = models.FloatField('RD vZ', null=False)

    # Computed performance ratings
    comp_rat = models.FloatField('Perf', null=True, blank=True)
    comp_rat_vp = models.FloatField('P-del vP', null=True, blank=True)
    comp_rat_vt = models.FloatField('P-del vT', null=True, blank=True)
    comp_rat_vz = models.FloatField('P-del vZ', null=True, blank=True)

    # Backwards filtered rating numbers
    bf_rating = models.FloatField('BF', default=0, null=False)
    bf_rating_vp = models.FloatField('BF-del vP', default=0, null=False)
    bf_rating_vt = models.FloatField('BF-del vT', default=0, null=False)
    bf_rating_vz = models.FloatField('BF-del vZ', default=0, null=False)

    # Backwards filtered rating deviations
    bf_dev = models.FloatField('BFD', null=True, blank=True, default=1)
    bf_dev_vp = models.FloatField('BFD vP', null=True, blank=True, default=1)
    bf_dev_vt = models.FloatField('BFD vT', null=True, blank=True, default=1)
    bf_dev_vz = models.FloatField('BFD vZ', null=True, blank=True, default=1)

    # Ranks among all players (if player is active)
    position = models.IntegerField('Rank', null=True)
    position_vp = models.IntegerField('Rank vP', null=True)
    position_vt = models.IntegerField('Rank vT', null=True)
    position_vz = models.IntegerField('Rank vZ', null=True)

    decay = models.IntegerField('Decay', default=0, null=False)
    domination = models.FloatField(null=True, blank=True)

    # {{{ String representation
    def __str__(self):
        return self.player.tag + ' P' + str(self.period.id)
    # }}}

    # {{{ get_next: Get next rating object for the same palyer
    def get_next(self):
        try:
            if self.next:
                return self.next
        except:
            pass

        try:
            self.next = Rating.objects.get(prev=self)
            return self.next
        except:
            return None
    # }}}

    # {{{ get_ratings: Return all rating information in a list
    def ratings(self):
        return [self.rating, self.rating_vp, self.rating_vt, self.rating_vz]
    # }}}

    # {{{ get_devs: Return all RD information in a list
    def get_devs(self):
        return [self.dev, self.dev_vp, self.dev_vt, self.dev_vz]
    # }}}

    # {{{ rating_diff(_vx): Differences in rating between this and previous period
    def rating_diff(self, race=None):
        if self.prev is not None:
            a = self.get_totalrating(race) - self.prev.get_totalrating(race)
            return a
        return self.get_totalrating(race) - start_rating(self.player.country, self.period)

    def rating_diff_vp(self):
        return self.rating_diff('P')

    def rating_diff_vt(self):
        return self.rating_diff('T')

    def rating_diff_vz(self):
        return self.rating_diff('Z')
    # }}}

    # {{{ get_rating(race=None): Return rating delta by race
    def get_rating(self, race=None):
        if race == 'P':
            return self.rating_vp
        elif race == 'T':
            return self.rating_vt
        elif race == 'Z':
            return self.rating_vz
        return self.rating
    # }}}

    # {{{ get_dev(race=None): Return RD by race
    def get_dev(self, race=None):
        if race == 'P':
            return self.dev_vp
        elif race == 'T':
            return self.dev_vt
        elif race == 'Z':
            return self.dev_vz
        return self.dev
    # }}}

    # {{{ get_totalrating(race): Return total rating by race
    def get_totalrating(self, race):
        if race in ['P','T','Z']:
            return self.rating + self.get_rating(race)
        else:
            return self.rating

    def get_totalrating_vp(self):
        return self.get_totalrating('P')

    def get_totalrating_vt(self):
        return self.get_totalrating('T')

    def get_totalrating_vz(self):
        return self.get_totalrating('Z')
    # }}}

    # {{{ get_totaldev(race): Return total RD by race (expected total RD if None)
    def get_totaldev(self, race):
        if race in ['P','T','Z']:
            return sqrt(self.get_dev(None)**2 + self.get_dev(race)**2)
        else:
            d = self.get_dev(None)**2
            for r in ['P','T','Z']:
                d += self.get_dev(r)**2/9
            return sqrt(d)
    # }}}

    # {{{ set_rating(d, write_bf=False): Sets rating numbers as given by the dict d with keys MPTZ, writes
    # them to bf if write_bf is True
    def set_rating(self, d, write_bf=False):
        self.rating = d['M']
        self.rating_vp = d['P']
        self.rating_vt = d['T']
        self.rating_vz = d['Z']

        if write_bf:
            self.bf_rating = self.rating
            self.bf_rating_vp = self.rating_vp
            self.bf_rating_vt = self.rating_vt
            self.bf_rating_vz = self.rating_vz
    # }}}

    # {{{ set_dev(d, write_bf=False): Sets RD as given by the dict d with keys MPTZ, writes to bf if write_bf
    # is True
    def set_dev(self, d, write_bf=False):
        self.dev = d['M']
        self.dev_vp = d['P']
        self.dev_vt = d['T']
        self.dev_vz = d['Z']

        if write_bf:
            self.bf_dev = self.dev
            self.bf_dev_vp = self.dev_vp
            self.bf_dev_vt = self.dev_vt
            self.bf_dev_vz = self.dev_vz
    # }}}

    # {{{ set_comp_rating(d): Sets performance ratings as given by the dict d with keys MPTZ
    def set_comp_rating(self, d):
        self.comp_rat = d['M']
        self.comp_rat_vp = d['P']
        self.comp_rat_vt = d['T']
        self.comp_rat_vz = d['Z']
    # }}}

    # {{{ set_comp_dev(d): Sets performance RD as given by the dict d with keys MPTZ
    def set_comp_dev(self, d):
        self.comp_dev = d['M']
        self.comp_dev_vp = d['P']
        self.comp_dev_vt = d['T']
        self.comp_dev_vz = d['Z']
    # }}}
# }}}

# {{{ BalanceEntries
class BalanceEntry(models.Model):
    class Meta:
        db_table = 'balanceentry'

    date = models.DateField('Date', null=False)
    pvt_wins = models.IntegerField('PvT wins', null=False)
    pvt_losses = models.IntegerField('PvT losses', null=False)
    pvz_wins = models.IntegerField('PvZ wins', null=False)
    pvz_losses = models.IntegerField('PvZ losses', null=False)
    tvz_wins = models.IntegerField('TvZ wins', null=False)
    tvz_losses = models.IntegerField('TvZ losses', null=False)
    p_gains = models.FloatField('P gains', null=False)
    t_gains = models.FloatField('T gains', null=False)
    z_gains = models.FloatField('Z gains', null=False)
# }}}

# {{{ Cluster
class Cluster(models.Model):
    class Meta:
        db_table = 'cluster'
    
    period = models.ForeignKey(Period, null=False)
    player = models.ForeignKey(Player, null=False)
    cluster = models.IntegerField("Cluster", null=False)
    distance = models.IntegerField("Dist", null=True)
# }}}
