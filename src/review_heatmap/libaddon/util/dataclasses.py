# -*- coding: utf-8 -*-

# Libaddon for Anki
#
# Copyright (C) 2018-2021  Aristotelis P. <https//glutanimate.com/>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version, with the additions
# listed at the end of the license file that accompanied this program.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# NOTE: This program is subject to certain additional terms pursuant to
# Section 7 of the GNU Affero General Public License.  You should have
# received a copy of these additional terms immediately following the
# terms and conditions of the GNU Affero General Public License that
# accompanied this program.
#
# If not, please request a copy through one of the means of contact
# listed here: <https://glutanimate.com/contact/>.
#
# Any modifications to this file must keep this entire header intact.


import dataclasses
from typing import Any, Type


def dataclass_from_dataclass(
    old_dataclass_object: Any, new_dataclass_factory: Type
) -> Any:
    return new_dataclass_factory(
        **dataclass_as_dict_field_limited(
            old_dataclass_object=old_dataclass_object,
            new_dataclass_factory=new_dataclass_factory,
        )
    )


def dataclass_as_dict_field_limited(
    old_dataclass_object: Any, new_dataclass_factory: Type
) -> dict:
    old_dataclass_dict = dataclasses.asdict(old_dataclass_object)
    return limit_dict_by_dataclass_fields(old_dataclass_dict, new_dataclass_factory)


def limit_dict_by_dataclass_fields(dictionary: dict, dataclass_factory: Type) -> dict:
    field_names = set(f.name for f in dataclasses.fields(dataclass_factory))
    return {k: v for k, v in dictionary.items() if k in field_names}
