# 空间数据的可视化表达 — 第 98 页

> 来源: 006-空间数据的可视化表达-空间数据的可视化表达.pdf
> 页码: 98
> OCR置信: 92.4%

![page 98](../page_098.jpg)


#### 图层/数据选择
>安徽省道路数据，高速、城市主干道、步行道..
SelectbyAttributes X Table

#### 图
Entera WHEREclause to selectrecords inthe table window. 安徽省立方数据学社 XMethod: Create anew selection bridge tunnel felass_cn type
"oneway" F 居住区道路 城市支路
"bpuq.. F 第三级道路 城市次干路

#### F 居住区道路 城市支路
"tunnel" F 居住区道路 第三级道路 城市次干路 城市支路
"fclass_cn" F F 商速公路 高架及快速路
"type" F 商速公路 高架及快速路

#### F 高速公路 高架及快速路
<> Like 干道连接 F 高速公路 高架及快速路
高速公路 F 商速公路 城市次干路 高架及快速路
>= And 高速公路连接 F 第三级道路 第三级道路 城市次干路
<= Or 公车专用道 F 第三级道路 城市次干路
居住区道路 F 第三级道路 城市次干路
马道 F 高速公路 高架及快速路
() Not F 高速公路 高菜及快速路

#### F 商速公路 高架及快速路
In Null Get UniqueValuesGoTo: F 高速公路 高架及快速路
SELECT·FROM安徽省_立方数据学社WHERE： F 商速公路 高莱及快速路

#### F 高速公路 商架及快速路
“fclass_cn"=高速公路 F 第三级道路 城市次干路
F 第三级道路 城市次干路 商菜及快速路

#### F 高速公路
F 第三级道路 高速公路 高架及快速路

#### 城市次干路

#### 第三级道路 城市次干路

#### F 干道连接 高架及快速路
Clear Vernfy Help Load.... Save...
Apply Close 14 (0outof141566Selected)

#### 安徽省立方数据学社
