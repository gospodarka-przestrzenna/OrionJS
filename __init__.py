# coding=utf-8
"""
 This script initializes the plugin, making it known to QGIS.
"""


# pylint: disable=C0103
# noinspection PyPep8Naming
def classFactory(iface):
    """Load Plugin class.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    from .orionjs import OrionJS
    return OrionJS(iface)
# pylint: enable=C0103
