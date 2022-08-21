import uuid
import time

# 用来设置item的uuid
def getUUID():
    UUID = uuid.uuid3(uuid.NAMESPACE_OID, str(time.time()))
    return str(UUID)


# 用来设置item的对齐方式



# 用来设置属性窗口中的对齐按钮
def setAlignBtnEnabled(hAlignBtnList, vAlignBtnList, alignment):
    for btn in hAlignBtnList:
        btn.setEnabled(True)
    for btn in vAlignBtnList:
        btn.setEnabled(True)

    alignLeftBtn = hAlignBtnList[0]
    alignHCenterBtn = hAlignBtnList[1]
    alignRightBtn = hAlignBtnList[2]
    alignTopBtn = vAlignBtnList[0]
    alignVCenterBtn = vAlignBtnList[1]
    alignBottomBtn = vAlignBtnList[2]

    # 从场景中发过来对齐方式肯定是水平和垂直两个方向上一起的
    if alignment == 33:
        alignLeftBtn.setEnabled(False)
        alignTopBtn.setEnabled(False)
    elif alignment == 65:
        alignLeftBtn.setEnabled(False)
        alignBottomBtn.setEnabled(False)
    elif alignment == 129:
        alignLeftBtn.setEnabled(False)
        alignVCenterBtn.setEnabled(False)
    elif alignment == 34:
        alignRightBtn.setEnabled(False)
        alignTopBtn.setEnabled(False)
    elif alignment == 66:
        alignRightBtn.setEnabled(False)
        alignBottomBtn.setEnabled(False)
    elif alignment == 130:
        alignRightBtn.setEnabled(False)
        alignVCenterBtn.setEnabled(False)
    elif alignment == 36:
        alignHCenterBtn.setEnabled(False)
        alignTopBtn.setEnabled(False)
    elif alignment == 68:
        alignHCenterBtn.setEnabled(False)
        alignBottomBtn.setEnabled(False)
    elif alignment == 132:
        alignHCenterBtn.setEnabled(False)
        alignVCenterBtn.setEnabled(False)