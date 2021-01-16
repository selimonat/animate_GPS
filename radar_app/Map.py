"""
This is a class implementation of the modular code in build_static_table.
I am taking from there to here all the code that can nicely make plots of maps and 
plot on it raw and streaming data.
"""

import folium
import logging


class Map:
    def __init__(self, lat, lon, zoom_start):
        """
            Pass a SurgeStreaming instance that contains data for a specific set of parameters.
        """
        logging.info('Creating Map object.')
        # set the center of the map
        self.map = folium.Map(location=(lat, lon), zoom_start=zoom_start, tiles="cartodbpositron")

    def add_dot_to_map(self, lat, lon, color="black", radius=3, opacity=0.5, line_weight=1):
        """
            Draws circles to self.map using at lat/lon coordinates present in DF. Column names are assumed to be
            lat/lon.

            Pass TOOLTIP_COLUMN argument to be shown as tooltip information on mouse hover. If this is not provided
            latitude information will be shown.

            :df: DataFrame with lat lon columns
            :tooltip_column: name of column to be shown as tooltips.

        """

        folium.CircleMarker(
            location=(lat, lon),
            radius=radius,
            weight=line_weight,
            fill_color=color,
            color=color,
            tooltip=f"{lat}-{lon}",
            opacity=opacity,
        ).add_to(self.map)