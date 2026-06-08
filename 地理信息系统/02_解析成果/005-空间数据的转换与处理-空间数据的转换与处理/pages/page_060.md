# 空间数据的转换与处理 — 第 60 页

> 来源: 005-空间数据的转换与处理-空间数据的转换与处理.pdf
> 页码: 60
> OCR置信: 96.7%

![page 60](../page_060.jpg)

>投影转化 矢量数据（Feature）

#### Project 口
Input Dataset or Feature Class GeographicTransformation(optional)
polygonInput Coordinate System (optional) Thismethodcanbe usedforconvertingdatabetweentwoGCS_WGS_1984 geographic coordinate systems or datums.This optionalparametermayberequiredif theinputandoutputOutput Dataset or Feature Class coordinate systemshave different datum.
E:\GIS_Example\Line_p.shpOutput Coordinate System Thetool automaticallyselectsadefault transformation.
You canselectadifferent transformationfromthedrop-
GCS_China_Geodetic_Coordinate_System_2000 downlist.Transformationsarebi-directional.ForexampleVertical(optional) ifconvertingdatafromWGS1984toNAD1927,youcanpickatransformation calledNAD_1927_to_WGS_1984_3.
GeographicTransformation (optional) and thetool will apply it correctly.
Theparameterprovidesadrop-down listofvalidtransformation methods.See the usage tipsforfurtherinformation onhowtoselectoneormore appropriatetransformations.
Preserve Shape (optional)
Maximum Offset Deviation (optional)
UnknownOK Cancel Environments... <<HideHelp Tool Help
