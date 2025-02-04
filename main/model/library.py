'''
Library data attributes.
'''
from enum import Enum

class LibraryColumn(Enum):
    '''
    Attribute of a DataFrame that represents the Pokemon
    library, pre-enrichment.
    '''
    POKEMON_NAME = 'Name'
    POKEMON_TYPE = 'Pokemon'
    POKEMON_LEVEL = 'Level'
    FAST_ATTACK = 'Fast attack'
    CHARGED_ATTACK = 'Charged attack'
    ATTACK = 'IV attack'
    DEFENCE = 'IV defence'
    HP = 'IV HP'

class EnrichedLibraryColumn(Enum):
    '''
    Attribute of a DataFrame that represents the Pokemon
    library, post-enrichment.
    '''
    MAX_ATTACK = 'Max attack'
    MAX_DEFENCE = 'Max defence'
    MAX_HP = 'Max HP'
    REAL_ATTACK = 'Real attack'
    REAL_DEFENCE = 'Real defence'
    REAL_HP = 'Real HP'
    CP = 'CP'
    FAST_ATTACK_STAB = 'Fast attack STAB'
    CHARGED_ATTACK_STAB = 'Charged attack STAB'
    ATTACK_CYCLE_LENGTH = 'Attack cycle length'
    ATTACK_CYCLE_DAMAGE = 'Attack cycle damage'
    DPT = 'DPT'
