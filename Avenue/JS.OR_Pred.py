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
        CostDA=CostDA+(self._lstVA.Get(r).Get(a)*(Dmax-D))
    end
    CostD=CostD+CostDA
    VTb=av.FindDoc(self._V1+"_UD_"+a.AsString).GetVTab
    fld=VTb.FindField("Iter_"+(self._IterN+1).AsString)
    VTb.SetEditable(True)
    for r in AvIter(range(self._nr)):
        VTb.SetValue(fld, r, self._LstPA.Get(a)*lstPred.Get(r)/Sum)
    end
    
    self._VTb_Var.SetValue( self._lst_fDc.Get(a), self._VTb_Var.GetNumRecords-1, CostDA)
    
    fldIter = Field.Make("Iter_"+(self._IterN+2).AsString, #FIELD_DECIMAL, 6, 3)
    fldIter.SetVisible( TRUE )
    VTb.AddFields({fldIter})
    VTb.SetEditable(False)

end
#MsgBox.Info(CostD.AsString,"KosztD") #@@@@@@@@@@
self._lst_K_Crnt.Set(2,CostD)
self._VTb_Var.SetValue( self._lst_FVarKFD_k.Get(5), self._VTb_Var.GetNumRecords-1, CostD)