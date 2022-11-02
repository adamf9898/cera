import time
from typing import Optional, Union
import typing
import requests
import ijson
import json
import re
import msgspec


class TaggedBase(msgspec.Struct, tag_field="layout", tag=str.lower, rename="lower"):
    name: str
    set: str
    collector_number: str
    rarity: str


class Image_URIs(msgspec.Struct):
    """Spec describing images."""

    normal: str
    png: str
    small: str


class CardFace(msgspec.Struct):
    """Spec describing a card face."""

    name: str
    mana_cost: str
    type_line: Optional[str] = None
    cmc: Optional[float] = None
    mana_cost: Optional[str] = None
    loyalty: Optional[str] = None
    image_uris: Optional[Image_URIs] = None
    oracle_text: Optional[str] = None
    power: Optional[str] = None
    toughness: Optional[str] = None


class normal(TaggedBase):
    """Spec describing a Scryfall card."""

    oracle_id: str
    mana_cost: str
    image_uris: Image_URIs
    type_line: str
    cmc: float
    loyalty: Optional[str] = None
    oracle_text: Optional[str] = None
    power: Optional[str] = None
    toughness: Optional[str] = None


class split(TaggedBase):
    """Spec describing split card"""

    mana_cost: str
    oracle_id: str
    cmc: float
    card_faces: list[CardFace]
    type_line: str
    image_uris: Image_URIs


class flip(TaggedBase):
    """Spec describing split card"""

    mana_cost: str
    oracle_id: str
    cmc: float
    type_line: str
    card_faces: list[CardFace]
    image_uris: Image_URIs


class transform(TaggedBase):
    """Spec describing split card"""

    card_faces: list[CardFace]
    oracle_id: str
    type_line: str
    cmc: Optional[float]


class modal_dfc(TaggedBase):
    """Spec describing split card"""

    card_faces: list[CardFace]
    oracle_id: str
    cmc: Optional[float]
    type_line: Optional[str]


class meld(TaggedBase):
    """Spec describing split card"""

    mana_cost: str
    oracle_id: str
    cmc: float
    type_line: str
    image_uris: Image_URIs
    loyalty: Optional[str] = None
    oracle_text: Optional[str] = None
    power: Optional[str] = None
    toughness: Optional[str] = None


class leveler(TaggedBase):
    """Spec describing split card"""

    mana_cost: str
    oracle_id: str
    cmc: float
    oracle_text: str
    type_line: str
    image_uris: Image_URIs
    power: Optional[str] = None
    loyalty: Optional[str] = None
    toughness: Optional[str] = None


class Class(TaggedBase):
    """Spec describing split card"""

    mana_cost: str
    oracle_id: str
    cmc: float
    type_line: str
    image_uris: Image_URIs
    oracle_text: str


class saga(TaggedBase):
    """Spec describing split card"""

    mana_cost: str
    oracle_id: str
    cmc: float
    type_line: str
    image_uris: Image_URIs
    oracle_text: str


class adventure(TaggedBase):
    """Spec describing split card"""

    mana_cost: str
    oracle_id: str
    image_uris: Image_URIs
    cmc: float
    type_line: str
    oracle_text: Optional[str] = None
    power: Optional[str] = None
    toughness: Optional[str] = None


class planar(TaggedBase):
    """Spec describing split card"""

    pass


class scheme(TaggedBase):
    """Spec describing split card"""

    pass


class vanguard(TaggedBase):
    """Spec describing split card"""

    pass


class token(TaggedBase):
    """Spec describing split card"""

    pass


class double_faced_token(TaggedBase):
    """Spec describing split card"""

    pass


class emblem(TaggedBase):
    """Spec describing split card"""

    pass


class augment(TaggedBase):
    """Spec describing split card"""

    pass


class host(TaggedBase):
    """Spec describing split card"""
    oracle_id: str
    mana_cost: str
    image_uris: Image_URIs
    type_line: str
    cmc: float
    loyalty: Optional[str] = None
    oracle_text: Optional[str] = None
    power: Optional[str] = None
    toughness: Optional[str] = None


class art_series(TaggedBase):
    """Spec describing split card"""

    pass


class reversible_card(TaggedBase):
    """Spec describing split card"""

    card_faces: list[CardFace]


AllCardTypes = Union[
    adventure,
    art_series,
    augment,
    Class,
    double_faced_token,
    emblem,
    flip,
    host,
    leveler,
    meld,
    modal_dfc,
    normal,
    planar,
    reversible_card,
    saga,
    scheme,
    split,
    token,
    transform,
    vanguard,
]

decoder = msgspec.json.Decoder(list[AllCardTypes]).decode


def msgspec_collection(cardlist, out_dict=False):
    """Returns list of JSON data containing all cards from the list by collector_number and set."""
    blob_json = []
    out = {}
    with open("default-cards.json", "rb") as f:
        for c in decoder(f.read()):
            if (
                isinstance(c, art_series)
                or isinstance(c, emblem)
                or isinstance(c, double_faced_token)
                or isinstance(c, token)
                or isinstance(c, vanguard)
                or isinstance(c, planar)
                or isinstance(c, augment)
                or isinstance(c, scheme)
            ):
                continue
            if [c.collector_number, c.set] in cardlist:
                card_obj = tts_parse(c)
                blob_json.append(card_obj)
                out[f"{c.collector_number}{c.set}"] = card_obj
    if out_dict:
        return out
    return blob_json


def italicize_reminder(text: str):
    out = re.sub(r"\(", "[i](", text)
    out = re.sub(r"\)", ")[/i]", out)
    return out


def make_oracle_dfc(card_dota: Union[transform, modal_dfc], is_reverse=False):
    face_1 = card_dota.card_faces[0]
    face_2 = card_dota.card_faces[1]
    descriptionHold = (
        ("" if is_reverse else "[6E6E6E]")
        + f"[b]{face_1.name} {face_1.mana_cost}[\b]"
        + "\n"
        + f"{face_1.type_line} {plus_rarity(card_dota.rarity)}"
        + "\n"
        + italicize_reminder(face_1.oracle_text if face_1.oracle_text is not None else "")
        + (
            f"\n[b]{face_1.power}/{face_1.toughness}[/b]"
            if face_1.power is not None and face_2.toughness is not None
            else ""
        )
        + (
            f"\n[b]{face_1.loyalty}[/b] Starting Loyalty"
            if face_1.loyalty is not None
            else "" + "\n" + "[6E6E6E]"
            if is_reverse
            else "[-]"
        )
        + "\n"
        + f"[b]{face_2.name} {face_2.mana_cost}[/b]"
        + "\n"
        + f'{face_2["type_line"]} {plus_rarity(card_dota.rarity)}'
        + "\n"
        + italicize_reminder(face_2.oracle_text)
        + (
            f"\n[b]{face_2.power}/{face_2.toughness}[/b]"
            if ("Creature" in face_2.type_line or "Vehicle" in face_2.type_line)
            else ""
        )
        + (
            (f"\n[b]{face_2.loyalty}[/b] Starting Loyalty" if face_2.loyalty is not None else "")
            if "loyalty" in face_2.keys()
            else ""
        )
        + ("[-]" if is_reverse else "")
    )
    return descriptionHold


def make_oracle_normal(card_data: Union[normal, meld]):
    descriptionHold = (
        f"[b]{card_data.name} {card_data.mana_cost}[/b]"
        + "\n"
        + f"{card_data.type_line} {plus_rarity(card_data.rarity)}"
        + "\n"
        + italicize_reminder(card_data.oracle_text)
        + (
            f"\n[b]{card_data.power}/{card_data.toughness}[/b]"
            if card_data.power is not None and card_data.toughness is not None
            else ""
        )
        + (f"\n[b]{card_data.loyalty}[/b] Starting Loyalty" if card_data.loyalty is not None else "")
    )
    return descriptionHold

def make_oracle_saga(card_data: Union[saga, Class]):
    descriptionHold = (
        f"[b]{card_data.name} {card_data.mana_cost}[/b]"
        + "\n"
        + f"{card_data.type_line} {plus_rarity(card_data.rarity)}"
        + "\n"
        + italicize_reminder(card_data.oracle_text)
    )
    return descriptionHold


def make_oracle_splitadventure(card_data: Union[split, adventure]):
    descriptionHold = (
        "[b]"
        + f"[b]{card_data.card_faces[0].name} {card_data.card_faces[0].mana_cost}[/b]"
        + "\n"
        + f"{card_data.card_faces[0].type_line} {plus_rarity(card_data.rarity)}"
        + "\n"
        + italicize_reminder(card_data.card_faces[0]["oracle_text"])
        + (
            "\n[b]" + card_data.card_faces[0].power + "/" + card_data.card_faces[0].toughness + "[/b]\n"
            if card_data.card_faces[0].power is not None and card_data.card_faces[0].toughness is not None
            else ""
        )
        + "\n"
        + f"[b]{card_data.card_faces[1].name} {card_data.card_faces[1].mana_cost}[/b]"
        + "\n"
        + f"{card_data.card_faces[1].type_line} {plus_rarity(card_data.rarity)}"
        + "\n"
        + italicize_reminder(card_data.card_faces[1].oracle_text)
        if card_data.card_faces[1].oracle_text is not None
        else ""
        + "\n"
        + (
            "\n[b]" + card_data.card_faces[1].power + "/" + card_data.card_faces[1].toughness + "[/b]\n"
            if "power" in card_data.card_faces[1].keys() and "toughness" in card_data.card_faces[1].keys()
            else ""
        )
    )
    return descriptionHold


def make_oracle_reversible(card_data: reversible_card):
    return


def make_oracle_vanguard(card_data: vanguard):
    descriptionHold = (
        "[b]"
        + card_data["name"]
        + card_data["mana_cost"]
        + "[/b]"
        + "\n"
        + card_data["type_line"]
        + plus_rarity(card_data["rarity"])
        + "\n"
        + italicize_reminder(card_data["oracle_text"])
        + "\n"
        + f'Life: {card_data["life_modifier"]} + 20 = [b]{(20 + int(card_data["life_modifier"]))}[/b]'
        + "\n"
        + f'Hand: {card_data["hand_modifier"]} + 7 = [b]{(7 + int(card_data["hand_modifier"]))}[/b]'
    )
    return descriptionHold


def plus_rarity(rarity):
    # Colors scraped from Scryfall
    if rarity == "mythic":
        # f64800
        return "[f64800]「M」[-]"
    elif rarity == "rare":
        # c5b37c
        return "[c5b37c]「R」[-]"
    elif rarity == "uncommon":
        # 6c848c
        return "[6c848c]「U」[-]"
    elif rarity == "common":
        # 16161d
        return "「C」"
    elif rarity == "special":
        # 905d98
        return "[905d98]「S」[-]"
    elif rarity == "bonus":
        # 9c202b
        return "[9c202b]「B」[-]"
    return ""


def tts_parse(o: AllCardTypes) -> dict[str, dict]:
    card_obj = {
        "oracle_id": o.oracle_id if o.oracle_id is not None else "",
        "cmc": o.cmc if o.cmc is not None else 0,
        "type_line": o.type_line if o.type_line is not None else "",
        "set": o.set,
        "name": o.name,
        "collector_number": o.collector_number,
    }
    if isinstance(o, transform) or isinstance(o, modal_dfc):
        extra_obj = {
            "card_faces": [
                {
                    "name": i.name,
                    "type_line": i.type_line if i.type_line is not None else "",
                    "oracle_text": make_oracle_dfc(o, c == 0),
                    "image_uris": {"normal": i.image_uris.normal, "small": i.image_uris.small},
                    "power": i.power if i.power is not None else 0,
                    "toughness": i.toughness if i.toughness is not None else 0,
                    "mana_cost": i.mana_cost if i.mana_cost is not None else "",
                    "loyalty": i.loyalty if i.loyalty is not None else 0,
                }
                for c, i in enumerate(o.card_faces)
            ],
            "layout": "transform",
        }
    elif isinstance(o, split):
        extra_obj = {
            "type_line": o.type_line,
            "oracle_text": make_oracle_splitadventure(o),
            "image_uris": {"normal": o.image_uris.normal, "small": o.image_uris.small},
            "power": 0,
            "toughness": 0,
            "mana_cost": o.mana_cost if o.mana_cost is not None else "",
            "loyalty": 0,
            "layout": "split",
        }
    elif isinstance(o, flip):
        extra_obj = {
            "card_faces": [
                {
                    "name": i.name,
                    "type_line": i.type_line if i.type_line is not None else "",
                    "oracle_text": make_oracle_dfc(o, c == 0),
                    "image_uris": {"normal": o.image_uris.normal, "small": o.image_uris.small},
                    "power": i.power if i.power is not None else 0,
                    "toughness": i.toughness if i.toughness is not None else 0,
                    "mana_cost": i.mana_cost if i.mana_cost is not None else "",
                    "loyalty": i.loyalty if i.loyalty is not None else 0,
                }
                for c, i in enumerate(o.card_faces)
            ],
            "layout": "flip",
        }
    elif isinstance(o, adventure):
        extra_obj = {
            "oracle_text": make_oracle_splitadventure(o),
            "image_uris": {"normal": o.image_uris.normal, "small": o.image_uris.small},
            "power": 0,
            "toughness": 0,
            "mana_cost": o.mana_cost,
            "loyalty": 0,
            "layout": "adventure",
        }
    elif isinstance(o, vanguard):
        extra_obj = {
            "oracle_text": make_oracle_vanguard(o),
            "image_uris": {"normal": o.image_uris.normal},
            "power": 0,
            "toughness": 0,
            "mana_cost": "",
            "loyalty": 0,
            "layout": "vanguard",
        }
    elif isinstance(o, reversible_card):
        extra_obj = {
            "card_faces": [
                {
                    "name": i.name,
                    "type_line": i.type_line if i.type_line is not None else "",
                    "oracle_text": make_oracle_dfc(o, c == 0),
                    "image_uris": {
                        "normal": i.image_uris.normal if i.image_uris is not None else "https://i.imgur.com/TyC0LWj.jpg"
                    },
                    "power": 0,
                    "toughness": 0,
                    "mana_cost": i.mana_cost if i.mana_cost is not None else "",
                    "loyalty": 0,
                }
                for c, i in enumerate(o.card_faces)
            ],
            "type_line": o.card_faces[0].type_line + " // " + o.card_faces[1].type_line,
            "cmc": o.card_faces[0].cmc,
            "oracle_id": o.card_faces[0].oracle_id,
            "layout": "reversible_card",
        }
    elif (
        isinstance(o, normal)
        or isinstance(o, meld)
        or isinstance(o, leveler)
        or isinstance(o, host)
    ):
        extra_obj = {
            "oracle_text": make_oracle_normal(o),
            "image_uris": {"normal": o.image_uris.normal, "small": o.image_uris.small},
            "power": o.power if o.power is not None else 0,
            "toughness": o.toughness if o.toughness is not None else 0,
            "mana_cost": o.mana_cost,
            "loyalty": o.loyalty if o.loyalty is not None else 0,
            "layout": "normal",
        }
    elif isinstance(o, Class) or isinstance(o, saga):
        extra_obj = {
            "oracle_text": make_oracle_saga(o),
            "image_uris": {"normal": o.image_uris.normal, "small": o.image_uris.small},
            "power": 0,
            "toughness": 0,
            "mana_cost": o.mana_cost,
            "loyalty": 0,
            "layout": "normal",
        }
    card_obj = {**card_obj, **extra_obj}
    return card_obj
