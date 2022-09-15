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