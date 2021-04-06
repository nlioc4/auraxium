"""Data classes for :mod:`auraxium.ps2.directive`."""

from typing import Optional

from ..base import ImageData
from ..types import LocaleData

from .base import RESTPayload

__all__ = [
    'DirectiveData',
    'DirectiveTierData',
    'DirectiveTreeData',
    'DirectiveTreeCategoryData'
]

# pylint: disable=too-few-public-methods


class DirectiveData(RESTPayload, ImageData):
    """Data class for :class:`auraxium.ps2.directive.Directive`.

    This class mirrors the payload data returned by the API, you may
    use its attributes as keys in filters or queries.
    """

    directive_id: int
    directive_tree_id: int
    directive_tier_id: int
    objective_set_id: int
    qualify_requirement_id: Optional[int] = None
    name: LocaleData
    description: Optional[LocaleData] = None


class DirectiveTierData(RESTPayload, ImageData):
    """Data class for :class:`auraxium.ps2.directive.DirectiveTier`.

    This class mirrors the payload data returned by the API, you may
    use its attributes as keys in filters or queries.
    """

    directive_tier_id: int
    directive_tree_id: int
    reward_set_id: Optional[int] = None
    directive_points: int
    completion_count: int
    name: LocaleData


class DirectiveTreeData(RESTPayload, ImageData):
    """Data class for :class:`auraxium.ps2.directive.DirectiveTree`.

    This class mirrors the payload data returned by the API, you may
    use its attributes as keys in filters or queries.
    """

    directive_tree_id: int
    directive_tree_category_id: int
    name: LocaleData
    description: Optional[LocaleData] = None


class DirectiveTreeCategoryData(RESTPayload):
    """Data class for :class:`auraxium.ps2.directive.DirectiveTreeCategory`.

    This class mirrors the payload data returned by the API, you may
    use its attributes as keys in filters or queries.
    """

    directive_tree_category_id: int
    name: LocaleData
