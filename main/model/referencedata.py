from enum import Enum

class PokemonType(Enum):
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
    LEVEL = 'Level'
    MULTIPLIER = 'Multiplier'

class AttackPerPokemonColumn(Enum):
    ATTACK = 'Attack'
    POKEMON = 'Pokemon'

class ChargedAttackColumn(Enum):
    ATTACK = 'Charged attack'
    TYPE = 'Charged attack type'
    DAMAGE = 'Charged attack damage'
    ENERGY_COST = 'Charged attack energy cost'

class FastAttackColumn(Enum):
    ATTACK = 'Fast attack'
    TYPE = 'Fast attack type'
    TURNS = 'Fast attack duration'
    DAMAGE = 'Fast attack damage'
    ENERGY_GENERATED = 'Fast attack energy generated'

class PokemonTypeColumn(Enum):
    POKEMON = 'Pokemon'
    BASE_ATTACK = 'Base attack'
    BASE_DEFENCE = 'Base defence'
    BASE_HP = 'Base HP'
    TYPE_1 = 'Type 1'
    TYPE_2 = 'Type 2'