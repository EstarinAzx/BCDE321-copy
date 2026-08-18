from zimp.domain.common.dev_card import DevCard, CardEffect, CardEffectType

CARD_DATA = (
    DevCard(
        (CardEffect(CardEffectType.NONE),
        CardEffect(CardEffectType.ITEM),
        CardEffect(CardEffectType.ZOMBIES, 6)),
        1,
    ),
    DevCard(
        (CardEffect(CardEffectType.ZOMBIES, 4),
        CardEffect(CardEffectType.HEALTH, -1),
        CardEffect(CardEffectType.ITEM)),
        2,
    ),
    DevCard(
        (CardEffect(CardEffectType.ITEM),
        CardEffect(CardEffectType.ZOMBIES, 4),
        CardEffect(CardEffectType.HEALTH, -1)),
        3,
    ),
    DevCard(
        (CardEffect(CardEffectType.ZOMBIES, 4),
        CardEffect(CardEffectType.HEALTH, -1),
        CardEffect(CardEffectType.ZOMBIES, 6)),
        4,
    ),
    DevCard(
        (CardEffect(CardEffectType.ITEM),
        CardEffect(CardEffectType.ZOMBIES, 5),
        CardEffect(CardEffectType.HEALTH, -1)),
        5,
    ),
    DevCard(
        (CardEffect(CardEffectType.HEALTH, -1),
        CardEffect(CardEffectType.ZOMBIES, 4),
        CardEffect(CardEffectType.NONE)),
        6,
    ),
    DevCard(
        (CardEffect(CardEffectType.ZOMBIES, 3),
        CardEffect(CardEffectType.NONE),
        CardEffect(CardEffectType.ZOMBIES, 5)),
        7,
    ),
    DevCard(
        (CardEffect(CardEffectType.HEALTH, 1),
        CardEffect(CardEffectType.ITEM),
        CardEffect(CardEffectType.ZOMBIES, 4)),
        8,
    ),
    DevCard(
        (CardEffect(CardEffectType.NONE),
        CardEffect(CardEffectType.HEALTH, 1),
        CardEffect(CardEffectType.ZOMBIES, 4)),
        9,
    ),
)