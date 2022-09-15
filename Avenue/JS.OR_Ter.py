#**JS.OR_Ter
lstATab=AvList([])
LstFTab=AvList([])
for a in self._Lst_nz:
    VTb=av.FindDoc (self._V1+"_Akt_Sc_"+a).GetVTab
    lstATab.Add(VTb)
    LstFTab.Add(VTb.FindField("Iter"+(self._IterN+1).AsString))
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
    while (Rep2)
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
                
#                MSGBOX.LISTASSTRING(lst_Oc1,"poczatkowe wsk ciecia rej"+r.AsString,NR1.AsString+NR2.AsString)
                #=======end wstepny wsp ciecia aktywnosci rejonach
                
                
                #=======normowanie wsp ciecia aktywnosci rejonach i przydzial aktywn
                Rep3=True
                NR3=0
                while (REP3)
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
                    a3=(a1^1.5)/(a2^0.5)
                    if (a3.IsNotNULL) :
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
                    a3=(a1^1.5)/(a2^0.5)
                    if ((a3.IsNULL).NOT) :
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

        if (Ocp_mx<=(Ocp_Cut*1.02)) :
            Rep2=False
            break
        end
    end #END While Rep2
    #========================================
    
    if (Ocp_Cut<=1.02) :
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
    Sum=self._LstPA.Get(aa)/Sum
    for r in AvIter(range(self._nr)):
        self._lst_VnzA_t.Get(r).Set(a,self._lst_VnzA_t.Get(r).Get(a)*Sum)
    end 
    
    VTb=av.FindDoc( self._V1+"_Akt_"+aa.AsString).GetVTab

    VTb.SetEditable(True)
    fldIter = Field.Make("Iter_"+(self._IterN+1).AsString, Field.DECIMAL, 10, 1)
    fldIter.SetVisible( TRUE )
    VTb.AddFields(AvList([fldIter]))
    
    for r in AvIter(range(self._nr)):
        VTb.SetValue(fldIter, r, self._lst_VnzA_t.Get(r).Get(a)) #z konfliktem terenowym
        #VTb.SetValue(fldIter, r, lst_VASc.Get(r).Get(a))        #bez konfliktu terenowego
    end
    VTb.SetEditable(False)

end    

    
