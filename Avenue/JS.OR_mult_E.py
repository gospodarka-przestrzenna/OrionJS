#****JS.OR_mult_E

lst=AvList([])
self._lst_eKFD=AvList([])
for a in AvIter(range(self._nnz)):
    self._lst_eKFD.Add(lst.clone)
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
