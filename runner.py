# -*- coding: utf-8 -*-
import math
from PyQt5.QtWidgets import QAction,QMessageBox,QApplication,QInputDialog,QFileDialog
from PyQt5.QtCore import Qt, QBasicTimer
from qgis.gui import QgsMapLayerComboBox
from qgis.core import *#from .example_use import *
from qgis.utils import spatialite_connect
from .av import *
class Runner(QAction):
    """
    Action for opening dock widget for database connections
    """
    def __init__(self,plugin):
        super(Runner,self).__init__(
			plugin.icon('runner.png'),
			"Variant_Make",
			plugin.iface.mainWindow()
	           )
        self.triggered.connect(self.run)
        self.plugin=plugin
        self.iface=plugin.iface
        # dailog cannot be set in function variable (it is GCed)
        self.dlg=None
        # binding frontend actions with logic

    def JS_OR_Kont(self):
        #**JS.OR_Kont
        #
        Tb_Kon=av.FindDoc ("kon_lst")

        VTb_Kon=Tb_Kon.GetVtab
        fldKNodT=VTb_Kon.FindField("Net_Nod_Tb")
        fldKZonT=VTb_Kon.FindField("Zon_Tb")
        fldKZnDst=VTb_Kon.FindField("Zn_Dst_Fld")
        fldKZnCost=VTb_Kon.FindField("Zn_Cst_Fld")

        #--------------------------------------    

        lstVVK=AvList([])
        lstUK=AvList([])


        lst=AvList([])
        for i in AvIter(range(self._Lst_nzn.Count)):
            lst.Add(0)
        end

        for r in AvIter(range(self._nr)):
            lstVVK.Add(lst.DeepClone )
            lstUK.Add(lst.DeepClone )
        end
        #for r in AvIter(range(self._nr)):
        #    MsgBox.ListAsString(lstVVK.Get(r),"","")
        #    MsgBox.ListAsString(self._lstVA.Get(r),"","")
        #end

        #eul=Number.GetEuler # EXP będziemy generować inaczej
        CostK=0
        #************* begin cal

        for k in AvIter(range(self._nk)):
            #MsgBox.Info("Nr_Kontaktu" +k.AsString,"")

            COSTK1=0
            SUMK1=0
            Sel=-(VTb_Kon.ReturnValue(VTb_Kon.FindField("Selekt"),k))
            Nas=VTb_Kon.ReturnValue(VTb_Kon.FindField("Nasil"),k)
            Kzk=VTb_Kon.ReturnValue(VTb_Kon.FindField("Kzk"),k)

        #---------------
            VTb_Nod=av.FindDoc (VTb_Kon.ReturnValue(fldKNodT,k)).GetVtab
            fldLoc=VTb_Nod.FindField("loc_Id")
            lst=AvList([])
            for rec in VTb_Nod:
                lst.Add(VTb_Nod.ReturnValue(fldLoc,rec))
            end
            lstRPos=AvList([])
            for i in AvIter(range(self._nr)):
                pos=lst.FindByValue(i)
                if (pos>= 0) :
                    lstRPos.Add(pos)
                else:
                    MsgBox.Error("Numeracja rejonow i wezlow potencjalowych sa niezgodne"+ i.AsString,"Kontakty")
                    return NIL
                end
            end
            lst=VTb_Nod.GetFields
            Pat=av.AsPattern("Strefa_*")
            Lst_Strf=AvList([])
            for fld in lst:
                if (fld.GetName==Pat) :
                    Lst_Strf.Add(fld)
                end
            end
            VTb_Zon=av.FindDoc (VTb_Kon.ReturnValue(fldKZonT,k)).GetVtab
            fld_Zon=VTb_Zon.FindField(VTb_Kon.ReturnValue(fldKZnDst,k))
            fld_Cost=VTb_Zon.FindField(VTb_Kon.ReturnValue(fldKZnCost,k))
            lstZon=AvList([])
            lstCost=AvList([])
            for rec in VTb_Zon:
                i=VTb_Zon.ReturnValue(fld_Zon,rec)
                if (i>0) :
                    lstZon.Add(i)
                end
                j=VTb_Zon.ReturnValue(fld_Cost,rec)
                if (j>0) :
                    lstCost.Add(j)
                end
            end
            lstZon.RemoveDuplicates
            lstZon.Sort(TRUE)
            lstCost.RemoveDuplicates
            lstCost.Sort(TRUE)

        #-------------------
            KZon= -1
            for j in lstZon:
                if (j>=Kzk) :
                    break
                end
                KZon=KZon+1
                
            end

            lst_ors=VTb_Kon.ReturnValue(VTb_Kon.FindField("akt_orig"),k).AsList
            lst_orn=AvList([])
            for i in lst_ors:
                lst_orn.Add(i.AsNumber)
            end

            lst_dss=VTb_Kon.ReturnValue(VTb_Kon.FindField("akt_dest"),k).AsList
            lst_dsn=AvList([])
            for i in lst_dss:
                lst_dsn.Add(i.AsNumber)
            end
            
            lst_ds_nz=AvList([])
            for a in lst_dsn:
                if (self._Lst_nzn.FindByValue(a) > -1) :
                    lst_ds_nz.Add(a)
                end
            end
        #-----------------------------------------
            for r in AvIter(range(self._nr)):
                Pr=1
                SumP=0
                VOr=0
                for a in lst_orn:
                    ######## tu mozna zmienic Nas na indywidualny
                    VOr=VOr+(Nas*self._lstVA.Get(r).Get(a))
                end
                if (VOr>0) :
                    for strf in AvIter(range(0,(KZon)+1)):
                        lstDStrf=VTb_Nod.ReturnValue(Lst_Strf.Get(strf),lstRPos.Get(r)).AsList
                        #######MsgBox.Info(strf.AsString,"strefa")
                        if (lstDStrf.Count>0) :
                            for i in AvIter(range(lstDStrf.Count)):
                                lstDStrf.Set(i,lstDStrf.Get(i).AsNumber)
                            end
                            SumS=0     #**** suma celow w strefie
                            for rr in lstDStrf:
                                for aa in lst_dsn:
                                    SumS=SumS+self._lstVA.Get(rr).Get(aa)
                                end
                            end
                            if (SumS>0) :
                                #PrC=eul^(Sel*(SumP+SumS))
                                PrC=math.exp(Sel*(SumP+SumS))
                                #MsgBox.Info((SumP+SumS).AsString+PrC.AsString+strf.AsString,k.AsString+r.AsString)
                                PrS=Pr-PrC
                                Vot=VOr*PrS         #Glos do strefy
                                COSTK1=COSTK1+(Vot*lstCost.Get(strf))
                                SUMK1=SUMK1+Vot
                                CostK=CostK+(Vot*lstCost.Get(strf)) #Sumowanie kosztow kontaktow
                                #MsgBox.Info(Nas.AsString+PrS.AsString+Vot.AsString,"")
                                for rr in lstDStrf:
                                    
                                    for aa in lst_ds_nz:
                                        posA=self._lst_pos_anz.Get(aa)
                                        lstVVK.Get(rr).Set(posA, lstVVK.Get(rr).Get(posA) + (Vot*self._lstVA.Get(rr).Get(aa)/SumS))
                                    end
                                    
                                end
                                SumP=SumP+SumS
                                Pr=PrC
                            end #SumS>0
                        end #lstDStr.Count>0
                    end #str
                
                end #VOr>0
            end #rej origin
        #--------------------------------------
        ################MSGBOX.INFO(k.AsString+SUMK1.AsString+COSTK1.ASString,"")
        ################MSGBOX.Input ("kont:"+k.AsString, "", SUMK1.AsString+"     "+COSTK1.ASString)
        self._VTb_Var.SetValue( self._lst_fKn.Get(k),    self._VTb_Var.GetNumRecords-1, SUMK1)
        self._VTb_Var.SetValue( self._lst_fKc.Get(k),    self._VTb_Var.GetNumRecords-1, COSTK1)

        end #kont

        #for r in AvIter(range(self._nr)):
            #MsgBox.ListAsString(lstVVK.Get(r),"","")
        #end

        for a in self._Lst_nzn:
            Sum=0
            posA=self._lst_pos_anz.Get(a)
            for r in AvIter(range(self._nr)):
                Sum=Sum + lstVVK.Get(r).Get(posA)
            end
            for r in AvIter(range(self._nr)):
                va= self._lstVA.Get(r).Get(a)
                if (va>0) :
                    lstUK.Get(r).Set(posA, lstVVK.Get(r).Get(posA)*self._lstPA.Get(a)/(self._lstVA.Get(r).Get(a)*Sum))
                end
            end
        end
        #for r in AvIter(range(self._nr)):
        #    MsgBox.ListAsString(lstUK.Get(r),"","")
        #end

        for a in self._Lst_nzn:
            posA=self._lst_pos_anz.Get(a)
            VTb=av.FindDoc( self._V1+"_UK_"+a.AsString).GetVTab
            fld=VTb.FindField("Iter_"+(self._iterN+1).AsString)
            VTb.SetEditable(True)
            for r in AvIter(range(self._nr)):
                VTb.SetValue(fld, r, lstUK.Get(r).Get(posA))
            end

            fldIter = Field.Make("Iter_"+(self._iterN+2).AsString, Field.DECIMAL, 6, 3)
            fldIter.SetVisible( TRUE )
            VTb.AddFields(AvList([fldIter]))

            VTb.SetEditable(False)
        end
        #################MsgBox.Info(CostK.AsString,"Koszt Kontaktow") #@@@@@@@@@@@@@@@@@@@
        self._lst_K_Crnt.Set(0,CostK)
        self._VTb_Var.SetValue( self._lst_FVarKFD_k.Get(3),    self._VTb_Var.GetNumRecords-1, CostK)
        #MsgBox.Info("END Kont","")
        return NIL
    # END OF JS_OR_Kont
    ############

    def JS_OR_mult_J(self):           
        Tb_LAkt=av.FindDoc ("akt_lst")
        VTb_LAkt=Tb_LAkt.GetVtab
        lst_fld=AvList([VTb_LAkt.FindField("Mult_JK"),
                VTb_LAkt.FindField("Mult_JF"),
                VTb_LAkt.FindField("Mult_JD")])
        lst=AvList([])
        self._lst_jKFD=AvList([])
        for  a in AvIter(range(self._nnz)):
            self._lst_jKFD.Add(lst.Clone)
            for fld in lst_fld:
                self._lst_jKFD.Get(a).Add(VTb_LAkt.ReturnValue(fld,self._Lst_nzn.Get(a)))
            end
        end
    # END OF JS_OR_mult_J
    ############

    def JS_OR_mult_E(self):
        #****JS.OR_mult_E

        lst=AvList([])
        self._lst_eKFD=AvList([])
        for a in AvIter(range(self._nnz)):
            self._lst_eKFD.Add(lst.Clone)
            for p in AvIter([0,1,2]):
                self._lst_eKFD.Get(a).Add(self._lst_Dns.Get(a)*self._lst_jKFD.Get(a).Get(p))
            end
        end

        #for each a in 0..(self._nnz-1)
        #    lst=self._lst_eKFD.Get(a).Clone
        #    lst.Sort(FALSE)
        #    mx=lst.Get(0)
        #    for each p in 0..2
        #        self._lst_eKFD.Get(a).Set(p,self._lst_eKFD.Get(a).Get(p)/mx)
        #    end
        #end


        for p in AvIter([0,1,2]):
            lst=AvList([])
            for a in AvIter(range(self._nnz)):
                lst.Add(self._lst_eKFD.Get(a).Get(p))
            end
            lst.Sort(FALSE)
            mx=lst.Get(0)
            if (mx==0): 
                mx=1 
            end
            for a in AvIter(range(self._nnz)):
                self._lst_eKFD.Get(a).Set(p,self._lst_eKFD.Get(a).Get(p)/mx)
            end
            
        end
    # END OF JS_OR_mult_E
    ############

    def JS_OR_Ter(self):
        #**JS.OR_Ter
        lstATab=AvList([])
        LstFTab=AvList([])
        for a in self._Lst_nz:
            VTb=av.FindDoc (self._V1+"_Akt_Sc_"+a).GetVTab
            lstATab.Add(VTb)
            LstFTab.Add(VTb.FindField("Iter"+(self._iterN+1).AsString))
        end

        VTabRej=av.FindDoc ("rej").GetVTab
        FldCap=VTabRej.FindField("Cap")

        lst_Cap=AvList([])
        for r in AvIter(range(self._nr)):
            lst_Cap.Add(VTabRej.ReturnValue(FldCap,r))
        end
        lst_Fi=AvList([])     ########## wspolczynniki wagowe Fi
        for a in AvIter(range(self._nnz)):
            Sum=0
            for p in self._lstProc:
                Sum=Sum+(self._lst_eKFD.Get(a).Get(p)*self._lst_rKFD.Get(p))
            end
            lst_Fi.Add(Sum/self._nProc)
        end

        #self._lst_VnzA_t=self._LST_TMP.DeepClone
        #self._LST_TMP=self._lst_VnzA_t.DeepClone
        lst_VASc=self._lst_VnzA_t.DeepClone
        #RETURN    NIL


        #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$start cut bez konf ter
        #for i in AvIter(range(self._nnz)):
        #    MSGBOX.LISTASSTRING(self._lst_jKFD.Get(i),"J"+i.Asstring,"")
        #end
        #for i in AvIter(range(self._nnz)):
        #    MSGBOX.LISTASSTRING(self._lst_eKFD.Get(i),"E"+i.Asstring,"")
        #end
        #MSGBOX.LISTASSTRING(self._lst_rKFD,"R","")
        #MSGBOX.LISTASSTRING(lst_Fi,"Fi","")
        #for i in range(0,(2)+1):
        #    MSGBOX.ListAsString(lst_VASc.Get(i),"VA","")
        #end
        #RETURN NIL

        #LSTSC=AvList([[],[],[],[]]])
        #for ls in LSTSC:
        #    for r in AvIter(range(self._nr)):
        #        ls.Add(0)
        #    end
        #end

        lst_ACutSum=AvList([])    #dla sprawozdania    relokacji
        for a in AvIter(range(self._nnz)):
            lst_ACutSum.Add(0)
        end

        #=====================================
        Rep1=True
        nR1=0
        while (Rep1):
            nR1=nR1+1
            if (nR1>50) :
                Rep1=False
                break
            end
            
            lst_Ocp=AvList([])    ######### wskazniki wypelnienia
            Ocp_mx=0
            for r in AvIter(range(self._nr)):
                Sum=0
                
        #        IF (R<5) :
        #        MSGBOX.LISTASSTRING(self._lst_VnzA_t.Get(r),r.AsString,"Poczatek REP1")
        #        END
                
                for a in AvIter(range(self._nnz)):
                    Sum=Sum+(self._lst_VnzA_t.Get(r).Get(a)/self._lst_Dns.Get(a))
                end
                Ocp=Sum/lst_Cap.Get(r)
                lst_Ocp.Add(Ocp)
                if (Ocp>Ocp_mx) :
                    Ocp_mx=Ocp
                end
            end


        #    MSGBOX.LISTASSTRING(lst_Ocp,"Ocup","")
            #RETURN NIL
            
            
            if (Ocp_mx<=1.02) :
                Rep1=False
                break
            end

            Ocp_cut=(self._vc*Ocp_mx)+((1- self._vc)/Ocp_mx) ######aktualny poziom ciecia
            
            #MSGBOX.INFO(Ocp_mx.AsString+Ocp_cut.AsString,"Max, Cut"+nR1.AsString)
            
            Rep2=TRUE
            nR2=0
            while (Rep2):
                nR2=nR2+1
                if (nR2>50) :
                    Rep2=False
                    break
                end

                lst_ACut=AvList([])
                for a in AvIter(range(self._nnz)):
                    lst_ACut.Add(0)
                end
                #=========ciecie w rejonach przepelnionych
                for r in AvIter(range(self._nr)):
                    Ocp=lst_Ocp.Get(r)
                    if (Ocp>Ocp_cut) :    #@@@@@@@ciecie tylko w rejonach przepelnionych
                        
                        
                        #=======wstepny wsp ciecia aktywnosci rejonach
                        Sum=0
                        for a in AvIter(range(self._nnz)):
                            Sum=Sum+(lst_Fi.Get(a)*self._lst_VnzA_t.Get(r).Get(a)/self._lst_Dns.Get(a))    #mianownik wsp. ciecia
                        end
                        
                        lst_Oc1=AvList([])
                        for a in AvIter(range(self._nnz)):
                            lst_Oc1.Add(lst_Fi.Get(a)*lst_Cap.Get(r)*Ocp_cut/Sum)    ######wsp ciecia aktywn a w rejonie r
                        end
                        
                        #MSGBOX.LISTASSTRING(lst_Oc1,"poczatkowe wsk ciecia rej"+r.AsString,NR1.AsString+NR2.AsString)
                        #=======end wstepny wsp ciecia aktywnosci rejonach
                        
                        
                        #=======normowanie wsp ciecia aktywnosci rejonach i przydzial aktywn
                        Rep3=True
                        NR3=0
                        while (Rep3):
                            NR3=NR3+1
                            Sum1=0
                            Sum2=0
                            for a in AvIter(range(self._nnz)):
                                if(lst_Oc1.Get(a)>=1) :
                                    Sum1=Sum1+(self._lst_VnzA_t.Get(r).Get(a)/self._lst_Dns.Get(a))
                                else:
                                    Sum2=Sum2+(lst_Fi.Get(a)*self._lst_VnzA_t.Get(r).Get(a)/self._lst_Dns.Get(a))
                                end
                            end 
                                                                                                                                
                            for a in AvIter(range(self._nnz)):
                                v=lst_Oc1.Get(a)
                                if (v>=1) :
                                    v=1
                                else:
                                    v=lst_Fi.Get(a)*(Ocp_cut*lst_Cap.Get(r) - Sum1)/Sum2
                                end
                                lst_Oc1.Set(a,v)
                            end
                            lst=lst_Oc1.Clone
                            lst.Sort(False)
                            mx=lst.Get(0)
                            
                            
                            if (mx<=1) :
                                Rep3=False
                                break
                            end
                        end
                        #MSGBOX.LISTASSTRING(lst_Oc1,"    ciecia w rej:"+r.AsString,NR1.AsString+NR2.AsString+NR3.AsString)

                        #TSUM=0
                        #for a in AvIter(range(self._nnz)):
                            #TSUM=TSUM+(self._lst_VnzA_t.Get(r).Get(a)*v/self._lst_Dns.Get(a))
                        #END
                        
                        
                        ############MSGBOX.LISTASSTRING(AvList([TSUM,lst_Cap.Get(r)*Ocp_cut]),"Before","")
                        
                        for a in AvIter(range(self._nnz)):
                            v=lst_Oc1.Get(a)
                            va=self._lst_VnzA_t.Get(r).Get(a)
                            lst_ACut.Set(a,lst_ACut.Get(a)+(va*(1-v))) ####sciete porcje aktywn    
                            self._lst_VnzA_t.Get(r).Set(a,va*v)        ########nowy przydzial aktywn a w rej r
                            
                            
                            #LSTSC.GET(a).SET(r,LSTSC.GET(a).GET(r)+(va*(1-v)))
                            
                            
                        end

                        #TSUM=0
                        #for a in AvIter(range(self._nnz)):
                            #TSUM=TSUM+(self._lst_VnzA_t.Get(r).Get(a)*v/self._lst_Dns.Get(a))
                        #END
                        ############MSGBOX.LISTASSTRING(AvList([TSUM,lst_Cap.Get(r)*Ocp_cut]),"After","")
                        #RETURN NIL
                        
                        #MSGBOX.LISTASSTRING(AvList([TSUM,((Ocp_cut*lst_Cap.Get(r) - Sum1))]),"must be equal","")
                        #MSGBOX.LISTASSTRING(lst_ACut,"Sciete aktywnosci, rej"+r.AsString,"")
                        #Stp=MSGBOX.YESNO("co dalej","",True)
                        #if (STP=False) : Return NIL end
                        #=======end normowanie wsp ciecia aktywnosci rejonach i przydzial aktywn
        #            MSGBOX.LISTASSTRING(self._lst_VnzA_t.Get(r),r.AsString,"Tylko Scinane rejony")
                    end    #if (Ocp>Ocp_cut)
                    

                end #r
        #        MSGBOX.LISTASSTRING(lst_ACut,"","Sciete aktywnosci")
                
                #========    End ciecie w rejonach przepelnionych
                    
                #MSGBOX.INFO("koniec scinania","")
                #RETURN NIL
                for a in AvIter(range(self._nnz)):
                    lst_ACutSum.Set(a, lst_ACutSum.Get(a)+lst_ACut.Get(a)) #dla sprawozdania    relokacji
                end
                #========== rozprowadz nadwyzki
                lst_Sum=AvList([])
                for a in AvIter(range(self._nnz)):
                    lst_Sum.Add(0)
                end
                for r in AvIter(range(self._nr)):
                    if (Ocp<(Ocp_cut*0.98)) : #@@@@@@@tylko w rejonach z miejscem
                        for a in AvIter(range(self._nnz)):
                            a1=lst_VASc.Get(r).Get(a)
                            a2=self._lstVA.Get(r).Get(self._Lst_nzn.Get(a))
                            if (a2 !=0) :
                                a3=(a1**1.5)/(a2**0.5)
                                lst_Sum.Set(a, lst_Sum.Get(a)+a3) #BBBBBBBBBBBBBBBBB a2=0 powoduje blad#######
                            end
        #                    IF (R<4) :
        #                    MSGBOX.LISTASSTRING(AvList([r,a,a1,a2,a3]),"rej, a , a1, a2, a3","Retencja")
        #                    END
                        end
                    end
        #            IF (R<4) :
        #            MSGBOX.LISTASSTRING(self._lst_VnzA_t.Get(r),r.AsString,"Przed Retencja")
        #            MSGBOX.LISTASSTRING(lst_Sum,"lst_Sum","Retencja")
        #            END
                end
                

                for r in AvIter(range(self._nr)):
                    if (Ocp<(Ocp_cut*0.98)) :
                        for a in AvIter(range(self._nnz)):
                            a1=lst_VASc.Get(r).Get(a)
                            a2=self._lstVA.Get(r).Get(self._Lst_nzn.Get(a))
                            if (a2 != 0) :
                                a3=(a1**1.5)/(a2**0.5)
                            
                                va=self._lst_VnzA_t.Get(r).Get(a)
                                self._lst_VnzA_t.Get(r).Set(a,va+(a3/lst_Sum.Get(a)*lst_ACut.Get(a)) )######nowy przydz aktywn a w rej r
                            end
                        end
                    end
        #            IF (R<4) :
        #            MSGBOX.LISTASSTRING(self._lst_VnzA_t.Get(r),r.AsString,"Tylko Po Retencji")
        #            END
                end 
                #========== END rozprowadz nadwyzki
        #        RETURN NIL
                #========== aktualne wskazniki wypelnienia rejonow
                lst_Ocp=AvList([])    
                Ocp_mx=0
                for r in AvIter(range(self._nr)):
                    Sum=0
                    for a in AvIter(range(self._nnz)):
                        Sum=Sum+(self._lst_VnzA_t.Get(r).Get(a)/self._lst_Dns.Get(a))
                    end
                    Ocp=Sum/lst_Cap.Get(r)
                    lst_Ocp.Add(Ocp)
                    if (Ocp>Ocp_mx) :
                        Ocp_mx=Ocp
                    end
                end
                #========== END aktualne wskazniki wypelnienia rejonow

                if (Ocp_mx<=(Ocp_cut*1.02)) :
                    Rep2=False
                    break
                end
            end #END While Rep2
            #========================================
            
            if (Ocp_cut<=1.02) :
                Rep1=False
                break
            end        
        end #Rep1
        #======= END Rep1


        #for a in AvIter(range(self._nnz)):
        #MSGBOX.LISTASSTRING(LSTSC.Get(a),"SCIETE AKTYWNOSCI",a.AsString)
        #END
        #RETURN NIL
        for a in AvIter(range(self._nnz)):
            self._VTb_Var.SetValue( self._lst_fTr.Get(self._Lst_nzn.Get(a)),    self._VTb_Var.GetNumRecords-1, lst_ACutSum.Get(a))
        end
        #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$End cut bez konf ter

        for a in AvIter(range(self._nnz)):
            Sum=0
            aa=self._Lst_nzn.Get(a)
            for r in AvIter(range(self._nr)):
                Sum=Sum+self._lst_VnzA_t.Get(r).Get(a)
            end 
            Sum=self._lstPA.Get(aa)/Sum
            for r in AvIter(range(self._nr)):
                self._lst_VnzA_t.Get(r).Set(a,self._lst_VnzA_t.Get(r).Get(a)*Sum)
            end 
            
            VTb=av.FindDoc( self._V1+"_Akt_"+aa.AsString).GetVTab

            VTb.SetEditable(True)
            fldIter = Field.Make("Iter_"+(self._iterN+1).AsString, Field.DECIMAL, 10, 1)
            fldIter.SetVisible( TRUE )
            VTb.AddFields(AvList([fldIter]))
            
            for r in AvIter(range(self._nr)):
                VTb.SetValue(fldIter, r, self._lst_VnzA_t.Get(r).Get(a)) #z konfliktem terenowym
                #VTb.SetValue(fldIter, r, lst_VASc.Get(r).Get(a))        #bez konfliktu terenowego
            end
            VTb.SetEditable(False)

        end    
    # END OF JS_OR_Ter
    ############

    def JS_OR_Pred(self):
        #**JS.OR_Pred
        DMax=5
        Tb_Rej=av.FindDoc ("rej")
        VTb_Rej=Tb_Rej.GetVtab

        lstVVD=AvList([])

        CostD=0
        for a in self._Lst_nzn:
            CostDA=0
            posA=self._lst_pos_anz.Get(a)
            fldPred=VTb_Rej.FindField("Pred_"+a.AsString)
            lstPred=AvList([])
            Sum=0
            for r in AvIter(range(self._nr)):
                D=VTb_Rej.ReturnValue(fldPred, r)
                lstPred.Add(D)
                Sum=Sum+(D*self._lstVA.Get(r).Get(a))
                CostDA=CostDA+(self._lstVA.Get(r).Get(a)*(DMax-D))
            end
            CostD=CostD+CostDA
            VTb=av.FindDoc(self._V1+"_UD_"+a.AsString).GetVTab
            fld=VTb.FindField("Iter_"+(self._iterN+1).AsString)
            VTb.SetEditable(True)
            for r in AvIter(range(self._nr)):
                VTb.SetValue(fld, r, self._lstPA.Get(a)*lstPred.Get(r)/Sum)
            end
            
            self._VTb_Var.SetValue( self._lst_fDc.Get(a), self._VTb_Var.GetNumRecords-1, CostDA)
            
            fldIter = Field.Make("Iter_"+(self._iterN+2).AsString, Field.DECIMAL, 6, 3)
            fldIter.SetVisible( TRUE )
            VTb.AddFields(AvList([fldIter]))
            VTb.SetEditable(False)

        end
        #MsgBox.Info(CostD.AsString,"KosztD") #@@@@@@@@@@
        self._lst_K_Crnt.Set(2,CostD)
        self._VTb_Var.SetValue( self._lst_FVarKFD_k.Get(5), self._VTb_Var.GetNumRecords-1, CostD)
    # END OF JS_OR_Pred
    ############

    def JS_OR_mult_R(self):
        #****JS.OR_mult_R

        #self._lst_K_Crnt=AvList([2,3,4])
        lst_K_Mn=self._lst_K_Min.Clone
        lst_K_Mx=self._lst_K_Max.Clone
        self._lst_rKFD=AvList([0,0,0])

        if (self._nProc==1) :
            self._lst_rKFD.Set(self._lstProc.Get(0),1)
        elif (self._nProc==2) :
            R0=self._lst_KFD.Get(self._lstProc.Get(0))
            R1=self._lst_KFD.Get(self._lstProc.Get(1))
            
            if (R0==R1) :
                for i in AvIter(range(self._nProc)):
                    p=self._lstProc.Get(i)
                    if (self._lst_K_Crnt.Get(p) < self._lst_K_Min.Get(p)) :
                        self._lst_rKFD.Set(p,0)
                    elif (self._lst_K_Crnt.Get(p) > self._lst_K_Max.Get(p)) :
                        self._lst_rKFD.Set(p,1)
                    else:
                        self._lst_rKFD.Set(p,(self._lst_K_Crnt.Get(p)-self._lst_K_Max.Get(p))/(self._lst_K_Min.Get(p)-self._lst_K_Max.Get(p)))
                    end
                end
            else:
                if (R0>R1) :
                    lst_K_Mx.Set(0,lst_K_Mn.Get(0)+((lst_K_Mx.Get(0)-lst_K_Mn.Get(0))*R1))
                    lst_K_Mn.Set(2,lst_K_Mn.Get(2)+((lst_K_Mx.Get(2)-lst_K_Mn.Get(2))*(1-R1)))
                else:
                    lst_K_Mn.Set(0,lst_K_Mn.Get(0)+((lst_K_Mx.Get(0)-lst_K_Mn.Get(0))*(1-R1)))
                    lst_K_Mx.Set(2,lst_K_Mn.Get(2)+((lst_K_Mx.Get(2)-lst_K_Mn.Get(2))*R1))
                end
                for i in AvIter(range(self._nProc)):
                    p=self._lstProc.Get(i)
                    if (self._lst_K_Crnt.Get(p) < lst_K_Mn.Get(p)) :
                        self._lst_rKFD.Set(p,0)
                    elif (self._lst_K_Crnt.Get(p) > lst_K_Mx.Get(p)) :
                        self._lst_rKFD.Set(p,1)
                    else:
                        self._lst_rKFD.Set(p,(self._lst_K_Crnt.Get(p)-lst_K_Mx.Get(p))/(lst_K_Mn.Get(p)-lst_K_Mx.Get(p)))
                    end
                end
                
            end
        #elif (self._nProc==3) :
        end
    # END OF JS_OR_mult_R
    ############

    def JS_OR_Scal(self):
        #**JS.OR_Scal
        lst_KFD_n=AvList(["_UK_","_UF_","_UD_"])


        self._lst_VnzA_t=AvList([])
        for r in AvIter(range(self._nr)):
            self._lst_VnzA_t.Add(AvList([])) 
        end

        if (self._nProc==1) :
            for a in self._Lst_nz:
                an=a.AsNumber
                VTb1=av.FindDoc (self._V1+ lst_KFD_n.Get(self._lstProc.Get(0)) +a).GetVTab
                IterFld1=VTb1.FindField("Iter_"+(self._iterN+1).AsString)
                for r in AvIter(range(self._nr)):
                    v=VTb1.ReturnValue(IterFld1,r)*self._lstVA.Get(r).Get(an)
                    self._lst_VnzA_t.Get(r).Add(v)
                end
            end

        elif (self._nProc==2) :
            aa=0
            for a in self._Lst_nz:
                an=a.AsNumber
                VTb1=av.FindDoc (self._V1+lst_KFD_n.Get(self._lstProc.Get(0))+a).GetVTab
                IterFld1=VTb1.FindField("Iter_"+(self._iterN+1).AsString)
                VTb2=av.FindDoc (self._V1+lst_KFD_n.Get(self._lstProc.Get(1))+a).GetVTab
                IterFld2=VTb2.FindField("Iter_"+(self._iterN+1).AsString)
                
                lstU=AvList([])
                Sum=0
                
                p=self._lstProc.Get(0)
                RJ1=self._lst_rKFD.Get(p) * self._lst_jKFD.Get(aa).Get(p)
                p=self._lstProc.Get(1)    
                RJ2=self._lst_rKFD.Get(p) * self._lst_jKFD.Get(aa).Get(p)
                for r in AvIter(range(self._nr)):
                    u1=1+((VTb1.ReturnValue(IterFld1,r)-1)*RJ1)
                    u2=1+((VTb2.ReturnValue(IterFld2,r)-1)*RJ2)
                    usc=(u1*u2)**0.5
                    lstU.Add(usc)
                    Sum=Sum+(self._lstVA.Get(r).Get(an)*usc)
                end

                for r in AvIter(range(self._nr)):
                    v=self._lstPA.Get(an)*self._lstVA.Get(r).Get(an)*lstU.Get(r)/Sum
                    self._lst_VnzA_t.Get(r).Add(v)
                end
                aa=aa+1
            end
        else: #=====self._nProc=3=======
            aa=0
            for a in self._Lst_nz:
                VTb1=av.FindDoc (self._V1+lst_KFD_n.Get(self._lstProc.Get(0))+a).GetVTab
                IterFld1=VTb1.FindField("Iter_"+(self._iterN+1).AsString)
                VTb2=av.FindDoc (self._V1+lst_KFD_n.Get(self._lstProc.Get(1))+a).GetVTab
                IterFld2=VTb2.FindField("Iter_"+(self._iterN+1).AsString)
                VTb3=av.FindDoc (self._V1+lst_KFD_n.Get(self._lstProc.Get(2))+a).GetVTab
                IterFld3=VTb3.FindField("Iter_"+(self._iterN+1).AsString)
                
                lstU=AvList([])
                Sum=0
                
                p=self._lstProc.Get(0)
                RJ1=self._lst_rKFD.Get(p) * self._lst_jKFD.Get(aa).Get(p)
                p=self._lstProc.Get(1)    
                RJ2=self._lst_rKFD.Get(p) * self._lst_jKFD.Get(aa).Get(p)
                p=self._lstProc.Get(2)    
                RJ3=self._lst_rKFD.Get(p) * self._lst_jKFD.Get(aa).Get(p)
                for r in AvIter(range(self._nr)):
                    u1=1+((VTb1.ReturnValue(IterFld1,r)-1)*RJ1)
                    u2=1+((VTb2.ReturnValue(IterFld2,r)-1)*RJ2)
                    u3=1+((VTb2.ReturnValue(IterFld2,r)-1)*RJ3)
                    usc=(u1*u2*u3)**0.33
                    lstU.Add(usc)
                    Sum=Sum+(self._lstVA.Get(r).Get(a)*usc)
                end

                for r in (self._nr-1):
                    v=self._lstPA.Get(a)*self._lstVA.Get(r).Get(a)*lstU.Get(r)/Sum
                    self._lst_VnzA_t.Get(r).Add(v)
                end
                
                aa=aa+1
            end

        end #=====end self._nProc=1,2,3 =======

        aa=0
        for a in self._Lst_nz:
            VTbA=av.FindDoc (self._V1+"_Akt_Sc_"+a).GetVTab
            IterFldA=VTbA.FindField("Iter_"+(self._iterN+1).AsString)
            Sum=0
            for r in AvIter(range(self._nr)):
                Sum=Sum+self._lst_VnzA_t.Get(r).Get(aa)
            end
            Sum=self._lstPA.Get(a.AsNumber)/Sum
            VTbA.SetEditable(True)
            for r in AvIter(range(self._nr)):
                self._lst_VnzA_t.Get(r).Set(aa,self._lst_VnzA_t.Get(r).Get(aa)*Sum)
                VTbA.SetValue(IterFldA,r,self._lst_VnzA_t.Get(r).Get(aa) )
            end


            fldIter = Field.Make("Iter_"+(self._iterN+2).AsString, Field.DECIMAL, 8, 1)
            fldIter.SetVisible( True )
            VTbA.AddFields(AvList([fldIter]))
            VTbA.SetEditable(False)
            
            
            aa=aa+1
        end
    # END OF JS_OR_Scal
    ############

    def run(self):

        V_pos=12

        av.GetDatabase()

        Lst=AvList([])
        #Pat = "*_proj_lst.dbf".AsPattern
        #for aObj in LstD:
        #    if ((aObj.GetClass.GetClassName=="Table") and (aObj.GetName==Pat)) :
        #        Lst.Add(aObj)
        #    end
        #end
        #Tb_Prj= MsgBox.ListAsString(Lst,"Wybierz tablice projektu","Projekt ORION")
        Tb_Prj=av.FindDoc("proj_lst")
        #if (Tb_Prj = NIL) then Return NIL end
        self._VTb_Prj=Tb_Prj.GetVtab
        fldN=self._VTb_Prj.FindField("Name")
        fldS=self._VTb_Prj.FindField("Symb")
        fldI=self._VTb_Prj.FindField("Val_int")
        fldT=self._VTb_Prj.FindField("Val_txt")
        fldD=self._VTb_Prj.FindField("Val_dec")


        self._Pref=self._VTb_Prj.ReturnValue(fldT,0)
        self._nr=self._VTb_Prj.ReturnValue(fldI,1)
        self._na=self._VTb_Prj.ReturnValue(fldI,2)
        self._nnz=self._VTb_Prj.ReturnValue(fldI,3)
        self._nk=self._VTb_Prj.ReturnValue(fldI,4)
        self._vc=self._VTb_Prj.ReturnValue(fldD,5)

        
        self._lst_K_Min=AvList([self._VTb_Prj.ReturnValue(fldD,6),self._VTb_Prj.ReturnValue(fldD,8),self._VTb_Prj.ReturnValue(fldD,10)])
        self._lst_K_Max=AvList([self._VTb_Prj.ReturnValue(fldD,7),self._VTb_Prj.ReturnValue(fldD,9),self._VTb_Prj.ReturnValue(fldD,11)])
        self._lst_K_Crnt=AvList([0,0,0])
        lst=AvList([])
        for rec in range(V_pos,((self._VTb_Prj.GetNumRecords-1))+1):
            if (self._VTb_Prj.ReturnValue(fldS,rec)=="V") :
                lst.Add(self._VTb_Prj.ReturnValue(fldN,rec))
            end
        end



        #**tabl wariantow
        V=MsgBox.ListAsString(lst,"Wybierz wariant do obliczen", "ORION")
        self._V1=self._VTb_Prj.ReturnValue(fldT,V_pos+lst.FindByValue(V))

        self._lst_KFD=AvList([])     #====lista wspolczynnikow procedur
        self._lst_KFD.Add(V.Extract(1).BasicTrim ("K=", "").AsNumber)
        self._lst_KFD.Add(V.Extract(2).BasicTrim ("F=", "").AsNumber)
        self._lst_KFD.Add(V.Extract(3).BasicTrim ("D=", "").AsNumber)

        self._nProc=0            #====liczba aktywnych procedur
        for i in self._lst_KFD:
            if (i>0):
                self._nProc=self._nProc+1
            end
        end

        if (self._nProc==0) :
            MsgBox.Error("Wszystkie procedury R-F-D sa wylaczone","ORION-Run")
            return
        end

        self._lstProc=AvList([])        #====lista aktywnych procedur
        for i in AvIter(range(self._lst_KFD.Count)):
            if (self._lst_KFD.Get(i)>0) :
                self._lstProc.Add(i.Clone)
            end
        end



        #**end tabl wariantow

        #**tabl var aggreg
        Tb_Var=av.FindDoc ("var_agr")
        self._VTb_Var=Tb_Var.GetVtab
        self._lst_FVarKFD_k=AvList([self._VTb_Var.FindField("ID"), self._VTb_Var.FindField("Name"), self._VTb_Var.FindField("Iter")])

        lst=AvList(["Cost_K","Cost_F","Cost_D"])
        for i in range(0,(2)+1):
            self._lst_FVarKFD_k.Add(self._VTb_Var.FindField(lst.Get(i)))
        end
        self._VTb_Var.SetEditable(TRUE)
        #**end tabl var aggreg


        self._lst_fKn=AvList([])
        self._lst_fKc=AvList([])
        for k in AvIter(range(self._nk)):
            self._lst_fKn.Add(self._VTb_Var.FindField("K_"+k.AsString+"_numb"))
            self._lst_fKc.Add(self._VTb_Var.FindField("K_"+k.AsString+"_cost"))
        end

        self._lst_fDc=AvList([])
        for a in AvIter(range(self._na)):
            self._lst_fDc.Add(self._VTb_Var.FindField("D_"+a.AsString+"_cost"))
        end

        self._lst_fTr=AvList([])
        for a in AvIter(range(self._na)):
            self._lst_fTr.Add(self._VTb_Var.FindField("T_"+a.AsString+"_reloc"))
        end

        #===========================================
        Tb_LAkt=av.FindDoc ("akt_lst")
        VTb_LAkt=Tb_LAkt.GetVtab
        fldMv=VTb_LAkt.FindField("Movable")
        fldDs=VTb_LAkt.FindField("Density")


        self._Lst_nz=AvList([])
        self._Lst_z=AvList([])
        for i in AvIter(range(self._na)):
            j=VTb_LAkt.ReturnValue(fldMv,i)
            if(j==1) :
                self._Lst_nz.Add(i.AsString)
            else:
                self._Lst_z.Add(i.AsString)
            end
        end
        self._Lst_nzn=AvList([])
        for a in self._Lst_nz:
            self._Lst_nzn.Add(a.AsNumber)
        end

        self._lst_pos_anz=AvList([])
        for a in AvIter(range(self._na)):
            self._lst_pos_anz.Add(NIL)
        end
        for i in AvIter(range(self._Lst_nzn.Count)):
            self._lst_pos_anz.Set(self._Lst_nzn.Get(i),i)
        end

        self._lst_Dns=AvList([])
        for a in self._Lst_nzn:
            self._lst_Dns.Add(VTb_LAkt.ReturnValue(fldDs,a))    
        end


        Pat = av.AsPattern("Iter_.*")
        #MsgBox.Info(self._Pref+"_"+self._V1+"_Akt_"+self._Lst_nz.Get(0)+".dbf","")
        VTb=av.FindDoc (self._V1+"_Akt_"+self._Lst_nz.Get(0)).GetVTab
        
        Lst=VTb.GetFields
        lstIterFld=AvList([])
        for Fld in Lst:
            if (Fld.GetName==Pat) :
                lstIterFld.Add(Fld)
            end
        end
        pIter=MsgBox.ListAsString(lstIterFld,"Wybierz rozmieszczenie poczatkowe","Run ORION").GetName.AsTokens("_").Get(1).AsNumber
        nIter=MsgBox.Input("Wprowadz liczbe iteracji do wykonania", "Run ORION", 1).AsNumber

        #--------------------Akt
        for a in self._Lst_nz:
            VTb=av.FindDoc (self._V1+"_Akt_"+a).GetVTab
            Lst=VTb.GetFields
            LstRmFld=AvList([])
            for Fld in Lst:
                FldN=Fld.GetName
                if ((FldN==Pat)and (FldN.AsTokens("_").Get(1).AsNumber>pIter)) :
                    LstRmFld.Add(Fld)
                end
            end
            if (LstRmFld.Count>0) :
                VTb.SetEditable(True)
                VTb.RemoveFields(LstRmFld)
                VTb.SetEditable(False)
            end
        end

        #--------------------Akt_Sc
        for a in self._Lst_nz:
            #MsgBox.Info(self._Pref+"_"+self._V1+"_Akt_Sc_"+a+".dbf","")
            VTb=av.FindDoc (self._V1+"_Akt_Sc_"+a).GetVTab
            Lst=VTb.GetFields
            LstRmFld=AvList([])
            for Fld in Lst:
                FldN=Fld.GetName
                if ((FldN==Pat)and (FldN.AsTokens("_").Get(1).AsNumber>(pIter+1))) :
                    LstRmFld.Add(Fld)
                end
            end
            if (LstRmFld.Count>0) :
                VTb.SetEditable(True)
                VTb.RemoveFields(LstRmFld)
                VTb.SetEditable(False)
            end
        end
        #--------------------K
        if (self._lst_KFD.Get(0)>0) :
            for a in self._Lst_nz:
                VTb=av.FindDoc (self._V1+"_UK_"+a).GetVTab
                Lst=VTb.GetFields
                LstRmFld=AvList([])
                for Fld in Lst:
                    FldN=Fld.GetName
                    if ((FldN==Pat)and (FldN.AsTokens("_").Get(1).AsNumber>(pIter+1))) :
                        LstRmFld.Add(Fld)
                    end
                end
                if (LstRmFld.Count>0) :
                    VTb.SetEditable(True)
                    VTb.RemoveFields(LstRmFld)
                    VTb.SetEditable(False)
                end
            end
        end 
        #--------------------F
        if (self._lst_KFD.Get(1)>0) :
            for a in self._Lst_nz:
                VTb=av.FindDoc (self._V1+"_UF_"+a).GetVTab
                Lst=VTb.GetFields
                LstRmFld=AvList([])
                for Fld in Lst:
                    FldN=Fld.GetName
                    if ((FldN==Pat)and (FldN.AsTokens("_").Get(1).AsNumber>(pIter+1))) :
                        LstRmFld.Add(Fld)
                    end
                end
                if (LstRmFld.Count>0) :
                    VTb.SetEditable(True)
                    VTb.RemoveFields(LstRmFld)
                    VTb.SetEditable(False)
                end
            end
        end
        #--------------------D
        if (self._lst_KFD.Get(2)>0) :
            for a in self._Lst_nz:
                VTb=av.FindDoc (self._V1+"_UD_"+a).GetVTab
                Lst=VTb.GetFields
                LstRmFld=AvList([])
                for Fld in Lst:
                    FldN=Fld.GetName
                    if ((FldN==Pat)and (FldN.AsTokens("_").Get(1).AsNumber>(pIter+1))) :
                        LstRmFld.Add(Fld)
                    end
                end
                if (LstRmFld.Count>0) :
                    VTb.SetEditable(True)
                    VTb.RemoveFields(LstRmFld)
                    VTb.SetEditable(False)
                end
            end
        end
        #--------------------



        #===============================    
        Tb_Rej=av.FindDoc ("rej")
        VTb_Rej=Tb_Rej.GetVtab

        # *******Listy Rozm Aktywn
        lst_a=AvList([])
        for a in AvIter(range(self._na)):
            lst_a.Add(a.AsString)
        end
        self._lstVA=AvList([])
        for r in range(1,(self._nr)+1):
            self._lstVA.Add(AvList([])) 
        end

        for a in lst_a:
            if (self._Lst_nz.FindByValue (a)>(-1)) :
                VTb=av.FindDoc(self._V1+"_Akt_"+a).GetVTab
                xx=0
                yy=0
                fld=VTb.FindField("Iter_"+ pIter.AsString)
            else:
                VTb= VTb_Rej
                fld=VTb.FindField("Akt_"+a)
            end
            for r in AvIter(range(self._nr)):
                self._lstVA.Get(r).Add(VTb.ReturnValue(fld,r))
            end
        end

        Tb_LAkt=av.FindDoc ("akt_lst")
        VTb_LAkt=Tb_LAkt.GetVtab
        fld=VTb_LAkt.FindField("Progr_Cal")
        self._lstPA=AvList([])
        for a in AvIter(range(self._na)):
            self._lstPA.Add(VTb_LAkt.ReturnValue(fld,a))
        end
        #------------------------------------------
        #
        #results = av.Run( "JS.OR_mult_J", AvList([]) )
        results = self.JS_OR_mult_J()
        ################MsgBox.Info("End J","")
        # results = av.Run( "JS.OR_mult_E", AvList([]) )
        results = self.JS_OR_mult_E()
        ################MsgBox.Info("End E","")


        for Iter in AvIter(range(pIter,((pIter+nIter-1))+1)):
            av.SetShowStatus (TRUE)
            av.ShowMsg ("Iteracja:"+Iter.AsString)
            progress = ((Iter-pIter)/(nIter-pIter)) * 100 
            doMore = av.SetStatus(progress)

            self._iterN=Iter
            self._iter=Iter.AsString
            rec=self._VTb_Var.AddRecord
            self._VTb_Var.SetValue( self._lst_FVarKFD_k.Get(0), rec, rec)
            self._VTb_Var.SetValue( self._lst_FVarKFD_k.Get(1), rec,  self._V1)
            self._VTb_Var.SetValue( self._lst_FVarKFD_k.Get(2), rec, self._iterN)
            
            
            if (self._lst_KFD.Get(0)>0) :
                #results = av.Run( "JS.OR_Kont", AvList([]) )
                results = self.JS_OR_Kont()
            end
        ################    MsgBox.Info("End K        iter:"+self._iter.AsString,"")
            
            if (self._lst_KFD.Get(2)>0) :
                #results = av.Run( "JS.OR_Pred", AvList([]) )
                result = self.JS_OR_Pred()
            end
        ################    MsgBox.Info("End D        iter:"+self._iter.AsString,"")
            #Return Nil
            
            if (self._lst_KFD.Get(1)>0) :
                pass
                #results = av.Run( "JS.OR_Konf", AvList([]) )
            end
            
            #results = av.Run( "JS.OR_mult_R", AvList([]) )
            result = self.JS_OR_mult_R()
        ################    MsgBox.Info("End R        iter:"+self._iter.AsString,"")
            
            #results = av.Run( "JS.OR_Scal", AvList([]) )
            result = self.JS_OR_Scal()
        ################    MsgBox.Info("End Sc        iter:"+self._iter.AsString,"")
        # RETURN NIL

            #results = av.Run( "JS.OR_Ter", AvList([]) )
            result=self.JS_OR_Ter()
            #MsgBox.Info("End T        iter:"+self._iter.AsString,"")

            for a in lst_a:
                if (self._Lst_nz.FindByValue (a)>(-1)) :
                    VTb=av.FindDoc( self._V1+"_Akt_"+a).GetVTab
                    fld=VTb.FindField("Iter_"+ (Iter+1).AsString)
                    an=a.AsNumber
                    for r in AvIter(range(self._nr)):
                        self._lstVA.Get(r).Set(an,VTb.ReturnValue(fld,r))
                    end
                end
            end
            if (not doMore) :
                break
            end
        end
        av.ClearMsg
        self._VTb_Var.SetEditable(FALSE)
        av.close()
        return 

