from ayon_server.actions import SimpleActionManifest


EXAMPLE_SIMPLE_ACTIONS = [
    SimpleActionManifest(
        identifier="example-folder-action-1",
        label="Example folder action 1",
        category="server",
        order=100,
        icon={"type": "material-symbols", "name": "folder"},

        entity_type="folder",
        entity_subtypes=None,
        allow_multiselection=False,
    ),
    SimpleActionManifest(
        identifier="example-folder-action-2",
        label="Example folder action 2",
        category="admin",
        order=100,
        icon={"type": "material-symbols", "name": "delete"},

        entity_type="folder",
        entity_subtypes=None,
        allow_multiselection=False,
    ),
    SimpleActionManifest(
        identifier="example-task-action",
        label="Task Action",
        category="server",
        order=100,
        icon={"type": "material-symbols", "name": "task"},

        entity_type="task",
        entity_subtypes=None,
        allow_multiselection=False,
    ),
    SimpleActionManifest(
        identifier="launch-nuke",
        label="Launch Nuke",
        category="application",
        order=100,
        icon={"type": "url", "url": "{addon_url}/public/icons/nuke.png"},

        entity_type="task",
        entity_subtypes=["Compositing", "Roto", "Matchmove"],
        allow_multiselection=True,
    ),
    SimpleActionManifest(
        identifier="launch-photoshop",
        label="Launch Photoshop",
        category="application",
        order=100,
        icon={"type": "url", "url": "{addon_url}/public/icons/photoshop.png"},

        entity_type="task",
        entity_subtypes=["Compositing", "Texture"],
        allow_multiselection=True,
    ),
    SimpleActionManifest(
        identifier="launch-houdini",
        label="Launch Houdini",
        category="application",
        order=100,
        icon={"type": "url", "url": "{addon_url}/public/icons/houdini.png"},

        entity_type="task",
        entity_subtypes=["FX", "Modeling"],
        allow_multiselection=True,
    ),
    SimpleActionManifest(
        identifier="launch-maya",
        label="Launch Maya",
        category="application",
        order=100,
        icon={"type": "url", "url": "{addon_url}/public/icons/maya.png"},

        entity_type="task",
        entity_subtypes=["FX", "Modeling", "Lighting", "Animation", "Rigging", "Lookdev"],
        allow_multiselection=False,
    )
]
