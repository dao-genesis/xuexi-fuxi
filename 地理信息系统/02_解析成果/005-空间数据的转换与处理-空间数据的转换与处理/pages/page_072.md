# 空间数据的转换与处理 — 第 72 页

> 来源: 005-空间数据的转换与处理-空间数据的转换与处理.pdf
> 页码: 72
> OCR置信: 96.2%

![page 72](../page_072.jpg)


### 4.1数据格式转化

#### >矢量转栅格
Polygon toRasterInput Features Cellassignmenttype(optional)
Value field Themethodtodeterminehowthecellwillbeassignedavaluewhenmorethanonefeaturefallswithinacell.
Output Raster Dataset CELL_CENTER-Thepolygonthatoverlapsthecenterof thecellyields the attribute toassigntoCell assigmment type (optional) the cell.
CELL_CENTER MAXIMUMAREA-ThesinglefeaturewiththePriority field (optional) largestareawithinthecellyieldstheattributetoNON assign to the cell.
Cellsize(optional) MAXIMUM_COMBINED_AREA-Ifthereismorethanone featureinacellwiththesamevalue,theareasofthesefeatureswillbecombined.Thecellwill determinethevaluetoassigntothecell.
OK Cancel Environments... <<HideHelp Tool Help
