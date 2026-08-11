from zimp.domain.events.dev_card import DevCard, CardEffect, EffectType

CARD_DATA = (
    DevCard(
        (CardEffect(EffectType.NONE),
        CardEffect(EffectType.ITEM),
        CardEffect(EffectType.ZOMBIES, 6)),
        0,
    ),
    DevCard(
        (CardEffect(EffectType.ZOMBIES, 4),
        CardEffect(EffectType.HP, -1),
        CardEffect(EffectType.ITEM)),
        1,
    ),
    DevCard(
        (CardEffect(EffectType.ITEM),
        CardEffect(EffectType.ZOMBIES, 4),
        CardEffect(EffectType.HP, -1)),
        2,
    ),
    DevCard(
        (CardEffect(EffectType.ZOMBIES, 4),
        CardEffect(EffectType.HP, -1),
        CardEffect(EffectType.ZOMBIES, 6)),
        3,
    ),
    DevCard(
        (CardEffect(EffectType.ITEM),
        CardEffect(EffectType.ZOMBIES, 5),
        CardEffect(EffectType.HP, -1)),
        4,
    ),
    DevCard(
        (CardEffect(EffectType.HP, -1),
        CardEffect(EffectType.ZOMBIES, 4),
        CardEffect(EffectType.NONE)),
        5,
    ),
    DevCard(
        (CardEffect(EffectType.ZOMBIES, 3),
        CardEffect(EffectType.NONE),
        CardEffect(EffectType.ZOMBIES, 5)),
        6,
    ),
    DevCard(
        (CardEffect(EffectType.HP, 1),
        CardEffect(EffectType.ITEM),
        CardEffect(EffectType.ZOMBIES, 4)),
        7,
    ),
    DevCard(
        (CardEffect(EffectType.NONE),
        CardEffect(EffectType.HP, 1),
        CardEffect(EffectType.ZOMBIES, 4)),
        8,
    ),
)