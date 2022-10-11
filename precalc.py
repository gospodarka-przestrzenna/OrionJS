# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QAction,QMessageBox,QApplication,QInputDialog,QFileDialog
from PyQt5.QtCore import Qt, QBasicTimer
from qgis.gui import QgsMapLayerComboBox
from qgis.core import *#from .example_use import *
from qgis.utils import spatialite_connect
from .av import *
import os
class PreCal(QAction):
    """
    Action for opening dock widget for database connections
    """
    def __init__(self,plugin):
        super(PreCal,self).__init__(
			plugin.icon("precal.png"),
			"Pre_Calc",
			plugin.iface.mainWindow()
	           )
        self.triggered.connect(self.run)
        self.plugin=plugin
        self.iface=plugin.iface
        # dailog cannot be set in function variable (it is GCed)
        self.dlg=None
        # binding frontend actions with logic

    def run(self):

        av.GetDatabase()
        if av.con == None:
            return
        # początek po MsG
        Tb_Prj=av.FindDoc("proj_lst")
        _VTb_Prj=Tb_Prj.GetVtab
        fldI=_VTb_Prj.FindField("Val_int")
        fldT=_VTb_Prj.FindField("Val_txt")
        fldD=_VTb_Prj.FindField("Val_dec")

        _Pref=_VTb_Prj.ReturnValue(fldT,0)
        _nr=_VTb_Prj.ReturnValue(fldI,1)
        _na=_VTb_Prj.ReturnValue(fldI,2)
        _nnz=_VTb_Prj.ReturnValue(fldI,3)
        _nk=_VTb_Prj.ReturnValue(fldI,4)
        _vc=_VTb_Prj.ReturnValue(fldD,5)


        Tb_LAkt=av.FindDoc("akt_lst")
        VTb_LAkt=Tb_LAkt.GetVtab
        fldPU=VTb_LAkt.FindField("Progr_User")
        fldPC=VTb_LAkt.FindField("Progr_Cal")
        VTb_LAkt.SetEditable(TRUE)

        #*****kontrola rozkladu akt
        Tb_Rej=av.FindDoc ("rej")
        VTb_Rej=Tb_Rej.GetVtab

        for i in AvIter(range(_na)):
            fldV=VTb_Rej.FindField("Akt_"+i.AsString)
            Sum=0
            for rec in VTb_Rej:
                Sum=Sum+VTb_Rej.ReturnValue(fldV,rec)
            end
            VTb_LAkt.SetValue(fldPC,i,Sum)
            Val=VTb_LAkt.ReturnValue(fldPU,i)
            if (Sum!=Val) :
                MsgBox.Warning("Program aktywnosci"+i.AsString+"="+Val.AsString
                    +NL+"Suma rozmieszczen aktywnosci"+i.AsString+"="+Sum.AsString ,"Uwaga")
            end 
        end
        VTb_LAkt.SetEditable(FALSE)

        #*****regulatory*********
        MsgBox.Info("Obliczanie Stalych regulatorow kontaktow","Pre Calculation")

        Tb_LAkt=av.FindDoc ("akt_lst")
        VTb_LAkt=Tb_LAkt.GetVtab
        fldMV=VTb_LAkt.FindField("Movable")
        fldPC=VTb_LAkt.FindField("Progr_Cal")
        fldDs=VTb_LAkt.FindField("Density")

        _Lst_nz=AvList([])
        _Lst_nzn=AvList([])
        _Lst_z=AvList([])
        _lst_pos_anz=AvList([])

        for i in AvIter(range(_na)):
            j=VTb_LAkt.ReturnValue(fldMV,i)
            if(j==1) :
                _Lst_nzn.Add(i)
                _Lst_nz.Add(i.AsString)
            else:
                _Lst_z.Add(i.AsString)
            end
        end

        for a in AvIter(range(_na)):
            _lst_pos_anz.Add(NIL)
        end
        for i in AvIter(range(_Lst_nzn.Count)):
            _lst_pos_anz.Set(_Lst_nzn.Get(i),i)
        end

        LstMV=AvList([])
        LstPC=AvList([])
        for a in VTb_LAkt:
            LstMV.Add(VTb_LAkt.ReturnValue(fldMV,a))
            LstPC.Add(VTb_LAkt.ReturnValue(fldPC,a))
        end

        Tb_LKon=av.FindDoc("kon_lst")
        VTb_LKon=Tb_LKon.GetVtab
        fldNS=VTb_LKon.FindField("Nasil")
        fldAO=VTb_LKon.FindField("Akt_Orig")
        fldAD=VTb_LKon.FindField("Akt_Dest")

        #=======koszy kontaktow========
        LstNS=AvList([])
        LstAO=AvList([])
        LstAD=AvList([])
        for k in AvIter(range(_nk)):
            LstNS.Add(VTb_LKon.ReturnValue(fldNS,k)) 
            
            Lst=VTb_LKon.ReturnValue(fldAO,k).AsList
            for i in AvIter(range(Lst.Count)):
                Lst.Set(i,Lst.Get(i).AsNumber)
            end
            LstAO.Add(Lst)
        #    MsgBox.ListAsString(LstAO.Get(k),"","")
            Lst=VTb_LKon.ReturnValue(fldAD,k).AsList
            for i in AvIter(range(Lst.Count)):
                Lst.Set(i,Lst.Get(i).AsNumber)
            end
            LstAD.Add(Lst)
        end
        SUMK=0                                         ######Suma wszystkich glosow wyslanych ze wszystkich zrodel
        for k in AvIter(range(_nk)):
            for aa in LstAO.Get(k):
                SUMK=SUMK+(LstPC.Get(aa)*LstNS.Get(k)) 
            end
        end
        #MsgBox.Info(SUMK.AsString,"Suma Kont")
        LstGK=AvList([])
        for a in AvIter(range(_na)):
            GKZ=0                                        ######Suma nasilen wszystkich kontaktow aktywn zrodlowej a 
            for k in AvIter(range(_nk)):
                if (LstAO.Get(k).FindByValue (a) > -1) :
                    GKZ=GKZ+LstNS.Get(k)
                end
            end
            ###########MsgBox.Info(GKZ.AsString,"GKZ")

            GKC=0                                         ######????? Suma wszystkich kontaktow wyslanych ze zrodel 
            for k in AvIter(range(_nk)):
                if (LstAD.Get(k).FindByValue (a) > -1) :
                    V1=0                                    ###### Suma glosow wyslanych w kontakcie k gdzie a - jest aktywn celowa
                    for aa in (LstAO.Get(k)):
                        V1=V1+(LstPC.Get(aa)*LstNS.Get(k))
                    end
                    SumCel=0                            ###### Suma celow w kontakcie k gdzie a - jest aktywn celowa
                    for aa in LstAD.Get(k):
                        SumCel=SumCel+LstPC.Get(aa)
                    end
                    GKC=GKC+(V1/SumCel)     ###### Suma glosow na jednostke aktywn a jako cel we wszystkich kontaktach
                end
            end
        #    MsgBox.Info(GKZ.AsString+"     "+GKC.AsString,a.AsString+"    GKZ, GKC")
            LstGK.Add((GKZ+GKC)/(2*SUMK))
        end
        ###########MsgBox.ListAsString(LstGK,"GK_0","")

        V1=0

        for a in AvIter(range(_na)):
            V1=V1+ (LstPC.Get(a)*LstGK.Get(a)) 
        end
        for a in AvIter(range(_na)):
            LstGK.Set(a,LstGK.Get(a)*3/V1)
        end
        lst=AvList([])
        for a in _Lst_nzn:
            lst.Add(LstGK.Get(a))
        end
        LstGK=lst
        ###########MsgBox.ListAsString(LstGK,"GK","")

        #=======koszy predyspozycji========

        fldC=VTb_Rej.FindField("Cap")
        lstGD=AvList([])
        lst_PC=AvList([])
        for a in _Lst_nzn:
            K_mx=0
            K_mn=0
            A_V=VTb_LAkt.ReturnValue(fldPC,a)
            lst_PC.Add(A_V)
            Ac=A_V
            Ds=VTb_LAkt.ReturnValue(fldDs,a)
            
            fldP=VTb_Rej.FindField("Pred_"+a.AsString)
            lstP=AvList([])
            lstC=AvList([])
            for rec in VTb_Rej:
                lstP.Add(VTb_Rej.ReturnValue(fldP,rec))
                lstC.Add(VTb_Rej.ReturnValue(fldC,rec))
            end
            LstDiv=lstP.Clone
            LstDiv.RemoveDuplicates
            LstDiv.Sort (True)
            
            for d in LstDiv:
                SuC=0
                for r in AvIter(range(_nr)):
                    if (lstP.Get(r)==d) :
                        SuC=SuC+ lstC.Get(r) 
                    end
                end
                Su=SuC*Ds
                if (Su<Ac) :
                    K_mx=K_mx+(Su*(5-d))
                    Ac=Ac-Su
                else:
                    K_mx=K_mx+(Ac*(5-d))
                    break
                end
            end
            Ac=A_V
            LstDiv.Sort (False)
            for d in LstDiv:
                SuC=0
                for r in AvIter(range(_nr)):
                    if (lstP.Get(r)==d) :
                        SuC=SuC+ lstC.Get(r) 
                    end
                end
                Su=SuC*Ds
                if (Su<Ac) :
                    K_mn=K_mn+(Su*(5-d))
                    Ac=Ac-Su
                else:
                    K_mn=K_mn+(Ac*(5-d))
                    break
                end
            end
            lstGD.Add((K_mx-K_mn)/A_V)
        end
        ##########MsgBox.ListAsString(lstGD,"GD_0","")

        Su=0
        for i in AvIter(range(_nnz)):
            Su=Su + (lst_PC.Get(i)*lstGD.Get(i))
        end
        for i in AvIter(range(_nnz)):
            lstGD.Set(i, lstGD.Get(i)/Su)
        end
        ##########MsgBox.ListAsString(lstGD,"GD","")


        #=======koszy konfliktow========
        lstGF=AvList([])
        for i in AvIter(range(_nnz)):
            lstGF.Add(0)
        end

        #=======regulatory========
        lst_fld=AvList([VTb_LAkt.FindField("Mult_JK"),VTb_LAkt.FindField("Mult_JF"),VTb_LAkt.FindField("Mult_JD")])
        VTb_LAkt.SetEditable(TRUE)

        a=0
        for aa in _Lst_nzn:
            lstJ=AvList([LstGK.Get(a),lstGF.Get(a),lstGD.Get(a)])
            lst=lstJ.Clone
            lst.Sort(False)
            mx=lst.Get(0)
            for i in [0,1,2]:
                VTb_LAkt.SetValue(lst_fld.Get(i),aa,lstJ.Get(i)/mx)
                lstJ.Set(i,lstJ.Get(i)/mx)
            end
        ############MsgBox.ListAsString(lstJ,"J","")
            a=a+1
        end

        VTb_LAkt.SetEditable(FALSE)
        
        av.close()
        return



