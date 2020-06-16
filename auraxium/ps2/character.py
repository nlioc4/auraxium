"""Objects related to characters."""

import dataclasses
import datetime
import logging
from typing import Awaitable, ClassVar, Dict, Final, Optional, Union

from ..base import Named, Ps2Data
from ..cache import TLRUCache
from ..census import Query
from ..client import Client
from ..request import extract_single, run_query
from ..types import CensusData

from .faction import Faction

__all__ = ['Character']

log = logging.getLogger('auraxium.ps2')


@dataclasses.dataclass(frozen=True)
class CharacterData(Ps2Data):
    """Data container for Character objects."""

    character_id: int
    name: Dict[str, str]
    faction_id: int
    title_id: Optional[int]
    prestige_level: int
    times: CensusData
    certs: CensusData
    battle_rank: CensusData
    profile_id: int
    daily_ribbon: CensusData  # Optional for deleted chars?

    @classmethod
    def populate(cls, payload: CensusData) -> 'CharacterData':
        return cls(
            # Required
            int(payload['character_id']),
            payload['name'],
            int(payload['faction_id']),
            int(payload.get('title_id', -1)),
            int(payload['prestige_level']),
            payload['times'],
            payload['certs'],
            payload['battle_rank'],
            int(payload['profile_id']),
            payload['daily_ribbon'])


class Character(Named, cache_size=256, cache_ttu=300.0):
    """A player-controlled character."""

    _cache: ClassVar[TLRUCache[Union[int, str], 'Character']]
    data: CharacterData
    _collection = 'character'
    _id_field = 'character_id'

    @property
    def asp_rank(self) -> int:
        """Return the ASP rank of the player."""
        return int(self.data.prestige_level)

    @property
    def battle_rank(self) -> int:
        """Return the battle rank of the player."""
        return int(self.data.battle_rank['value'])

    @property
    def battle_rank_progress(self) -> float:
        """Return the progress to the next battle rank."""
        return float(self.data.battle_rank['percent_to_next'])

    @property
    def created(self) -> datetime.datetime:
        """Return the creation date of the character."""
        return datetime.datetime.utcfromtimestamp(
            int(self.data.times['creation']))

    @property
    def daily_ribbons(self) -> int:
        """Return the number of available daily ribbons."""
        return int(self.data.daily_ribbon['count'])

    @property
    def faction(self) -> Awaitable[Faction]:
        """Return the faction of the player."""

        async def get_faction() -> Faction:
            faction_id = int(self.data.faction_id)
            faction = await Faction.get_by_id(faction_id, client=self._client)
            assert faction is not None
            return faction

        return get_faction()

    @property
    def last_seen(self) -> datetime.datetime:
        """Return the last save date of the character."""
        return datetime.datetime.utcfromtimestamp(
            int(self.data.times['last_seen']))

    @property
    def last_login(self) -> datetime.datetime:
        """Return the last save date of the character."""
        return datetime.datetime.utcfromtimestamp(
            int(self.data.times['last_login']))

    @property
    def playtime(self) -> float:
        """Return the total playtime of the character in hours."""
        return float(self.data.times['minutes_played']) / 60.0

    @property
    def certs(self) -> int:
        """Return the current certification balance of the player."""
        return int(self.data.certs['available_points'])

    @property
    def certs_earned(self) -> int:
        """Return the number of earned certification points."""
        return int(self.data.certs['earned_points'])

    @property
    def certs_gifted(self) -> int:
        """Return the number of gifted certification points."""
        return int(self.data.certs['gifted_points'])

    @property
    def certs_spent(self) -> int:
        """Return the number of spent certification points."""
        return int(self.data.certs['spent_points'])

    # @property
    # def profile(self) -> Awaitable[Profile]:
    #     """Return the current profile of the player."""

    #     async def get_profile() -> Profile:
    #         profile_id = int(self.data.profile_id)
    #         profile = await Profile.get_by_id(profile_id, client=self._client)
    #         assert profile is not None
    #         return profile

    #     return get_profile()

    # @property
    # def title(self) -> Awaitable[Title]:
    #     """Return the title of the player."""

    #     async def get_title() -> Title:
    #         title_id = int(self.data.title_id)
    #         title = await Title.get_by_id(title_id, client=self._client)
    #         assert title is not None
    #         return title

    #     return get_title()

    @property
    def is_online(self) -> Awaitable[bool]:
        """Return the online status of the player."""

        async def get_online_status() -> bool:
            query = Query('characters_online_status', character_id=self.id)
            data = await run_query(query, session=self._client.session)
            payload = extract_single(data, 'characters_online_status')
            return bool(payload['online_status'])

        return get_online_status()

    def _build_dataclass(self, payload: CensusData) -> CharacterData:
        return CharacterData.populate(payload)

    @classmethod
    async def get_by_id(cls, id_: int, *, client: Client
                        ) -> Optional['Character']:
        """Retrieve an object by their unique Census ID.

        Args:
            id_: The unique ID of the character.
            client: The client through which to perform the request.

        Returns:
            The character with the matching ID, or None if not found.

        """
        table: Final[str] = 'single_character_by_id'
        log.debug('<%s:%d> requested', cls.__name__, id_)
        if (instance := cls._cache.get(id_)) is not None:
            log.debug('%r restored from cache', instance)
            return instance
        log.debug('<%s:%d> not cached, generating API query...',
                  cls.__name__, id_)
        query = Query(collection=table, service_id=client.service_id)
        query.add_term(field=cls._id_field, value=id_).limit(1)
        data = await run_query(query, session=client.session)
        payload = extract_single(data, table)
        return cls(payload, client=client)

    @classmethod
    async def get_by_name(cls, name: str, *, locale: str = 'en', client: Client
                          ) -> Optional['Character']:
        """Retrieve an object by its unique name.

        This query is always case-insensitive.

        Args:
            client: The client through which to perform the request.
            name: The name to search for.
            locale (optional): The locale of the search key. Defaults
                to 'en'.

        Returns:
            The entry with the matching name, or None if not found.

        """
        log.debug('%s "%s"[%s] requested', cls.__name__, name, locale)
        if (instance := cls._cache.get(f'_{name.lower()}')) is not None:
            log.debug('%r restored from cache', instance)
            return instance
        log.debug('%s "%s"[%s] not cached, generating API query...',
                  cls.__name__, name, locale)
        query = Query(collection=cls._collection, service_id=client.service_id)
        query.add_term(field='name.first_lower', value=name.lower())
        data = await run_query(query, session=client.session)
        payload = extract_single(data, cls._collection)
        return cls(payload, client=client)

    def name(self, locale: str = 'en') -> str:
        """Return the unique name of the player.

        Since character names are not localised, the "locale" kwarg is
        ignored.

        This will always return the capitalised version of the name.
        Use the built-int str.lower() method for a lowercase version.
        """
        return str(self.data.name)
