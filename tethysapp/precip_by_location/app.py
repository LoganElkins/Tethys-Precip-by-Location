from tethys_sdk.base import TethysAppBase, url_map_maker
from tethys_sdk.app_settings import PersistentStoreDatabaseSetting


class PrecipByLocation(TethysAppBase):
    """
    Tethys app class for Precip By Location.
    """

    name = 'Precip By Location'
    index = 'precip_by_location:home'
    icon = 'precip_by_location/images/icon.gif'
    package = 'precip_by_location'
    root_url = 'precip-by-location'
    color = '#900F0F'
    description = ''
    tags = ''
    enable_feedback = False
    feedback_emails = []

    def url_maps(self):
        """
        Add controllers
        """
        UrlMap = url_map_maker(self.root_url)

        url_maps = (
            UrlMap(
                name='home',
                url='precip-by-location',
                controller='precip_by_location.controllers.home'
            ),
            UrlMap(
                name='graph_ajax',
                url='precip-by-location/graphs/{locID}/ajax',
                controller='precip_by_location.controllers.graph_ajax'
            ),
            UrlMap(
                name='graph',
                url='precip-by-location/graph',
                controller='precip_by_location.controllers.graph'
            )
        )

        return url_maps
    
    def persistent_store_settings(self):
        ps_settings = (
            PersistentStoreDatabaseSetting(
                name='primary_db',
                description='primary database',
                initializer='precip_by_location.model.initPrimaryDB',
                required=True
            ),
        )
        return ps_settings