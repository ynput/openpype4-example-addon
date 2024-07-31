from typing import Literal, TYPE_CHECKING

from pydantic import validator

from ayon_server.lib.postgres import Postgres
from ayon_server.settings import (
    BaseSettingsModel,
    SettingsField,
    ensure_unique_names,
    normalize_name,
)
from ayon_server.settings.enum import (
    folder_types_enum,
    anatomy_presets_enum,
    addon_all_app_host_names_enum,
)
from ayon_server.types import (
    ColorRGB_hex,
    ColorRGBA_hex,
    ColorRGB_float,
    ColorRGBA_float,
    ColorRGB_uint8,
    ColorRGBA_uint8,
)

if TYPE_CHECKING:
    from ayon_server.addons import BaseServerAddon


async def async_enum_resolver() -> list[str]:
    """Return a list of project names."""
    return [row["name"] async for row in Postgres.iterate("SELECT name FROM projects")]


def enum_resolver() -> list[dict[str, str]]:
    """Return a list of value/label dicts for the enumerator.

    Returning a list of dicts is used to allow for a custom label to be
    displayed in the UI.
    """
    return [{"value": f"value{i}", "label": f"Label {i}"} for i in range(10)]


async def recursive_enum_resolver(
    addon: "BaseServerAddon",
    project_name: str | None = None,
    settings_variant: str = "production",
) -> list[str]:
    if addon is None:
        return []

    if project_name:
        settings = await addon.get_project_settings(
            project_name=project_name, variant=settings_variant
        )
    else:
        settings = await addon.get_studio_settings(variant=settings_variant)

    return settings.list_of_strings


class Colors(BaseSettingsModel):
    """Default is blue"""

    rgb_hex: ColorRGB_hex = SettingsField(
        "#0000ff",
        title="RGB Hex",
    )
    rgba_hex: ColorRGBA_hex = SettingsField(
        "#0000ff",
        title="RGBA Hex",
    )
    rgb_float: ColorRGB_float = SettingsField(
        (0, 0, 1),
        title="RGB Float",
    )
    rgba_float: ColorRGBA_float = SettingsField(
        (0, 0, 1, 1),
        title="RGBA Float",
    )
    rgb_uint8: ColorRGB_uint8 = SettingsField(
        (0, 0, 255),
        title="RGB Uint8",
    )
    rgba_uint8: ColorRGBA_uint8 = SettingsField(
        (0, 0, 255, 0),
        title="RGBA Uint8",
    )


class ConditionalModel1(BaseSettingsModel):
    _layout = "compact"
    something: str = SettingsField("", description="Something")


class ConditionalModel2(BaseSettingsModel):
    _layout = "compact"
    something_else: str = SettingsField("", description="Something else")
    something_else_number: int = SettingsField(0, description="Something else's number")


class ConditionalModel3(BaseSettingsModel):
    _title = "Something completely different"
    key1: str = SettingsField("", description="Key 1")
    key2: str = SettingsField("", description="Key 2")
    key3: str = SettingsField("", description="Key 3")


model_switcher_enum = [
    {"value": "model1", "label": "Something"},
    {"value": "model2", "label": "Something else"},
    {"value": "model3", "label": "Something completely different"},
]


class CompactListSubmodel(BaseSettingsModel):
    # Compact layout is used, when a submodel has just a few
    # attributes, which may be displayed in a single row

    _layout = "compact"
    name: str = SettingsField(..., title="Name")
    int_value: int = SettingsField(..., title="Integer")
    enum: list[str] = SettingsField(
        default_factory=list,
        title="Enum",
        enum_resolver=lambda: ["foo", "bar", "baz"],
    )

    @validator("name")
    def validate_name(cls, value):
        """Ensure name does not contain weird characters"""
        return normalize_name(value)


class NestedSettings(BaseSettingsModel):
    """Nested settings without grouping

    Submodels also support docstrings, which are propagated
    to the frontend. Just be aware a description attribute on
    the parent field will override the docstring.

    Docstring can be splitted to multiple paragraph simply
    by adding an empty line.
    """

    spam: bool = SettingsField(False, title="Spam")
    eggs: bool = SettingsField(False, title="Eggs")
    bacon: bool = SettingsField(False, title="Bacon")

    model_switcher: str = SettingsField(
        "",
        title="Model switcher",
        description="Switch between two models",
        enum_resolver=lambda: model_switcher_enum,
        conditionalEnum=True,
        section="Pseudo-dynamic models",
    )

    model1: ConditionalModel1 = SettingsField(default_factory=ConditionalModel1)
    model2: ConditionalModel2 = SettingsField(default_factory=ConditionalModel2)
    model3: ConditionalModel3 = SettingsField(default_factory=ConditionalModel3)

    nested_list_of_submodels: list[CompactListSubmodel] = SettingsField(
        [
            CompactListSubmodel(name="default", int_value=42, enum=["foo", "bar"]),
        ],
        title="A list of compact objects",
        required_items=["default"],
    )


class GroupedSettings(BaseSettingsModel):
    _isGroup = True
    your_name: str = SettingsField("", title="Name")
    your_quest: str = SettingsField("", title="Your quest")
    favorite_color: str = SettingsField(
        "red",
        title="Favorite color",
        enum_resolver=lambda: ["red", "green", "blue"],
    )


class DictLikeSubmodel(BaseSettingsModel):
    _layout = "expanded"

    name: str = SettingsField(..., title="Name", scope=["studio", "project", "site"])
    value1: str = SettingsField("", title="Value 1", scope=["studio", "project", "site"])
    value2: str = SettingsField("", title="Value 2", scope=["studio", "project", "site"])
    value3: str = SettingsField("", title="Value 3", scope=["studio", "project", "site"])
    value4: str = SettingsField("", title="Value 4")

    @validator("name")
    def validate_name(cls, value):
        """Ensure name does not contain weird characters"""
        return normalize_name(value)


class ExampleSettings(BaseSettingsModel):
    """Test addon settings.


    This is a test addon settings. It is used to test various
    features of the settings system.

    Docstrings are propagated to the frontend, so you can use
    them to describe your settings, submodels and their fields.

    On the frontend, docstrings are rendered as markdown, so you
    can use markdown syntax to format your descriptions, e.g.:
    **bold** , *italic* , `code`, [links](https://openpype.io)...
    """

    simple_string: str = SettingsField(
        "default value",
        title="Simple string",
        description="This is a simple string",
    )

    folder_type: str = SettingsField(
        "Asset",
        title="Folder type",
        description="Type of the folder the addon operates on",
        placeholder="Select folder type",
        enum_resolver=folder_types_enum,
    )

    anatomy_preset: str = SettingsField(
        "__primary__",
        title="Anatomy preset",
        description="Anatomy preset to use",
        enum_resolver=anatomy_presets_enum,
    )

    textarea: str = SettingsField(
        "",
        title="Textarea",
        widget="textarea",
        placeholder="Placeholder of the textarea field",
    )

    number: int = SettingsField(
        1,
        title="Number",
        description="Positive integer 1-10",
        gt=0,  # greater than
        le=10,  # less or equal
        placeholder="Placeholder of the number field",
    )

    # Scoped fields are shown only in specific contexts (studio/project/local)
    # By default, they are shown in studio and projects contexts

    hidden_setting: str = SettingsField(
        "you can't see me",
        title="Hidden setting",
        scope=[],
        description="This setting is hidden in all contexts",
    )

    all_scopes_setting: str = SettingsField(
        "You see me all the time",
        title="All scopes",
        scope=["studio", "project", "site"],
        description="This setting is shown in all contexts",
        section="Scoped fields",
    )

    studio_setting: str = SettingsField(
        "",
        title="Studio setting",
        scope=["studio"],
        description="This setting is only visible in studio scope",
    )

    project_setting: str = SettingsField(
        "",
        title="Project setting",
        scope=["project"],
        description="This setting is only visible in project scope",
    )

    project_site_setting: str = SettingsField(
        "",
        title="Project site setting",
        scope=["site"],
        description="This setting is only visible in the local scope",
    )

    all_scopes_list_of_submodels: list[DictLikeSubmodel] = SettingsField(
        default_factory=list,
        title="Dict-like list",
        scope=["studio", "project", "site"],
    )

    # Simple enumerators can be defined using Literal type

    simple_enum: Literal["red", "green", "blue"] = SettingsField(
        "red",
        title="Simple enum",
        section="Enumerators",
    )

    # For more complex enumerators, use enum_resolver function
    # which returns a list of items. enum_resolver can be both
    # async or blocking.

    # section argument is used to visually separate fields of the form
    # a horizontal line with a label will be shown just above the field
    # with a section argument

    project: str | None = SettingsField(
        None,
        enum_resolver=async_enum_resolver,
        title="Dynamic enum",
    )

    multiselect: list[str] = SettingsField(
        default_factory=list,
        title="Multiselect",
        enum_resolver=lambda: ["foo", "bar", "ba"],
    )

    app_host_names: list[str] = SettingsField(
        default_factory=list,
        title="App host names",
        enum_resolver=addon_all_app_host_names_enum,
    )

    # Enumerators can be defined using a list of dicts, where
    # each dict has "value" and "label" keys

    enum_with_labels: str = SettingsField(
        "value1",
        title="Enum with labels",
        enum_resolver=enum_resolver,
    )

    list_of_strings: list[str] = SettingsField(
        default_factory=list,
        title="List of strings",
        section="List",
    )

    recursive_enum: str = SettingsField(
        "",
        title="Recursive enum",
        enum_resolver=recursive_enum_resolver,
        section="Pick a value from the list above",
    )

    colors: Colors = SettingsField(
        default_factory=Colors,
        title="Colors",
    )

    # Settings models can be nested

    nested_settings: NestedSettings = SettingsField(
        default_factory=NestedSettings,
        title="Nested settings",
    )

    grouped_settings: GroupedSettings = SettingsField(
        default_factory=GroupedSettings,
        title="Grouped settings",
        description="Nested settings submodel with grouping",
    )

    list_of_submodels: list[CompactListSubmodel] = SettingsField(
        [
            CompactListSubmodel(name="default", int_value=42, enum=["foo", "bar"]),
        ],
        title="A list of compact objects",
        required_items=["default"],
    )

    dict_like_list: list[DictLikeSubmodel] = SettingsField(
        default_factory=list,
        title="Dict-like list",
    )


    @validator("list_of_submodels", "dict_like_list")
    def ensure_unique_names(cls, value):
        """Ensure name fields within the lists have unique names."""
        ensure_unique_names(value)
        return value
