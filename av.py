#from PyQt5.QtWidgets import QMessageBox
import sqlite3
import os,re

from datetime import datetime
__all__=['av','MsgBox','TRUE','FALSE','NL','AvList','NIL','nil','end','AvIter','Table','VTab','Field']

TRUE=True
FALSE=False
NL='\n'
NIL=None
nil=NIL
end=''

NOQGIS=False

if not NOQGIS:
    from qgis.utils import spatialite_connect
    from PyQt5.QtWidgets import QApplication,QMessageBox,QInputDialog,QFileDialog,QProgressDialog
    from PyQt5.QtCore import Qt
    #from PyQt5.QtGui import 
class AvOperations(object):
    def __add__(self,val):
        return AvVar(self.aspect(self)+val)
    def __radd__(self,val):
        return AvVar(val+self.aspect(self))
    def __mul__(self,val):
        return AvVar(self.aspect(self)*val)
    def __rmul__(self,val):
        return AvVar(val*self.aspect(self))
    def __truediv__(self,val):
        return AvVar(self.aspect(self)/val)
    def __rtruediv__(self,val):
        return AvVar(val/self.aspect(self))

class AvFloat(AvOperations,float):
    aspect=float
    def __init__(self,me):
        self=me
    def __getattr__(self,attribute):
        if attribute=='AsNumber':
            return self
        if attribute=='AsString':
            return AvStr(str(self))
        if attribute=='IsNumber':
            return True
        if attribute=='IsNotNumber':
            return False

class AvInt(AvOperations,int):
    aspect=int
    def __init__(self,me):
        self=me
    def __getattr__(self,attribute):
        if attribute=='AsList': 
            return AvStr(str(self)).AsList
        if attribute=='AsNumber':
            return self
        if attribute=='AsString':
            return AvStr(str(self))
        if attribute=='IsNumber':
            return True
        if attribute=='IsNotNumber':
            return False
        if attribute=='Clone':
            return int(self)

class MyNone(object):
    def __getattr__(self,attribute):
        if attribute=='AsNumber':
            return None
        if attribute=='AsString':
            return "(NULL)"
        if attribute=='AsList':
            return AvList([])
        if attribute=='IsNumber':
            return False
        if attribute=='IsNotNumber':
            return False
sqlite3.register_adapter(MyNone,lambda x: None)    

class AvStr(str,AvOperations):
    aspect=str
    def __init__(self,me):
        self=me
    def Right(self,numb):
        return self[-numb:]
    def Extract(self,num):
        return AvStr(self.split(" ")[num])
    def AsTokens(self,t):
        return AvList(self.split(t))
    def BasicTrim(self,s,e):
        self=self.replace(s,e)
        return AvStr(self)
    def __getattr__(self,attribute):
        if attribute=='AsNumber':
            try:
                return AvInt(int(self))
            except:
                pass
            return AvFloat(float(self))
        if attribute=='AsString':
            return self
        if attribute=='AsList':
            return AvList([AvInt(int(x)) for x in self.split(' ') if x!=''])
        if attribute=='IsNumber':
            return False
        if attribute=='IsNotNumber':
            return True
        if attribute=="GetName":
            return self
    def __eq__(self,element):
        if type(element) in [str, AvStr]:
            return str(element)==str(self)
        if type(element)==re.Pattern:
            if (element.match(str(self))):
                return True
            return False       
    
def AvVar(n):
    if type(n)==int:
        return AvInt(n)
    if type(n)==str:
        return AvStr(n)
    if type(n)==float:
        return AvFloat(n)    
    if type(n) in [AvInt ,AvStr, AvFloat, MyNone, AvList, MyField]:
        return n
    if n is None:
        return MyNone()
    print("unsupported type:",type(n))
    return n

class AvIter(object):
    def __init__(self,itr):
        try:
            self.iter=iter(itr)
        except:
            self.iter=iter(range(itr))
    def __iter__(self):
        return self
    def __next__(self):
        n=next(self.iter)
        p=AvVar(n)
        return p

class VTable(object):
    def __init__(self,name,av,fields):
        self.name=name
        self.av=av
        self.fields: list[MyField] = fields
        self.field_id: dict[str,int] = {f.name:i for i,f in enumerate(fields)}
        self.rows=[]

    def AddFields(self,fields):
        for f in fields:
            if f.name == "ID":
                continue
            self.fields.append(f)
            for r in self.rows:
                r.append(MyNone())
            if f.db_type:
                self._add_field(f)
            self.field_id={f.name:i for i,f in enumerate(self.fields)}
            
    def _add_field(self,f):
        q="ALTER TABLE %s ADD COLUMN %s"%(self.name,f.name+' '+f.db_type)
        self.av.con.execute(q)
        
        q='UPDATE gpkg_contents SET  last_change=? WHERE table_name=?' 
        self.av.con.execute(q,(datetime.now().isoformat(),self.name))        

        self.av.con.commit()

    def RemoveFields(self,fields):
        for f in fields:
            if f.name.lower() == "id":
                continue
            idx=self.field_id[f.name]

            self.fields=[fi for fi in self.fields if fi.name!=f.name ]
            self.field_id={f.name:i for i,f in enumerate(self.fields)}

            for r in self.rows:
                del(r[idx])
            q='ALTER TABLE %s DROP COLUMN %s'%(self.name,f.name)
            self.av.con.execute(q)
        q='UPDATE gpkg_contents SET  last_change=? WHERE table_name=?' 
        self.av.con.execute(q,(datetime.now().isoformat(),self.name))       
        self.av.con.commit()
        

    def __getattr__(self, attribute):
        if attribute=="AddRecord":
            return self.addRecord() 
        if attribute=="GetName":
            return self.name
        if attribute=="HasError":
            return False
        if attribute=="GetNumRecords":
            return len(self.rows)
        if attribute=="GetFields":
            return AvList(self.fields)

    def addRecord(self):
        row=[MyNone() for field in self.fields]
        self.rows.append(row)
        return len(self.rows)-1

    def SetEditable(self,tf):
        if not tf:
            self._save()
    def _save(self):
        self.av.con.execute("DELETE FROM %s" % self.name)
        self.av.con.commit()
        insert = "INSERT INTO %s VALUES (%s)"%(
            self.name,
            ','.join(['?' for f in self.fields])
        )
        self.av.con.executemany(insert,self.rows)
        q='UPDATE gpkg_contents SET  last_change=? WHERE table_name=?' 
        self.av.con.execute(q,(datetime.now().isoformat(),self.name))       
        self.av.con.commit()
        #print(self.av.con.execute("SELECT * FROM %s"%self.name).fetchall())

    def SetValue(self,field,nr,value):
        self.rows[nr][
            self.field_id[field.name]
            ]=value

    def ReturnValue(self,field,nr):
        return AvVar(self.rows[nr][
                self.field_id[field.name]
            ])

    def FindField(self,name):
        for f in self.fields:
            if f.name.lower() == name.lower() :
                return f

    def __iter__(self):
        return AvIter(range(len(self.rows)))

class AvList(list):
    def __init__(self,values):
        self.extend(values)
    def Add(self,el):
        self.append(el)
    def Get(self,i):
        return AvVar(self[i])
    def Set(self,i,el):
        if not i<len(self):
            raise(IndexError())
        self[i]=el
        
        #OR ERROR
    def Sort(self,bool):
        self.sort(reverse=(not bool))
    def __getattr__(self,attribute):
        if attribute=='Clone':
            return AvList(list(self))
        if attribute=='Count':
            return len(self)
        if attribute=='RemoveDuplicates':
            i=0
            while i<len(self):
                if(self[i] in self[:i]):
                    del(self[i])
                else:
                    i=i+1
        if attribute=='DeepClone':
            output=AvList([])
            for el in self:
                if type(el) == AvList :
                    output.append(el.DeepClone)
                elif type(el) == list:
                    output.append(list(el))
                else:
                    output.append(el)
            return output
    def FindByValue(self,el):
            if el in self:
                return self.index(el)
            return -1

class Av(object):
    def __init__(self,con=None,iface=None):
        self.con=con
        self.tables={}
        self.iface=iface
        self.progress=None
    def AsPattern(self,pat):
        return re.compile(pat,flags=re.I)    
    def FindDoc(self,table):
        cur=self.con.execute("SELECT * FROM %s ORDER BY ID"%table)
        fields=[MyField(i[0]) for i in cur.description]
        
        vtable=VTable(table,self,fields)
        vtable.rows=[list(row) for row in cur.fetchall()]
        idx=vtable.field_id[vtable.FindField("ID").name]
        if len(vtable.rows)>0 and vtable.rows[-1][idx]!=(len(vtable.rows)-1):
            raise IndexError("ID column must mach row numbers",vtable.rows[-1][idx],len(vtable.rows) )
        self.tables[str(table)]=vtable
        mt=MyTable(self,vtable)
        return mt
    def close(self):
        for vtable in self.tables.values():
            vtable._save()
        self.con.close()

    def NewDatabase(self):
        self.tables={}
        if NOQGIS:
            self.name=":memory:"
            self.con=sqlite3.connect(self.name)
        else:
            FNWrkDB=QFileDialog.getSaveFileName(None,caption="Choose file",
                directory=os.path.expanduser("~/OrionJS.gpkg"),filter="(*.gpkg *.sqlite)",
                options=QFileDialog.DontConfirmOverwrite
                )
            self.name=FNWrkDB[0]
            self.con=spatialite_connect(self.name)
        try:
            self.con.execute("SELECT gpkgCreateBaseTables()")
        except:
            print("Nie udało sie 'SELECT gpkgCreateBaseTables()'")
            
    def GetDatabase(self,name=None):
        self.tables={}
        if NOQGIS:
            self.name=name
            self.con=sqlite3.connect(self.name)
        else:
            FNWrkDB=QFileDialog.getOpenFileName(None,caption="Choose file",
                directory=os.path.expanduser("~"),filter="(*.gpkg)",
                options=QFileDialog.DontConfirmOverwrite
                )
            self.name=FNWrkDB[0]
            self.con=spatialite_connect(self.name)
        try:
            self.con.execute("SELECT AutoGPKGStart()")
        except:
            print("Nie udało sie 'SELECT AutoGPKGStart()'")

    def __getattr__(self,attribute):
        if attribute == "GetProject":
            return self
        if attribute == "GetFileName":
            return self
        if attribute == "GetName":
            return self.name
        if attribute == "ClearMsg":
            self.progress.reset()
            self.progress=None
    def Exists(self, name):
        return (self.con.execute("SELECT count(*) FROM sqlite_master WHERE name='%s' AND type=='table'"%name).fetchone()[0]>0)
    
    def _cancel(self):
        self.progress.reset()
    def SetShowStatus(self,b):
        if b :
            if not self.progress:
                self.progress = QProgressDialog("Computing...", "Cancel", 0, 100)
                self.progress.show()
                self.progress.setWindowModality(Qt.ApplicationModal)

                self.progress.setAutoClose(True)
                self.progress.canceled.connect(self._cancel)
            
    def ShowMsg(self,msg):
        self.progress.setLabelText(msg)
    def SetStatus(self,prg):
        self.progress.setValue(int(prg))
        return not self.progress.wasCanceled()

class MyMsgBox(object):

    def ListAsString(self,lst,text,title):
        indexed_items={str(i):i for i in lst}
        if NOQGIS:
            print(title)
            print(text)
            print(indexed_items.keys())
            return indexed_items[indexed_items.keys()[int(input())]]
        item,ok = QInputDialog.getItem(None,title,text,indexed_items.keys(),0,False)
        return indexed_items[item]
    def Warning(self,text,title):
        if NOQGIS:
            print(title)
            print(text)
            return
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(title)
        msg.setInformativeText(text)
        msg.setStandardButtons( QMessageBox.Ok )
        return msg.exec_()
    def Error(self,text,title):
        if NOQGIS:
            print(title)
            print(text)
            return
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Error)
        msg.setText(title)
        msg.setInformativeText(text)
        msg.setStandardButtons( QMessageBox.Ok )
        return msg.exec_()
    def Info(self,text,title):
        if NOQGIS:
            print(title)
            print(text)
            return
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(title)
        msg.setInformativeText(text)
        msg.setStandardButtons( QMessageBox.Ok )
        return msg.exec_()
    
    def YesNo(self,text,title,default):
        if NOQGIS:
            print(title)
            print(text)
            return bool(input())
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(title)
        msg.setInformativeText(text)
        msg.setStandardButtons( QMessageBox.No | QMessageBox.Yes )
        return msg.exec_()==QMessageBox.Yes
    def Input(self,text,title,default):
        return AvVar(self.MultiInput(text,title,[""],[default])[0])
    def MultiInput(self,text,title,labels,defaults):
        outputs=AvList([])
        for (l,d) in zip(labels,defaults):
            if (type(d)==AvInt) or (type(d)==int):
                if NOQGIS:
                    v=int(input())
                    ok=True
                else:
                    v,ok= QInputDialog.getInt(None,title,text+'\n'+l,value=d)
                if (not ok):
                    return
                outputs.append(v)
            elif (type(d)==AvStr) or (type(d)==str):
                if NOQGIS:
                    v=str(input())
                    ok=True
                else:
                    v,ok= QInputDialog.getText(None,title,text+'\n'+l,text=d)
                if (not ok):
                    return
                outputs.append(v)
            else:    
                if NOQGIS:
                    v=float(input())
                    ok=True
                else:
                    v,ok= QInputDialog.getDouble(None,title,text+'\n'+l ,value=d ,decimals=2)
                if (not ok):
                    return
                outputs.append(v)
        return outputs

class MyField(object):
    def __init__(self,name,db_type=None,py_type=None):
        self.name:str=str(name)
        self.db_type=db_type
        self.py_type=py_type
    def toDBdeclaration(self):
        return self.name+' '+self.db_type
    def SetVisible(self,_):
        pass    
    def __getattr__(self,attribute):
        if attribute=="GetName":
            return AvStr(self.name)
    def __str__(self) -> str:
        return self.name
    def __repr__(self):
        return "Field<"+self.name+">"

class MyFieldCreator(object):
    DECIMAL=1
    CHAR=2
    BYTE=3
    def __init__(self):
        pass
    def Make(self,name,type, major,minor):
        if type==self.DECIMAL and minor==0:
            return MyField(name,'INTEGER',int)
        if type==self.DECIMAL and minor>0:
            return MyField(name,'REAL',float)
        if type==self.CHAR :
            return MyField(name,'TEXT',str)
        if type==self.BYTE :
            return MyField(name,'int',int)

class MyTable(object):
    def __init__(self,av,vtable):
        self.av=av
        self.vtable=vtable

    def SetName(self,name):
        ## probably inset
        if NOQGIS:
            print("Name Not set")
            return
    def __getattr__(self, attribute):
        if attribute=="GetVtab" or attribute=="GetVTab":
            return self.vtable
        
class TableMaker(object):
    def __init__(self,av):
        self.av=av
    def MakeNew(self,vTableName, cls):
        q="DROP TABLE IF EXISTS %s"%vTableName
        self.av.con.execute(q)
        q="CREATE TABLE %s (ID INTEGER PRIMARY KEY)"%vTableName
        self.av.con.execute(q)
        vt=VTable(vTableName,self.av,[MyField("ID")])
        q='DELETE FROM gpkg_contents WHERE table_name=?'
        self.av.con.execute(q,(vTableName,))
        q='INSERT INTO gpkg_contents values (?,"attributes",?,NULL,?,NULL,NULL,NULL,NULL,0)' 
        self.av.con.execute(q,(vTableName,vTableName,datetime.now()))        
        self.av.con.commit()
        
        return vt
    def Make(self,vTable: VTable):
        return MyTable(self.av,vTable)
    
MsgBox=MyMsgBox()
Field=MyFieldCreator()
av=Av()
Table=TableMaker(av)
VTab=Table
File=av

##########################################################################
# Regular expressions to replace Avenue code to Python code
####################################################################
#'<<>>#
#  <<>>    
#0\.\.\((.*)-1\)<<>>AvIter(range($1)):
#for each<<>>for
#if(.*)=(.*)<<>>if$1==$2
#<><<>>!=
#then$<<>>:
#\+\+<<>>+
#\{(.*)\}<<>>AvList([$1])
#else<<>>else:
#(for.*(?<!:))\s*$<<>>$1:
##FIELD_<<>>Field.
####UWAGA:
#in\s(.*)\.\.(.*):<<>>in range($1,($2)+1):
#File\.<<>>av.
#IsNumber\.Not<<>>IsNotNumber
#(".*")\.AsPattern<<>>av.AsPattern($1)
#(?<![a-zA-Z0-9_"])(_[0-9a-zA-Z_]*)<<>>self.$1
#FALSE<<>>False
#BREAK<<>>break