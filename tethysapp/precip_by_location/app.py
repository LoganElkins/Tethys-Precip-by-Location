from tethys_sdk.base import TethysAppBase, url_map_maker


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