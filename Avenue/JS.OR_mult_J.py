'****JS.OR_mult_J

from av import AvList


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

