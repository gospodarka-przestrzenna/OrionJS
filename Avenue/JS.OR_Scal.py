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
        IterFld1=VTb1.FindField("Iter_"+(self._IterN+1).AsString)
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
        IterFld1=VTb1.FindField("Iter_"+(self._IterN+1).AsString)
        VTb2=av.FindDoc (self._V1+lst_KFD_n.Get(self._lstProc.Get(1))+a).GetVTab
        IterFld2=VTb2.FindField("Iter_"+(self._IterN+1).AsString)
        
        lstU=AvList([])
        Sum=0
        
        p=self._lstProc.Get(0)
        RJ1=self._lst_rKFD.Get(p) * self._lst_jKFD.Get(aa).Get(p)
        p=self._lstProc.Get(1)    
        RJ2=self._lst_rKFD.Get(p) * self._lst_jKFD.Get(aa).Get(p)
        for r in AvIter(range(self._nr)):
             u1=1+((VTb1.ReturnValue(IterFld1,r)-1)*RJ1)
             u2=1+((VTb2.ReturnValue(IterFld2,r)-1)*RJ2)
             usc=(u1*u2)^0.5
             lstU.Add(usc)
             Sum=Sum+(self._lstVA.Get(r).Get(an)*usc)
        end

        for r in AvIter(range(self._nr)):
             v=self._lstPA.Get(an)*self._lstVA.Get(r).Get(an)*lstU.Get(r)/Sum
             self._lst_VnzA_t.Get(r).Add(v)
        end
        aa=aa+1
    end
else #=====self._nProc=3=======
    aa=0
    for a in self._Lst_nz:
        VTb1=av.FindDoc (self._V1+lst_KFD_n.Get(self._lstProc.Get(0))+a).GetVTab
        IterFld1=VTb1.FindField("Iter_"+(self._IterN+1).AsString)
        VTb2=av.FindDoc (self._V1+lst_KFD_n.Get(self._lstProc.Get(1))+a).GetVTab
        IterFld2=VTb2.FindField("Iter_"+(self._IterN+1).AsString)
        VTb3=av.FindDoc (self._V1+lst_KFD_n.Get(self._lstProc.Get(2))+a).GetVTab
        IterFld3=VTb3.FindField("Iter_"+(self._IterN+1).AsString)
        
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
             usc=(u1*u2*u3)^0.33
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
    IterFldA=VTbA.FindField("Iter_"+(self._IterN+1).AsString)
    Sum=0
    for r in AvIter(range(self._nr)):
        Sum=Sum+self._lst_VnzA_t.Get(r).Get(aa)
    end
    Sum=self._LstPA.Get(a.AsNumber)/Sum
    VTbA.SetEditable(True)
    for r in AvIter(range(self._nr)):
        self._lst_VnzA_t.Get(r).Set(aa,self._lst_VnzA_t.Get(r).Get(aa)*Sum)
        VTbA.SetValue(IterFldA,r,self._lst_VnzA_t.Get(r).Get(aa) )
    end


    fldIter = Field.Make("Iter_"+(self._IterN+2).AsString, Field.DECIMAL, 8, 1)
    fldIter.SetVisible( True )
    VTbA.AddFields(AvList([fldIter]))
    VTbA.SetEditable(False)
    
    
    aa=aa+1
end



