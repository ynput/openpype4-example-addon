from typing import Type

from ayon_server.actions import (
    ActionExecutor,
    ExecuteResponseModel,
    SimpleActionManifest,
)
from ayon_server.addons import BaseServerAddon
from ayon_server.api.dependencies import CurrentUser, ProjectName
from ayon_server.entities import FolderEntity
from ayon_server.events import EventModel, EventStream
from ayon_server.exceptions import NotFoundException
from ayon_server.lib.postgres import Postgres
from nxtools import logging

from .actions import EXAMPLE_SIMPLE_ACTIONS
from .settings import ExampleSettings
from .site_settings import ExampleSiteSettings


class ExampleAddon(BaseServerAddon):
    settings_model: Type[ExampleSettings] = ExampleSettings
    site_settings_model: Type[ExampleSiteSettings] = ExampleSiteSettings

    # frontend_scopes defines, where the web frontend of the addon
    # should be displayed in openpype web app. Currently only "project"
    # is supported. Additional arguments may be passed (in this case)
    # to show the project hierarchy sidebar. This feature is not yet
    # fully functional and will be changed in the future.

    frontend_scopes: dict[str, dict[str, str]] = {"project": {"sidebar": "hierarchy"}}
    addon_type = "server"

    # intitalize method is called during the addon initialization
    # You can use it to register its custom REST endpoints

    def initialize(self):
        logging.info("Example addon INIT")
        self.add_endpoint(
            "get-random-folder/{project_name}",
            self.get_random_folder,
            method="GET",
        )

        EventStream.subscribe("entity.task.status_changed", self.on_task_status_changed)

    async def setup(self):
        pass

        # If the addon makes a change in server configuration,
        # e.g. adding a new attribute, you may trigger a server
        # restart by calling self.restart_server()
        # Use it with caution and only when necessary!
        # You don't want to restart the server every time the addon is loaded.

        # self.request_server_restart()

    # Example REST endpoint
    # Depends(dep_current_user) ensures the request is authenticated

    async def get_random_folder(
        self,
        user: CurrentUser,
        project_name: ProjectName,
    ):
        """Return a random folder from the database"""

        settings = await self.get_project_settings(project_name)
        assert settings is not None  # Keep mypy happy

        # Get a random folder id from the project
        try:
            result = await Postgres.fetch(
                f"""
                SELECT id FROM project_{project_name}.folders
                WHERE folder_type = $1
                ORDER BY RANDOM() LIMIT 1
                """,
                settings.folder_type,
            )
        except Postgres.UndefinedTableError:
            raise NotFoundException(f"Project {project_name} not found")

        try:
            folder_id = result[0]["id"]
        except IndexError:
            raise NotFoundException("No folder found")

        # Load the folder entity

        folder = await FolderEntity.load(project_name, folder_id)

        # ensure_read_access method raises ForbiddenException, when the user
        # does not have rights to view the folder.

        await folder.ensure_read_access(user)

        # FolderEntity.as_user returns the folder (similarly to folder.payload)
        # but it respects the user access level (so it may hide certain attributes)
        return folder.as_user(user)

    #
    # Event handlers
    #

    async def get_cached_setting(self) -> str:
        """
        We use this setting in a event handler so it is a good idea
        to cache it for better performance.
        """
        if not hasattr(self, "_cached_setting") or self._cached_setting is None:
            studio_settings = await self.get_studio_settings()
            self._cached_setting = studio_settings.grouped_settings.favorite_color
        return self._cached_setting

    async def on_settings_changed(
        self,
        old_settings: ExampleSettings,
        new_settings: ExampleSettings,
        **kwargs,
    ) -> None:
        """
        This method is called when the settings are changed.
        We update the cached setting here.
        """
        new_favorite_color = new_settings.grouped_settings.favorite_color
        logging.debug(
            f"Example addon settings changed. New favorite color is {new_favorite_color}"
        )
        self._cached_setting = new_favorite_color

    async def on_task_status_changed(self, event: EventModel):
        favorite_color = await self.get_cached_setting()
        logging.debug(f"Example addon says, that {event.description}")
        logging.debug(f"Admin's favorite color is {favorite_color}")

    #
    # Browser actions
    #

    async def get_simple_actions(
        self,
        project_name: str | None = None,
        variant: str = "production",
    ) -> list[SimpleActionManifest]:
        """Return a list of simple actions provided by the addon"""
        return EXAMPLE_SIMPLE_ACTIONS

    async def execute_action(
        self,
        executor: ActionExecutor,
    ) -> ExecuteResponseModel:
        """Execute an action provided by the addon"""

        if executor.identifier == "example-folder-action":
            context = executor.context
            folder_id = context.entity_ids[0]

            f = await FolderEntity.load(context.project_name, folder_id)
            return await executor.get_server_action_response(
                message=f"Action performed on {f.name}"
            )

        elif executor.identifier == "example-task-action":
            return await executor.get_launcher_action_response(args=["blabla"])

        raise ValueError(f"Unknown action: {executor.identifier}")
