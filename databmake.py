# -*- coding: utf-8 -*-
import os
from PyQt5.QtWidgets import QAction
from qgis.PyQt.QtWidgets import QProgressBar, QProgressDialog
from qgis.PyQt.QtCore import *
from qgis.gui import QgsMapLayerComboBox
from qgis.core import *#from .example_use import *
from qgis.utils import spatialite_connect
from .av import *
import time

class DatabMake(QAction):
    """
    Action for opening dock widget for database connections
    """
    def __init__(self,plugin):
        super(DatabMake,self).__init__(
			plugin.icon('databm.png'),
			"Datab_Make",
			plugin.iface.mainWindow()
	           )
        self.triggered.connect(self.run)
        self.plugin=plugin
        self.iface=plugin.iface
        # dailog cannot be set in function variable (it is GCed)
        self.dlg=None
        # binding frontend actions with logic

    def run(self):    

        #**JS.OR_Datatab_Make

        FID="ID"                        #Nr parametru, aktywnosci,
        FName="Name"                #Nazwa parametru, aktywnosci
        FSym="Symb"                 #Nazwa1 parametru
        FDec="Val_dec"            #Wartosc numeryczna (l.rzeczywista)
        FInt="Val_int"            #Wartosc numeryczna (l.calkowita)
        FTxt="Val_txt"            #Wartosc tekstowa
        FFile="File_Name"     #Nazwa zbioru aktywnosci

        #aPr=av.GetProject

        #aView=av.GetActiveDoc
        #LstTh=aView.GetThemes

        #*****Przestrzen robocza i prefix*****

        # PrN=av.GetProject.GetFileName 
        # FNWrkDir=PrN.ReturnDir 
        # #FNWrkDir=FileName.GetCWD 
        # #MsgBox.listasstring(AvList([FNWrkDir]),"","")
        # YesNo=MsgBox.YesNo ("Przestrzen robocza projektu:"+FNWrkDir.GetName+NL+"Aby kontynuowac wcisnij YES", "Projekt", TRUE)
        # if (YesNo==False) :
        #     return NIL 
        # end
        av.NewDatabase()
        if av.con == None:
            return
        # Pref=MsgBox.Input("Podaj prefix zbiorow","Projekt","DS1")
        Pref=''
        #*****Tablica parametrow*****
        #(######jesli nie tworzysz nowej tablicy, czytaj nr,na,nzz,nk######)
        YesNo=True
        aNewFlN="proj_lst"
        # class=dBASE
        #aNewFlN = FileDialog.Put(aNewFlN, "*.dbf", "Tabela Projektu")
        if (av.Exists (aNewFlN)) :
            YesNo=MsgBox.YesNo ("Tablica parametrow projektu:"+aNewFlN+"istnieje"+NL+"Czy chcesz utworzyc nowa tabele?", "Projekt", TRUE)
        end
        if ((YesNo==True) and (aNewFlN != nil)) :
            VTbPro=VTab.MakeNew (aNewFlN, 'class')
            #if (VTbPro.HasError) :
            #     if (VtbPro.HasLockError) :
            #             MsgBox.Error("Unable to acquire Write Lock for file " + aNewFlN.GetBaseName, "")
            #     else:
            #             MsgBox.Error("Unable to create " + aNewFlN.GetBaseName, "")
            #     end
            #     return nil
            # end
            fldID = Field.Make(FID, Field.DECIMAL, 3, 0)
            fldID.SetVisible( TRUE )
            VTbPro.AddFields(AvList([fldID]))
            
            fldName = Field.Make(FName, Field.CHAR, 25, 0)
            fldName.SetVisible( TRUE )
            VTbPro.AddFields(AvList([fldName]))

            fldSym = Field.Make(FSym, Field.CHAR, 6, 0)
            fldSym.SetVisible( TRUE )
            VTbPro.AddFields(AvList([fldSym]))

            fldI = Field.Make(FInt, Field.DECIMAL, 5, 0)
            fldI.SetVisible( TRUE )
            VTbPro.AddFields(AvList([fldI]))
            
            fldD = Field.Make(FDec, Field.DECIMAL, 15, 4)
            fldD.SetVisible( TRUE )
            VTbPro.AddFields(AvList([fldD]))

            fldT = Field.Make(FTxt, Field.CHAR, 25, 0)
            fldT.SetVisible( TRUE )
            VTbPro.AddFields(AvList([fldT]))

            TbPro = Table.Make(VTbPro)
            TbPro.SetName(VTbPro.GetName)

            labels =  AvList([ "Liczba rejonow", "Liczba aktywnosci", "Liczba aktywnosci niezd",
                                "Liczba kontaktow", "Wskaznik scinania (k.ter.)"])
            labels1 = AvList(["nr", "na", "nnz", "nk", "vc"])    
            defaults = AvList([ 3, 2, 1, 2, 0.9])    
                    
            LstPar=MsgBox.MultiInput ("Podaj parametry projektu", "Parametry", labels, defaults)
            n_r=LstPar.Get(0).AsNumber
            n_a=LstPar.Get(1).AsNumber
            n_nz=LstPar.Get(2).AsNumber
            n_k=LstPar.Get(3).AsNumber
            vc=LstPar.Get(4).AsNumber
            
            RecNP=VTbPro.AddRecord
            VTbPro.SetValue (fldID, RecNP, 0)
            VTbPro.SetValue (fldName, RecNP, "Prefix projektu")
            VTbPro.SetValue (fldSym, RecNP, "pref")
            VTbPro.SetValue (fldT, RecNP, Pref)    
            
            for i in AvIter(range(LstPar.Count)):
                RecNP=VTbPro.AddRecord
                VTbPro.SetValue (fldID, RecNP, RecNP)
                VTbPro.SetValue (fldName, RecNP, labels.Get(i))
                VTbPro.SetValue (fldSym, RecNP, labels1.Get(i))
                if (i<4) :
                    VTbPro.SetValue (fldI, RecNP, LstPar.Get(i).AsNumber)
                else:
                    VTbPro.SetValue (fldD, RecNP, LstPar.Get(i).AsNumber)
                end
            end

            labels = AvList([ "Koszt_K_Min", "Koszt_K_Max", "Koszt_F_Min",
                                "Koszt_F_Max", "Koszt_D_Min", "Koszt_D_Max"])
            labels1 = AvList(["kK_mn", "kK_mx", "kF_mn", "kF_mx", "kD_mn", "kD_mx"])    
            
            for i in AvIter(range(labels.Count)):
                RecNP=VTbPro.AddRecord
                VTbPro.SetValue (fldID, RecNP, RecNP)
                VTbPro.SetValue (fldName, RecNP, labels.Get(i))
                VTbPro.SetValue (fldSym, RecNP, labels1.Get(i))
            end

            VTbPro.SetEditable(False)
        else:
            Tb_Prj=av.FindDoc ("proj_lst")
            VTb_Prj=Tb_Prj.GetVtab
            fld=VTb_Prj.FindField("Val_Int")
            n_r=VTb_Prj.ReturnValue(fld,1)
            n_a=VTb_Prj.ReturnValue(fld,2)
            n_nz=VTb_Prj.ReturnValue(fld,3)
            n_k=VTb_Prj.ReturnValue(fld,4)
                
        end


        #*****Tablica Aktywnosci*****
        YesNo=True
        aNewFlN="akt_lst"
        # class=dBASE
        #aNewFlN = FileDialog.Put(aNewFlN, "*.dbf", "Tabela Projektu")
        if (av.Exists (aNewFlN)) :
            YesNo=MsgBox.YesNo ("Tablica aktywnosci:"+aNewFlN+"istnieje"+NL+"Czy chcesz utworzyc nowa tabele?", "Projekt", TRUE)
        end
        if ((YesNo==True) and (aNewFlN != nil)) :
            VTbAkt=VTab.MakeNew (aNewFlN, "class")
            # if (VTbAkt.HasError) :
            #     if (VtbAkt.HasLockError) :
            #             MsgBox.Error("Unable to acquire Write Lock for file " + aNewFlN.GetBaseName, "")
            #     else:
            #             MsgBox.Error("Unable to create " + aNewFlN.GetBaseName, "")
            #     end
            #     return nil
            # end
            
            fldID = Field.Make(FID, Field.DECIMAL, 3, 0)
            fldID.SetVisible( TRUE )
            VTbAkt.AddFields(AvList([fldID]))
            
            fldName = Field.Make(FName, Field.CHAR, 20, 0)
            fldName.SetVisible( TRUE )
            VTbAkt.AddFields(AvList([fldName]))

            fld = Field.Make("Movable", Field.BYTE , 2, 0)
            fld.SetVisible( TRUE )
            VTbAkt.AddFields(AvList([fld]))
            
            fld = Field.Make("Progr_User", Field.DECIMAL , 8, 0)
            fld.SetVisible( TRUE )
            VTbAkt.AddFields(AvList([fld]))
            
            fld = Field.Make("Progr_Cal", Field.DECIMAL , 8, 0)
            fld.SetVisible( TRUE )
            VTbAkt.AddFields(AvList([fld]))
            
            fld = Field.Make("Density", Field.DECIMAL , 6, 3)
            fld.SetVisible( TRUE )
            VTbAkt.AddFields(AvList([fld]))
            
        #    fldFil = Field.Make(FFile, Field.CHAR, 20, 0)
        #    fldFil.SetVisible( TRUE )
        #    VTbAkt.AddFields(AvList([fldFil]))
            
            fld = Field.Make("Mult_JK", Field.DECIMAL , 15, 10)
            fld.SetVisible( TRUE )
            VTbAkt.AddFields(AvList([fld]))
            
            fld = Field.Make("Mult_JF", Field.DECIMAL , 15, 10)
            fld.SetVisible( TRUE )
            VTbAkt.AddFields(AvList([fld]))

            fld = Field.Make("Mult_JD", Field.DECIMAL , 15, 10)
            fld.SetVisible( TRUE )
            VTbAkt.AddFields(AvList([fld]))

            TbAkt = Table.Make(VTbAkt)
            TbAkt.SetName(VTbAkt.GetName)
            
            for i in range(n_a):
                RecNA=VTbAkt.AddRecord
                VTbAkt.SetValue (fldID, RecNA, RecNA)
        #####        VTbAkt.SetValue (fldFil, RecNA, Pref+"_akt_"+RecNA.AsString+".dbf")
            end 
                
            VTbAkt.SetEditable(False)
        end
        #*****Tablica Rrejonow*****
        YesNo=True
        aNewFlN="rej"
        #class=dBASE
        #aNewFlN = FileDialog.Put(aNewFlN, "*.dbf", "Tabela Projektu")
        if (av.Exists (aNewFlN)) :
            YesNo=MsgBox.YesNo ("Tablica rejonow:"+aNewFlN+"istnieje"+NL+"Czy chcesz utworzyc nowa tabele?", "Projekt", TRUE)
        end
        if ((YesNo==True) and (aNewFlN != nil)) :
            VTbRej=VTab.MakeNew (aNewFlN, "class")
            # if (VTbRej.HasError) :
            #     if (VtbRej.HasLockError) :
            #             MsgBox.Error("Unable to acquire Write Lock for file " + aNewFlN.GetBaseName, "")
            #     else:
            #             MsgBox.Error("Unable to create " + aNewFlN.GetBaseName, "")
            #     end
            #     return nil
            # end
            
            fldID = Field.Make(FID, Field.DECIMAL, 3, 0)
            fldID.SetVisible( TRUE )
            VTbRej.AddFields(AvList([fldID]))
            
            fldName = Field.Make(FName, Field.CHAR, 20, 0)
            fldName.SetVisible( TRUE )
            VTbRej.AddFields(AvList([fldName]))

            fldCh = Field.Make("Cap", Field.DECIMAL, 8, 1)
            fldCh.SetVisible( TRUE )
            VTbRej.AddFields(AvList([fldCh]))
        
            fldArea = Field.Make("Area", Field.DECIMAL, 8, 0)
            fldArea.SetVisible( TRUE )
            VTbRej.AddFields(AvList([fldArea]))

            for i in AvIter(range(n_a)):
                #print(i,type(i.AsString)
                fld = Field.Make("Pred_"+i.AsString, Field.DECIMAL, 4, 2)
                fld.SetVisible( TRUE )
                VTbRej.AddFields(AvList([fld]))
            end
            
            for i in AvIter(range(n_a)):
                fld = Field.Make("Akt_"+i.AsString, Field.DECIMAL, 8, 1)
                fld.SetVisible( TRUE )
                VTbRej.AddFields(AvList([fld]))
            end

            TbRej = Table.Make(VTbRej)
            TbRej.SetName(VTbRej.GetName)
            
            for i in range(n_r):
                Rec=VTbRej.AddRecord
                VTbRej.SetValue (fldID, Rec, Rec)
            end 
                
            VTbRej.SetEditable(False)
        end

        #*****Tablica Kontaktow*****
        YesNo=True
        aNewFlN="kon_lst"
        # class=dBASE
        #aNewFlN = FileDialog.Put(aNewFlN, "*.dbf", "Tabela Projektu")
        if (av.Exists (aNewFlN)) :
            YesNo=MsgBox.YesNo ("Tablica kontaktow:"+aNewFlN+"istnieje"+NL+"Czy chcesz utworzyc nowa tabele?", "Projekt", TRUE)
        end
        if ((YesNo==True) and (aNewFlN != nil)) :
            VTbKon=VTab.MakeNew (aNewFlN, "class")
            # if (VTbKon.HasError) :
            #     if (VtbKon.HasLockError) :
            #             MsgBox.Error("Unable to acquire Write Lock for file " + aNewFlN.GetBaseName, "")
            #     else:
            #             MsgBox.Error("Unable to create " + aNewFlN.GetBaseName, "")
            #     end
            #     return nil
            # end
            VTbKon.SetEditable(True)
            
            fldID = Field.Make(FID, Field.DECIMAL, 3, 0)
            fldID.SetVisible( TRUE )
            VTbKon.AddFields(AvList([fldID]))
            
            fldName = Field.Make(FName, Field.CHAR, 25, 0)
            fldName.SetVisible( TRUE )
            VTbKon.AddFields(AvList([fldName]))

            fld = Field.Make("Selekt", Field.DECIMAL, 8, 6)
            fld.SetVisible( TRUE )
            VTbKon.AddFields(AvList([fld]))
        
            fld = Field.Make("Nasil", Field.DECIMAL, 8, 2)
            fld.SetVisible( TRUE )
            VTbKon.AddFields(AvList([fld]))

            fld = Field.Make("Kzk", Field.DECIMAL, 3, 0)
            fld.SetVisible( TRUE )
            VTbKon.AddFields(AvList([fld]))

            fld = Field.Make("Akt_Orig", Field.CHAR, 35, 0)
            fld.SetVisible( TRUE )
            VTbKon.AddFields(AvList([fld]))

            fld = Field.Make("Akt_Dest", Field.CHAR, 35, 0)
            fld.SetVisible( TRUE )
            VTbKon.AddFields(AvList([fld]))

            fld = Field.Make("Net_Nod_Tb", Field.CHAR, 30, 0)
            fld.SetVisible( TRUE )
            VTbKon.AddFields(AvList([fld]))
            
            fld = Field.Make("Zon_Tb", Field.CHAR, 30, 0)
            fld.SetVisible( TRUE )
            VTbKon.AddFields(AvList([fld]))
            
            fld = Field.Make("Zn_Dst_Fld", Field.CHAR, 10, 0)
            fld.SetVisible( TRUE )
            VTbKon.AddFields(AvList([fld]))
            
            fld = Field.Make("Zn_Cst_Fld", Field.CHAR, 10, 0)
            fld.SetVisible( TRUE )
            VTbKon.AddFields(AvList([fld]))
            
            TbKon = Table.Make(VTbKon)
            TbKon.SetName(VTbKon.GetName)
            
            for i in range(n_k):
                Rec=VTbKon.AddRecord
                VTbKon.SetValue (fldID, Rec, Rec)
            end 
                
            VTbKon.SetEditable(False)
        end


        #*****Tablica Kosztow i innych param*****
        YesNo=True
        aNewFlN="var_agr"
        #class=dBASE
        if (av.Exists (aNewFlN)) :
            YesNo=MsgBox.YesNo ("Tablica zmiennych zagregowanych:"+aNewFlN+"istnieje"+NL+"Czy chcesz utworzyc nowa tabele?", "Projekt", TRUE)
        end
        if ((YesNo==True) and (aNewFlN != nil)) :
            VTbVar=VTab.MakeNew (aNewFlN, "class")
            # if (VTbVar.HasError) :
            #     if (VTbVar.HasLockError) :
            #             MsgBox.Error("Unable to acquire Write Lock for file " + aNewFlN.GetBaseName, "")
            #     else:
            #             MsgBox.Error("Unable to create " + aNewFlN.GetBaseName, "")
            #     end
            #     return nil
            # end
            
            VTbVar.SetEditable(True)
            
            fldID = Field.Make(FID, Field.DECIMAL, 3, 0)
            fldID.SetVisible( TRUE )
            VTbVar.AddFields(AvList([fldID]))
            
            fldName = Field.Make(FName, Field.CHAR, 25, 0)
            fldName.SetVisible( TRUE )
            VTbVar.AddFields(AvList([fldName]))

            fldIter = Field.Make("Iter", Field.DECIMAL, 3, 0)
            fldIter.SetVisible( TRUE )
            VTbVar.AddFields(AvList([fldIter]))

            fld = Field.Make("Cost_K", Field.DECIMAL, 14, 1)
            fld.SetVisible( TRUE )
            VTbVar.AddFields(AvList([fld]))
        
            fld = Field.Make("Cost_F", Field.DECIMAL, 14, 1)
            fld.SetVisible( TRUE )
            VTbVar.AddFields(AvList([fld]))

            fld = Field.Make("Cost_D", Field.DECIMAL, 14, 1)
            fld.SetVisible( TRUE )
            VTbVar.AddFields(AvList([fld]))
            
            for k in AvIter(range(n_k)):
                fld = Field.Make("K_"+k.AsString+"_numb", Field.DECIMAL, 9, 1)
                fld.SetVisible( TRUE )
                VTbVar.AddFields(AvList([fld]))
                fld = Field.Make("K_"+k.AsString+"_cost", Field.DECIMAL, 14, 1)
                fld.SetVisible( TRUE )
                VTbVar.AddFields(AvList([fld]))
            end

            for a in AvIter(range(n_a)):
                fld = Field.Make("D_"+a.AsString+"_cost", Field.DECIMAL, 14, 1)
                fld.SetVisible( TRUE )
                VTbVar.AddFields(AvList([fld]))
            end

            for a in AvIter(range(n_a)):
                fld = Field.Make("T_"+a.AsString+"_reloc", Field.DECIMAL, 9, 1)
                fld.SetVisible( TRUE )
                VTbVar.AddFields(AvList([fld]))
            end

            TbVar = Table.Make(VTbVar)
            TbVar.SetName(VTbVar.GetName)

            VTbVar.SetEditable(False)
        end

        
        av.close()
        return
