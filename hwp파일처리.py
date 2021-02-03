#from 공정위 import *
import os
import olefile
import re
from collections import OrderedDict
import win32com.client as win32
import pandas as pd
import numpy as np
import fnmatch
import win32api
from pandas.io.clipboard import clipboard_get
def GetTableCellAddr():
    if not hwp.CellShape:  # 표 안에 있을 때만 CellShape 오브젝트를 리턴하니까
        raise AttributeError("현재 캐럿이 표 안에 있지 않습니다.")
    return hwp.KeyIndicator()[-1][1:].split(")")[0]

def SetTableCellAddr(addr):
    init_addr = hwp.KeyIndicator()[-1][1:].split(")")[0]  # 함수를 실행할 때의 주소를 기억.
    if not hwp.CellShape:  # 표 안에 있을 때만 CellShape 오브젝트를 리턴함
        raise AttributeError("현재 캐럿이 표 안에 있지 않습니다.")
    if addr == hwp.KeyIndicator()[-1][1:].split(")")[0]:  # 시작하자 마자 해당 주소라면
        return  # 바로 종료
    hwp.Run("CloseEx")  # 그렇지 않다면 표 밖으로 나가서
    hwp.FindCtrl()  # 표를 선택한 후
    hwp.Run("ShapeObjTableSelCell")  # 표의 첫 번째 셀로 이동함(A1으로 이동하는 확실한 방법 & 셀선택모드)
    while True:
        current_addr = hwp.KeyIndicator()[-1][1:].split(")")[0]  # 현재 주소를 기억해둠
        hwp.Run("TableRightCell")  # 우측으로 한 칸 이동(우측끝일 때는 아래 행 첫 번째 열로)
        if current_addr == hwp.KeyIndicator()[-1][1:].split(")")[0]:  # 이동했는데 주소가 바뀌지 않으면?(표 끝 도착)
            # == 한 바퀴 돌았는데도 목표 셀주소가 안 나타났다면?(== addr이 표 범위를 벗어난 경우일 것)
            SetTableCellAddr(init_addr)  # 최초에 저장해둔 init_addr로 돌려놓고
            hwp.Run("Cancel")  # 선택모드 해제
            raise AttributeError("입력한 셀주소가 현재 표의 범위를 벗어납니다.")
        if addr == hwp.KeyIndicator()[-1][1:].split(")")[0]:  # 목표 셀주소에 도착했다면?
            return  # 함수 종료

def 문자열사이공백(string,n=0,m=None):
    strings = [i for i in string]
    if n is None:
        a = f",{m}"
    elif m is None:
        a = f"{n},"
    else:
        a = f"{n},{m}"
    n,m= 1,3
    a = r"\s{" + a +"}"
    return a.join(strings)

dir1=os.getcwd()+"\\"+"금감원_file"+"\\"
filename=fnmatch.filter(os.listdir("금감원_file"),'*.hwp')

hwp = win32.gencache.EnsureDispatch("HWPFrame.HwpObject")
hwp.XHwpWindows.Item(0).Visible = True
hwp.RegisterModule("FilePathCheckDLL","FilePathCheckerModule")

data_all = []
filter_=["회사명 등","지적사항","조치"]
filter_re = [문자열사이공백(i) for i in filter_]
for file in filename:
    pass
    hwp.Open(dir1+file, "HWP", "forceopen:true")
    hwp.HAction.GetDefault("RepeatFind", hwp.HParameterSet.HFindReplace.HSet);
    ctrlcode = hwp.HeadCtrl
    data_parent = []
    while ctrlcode is not None:
        if ctrlcode.CtrlID == "tbl":
            hwp.SetPosBySet(ctrlcode.GetAnchorPos(0))
            hwp.FindCtrl()
            hwp.Run("ShapeObjTableSelCell")
            hwp.Run("TableCellBlockExtend")
            hwp.Run("TableCellBlockExtend")
            hwp.Run("Copy")
            a = clipboard_get()
            if all([re.compile(i).search(a) for i in filter_re]):
                num = 1
                dat = {i: "" for i in filter_}
                posibl = {i: True for i in ["A", "B", "C"]}
                while True:
                    num +=1
                    for 위치,항목 in zip(["A","B","C"],filter_):
                        try:
                            SetTableCellAddr(f"{위치}{num}")
                            hwp.Run("Copy")
                            sub_dat = clipboard_get()
                            sub_dat = re.compile(r'\s+').sub(" ",sub_dat)
                            dat[항목] += " " + sub_dat
                        except:
                            posibl[위치] = False
                            hwp.SetPosBySet(ctrlcode.GetAnchorPos(0))
                            hwp.FindCtrl()
                            hwp.Run("ShapeObjTableSelCell")
                    if not any(posibl.values()):
                        break
                data_parent.append(dat)
            ctrlcode = ctrlcode.Next
        else:
            ctrlcode = ctrlcode.Next
    if len(data_parent) >0 :
        data_all.append(data_parent)
a = [pd.DataFrame(i) for i in data_all]
a = pd.concat(a)
a = a.reset_index()
a = a.rename(columns = {"index":"origin_index"})
a[filter_].to_excel("금감원파일1차정리.xlsx")
a.to_excel("금감원파일1차정리.xlsx")
