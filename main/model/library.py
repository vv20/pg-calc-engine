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
    CHARGED_ATTACK_1 = 'Charged attack 1'
    CHARGED_ATTACK_2 = 'Charged attack 2'
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
    CHARGED_ATTACK_1_TYPE = 'Charged attack 1 type'
    CHARGED_ATTACK_1_DAMAGE = 'Charged attack 1 damage'
    CHARGED_ATTACK_1_ENERGY_COST = 'Charged attack 1 energy cost'
    CHARGED_ATTACK_1_STAB = 'Charged attack 1 STAB'
    ATTACK_CYCLE_1_LENGTH = 'Attack cycle 1 length'
    ATTACK_CYCLE_1_DAMAGE = 'Attack cycle 1 damage'
    DPT_1 = 'DPT 1'
    CHARGED_ATTACK_2_TYPE = 'Charged attack 2 type'
    CHARGED_ATTACK_2_DAMAGE = 'Charged attack 2 damage'
    CHARGED_ATTACK_2_ENERGY_COST = 'Charged attack 2 energy cost'
    CHARGED_ATTACK_2_STAB = 'Charged attack 2 STAB'
    ATTACK_CYCLE_2_LENGTH = 'Attack cycle 2 length'
    ATTACK_CYCLE_2_DAMAGE = 'Attack cycle 2 damage'
    DPT_2 = 'DPT 2'
