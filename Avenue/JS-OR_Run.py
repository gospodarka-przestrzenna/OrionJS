#**JS.OR_Run

### 
# ???
V_pos=12

LstD=av.GetProject.GetDocs 

Lst=AvList([])
Pat = "*_proj_lst.dbf".AsPattern
for aObj in LstD:
    if ((aObj.GetClass.GetClassName=="Table") and (aObj.GetName==Pat)) :
        Lst.Add(aObj)
    end
end
Tb_Prj=MsgBox.ListAsString(Lst,"Wybierz tablice projektu","Projekt ORION")

if (Tb_Prj = NIL) then Return NIL end
_VTb_Prj=Tb_Prj.GetVtab
fldN=_VTb_Prj.FindField("Name")
fldS=_VTb_Prj.FindField("Symb")
fldI=_VTb_Prj.FindField("Val_int")
fldT=_VTb_Prj.FindField("Val_txt")
fldD=_VTb_Prj.FindField("Val_dec")


_Pref=_VTb_Prj.ReturnValue(fldT,0)
_nr=_VTb_Prj.ReturnValue(fldI,1)
_na=_VTb_Prj.ReturnValue(fldI,2)
_nnz=_VTb_Prj.ReturnValue(fldI,3)
_nk=_VTb_Prj.ReturnValue(fldI,4)
_vc=_VTb_Prj.ReturnValue(fldD,5)

_lst_K_Min=AvList([_VTb_Prj.ReturnValue(fldD,6),_VTb_Prj.ReturnValue(fldD,8),_VTb_Prj.ReturnValue(fldD,10)])
_lst_K_Max=AvList([_VTb_Prj.ReturnValue(fldD,7),_VTb_Prj.ReturnValue(fldD,9),_VTb_Prj.ReturnValue(fldD,11)])
_lst_K_Crnt=AvList([0,0,0])
lst=AvList([])
for rec in range(V_pos,((_VTb_Prj.GetNumRecords-1))+1):
    if (_VTb_Prj.ReturnValue(fldS,rec)=="V") :
        lst.Add(_VTb_Prj.ReturnValue(fldN,rec))
    end
end



#**tabl wariantow
V=MsgBox.ListAsString(lst,"Wybierz wariant do obliczen", "ORION")
_V1=_VTb_Prj.ReturnValue(fldT,V_pos+lst.FindByValue(V))

_lst_KFD=AvList([])     #====lista wspolczynnikow procedur
_lst_KFD.Add(V.Extract(1).BasicTrim ("K=", "").AsNumber)
_lst_KFD.Add(V.Extract(2).BasicTrim ("F=", "").AsNumber)
_lst_KFD.Add(V.Extract(3).BasicTrim ("D=", "").AsNumber)

_nProc=0            #====liczba aktywnych procedur
for i in _lst_KFD:
    if (i>0):
        _nProc=_nProc+1
    end
end

if (_nProc==0) :
    MsgBox.Error("Wszystkie procedury R-F-D sa wylaczone","ORION-Run")
    return
end

_lstProc=AvList([])        #====lista aktywnych procedur
for i in AvIter(range(_lst_KFD.Count)):
    if (_lst_KFD.Get(i)>0) :
        _lstProc.Add(i.Clone)
    end
end



#**end tabl wariantow

#**tabl var aggreg
Tb_Var=av.FindDoc (_Pref+"_var_agr.dbf")
_VTb_Var=Tb_Var.GetVtab
_lst_FVarKFD_k=AvList([_VTb_Var.FindField("Id"), _VTb_Var.FindField("Name"), _VTb_Var.FindField("Iter")])

lst=AvList(["Cost_K","Cost_F","Cost_D"])
for i in range(0,(2)+1):
    _lst_FVarKFD_k.Add(_VTb_Var.FindField(lst.Get(i)))
end
_VTb_Var.SetEditable(TRUE)
#**end tabl var aggreg


_lst_fKn=AvList([])
_lst_fKc=AvList([])
for k in AvIter(range(_nk)):
    _lst_fKn.Add(_VTb_Var.FindField("K_"+k.AsString+"_numb"))
    _lst_fKc.Add(_VTb_Var.FindField("K_"+k.AsString+"_cost"))
end

_lst_fDc=AvList([])
for a in AvIter(range(_na)):
    _lst_fDc.Add(_VTb_Var.FindField("D_"+a.AsString+"_cost"))
end

_lst_fTr=AvList([])
for a in AvIter(range(_na)):
    _lst_fTr.Add(_VTb_Var.FindField("T_"+a.AsString+"_reloc"))
end

#===========================================
Tb_LAkt=av.FindDoc (_Pref+"_akt_lst.dbf")
VTb_LAkt=Tb_LAkt.GetVtab
fldMv=VTb_LAkt.FindField("Movable")
fldDs=VTb_LAkt.FindField("Density")


_Lst_nz=AvList([])
_Lst_z=AvList([])
for i in AvIter(range(_na)):
    j=VTb_LAkt.ReturnValue(fldMv,i)
    if(j==1) :
        _Lst_nz.Add(i.AsString)
    else:
        _Lst_z.Add(i.AsString)
    end
end
_Lst_nzn=AvList([])
for a in _Lst_nz:
    _Lst_nzn.Add(a.AsNumber)
end

_lst_pos_anz=AvList([])
for a in AvIter(range(_na)):
    _lst_pos_anz.Add(NIL)
end
for i in AvIter(range(_Lst_nzn.Count)):
    _lst_pos_anz.Set(_Lst_nzn.Get(i),i)
end

_lst_Dns=AvList([])
for a in _Lst_nzn:
    _lst_Dns.Add(VTb_LAkt.ReturnValue(FldDs,a))    
end


Pat = "Iter_*".AsPattern
#MsgBox.Info(_Pref+"_"+_V1+"_Akt_"+_Lst_nz.Get(0)+".dbf","")
VTb=av.FindDoc (_Pref+"_"+_V1+"_Akt_"+_Lst_nz.Get(0)+".dbf").GetVTab
Lst=VTb.GetFields
lstIterFld=AvList([])
for Fld in Lst:
    if (Fld.GetName==Pat) :
        lstIterFld.Add(Fld)
    end
end
pIter=MsgBox.ListAsString(lstIterFld,"Wybierz rozmieszczenie poczatkowe","Run ORION").GetName.AsTokens("_").Get(1).AsNumber
nIter=MsgBox.Input("Wprowadz liczbe iteracji do wykonania", "Run ORION", "1").AsNumber

#******* usuwanie pol Iter_*
#--------------------Akt
for a in _Lst_nz:
    VTb=av.FindDoc (_Pref+"_"+_V1+"_Akt_"+a+".dbf").GetVTab
    Lst=VTb.GetFields
    LstRmFld=AvList([])
    for Fld in Lst:
        FldN=Fld.GetName
        if ((FldN==Pat)and (FldN.AsTokens("_").Get(1).AsNumber>pIter)) :
            LstRmFld.Add(Fld)
        end
    end
    If (LstRmFld.Count>0) :
        VTb.SetEditable(True)
             VTb.RemoveFields(LstRmFld)
        VTb.SetEditable(False)
    end
end

#--------------------Akt_Sc
for a in _Lst_nz:
    #MsgBox.Info(_Pref+"_"+_V1+"_Akt_Sc_"+a+".dbf","")
    VTb=av.FindDoc (_Pref+"_"+_V1+"_Akt_Sc_"+a+".dbf").GetVTab
    Lst=VTb.GetFields
    LstRmFld=AvList([])
    for Fld in Lst:
        FldN=Fld.GetName
        if ((FldN==Pat)and (FldN.AsTokens("_").Get(1).AsNumber>(pIter+1))) :
            LstRmFld.Add(Fld)
        end
    end
    If (LstRmFld.Count>0) :
        VTb.SetEditable(True)
             VTb.RemoveFields(LstRmFld)
        VTb.SetEditable(False)
    end
end
#--------------------K
if (_lst_KFD.Get(0)>0) :
    for a in _Lst_nz:
        VTb=av.FindDoc (_Pref+"_"+_V1+"_UK_"+a+".dbf").GetVTab
        Lst=VTb.GetFields
        LstRmFld=AvList([])
        for Fld in Lst:
            FldN=Fld.GetName
            if ((FldN==Pat)and (FldN.AsTokens("_").Get(1).AsNumber>(pIter+1))) :
                LstRmFld.Add(Fld)
            end
        end
        If (LstRmFld.Count>0) :
            VTb.SetEditable(True)
                 VTb.RemoveFields(LstRmFld)
            VTb.SetEditable(False)
        end
    end
end
#--------------------F
if (_lst_KFD.Get(1)>0) :
    for a in _Lst_nz:
        VTb=av.FindDoc (_Pref+"_"+_V1+"_UF_"+a+".dbf").GetVTab
        Lst=VTb.GetFields
        LstRmFld=AvList([])
        for Fld in Lst:
            FldN=Fld.GetName
            if ((FldN==Pat)and (FldN.AsTokens("_").Get(1).AsNumber>(pIter+1))) :
                LstRmFld.Add(Fld)
            end
        end
        If (LstRmFld.Count>0) :
            VTb.SetEditable(True)
                 VTb.RemoveFields(LstRmFld)
            VTb.SetEditable(False)
        end
    end
end
#--------------------D
if (_lst_KFD.Get(2)>0) :
    for a in _Lst_nz:
        VTb=av.FindDoc (_Pref+"_"+_V1+"_UD_"+a+".dbf").GetVTab
        Lst=VTb.GetFields
        LstRmFld=AvList([])
        for Fld in Lst:
            FldN=Fld.GetName
            if ((FldN==Pat)and (FldN.AsTokens("_").Get(1).AsNumber>(pIter+1))) :
                LstRmFld.Add(Fld)
            end
        end
        If (LstRmFld.Count>0) :
            VTb.SetEditable(True)
                 VTb.RemoveFields(LstRmFld)
            VTb.SetEditable(False)
        end
    end
end
#--------------------



#===============================    
Tb_Rej=av.FindDoc (_Pref+"_rej.dbf")
VTb_Rej=Tb_Rej.GetVtab

# *******Listy Rozm Aktywn
lst_a=AvList([])
for a in AvIter(range(_na)):
    lst_a.Add(a.AsString)
end
_lstVA=AvList([])
for r in range(1,(_nr)+1):
    _lstVA.Add(AvList([])) 
end

for a in lst_a:
    if (_Lst_nz.FindByValue (a)>(-1)) :
        VTb=av.FindDoc(_Pref+"_"+ _V1+"_Akt_"+a+".dbf").GetVTab
        xx=0
        yy=0
        fld=VTb.FindField("Iter_"+ pIter.AsString)
    else:
        VTb= VTb_Rej
        fld=VTb.FindField("Akt_"+a)
    end
    for r in AvIter(range(_nr)):
        _lstVA.Get(r).Add(VTb.ReturnValue(fld,r))
    end
end

Tb_LAkt=av.FindDoc (_Pref+"_akt_lst.dbf")
VTb_LAkt=Tb_LAkt.GetVtab
fld=VTb_LAkt.FindField("Progr_Cal")
_lstPA=AvList([])
for a in AvIter(range(_na)):
    _lstPA.Add(VTb_LAkt.ReturnValue(fld,a))
end
#------------------------------------------
#
results = av.Run( "JS.OR_mult_J", AvList([]) )
################MsgBox.Info("End J","")
results = av.Run( "JS.OR_mult_E", AvList([]) )
################MsgBox.Info("End E","")


for iter in range(piter,((pIter+nIter-1))+1):
    av.SetShowStatus (TRUE)
    av.ShowMsg ("Iteracja:"+Iter.AsString)
    progress = ((Iter-pIter)/(nIter-pIter)) * 100 
    doMore = av.SetStatus( progress )

    _iterN=iter
    _iter=iter.AsString
    rec=_VTb_Var.AddRecord
    _VTb_Var.SetValue( _lst_FVarKFD_k.Get(0), rec, rec)
    _VTb_Var.SetValue( _lst_FVarKFD_k.Get(1), rec, _Pref+"_"+ _V1)
    _VTb_Var.SetValue( _lst_FVarKFD_k.Get(2), rec, _iterN)
    
    
    if (_lst_KFD.Get(0)>0) :
        results = av.Run( "JS.OR_Kont", AvList([]) )
    end
################    MsgBox.Info("End K        iter:"+_Iter.AsString,"")
    
    if (_lst_KFD.Get(2)>0) :
        results = av.Run( "JS.OR_Pred", AvList([]) )
    end
################    MsgBox.Info("End D        iter:"+_Iter.AsString,"")
    #Return Nil
    
    if (_lst_KFD.Get(1)>0) :
        #results = av.Run( "JS.OR_Konf", AvList([]) )
    end
    
    results = av.Run( "JS.OR_mult_R", AvList([]) )
################    MsgBox.Info("End R        iter:"+_Iter.AsString,"")
    
    results = av.Run( "JS.OR_Scal", AvList([]) )
################    MsgBox.Info("End Sc        iter:"+_Iter.AsString,"")
# RETURN NIL

    results = av.Run( "JS.OR_Ter", AvList([]) )
    #MsgBox.Info("End T        iter:"+_Iter.AsString,"")

    for a in lst_a:
        if (_Lst_nz.FindByValue (a)>(-1)) :
            VTb=av.FindDoc(_Pref+"_"+ _V1+"_Akt_"+a+".dbf").GetVTab
            fld=VTb.FindField("Iter_"+ (iter+1).AsString)
            an=a.AsNumber
            for r in AvIter(range(_nr)):
                _lstVA.Get(r).Set(an,VTb.ReturnValue(fld,r))
            end
        end
    end
    if (not doMore) :
        break
    end
end
av.ClearMsg
_VTb_Var.SetEditable(FALSE)
