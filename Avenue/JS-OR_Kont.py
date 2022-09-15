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
for i in AvIter(range(_Lst_nzn.Count)):
    lst.Add(0)
end

for r in AvIter(range(_nr)):
    lstVVK.Add(lst.DeepClone )
    lstUK.Add(lst.DeepClone )
end
#for r in AvIter(range(_nr)):
#    MsgBox.ListAsString(lstVVK.Get(r),"","")
#    MsgBox.ListAsString(_lstVA.Get(r),"","")
#end

#eul=Number.GetEuler # EXP będziemy generować inaczej
CostK=0
#************* begin cal

for k in AvIter(range(_nk)):
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
    for i in AvIter(range(_nr)):
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
            lstZon.add(i)
        end
        j=VTb_Zon.ReturnValue(fld_Cost,rec)
        if (j>0) :
            lstCost.add(j)
        end
    end
    lstZon.RemoveDuplicates
    lstZon.Sort(TRUE)
    lstCost.RemoveDuplicates
    lstCost.Sort(TRUE)

#-------------------
    KZon= -1
    for j in lstZon:
        if (j>=kzk) :
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
        if (_Lst_nzn.FindByValue(a) > -1) :
            lst_ds_nz.Add(a)
        end
    end
#-----------------------------------------
    for r in AvIter(range(_nr)):
        Pr=1
        SumP=0
        VOr=0
        for a in lst_orn:
            ######## tu mozna zmienic Nas na indywidualny
            VOr=VOr+(Nas*_lstVA.Get(r).Get(a))
        end
        if (VOr>0) :
            for strf in range(0,(KZon)+1):
                lstDStrf=VTb_Nod.ReturnValue(Lst_Strf.Get(strf),lstRPos.Get(r)).AsList
                #######MsgBox.Info(strf.AsString,"strefa")
                if (lstDStrf.Count>0) :
                    for i in AvIter(range(lstDStrf.Count)):
                        lstDStrf.Set(i,lstDStrf.Get(i).AsNumber)
                    end
                    SumS=0     #**** suma celow w strefie
                    for rr in lstDStrf:
                        for aa in lst_dsn:
                            SumS=SumS+_lstVA.Get(rr).Get(aa)
                        end
                    end
                    if (SumS>0) :
                        #PrC=eul^(Sel*(SumP+SumS))
                        PrC=math.exp(Sel*(SumP+SumS))
                        #MsgBox.Info((SumP+SumS).AsString+PrC.AsString+strf.AsString,k.AsString+r.AsString)
                        PrS=Pr-PrC
                        Vot=VOr*PrS         #Glos do strefy
                        COSTK1=COSTK1+(Vot*lstCost.Get(strf))
                        SUMK1=Sumk1+Vot
                        CostK=CostK+(Vot*lstCost.Get(strf)) #Sumowanie kosztow kontaktow
                        #MsgBox.Info(Nas.AsString+PrS.AsString+Vot.AsString,"")
                        for rr in lstDStrf:
                            
                            for aa in lst_ds_nz:
                                posA=_lst_pos_anz.Get(aa)
                                lstVVK.Get(rr).Set(posA, lstVVK.Get(rr).Get(posA) + (Vot*_lstVA.Get(rr).Get(aa)/SumS))
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
_VTb_Var.SetValue( _lst_fKn.Get(k),    _VTb_Var.GetNumRecords-1, SUMK1)
_VTb_Var.SetValue( _lst_fKc.Get(k),    _VTb_Var.GetNumRecords-1, COSTK1)

end #kont

#for r in AvIter(range(_nr)):
    #MsgBox.ListAsString(lstVVK.Get(r),"","")
#end

for a in _Lst_nzn:
    Sum=0
    posA=_lst_pos_anz.Get(a)
    for r in AvIter(range(_nr)):
        Sum=Sum + lstVVK.Get(r).Get(posA)
    end
    for r in AvIter(range(_nr)):
        va= _lstVA.Get(r).Get(a)
        if (va>0) :
            lstUK.Get(r).Set(posA, lstVVK.Get(r).Get(posA)*_LstPA.Get(a)/(_lstVA.Get(r).Get(a)*Sum))
        end
    end
end
#for r in AvIter(range(_nr)):
#    MsgBox.ListAsString(lstUK.Get(r),"","")
'end

for a in _Lst_nzn:
    posA=_lst_pos_anz.Get(a)
    VTb=av.FindDoc( _V1+"_UK_"+a.AsString).GetVTab
    fld=VTb.FindField("Iter_"+(_IterN+1).AsString)
    VTb.SetEditable(True)
    for r in AvIter(range(_nr)):
        VTb.SetValue(fld, r, lstUK.Get(r).Get(posA))
    end

    fldIter = Field.Make("Iter_"+(_IterN+2).AsString, Field.DECIMAL, 6, 3)
    fldIter.SetVisible( TRUE )
    VTb.AddFields(AvList([fldIter]))

    VTb.SetEditable(False)
end
#################MsgBox.Info(CostK.AsString,"Koszt Kontaktow") #@@@@@@@@@@@@@@@@@@@
_lst_K_Crnt.Set(0,CostK)
_VTb_Var.SetValue( _lst_FVarKFD_k.Get(3),    _VTb_Var.GetNumRecords-1, CostK)
#MsgBox.Info("END Kont","")
Return NIL