'''
Reference data attributes and Pokemon type enums.
'''
from enum import Enum

class PokemonType(Enum):
    '''
    Types of Pokemon.
    '''
    NORMAL = 'Normal'
    FIRE = 'Fire'
    WATER = 'Water'
    GRASS = 'Grass'
    ELECTRIC = 'Electric'
    ICE = 'Ice'
    FIGHTING = 'Fighting'
    POISON = 'Poison'
    GROUND = 'Ground'
    FLYING = 'Flying'
    PSYCHIC = 'Psychic'
    BUG = 'Bug'
    ROCK = 'Rock'
    GHOST = 'Ghost'
    DRAGON = 'Dragon'
    DARK = 'Dark'
    STEEL = 'Steel'
    FAIRY = 'Fairy'

class CpmColumn(Enum):
    '''
    Attribute of a DataFrame that represents the combat power multiplier table.
    '''
    LEVEL = 'Level'
    MULTIPLIER = 'Multiplier'

class AttackPerPokemonColumn(Enum):
    '''
    Attribute of a DataFrame that represents attack to Pokemon mapping.
    '''
    ATTACK = 'Attack'
    POKEMON = 'Pokemon'

class ChargedAttackColumn(Enum):
    '''
    Attribute of a DataFrame that represents Pokemon charged attacks.
    '''
    ATTACK = 'Charged attack'
    TYPE = 'Charged attack type'
    DAMAGE = 'Charged attack damage'
    ENERGY_COST = 'Charged attack energy cost'

class FastAttackColumn(Enum):
    '''
    Attribute of a DataFrame that represents Pokemon fast attacks.
    '''
    ATTACK = 'Fast attack'
    TYPE = 'Fast attack type'
    TURNS = 'Fast attack duration'
    DAMAGE = 'Fast attack damage'
    ENERGY_GENERATED = 'Fast attack energy generated'

class PokemonTypeColumn(Enum):
    '''
    Attribute of a DataFrame that represents Pokemon types.
    '''
    POKEMON = 'Pokemon'
    BASE_ATTACK = 'Base attack'
    BASE_DEFENCE = 'Base defence'
    BASE_HP = 'Base HP'
    TYPE_1 = 'Type 1'
    TYPE_2 = 'Type 2'
