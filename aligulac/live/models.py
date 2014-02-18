from django.contrib import admin
from django.db import models
from ratings.models import Player

KEY_TYPES = (
    ("m", "master"), 
    ("u", "upload")
)


class TournamentHost(models.Model):
    name = models.CharField("Name", max_length=25)

    def __str__(self):
        return self.name

class Tournament(models.Model):
    name = models.CharField("Name", max_length=50)

    running = models.BooleanField("IsRunning", default=False)

    host = models.ForeignKey(TournamentHost)

    def __str__(self):
        return self.name

class TournamentKey(models.Model):
    key = models.CharField("Key", max_length=64)
    
    key_type = models.CharField("Type", choices=KEY_TYPES, 
                                max_length=2)

    host = models.ForeignKey(TournamentHost, related_name="key")

    def __str__(self):
        return self.key_type + " key"

class Match(models.Model):
    pla = models.ForeignKey(Player, related_name='+')
    plb = models.ForeignKey(Player, related_name='+')

    sca = models.IntegerField()
    scb = models.IntegerField()

    tournament = models.ForeignKey(Tournament)

    def __repr__(self):
        return "{}-{} {}-{}".format(self.pla, self.plb, self.sca, self.scb)

    def __str__(self):
        return repr(self)

    def to_dict(self):
        return {
            "pla_id": self.pla_id,
            "plb_id": self.plb_id,
            "pla_tag": self.pla.tag,
            "plb_tag": self.plb.tag,
            "sca": self.sca,
            "scb": self.scb,
            "id": self.id,
            "tournament_id": self.tournament_id
        }

class Game(models.Model):
    
    game_index = models.IntegerField("GameIndex")

    map = models.CharField("Map", max_length=64)

    match = models.ForeignKey("Match")

    is_live = models.BooleanField("IsLive", default=False)

    class Meta:
        unique_together = ["game_index", "match"]

    def __str__(self):
        return "Game {} of {}, id: {}".format(self.game_index, self.match, self.id)

    def to_dict(self):
        return {
            "game_index": self.game_index, 
            "id": self.id, 
            "match_id": self.match_id
        }

LIVE_STATS_MAP = {
    "Update": "update",
    "GameTime": "game_time",
    "MineralsCurrent": "minerals_current",
    "MineralsIncome": "minerals_income",
    "MineralsGathered": "minerals_gathered",
    "GasCurrent": "gas_current",
    "GasIncome": "gas_income",
    "GasGathered": "gas_gathered",
    "SupplyCurrent": "supply_current",
    "SupplyCap": "supply_cap",
    "SupplyWorkers": "supply_workers",
    "SupplyArmy": "supply_army"
}

# https://code.djangoproject.com/wiki/DynamicModels
def create_model(name, fields=None, app_label='', module='', options=None, admin_opts=None):
    """
    Create specified model
    """
    class Meta:
        # Using type('Meta', ...) gives a dictproxy error during model creation
        pass

    if app_label:
        # app_label must be set using the Meta inner class
        setattr(Meta, 'app_label', app_label)

    # Update Meta with any options that were provided
    if options is not None:
        for key, value in options.items():
            setattr(Meta, key, value)

    # Set up a dictionary to simulate declarations within a class
    attrs = {'__module__': module, 'Meta': Meta}

    # Add in any fields that were provided
    if fields:
        attrs.update(fields)

    # Create the class, which automatically triggers ModelBase processing
    model = type(name, (models.Model,), attrs)

    # Create an Admin class if admin options were provided
    if admin_opts is not None:
        class Admin(admin.ModelAdmin):
            pass
        for key, value in admin_opts:
            setattr(Admin, key, value)
        admin.site.register(model, Admin)

    return model

def generate_live_stat_model():
    
    fields = dict()

    fields.update({
        "game": models.ForeignKey(Game),
        "player_index": models.IntegerField("PlayerIndex")
    })

    def to_json(self):
        d = {
            "player_index": self.player_index,
            "game_id": self.game_id
        }

        for k in LIVE_STATS_MAP:
            v = LIVE_STATS_MAP[k]
            d[v] = self.__dict__[v]

        return d

    fields["to_json"] = to_json

    for k in LIVE_STATS_MAP:
        fields[LIVE_STATS_MAP[k]] = models.IntegerField(k)

    meta_options = {
        "unique_together": [
            "update", 
            "player_index", 
            "game"
        ]
    }

    return create_model('LiveStat', fields=fields, app_label='live', module='live',
                        admin_opts={}, options=meta_options)

LiveStat = generate_live_stat_model()
