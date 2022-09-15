# -*- coding: utf-8 -*-
import os
from PyQt5.QtWidgets import QAction,QMessageBox,QApplication,QInputDialog,QFileDialog
from PyQt5.QtCore import Qt, QBasicTimer
from qgis.gui import QgsMapLayerComboBox
from qgis.core import *#from .example_use import *
from qgis.utils import spatialite_connect
from .av import *
class VariantMake(QAction):
    """
    Action for opening dock widget for database connections
    """
    def __init__(self,plugin):
        super(VariantMake,self).__init__(
			plugin.icon('variant.png'),
			"Variant_Make",
			plugin.iface.mainWindow()
	           )
        self.triggered.connect(self.run)
        self.plugin=plugin
        self.iface=plugin.iface
        # dailog cannot be set in function variable (it is GCed)
        self.dlg=None
        # binding frontend actions with logic

    def run(self):
        #**JS.OR_Variant_Make

        # Lst=av.GetProject.GetDocs 
        # LstTb=AvList([])
        # Pat = "*_proj_lst.dbf".AsPattern
        # for aObj in Lst:
        #     if ((aObj.GetClass.GetClassName=="Table") and (aObj.GetName==Pat)) :
        #         LstTb.Add(aObj)
        #     end
        # end
        # Tb_Prj=MsgBox.ListAsString(LstTb,"Wybierz tablice projektu","Projekt ORION")
        av.GetDatabase()

        #if (Tb_Prj == NIL):
        #    return NIL 
        #end
        Tb_Prj=av.FindDoc("proj_lst")
        VTb_Prj=Tb_Prj.GetVtab
        fldID=VTb_Prj.FindField("ID")
        fldN=VTb_Prj.FindField("Name")
        fldS=VTb_Prj.FindField("Symb")
        fldI=VTb_Prj.FindField("Val_int")
        fldT=VTb_Prj.FindField("Val_txt")


        Pref=VTb_Prj.ReturnValue(fldT,0)
        n_r=VTb_Prj.ReturnValue(fldI,1)
        n_a=VTb_Prj.ReturnValue(fldI,2)
        n_nz=VTb_Prj.ReturnValue(fldI,3)
        n_k=VTb_Prj.ReturnValue(fldI,4)


        labels = AvList(["Prefiks variantu", "wskaznik K", "wskaznik F", "wskaznik D"])    
        labels1=AvList(["","K","F","D"])
        defaults = AvList(["A", 0.0, 0.0, 0.0])
        lst_var = MsgBox.MultiInput( "Ustaw prefiks wariantu i wskazniki procedur (<0..1>)", "Wasriant", labels, defaults )

        for i in range(1,(3)+1):
            if (lst_var.Get(i).IsNotNumber) :
                MsgBox.Error(labels.Get(i)+"podano nieprawidlowo -  "+lst_var.Get(i),"Parameters Error")
            end 
        end

        str0=lst_var.Get(0)
        #str=str.Trim
        str1=str0
        KFD=AvList([])
        for i in range(1,(3)+1):
            p=lst_var.Get(i).AsNumber
            
            #if (str.Count>0) :
                #str=str+"  "
                #str1=str1+"_"
            #end
            #str=str+labels1.Get(i)+"="+lst_var.Get(i)
            #str1=str1+labels1.Get(i)    +("00"+(p*100).AsString).Right(3)
            str0=str0+" "+labels1.Get(i)+"="+lst_var.Get(i).AsString
            str1=str1+"_"+labels1.Get(i)  +"%03d"%(p*100)  # ("00"+(p*100).AsString).Right(3)
            KFD.Add(p)
        end
        VTb_Prj.SetEditable(True)
        rec=VTb_Prj.AddRecord
        VTb_Prj.SetValue(fldID,rec,rec)
        VTb_Prj.SetValue(fldS,rec,"V")
        VTb_Prj.SetValue(fldN,rec,str0)
        VTb_Prj.SetValue(fldT,rec,str1)
        #VTb_Prj.SetEditable(False)


        Tb_LAkt=av.FindDoc ("akt_lst")
        VTb_LAkt=Tb_LAkt.GetVtab
        fldMv=VTb_LAkt.FindField("Movable")
        fldDs=VTb_LAkt.FindField("Density")
        #VTb_LAkt.SetEditable(TRUE)

        Lst_nz=AvList([])
        for i in AvIter(range(n_a)):
            j=VTb_LAkt.ReturnValue(fldMv,i)
            if(j==1) :
                Lst_nz.Add(i)
            end
        end

        Tb_Rej=av.FindDoc ("rej")
        VTb_Rej=Tb_Rej.GetVtab

        #PrN=av.GetProject.GetFileName 
        #FNWrkDir=PrN.ReturnDir 
        #class=dBASE


        #=====tablice Akt========
        for a in Lst_nz:
            aNewFlN=str1+"_Akt_"+a.AsString
            VTb=VTab.MakeNew (aNewFlN, 'class')
            # if (VTb.HasError) :
            #     if (Vtb.HasLockError) :
            #             MsgBox.Error("Unable to acquire Write Lock for file " + aNewFlN.GetBaseName, "")
            #     else:
            #             MsgBox.Error("Unable to create " + aNewFlN.GetBaseName, "")
            #     end
            #     return nil
            # end
            fldID = Field.Make("ID", Field.DECIMAL, 3, 0)
            fldID.SetVisible( TRUE )
            VTb.AddFields(AvList([fldID]))
            
            fldIter = Field.Make("Iter_0", Field.DECIMAL, 10, 1)
            fldIter.SetVisible( TRUE )
            VTb.AddFields(AvList([fldIter]))
            VTb.SetEditable(True)

            Tb = Table.Make(VTb)
            Tb.SetName(VTb.GetName)

            fldA=VTb_Rej.FindField("Akt_"+a.AsString)
            for rec in VTb_Rej:
                recA=VTb.AddRecord
                VTb.SetValue(fldID,recA,recA)
                VTb.SetValue(fldIter,recA,VTb_Rej.ReturnValue(fldA,rec))
            end
            
            VTb.SetEditable(False)
            
        end
        #=====tablice Akt_Sc========
        for a in Lst_nz:
            aNewFlN=str1+"_Akt_Sc_"+a.AsString
            VTb=VTab.MakeNew (aNewFlN, "class")
            # if (VTb.HasError) :
            #     if (Vtb.HasLockError) :
            #             MsgBox.Error("Unable to acquire Write Lock for file " + aNewFlN.GetBaseName, ""):
            #     else:
            #             MsgBox.Error("Unable to create " + aNewFlN.GetBaseName, "")
            #     end
            #     return nil
            # end
            fldID = Field.Make("ID", Field.DECIMAL, 3, 0)
            fldID.SetVisible( TRUE )
            VTb.AddFields(AvList([fldID]))
            
            fldIter = Field.Make("Iter_1", Field.DECIMAL, 10, 1)
            fldIter.SetVisible( TRUE )
            VTb.AddFields(AvList([fldIter]))
            VTb.SetEditable(True)

            Tb = Table.Make(VTb)
            Tb.SetName(VTb.GetName)
            for r in AvIter(range(n_r)):
                recA=VTb.AddRecord
                VTb.SetValue(fldID,recA,recA)
            end
            VTb.SetEditable(False)
        end


        #=====tablice UK========
        if (lst_var.Get(1).AsNumber>0) :
            for a in Lst_nz:
                aNewFlN=str1+"_UK_"+a.AsString
                VTb=VTab.MakeNew (aNewFlN, "class")
                # if (VTb.HasError) :
                #     if (Vtb.HasLockError) :
                #             MsgBox.Error("Unable to acquire Write Lock for file " + aNewFlN.GetBaseName, ""):
                #     else:
                #             MsgBox.Error("Unable to create " + aNewFlN.GetBaseName, "")
                #     end
                #     return nil
                # end
                fldID = Field.Make("ID", Field.DECIMAL, 3, 0)
                fldID.SetVisible( TRUE )
                VTb.AddFields(AvList([fldID]))
                
                fldIter = Field.Make("Iter_1", Field.DECIMAL, 6, 3)
                fldIter.SetVisible( TRUE )
                VTb.AddFields(AvList([fldIter]))
                VTb.SetEditable(True)
            
                Tb = Table.Make(VTb)
                Tb.SetName(VTb.GetName)
                for r in AvIter(range(n_r)):
                    recA=VTb.AddRecord
                    VTb.SetValue(fldID,recA,recA)
                end
                VTb.SetEditable(False)
            end
        end
        #=====tablice UD========
        if (lst_var.Get(3).AsNumber>0) :
            for a in Lst_nz:
                aNewFlN=str1+"_UD_"+a.AsString
                VTb=VTab.MakeNew (aNewFlN, 'class')
                # if (VTb.HasError) :
                #     if (Vtb.HasLockError) :
                #             MsgBox.Error("Unable to acquire Write Lock for file " + aNewFlN.GetBaseName, ""):
                #     else:
                #             MsgBox.Error("Unable to create " + aNewFlN.GetBaseName, "")
                #     end
                #     return nil
                # end
                fldID = Field.Make("ID", Field.DECIMAL, 3, 0)
                fldID.SetVisible( TRUE )
                VTb.AddFields(AvList([fldID]))
                
                fldIter = Field.Make("Iter_1", Field.DECIMAL, 6, 3)
                fldIter.SetVisible( TRUE )
                VTb.AddFields(AvList([fldIter]))
                VTb.SetEditable(True)
            
                Tb = Table.Make(VTb)
                Tb.SetName(VTb.GetName)
                for r in AvIter(range(n_r)):
                    recA=VTb.AddRecord
                    VTb.SetValue(fldID,recA,recA)
                end
            
                VTb.SetEditable(False)
            end
        end

        av.close()
        return
