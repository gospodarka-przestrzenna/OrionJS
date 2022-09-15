# -*- coding: utf-8 -*-
###############################################################################

from os import path
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5 import uic
from .databmake import DatabMake
from .precalc import PreCal
from .variantmake import VariantMake
from .runner import Runner
#from .mds import MDS

class OrionJS(object):
    def __init__(self,iface):
        self.iface=iface
        self.plugin_path=path.dirname(path.abspath(__file__))
        self.plugin_menu_entry="&OrionJS"
        self.menu_actions=[]
        self.global_values={}
        #self.menu_actions_class=[]
        #adding actions
        #self.menu_actions_class.append(DatabMake)
        self.menu_actions.append(DatabMake(self))
        self.menu_actions.append(PreCal(self))
        self.menu_actions.append(VariantMake(self))
        self.menu_actions.append(Runner(self))
        


    def initGui(self):
        """
        Gui initialization and actions adding
        """
        for action in self.menu_actions:
            self.iface.addPluginToMenu(self.plugin_menu_entry,action)
            self.iface.addToolBarIcon(action)

    def unload(self):
        """
        Gui purge
        """
        for action in self.menu_actions:
            self.iface.removePluginMenu(self.plugin_menu_entry,action)
            self.iface.removeToolBarIcon(action)

    def ui_loader(self,*ui_name):
        """
        Returns object created based on provided .ui filename.
        In addition subdirectory can be stated:
        ui_loader('form.ui')
        ui_loader('formsdir','form.ui')
        """
        return uic.loadUi(path.join(self.plugin_path,*ui_name))

    def icon(self,name):
        icon_path=path.join(self.plugin_path,'images',name)
        return QIcon(icon_path)
