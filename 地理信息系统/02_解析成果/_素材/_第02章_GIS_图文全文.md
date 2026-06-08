# 第二章 · GIS · 图文全文

> 教师: 黄源生 · 学期: 2026春
> 章节: 第二章 GIS
> 含 2 个PDF

---

## PDF: 空间数据-知识点回顾
> 页数: 166

### 第 1 页

![page 1](003-GIS-空间数据-知识点回顾/page_001.jpg)

知识点回顾
如何更改MIXD文件中数据框/层名称？
在需要更名的数据层上单击左键，选定数据层，
再次单击左键，数据层名称进入可编辑状态
输入新名称。
选定数据层一图层属性 主（Properties）一常规
（General）→图层名称（LayerName）
不会修改Windows系统下文件名称！

### 第 2 页

![page 2](003-GIS-空间数据-知识点回顾/page_002.jpg)

知识点回顾
MXD文件中调整数据层顺序的原则？
数据层在内容表中的排序，直接影响输出地图
中的表达效果。
(1)按点、线、面要素类型依次由上至下排列;
(2)按要素重要程度的高低依次由上至下排列;
(3)按要素线划的细粗依次由下至上排列;
(4)按要素色彩的浓淡程度依次由下至上排列。
清晰直观的地图表达，不能遮挡主要要素！！！
内容列表模式：按绘制顺序列出

### 第 3 页

![page 3](003-GIS-空间数据-知识点回顾/page_003.jpg)

知识点回顾
MXD文件中如何复制、删除数据层？
Table Of Contents 口X
①在内容列表中选
中需复制的数据层 日 LayersRiverNetCounty
（按Ctrl或Shift选择
WaterArel
多个数据层); CopyHefeiRSimage Remove
②点击鼠标右键； GroupTurn On
③在弹出快捷菜单 TurnOffCreate LayerPackage...
中选择复杂(copy)；
Zoom To LayersVisibleScale Range

### 第 4 页

![page 4](003-GIS-空间数据-知识点回顾/page_004.jpg)

知识点回顾
MXD文件中如何复制、删除数据层？
④选中数据层需要 Table OfContents 口X
。三
复杂到的数据框；
TableOf Contents5点击鼠标右键：
6在弹出快捷菜单 LayersRiverN
中选择粘贴(Past)。 CopyRiverN
选中图层→点击鼠 WaterA Remove
+ County Group
标右键→删除
+ City Turn On
(remove)。

### 第 5 页

![page 5](003-GIS-空间数据-知识点回顾/page_005.jpg)

知识点回顾
文件连接 （FolderConnections）如何操作？
AddDataLookin: Home-Documents\ArcGISHome-Documents\ArcGISFolderConnections ments\ArcGISToolboxes ctionsDatabaseServers tToFolder...
Database ConnectionsGISServersMyHostedServices DATAReady-To-UseServicesName: Add nnectionsShow of type: Datasets,Layers andResults CancelervicesleServicesTracking Connections

### 第 6 页

![page 6](003-GIS-空间数据-知识点回顾/page_006.jpg)

知识点回顾
新建、删除矢量文件/文件夹如何操作？
Catalog 口x
←价鞋
选中目标文件 Location: ArcGIS_3rdHome-Documents\ArcGIS
夹→点击鼠标 日 FolderConnections
$RECYCLE.BIN Folder
右键→新建 ArcGIS3r Copy
+ Desktop File Geodatabase
+ document Paste PersonalGeodatabasedownload DeleteGIS_map Rename Database Connection...
NoteExpr ArcGiSServer Connection...
选中目标文件 Notes RefreshIdd Layer...
Report New GroupLayer
夹→点击鼠标 source_co Item Description... PythonToolboxSubject Properties...
Shapefile....
右键→删除 Turn Feature Clas...
ToolboxdBASETableLAS DatasetAddressLocator..
Composite AddressLocator..
XMLDocument

### 第 7 页

![page 7](003-GIS-空间数据-知识点回顾/page_007.jpg)

知识点回顾
ArcGIS中如何使用在线地图？
AddWMTSServer
选择“GISServers"
Examples:   双击“AddWMTSVersion: Default versionCustom Parameters Server";
Parameter Value
设置“URL";
Server LayersGetLayers 点击“get layers"；
-Layers LimgTle Matrix Sets 确定OK
白-c1:295829355.4545662:147914677.7272833:73957338.8636414:36978669.4318215:18489334.7159106:9244667.3579557:4622333.6789788:2311166.8394899:1155583.41974410:577791.709872
Account(Optional)
User:
Password: SavePasswordOK Cancel

### 第 8 页

![page 8](003-GIS-空间数据-知识点回顾/page_008.jpg)

知识点回顾
Geoprocessing地理处理框架中环境设置有什
么作用？
Environment Settings
环境设置会影响工 Workspace
具和命令的运行； xYResolutionandToleranceMValues
在应用程序级别或 ZValuesGeodatabase
运行工具时设置； GeodatabaseAdvancedFieldsRandom Numbers
应用程序级别设置 CartographyCoverage
与地图文档一起保 RasterAnalysisRasterStorage
存。 TerrainDatasetOK Cancel ShowHelp>>

### 第 9 页

![page 9](003-GIS-空间数据-知识点回顾/page_009.jpg)

1.3Geoprocessing地理处理框架
>ArcToolbox内容简介 环境设置
Environment Settings x
环境设置会影响工 Workspace
具和命令的运行； xYResolutionandToleranceMValues
在应用程序级别或 ZValuesGeodatabase
运行工具时设置； GeodatabaseAdvancedFieldsRandomNumbers
应用程序级别设置 CartographyCoverage
与地图文档一起保 RasterAnalysisRasterStorage
存。 TerrainDatasetOK Cancel Show Help>>

### 第 10 页

![page 10](003-GIS-空间数据-知识点回顾/page_010.jpg)

1.3Geoprocessing地理处理框架
>ArcToolbox内容简介 环境设置
Geoprocessing Customize Windows Intersect XBuffer InputFeaturesIntersect Features Ra...
Union GeologyWatershedsMergeDissolveSearchForToolsArcToolbox OutputFeature ClassEnvironments... C:gisclass\mgisdataRapidcity\chap6pptdata.gdb\geolwatsResults JoinAttributes(optional)
ModelBuilder xYTolerance(optional)
Python OutputType(optional)
INPUTOK Cancel Environments... Show Help>>
Geoprocessing Options...
影响所有工具和菜单 影响一个工具的一次执行

### 第 11 页

![page 11](003-GIS-空间数据-知识点回顾/page_011.jpg)

空间数据的采集与组织
NationalView

### 第 12 页

![page 12](003-GIS-空间数据-知识点回顾/page_012.jpg)

本章内容
一、矢量数据组织
二、栅格数据组织
三、创建地理数据库
四、数据采集
五、数据编辑

### 第 13 页

![page 13](003-GIS-空间数据-知识点回顾/page_013.jpg)

》空间数据采集是指将现有的地图、外业观
测成果、航空相片、遥感图像、文本资料
等转成计算机可以识别处理的数字形式
>数据采集可分为属性数据采集和图形数据
采集。
表示空间实体的位置、形状、
地理空间数据
大小及其分布特征的数据。
地理
数据
表示空间实体的属性特征、
非地理空间数据
是对地理空间数据的说明。

### 第 14 页

![page 14](003-GIS-空间数据-知识点回顾/page_014.jpg)

》空间数据采集是指将现有的地图、外业观
测成果、航空相片、遥感图像、文本资料
等转成计算机可以识别处理的数字形式
>数据采集可分为属性数据采集和图形数据
采集。
>数据组织就是按照一定的方式和规则对数
据进行归并、存储、处理的过程。数据组
织的好坏，直接影响到GIS 的性能。

### 第 15 页

![page 15](003-GIS-空间数据-知识点回顾/page_015.jpg)

> *此页无文字*

### 第 16 页

![page 16](003-GIS-空间数据-知识点回顾/page_016.jpg)

DH JX1

### 第 17 页

![page 17](003-GIS-空间数据-知识点回顾/page_017.jpg)

★ TSGTSG DH

### 第 18 页

![page 18](003-GIS-空间数据-知识点回顾/page_018.jpg)

》空间数据采集是指将现有的地图、外业观
测成果、航空相片、遥感图像、文本资料
等转成计算机可以识别处理的数字形式
>数据采集可分为属性数据采集和图形数据
采集。
>数据组织就是按照一定的方式和规则对数
据进行归并、存储、处理的过程。数据组
织的好坏，直接影响到GIS 的性能。

### 第 19 页

![page 19](003-GIS-空间数据-知识点回顾/page_019.jpg)

>GIS中主要有矢量、栅格、点云和地理数据
库（geodatabase）四种数据组织方式。
矢量数据组织包括点、线、面数据以及拓扑关系
的组织。
栅格数据组织用于管理影像图片等不同格式的栅
格数据。
ArcGIS也可以加载和处理摄影测量或激光雷达
获得的点云数据
地理数据库是ArcGIS数据模型发展的第三代产物，
它是面向对象的数据模型，能够表示要素的自然
行为和要素之间的关系。

### 第 20 页

![page 20](003-GIS-空间数据-知识点回顾/page_020.jpg)

地理空间数据的基本结构
地理空间对象：GIS处理的客体，是现实世界中客观存在的
实体或现象
空间对象可抽象为点、线、面、体等多种数据类型及其组合
线一维 点零维
空间对象
面二维 体三维 时间四维

### 第 21 页

![page 21](003-GIS-空间数据-知识点回顾/page_021.jpg)

地理空间数据的基本结构
地理空间实体
地理空间实体是对复杂地理事物和现象进行简化抽象
得到的结果，简称空间实体，它们的一个典型特征是
与一定的地理空间位置有关，都具有一定的几何形态
分布状况以及彼此之间的相互关系
地理空间实体包括点、线、面和体等多种类型，是地
理信息系统（GIS）中用于表示现实世界中地理现象的
基本单位。

### 第 22 页

![page 22](003-GIS-空间数据-知识点回顾/page_022.jpg)

地理空间数据的基本结构
在GIS中，地理数据是表示地理位置，分布特点的自然现象和社
会现象的诸要素文件。它包括自然地理数据和社会经济数据
表示空间实体的位置、形状、
地理空间数据
大小及其分布特征的数据。
地理
数据
表示空间实体的属性特征
非地理空间数据
是对地理空间数据的说明。
地理空间数据的特征
空间特征：空 空间物体的几何特征以及拓扑关系
属性特征： 空间对象的属性信息
时间特征：地理空间数据是动态的

### 第 23 页

![page 23](003-GIS-空间数据-知识点回顾/page_023.jpg)

地理空间数据的基本结构
地理空间数据分类
根据数据来源，地理空间数据可分为以下四类：
图形数据 图像数据 实体属性数据 统计数据
数字化的 航空和航 空间实体的专 描述性
数据 天数据 题信息数据 数据
地理空间数据 非地理空间数据
栅格结构
矢量结构

### 第 24 页

![page 24](003-GIS-空间数据-知识点回顾/page_024.jpg)

地理空间数据的基本结构
图形数据的表达
以单一的坐标来表示。
(x1, y1)
点
（“代码"，1，X1，y1)
(x2, y2) 以多个坐标来表示。
线 （“代码"，3，X1，y1，X2，y2
(x3, y3)
(x1, y1) X3, y3)
(x2, y2) 以多个坐标来表示，且最后一个
(x3, y3) 坐标必须与第一个坐标重合。
面
（"代码"，4，X1，y1，X2，y2
(x1, y1) (x4, y4)
X3, y3， X4, y4, X1， y1)

### 第 25 页

![page 25](003-GIS-空间数据-知识点回顾/page_025.jpg)

地理空间数据的基本结构
图形数据的组织
点 线 面 属性表
Pt.ID X Ln.ID Pt.1 Pt.2 Pol.ID Ln.ID Pol.ID Attrib.
12345 24.5 27.4 36 73839 14628 328101 4441515 3835292842 1415167718 104.224.8 24.1 100.127.8 22.5 105.730.1 29.9 102.714.2 30.1 106.1
... ... ... ... ... .*. ... ... ...

### 第 26 页

![page 26](003-GIS-空间数据-知识点回顾/page_026.jpg)

地理空间数据的基本结构
图形数据的拓扑结构
邻接 相交 相离 包含 重合
点一点
点一线
点一面
线一线
线一面
面一面

### 第 27 页

![page 27](003-GIS-空间数据-知识点回顾/page_027.jpg)

地理空间数据的基本结构
图像数据的特征
图像数据的最小单元为像元或像素，像元或像素的数值
可用于描述客观世界中存在的现象。
图像数据的实质是像元的阵列，每个像元由行列号确定
其位置，且具有实体属性的编码值。
图像数据是地表一定面积内数据的近似、离散化的标识
图像数据的表现 图像数据的存储结构

### 第 28 页

![page 28](003-GIS-空间数据-知识点回顾/page_028.jpg)

地理空间数据的基本结构
图像数据的表达

### 第 29 页

![page 29](003-GIS-空间数据-知识点回顾/page_029.jpg)

地理空间数据的基本结构
图像数据的表达
点：表示单个像元
值
线：在一定方向上链
接成串的相邻像元的
集合
面：聚集在一起的
相邻像元的集合
层：表示一种地理属性或同一属性的不同特征

### 第 30 页

![page 30](003-GIS-空间数据-知识点回顾/page_030.jpg)

地理空间数据的基本结构
图像数据的特征 分辨率
像元大小决定了影像数据所表达对象的详细程度，像元
一般是用相同宽度和高度的方格表示。一个面对象可以
采用不同像元大小的像素数据表示，像元越小，则表达
越为精细，占用存储空间越大
像元（像素）
高度
宽度

### 第 31 页

![page 31](003-GIS-空间数据-知识点回顾/page_031.jpg)

地理空间数据的基本结构
图像数据的特征 分辨率
像素所代表地面范围的大小，或地面物体能分辨的最小单元
高空间分辨率 低空间分辨率
地物A 地物B
距离d1<分辨率
实际地物情况 不可分辨出两个地物 遥感图像上显示
地物C 地物D
距离d2>分辨率
实际地物情况 可以分辨出两个地物
遥感图像上显示

### 第 32 页

![page 32](003-GIS-空间数据-知识点回顾/page_032.jpg)

第一节
矢量数据组织

### 第 33 页

![page 33](003-GIS-空间数据-知识点回顾/page_033.jpg)

矢量数据结构概述
》矢量数据是指通过记录实体坐标及其关系，尽可
能精确地表示点、线、面等地理实体的空间位置
和形状，坐标空间为连续空间，允许任意位置、
长度和面积的精确定义。
Foresl0005S59561000 581000

### 第 34 页

![page 34](003-GIS-空间数据-知识点回顾/page_034.jpg)

一、矢量数据组织
矢量数据具有数据量少、数据精确的特点；
ArcGIS中矢量数据组织：
》基于文件系统的矢量数据组织；
》基于地理数据库的数据组织

### 第 35 页

![page 35](003-GIS-空间数据-知识点回顾/page_035.jpg)

一、矢量数据组织
矢量数据结构直接以几何空间坐标为基础，
记录采样点坐标，通过这种数据组织方式，
可以得到精美的地图：
可以对复杂数据以最小的数据冗余进行存贮、
数据精度高、存储空间小等特点，是一种高
效的图形数据结构。
ArcGIS中矢量数据组织方式：
》基于文件系统的矢量数据组织；
》基于地理数据库的数据组织

### 第 36 页

![page 36](003-GIS-空间数据-知识点回顾/page_036.jpg)

一、矢量数据组织
基于文件系统的矢量数据
>Windows文件系统下的数据组织方式，
ArcGIS有Shapefile和Coverage两种格式。
/Shapefile一GIS软件界的一个开放标准，易操
作、规范性、可与其他数据转换一应用广泛。
／Shapefile是一种用于存储地理要素的几何位置
和属性信息的非拓扑简单格式。
（可通过点、线、面来表示。 B
／Shapefile通常由多个文件组成！！！

### 第 37 页

![page 37](003-GIS-空间数据-知识点回顾/page_037.jpg)

一、矢量数据组织
基于文件系统的矢量数据
rivernet.cpg waterstation.cpg Windows系统下
rivernet.dbf waterstation.dbf
的Shapefile文件
rivernet.prj water_station.prjrivernet.sbn waterstation.shprivernet.sbx waterstation.shp.xml rivernet.shprivernet.shpwaterstation.shx Urumchi.shprivernet.shp.xmlXinjiang.cpgrivernet.shx waterstation.shpXinjiang.dbfUrumchi.cpgXinjiang.prj Xinjiang.shpUrumchi.dbfUrumchi.prj Xinjiang.sbnXinjiang.sbx ArcGIS软件下
Urumchi.sbnUrumchi.sbx Xinjiang.shp
的Shapefile文件
Urumchi.shp Xinjiang.shp.xmlUrumchi.shx Xinjiang.shx

### 第 38 页

![page 38](003-GIS-空间数据-知识点回顾/page_038.jpg)

一、矢量数据组织
基于文件系统的矢量数据
》(1).shp：用于存储要素几何的主文件;
(2).shx：用于存储要素几何索引的索引文件;
(3).dbf：用于存储要素属性信息的dBASE表;
(4).sbn和.sbx：用于存储要素空间索引的文件；
(5).prj：用于存储坐标系信息的文件;
》(6).xml：元数据，存储Shapefile的相关信息。
/各文件共同组成Shapefile，其前缀必须相同
并且各文件必须在同一目录下。

### 第 39 页

![page 39](003-GIS-空间数据-知识点回顾/page_039.jpg)

一、矢量数据组织
··国
省级行政区
Teri_Indus Total_Col1 35 Urban_to_T Vocation 5230000 DZM NAMS 黑龙江 Heilongjiang NAMSSN35.9 124 18 1650000 新蓬 Sinkiang37.5 32.43 1640000 3140000 山园 宁夏 Ningxia Shanxi45.9 35.5 0540000 Tibet30.4 38 13410000 4370000 山东 河南 Shandong36.3 41.49 17 320000 Jiangsu Henan33.2 40.22 27.81 14420000 13340000 安徽 湖北 Anhui Hubei36.3 48.67 8330000 浙江 Zhejiang39.1 40.8 27.67 29. 13430000 4360000 江西 Jiangxi Hunan34.6 23.36 75 1 530000 云南 湖商 Yunnan40 41.57 23.87 4520000 350000 贵州 福注 Fujian Cuizhou37.2 28.15 5450000 8 广西 Guangxi39.3 40. 11 55 16440000 0460000 广东 海南 Guangdong Hainan34.2 49.68 4220000 吉林 Jilin45.5 39 54.24 9210000 3120000 辽宁 天津 Liaoning Tianjing42.1 35.6 18 34.76 1630000 青海 Qinghai24.01 32.26 2620000 3610000 甘肃 陕园 Shanxi Gansu35.3 1 42.68 4150000 内乘古 Inner Mongolia33.5 40.8 26.08 33.09 2500000 兰庆 周北 Chongqing909 88.31 11 6310000 130000 上海 Hebei Shanghai58.3 77.54 0710000 4110000 北京 台湾 Beijing Taiwanoo 0 0810000 香港 HongKong34 42 26.69 0 0820000 5510000 四川 澳门 Sichuan Macau
(0out of 34 Selected)
省级行政区

### 第 40 页

![page 40](003-GIS-空间数据-知识点回顾/page_040.jpg)

一、矢量数据组织
基于文件系统的矢量数据 特点
》总的数据量没有大小限制，单张表或者
要素类的大小限制为1TB。
>使用Windows资源管理器可以对数据进
行管理。
》在Windows资源管理器下文件太多，不
容易管理。

### 第 41 页

![page 41](003-GIS-空间数据-知识点回顾/page_041.jpg)

一、矢量数据组织
基于地理数据库的矢量数据
地理数据库是一种面向对象的空间数据模型，
它对地理空间特征的表达更接近我们对现实世
界的认知。
ESRI公司研发的一种采用标准关系数据库的数
据管理模式，是一个为ArcGIS所用的数据框架，
该框架定义了ArcGIS中用到的所有的数据类型
分为个人地理数据库、文件地理数据库和企业
级地理数据库。

### 第 42 页

![page 42](003-GIS-空间数据-知识点回顾/page_042.jpg)

一、矢量数据组织
个人数据库（PersonalGeodatabase）
MicrosoftAccess数据库（.mdb）；
数据文件不能超过2GB；
》适用于个人或小规模工作组；
》仅适用于Windows，不可跨平台

### 第 43 页

![page 43](003-GIS-空间数据-知识点回顾/page_043.jpg)

一、矢量数据组织
文件地理数据库（FileGeodatabase）
》一文件夹的形式保存各类型的GIS数据；
>每个数据集在磁盘上都是一个单独的文件夹;
适用于个人或小规模工作组；
每个数据集上限1TB，超大型影像数据集可提升
至256TB；
》跨平台，Windows、Linux。

### 第 44 页

![page 44](003-GIS-空间数据-知识点回顾/page_044.jpg)

一、矢量数据组织
SDE地理数据库（ArcSDEgeodatabase）
》存储为商业的RDBMS（Oracle、SQLServer、
MySQL）;
》适用于多人或大型工作组（企业）；
支持多用户同时编辑文件；
需要RDBMS证书和ArcSED技术支撑；
跨平台，Windows、Linux。

### 第 45 页

![page 45](003-GIS-空间数据-知识点回顾/page_045.jpg)

第二节
栅格数据组织

### 第 46 页

![page 46](003-GIS-空间数据-知识点回顾/page_046.jpg)

二、栅格数据组织
栅格数据结构概述
以规则栅格阵列表示空间对象的
数据结构称为栅格数据结构。阵
列中每个栅格单元上的数值表示
空间对象的属性特征。即栅格阵
列中每个单元的行列号确定位置
属性值表示空间对象的类型、等
级等特征。每个栅格单元只能存
在一个值。

### 第 47 页

![page 47](003-GIS-空间数据-知识点回顾/page_047.jpg)

二、栅格数据组织
栅格数据结构概述
栅格数据结构的显著特点：属性明显，定位隐含，
即数据直接记录属性的指针或属性本身，而所在
位置则根据行列号转换为相应的坐标给出，也就
是说定位是根据数据在数据集中的位置得到的。
>栅格数据的优缺点：
口优点：数据结构简单、数学模拟方便
口缺点：数据量大、难以建立实体间的拓扑关系、
通过改变分辨率而减少数据量时精度和信息量
同时受损等。

### 第 48 页

![page 48](003-GIS-空间数据-知识点回顾/page_048.jpg)

二、栅格数据组织
栅格数据结构概述
》完全栅格数据结构（也称编码）将栅格看作
一个数据矩阵，逐行逐个记录栅格单元的值。
》这是最简单最直接的一种栅格编码方法。通
常这种编码为栅格文件或格网文件，它不采
用任何压缩数据的处理。

### 第 49 页

![page 49](003-GIS-空间数据-知识点回顾/page_049.jpg)

二、栅格数据组织
创建栅格数据
位置：通常由一对有序的行列
3 3 坐标(X，Y)表示
属性：保存各种类型的数据值，
3 3 1 14 3 3 1 1 1 如整数、实数、编码和日期等。
3 3 2 2 14 2 2 2 》某一区域的单元格具有同一属
性。

### 第 50 页

![page 50](003-GIS-空间数据-知识点回顾/page_050.jpg)

二、栅格数据组织
栅格数据结构
Red-green-bluecompositeAttributevalues 255
rangefrom0 to255
ineachbandBand1 Band2
Band3

### 第 51 页

![page 51](003-GIS-空间数据-知识点回顾/page_051.jpg)

矢量数据VS.栅格数据
优点 缺点
>数据结构严密，余度小，数据量小; 数据结构处理算法复杂
空间拓扑关系清晰，易于网络分析； 叠置分析与栅格图组合比较难；
矢量数据
面向对象目标的，不仅能表达属性编码 >数学模拟比较困难；
而且能方便地记录每个自标的具体的 空间分析技术上比较复杂，需要更复
属性描述信息； 杂的软、硬件条件；
能实现图形数据的恢复、更新和综合； >显示与绘图成本比较高。
>图形显示质量好、精度高。
数据结构简单，易于算法实现； 图形数据量大，用大像元减小数据量
栅格数据
空间数据的叠置和组合容易，有利于与 时，精度和信息量受损失；
遥感数据的匹配应用和分析； >难以建立空间网络连接关系；
易执行各类空间分析，地理现象模拟； >投影变化实现困难；
>输出方法快速建议，成本低廉。 图形数据质量低，地图输出不精美。

### 第 52 页

![page 52](003-GIS-空间数据-知识点回顾/page_052.jpg)

第三节
创建地理数据库

### 第 53 页

![page 53](003-GIS-空间数据-知识点回顾/page_053.jpg)

三、创建地理数据库
3.1数据库基础 数据组织方式
数据是信息的具体表达形式。为了表达更有意
义的信息内容，数据必须按一定的方式进行组
织和存储。
数据的 数据库
组织
文件
数据项
记录

### 第 54 页

![page 54](003-GIS-空间数据-知识点回顾/page_054.jpg)

三、创建地理数据库
3.1数据库基础 数据项
》数据项：定义数据的最小单位，是数据记录中
最基本的、不可分的数据单元
》域：数据项的取值范围，可以是数值（整数、
小数）、字符、日期等。
域：{男、女}
姓名 学号 姓别 学院 专业
数据项 张三 20200023 男 生态与环境学院 环境科学
李四 20210123 女 外语学院 英国文学

### 第 55 页

![page 55](003-GIS-空间数据-知识点回顾/page_055.jpg)

三、创建地理数据库
3.1数据库基础 一记录
>记录（record）：由若干相关联的数据项组成，
是关于一个实体的数据总和。
·字段：同类型 ·值：记录反映 ·标识符：标识每
记录的框架。 实体的内容。 个记录的数据项。
标识符/关键字
姓名 学号 姓别 学院 专业 字段
张三 20200023 男 生态与环境学院 环境科学
记录 李四 女 外语学院 英国文学

### 第 56 页

![page 56](003-GIS-空间数据-知识点回顾/page_056.jpg)

三、创建地理数据库
3.1数据库基础 文件
>文件（file）：给定类型记录的全部具体值的集
合，用文件名称标识。
学生基本信息表
姓名 学号 姓别 学院 专业
具体
张三 20200023 男女 生态与环境学院 环境科学
值的
李四 20210123 外语学院 英国文学
集合
文件存储
JMD_M_500.dbf

### 第 57 页

![page 57](003-GIS-空间数据-知识点回顾/page_057.jpg)

三、创建地理数据库
3.1数据库基础 数据组织方式：数据库
>具有特定联系的数据集合体。
》比文件更大的数据组织。
》内部机构是文件的集合，这些文件具有某种直
接的联系，不是孤立的。
姓名 学号 表格（Table)
张三 20232123
数据
数据库 视图（View)
(data)
数据
QL 存储过程（Storedprocedure）
触发器 (Trigger)

### 第 58 页

![page 58](003-GIS-空间数据-知识点回顾/page_058.jpg)

三、创建地理数据库
3.1 数据库基础 数据组织方式：数据库
序号 物品 单价 上月结余 本月领用 本月购入 购入金额 库存 盘点数 差异 备注
1 笔 5 500 200 100 400 -4002 文件央 10 500 150 200 550 -5503 笔 5 500 200 100 400 -4004 文件夹 10 500 150 200 550 -5505 笔 5 500 200 100 400 -4006 文件央 10 500 150 200 550 -5507 笔 5 500 200 100 400 -4008 文件央 10 500 150 200 550 -5509 笔 5 500 200 100 400 -40010 文件夹 10 500 150 200 550 -55011 笔 5 500 200 100 400 -40012 文件央 10 500 150 200 550 -55013 笔 5 500 200 100 400 -40014 文件央 10 500 150 200 550 -55015 笔 5 500 200 100 400 -400

### 第 59 页

![page 59](003-GIS-空间数据-知识点回顾/page_059.jpg)

三、创建地理数据库
3.1数据库基础 数据组织方式：数据库
序 小型建筑 需要安装 不需要安装的 建筑安装 其他费用 预备费 总价值 生产准备
号 表格编号 工程费 的设备费 设备、工器具费 工程费 及开办费
（元） 人民币（元）其中外币（） （元）
IⅢI IV V VI VII VII IX X XI XI

### 第 60 页

![page 60](003-GIS-空间数据-知识点回顾/page_060.jpg)

三、创建地理数据库
3.2空间数据库 数据与数据库
空间数据库（Geodatabase）是某一区域内关于
一定地理要素特征的数据集合，一般是以一系
列特定结构的文件的形式组织在存储介质之上的。
矢量数据
属性数据
影像数据 特定的数
影像数据
据结构
矢量数据
属性数据
数据的有效
结合

### 第 61 页

![page 61](003-GIS-空间数据-知识点回顾/page_061.jpg)

三、创建地理数据库
3.2空间数据库 一主要特征
土地管理
数据集中管理
城市规划
保证不同用户和应
基础地理
用可以共享数据。 交通管理
数据库
数据具有独特性 数据共享方便
数据独立于应用程
楚河
序，提高了数据库
数据库管理 stiet
用于系统的效率和
稳定性。 数据库与应用系统
相互独立

### 第 62 页

![page 62](003-GIS-空间数据-知识点回顾/page_062.jpg)

三、创建地理数据库
3.2空间数据库 主要特征
数据余度小
解决
数据统一定义、组织和存储，集中管理， “数据孤岛”
避免了数据余，提高了数据的一致性 现象
复杂的数据模型
根节点 R1
采用复杂的数据模型组织和管理 层次
兄弟节点 R2 R3 模型
数据是以文件方式的本质区别
R4 R5 叶节点
安全性
设置登录密码和用户权限，拒绝 SQLServer2008R2
非法访问，以确保数据的安全性、 I.S
中
一致性和并发性。

### 第 63 页

![page 63](003-GIS-空间数据-知识点回顾/page_063.jpg)

三、创建地理数据库
3.2创建一个新的地理数据库
>借助ArcCatalog软件或ArcMap软件中
Catalog窗口创建地理数据库。
·本地地理数据库：个人数据库(PersonalGeodatabase)限2GB、文件地理数据库(FileGeodatabase);
·ArcSDE地理数据库：空间数据库连接

### 第 64 页

![page 64](003-GIS-空间数据-知识点回顾/page_064.jpg)

三、创建地理数据库
3.2创建一个新的地理数据库
在Catalog目录中选中文件→新建 FolderFile GeodatabaseCatalog X 一文件数据 Personal GeodatabaseCatalog Catalog ion...
Location: GIS_Example 主
品 《 nection...
+ scratch.gToolbox.t 地理数据库中的组成项包括对象
EFolderConn
一 E:
+ $RECY 类、要素类和要素数据集
ArcGI:
Desktop ArcGIS3rd GISExampledocument 田 Desktop ExampleDB.mdbdownload 田 document Example_DB.gdbGISExample 田 download + GISmap
日 GISExample NoteExpress
+ GIS_map NewPersonal NotesNoteExpress GIS_mapNotes NoteExpress ReportPPT + Notes source_code
+ Report PPT + Subject ssLocator...
Report

### 第 65 页

![page 65](003-GIS-空间数据-知识点回顾/page_065.jpg)

3.2创建一个新的地理数据库
建立要素数据集
在Catalog NewFeature Dataset 新建(New)-
要素数据集 Name: Feature_ExCatalog
←→价 Feature Dataset..
Location: Example_DB.gdbFeature Class...
+ $RECYCLE.BINArcGIS3rd Table...
+ Desktopdocument View...
peojumopGIS_Example Relationship Class...
Example DB.mdbExampleDB.gdb Raster Catalog...
GIS_mapNoteExpress Raster Dataset...
NotesPPT MosaicDataset...
Reportsource_code Schematic Dataset
+ Subject
<上一步（B) 下一页（N）> 取消 Toolbox

### 第 66 页

![page 66](003-GIS-空间数据-知识点回顾/page_066.jpg)

3.2创建一个新的地理数据库
NewFeature Dataset NewFeatureDataset NewFeatureDataset XChoose thecoordinate system that will be use Choose thecoordinate system that will be usec XY ToleranceTheXY tolerance istheminimum distancebetween coordinatesbefore theyareGeographiccoordinate systemsuselatitudear Verticalcoordinate systemsdefine the origin a considered equal.TheXY tolerance isused when evaluating relationshipsmodelof the earth'ssurface.Projected coordi define the positive direction of valuesin order Catalog 口xconversionto transform latitude andlongitudeTypehere to search 七价 >
Typehere tosearch FavoritesFavorites VerticalCoordinateSystems Location: Example_DB.gdbChina GeodeticCoordinateSyster 田 $RECYCLE.BINPCs_Transverse_Mercator 田 ArcGIS3rdWGS1984 DesktopWGS1984WorldMercator 田
GeographicCoordinate Systems 田 documentProjectedCoordinateSystems 田 downloadCurrentcoordinate system: GIS_ExampleNo coordinate system. ExampleDB.mdbCurrentcoordinate system:
WGS_1984_World_Mercator 日 Example DB.gdbWKID:3395Authority:EPSG Feature_ExProjection:Mercator 田 GIS_mapFalse_Easting:0.0 False_Northing:0.0 NoteExpressStandard_Parallel_1:0.0 Central_Meridian:0.0 田 NotesLinearUnit:Meter(1.0) 田
GeographicCoordinate System:GCS_WGS_1984 田 Report
选择高程系统 source_code
选择坐标系统
<上—步（B) Finish 取消

### 第 67 页

![page 67](003-GIS-空间数据-知识点回顾/page_067.jpg)

3.2创建一个新的地理数据库
NewFeatureClass
建立要素类（矢量文 Name:
Feature_ClassAlias: Feature
在Catalog目录中选中要 TypeType of features stored in thisfeature class:
要素类(FeatureClass.. Polygon FeaturesPolygonFeaturesLineFeaturesCatalog 口 Cop PointFeaturesMultipoint Features
>> Past MultiPatchFeatures TurnFeaturesLocation: Feature_Ex Dimension FeaturesDele AnnotationFeaturesSRECYCLE.BIN Geometry Properties
+ ArcGIS_3rd Ren Coordinatesinclude Mvalues.Used to store route data.
+ Desktop Coordinates includeZvalues.Used to store3D data.
+ document Refi
+ downloadGIS_Example MarExample_DB.mdbExampleDB.gdb NevFeatureExGIS_map ImpNoteExpressNotes ExpReport Iten
+ source_codePro <上步（B) 一页（N）> 取消

### 第 68 页

![page 68](003-GIS-空间数据-知识点回顾/page_068.jpg)

3.2创建一个新的地理数据库
NewFeatureCla NewFeatureClass XSpecifythed Field Name DataType Field Name DataTypeConfiguratid OBJECTID ObjectID ObjectIDSHAPE Geometry GeometryODefault lame Text TextThisop Catalog 口 Xtable/feOUseconf Location: Feature_ExThisop SRECYCLE.BINwhichr ArcGIS_3rdnewtal Desktop
+ documentdownloadClick anyfieldtosee itsproperties. 日 GIS_Examplesee Example_DB.mdbField Properties 日 Example_DB.gdbAlias Name Feature ExAbout Config AllowNULLvalues YesDefaultValue Feature_ClassLength 50 GIS_map
配置 田 NoteExpress
+ NotesImport.. PPTToaddanewfield,type thenameinto anemptyrowin theFieldNamecolumn,click ld,1 Reportin theData Type column to choose the data type,then edit the FieldProperties. col
按Del键删除选中字段
<上—步(B) Finish 取消 <上—步（B) Finish 取消

### 第 69 页

![page 69](003-GIS-空间数据-知识点回顾/page_069.jpg)

3.2创建一个新的地理数据库
建立关系表格
在Catalog目录中选中地理数据库→新建(New)
关系表（Table...)
Catalog 口x Copy
>> 启 Paste Feature Dataset...
Location: Example_DB.gdb Delete Feature Class...
田 $RECYCLE.BIN Rename Table...
田 ArcGIS_3rd Refresh
田 DesktopMakeDefaultGeodatabase View...
document
+ download Administration Relationship Class...
GISExampleExample DB.mdb Distributed Geodatabase Raster Catalog...
ExampleDB.gdb NewFeature_Ex RasterDataset...
Feature_Class Import
+ GIS_map MosaicDataset...
NoteExpress ExportNotes ShareasGeodataService... SchematicDatasetReport ItemDescription.. ToolboxProperties...

### 第 70 页

![page 70](003-GIS-空间数据-知识点回顾/page_070.jpg)

3.2创建一个新的地理数据库
NewTable NewTable NewTable XName: Example_Table Specify the database storage configuration. FieldName DataTvpeOBJECTID ObjectIDAlias: Ex_Tab ConfigurationKeyword Name TextODefault NL FloatThis option uses the default storageptable/feature classCatalog 口 XOUse configurationk
仓价
This option allowswhichreferencestLocation: Example_DB.gdbSRECYCLE.BINArcGIS_3rdDesktop
+ documentdownload
日 GIS_ExampleExample_DB.mdb NIAbout Configuration Example_DB.gdb Yes
日
FeatureExExample_TableGIS_map
+ NoteExpress Import..
Notes anemptyrowinteFieldNamecolumn，click
+ data type,thenedtheFieldProperties.
+ Report
<上—步（B) Finish 取消

### 第 71 页

![page 71](003-GIS-空间数据-知识点回顾/page_071.jpg)

3.2创建一个新的地理数据库
建立拓扑关系
在Catalog目录中选中要素数据集→新建(New)
关系表(Table...) NewTopologyCatalog Thiswizardwill helpyoubuildanew
口 X topology.
A topology allowsyou tomodel theLocation: Feature_Ex integratedbehaviorofdifferentdatatypes.
+ SRECYCLE.BIN
+ ArcGIS3rd Some examplesinclude modeling SS...
+ Desktop adjacent land parcels or soil polygons,
+ document coastline and country boundaries,a
+ download roadsnetwork,roadand busroutes,
and nested geography(censusGIS_Example information).
Example DB.mdbExampleDB.gdbFeature ExExample_TableGIS_map
+ NoteExpress
+ Notes 上步（B） 下一页（N）> 取消
+ PPT
+ ReportProperties...

### 第 72 页

![page 72](003-GIS-空间数据-知识点回顾/page_072.jpg)

3.2创建一个新的地理数据库
NewTopology NewTopology NewTopologNewTopologyEntera nan Selectthe Each feature Specify therulesforthetopology:
FeatureEx much thefeathelessthef RuleFeat Feature Class Feature Class AddRule...
Enter the nun AddRuleEnteraclus0.0010000 Features of feature dlass: RuleDescriptionSpecify thera Feature_Class An area must notoverlap anotherareafromthesamelayer.
The cluster Rule: Anyareawherefeaturesoverlapboundaries Feature Clas isanerror.
falling withi MustNotOverlapFeature_ MustNotOverlapMustNotHaveGapsMust NotOverlapWithThe default MustBeCoveredByFeatureClassOfMustCoverEachOther showErrorscannotset Must BeCovered ByContainsPoint OK CancelContains One Point
<上一步（B) 下一页（N）> 取消

### 第 73 页

![page 73](003-GIS-空间数据-知识点回顾/page_073.jpg)

3.2创建一个新的地理数据库
NewTopologyCatalog 口xSummary:
Name:Feature_ExTopologyClusterTolerance:0.001 Location: IFeature_Ex_Topology
田 SRECYCLE.BINZClusterTolerance ArcGIS3rdNewTopologyFeature Classes: DesktopFeature_Class,Ranl + documentThenewtopologyhasbeencreated.No + downloadRules: the topology. GIS_ExampleFeature Class-Mu Example_DB.mdbExample_DB.gdbFeature_ExFeature ClassExampleTableGIS_mapNoteExpressNotes
<上一步（B) Finish 取消

### 第 74 页

![page 74](003-GIS-空间数据-知识点回顾/page_074.jpg)

3.2创建一个新的地理数据库
拓扑关系的应用一检查数据错误
空间数据采集过程中，人为因素是造成图形数
据错误的主要原因。
不正规多边形
多边形不封闭
结点不重合
过头
不连接
碎屑多边形 伪结点

### 第 75 页

![page 75](003-GIS-空间数据-知识点回顾/page_075.jpg)

3.2创建一个新的地理数据库
一般操作流程
》选中新建对象的父文件/数据库；
》点击鼠标右键，选择新建；
>选择需新建的对象；
>进入新建向导对话窗口。

### 第 76 页

![page 76](003-GIS-空间数据-知识点回顾/page_076.jpg)

第四节
数据采集

### 第 77 页

![page 77](003-GIS-空间数据-知识点回顾/page_077.jpg)

数据采集就是运用各种技术手段，通过各种渠道收
集数据的过程。服务于地理信息系统的数据采集工
作包括两方面内容：空间数据的采集和属性数据的
采集。
空间数据采集方法：野外数据采集、现有地图数字
化、摄影测量方法、遥感图像处理方法等。
属性数据采集方法：相关部门的观测、测量数据、
各类统计数据、专题调查数据、文献资料数据等渠
道获取。
遥感图像解译也是获取属性数据的重要渠道

### 第 78 页

![page 78](003-GIS-空间数据-知识点回顾/page_078.jpg)

4.1手动数字化
>根据卫星影像/电子地图，全手动绘制点、
线、面要素。
>一般流程如下：
①在ArcMap中新建一个空白地图文档
(.Mxd) ;
②加载卫星影像数据；
③创建一个新的与卫星影像坐标系相同的要素
类（点、线、面要素）；
④开始编辑要素类...··

### 第 79 页

![page 79](003-GIS-空间数据-知识点回顾/page_079.jpg)

4.1手动数字化
在地理数据库中创建
>在文件夹中创建

### 第 80 页

![page 80](003-GIS-空间数据-知识点回顾/page_080.jpg)

4.1.1 创建要素
Catalog Folder
一+ File GeodatabaseLocation: GIS_Example Personal Geodatabase
田 ArcGIS_3rdDesktop Database Connection...
+ document ArcGiSServer Connection..
+ download 百 CopyGISExampl Layer...
Exampl le_DB. 启 Paste Group Layer
+ Exampl DB. Delete PythonToolbox
+ GIS_map
+ NoteExpress Rename Shapefile...
+ Notes urnFeatureClass...
+ Id Refresh
+ Report Toolbox
+ source_code New dBASE Table
+ SubjectSystemVolume LAS Dataset
+ ItemDescription...
+ 给排水设计手册 AddressLocator...
Properties... Composite Address Locator...
XMLDocument

### 第 81 页

![page 81](003-GIS-空间数据-知识点回顾/page_081.jpg)

4.1.1创建要素
Type here to search @
Name: dom_area Favorites
田 Geographic Coordinate SystemsFeature Type: Polygon 田 ProjectedCoordinate SystemsPointSpatial Reference PolvlinePolygon CatalogDescription: MultiPoint
个 七价
Name:GCS_WGS_1984 Current coordinate system: GCS_WGS_1984
WKID:4326Authority:EPSG Location: GIS_ExampleAngularUnit:Degree(0.01745: PrimeMeridian:Greenwich(0.0) FolderConnectionsSpheroid:WGS_1984 SemmajorAxis:6378137.0 E:\
SemminorAxis:6356752.314 田 $RECYCLE.BINInverseFlattening:298.2572 田 ArcGIS_3rd
田 DesktopdocumentShowDetails Edit... download
日 GIS_ExampleCoordinates wilcontain Mvalues.Used to storeroute data. Example_DB.gdbCoordinates will containZvalues.Used to store 3D data. ExampleDB.mdbdom_area.shpOK Cancel Line.shp
田 GIS_mapNoteExpress
+ Notes

### 第 82 页

![page 82](003-GIS-空间数据-知识点回顾/page_082.jpg)

4.1.1创建要素
Untitled-ArcMap 口 ×
FileEdit ViewBookmarksInsertSelection Geoprocessing Customize Windows Help1:3,045,959,547,568 3DAnalystparcelscan.tif Georeferencing
? Editor DrawingTable Of Contents x ResultsLaversE:\GIS_Exampledom_area CopyRemoveE:\ArcGIS_3rd\Chp
日 parcelscan.tif OpenAttributeTableJoins and Relates1
Zoom ToLayer
选中图层
Zoom To MakeVisibleZoomToRasterResolution Zoom To Layer
点击右键
Visible Scale Range Zoom to the extentof theData selected layerEditFeatures ArcToolboxSave AsLayerFile...
Create Layer Package...
Properties... Catalog
-88888.268 1565422.265DecimalDegrees

### 第 83 页

![page 83](003-GIS-空间数据-知识点回顾/page_083.jpg)

4.1.1创建要素
Untitled-ArcMap 口 XFile PE View Bookmarks Insert Selection Geoprocessing Customize Windows Help
日 1:92,973,989 3DAnalystparcelscan.tif Georeferencing-
KX Editor- DrawingTable Of Contents
合名 020
D05 4/.65
日 Layers 10044
E:\GIS_ExampleLine 006 6789 021 AttributesCreate Featuresdom_area 100 1101507. 12
日白 E:\ArcGIS_3rd\Chp3\T 022
日 parcelscan.tif 09.340 008
口1 11628 35009 35 35024 0 63 1286 027 028 36.34 Search39.65 108 81011 315 58.15 03443 108.84 012 2.
6; 16 ArcToolbox60385033 03330 013132. .18 38014 Catalog45 72 .57'2 2
四
481847.092 3768458.302Decimal Degrees

### 第 84 页

![page 84](003-GIS-空间数据-知识点回顾/page_084.jpg)

4.1.2绘制几何形状（点、线、面）
Untitled-ArcMap 口
File Edit ViewBookmarksInsert Selection Geoprocessing Customize Windows Help1:92,973,989 3DAnalystparcelscan.tif Georeferencing*
KX Editor- Drawing RTable Of Contents XLayers RemoveFAGISExample
日 Line 四 OpenAttributeTabledom_area Joins and Relates
口 ZoomToLayerE:\ArcGIS_3rd\Chp3\T Zoom To MakeVisibleparcelscan.tif
口1 UseSymbol LevelsSelection 35 63
Label Features 028
EditFeatures StartEditingConvert Labels toAnnotation.... Define New Types Of Features...
ConvertFeatures toGraphics..
ConvertSymbology toRepresentation.. Organize Feature Templates..
Data 032
Save AsLayer File...
CreateLayerPackage...
Properties..
481920.318 3768476.001Decimal Degrees

### 第 85 页

![page 85](003-GIS-空间数据-知识点回顾/page_085.jpg)

4.1.2绘制几何形状（点、线、面）
编辑工具条 (Editor toolbar)
菜单 草图绘制工具 整形 拆分 属性 创建要素
Editors
编辑工具 编辑拐点 切割多边形 旋转 草图属性
CreateFeatures 口xAttributes x
图 Edit SketchProperties dom_areabuildings ×ZM|FinishSketchCommercial X dom_areaCommercial LineResidential 0 3122512.335 10094299.0711 3122415.981 10094244.383 Linel2 3122455.043 10094166.258
OBJECTIDBldgtype Commercial ConstructionToolsAddress <Null>
City Austin LineState X1 RectangleSHAPE_Length 708.039734 CircleSHAPE_Area 17921.096956
OBJECTID EllipseObjectID 2Freehand

### 第 86 页

![page 86](003-GIS-空间数据-知识点回顾/page_086.jpg)

4.1.2绘制几何形状（点、线、面）
>绘制线条 + 鼠标形态
Create Features XCreateFeatures 口x
<Search> QSnap ToFeaturedom_area Direction.. Ctrl+A 点击
Deflection....
dom_area Length... Ctrl+L 鼠标
Line Change LengthAbsoluteX,... F6 左键
Line Delta X,Y.. Ctrl+D ToolsDirection/Length.... Ctrl+GParallel Ctrl+P 15
Perpendicular Ctrl+EConsuctionTools SegmentDeflection.. F7 点击鼠标左键绘图
Replace SketchLine TangentCurve...
FindText Ctrl+WRectangle Streaming F8
Circle Delete Sketch Ctrl+DeleteFinish Sketch F2
Ellipse Square andFinishS Freehand FinishPart
点击鼠标右键，完成草图绘制

### 第 87 页

![page 87](003-GIS-空间数据-知识点回顾/page_087.jpg)

4.1.2绘制几何形状（点、线、面）
Untitled-ArcMapFileEdit Bookmarks Insert Selection Geoprocessing Customize WindowsHelp
×5 1:92,973,989 3DAnalystparcelscan.tif GeoreferencingKKA 口·A·| 10 BTable Of ContentsD05 02 Editor 4中
LayersE:\GIS_Example 1034 Start Editing
日Line 006 8.43 02 Stop Editing SearchSave Editsdom_area 100 410 Move... Features
口 0 点击鼠 Split.. <Search> 、
E:\ArcGIS_3rd\Chp3\T 09
parcelscan.tif Construct Points... a ArcToolbox008 Copy Paralle... _area
□1 11628 Merge...
Buffer...
009 Union.... oCatalogClip.... struction Tools 36.34108 Validate Features9.65 011 Snapping ine1 ectangle 15108.8 MoreEditingTools ircleEditingWindows llipse35 031 Options.. reehand30 35024 32.
0 福
72 45 G7 72.59
一日口 一
481933.371 3768456.533Decimal Degrees

### 第 88 页

![page 88](003-GIS-空间数据-知识点回顾/page_088.jpg)

4.1.2绘制几何形状（点、线、面）
>绘制线条一保存
Editor 保存对文件的编辑，并
StartEditing
继续编辑。
Stop Editing
停止编辑并保存任何未
Save Edits
保存的编辑。
常备份，勤保存！
Doyouwanttosaveyouredits?
是（Y） 否（N) 取消

### 第 89 页

![page 89](003-GIS-空间数据-知识点回顾/page_089.jpg)

>绘制线条一保存
Untitled-ArcMap 口
FileEdit ViewBookmarksInsertSelection Geoprocessing CustomizeWindows Help1:92,973,989 3DAnalyst-parcelscan.tifA·宋体
TableOf Contents xEditor
日 Layers Editor-
E:\GIS_Exampledom_area Create Features 口
电 <Search>
E:\ArcGIS_3rd\Chp3\Tparcelscan.tif There are no templates to show. ArcToolbox
口1
CatalogSelecta template,
481946.8653768451.887Decimal Degrees

### 第 90 页

![page 90](003-GIS-空间数据-知识点回顾/page_090.jpg)

4.1.2绘制几何形状（点、线、面）
>绘制面要素
操作流程基本一致，仅创建要素窗口有差异。
CreateFeatures 口x CreateFeatures
<Search>
dom_area Clickhere to seetemplatesnotlisterXdom_area LineLine Line
-Line
肉 肉
Construction Tools ConstructionToolsPolygon LineRectangle RectangleCircle CircleEllipse Ellipse2 Freehand 2FreehandC AutoCompleteFreehand

### 第 91 页

![page 91](003-GIS-空间数据-知识点回顾/page_091.jpg)

4.2自动数字化
》只能是二值化（黑白色）电子地图或图片
不不
不
056057058 风频
059 不
060 甲
061 不 ④
062 001
C90 002 002064 020 017065 003 021 003 018990 004 022 00 019067 005 023 005 020068 006 024 006 021069 007 025 007 022070 008 026 008,
071 009 010 009 028072 011 028073 029074075076 033078 091092

### 第 92 页

![page 92](003-GIS-空间数据-知识点回顾/page_092.jpg)

4.2自动数字化
需用到ArcScan工具： ExtensionsSelect the extensionsyouwant to use.
3DAnalystCustomize Windows Help ArcScanGeostatistical Analystolbars NetworkAnalystPublisherExtensions... SchematicsSpatial AnalystAdd-InManager... Tracking AnalystCustomize Mode...
Style Manager....
ArcMapOptions...
Description:
选择自定义菜单
ArcScan 10.6.0
Copyright1999-2017Esri Inc.AllRightsReserved
（Customize)→扩展 Providessupportforthecreationofvectorfeaturesfromarasterimage.
(Extentions)-→ArcScanClose
>Close

### 第 93 页

![page 93](003-GIS-空间数据-知识点回顾/page_093.jpg)

4.2自动数字化
需用到ArcScan工具：
3D Analyst
菜单（或工具条）点击
Advanced Editing
鼠标右键→快捷菜单中 Animation
选择ArcScan ArcScanWind ows Help Data DrivenPages3DAn DataFrameToolsEditorArcScanparcelscan.tif Vectorization Raster Cleanup Cell Selection

### 第 94 页

![page 94](003-GIS-空间数据-知识点回顾/page_094.jpg)

4.2自动数字化
4.2.1半自动数字化
①选中内容列表中的Line
图层→②启动编辑，打开
00 810 001
编辑工具条→③创建要素 062 020 0023C3 621 00 118
CO 022
窗口 中选择 0C5 023 005 C2C006 C24 900 C21
LOC 025 007 C22
Line→④ArcScan工具条中
选择矢量化追F按钮

### 第 95 页

![page 95](003-GIS-空间数据-知识点回顾/page_095.jpg)

4.2自动数字化
Untitled-ArcMap 口
FileEditViewBookmarks Insert Selection Geoprocessing Customize Windows Help1:200,000,000 Drawing- 宋体 SWATProje jectSetupGeoreferencing" parcelscan.tifTable Of Contents ResultsAroToolboxArcScan
日 Layers parcelscan.tif Vectorization arterCleanup CellSelectionLine Create Features
日 m_area ditorEditor- dom_area
日 par elscan.tif dom_area
國 Copy LineRemove Line
口 penAttributeTableinsandRelatesZoomToLayerZo m ToMake VisibleVisi eScaleRange 1.3: Construction Tools5 001 AttributesUse mbol Levels LineSelecton 020 2C0 017 RectangleLabel Features DC3 003 1118 Circle621 EllipseEditFeatures 004 00 2FreehandConvert Labels to Annotation... 0C5 020 005 C2CConvertFeaturestoGraphic. 006 024 000 C21
Convert Symbology to Representation... LOC EC C22
Data 025
SaveAsLayer File... 600 026
Create Layer Package.... 013 02 028
Properties..
481672.351 3768513.07DecimalDegrees

### 第 96 页

![page 96](003-GIS-空间数据-知识点回顾/page_096.jpg)

4.2自动数字化
4.2.1半自动数字化
在线的断点处点击鼠标
左键;
点击鼠标左键
②在线上其他任意位置再
00 5 001 次点击鼠标左键；
062 020 0173C3 621 0O 118004 022 ③识别后点击鼠标右键；
3C5 023 005 C2C006 006 C21
LOC 025 007 C22 ④弹出快捷菜单中选择完
成草图(Finish Sketch)。

### 第 97 页

![page 97](003-GIS-空间数据-知识点回顾/page_097.jpg)

4.2自动数字化
Untitled-ArcMap 口
Bookmarks Insert Selection Geoprocessing Customize Windows1:200,000,000 Drawing· SWATProject SetupGeoreferencing parcelscan.tif 同日
Table Of Contents Results
国 ArcScanLayers parcelscan.tif Vectorization Raster Cleanup CellSelectionLine Create FeaturesArcToolboxdom_area Editor <s>
口 055 Editor- 国 dom_area
日 parcelscan.tif dom_area0 Line
口1 2.7 Line058051 Construction Tools062 OC 54 810 6.0 C01 Line Attributes063 二 RectangleC54 002 020 2C0 017 OCircle116h S0C 021 003 018 EllipseC04 2Freehand066 C22 00 C1S Catalog067 005 005 C20000 023
C24 000 021
BCO 025 007070 026 00871 009481673.264 3768646.85Decimal Degrees

### 第 98 页

![page 98](003-GIS-空间数据-知识点回顾/page_098.jpg)

4.2自动数字化
Untitled-ArcMap 口 ×
FileEditView Bookmarks InsertSelection Geoprocessing Customize WindowsHelp1:200,000,000 Drawing- SWATProjectSetup
+ Georeferencing- parcelscan.tifTable Of Contents XArcScan
日Layers parcelscan.tif Vectorization Raster Cleanup Cell SelectionLine Create Features 口
ArcToolboxdom_area Editor <Search> QEditor- dom_areaparcelscan.tif OSR dom_area10 Line11 257 Line058600
昌
051 Construction Tools062 OC 04 810 6.0 C01 Line Attributes063 口 RectangleC54 502 002 017 Circle80C L2 020 Ellipse11h 003 018 2rFreehand066 C34 G22 00 C1S Catalog067 005 023 S00 C20
ROO 003 C21 000 021025 022.
070 026 80G 02371 009481665.65 3768683.493Decimal Degrees

### 第 99 页

![page 99](003-GIS-空间数据-知识点回顾/page_099.jpg)

4.2自动数字化
Untitled-ArcMap 口
FileEditView Bookmarks InsertSelection Geoprocessing Customize Windows Help1:60,000,000 Drawing-k 口 宋体 SWATProjectSetup
+ KX Georeferencing-prcelscan.tifTable Of Contents XArcScanLayers parcelscan.tif Vectorization 厅 Raster Cleanup CellSelectionLine 5 Create Features
日 dom_area Editor ·<Search> ®
60.04 Editor- 中 国 dom_areaparcelscan.tif B 30.41 dom_area70 Line Edit SketohProperties
.62 LineB 002 017100 C10）
003 018 Construction Tools3 Polygon Attributes
口 RectangleCirle004 019 Ellipse3
寸 2rFreehand3 Auto Complete Polygon Catalog005 6 020 Search3 47. 6.
3 100.44481730.384 3768586.808Decimal Degrees

### 第 100 页

![page 100](003-GIS-空间数据-知识点回顾/page_100.jpg)

4.2自动数字化
Untitled-ArcMap 口 XFileEditViewBookmarksInsertSelection Geoprocessing CustomizeWindowsHelp1:60,000,000 Drawing- 口·A SWATProjectSetupIK Georeferencing" parcelsoan.tifTable Of ContentsArcScan X
日Layers parcelscan.tif Vectorization Raster Cleanup Cell SelectionLine 5 Create Features
日 dom_area Editor X <Search> ®
60.04 Editor" 中 dom_areaparcelscan.tif domarea10 70 Line Edit
口1 7.62 Line98.10
B 002 017 Sketoh100 C100 Pr018 好 Construction ToolsX 3Polygon4 Attributes
口 RectangleOCircle004 019 Ellipse2rFreehand LarAuto Complete Polygon005 .66 02047.
3 100.44
Numberof featuresselected:1 481752.656 3768551.259DecimalDegrees

### 第 101 页

![page 101](003-GIS-空间数据-知识点回顾/page_101.jpg)

4.2自动数字化
4.2.2全自动数字化
①清除不必要的内容；②自动数字化

### 第 102 页

![page 102](003-GIS-空间数据-知识点回顾/page_102.jpg)

4.2自动数字化
4.2.2全自动数字化—图像清理
》使用栅格绘图工具
ArcScanparcelscan.tif Vectorization Raster Cleanup Cell Selection|
Start Cleanup
①ArcScan工具条中点击栅格
Stop Cleanup
清理按钮; RasterPainting ToolbarEraseSelected Cells
②弹出菜单中点击开始清理： Fill Selected CellsErosion...
③点击绘图工具条
Dilation...
Opening....
Raster Painting Closing...
Save As...
橡皮擦工具 魔术橡皮擦工具

### 第 103 页

![page 103](003-GIS-空间数据-知识点回顾/page_103.jpg)

4.2自动数字化
4.2.2全自动数字化—图像清理
》使用像元选择工具
ArcScanparcelscan.tif Vectorization Raster Cleanup Cell Selection
①ArcScan工具条中点击 SelectConnected Cells...
像元选择工具； ClearSelected CellsSaveSelection As...
②点击选择相连像元。

### 第 104 页

![page 104](003-GIS-空间数据-知识点回顾/page_104.jpg)

4.2自动数字化
4.2.2全自动数字化—图像清理
690 435 025 p72 'innit 24.0 403.
070 008 0081:3.8O 023026 思 116.28071 600 025 20 3510525 009 024 62027 026 027 P2.U 028010 123.35 396 ivi:
072 C.u10.1.35 5375 028 EH. 12011 11885 029 012 03443 073 355104.46 03 10.530 70.
012 7e.55 013 033074 030114.50 3 0311 G 3075 07 015 032
"27.49 3 3 72.89 43302820: 016 a 1. 029 030076 5. 017 03315 3.65077 7.5 392311572078 2 585 426 37 42 4 2 091 4.5159 2 10.3 083 084 085 086 087 088 089 060 27.35079 7.222 123 10035

### 第 105 页

![page 105](003-GIS-空间数据-知识点回顾/page_105.jpg)

4.2自动数字化
4.2.2全自动数字化—图像清理
》使用像元选择工具
ArcScanparcelscan.tif Vectorization Raster Cleanup Cell Selection
如选择效果不佳，点
Select Connected Cells...
击清除选择； InteractiveSelectionTargetClearSelected Cells
如效果不错，点击选
Save SelectionAs...
项另存。

### 第 106 页

![page 106](003-GIS-空间数据-知识点回顾/page_106.jpg)

4.2自动数字化
4.2.2全自动数字化一图像清理
》使用像元选择工具
①设置存 ExportRasterDataset
储路 ArcMap
学位论文评审
② 设 教府文件
Doyouwanttoadd theexporteddatato themapasa layer? parcelscan.tif
件名; RasSelO.tif
③设
是（Y） 否(N）
件格式，
Name: RasSelo Save
④保存
Saveastype: TIFF Cancel

### 第 107 页

![page 107](003-GIS-空间数据-知识点回顾/page_107.jpg)

4.2自动数字化
4.2.2全自动数字化—图像清理
Untitled-ArcMFile Edit View 完成图像清理，开
nal 0561114
始全自动数字化 057
O Contents 058690
日 Layers 060
RasSelO.tiValue 061
High: 062 001 019 001063
Low:0 064 002 020 002 017065 003 021 003 018
parcelsca 066 004 022 004 019
田Line 067 S00 023 005 020
dom_area 068 006 006 021 (0.41024
口 069 007 025 200
parcelsca 070 008 026 008071 009 027 009
□1 072 010 028073 011074 012 10013 014075076 033077078 0913 80 092

### 第 108 页

![page 108](003-GIS-空间数据-知识点回顾/page_108.jpg)

4.2自动数字化
4.2.2全自动数字化—图像清理
ArcScanRasSelO.tif Vectorization Raster Cleanup Cell Selection
①ArcScan工具条中选择矢量化：
②弹出菜单中，选择显示预览；
③点击生成要素，弹出窗口设置
好参数，点击OK;
④点击编辑器，保存并停止编辑
EditorEditor 中
Start EditingStop EditingSave Edits

### 第 109 页

![page 109](003-GIS-空间数据-知识点回顾/page_109.jpg)

4.3逻辑一致性
邻接 相交 相离 包含 重合
>逻辑一致性是指GIS数据（点/线 点一点
点一线
面要素）对现实世界中的地理 点一面
线一线
事物之间的空间关系的模仿程度 线一
面
》基本编辑涉及逻辑一致性的两个方面。
·确保两条相交的线段在公共顶点相交。
·确保相邻多边形共享相同的边界。

### 第 110 页

![page 110](003-GIS-空间数据-知识点回顾/page_110.jpg)

4.3逻辑一致性
悬挂
拓扑正确一水平线与垂直
线相交，形成三条直线，
悬挂一两条线连接失 线与线之间有公共节点。
败，线与线间有空隙。
节点nodeGIS数据结构完整性的角度出发。
现实世界中是否存在（悬挂）?
自动连接功能，确保逻辑一致性 捕捉工具
(Snaping Tool)

### 第 111 页

![page 111](003-GIS-空间数据-知识点回顾/page_111.jpg)

4.3逻辑一致性
捕捉容差 （(Snapping tolerance)
捕捉容差是两个顶点之间的最小距离。像素、长度单位
如果光标在一个顶点的容差范围内，那么下一次鼠标点
击将被锁定到该顶点。
SnaptoleranceScreen pixelMap unit

### 第 112 页

![page 112](003-GIS-空间数据-知识点回顾/page_112.jpg)

Customize WindowsHelpToolbars 3DAnalyst
捕捉类型 Extensions... Advanced EditingAdd-ln Manager.. AnimationCustomize Mode... ArcScanStyle Manager... COGOArcMap Options.. Data Driven PagesData Frame ToolsWindows Help Distributed Geodatabase3D Analyst- Edit VerticesEditorEditor 中 EffectsStart Editing Feature CacheStopEditing Feature ConstructionGeocodingSave Edits Geodatabase HistoryMove... GeometricNetworkEditingGeoreferencingSplit... Geostatistical Analystonstruct Points. GPS GraphicsCopy Parallel Image ClassificationMerge.. LabelingBuffer... LAS DatasetUnion.... Network Analyst Layoutclip... Parcel EditorValidate Features PublisherRaster PaintingSnapping Snapping Toolbar RepresentationMore Editing Tools Options.. Route EditingEditing Windows Workwith the snapping Schematicenvironment and set snappir Schematic EditorOptions... options for snapping. Schematic Network AnalystSnappingSpatial AdjustmentSpatialAnalystStandardCustomize订制→Toolbar工具条 TabletTIN EditingToolsTopologyEditor toolbar编辑工具条→Snapping捕捉 Tracking AnalystTransform ParcelsUtility Network AnalystVersioningCustomize...

### 第 113 页

![page 113](003-GIS-空间数据-知识点回顾/page_113.jpg)

捕捉类型
捕捉点
捕捉容差
捕捉终点 田
捕捉边
SnappingSnapping 田
Use SnappingIntersection Snapping
捕捉顶点 TangentSnappingSnapTo SketchSnap To Topology NodesOptions...

### 第 114 页

![page 114](003-GIS-空间数据-知识点回顾/page_114.jpg)

捕捉设置
EditorStart EditingStop EditingSnappingSaveEdits Snapping- 田
口
Snapping Snapping ToolbarMore Editing Options... Use SnappingEditingWindows IntersectionSnappingepping Options MidpointSnappingOptions... GeneralTangent SnappingTolerance: 10 PixelsSnap ToSketchSnap Symbol:
Snap To Topology Nodesbuildings:VertexOptions..
Layer NameSketch:EdgeSnapTypeTextSymbol...
OK Cancel

### 第 115 页

![page 115](003-GIS-空间数据-知识点回顾/page_115.jpg)

相邻多边形
》保持相邻多边形的逻辑一致性是很重要的。
重叠
缝隙
两个多边形之间的拓 两个多边形的重合边
扑错误 界，无拓扑错误
>相邻林地发生的两次病虫害。

### 第 116 页

![page 116](003-GIS-空间数据-知识点回顾/page_116.jpg)

4.3创建相邻多边形
常用两种方法
－使用特殊工具来创建相邻的多边形。
一先创建一个大的多边形，再切割成两个相邻多边形。
追踪工具（Trace）
自动补全多边形工具
(Auto complete polygon)

### 第 117 页

![page 117](003-GIS-空间数据-知识点回顾/page_117.jpg)

4.3创建相邻多边形
1.选择要素模板
buildings CreateFeatures X2.选择创建工具一polygon CommercialResidential
(Construction tool)
boundaryboundary3.输入第一个多边形 Polygon buildingsRectangle Commercial4.将创建工具换为“自动 ResidentialStreets
完成多边形”Auto -StreetsComplete Polygon AutoCompletePolygon ConstructionTools5.创建邻接多边形，起始 PolygonRectangle
点和结束点必须位于第 中 CircleEllipse
一个多边形内部 Trace FreehandCreate segments by tracing AutoCompletepress O to access tracing existing features.Right-click or Polygon6.新多边形将使用旧多边 options,including setting anoffset.
形的现有边界。
或使用追踪工具（Trace）

### 第 118 页

![page 118](003-GIS-空间数据-知识点回顾/page_118.jpg)

第五节
数据编辑

### 第 119 页

![page 119](003-GIS-空间数据-知识点回顾/page_119.jpg)

编辑技巧
>编辑前一定要备份（backupcopy
》打开新的地图文档进行编辑，只添加你需要
的图层；
》减少打开文件的数量；
》尽量保持层在相同的坐标系统，以避免出现
意外的错误;
常保存（Savefrequently）
常备份，勤保存

### 第 120 页

![page 120](003-GIS-空间数据-知识点回顾/page_120.jpg)

编辑技巧
编辑矢量文件通常会破坏地图
文档（.mxd）布局
》建议在专门打开的地图文档
（Map document）中进行编辑，
其中包含所需的最小数量的文
件。
Erupfions Hg hway Lagend
》尽量不要在你花了几天时间开 Countles ooprso.mlle72-35
发绘制的华丽地图文件（Mapdocument）中边界数量数据。

### 第 121 页

![page 121](003-GIS-空间数据-知识点回顾/page_121.jpg)

图形编辑
Graphic edit

### 第 122 页

![page 122](003-GIS-空间数据-知识点回顾/page_122.jpg)

快捷工具
>编辑工具（EditTool）用于选择要
素，以便可以移动、删除或编辑它
编辑工具 们。
>选择要素工具（SelectFeatures）
·鼠标单击要素进行选择
选择要素
·添加另一个要素
·鼠标框选多个要素
·点击空白区域来清除选择（或使用
清除选择
清除选择—ClearSelection—工具）

### 第 123 页

![page 123](003-GIS-空间数据-知识点回顾/page_123.jpg)

选择要素
移动工具 选择要素
鼠标框选（按住
鼠标左键拖拽）
Shift+鼠标单击
（或鼠标框选）

### 第 124 页

![page 124](003-GIS-空间数据-知识点回顾/page_124.jpg)

分割多边形
1.使用编辑工具选择要素。 2.点击裁剪多边形工具。
EditorEditor3.使用切割多边形工具绘制 4.双击鼠标完成线条并分割多
切割线。 边形。
起始点和结束点必须位于多边形外部

### 第 125 页

![page 125](003-GIS-空间数据-知识点回顾/page_125.jpg)

移动要素
1.使用编辑工具（Edittool）选中目标要素（单
个或多个）
2.悬停鼠标，拖动要素到目标位置。

### 第 126 页

![page 126](003-GIS-空间数据-知识点回顾/page_126.jpg)

删除要素
1.使用编辑工具（Edittool）选中目标要素（单个
或多个）
2.按键盘上的Del键输出选中对象，也可在属性表
中进行删除

### 第 127 页

![page 127](003-GIS-空间数据-知识点回顾/page_127.jpg)

编辑顶点
1.使用编辑工具 (Edit tool) 2.选择编辑顶点（EditVertices)，
选中目标要素 草图出现了。
Editor
中
Route Measure Editing Route Measure EditingInsertVertex Insert VertexDelete Vertex DeleteVertexMove... Move...
3.单击并拖动可移动顶点。 MoveTo.... MoveTo...
Change Segment Change SegmentFlip Flip4.单击鼠标右键，打开草图菜 Trim To Length.... Trim To Length..
Part Part
单以添加或删除顶点。 DeleteSketchCtrl+Delete Delete SketchCtrl+DeleteFinish Sketch F2 口 Finish Sketch F2
FinishPart FinishPartSketch Properties Sketch Properties5.双击或在草图菜单中选择
“Finish Sketch”完成编辑

### 第 128 页

![page 128](003-GIS-空间数据-知识点回顾/page_128.jpg)

旋转要素
1.使用编辑工具（Edittool） 2.选择旋转工具（Rotatetool）
选中目标要素
EditorEditor 中
(optional)拖动x移动旋转中心
点位置
3.在旋转点周围单击并拖动

### 第 129 页

![page 129](003-GIS-空间数据-知识点回顾/page_129.jpg)

分割线要素
1.使用编辑工具选择要素。2．点击分割工具（SplitTool)
EditorEditor3.在分割处点击鼠标。

### 第 130 页

![page 130](003-GIS-空间数据-知识点回顾/page_130.jpg)

要素reshape (整形）
1.使用编辑工具选择要素。 2.点击整形工具（Reshape）
EditorEditor- 中
4.输入最后一个顶点并双击完
3.使用鼠标描绘需要整形 成草图（或finishsketch）
的形状。

### 第 131 页

![page 131](003-GIS-空间数据-知识点回顾/page_131.jpg)

编辑状态下的快捷菜单
SnapToFeatureDirection.. Ctrl+ADeflection...
草图上点击 Length... Ctrl+LChangeLength
右键
Route Measure Editing Absolute X,... F6
InsertVertex DeltaX,Y... Ctrl+DDeleteVertex Direction/Length... Ctrl+GMove.. ParallelMove To... Perpendicular Ctrl+EChange Segment SegmentDeflection... F7
Flip Replace SketchTrim to Length.. TangentCurve...
Part FindText Ctrl+WDeleteSketch Ctrl+Delete Streaming F8
草图上点
Finish Sketch F2 Delete Sketch Ctrl+DeleteFinishPart 击右键 Finish Sketch F2
SketchProperties Square and FinishFinish PartVertex menuSketch menu
顶点菜单
草图菜单

### 第 132 页

![page 132](003-GIS-空间数据-知识点回顾/page_132.jpg)

Multipartfeatures（多要素）
》是由多个简单的要素组
成的，这些要素是不相
交的。
点击右键选择 FinishPart继续绘制下一个多
边形。
Delete SketchFinishSketch 》使用FinishSketch完成图
FinishPart
形绘制，或在最后一个
顶点双击。

### 第 133 页

![page 133](003-GIS-空间数据-知识点回顾/page_133.jpg)

编辑草图属性
EditorEditor #中XQI
用于查看或编辑顶点
RouteMeasure EditingInsertVertex 坐标，或删除顶点。
DeleteVertexEditSketch Properties 口xMove...
Move To... ZM|FinishSketchChange Segment #
0 9766988.843 5412849.986
Trim toLength...
9767027.251 5412872.8622 9767050.000 5412903.974
DeleteSketch Ctrl+Delete3 9767043.143 5412983.586
FinishSketch F24 9767049.103 5413036.6609767088.173 5413080.5846 9767144.460 5413090.650
Vertex menu 9767211.342 5413088.820
R 9767265643 5413051302

### 第 134 页

![page 134](003-GIS-空间数据-知识点回顾/page_134.jpg)

Sketching tools（草图工具）
EditorEditor
》控制连接顶点的边的
默认为直线工
具（Straight 类型
segment tool)
》供不同的方法来添加
下一个顶点
·直线
浮动迷你
·直角
工具栏
人|口 ·圆弧

### 第 135 页

![page 135](003-GIS-空间数据-知识点回顾/page_135.jpg)

Right Angle sketch tool （直角）
3.鼠标点击输入角点
1.选择要素模板 4.输入最后一个角点并双击
buildings 完成草图（或finishsketch）
CommercialResidential2.选择直角工具（RightAngle ) Feature ConstructionEditorEditorSnapToFeatureAbsolute X,Y... F6
DeltaX,... Ctrl+DFeature Construction X Direction/Length...Ctrl+GDeleteSketch Ctrl+DeleteFinish Sketch F2
RightAngleSquare andFinishFinishPart

### 第 136 页

![page 136](003-GIS-空间数据-知识点回顾/page_136.jpg)

Arc Segment sketch tool (圆弧)
1.选择要素模板 3.沿道路输入节点（鼠标
点击)
StreetsStreets2.选择弧段工具（ArcSegment )
4.输入最后一个顶点并双击
完成草图（或finishsketch）
Feature Construction
-么人
FinishSketch F2

### 第 137 页

![page 137](003-GIS-空间数据-知识点回顾/page_137.jpg)

属性编辑/修改
What is an attribute table?

### 第 138 页

![page 138](003-GIS-空间数据-知识点回顾/page_138.jpg)

属性窗口
EditorEditorUsefulwindow：用于编辑所选要素的属性
右键单击快捷菜单项
Attributes
显示当前选 (contextmenu)
日 buildings
择的要素 口 CommercialCommercialResidential 京 FlashResidential ZoomToPanTo
四口 CopyAttributesOBJECTID 3
Bldgtype Commercial 启 PasteAttributesAddress <IInN> M OnlySelectThisCity Austin UnselectStat TX DeleteSHAPE_Length 441.572368
编辑字段属性 SHAPE_Area 8826.985592 OpenAttributeTableOBJECTID Layer Properties...
ObjectIDNullvaluesnotallowed contextmenu

### 第 139 页

![page 139](003-GIS-空间数据-知识点回顾/page_139.jpg)

属性窗口
编辑属性
编辑单个要素 编辑多个要素
Attributes x AttributesbuildingsCommercial Commercial
口 Commercial 1.单击要素 Commercial 1.单击图
口
Residential Residential 层名称
Residential Residential
口 肉口
OBJECTID 3 OBJECTIDBldgtype Commercial BldgtypeAddress <Null> AddressCity Austin City AustinState TX State TXSHAPE_Length 441.572368 SHAPE_LengthSHAPE_Area 8826.985592 SHAPE_AreaOBJECTID OBJECTIDObjectID 2.编辑字段 ObjectID 2.编辑字段
Null valuesnot allowed Null valuesnot allowed

### 第 140 页

![page 140](003-GIS-空间数据-知识点回顾/page_140.jpg)

属性表
TableOfCont.xLayers
日日 CN-shaA 國 CopyRemoveOpen Attribute TableJoins and RelatesZoomTo Layer Open Attribute TableZoom To Make Visible Open this layer's attributeVisible Scale Range double-click layer name OR table.Shortcut:CTRL+
UseSymbol Levels CTRL+T.
SelectionLabelFeaturesEdit FeaturesConvert Labels to AnnotationConvert Features to Graphics...
Convert Symbology to Representation...
Save As Layer File....
Create Layer PackageProperties...
选中图层→鼠标右键
→Open Attribute Table

### 第 141 页

![page 141](003-GIS-空间数据-知识点回顾/page_141.jpg)

ArcGIS 中的字段
water_stationFID Shape ID 省份名 流城 控制单 水体 控制断 2014年水 2020年水 监测断 监测1 控制藏
OPoint W1478 新疆维晋尔自治区 西北诸河 阿克苏河阿克苏地区龙口拉制单元 阿克苏河 龙口 II 阿克苏 乌什县 阿克苏地区：温宿县
1Point W1479 新疆维晋尔自治区 西北堵河 阿克苏河阿克苏地区塔里木栏河闸拉制单元 阿克苏河 艾比湖 塔里木拉河闸 II 阿克苏 阿瓦提县 阿克苏地区：阿克苏市，阿
2Point 3Point W1480 新疆维善尔自治区 西北诸河 艾比湖博尔塔拉蒙古自治州控制单元 艾比湖1 V- V 博尔塔 精同县 博尔塔拉豪古自治州：阿拉
W1481 新疆维普尔白治区 四北诸河 白杨河塔城地区控制单元 白杨河 白杨河水库出口 克拉玛 乌尔禾区 克拉玛依市：白城滩区，克
4Point W1482 新疆维普尔自治区 西北堵河 白杨河吐鲁餐地区拉制单元 白杨河 河东乡大桥 吐餐谷 托克县 社鲁路地区：都兽县，吐餐 阿勒泰地区：布尔津县
5Point W1483 新疆维普尔自治区 西北堵河 布尔津河阿勒泰地区拉制单元 布尔津河 布尔津河大桥 阿勒泰 布尔津县
6Point W1484 新疆维吾尔白治区 西北诸河 车尔臣河巴音郭楞豪古自治州拉制单元 车尔臣河 塔提让 II II 巴音邦 且末县 巴音郭楞豪古自治州：且末
7Point W1485 新疆维普尔自治区 西北堵河 额尔齐斯河阿勒寨地区北屯大桥拉制单元 额尔齐斯河 北屯大桥 阿动票 阿勒市 阿勒泰地区：阿勒泰市，富
8Point W1486 新疆维吾尔自治区 西北堵河 额尔齐斯河阿勒泰地区布尔津水文站控制单元 额尔齐斯河 布尔津水文站 II II 阿勒票 布尔津县 阿勒寨地区：阿勒泰市，布
9Point W1487 新疆维吾尔自治区 四北诸河 额尔齐斯河阿勒泰地区额河南湾控制单元 额尔齐斯河 额河南湾 II II 阿动寨 哈巴河县 阿勒寨地区：哈巴河县，吉
10Point W1488 新疆维晋尔自治区 西北堵河 额尔齐斯河阿勒泰地区高道大桥控制单元 额尔齐斯河 蕴大桥 11 II 阿动票 高道县 阿勒泰地区：高道县
11Point W1489 新疆维普尔自治区 西北堵河 顿敏河塔城地区控制单元 额敏河 巴士拜大桥 II1 塔城 裕民县 塔城地区：额敏县，塔城市
12Point W1490 新疆维普尔自治区 西北诸河 巩乃斯河伊翠州控制单元 巩乃斯河 羊场大桥 II II 伊型 尼勒克县 巴音郭榜蒙古自治州：和静
13Point W1491 新疆维晋尔自治区 西北堵河 喀拉喀什河和田地区拉制单元 喀拉喀什河 喀河大桥 和田 和田市 和田地区：和田县，星玉县
14Point W1492 新疆维善尔自治区 西北诸河 喀什河伊州控制单元 喀什河 喀什河大桥 II 伊型 伊宁县 伊率哈萨克自治州：尼勒克
16Point 15Point W1493 新疆维普尔自治区 西北诸河 开都河巴音榜聚古自治州拉制单元 开都河 哈尔英教 I1 巴音邦 和静县 巴音郭榜票古自治州：和静 昌吉回族自治州：卓崇市，
17Point W1494 新疆维晋尔自治区 西北堵河 开屋河昌吉州控制单元 开星河 老奇台 I1 II 昌吉 新台县
W1495 新疆维普尔自治区 西北诸河 克孜河克孜勒苏柯尔克孜自治州控制单元 克孜河 三级电站 I1 I1 喀什 疏附县 喀什地区：疏附县：克孜勒
18Point W1496 新疆维哥尔自治区 西北堵河 孔雀河巴音都楞聚古自治州汇合口拉制单元 孔雀河 汇合口 I1 II 巴营邦 时县 巴音郭楞戴古自治州：摩尔
19Point W1497 新疆维荟尔自治区 西北诺河 孔雀河巴音楞乘古自治州兰干控制单元 孔省河 兰干 巴音扣 库尔勒市 巴音楞蒙古自治州：库尔
20Point W1498 新疆维著尔白治区 西北诸河 奎屯河塔城地区控制单元 雀屯河 老龙口 I1 II 审型 雀屯市 塔城地区：乌苏市
21Point W1499 新疆维普尔自治区 西北堵河 查屯河伊翠州拉制单元 座屯河 黄沟二库 胡杨河 克拉玛依市：独山子区：伊犁
22Point W1500 新疆维吾尔自治区 西北墙河 赛里木湖博尔塔拉豪古自治州控制单元 赛里木湖 湖2 III 博尔塔 博乐市 博尔塔拉蒙古自治州：博乐
23Point W1501 新疆维吾尔自治区 西北清河 三屯河昌吉州拉制单元 三屯河 三屯河首 II 昌吉市 品古回族自治州： 昌吉市，
24Point W1502 新疆维晋尔自治区 西北诸河 水磨河乌鲁木齐市拉制单元 水河 七纺桥 IV IV 乌餐木 水磨沟区 乌餐木齐市： 米东区，沙依
25Point 26Point T1503 新疆维普尔自治区 西北诸河 塔里木河阿克苏地区控制单元 塔里木河 轮台 贰化物不参与 阿克苏 轮台县 阿克苏地区：拜城县，库车
W1504 新疆维吾尔白治区 西北诸河 塔里木河巴音郭楞豪古自治州拉制单元 塔里木河 尉 赢化物不参与 巴音 时华县 伊翠哈萨克自治州：特克斯 巴音楞豪古自治州：轮台
27Point W1505 新疆维普尔自治区 西北诸河 特克斯河伊翠州科布大桥控制单元 特克斯河 科布大桥 II 特克斯县
28Point W1506 新疆维普尔自治区 西北堵河 特克斯河伊型州龙口大桥控制单元 特克斯河 龙口大桥 I1 II 伊率 巩留县 伊翠哈萨克自治州：巩留县
29Point W1507 新疆维吾尔自治区 西北诸河 提孜郑南河喀什地区控制单元 提孜那甫河 萨依巴格 II 客什 叶城县 喀什地区：叶城县，泽普县
30Point W1508 新疆维晋尔自治区 西北堵河 托什干河阿克苏地区控制单元 托什干河 阿热力 II 阿克苏 温宿县 阿克苏地区：温宿县，乌什
31Point W1509 新疆维晋尔自治区 西北诸河 乌鲁木齐河乌鲁木齐市青年渠拉制单元 乌鲁木齐河 青年 II 乌鲁木 天山区 乌鲁木齐市：达板城区，乌鲁
32Point W1510 新疆维吾尔自治区 西北诸河 乌鲁木齐河乌鲁木齐市英维桥拉制单元 乌鲁木齐河 英雄桥 II II 乌鲁木 乌鲁木齐 乌鲁木齐市：新市区
33Point W1511 新疆维善尔自治区 西北堵河 乌鲁木齐河乌鲁木齐市跃进桥控制单元 乌鲁木齐河 跃进桥 11 I1 乌鲁木 乌鲁木齐 乌鲁木齐市： 乌鲁木齐县
35Point 34Point W1512 新疆维吾尔自治区 西北堵河 乌伦古湖阿勒泰地区控制单元 乌伦古河阿勒泰地区控制单元 乌伦古河 项山 II1 阿勒 福海县 阿勒泰地区： 高道县， 青河
36Point W1513 新疆维普尔自治区 西北诸河 乌伦古湖 南邮渔政点 V- COD. 氧化物 阿动泰 福海县 阿勒泰地区：福海县， 吉木
37Point W1514 新疆维晋尔自治区 西北堵河 乌伦古潮码头 V- COD. 氧化物 阿动 福海县
38Point W1515 新疆维善尔自治区 西北诸河 西北诸河 叶尔莞河喀什地区阿瓦提镇拉制单元 乌伦古湖湖中心 V- COD. 氧化物 阿勒泰 福海县 莎车县 喀什地区：巴楚县，麦盖捷
39Point W1516 新疆维普尔自治区 叶尔莞河 阿瓦提镇 II II 喀什
40|Point W1517 新疆维萧尔自治区 西北诸河 叶尔莞河喀什地区卡群控制单元 叶尔莞河 卡群 客什 莎车县 喀什地区： 莎车县， 塔什库
w1518 西北请河叶尔羊河域什协区依干基济口格制单元 叶尔羊河 依干基济口 TTT ITTT 苏车 什协区： 药车县、
1 (0outof55Selected)
water station] water_shtation_e

### 第 142 页

![page 142](003-GIS-空间数据-知识点回顾/page_142.jpg)

ArcGIS中字段类型 (type)
Field Type Explanation ExainplesShort Integersstored as2-bytebinarynumbers 255
Rangeofvalues-32,000 to+32,000 12001
Long Integersstored as10-bytebinarynumbers 156000
Rangeofvalues-2.14billionto+2.14billion 457890
Floating-point values witheight significant digits in 1.289385e12
Floatthemantissa 1.5647894e-02
Double Double-precision floating-point valueswith 161.12114118119141e13
significantdigitsin themantissa
"MapleSt'
Text Alphanumericstrings
‘JohnH.SmithDate 07/12/92
Dateformat10/17/63
Binarylargeobject;anycomplexbinarydataBLOB*
includingimages,documents,etc.
>Short/Long: 整数（Integer）
>Float/Double：小数（Float）

### 第 143 页

![page 143](003-GIS-空间数据-知识点回顾/page_143.jpg)

Integer vs. float
》为了存储十进制数据，电脑采用科学计数
法进行存储（包含小数和指数部分）
3.2957239e04 = 32957.239
-3.2957239e04 = -32957.2393.2957239e-04 = 0.00032957239
数学中的科学计数法：
3.2957239 x 104 = 3.2957239e04

### 第 144 页

![page 144](003-GIS-空间数据-知识点回顾/page_144.jpg)

Float数据精度
》较大的数字开始出现精度丢失，因为尾数
中有效数字的数量是有限的（如）。
·3295723956249.723
·3.2957239e12 = 3295723900000
>双精度浮点数据（double）为尾数值分配
了更多的存储空间
·3.295723956249723e12 =3295723956249.723

### 第 145 页

![page 145](003-GIS-空间数据-知识点回顾/page_145.jpg)

ArcGIS 属性表界面
调整字段宽度
将鼠标悬停
cd110
OBJECTID* Shape NAME ARTY DISTRICTID STFIPS STATE 在两字段交
Polygon Robert A.Brady mocrat 4201 4222422422422 PA2Polygon ChakaFattah Democrat 4202 AAAAAAA 界处，鼠标
3Polygon PhilEnglish Republican 42034Polygon Jason Atmire Democrat 42045Polygon John E.Peterson Republican 4205 呈双箭头后
6Polygon JimGerlach Republican 42067Polygon JoeSestak Democrat 4207 拖动
8Polygon PatrickJ.Murphy Democrat 4208
(0outof437Selected)
US Counties
·临时变化，不会影响文件的存储

### 第 146 页

![page 146](003-GIS-空间数据-知识点回顾/page_146.jpg)

ArcGIS 属性表界面
Field Properties 鼠标右键单价字段
Table Name: 名称
Alias: POINT_XDian_A Calcu Type: DoubleFID Sha rC OINTX POINT_YOPoint Prope Display SortAscending 3729637729249323858828
Paint TurnfieldoffStatisticsof Dian_ Coc SortDescendingMakefieldreadonly AdvancedSorting...
FieldPOINTX Highlight fieldStatistics: Number Format: Numeric Summarize...
Minimum:779045.79 Count: 4856 Statistics...
Maximum:796885.44 DataSum: 3838514551 FieldCalculator...
Mean: 790468.40 Units: PrecisionStandardDeviation:2 CalculateGeometry...
Nulls: 0 ScaleTurnFieldOffAbou-
18 Point 15101 3081 DeleteField19PointOK Cancel Properties...
ApplyDianA dem30m
展状态栏
有

### 第 147 页

![page 147](003-GIS-空间数据-知识点回顾/page_147.jpg)

ArcGIS 属性表界面
Field Properties POP2010 POP2010
Name: POINTY 1309580 1,310,000
NumberFormat6756150 6.760,000
Category:
None Rounding 983932 984,000
Curency Numberof decimal placesNumenc Numberof significant digits 1338645 1,340,000
DirectionPercentageCustom 662194 662,000
Rate AlignmentFraction 827263 827,000
Scientific LeftAngle ORight characters548154 548.000
Show thousands separatorsPadwithzerosShow plus signGeneraloptionsforthedisplayof numbers 》小数位数、数字有效位数
OK Cancel 对齐方式
OK Cancel Apply 位数补齐...

### 第 148 页

![page 148](003-GIS-空间数据-知识点回顾/page_148.jpg)

ArcGIS 属性表界面
选项菜单
三
Find and Replace...
电 Select By Attributes... SUB_REGION STATEABB POP2000 POP2007 POPOO SQMI POIClear Selection Pacific HI 1211537 1299555 189.9
SwitchSelection Pacific WA 5894121 6516384 87.6
SelectAll Mountain MT 902195 959171 6.1
NewEngland ME 1274923 1352536 39.6
AddField... West North Central ND 642200 657816 9.1
Turn AllFields On WestNorthCentral SD 754844 805562 9.8
ShowField Aliases Mountain WY 493782 523174 5
Arrange Tables NewHorizontal TabGroup 5363675 5687426 95.6
NewVertical TabGroup 1293953 1513708 15.5
Restore Default Column WidthsRestoreDefaultFieldOrder Move toPreviousTab GroupJoins and Relates Move to Next Tab GroupRelated TablesCreate Graph...
Add TabletoLayoutReload CachePrint...
ReportsExpor...
Appearance...

### 第 149 页

![page 149](003-GIS-空间数据-知识点回顾/page_149.jpg)

ArcGIS属性表界面
Select byAttributes
关找切换选 删除选中项
EnteraWHEREclause toselectrecordsinthe tablewindow.
Method: Create anew selection
"FID"
Table "Id"
"ID_T"
"markero"
"markerG"
StatesSTATENAME STATEFIPS SUB REGION ST <> LikeHawail 15 Pacific AndFind and Replace.... Pacific
<= OrSelectBy Attributes.... MountainClear Selection NewEngland 0 NotWestNorth Central Get Unique Values GoTo:
Switch Selection WestNorth Central Is In NullSelectAll Mountain SELECTFROMDian_AWHERE:
AddField... EastNorthCentralTurn All FieldsOn Mountain IDShow Field Aliases 191
(0outof51Selected) 12121212
ArrangeTables 661661 Clear Verify Help Load. Save.
Restore Default Column WidthsApply CloseRestore DefaultField OrderJoins and RelatesRelated Tables

### 第 150 页

![page 150](003-GIS-空间数据-知识点回顾/page_150.jpg)

ArcGIS属性表界面一查询 (query)
Select by Attributes 面
Find&keplaceEnteraWHEREclauseto selectrecordsin the tablewindow. 面 SelectByAttributes...
Method: Create a new selection ClearSelection
"FID" SwitchSelection
"Pl SelectAll
"ID_T""
"markerO" 一些有效的查询
"markerG"
Like "POP1990">1000000
"STATE NAME"=‘AlabamaNot [POP2000]>=[POP1990]
Null Get UniqueValues GoTo:
SELECT·FROMDian AWHERE: DBF表格的字段名用引号括起
来("")
1919191919 Clear Venfy Hep Load... Save. Geodatabase表的字段名用方括
Apply Close 号括起来(1)

### 第 151 页

![page 151](003-GIS-空间数据-知识点回顾/page_151.jpg)

ArcGIS属性表界面一查询 J（query)
>使用AND或OR进行多个条件查询
"STATE"=‘Alabama’OR"STATE"="Texas’
[Value]>5000AND[Value]<100005000<[Value]<10000

### 第 152 页

![page 152](003-GIS-空间数据-知识点回顾/page_152.jpg)

显示选定项目
SELECT*FROMstatesWHERE:
"P0P2000">2000000
Table xUS States XOBJ Shape NAME ST SUB REGION ABBR POP2000 POP20107 Polygon Wyoming 56 Mountain WY 493782 548.0008 Polygon Wisconsin 55 East North Central WI 5363675 5.740.0009 Polygon Idaho 16 Mountain10 Polygon Vemont 50 NewEnglar Table112 Polygon Minnesota 27 WestNorthPolygon Oregon 41 Pacific13 Polygon New Hampshire 33 NewEnglar US States X1415 Polygon lowa 19 West North OBJ Shape NAME ST SUBREGION ABBR POP2000 POP2010
Polygon Massachusetts 25 NewEnglar Polygon Washington 53 Pacific WA 5894121 6,760.00016Polvaon Nebrask. North 8 2 Polygon Wisconsin 55 East North Central WI 5363675 5.740.00011 Polygon Minnesota 27 West NorthCentral MN 4919479 5.330.0000 (34outof51Sele 12 Polygon Oregon 41 Pacific OR 3421399 3.870.000
USStates 14 Polygon lowa 19 West NorthCentral IA 2926324 3,060,00015 Polygon Massachusetts 25 New England MA 6349097 6.560.00017 Polygon NewYork 36 MiddleAtlantic NY 18976457 19,500,00018 Polygon Pennsylvania 42 Middle Atlantic PA 12281054 12,600,00019 Polygon Connecticut 09 NewEngland CT 3405565 3.540.00021Polvaon 34 lleAtlantic NJ 8414350 8.820.000
(34outof51 elected)
USStates

### 第 153 页

![page 153](003-GIS-空间数据-知识点回顾/page_153.jpg)

添加字段
Table 口
xinjiang_cityFID Shape ARBA PBRIMBTBR SHID SHI_D_ID SHI OI0Polygon 116798000000 2096580 10 9 654300
Table 1 Polygon 94874500000 2687920 12 6542003Polygon 2 Polygon 3031240 10716.4 16 65900020032500 34022.8 20 23 23 2229333340 19 18 6590004Polygon 896150000 175066 19 659000
Polygon 7334930000 633100 22 6502006 Polygon 24853600000 985175 24 652700
Polygon 55391000000 1678520 26 6540008Polygon 26657500000 924662 28 6523009Polygon 1171760000 189288 32 65400010 Polygon 46828900000 1138420 33 65230011 Polygon 14202700000 1033380 37 65010012 Polyson 399172000 106625 42 39 65020013 Polygon 137217000000 1691910 40 65220014Polygon 457281000 114874 41 659000 try...
15 Polygon 740451000 227948 43 42 65900016 Polygon 471538000000 4310220 103 102 65280017 Polygon 69325800000 1445060 189 188 65210018 Polyeon 127783000000 2271210 190 189 652900 Lolumn19 Polygon 69899200000 2489520 216 215 65300020Polygon 167685000000 2756660 257 256 62090021 Polygon 111463000000 3401670 259 258 65310022 Polygon 3927410000 419426 260 259 65900023 Polyson 1915670000 331813 266 265 659000 Cancel24Polygon 248088000000 2732210 272 271 65320025 Polygon 253024000000 3282980 659 658 63280026Polygon 337204000000 4618910 828 827 54250027 Polygon 352242000000 4892010 836 835 54240028Polveon 204940000000 3502800 878 877 632700
在添加字段之前，一定考虑好字段名称/类型！

### 第 154 页

![page 154](003-GIS-空间数据-知识点回顾/page_154.jpg)

Adding multiple fieldsFeature ClassProperties ？ XIndexes Subtypes Relationships RepresentationsGeneral XYCoordinate System Tolerance Resolution Domain Fields
>Catalog窗口 FieldName Data TypeHSE_UNTS Long IntegerVACANT LongIntegerOWNER_OCC Long Integer
空白行输入字段名 RENTER_OCC LongIntegerNO_FARMS07 DoubleAVG_SIZE07 DoubleCROP_ACR07 Double
设置字段数据类型 AVG_SALE07 DoubleSQMI LongIntegerShape_Length Double
设置字段属性，如别 Shape_Area DoubleHISP_PERCShort Integer
名、空值、默认值等 Click any field to seeits properties. LongIntegerField Properties Float DoubleAlias HISP_PERC Text
应用设置 AllowNULLvalues Yes Date BlobDefaultValue GuidRasterImport...
Toaddanewfeld,typethenameintoanemptyrowintheFieldNamecolumn,likintheData Typecolumn to choose the data type,then edit theFieldProperties.
慎重确定字段名称和字段
的数据类型
OK Cancel Apply

### 第 155 页

![page 155](003-GIS-空间数据-知识点回顾/page_155.jpg)

Adding multiple fieldsCatalog窗口→选中目标文件点击鼠标右键→propertiesShapefileProperties FeatureClassPropertiesGeneralXY CoordinateSystemFieldsIndexesFeature Extent General EditorTrackingIndexes Subtypes Feature Extent Relationships RepresentationsXY CoordinateSystem Domain,ResolutionandTolerance FieldsFieldName DataTypeFID ObjectID FieldName Data TypeShape LongInteger Geometry OBJECTID Shape ObjectID Geometryexp Float AREA PERIMETER Float FloatSHENG_ Long IntegerSHENG_ID Long integerSHENG ShortIntegerShape_Length name TextDoubleShape_Area DoubleClickanyfeld toseeitsproperties. Clickanyfield to see its properties.
Field Properties FieldPropertiesPrecision 0 Alias OBJECTDScaleToaddanewfeld，typethenameintoanemptyrowintheFieldNamecolumn，likin ToaddanewfeldtyethenameintoanemptyrowinthFieldNamecolumndikinthe Data Type column to choose the data type,thenedithe Field Properties. the Data Type column to choose the data type,then edit the Field Properties.
确定 取消 应用（A） 确定 取消 应用（A)

### 第 156 页

![page 156](003-GIS-空间数据-知识点回顾/page_156.jpg)

字段编辑与计算
Editing and calculating fields

### 第 157 页

![page 157](003-GIS-空间数据-知识点回顾/page_157.jpg)

编辑记录
开始编辑
Start EditingThismap contains datafrommore thanonedatabase orfolder.
Pleasechoose thelayerorworkspace toedit. Editordem30m.vatDian_A 选中需要编辑的图 StartEditing
层，并点击OK Stop EditingSaveEditsDoyou want to saveyouredits? 存编辑、停止编辑
是(M） 否（N) 取消
EditorSource Typee:\spatialdata\dem30\dem30m\ ArcInfo Workspace Start EditingG:\Rs_InterpretationspatialPointsClustered Shapefiles/dBaseFilesStop EditingSave EditsAboutediting andworkspaces OK Cancel

### 第 158 页

![page 158](003-GIS-空间数据-知识点回顾/page_158.jpg)

字段计算
SortAscendingField Calculator ？
SortDescendingAdvanced Sorting... ParserVBScript PythonSummarize... Fields: Type: Functions:
Shape ONumber Abs()
Statistics... STATE_NAME At()
STATE_FIPS sting Cos()
Field Calculator... SUB_REGION Exp() Fix（)
Date Int()
CalculateGeometry... STATE_ABBR Log(）
POP2000 Sin()
TurnFieldOff POPOO_SQMI POP2010 ()bs Tan()
Freeze/UnfreezeColumn POP10_SQMIshowCodeblock &
DeleteField +
Properties.. [HISPANIC]/[POP2000]*100
选择字段，点击右键；
计算的字段通常为“空字段
字段计算无法执行撤销操作， Clear Load... Save... Hep
除非是在编辑模式下 OK Cancel

### 第 159 页

![page 159](003-GIS-空间数据-知识点回顾/page_159.jpg)

字段计算 （高级处理）
级类型 二级类型
编号 名称 编号 名称 含义
水域 指天然陆地水域和水利设施用地。
41 河渠 指天然形成或人工开挖的河流及主干常年水位以下的土
地。人工渠包括堤岸。
42 湖泊 指天然形成的积水区常年水位以下的土地。
43 水库坑 指人工修建的蓄水区常年水位以下的土地。
塘
永久性
44 冰川雪 指常年被冰川和积雪所覆盖的土地。
地
45 滩涂 指沿海大潮高潮位与低潮位之间的潮浸地带。
46 滩地 指河、湖水域平水期水位与洪水期水位之间的土地。 LUC1995.TIF
城乡、工 OID Value Count
矿、居民 指城乡居民点及其以外的工矿、交通等用地。 0 11 6738377
用地 218345842 1506090851 地 城镇用 指大、中、小城市及县镇以上建成区用地。 3 94174234 898738152 农村居 民点 指独立于城镇以外的农村居民点。 6 1577774 294277550453153 其它建指厂矿、大型工业区、油田、盐场、采石场等用地以及交 设用地通道路、机场及特殊用地。 8 13503685195
未利用土 10 1122
b 地 目前还未利用的土地，包括难利用的土地。 72411
指地表为沙覆盖，植被覆盖度在5%以下的土地，包括沙 1105561 沙地 漠，不包括水系中的沙漠。 204555653462 戈壁 指地表以碎砾石为主，植被覆盖度在5%以下的土地。 26974

### 第 160 页

![page 160](003-GIS-空间数据-知识点回顾/page_160.jpg)

字段计算 （高级处理）
FieldCalculator FieldCalculatorParser ParserOvBScript OPython OVBScript OPythonFields: Type: Functions: Fields: Type: Functions:
OID ONumber Abs（) Atn(） OID ONumber .conjugateOValue Ostring (so Value .denominatorOCount Exp() Count Ostring .numeratorO .imag0
luc ODate Fix(） luc ODate .realoInt（) .as_integer_ratio0
Log() .fromhexoSin(） .hexoSqr(） .is_integerOTan() math.acos()
math.acosh()
math.asin()
showCodeblock ShowCodeblockluc= Pre-Loqic Script Code:
deftransform(x):
if0<x<20: return耕地”
elif20<=x<30:
return“林地”
elif30<=x<40:
rehn草+thtransform(!Value!jAboutcalculatingfields Clear Load... Save... Aboutcalculatinq fields Clear Load... Save...
OK Cancel OK Cancel

### 第 161 页

![page 161](003-GIS-空间数据-知识点回顾/page_161.jpg)

字段计算 （高级处理）
Python代码 1221 22
def transform(x): 23 2431 32
if0<x<20: 41 33
return"耕地" □42 4346 51
elif20<=x<30: 52 53
return"林地"
elif30<=x<40:
return"草地"
elif40<=x<50:
return"水域"
else:
return"建筑用地” LUC1995
津筑电 ucLUC1995.TIF 材地 水城
普联地
OID Value Count luc0 11 6738377 耕地
21834584耕地
2 15060908 林地
9417423 林地
4 8987381 林地
5 294277 林地
6 1577774 苹地
5504531 苹地
8 135036草地
9 85195水城
1122水城
72411水城
11055水城
204555注筑用地
6534注筑用地
26974注筑用地

### 第 162 页

![page 162](003-GIS-空间数据-知识点回顾/page_162.jpg)

ArcGIS中的除法
>数学中1/2=0.5;
>ArcGIS软件常用Python2.7进行工具的编写；
>在python2.7中/表示除法（IntegerDivision），
1/3=0,1/2=0,2/3=0,5/2=2，向下取整
>避免错误：将Integer转化为float.
E.g. 1.0/3 = 0.33, 1/2.0=0.5, 2.0/3.0 = 0.67, 5.0/2 = 2.5

### 第 163 页

![page 163](003-GIS-空间数据-知识点回顾/page_163.jpg)

矢量数据的几何测量
自动创建与维护（Geodatabasefeaturesclasses)
字段通常位于属性表的末端
·Shape_AreaShape_Length
单位将匹配坐标系中的单位
US StatesAVG_SIZE07 CROPACROAVG_SALE07 SQMI ShapeLength Shape_Area149 177626 68.29 10931 1275835.715167 16513001143.5337381 7609210 172.92 71297 3004175.455006 164442316568.0452079 18241710 94.94 14703 2859079.544323 359662292212.805166 529253 75.86 39555 1804888.364454 78384814218.17521241 27527180 190.31 70698 1753454.614357 173072126682.4011401 19094311 210.8 77115 1943874.72695 187970221480.162726 2576017 104.58 97813 1960001.350821 238004239410.541194 10116279 114.2959822 1968992.210358 136605586997.204
(0outof51Selected)

### 第 164 页

![page 164](003-GIS-空间数据-知识点回顾/page_164.jpg)

矢量数据的几何测量 （Shapefile）
>Shapefiles不会自动创建或维护Area/Length
字段！
·必须手动创建和更新
一些函数和操作可以改变features的长度和面积
如果您找到一个AREA字段，则不能保证它是
正确的.
watershedsFID Shape AREA PERIMETER NAME AREA_ACRE0Polygon 5265900 16620 Nameless Cave 1301.231 Polygon 765900 5700 RobbinsdaleParkEast 189.2572 Polygon 1311120 27480RedRockCanyon 3239.84013Polygon 2283300 9780 WonderlandDrive 564.213014 Polygon 511200 4140 Highway79IndustrialPark 126.325 Polygon 4786200 15780 SouthRobbinsdale 1182.68999 Polygon 1192060 25782.6 Landfil 2945.62991014020 22000.6 TeolDD 2505.C000

### 第 165 页

![page 165](003-GIS-空间数据-知识点回顾/page_165.jpg)

Be careful!
Table XwatershedsFID Shape AREA PERIMETER NAME AREAACRE PERCENT Shapefiles文件
0 Polygon 5265900 16620 Nameless Cave 1301.23 3.0465
Polygon 765900 5700 RobbinsdaleParkEast 189.257 0.443099 发生变化时
2 Polygon 1311120 27480 Red RockCanyon 3239.8401 7.585283 Polygon 2283300 9780 WonderlandDrive 564.21301 1.320974 Polygon 511200 4140 Highway79 Industial Park 126.32 0.295747 （裁剪、融合、
5 Polygon 4786200 15780 South Robbinsdale 1182.6899 2.768986 Polygon 1192060 25782.6 Landfill 2945.6299 6.89646
Pahinan 1014020 220086 TnilR.Pae 25056899 586647 编辑）属性表
(0outof26Selected) 中的
watershedsAREA/LENGTH/PERIMETER字段不会
自动更新。
Before After

### 第 166 页

![page 166](003-GIS-空间数据-知识点回顾/page_166.jpg)

使用几何计算工具
选择空字段或需更
新字段，点击右键 选择需要计算的几何类
选择“Calculate 型、坐标系以及单位
GeometryCalculateGeometry ？
AREAACRE PERCENTIE Property: Area13012 SortAscending Coordinate System189.2 SortDescending OUsecoordinatesystem of thedata source:
3239.84 PCS:NAD 1927UTMZone 13N564.213 Advanced Sorting..
126. Usecoordinate systemof thedata frame:
1182.68 Summarize... PCS:North America Equidistant Conic2945.62 Statistics...
250568 Units: Acres Us[ac]
Field Calculator...
Calculate Geometry... Calculate selectedrecordsonlyTurnField Off Help OK Cancel

---

## PDF: 知识点回顾
> 页数: 169

### 第 1 页

![page 1](004-空间数据-知识点回顾/page_001.jpg)

知识点回顾
如何更改MIXD文件中数据框/层名称？
在需要更名的数据层上单击左键，选定数据层，
再次单击左键，数据层名称进入可编辑状态
输入新名称。
选定数据层一图层属性 主（Properties）一常规
（General）→图层名称（LayerName）
不会修改Windows系统下文件名称！

### 第 2 页

![page 2](004-空间数据-知识点回顾/page_002.jpg)

知识点回顾
MXD文件中调整数据层顺序的原则？
数据层在内容表中的排序，直接影响输出地图
中的表达效果。
(1)按点、线、面要素类型依次由上至下排列;
(2)按要素重要程度的高低依次由上至下排列;
(3)按要素线划的细粗依次由下至上排列;
(4)按要素色彩的浓淡程度依次由下至上排列。
清晰直观的地图表达，不能遮挡主要要素！！！
内容列表模式：按绘制顺序列出

### 第 3 页

![page 3](004-空间数据-知识点回顾/page_003.jpg)

知识点回顾
MXD文件中如何复制、删除数据层？
Table Of Contents 口X
①在内容列表中选
中需复制的数据层 日 LayersRiverNetCounty
（按Ctrl或Shift选择
WaterArel
多个数据层); CopyHefeiRSimage Remove
②点击鼠标右键； GroupTurn On
③在弹出快捷菜单 TurnOffCreate LayerPackage...
中选择复杂(copy)；
Zoom To LayersVisibleScale Range

### 第 4 页

![page 4](004-空间数据-知识点回顾/page_004.jpg)

知识点回顾
MXD文件中如何复制、删除数据层？
④选中数据层需要 Table OfContents 口X
。三
复杂到的数据框；
TableOf Contents5点击鼠标右键：
6在弹出快捷菜单 LayersRiverN
中选择粘贴(Past)。 CopyRiverN
选中图层→点击鼠 WaterA Remove
+ County Group
标右键→删除
+ City Turn On
(remove)。

### 第 5 页

![page 5](004-空间数据-知识点回顾/page_005.jpg)

知识点回顾
文件连接 （FolderConnections）如何操作？
AddDataLookin: Home-Documents\ArcGISHome-Documents\ArcGISFolderConnections ments\ArcGISToolboxes ctionsDatabaseServers tToFolder...
Database ConnectionsGISServersMyHostedServices DATAReady-To-UseServicesName: Add nnectionsShow of type: Datasets,Layers andResults CancelervicesleServicesTracking Connections

### 第 6 页

![page 6](004-空间数据-知识点回顾/page_006.jpg)

知识点回顾
新建、删除矢量文件/文件夹如何操作？
Catalog 口x
←价鞋
选中目标文件 Location: ArcGIS_3rdHome-Documents\ArcGIS
夹→点击鼠标 日 FolderConnections
$RECYCLE.BIN Folder
右键→新建 ArcGIS3r Copy
+ Desktop File Geodatabase
+ document Paste PersonalGeodatabasedownload DeleteGIS_map Rename Database Connection...
NoteExpr ArcGiSServer Connection...
选中目标文件 Notes RefreshIdd Layer...
Report New GroupLayer
夹→点击鼠标 source_co Item Description... PythonToolboxSubject Properties...
Shapefile....
右键→删除 Turn Feature Clas...
ToolboxdBASETableLAS DatasetAddressLocator..
Composite AddressLocator..
XMLDocument

### 第 7 页

![page 7](004-空间数据-知识点回顾/page_007.jpg)

知识点回顾
ArcGIS中如何使用在线地图？
AddWMTSServer
选择“GISServers"
Examples:   双击“AddWMTSVersion: Default versionCustom Parameters Server";
Parameter Value
设置“URL";
Server LayersGetLayers 点击“get layers"；
-Layers LimgTle Matrix Sets 确定OK
白-c1:295829355.4545662:147914677.7272833:73957338.8636414:36978669.4318215:18489334.7159106:9244667.3579557:4622333.6789788:2311166.8394899:1155583.41974410:577791.709872
Account(Optional)
User:
Password: SavePasswordOK Cancel

### 第 8 页

![page 8](004-空间数据-知识点回顾/page_008.jpg)

知识点回顾
Geoprocessing地理处理框架中环境设置有什
么作用？
Environment Settings
环境设置会影响工 Workspace
具和命令的运行； xYResolutionandToleranceMValues
在应用程序级别或 ZValuesGeodatabase
运行工具时设置； GeodatabaseAdvancedFieldsRandom Numbers
应用程序级别设置 CartographyCoverage
与地图文档一起保 RasterAnalysisRasterStorage
存。 TerrainDatasetOK Cancel ShowHelp>>

### 第 9 页

![page 9](004-空间数据-知识点回顾/page_009.jpg)

1.3Geoprocessing地理处理框架
>ArcToolbox内容简介 环境设置
Environment Settings x
环境设置会影响工 Workspace
具和命令的运行； xYResolutionandToleranceMValues
在应用程序级别或 ZValuesGeodatabase
运行工具时设置； GeodatabaseAdvancedFieldsRandomNumbers
应用程序级别设置 CartographyCoverage
与地图文档一起保 RasterAnalysisRasterStorage
存。 TerrainDatasetOK Cancel Show Help>>

### 第 10 页

![page 10](004-空间数据-知识点回顾/page_010.jpg)

1.3Geoprocessing地理处理框架
>ArcToolbox内容简介 环境设置
Geoprocessing Customize Windows Intersect XBuffer InputFeaturesIntersect Features Ra...
Union GeologyWatershedsMergeDissolveSearchForToolsArcToolbox OutputFeature ClassEnvironments... C:gisclass\mgisdataRapidcity\chap6pptdata.gdb\geolwatsResults JoinAttributes(optional)
ModelBuilder xYTolerance(optional)
Python OutputType(optional)
INPUTOK Cancel Environments... Show Help>>
Geoprocessing Options...
影响所有工具和菜单 影响一个工具的一次执行

### 第 11 页

![page 11](004-空间数据-知识点回顾/page_011.jpg)

空间数据的采集与组织
NationalView

### 第 12 页

![page 12](004-空间数据-知识点回顾/page_012.jpg)

本章内容
一、矢量数据组织
二、栅格数据组织
三、创建地理数据库
四、数据采集
五、数据编辑

### 第 13 页

![page 13](004-空间数据-知识点回顾/page_013.jpg)

》空间数据采集是指将现有的地图、外业观
测成果、航空相片、遥感图像、文本资料
等转成计算机可以识别处理的数字形式
>数据采集可分为属性数据采集和图形数据
采集。
表示空间实体的位置、形状、
地理空间数据
大小及其分布特征的数据。
地理
数据
表示空间实体的属性特征、
非地理空间数据
是对地理空间数据的说明。

### 第 14 页

![page 14](004-空间数据-知识点回顾/page_014.jpg)

》空间数据采集是指将现有的地图、外业观
测成果、航空相片、遥感图像、文本资料
等转成计算机可以识别处理的数字形式
>数据采集可分为属性数据采集和图形数据
采集。
>数据组织就是按照一定的方式和规则对数
据进行归并、存储、处理的过程。数据组
织的好坏，直接影响到GIS 的性能。

### 第 15 页

![page 15](004-空间数据-知识点回顾/page_015.jpg)

> *此页无文字*

### 第 16 页

![page 16](004-空间数据-知识点回顾/page_016.jpg)

DH JX1

### 第 17 页

![page 17](004-空间数据-知识点回顾/page_017.jpg)

★ TSGTSG DH

### 第 18 页

![page 18](004-空间数据-知识点回顾/page_018.jpg)

》空间数据采集是指将现有的地图、外业观
测成果、航空相片、遥感图像、文本资料
等转成计算机可以识别处理的数字形式
>数据采集可分为属性数据采集和图形数据
采集。
>数据组织就是按照一定的方式和规则对数
据进行归并、存储、处理的过程。数据组
织的好坏，直接影响到GIS 的性能。

### 第 19 页

![page 19](004-空间数据-知识点回顾/page_019.jpg)

>GIS中主要有矢量、栅格、点云和地理数据
库（geodatabase）四种数据组织方式。
矢量数据组织包括点、线、面数据以及拓扑关系
的组织。
栅格数据组织用于管理影像图片等不同格式的栅
格数据。
ArcGIS也可以加载和处理摄影测量或激光雷达
获得的点云数据
地理数据库是ArcGIS数据模型发展的第三代产物，
它是面向对象的数据模型，能够表示要素的自然
行为和要素之间的关系。

### 第 20 页

![page 20](004-空间数据-知识点回顾/page_020.jpg)

地理空间数据的基本结构
地理空间对象：GIS处理的客体，是现实世界中客观存在的
实体或现象
空间对象可抽象为点、线、面、体等多种数据类型及其组合
线一维 点零维
空间对象
面二维 体三维 时间四维

### 第 21 页

![page 21](004-空间数据-知识点回顾/page_021.jpg)

地理空间数据的基本结构
地理空间实体
地理空间实体是对复杂地理事物和现象进行简化抽象
得到的结果，简称空间实体，它们的一个典型特征是
与一定的地理空间位置有关，都具有一定的几何形态
分布状况以及彼此之间的相互关系
地理空间实体包括点、线、面和体等多种类型，是地
理信息系统（GIS）中用于表示现实世界中地理现象的
基本单位。

### 第 22 页

![page 22](004-空间数据-知识点回顾/page_022.jpg)

地理空间数据的基本结构
在GIS中，地理数据是表示地理位置，分布特点的自然现象和社
会现象的诸要素文件。它包括自然地理数据和社会经济数据
表示空间实体的位置、形状、
地理空间数据
大小及其分布特征的数据。
地理
数据
表示空间实体的属性特征
非地理空间数据
是对地理空间数据的说明。
地理空间数据的特征
空间特征：空 空间物体的几何特征以及拓扑关系
属性特征： 空间对象的属性信息
时间特征：地理空间数据是动态的

### 第 23 页

![page 23](004-空间数据-知识点回顾/page_023.jpg)

地理空间数据的基本结构
地理空间数据分类
根据数据来源，地理空间数据可分为以下四类：
图形数据 图像数据 实体属性数据 统计数据
数字化的 航空和航 空间实体的专 描述性
数据 天数据 题信息数据 数据
地理空间数据 非地理空间数据
栅格结构
矢量结构

### 第 24 页

![page 24](004-空间数据-知识点回顾/page_024.jpg)

地理空间数据的基本结构
图形数据的表达
以单一的坐标来表示。
(x1, y1)
点
（“代码"，1，X1，y1)
(x2, y2) 以多个坐标来表示。
线 （“代码"，3，X1，y1，X2，y2
(x3, y3)
(x1, y1) X3, y3)
(x2, y2) 以多个坐标来表示，且最后一个
(x3, y3) 坐标必须与第一个坐标重合。
面
（"代码"，4，X1，y1，X2，y2
(x1, y1) (x4, y4)
X3, y3， X4, y4, X1， y1)

### 第 25 页

![page 25](004-空间数据-知识点回顾/page_025.jpg)

地理空间数据的基本结构
图形数据的组织
点 线 面 属性表
Pt.ID X Ln.ID Pt.1 Pt.2 Pol.ID Ln.ID Pol.ID Attrib.
12345 24.5 27.4 36 73839 14628 328101 4441515 3835292842 1415167718 104.224.8 24.1 100.127.8 22.5 105.730.1 29.9 102.714.2 30.1 106.1
... ... ... ... ... .*. ... ... ...

### 第 26 页

![page 26](004-空间数据-知识点回顾/page_026.jpg)

地理空间数据的基本结构
图形数据的拓扑结构
邻接 相交 相离 包含 重合
点一点
点一线
点一面
线一线
线一面
面一面

### 第 27 页

![page 27](004-空间数据-知识点回顾/page_027.jpg)

地理空间数据的基本结构
图像数据的特征
图像数据的最小单元为像元或像素，像元或像素的数值
可用于描述客观世界中存在的现象。
图像数据的实质是像元的阵列，每个像元由行列号确定
其位置，且具有实体属性的编码值。
图像数据是地表一定面积内数据的近似、离散化的标识
图像数据的表现 图像数据的存储结构

### 第 28 页

![page 28](004-空间数据-知识点回顾/page_028.jpg)

地理空间数据的基本结构
图像数据的表达

### 第 29 页

![page 29](004-空间数据-知识点回顾/page_029.jpg)

地理空间数据的基本结构
图像数据的表达
点：表示单个像元
值
线：在一定方向上链
接成串的相邻像元的
集合
面：聚集在一起的
相邻像元的集合
层：表示一种地理属性或同一属性的不同特征

### 第 30 页

![page 30](004-空间数据-知识点回顾/page_030.jpg)

地理空间数据的基本结构
图像数据的特征 分辨率
像元大小决定了影像数据所表达对象的详细程度，像元
一般是用相同宽度和高度的方格表示。一个面对象可以
采用不同像元大小的像素数据表示，像元越小，则表达
越为精细，占用存储空间越大
像元（像素）
高度
宽度

### 第 31 页

![page 31](004-空间数据-知识点回顾/page_031.jpg)

地理空间数据的基本结构
图像数据的特征 分辨率
像素所代表地面范围的大小，或地面物体能分辨的最小单元
高空间分辨率 低空间分辨率
地物A 地物B
距离d1<分辨率
实际地物情况 不可分辨出两个地物 遥感图像上显示
地物C 地物D
距离d2>分辨率
实际地物情况 可以分辨出两个地物
遥感图像上显示

### 第 32 页

![page 32](004-空间数据-知识点回顾/page_032.jpg)

第一节
矢量数据组织

### 第 33 页

![page 33](004-空间数据-知识点回顾/page_033.jpg)

矢量数据结构概述
》矢量数据是指通过记录实体坐标及其关系，尽可
能精确地表示点、线、面等地理实体的空间位置
和形状，坐标空间为连续空间，允许任意位置、
长度和面积的精确定义。
Foresl0005S59561000 581000

### 第 34 页

![page 34](004-空间数据-知识点回顾/page_034.jpg)

一、矢量数据组织
矢量数据具有数据量少、数据精确的特点；
ArcGIS中矢量数据组织：
》基于文件系统的矢量数据组织；
》基于地理数据库的数据组织

### 第 35 页

![page 35](004-空间数据-知识点回顾/page_035.jpg)

一、矢量数据组织
矢量数据结构直接以几何空间坐标为基础，
记录采样点坐标，通过这种数据组织方式，
可以得到精美的地图：
可以对复杂数据以最小的数据冗余进行存贮、
数据精度高、存储空间小等特点，是一种高
效的图形数据结构。
ArcGIS中矢量数据组织方式：
》基于文件系统的矢量数据组织；
》基于地理数据库的数据组织

### 第 36 页

![page 36](004-空间数据-知识点回顾/page_036.jpg)

一、矢量数据组织
基于文件系统的矢量数据
>Windows文件系统下的数据组织方式，
ArcGIS有Shapefile和Coverage两种格式。
/Shapefile一GIS软件界的一个开放标准，易操
作、规范性、可与其他数据转换一应用广泛。
／Shapefile是一种用于存储地理要素的几何位置
和属性信息的非拓扑简单格式。
（可通过点、线、面来表示。 B
／Shapefile通常由多个文件组成！！！

### 第 37 页

![page 37](004-空间数据-知识点回顾/page_037.jpg)

一、矢量数据组织
基于文件系统的矢量数据
rivernet.cpg waterstation.cpg Windows系统下
rivernet.dbf waterstation.dbf
的Shapefile文件
rivernet.prj water_station.prjrivernet.sbn waterstation.shprivernet.sbx waterstation.shp.xml rivernet.shprivernet.shpwaterstation.shx Urumchi.shprivernet.shp.xmlXinjiang.cpgrivernet.shx waterstation.shpXinjiang.dbfUrumchi.cpgXinjiang.prj Xinjiang.shpUrumchi.dbfUrumchi.prj Xinjiang.sbnXinjiang.sbx ArcGIS软件下
Urumchi.sbnUrumchi.sbx Xinjiang.shp
的Shapefile文件
Urumchi.shp Xinjiang.shp.xmlUrumchi.shx Xinjiang.shx

### 第 38 页

![page 38](004-空间数据-知识点回顾/page_038.jpg)

一、矢量数据组织
基于文件系统的矢量数据
》(1).shp：用于存储要素几何的主文件;
(2).shx：用于存储要素几何索引的索引文件;
(3).dbf：用于存储要素属性信息的dBASE表;
(4).sbn和.sbx：用于存储要素空间索引的文件；
(5).prj：用于存储坐标系信息的文件;
》(6).xml：元数据，存储Shapefile的相关信息。
/各文件共同组成Shapefile，其前缀必须相同
并且各文件必须在同一目录下。

### 第 39 页

![page 39](004-空间数据-知识点回顾/page_039.jpg)

一、矢量数据组织
··国
省级行政区
Teri_Indus Total_Col1 35 Urban_to_T Vocation 5230000 DZM NAMS 黑龙江 Heilongjiang NAMSSN35.9 124 18 1650000 新蓬 Sinkiang37.5 32.43 1640000 3140000 山园 宁夏 Ningxia Shanxi45.9 35.5 0540000 Tibet30.4 38 13410000 4370000 山东 河南 Shandong36.3 41.49 17 320000 Jiangsu Henan33.2 40.22 27.81 14420000 13340000 安徽 湖北 Anhui Hubei36.3 48.67 8330000 浙江 Zhejiang39.1 40.8 27.67 29. 13430000 4360000 江西 Jiangxi Hunan34.6 23.36 75 1 530000 云南 湖商 Yunnan40 41.57 23.87 4520000 350000 贵州 福注 Fujian Cuizhou37.2 28.15 5450000 8 广西 Guangxi39.3 40. 11 55 16440000 0460000 广东 海南 Guangdong Hainan34.2 49.68 4220000 吉林 Jilin45.5 39 54.24 9210000 3120000 辽宁 天津 Liaoning Tianjing42.1 35.6 18 34.76 1630000 青海 Qinghai24.01 32.26 2620000 3610000 甘肃 陕园 Shanxi Gansu35.3 1 42.68 4150000 内乘古 Inner Mongolia33.5 40.8 26.08 33.09 2500000 兰庆 周北 Chongqing909 88.31 11 6310000 130000 上海 Hebei Shanghai58.3 77.54 0710000 4110000 北京 台湾 Beijing Taiwanoo 0 0810000 香港 HongKong34 42 26.69 0 0820000 5510000 四川 澳门 Sichuan Macau
(0out of 34 Selected)
省级行政区

### 第 40 页

![page 40](004-空间数据-知识点回顾/page_040.jpg)

一、矢量数据组织
基于文件系统的矢量数据 特点
》总的数据量没有大小限制，单张表或者
要素类的大小限制为1TB。
>使用Windows资源管理器可以对数据进
行管理。
》在Windows资源管理器下文件太多，不
容易管理。

### 第 41 页

![page 41](004-空间数据-知识点回顾/page_041.jpg)

一、矢量数据组织
基于地理数据库的矢量数据
地理数据库是一种面向对象的空间数据模型，
它对地理空间特征的表达更接近我们对现实世
界的认知。
ESRI公司研发的一种采用标准关系数据库的数
据管理模式，是一个为ArcGIS所用的数据框架，
该框架定义了ArcGIS中用到的所有的数据类型
分为个人地理数据库、文件地理数据库和企业
级地理数据库。

### 第 42 页

![page 42](004-空间数据-知识点回顾/page_042.jpg)

一、矢量数据组织
个人数据库（PersonalGeodatabase）
MicrosoftAccess数据库（.mdb）；
数据文件不能超过2GB；
》适用于个人或小规模工作组；
》仅适用于Windows，不可跨平台

### 第 43 页

![page 43](004-空间数据-知识点回顾/page_043.jpg)

一、矢量数据组织
文件地理数据库（FileGeodatabase）
》一文件夹的形式保存各类型的GIS数据；
>每个数据集在磁盘上都是一个单独的文件夹;
适用于个人或小规模工作组；
每个数据集上限1TB，超大型影像数据集可提升
至256TB；
》跨平台，Windows、Linux。

### 第 44 页

![page 44](004-空间数据-知识点回顾/page_044.jpg)

一、矢量数据组织
SDE地理数据库（ArcSDEgeodatabase）
》存储为商业的RDBMS（Oracle、SQLServer、
MySQL）;
》适用于多人或大型工作组（企业）；
支持多用户同时编辑文件；
需要RDBMS证书和ArcSED技术支撑；
跨平台，Windows、Linux。

### 第 45 页

![page 45](004-空间数据-知识点回顾/page_045.jpg)

知识点回顾
地理空间数据可分为哪几类？
根据数据来源，地理空间数据可分为以下四类：
图形数据 图像数据 实体属性数据 统计数据
数字化的 航空和航 空间实体的专 描述性
数据 天数据 题信息数据 数据
地理空间数据 非地理空间数据
表示空间实体的位置、形状、 表示空间实体的属性特征
大小及其分布特征的数据。 是对地理空间数据的说明

### 第 46 页

![page 46](004-空间数据-知识点回顾/page_046.jpg)

知识点回顾
什么是矢量数据？
》矢量数据是指通过记录实体坐标及其关
系，尽可能精确地表示点、线、面等地
理实体的空间位置和形状，坐标空间为
连续空间，允许任意位置、长度和面积
的精确定义。

### 第 47 页

![page 47](004-空间数据-知识点回顾/page_047.jpg)

知识点回顾
地理数据库有哪些类别？
个人数据库 (Personal Geodatabase)
文件地理数据库 （File Geodatabase）
SDE地理数据库（ArcSDEgeodatabase）

### 第 48 页

![page 48](004-空间数据-知识点回顾/page_048.jpg)

第二节
栅格数据组织

### 第 49 页

![page 49](004-空间数据-知识点回顾/page_049.jpg)

二、栅格数据组织
栅格数据结构概述
以规则栅格阵列表示空间对象的
数据结构称为栅格数据结构。阵
列中每个栅格单元上的数值表示
空间对象的属性特征。即栅格阵
列中每个单元的行列号确定位置
属性值表示空间对象的类型、等
级等特征。每个栅格单元只能存
在一个值。

### 第 50 页

![page 50](004-空间数据-知识点回顾/page_050.jpg)

二、栅格数据组织
栅格数据结构概述
栅格数据结构的显著特点：属性明显，定位隐含，
即数据直接记录属性的指针或属性本身，而所在
位置则根据行列号转换为相应的坐标给出，也就
是说定位是根据数据在数据集中的位置得到的。
>栅格数据的优缺点：
口优点：数据结构简单、数学模拟方便
口缺点：数据量大、难以建立实体间的拓扑关系、
通过改变分辨率而减少数据量时精度和信息量
同时受损等。

### 第 51 页

![page 51](004-空间数据-知识点回顾/page_051.jpg)

二、栅格数据组织
栅格数据结构概述
》完全栅格数据结构（也称编码）将栅格看作
一个数据矩阵，逐行逐个记录栅格单元的值。
》这是最简单最直接的一种栅格编码方法。通
常这种编码为栅格文件或格网文件，它不采
用任何压缩数据的处理。

### 第 52 页

![page 52](004-空间数据-知识点回顾/page_052.jpg)

二、栅格数据组织
创建栅格数据
位置：通常由一对有序的行列
3 3 坐标(X，Y)表示
属性：保存各种类型的数据值，
3 3 1 14 3 3 1 1 1 如整数、实数、编码和日期等。
3 3 2 2 14 2 2 2 》某一区域的单元格具有同一属
性。

### 第 53 页

![page 53](004-空间数据-知识点回顾/page_053.jpg)

二、栅格数据组织
栅格数据结构
Red-green-bluecompositeAttributevalues 255
rangefrom0 to255
ineachbandBand1 Band2
Band3

### 第 54 页

![page 54](004-空间数据-知识点回顾/page_054.jpg)

矢量数据VS.栅格数据
优点 缺点
数据结构严密，余度小，数据量小； >数据结构处理算法复杂
矢量数据 空间拓扑关系清晰，易于网络分析； >叠置分析与栅格图组合比较难；
面向对象目标的，不仅能表达属性编码 数学模拟比较困难；
而且能方便地记录每个目标的具体的 >空间分析技术上比较复杂，需要更复
属性描述信息； 杂的软、硬件条件;
>能实现图形数据的恢复、更新和综合； 显示与绘图成本比较高。
图形显示质量好、精度高。
数据结构简单，易于算法实现； 图形数据量大，用大像元减小数据量
栅格数据
空间数据的叠置和组合容易，有利于与 时，精度和信息量受损失；
遥感数据的匹配应用和分析； >难以建立空间网络连接关系；
易执行各类空间分析，地理现象模拟 >投影变化实现困难；
输出方法快速建议，成本低廉。 图形数据质量低，地图输出不精美。

### 第 55 页

![page 55](004-空间数据-知识点回顾/page_055.jpg)

第三节
创建地理数据库

### 第 56 页

![page 56](004-空间数据-知识点回顾/page_056.jpg)

三、创建地理数据库
3.1数据库基础 数据组织方式
数据是信息的具体表达形式。为了表达更有意
义的信息内容，数据必须按一定的方式进行组
织和存储。
数据的 数据库
组织
文件
数据项
记录

### 第 57 页

![page 57](004-空间数据-知识点回顾/page_057.jpg)

三、创建地理数据库
3.1数据库基础 数据项
》数据项：定义数据的最小单位，是数据记录中
最基本的、不可分的数据单元
》域：数据项的取值范围，可以是数值（整数、
小数）、字符、日期等。
域：{男、女}
姓名 学号 姓别 学院 专业
数据项 张三 20200023 男 生态与环境学院 环境科学
李四 20210123 女 外语学院 英国文学

### 第 58 页

![page 58](004-空间数据-知识点回顾/page_058.jpg)

三、创建地理数据库
3.1数据库基础 一记录
>记录（record）：由若干相关联的数据项组成，
是关于一个实体的数据总和。
·字段：同类型 ·值：记录反映 ·标识符：标识每
记录的框架。 实体的内容。 个记录的数据项。
标识符/关键字
姓名 学号 姓别 学院 专业 字段
张三 20200023 男 生态与环境学院 环境科学
记录 李四 女 外语学院 英国文学

### 第 59 页

![page 59](004-空间数据-知识点回顾/page_059.jpg)

三、创建地理数据库
3.1数据库基础 文件
>文件（file）：给定类型记录的全部具体值的集
合，用文件名称标识。
学生基本信息表
姓名 学号 姓别 学院 专业
具体
张三 20200023 男女 生态与环境学院 环境科学
值的
李四 20210123 外语学院 英国文学
集合
文件存储
JMD_M_500.dbf

### 第 60 页

![page 60](004-空间数据-知识点回顾/page_060.jpg)

三、创建地理数据库
3.1数据库基础 数据组织方式：数据库
>具有特定联系的数据集合体。
》比文件更大的数据组织。
》内部机构是文件的集合，这些文件具有某种直
接的联系，不是孤立的。
姓名 学号 表格（Table)
张三 20232123
数据
数据库 视图（View)
(data)
数据
QL 存储过程（Storedprocedure）
触发器 (Trigger)

### 第 61 页

![page 61](004-空间数据-知识点回顾/page_061.jpg)

三、创建地理数据库
3.1 数据库基础 数据组织方式：数据库
序号 物品 单价 上月结余 本月领用 本月购入 购入金额 库存 盘点数 差异 备注
1 笔 5 500 200 100 400 -4002 文件央 10 500 150 200 550 -5503 笔 5 500 200 100 400 -4004 文件夹 10 500 150 200 550 -5505 笔 5 500 200 100 400 -4006 文件央 10 500 150 200 550 -5507 笔 5 500 200 100 400 -4008 文件央 10 500 150 200 550 -5509 笔 5 500 200 100 400 -40010 文件夹 10 500 150 200 550 -55011 笔 5 500 200 100 400 -40012 文件央 10 500 150 200 550 -55013 笔 5 500 200 100 400 -40014 文件央 10 500 150 200 550 -55015 笔 5 500 200 100 400 -400

### 第 62 页

![page 62](004-空间数据-知识点回顾/page_062.jpg)

三、创建地理数据库
3.1数据库基础 数据组织方式：数据库
序 小型建筑 需要安装 不需要安装的 建筑安装 其他费用 预备费 总价值 生产准备
号 表格编号 工程费 的设备费 设备、工器具费 工程费 及开办费
（元） 人民币（元）其中外币（） （元）
IⅢI IV V VI VII VII IX X XI XI

### 第 63 页

![page 63](004-空间数据-知识点回顾/page_063.jpg)

三、创建地理数据库
3.2空间数据库 数据与数据库
空间数据库（Geodatabase）是某一区域内关于
一定地理要素特征的数据集合，一般是以一系
列特定结构的文件的形式组织在存储介质之上的。
矢量数据
属性数据
影像数据 特定的数
影像数据
据结构
矢量数据
属性数据
数据的有效
结合

### 第 64 页

![page 64](004-空间数据-知识点回顾/page_064.jpg)

三、创建地理数据库
3.2空间数据库 一主要特征
土地管理
数据集中管理
城市规划
保证不同用户和应
基础地理
用可以共享数据。 交通管理
数据库
数据具有独特性 数据共享方便
数据独立于应用程
楚河
序，提高了数据库
数据库管理 stiet
用于系统的效率和
稳定性。 数据库与应用系统
相互独立

### 第 65 页

![page 65](004-空间数据-知识点回顾/page_065.jpg)

三、创建地理数据库
3.2空间数据库 主要特征
数据余度小
解决
数据统一定义、组织和存储，集中管理， “数据孤岛”
避免了数据余，提高了数据的一致性 现象
复杂的数据模型
根节点 R1
采用复杂的数据模型组织和管理 层次
兄弟节点 R2 R3 模型
数据是以文件方式的本质区别
R4 R5 叶节点
安全性
设置登录密码和用户权限，拒绝 SQLServer2008R2
非法访问，以确保数据的安全性、 I.S
中
一致性和并发性。

### 第 66 页

![page 66](004-空间数据-知识点回顾/page_066.jpg)

三、创建地理数据库
3.2创建一个新的地理数据库
>借助ArcCatalog软件或ArcMap软件中
Catalog窗口创建地理数据库。
·本地地理数据库：个人数据库(PersonalGeodatabase)限2GB、文件地理数据库(FileGeodatabase);
·ArcSDE地理数据库：空间数据库连接

### 第 67 页

![page 67](004-空间数据-知识点回顾/page_067.jpg)

三、创建地理数据库
3.2创建一个新的地理数据库
在Catalog目录中选中文件→新建 FolderFile GeodatabaseCatalog X 一文件数据 Personal GeodatabaseCatalog Catalog ion...
Location: GIS_Example 主
品 《 nection...
+ scratch.gToolbox.t 地理数据库中的组成项包括对象
EFolderConn
一 E:
+ $RECY 类、要素类和要素数据集
ArcGI:
Desktop ArcGIS3rd GISExampledocument 田 Desktop ExampleDB.mdbdownload 田 document Example_DB.gdbGISExample 田 download + GISmap
日 GISExample NoteExpress
+ GIS_map NewPersonal NotesNoteExpress GIS_mapNotes NoteExpress ReportPPT + Notes source_code
+ Report PPT + Subject ssLocator...
Report

### 第 68 页

![page 68](004-空间数据-知识点回顾/page_068.jpg)

3.2创建一个新的地理数据库
建立要素数据集
在Catalog NewFeature Dataset 新建(New)-
要素数据集 Name: Feature_ExCatalog
←→价 Feature Dataset..
Location: Example_DB.gdbFeature Class...
+ $RECYCLE.BINArcGIS3rd Table...
+ Desktopdocument View...
peojumopGIS_Example Relationship Class...
Example DB.mdbExampleDB.gdb Raster Catalog...
GIS_mapNoteExpress Raster Dataset...
NotesPPT MosaicDataset...
Reportsource_code Schematic Dataset
+ Subject
<上一步（B) 下一页（N）> 取消 Toolbox

### 第 69 页

![page 69](004-空间数据-知识点回顾/page_069.jpg)

3.2创建一个新的地理数据库
NewFeature Dataset NewFeatureDataset NewFeatureDataset XChoose thecoordinate system that will be use Choose thecoordinate system that will be usec XY ToleranceTheXY tolerance istheminimum distancebetween coordinatesbefore theyareGeographiccoordinate systemsuselatitudear Verticalcoordinate systemsdefine the origin a considered equal.TheXY tolerance isused when evaluating relationshipsmodelof the earth'ssurface.Projected coordi define the positive direction of valuesin order Catalog 口xconversionto transform latitude andlongitudeTypehere to search 七价 >
Typehere tosearch FavoritesFavorites VerticalCoordinateSystems Location: Example_DB.gdbChina GeodeticCoordinateSyster 田 $RECYCLE.BINPCs_Transverse_Mercator 田 ArcGIS3rdWGS1984 DesktopWGS1984WorldMercator 田
GeographicCoordinate Systems 田 documentProjectedCoordinateSystems 田 downloadCurrentcoordinate system: GIS_ExampleNo coordinate system. ExampleDB.mdbCurrentcoordinate system:
WGS_1984_World_Mercator 日 Example DB.gdbWKID:3395Authority:EPSG Feature_ExProjection:Mercator 田 GIS_mapFalse_Easting:0.0 False_Northing:0.0 NoteExpressStandard_Parallel_1:0.0 Central_Meridian:0.0 田 NotesLinearUnit:Meter(1.0) 田
GeographicCoordinate System:GCS_WGS_1984 田 Report
选择高程系统 source_code
选择坐标系统
<上—步（B) Finish 取消

### 第 70 页

![page 70](004-空间数据-知识点回顾/page_070.jpg)

3.2创建一个新的地理数据库
NewFeatureClass
建立要素类（矢量文 Name:
Feature_ClassAlias: Feature
在Catalog目录中选中要 TypeType of features stored in thisfeature class:
要素类(FeatureClass.. Polygon FeaturesPolygonFeaturesLineFeaturesCatalog 口 Cop PointFeaturesMultipoint Features
>> Past MultiPatchFeatures TurnFeaturesLocation: Feature_Ex Dimension FeaturesDele AnnotationFeaturesSRECYCLE.BIN Geometry Properties
+ ArcGIS_3rd Ren Coordinatesinclude Mvalues.Used to store route data.
+ Desktop Coordinates includeZvalues.Used to store3D data.
+ document Refi
+ downloadGIS_Example MarExample_DB.mdbExampleDB.gdb NevFeatureExGIS_map ImpNoteExpressNotes ExpReport Iten
+ source_codePro <上步（B) 一页（N）> 取消

### 第 71 页

![page 71](004-空间数据-知识点回顾/page_071.jpg)

3.2创建一个新的地理数据库
NewFeatureCla NewFeatureClass XSpecifythed Field Name DataType Field Name DataTypeConfiguratid OBJECTID ObjectID ObjectIDSHAPE Geometry GeometryODefault lame Text TextThisop Catalog 口 Xtable/feOUseconf Location: Feature_ExThisop SRECYCLE.BINwhichr ArcGIS_3rdnewtal Desktop
+ documentdownloadClick anyfieldtosee itsproperties. 日 GIS_Examplesee Example_DB.mdbField Properties 日 Example_DB.gdbAlias Name Feature ExAbout Config AllowNULLvalues YesDefaultValue Feature_ClassLength 50 GIS_map
配置 田 NoteExpress
+ NotesImport.. PPTToaddanewfield,type thenameinto anemptyrowin theFieldNamecolumn,click ld,1 Reportin theData Type column to choose the data type,then edit the FieldProperties. col
按Del键删除选中字段
<上—步(B) Finish 取消 <上—步（B) Finish 取消

### 第 72 页

![page 72](004-空间数据-知识点回顾/page_072.jpg)

3.2创建一个新的地理数据库
建立关系表格
在Catalog目录中选中地理数据库→新建(New)
关系表（Table...)
Catalog 口x Copy
>> 启 Paste Feature Dataset...
Location: Example_DB.gdb Delete Feature Class...
田 $RECYCLE.BIN Rename Table...
田 ArcGIS_3rd Refresh
田 DesktopMakeDefaultGeodatabase View...
document
+ download Administration Relationship Class...
GISExampleExample DB.mdb Distributed Geodatabase Raster Catalog...
ExampleDB.gdb NewFeature_Ex RasterDataset...
Feature_Class Import
+ GIS_map MosaicDataset...
NoteExpress ExportNotes ShareasGeodataService... SchematicDatasetReport ItemDescription.. ToolboxProperties...

### 第 73 页

![page 73](004-空间数据-知识点回顾/page_073.jpg)

3.2创建一个新的地理数据库
NewTable NewTable NewTable XName: Example_Table Specify the database storage configuration. FieldName DataTvpeOBJECTID ObjectIDAlias: Ex_Tab ConfigurationKeyword Name TextODefault NL FloatThis option uses the default storageptable/feature classCatalog 口 XOUse configurationk
仓价
This option allowswhichreferencestLocation: Example_DB.gdbSRECYCLE.BINArcGIS_3rdDesktop
+ documentdownload
日 GIS_ExampleExample_DB.mdb NIAbout Configuration Example_DB.gdb Yes
日
FeatureExExample_TableGIS_map
+ NoteExpress Import..
Notes anemptyrowinteFieldNamecolumn，click
+ data type,thenedtheFieldProperties.
+ Report
<上—步（B) Finish 取消

### 第 74 页

![page 74](004-空间数据-知识点回顾/page_074.jpg)

3.2创建一个新的地理数据库
建立拓扑关系
在Catalog目录中选中要素数据集→新建(New)
关系表(Table...) NewTopologyCatalog Thiswizardwill helpyoubuildanew
口 X topology.
A topology allowsyou tomodel theLocation: Feature_Ex integratedbehaviorofdifferentdatatypes.
+ SRECYCLE.BIN
+ ArcGIS3rd Some examplesinclude modeling SS...
+ Desktop adjacent land parcels or soil polygons,
+ document coastline and country boundaries,a
+ download roadsnetwork,roadand busroutes,
and nested geography(censusGIS_Example information).
Example DB.mdbExampleDB.gdbFeature ExExample_TableGIS_map
+ NoteExpress
+ Notes 上步（B） 下一页（N）> 取消
+ PPT
+ ReportProperties...

### 第 75 页

![page 75](004-空间数据-知识点回顾/page_075.jpg)

3.2创建一个新的地理数据库
NewTopology NewTopology NewTopologNewTopologyEntera nan Selectthe Each feature Specify therulesforthetopology:
FeatureEx much thefeathelessthef RuleFeat Feature Class Feature Class AddRule...
Enter the nun AddRuleEnteraclus0.0010000 Features of feature dlass: RuleDescriptionSpecify thera Feature_Class An area must notoverlap anotherareafromthesamelayer.
The cluster Rule: Anyareawherefeaturesoverlapboundaries Feature Clas isanerror.
falling withi MustNotOverlapFeature_ MustNotOverlapMustNotHaveGapsMust NotOverlapWithThe default MustBeCoveredByFeatureClassOfMustCoverEachOther showErrorscannotset Must BeCovered ByContainsPoint OK CancelContains One Point
<上一步（B) 下一页（N）> 取消

### 第 76 页

![page 76](004-空间数据-知识点回顾/page_076.jpg)

3.2创建一个新的地理数据库
NewTopologyCatalog 口xSummary:
Name:Feature_ExTopologyClusterTolerance:0.001 Location: IFeature_Ex_Topology
田 SRECYCLE.BINZClusterTolerance ArcGIS3rdNewTopologyFeature Classes: DesktopFeature_Class,Ranl + documentThenewtopologyhasbeencreated.No + downloadRules: the topology. GIS_ExampleFeature Class-Mu Example_DB.mdbExample_DB.gdbFeature_ExFeature ClassExampleTableGIS_mapNoteExpressNotes
<上一步（B) Finish 取消

### 第 77 页

![page 77](004-空间数据-知识点回顾/page_077.jpg)

3.2创建一个新的地理数据库
拓扑关系的应用一检查数据错误
空间数据采集过程中，人为因素是造成图形数
据错误的主要原因。
不正规多边形
多边形不封闭
结点不重合
过头
不连接
碎屑多边形 伪结点

### 第 78 页

![page 78](004-空间数据-知识点回顾/page_078.jpg)

3.2创建一个新的地理数据库
一般操作流程
》选中新建对象的父文件/数据库；
》点击鼠标右键，选择新建；
>选择需新建的对象；
>进入新建向导对话窗口。

### 第 79 页

![page 79](004-空间数据-知识点回顾/page_079.jpg)

第四节
数据采集

### 第 80 页

![page 80](004-空间数据-知识点回顾/page_080.jpg)

数据采集就是运用各种技术手段，通过各种渠道收
集数据的过程。服务于地理信息系统的数据采集工
作包括两方面内容：空间数据的采集和属性数据的
采集。
空间数据采集方法：野外数据采集、现有地图数字
化、摄影测量方法、遥感图像处理方法等。
属性数据采集方法：相关部门的观测、测量数据、
各类统计数据、专题调查数据、文献资料数据等渠
道获取。
遥感图像解译也是获取属性数据的重要渠道

### 第 81 页

![page 81](004-空间数据-知识点回顾/page_081.jpg)

4.1手动数字化
>根据卫星影像/电子地图，全手动绘制点、
线、面要素。
>一般流程如下：
①在ArcMap中新建一个空白地图文档
(.Mxd) ;
②加载卫星影像数据；
③创建一个新的与卫星影像坐标系相同的要素
类（点、线、面要素）；
④开始编辑要素类...··

### 第 82 页

![page 82](004-空间数据-知识点回顾/page_082.jpg)

4.1手动数字化
在地理数据库中创建
>在文件夹中创建

### 第 83 页

![page 83](004-空间数据-知识点回顾/page_083.jpg)

4.1.1 创建要素
Catalog Folder
一+ File GeodatabaseLocation: GIS_Example Personal Geodatabase
田 ArcGIS_3rdDesktop Database Connection...
+ document ArcGiSServer Connection..
+ download 百 CopyGISExampl Layer...
Exampl le_DB. 启 Paste Group Layer
+ Exampl DB. Delete PythonToolbox
+ GIS_map
+ NoteExpress Rename Shapefile...
+ Notes urnFeatureClass...
+ Id Refresh
+ Report Toolbox
+ source_code New dBASE Table
+ SubjectSystemVolume LAS Dataset
+ ItemDescription...
+ 给排水设计手册 AddressLocator...
Properties... Composite Address Locator...
XMLDocument

### 第 84 页

![page 84](004-空间数据-知识点回顾/page_084.jpg)

4.1.1创建要素
Type here to search @
Name: dom_area Favorites
田 Geographic Coordinate SystemsFeature Type: Polygon 田 ProjectedCoordinate SystemsPointSpatial Reference PolvlinePolygon CatalogDescription: MultiPoint
个 七价
Name:GCS_WGS_1984 Current coordinate system: GCS_WGS_1984
WKID:4326Authority:EPSG Location: GIS_ExampleAngularUnit:Degree(0.01745: PrimeMeridian:Greenwich(0.0) FolderConnectionsSpheroid:WGS_1984 SemmajorAxis:6378137.0 E:\
SemminorAxis:6356752.314 田 $RECYCLE.BINInverseFlattening:298.2572 田 ArcGIS_3rd
田 DesktopdocumentShowDetails Edit... download
日 GIS_ExampleCoordinates wilcontain Mvalues.Used to storeroute data. Example_DB.gdbCoordinates will containZvalues.Used to store 3D data. ExampleDB.mdbdom_area.shpOK Cancel Line.shp
田 GIS_mapNoteExpress
+ Notes

### 第 85 页

![page 85](004-空间数据-知识点回顾/page_085.jpg)

4.1.1创建要素
Untitled-ArcMap 口 ×
FileEdit ViewBookmarksInsertSelection Geoprocessing Customize Windows Help1:3,045,959,547,568 3DAnalystparcelscan.tif Georeferencing
? Editor DrawingTable Of Contents x ResultsLaversE:\GIS_Exampledom_area CopyRemoveE:\ArcGIS_3rd\Chp
日 parcelscan.tif OpenAttributeTableJoins and Relates1
Zoom ToLayer
选中图层
Zoom To MakeVisibleZoomToRasterResolution Zoom To Layer
点击右键
Visible Scale Range Zoom to the extentof theData selected layerEditFeatures ArcToolboxSave AsLayerFile...
Create Layer Package...
Properties... Catalog
-88888.268 1565422.265DecimalDegrees

### 第 86 页

![page 86](004-空间数据-知识点回顾/page_086.jpg)

4.1.1创建要素
Untitled-ArcMap 口 XFile PE View Bookmarks Insert Selection Geoprocessing Customize Windows Help
日 1:92,973,989 3DAnalystparcelscan.tif Georeferencing-
KX Editor- DrawingTable Of Contents
合名 020
D05 4/.65
日 Layers 10044
E:\GIS_ExampleLine 006 6789 021 AttributesCreate Featuresdom_area 100 1101507. 12
日白 E:\ArcGIS_3rd\Chp3\T 022
日 parcelscan.tif 09.340 008
口1 11628 35009 35 35024 0 63 1286 027 028 36.34 Search39.65 108 81011 315 58.15 03443 108.84 012 2.
6; 16 ArcToolbox60385033 03330 013132. .18 38014 Catalog45 72 .57'2 2
四
481847.092 3768458.302Decimal Degrees

### 第 87 页

![page 87](004-空间数据-知识点回顾/page_087.jpg)

4.1.2绘制几何形状（点、线、面）
Untitled-ArcMap 口
File Edit ViewBookmarksInsert Selection Geoprocessing Customize Windows Help1:92,973,989 3DAnalystparcelscan.tif Georeferencing*
KX Editor- Drawing RTable Of Contents XLayers RemoveFAGISExample
日 Line 四 OpenAttributeTabledom_area Joins and Relates
口 ZoomToLayerE:\ArcGIS_3rd\Chp3\T Zoom To MakeVisibleparcelscan.tif
口1 UseSymbol LevelsSelection 35 63
Label Features 028
EditFeatures StartEditingConvert Labels toAnnotation.... Define New Types Of Features...
ConvertFeatures toGraphics..
ConvertSymbology toRepresentation.. Organize Feature Templates..
Data 032
Save AsLayer File...
CreateLayerPackage...
Properties..
481920.318 3768476.001Decimal Degrees

### 第 88 页

![page 88](004-空间数据-知识点回顾/page_088.jpg)

4.1.2绘制几何形状（点、线、面）
编辑工具条 (Editor toolbar)
菜单 草图绘制工具 整形 拆分 属性 创建要素
Editors
编辑工具 编辑拐点 切割多边形 旋转 草图属性
CreateFeatures 口xAttributes x
图 Edit SketchProperties dom_areabuildings ×ZM|FinishSketchCommercial X dom_areaCommercial LineResidential 0 3122512.335 10094299.0711 3122415.981 10094244.383 Linel2 3122455.043 10094166.258
OBJECTIDBldgtype Commercial ConstructionToolsAddress <Null>
City Austin LineState X1 RectangleSHAPE_Length 708.039734 CircleSHAPE_Area 17921.096956
OBJECTID EllipseObjectID 2Freehand

### 第 89 页

![page 89](004-空间数据-知识点回顾/page_089.jpg)

4.1.2绘制几何形状（点、线、面）
>绘制线条 + 鼠标形态
Create Features XCreateFeatures 口x
<Search> QSnap ToFeaturedom_area Direction.. Ctrl+A 点击
Deflection....
dom_area Length... Ctrl+L 鼠标
Line Change LengthAbsoluteX,... F6 左键
Line Delta X,Y.. Ctrl+D ToolsDirection/Length.... Ctrl+GParallel Ctrl+P 15
Perpendicular Ctrl+EConsuctionTools SegmentDeflection.. F7 点击鼠标左键绘图
Replace SketchLine TangentCurve...
FindText Ctrl+WRectangle Streaming F8
Circle Delete Sketch Ctrl+DeleteFinish Sketch F2
Ellipse Square andFinishS Freehand FinishPart
点击鼠标右键，完成草图绘制

### 第 90 页

![page 90](004-空间数据-知识点回顾/page_090.jpg)

4.1.2绘制几何形状（点、线、面）
Untitled-ArcMapFileEdit Bookmarks Insert Selection Geoprocessing Customize WindowsHelp
×5 1:92,973,989 3DAnalystparcelscan.tif GeoreferencingKKA 口·A·| 10 BTable Of ContentsD05 02 Editor 4中
LayersE:\GIS_Example 1034 Start Editing
日Line 006 8.43 02 Stop Editing SearchSave Editsdom_area 100 410 Move... Features
口 0 点击鼠 Split.. <Search> 、
E:\ArcGIS_3rd\Chp3\T 09
parcelscan.tif Construct Points... a ArcToolbox008 Copy Paralle... _area
□1 11628 Merge...
Buffer...
009 Union.... oCatalogClip.... struction Tools 36.34108 Validate Features9.65 011 Snapping ine1 ectangle 15108.8 MoreEditingTools ircleEditingWindows llipse35 031 Options.. reehand30 35024 32.
0 福
72 45 G7 72.59
一日口 一
481933.371 3768456.533Decimal Degrees

### 第 91 页

![page 91](004-空间数据-知识点回顾/page_091.jpg)

4.1.2绘制几何形状（点、线、面）
>绘制线条一保存
Editor 保存对文件的编辑，并
StartEditing
继续编辑。
Stop Editing
停止编辑并保存任何未
Save Edits
保存的编辑。
常备份，勤保存！
Doyouwanttosaveyouredits?
是（Y） 否（N) 取消

### 第 92 页

![page 92](004-空间数据-知识点回顾/page_092.jpg)

>绘制线条一保存
Untitled-ArcMap 口
FileEdit ViewBookmarksInsertSelection Geoprocessing CustomizeWindows Help1:92,973,989 3DAnalyst-parcelscan.tifA·宋体
TableOf Contents xEditor
日 Layers Editor-
E:\GIS_Exampledom_area Create Features 口
电 <Search>
E:\ArcGIS_3rd\Chp3\Tparcelscan.tif There are no templates to show. ArcToolbox
口1
CatalogSelecta template,
481946.8653768451.887Decimal Degrees

### 第 93 页

![page 93](004-空间数据-知识点回顾/page_093.jpg)

4.1.2绘制几何形状（点、线、面）
>绘制面要素
操作流程基本一致，仅创建要素窗口有差异。
CreateFeatures 口x CreateFeatures
<Search>
dom_area Clickhere to seetemplatesnotlisterXdom_area LineLine Line
-Line
肉 肉
Construction Tools ConstructionToolsPolygon LineRectangle RectangleCircle CircleEllipse Ellipse2 Freehand 2FreehandC AutoCompleteFreehand

### 第 94 页

![page 94](004-空间数据-知识点回顾/page_094.jpg)

4.2自动数字化
》只能是二值化（黑白色）电子地图或图片
不不
不
056057058 风频
059 不
060 甲
061 不 ④
062 001
C90 002 002064 020 017065 003 021 003 018990 004 022 00 019067 005 023 005 020068 006 024 006 021069 007 025 007 022070 008 026 008,
071 009 010 009 028072 011 028073 029074075076 033078 091092

### 第 95 页

![page 95](004-空间数据-知识点回顾/page_095.jpg)

4.2自动数字化
需用到ArcScan工具： ExtensionsSelect the extensionsyouwant to use.
3DAnalystCustomize Windows Help ArcScanGeostatistical Analystolbars NetworkAnalystPublisherExtensions... SchematicsSpatial AnalystAdd-InManager... Tracking AnalystCustomize Mode...
Style Manager....
ArcMapOptions...
Description:
选择自定义菜单
ArcScan 10.6.0
Copyright1999-2017Esri Inc.AllRightsReserved
（Customize)→扩展 Providessupportforthecreationofvectorfeaturesfromarasterimage.
(Extentions)-→ArcScanClose
>Close

### 第 96 页

![page 96](004-空间数据-知识点回顾/page_096.jpg)

4.2自动数字化
需用到ArcScan工具：
3D Analyst
菜单（或工具条）点击
Advanced Editing
鼠标右键→快捷菜单中 Animation
选择ArcScan ArcScanWind ows Help Data DrivenPages3DAn DataFrameToolsEditorArcScanparcelscan.tif Vectorization Raster Cleanup Cell Selection

### 第 97 页

![page 97](004-空间数据-知识点回顾/page_097.jpg)

4.2自动数字化
4.2.1半自动数字化
①选中内容列表中的Line
图层→②启动编辑，打开
00 810 001
编辑工具条→③创建要素 062 020 0023C3 621 00 118
CO 022
窗口 中选择 0C5 023 005 C2C006 C24 900 C21
LOC 025 007 C22
Line→④ArcScan工具条中
选择矢量化追F按钮

### 第 98 页

![page 98](004-空间数据-知识点回顾/page_098.jpg)

4.2自动数字化
Untitled-ArcMap 口
FileEditViewBookmarks Insert Selection Geoprocessing Customize Windows Help1:200,000,000 Drawing- 宋体 SWATProje jectSetupGeoreferencing" parcelscan.tifTable Of Contents ResultsAroToolboxArcScan
日 Layers parcelscan.tif Vectorization arterCleanup CellSelectionLine Create Features
日 m_area ditorEditor- dom_area
日 par elscan.tif dom_area
國 Copy LineRemove Line
口 penAttributeTableinsandRelatesZoomToLayerZo m ToMake VisibleVisi eScaleRange 1.3: Construction Tools5 001 AttributesUse mbol Levels LineSelecton 020 2C0 017 RectangleLabel Features DC3 003 1118 Circle621 EllipseEditFeatures 004 00 2FreehandConvert Labels to Annotation... 0C5 020 005 C2CConvertFeaturestoGraphic. 006 024 000 C21
Convert Symbology to Representation... LOC EC C22
Data 025
SaveAsLayer File... 600 026
Create Layer Package.... 013 02 028
Properties..
481672.351 3768513.07DecimalDegrees

### 第 99 页

![page 99](004-空间数据-知识点回顾/page_099.jpg)

4.2自动数字化
4.2.1半自动数字化
在线的断点处点击鼠标
左键;
点击鼠标左键
②在线上其他任意位置再
00 5 001 次点击鼠标左键；
062 020 0173C3 621 0O 118004 022 ③识别后点击鼠标右键；
3C5 023 005 C2C006 006 C21
LOC 025 007 C22 ④弹出快捷菜单中选择完
成草图(Finish Sketch)。

### 第 100 页

![page 100](004-空间数据-知识点回顾/page_100.jpg)

4.2自动数字化
Untitled-ArcMap 口
Bookmarks Insert Selection Geoprocessing Customize Windows1:200,000,000 Drawing· SWATProject SetupGeoreferencing parcelscan.tif 同日
Table Of Contents Results
国 ArcScanLayers parcelscan.tif Vectorization Raster Cleanup CellSelectionLine Create FeaturesArcToolboxdom_area Editor <s>
口 055 Editor- 国 dom_area
日 parcelscan.tif dom_area0 Line
口1 2.7 Line058051 Construction Tools062 OC 54 810 6.0 C01 Line Attributes063 二 RectangleC54 002 020 2C0 017 OCircle116h S0C 021 003 018 EllipseC04 2Freehand066 C22 00 C1S Catalog067 005 005 C20000 023
C24 000 021
BCO 025 007070 026 00871 009481673.264 3768646.85Decimal Degrees

### 第 101 页

![page 101](004-空间数据-知识点回顾/page_101.jpg)

4.2自动数字化
Untitled-ArcMap 口 ×
FileEditView Bookmarks InsertSelection Geoprocessing Customize WindowsHelp1:200,000,000 Drawing- SWATProjectSetup
+ Georeferencing- parcelscan.tifTable Of Contents XArcScan
日Layers parcelscan.tif Vectorization Raster Cleanup Cell SelectionLine Create Features 口
ArcToolboxdom_area Editor <Search> QEditor- dom_areaparcelscan.tif OSR dom_area10 Line11 257 Line058600
昌
051 Construction Tools062 OC 04 810 6.0 C01 Line Attributes063 口 RectangleC54 502 002 017 Circle80C L2 020 Ellipse11h 003 018 2rFreehand066 C34 G22 00 C1S Catalog067 005 023 S00 C20
ROO 003 C21 000 021025 022.
070 026 80G 02371 009481665.65 3768683.493Decimal Degrees

### 第 102 页

![page 102](004-空间数据-知识点回顾/page_102.jpg)

4.2自动数字化
Untitled-ArcMap 口
FileEditView Bookmarks InsertSelection Geoprocessing Customize Windows Help1:60,000,000 Drawing-k 口 宋体 SWATProjectSetup
+ KX Georeferencing-prcelscan.tifTable Of Contents XArcScanLayers parcelscan.tif Vectorization 厅 Raster Cleanup CellSelectionLine 5 Create Features
日 dom_area Editor ·<Search> ®
60.04 Editor- 中 国 dom_areaparcelscan.tif B 30.41 dom_area70 Line Edit SketohProperties
.62 LineB 002 017100 C10）
003 018 Construction Tools3 Polygon Attributes
口 RectangleCirle004 019 Ellipse3
寸 2rFreehand3 Auto Complete Polygon Catalog005 6 020 Search3 47. 6.
3 100.44481730.384 3768586.808Decimal Degrees

### 第 103 页

![page 103](004-空间数据-知识点回顾/page_103.jpg)

4.2自动数字化
Untitled-ArcMap 口 XFileEditViewBookmarksInsertSelection Geoprocessing CustomizeWindowsHelp1:60,000,000 Drawing- 口·A SWATProjectSetupIK Georeferencing" parcelsoan.tifTable Of ContentsArcScan X
日Layers parcelscan.tif Vectorization Raster Cleanup Cell SelectionLine 5 Create Features
日 dom_area Editor X <Search> ®
60.04 Editor" 中 dom_areaparcelscan.tif domarea10 70 Line Edit
口1 7.62 Line98.10
B 002 017 Sketoh100 C100 Pr018 好 Construction ToolsX 3Polygon4 Attributes
口 RectangleOCircle004 019 Ellipse2rFreehand LarAuto Complete Polygon005 .66 02047.
3 100.44
Numberof featuresselected:1 481752.656 3768551.259DecimalDegrees

### 第 104 页

![page 104](004-空间数据-知识点回顾/page_104.jpg)

4.2自动数字化
4.2.2全自动数字化
①清除不必要的内容；②自动数字化

### 第 105 页

![page 105](004-空间数据-知识点回顾/page_105.jpg)

4.2自动数字化
4.2.2全自动数字化—图像清理
》使用栅格绘图工具
ArcScanparcelscan.tif Vectorization Raster Cleanup Cell Selection|
Start Cleanup
①ArcScan工具条中点击栅格
Stop Cleanup
清理按钮; RasterPainting ToolbarEraseSelected Cells
②弹出菜单中点击开始清理： Fill Selected CellsErosion...
③点击绘图工具条
Dilation...
Opening....
Raster Painting Closing...
Save As...
橡皮擦工具 魔术橡皮擦工具

### 第 106 页

![page 106](004-空间数据-知识点回顾/page_106.jpg)

4.2自动数字化
4.2.2全自动数字化—图像清理
》使用像元选择工具
ArcScanparcelscan.tif Vectorization Raster Cleanup Cell Selection
①ArcScan工具条中点击 SelectConnected Cells...
像元选择工具； ClearSelected CellsSaveSelection As...
②点击选择相连像元。

### 第 107 页

![page 107](004-空间数据-知识点回顾/page_107.jpg)

4.2自动数字化
4.2.2全自动数字化—图像清理
690 435 025 p72 'innit 24.0 403.
070 008 0081:3.8O 023026 思 116.28071 600 025 20 3510525 009 024 62027 026 027 P2.U 028010 123.35 396 ivi:
072 C.u10.1.35 5375 028 EH. 12011 11885 029 012 03443 073 355104.46 03 10.530 70.
012 7e.55 013 033074 030114.50 3 0311 G 3075 07 015 032
"27.49 3 3 72.89 43302820: 016 a 1. 029 030076 5. 017 03315 3.65077 7.5 392311572078 2 585 426 37 42 4 2 091 4.5159 2 10.3 083 084 085 086 087 088 089 060 27.35079 7.222 123 10035

### 第 108 页

![page 108](004-空间数据-知识点回顾/page_108.jpg)

4.2自动数字化
4.2.2全自动数字化—图像清理
》使用像元选择工具
ArcScanparcelscan.tif Vectorization Raster Cleanup Cell Selection
如选择效果不佳，点
Select Connected Cells...
击清除选择； InteractiveSelectionTargetClearSelected Cells
如效果不错，点击选
Save SelectionAs...
项另存。

### 第 109 页

![page 109](004-空间数据-知识点回顾/page_109.jpg)

4.2自动数字化
4.2.2全自动数字化一图像清理
》使用像元选择工具
①设置存 ExportRasterDataset
储路 ArcMap
学位论文评审
② 设 教府文件
Doyouwanttoadd theexporteddatato themapasa layer? parcelscan.tif
件名; RasSelO.tif
③设
是（Y） 否(N）
件格式，
Name: RasSelo Save
④保存
Saveastype: TIFF Cancel

### 第 110 页

![page 110](004-空间数据-知识点回顾/page_110.jpg)

4.2自动数字化
4.2.2全自动数字化—图像清理
Untitled-ArcMFile Edit View 完成图像清理，开
nal 0561114
始全自动数字化 057
O Contents 058690
日 Layers 060
RasSelO.tiValue 061
High: 062 001 019 001063
Low:0 064 002 020 002 017065 003 021 003 018
parcelsca 066 004 022 004 019
田Line 067 S00 023 005 020
dom_area 068 006 006 021 (0.41024
口 069 007 025 200
parcelsca 070 008 026 008071 009 027 009
□1 072 010 028073 011074 012 10013 014075076 033077078 0913 80 092

### 第 111 页

![page 111](004-空间数据-知识点回顾/page_111.jpg)

4.2自动数字化
4.2.2全自动数字化—图像清理
ArcScanRasSelO.tif Vectorization Raster Cleanup Cell Selection
①ArcScan工具条中选择矢量化：
②弹出菜单中，选择显示预览；
③点击生成要素，弹出窗口设置
好参数，点击OK;
④点击编辑器，保存并停止编辑
EditorEditor 中
Start EditingStop EditingSave Edits

### 第 112 页

![page 112](004-空间数据-知识点回顾/page_112.jpg)

4.3逻辑一致性
邻接 相交 相离 包含 重合
>逻辑一致性是指GIS数据（点/线 点一点
点一线
面要素）对现实世界中的地理 点一面
线一线
事物之间的空间关系的模仿程度 线一
面
》基本编辑涉及逻辑一致性的两个方面。
·确保两条相交的线段在公共顶点相交。
·确保相邻多边形共享相同的边界。

### 第 113 页

![page 113](004-空间数据-知识点回顾/page_113.jpg)

4.3逻辑一致性
悬挂
拓扑正确一水平线与垂直
线相交，形成三条直线，
悬挂一两条线连接失 线与线之间有公共节点。
败，线与线间有空隙。
节点nodeGIS数据结构完整性的角度出发。
现实世界中是否存在（悬挂）?
自动连接功能，确保逻辑一致性 捕捉工具
(Snaping Tool)

### 第 114 页

![page 114](004-空间数据-知识点回顾/page_114.jpg)

4.3逻辑一致性
捕捉容差 （(Snapping tolerance)
捕捉容差是两个顶点之间的最小距离。像素、长度单位
如果光标在一个顶点的容差范围内，那么下一次鼠标点
击将被锁定到该顶点。
SnaptoleranceScreen pixelMap unit

### 第 115 页

![page 115](004-空间数据-知识点回顾/page_115.jpg)

Customize WindowsHelpToolbars 3DAnalyst
捕捉类型 Extensions... Advanced EditingAdd-ln Manager.. AnimationCustomize Mode... ArcScanStyle Manager... COGOArcMap Options.. Data Driven PagesData Frame ToolsWindows Help Distributed Geodatabase3D Analyst- Edit VerticesEditorEditor 中 EffectsStart Editing Feature CacheStopEditing Feature ConstructionGeocodingSave Edits Geodatabase HistoryMove... GeometricNetworkEditingGeoreferencingSplit... Geostatistical Analystonstruct Points. GPS GraphicsCopy Parallel Image ClassificationMerge.. LabelingBuffer... LAS DatasetUnion.... Network Analyst Layoutclip... Parcel EditorValidate Features PublisherRaster PaintingSnapping Snapping Toolbar RepresentationMore Editing Tools Options.. Route EditingEditing Windows Workwith the snapping Schematicenvironment and set snappir Schematic EditorOptions... options for snapping. Schematic Network AnalystSnappingSpatial AdjustmentSpatialAnalystStandardCustomize订制→Toolbar工具条 TabletTIN EditingToolsTopologyEditor toolbar编辑工具条→Snapping捕捉 Tracking AnalystTransform ParcelsUtility Network AnalystVersioningCustomize...

### 第 116 页

![page 116](004-空间数据-知识点回顾/page_116.jpg)

捕捉类型
捕捉点
捕捉容差
捕捉终点 田
捕捉边
SnappingSnapping 田
Use SnappingIntersection Snapping
捕捉顶点 TangentSnappingSnapTo SketchSnap To Topology NodesOptions...

### 第 117 页

![page 117](004-空间数据-知识点回顾/page_117.jpg)

捕捉设置
EditorStart EditingStop EditingSnappingSaveEdits Snapping- 田
口
Snapping Snapping ToolbarMore Editing Options... Use SnappingEditingWindows IntersectionSnappingepping Options MidpointSnappingOptions... GeneralTangent SnappingTolerance: 10 PixelsSnap ToSketchSnap Symbol:
Snap To Topology Nodesbuildings:VertexOptions..
Layer NameSketch:EdgeSnapTypeTextSymbol...
OK Cancel

### 第 118 页

![page 118](004-空间数据-知识点回顾/page_118.jpg)

相邻多边形
》保持相邻多边形的逻辑一致性是很重要的。
重叠
缝隙
两个多边形之间的拓 两个多边形的重合边
扑错误 界，无拓扑错误
>相邻林地发生的两次病虫害。

### 第 119 页

![page 119](004-空间数据-知识点回顾/page_119.jpg)

4.3创建相邻多边形
常用两种方法
－使用特殊工具来创建相邻的多边形。
一先创建一个大的多边形，再切割成两个相邻多边形。
追踪工具（Trace）
自动补全多边形工具
(Auto complete polygon)

### 第 120 页

![page 120](004-空间数据-知识点回顾/page_120.jpg)

4.3创建相邻多边形
1.选择要素模板
buildings CreateFeatures X2.选择创建工具一polygon CommercialResidential
(Construction tool)
boundaryboundary3.输入第一个多边形 Polygon buildingsRectangle Commercial4.将创建工具换为“自动 ResidentialStreets
完成多边形”Auto -StreetsComplete Polygon AutoCompletePolygon ConstructionTools5.创建邻接多边形，起始 PolygonRectangle
点和结束点必须位于第 中 CircleEllipse
一个多边形内部 Trace FreehandCreate segments by tracing AutoCompletepress O to access tracing existing features.Right-click or Polygon6.新多边形将使用旧多边 options,including setting anoffset.
形的现有边界。
或使用追踪工具（Trace）

### 第 121 页

![page 121](004-空间数据-知识点回顾/page_121.jpg)

第五节
数据编辑

### 第 122 页

![page 122](004-空间数据-知识点回顾/page_122.jpg)

编辑技巧
>编辑前一定要备份（backupcopy
》打开新的地图文档进行编辑，只添加你需要
的图层；
》减少打开文件的数量；
》尽量保持层在相同的坐标系统，以避免出现
意外的错误;
常保存（Savefrequently）
常备份，勤保存

### 第 123 页

![page 123](004-空间数据-知识点回顾/page_123.jpg)

编辑技巧
编辑矢量文件通常会破坏地图
文档（.mxd）布局
》建议在专门打开的地图文档
（Map document）中进行编辑，
其中包含所需的最小数量的文
件。
Erupfions Hg hway Lagend
》尽量不要在你花了几天时间开 Countles ooprso.mlle72-35
发绘制的华丽地图文件（Mapdocument）中边界数量数据。

### 第 124 页

![page 124](004-空间数据-知识点回顾/page_124.jpg)

图形编辑
Graphic edit

### 第 125 页

![page 125](004-空间数据-知识点回顾/page_125.jpg)

快捷工具
>编辑工具（EditTool）用于选择要
素，以便可以移动、删除或编辑它
编辑工具 们。
>选择要素工具（SelectFeatures）
·鼠标单击要素进行选择
选择要素
·添加另一个要素
·鼠标框选多个要素
·点击空白区域来清除选择（或使用
清除选择
清除选择—ClearSelection—工具）

### 第 126 页

![page 126](004-空间数据-知识点回顾/page_126.jpg)

选择要素
移动工具 选择要素
鼠标框选（按住
鼠标左键拖拽）
Shift+鼠标单击
（或鼠标框选）

### 第 127 页

![page 127](004-空间数据-知识点回顾/page_127.jpg)

分割多边形
1.使用编辑工具选择要素。 2.点击裁剪多边形工具。
EditorEditor3.使用切割多边形工具绘制 4.双击鼠标完成线条并分割多
切割线。 边形。
起始点和结束点必须位于多边形外部

### 第 128 页

![page 128](004-空间数据-知识点回顾/page_128.jpg)

移动要素
1.使用编辑工具（Edittool）选中目标要素（单
个或多个）
2.悬停鼠标，拖动要素到目标位置。

### 第 129 页

![page 129](004-空间数据-知识点回顾/page_129.jpg)

删除要素
1.使用编辑工具（Edittool）选中目标要素（单个
或多个）
2.按键盘上的Del键输出选中对象，也可在属性表
中进行删除

### 第 130 页

![page 130](004-空间数据-知识点回顾/page_130.jpg)

编辑顶点
1.使用编辑工具 (Edit tool) 2.选择编辑顶点（EditVertices)，
选中目标要素 草图出现了。
Editor
中
Route Measure Editing Route Measure EditingInsertVertex Insert VertexDelete Vertex DeleteVertexMove... Move...
3.单击并拖动可移动顶点。 MoveTo.... MoveTo...
Change Segment Change SegmentFlip Flip4.单击鼠标右键，打开草图菜 Trim To Length.... Trim To Length..
Part Part
单以添加或删除顶点。 DeleteSketchCtrl+Delete Delete SketchCtrl+DeleteFinish Sketch F2 口 Finish Sketch F2
FinishPart FinishPartSketch Properties Sketch Properties5.双击或在草图菜单中选择
“Finish Sketch”完成编辑

### 第 131 页

![page 131](004-空间数据-知识点回顾/page_131.jpg)

旋转要素
1.使用编辑工具（Edittool） 2.选择旋转工具（Rotatetool）
选中目标要素
EditorEditor 中
(optional)拖动x移动旋转中心
点位置
3.在旋转点周围单击并拖动

### 第 132 页

![page 132](004-空间数据-知识点回顾/page_132.jpg)

分割线要素
1.使用编辑工具选择要素。2．点击分割工具（SplitTool)
EditorEditor3.在分割处点击鼠标。

### 第 133 页

![page 133](004-空间数据-知识点回顾/page_133.jpg)

要素reshape (整形）
1.使用编辑工具选择要素。 2.点击整形工具（Reshape）
EditorEditor- 中
4.输入最后一个顶点并双击完
3.使用鼠标描绘需要整形 成草图（或finishsketch）
的形状。

### 第 134 页

![page 134](004-空间数据-知识点回顾/page_134.jpg)

编辑状态下的快捷菜单
SnapToFeatureDirection.. Ctrl+ADeflection...
草图上点击 Length... Ctrl+LChangeLength
右键
Route Measure Editing Absolute X,... F6
InsertVertex DeltaX,Y... Ctrl+DDeleteVertex Direction/Length... Ctrl+GMove.. ParallelMove To... Perpendicular Ctrl+EChange Segment SegmentDeflection... F7
Flip Replace SketchTrim to Length.. TangentCurve...
Part FindText Ctrl+WDeleteSketch Ctrl+Delete Streaming F8
草图上点
Finish Sketch F2 Delete Sketch Ctrl+DeleteFinishPart 击右键 Finish Sketch F2
SketchProperties Square and FinishFinish PartVertex menuSketch menu
顶点菜单
草图菜单

### 第 135 页

![page 135](004-空间数据-知识点回顾/page_135.jpg)

Multipartfeatures（多要素）
》是由多个简单的要素组
成的，这些要素是不相
交的。
点击右键选择 FinishPart继续绘制下一个多
边形。
Delete SketchFinishSketch 》使用FinishSketch完成图
FinishPart
形绘制，或在最后一个
顶点双击。

### 第 136 页

![page 136](004-空间数据-知识点回顾/page_136.jpg)

编辑草图属性
EditorEditor #中XQI
用于查看或编辑顶点
RouteMeasure EditingInsertVertex 坐标，或删除顶点。
DeleteVertexEditSketch Properties 口xMove...
Move To... ZM|FinishSketchChange Segment #
0 9766988.843 5412849.986
Trim toLength...
9767027.251 5412872.8622 9767050.000 5412903.974
DeleteSketch Ctrl+Delete3 9767043.143 5412983.586
FinishSketch F24 9767049.103 5413036.6609767088.173 5413080.5846 9767144.460 5413090.650
Vertex menu 9767211.342 5413088.820
R 9767265643 5413051302

### 第 137 页

![page 137](004-空间数据-知识点回顾/page_137.jpg)

Sketching tools（草图工具）
EditorEditor
》控制连接顶点的边的
默认为直线工
具（Straight 类型
segment tool)
》供不同的方法来添加
下一个顶点
·直线
浮动迷你
·直角
工具栏
人|口 ·圆弧

### 第 138 页

![page 138](004-空间数据-知识点回顾/page_138.jpg)

Right Angle sketch tool （直角）
3.鼠标点击输入角点
1.选择要素模板 4.输入最后一个角点并双击
buildings 完成草图（或finishsketch）
CommercialResidential2.选择直角工具（RightAngle ) Feature ConstructionEditorEditorSnapToFeatureAbsolute X,Y... F6
DeltaX,... Ctrl+DFeature Construction X Direction/Length...Ctrl+GDeleteSketch Ctrl+DeleteFinish Sketch F2
RightAngleSquare andFinishFinishPart

### 第 139 页

![page 139](004-空间数据-知识点回顾/page_139.jpg)

Arc Segment sketch tool (圆弧)
1.选择要素模板 3.沿道路输入节点（鼠标
点击)
StreetsStreets2.选择弧段工具（ArcSegment )
4.输入最后一个顶点并双击
完成草图（或finishsketch）
Feature Construction
-么人
FinishSketch F2

### 第 140 页

![page 140](004-空间数据-知识点回顾/page_140.jpg)

属性编辑/修改
What is an attribute table?

### 第 141 页

![page 141](004-空间数据-知识点回顾/page_141.jpg)

属性窗口
EditorEditorUsefulwindow：用于编辑所选要素的属性
右键单击快捷菜单项
Attributes
显示当前选 (contextmenu)
日 buildings
择的要素 口 CommercialCommercialResidential 京 FlashResidential ZoomToPanTo
四口 CopyAttributesOBJECTID 3
Bldgtype Commercial 启 PasteAttributesAddress <IInN> M OnlySelectThisCity Austin UnselectStat TX DeleteSHAPE_Length 441.572368
编辑字段属性 SHAPE_Area 8826.985592 OpenAttributeTableOBJECTID Layer Properties...
ObjectIDNullvaluesnotallowed contextmenu

### 第 142 页

![page 142](004-空间数据-知识点回顾/page_142.jpg)

属性窗口
编辑属性
编辑单个要素 编辑多个要素
Attributes x AttributesbuildingsCommercial Commercial
口 Commercial 1.单击要素 Commercial 1.单击图
口
Residential Residential 层名称
Residential Residential
口 肉口
OBJECTID 3 OBJECTIDBldgtype Commercial BldgtypeAddress <Null> AddressCity Austin City AustinState TX State TXSHAPE_Length 441.572368 SHAPE_LengthSHAPE_Area 8826.985592 SHAPE_AreaOBJECTID OBJECTIDObjectID 2.编辑字段 ObjectID 2.编辑字段
Null valuesnot allowed Null valuesnot allowed

### 第 143 页

![page 143](004-空间数据-知识点回顾/page_143.jpg)

属性表
TableOfCont.xLayers
日日 CN-shaA 國 CopyRemoveOpen Attribute TableJoins and RelatesZoomTo Layer Open Attribute TableZoom To Make Visible Open this layer's attributeVisible Scale Range double-click layer name OR table.Shortcut:CTRL+
UseSymbol Levels CTRL+T.
SelectionLabelFeaturesEdit FeaturesConvert Labels to AnnotationConvert Features to Graphics...
Convert Symbology to Representation...
Save As Layer File....
Create Layer PackageProperties...
选中图层→鼠标右键
→Open Attribute Table

### 第 144 页

![page 144](004-空间数据-知识点回顾/page_144.jpg)

ArcGIS 中的字段
water_stationFID Shape ID 省份名 流城 控制单 水体 控制断 2014年水 2020年水 监测断 监测1 控制藏
OPoint W1478 新疆维晋尔自治区 西北诸河 阿克苏河阿克苏地区龙口拉制单元 阿克苏河 龙口 II 阿克苏 乌什县 阿克苏地区：温宿县
1Point W1479 新疆维晋尔自治区 西北堵河 阿克苏河阿克苏地区塔里木栏河闸拉制单元 阿克苏河 艾比湖 塔里木拉河闸 II 阿克苏 阿瓦提县 阿克苏地区：阿克苏市，阿
2Point 3Point W1480 新疆维善尔自治区 西北诸河 艾比湖博尔塔拉蒙古自治州控制单元 艾比湖1 V- V 博尔塔 精同县 博尔塔拉豪古自治州：阿拉
W1481 新疆维普尔白治区 四北诸河 白杨河塔城地区控制单元 白杨河 白杨河水库出口 克拉玛 乌尔禾区 克拉玛依市：白城滩区，克
4Point W1482 新疆维普尔自治区 西北堵河 白杨河吐鲁餐地区拉制单元 白杨河 河东乡大桥 吐餐谷 托克县 社鲁路地区：都兽县，吐餐 阿勒泰地区：布尔津县
5Point W1483 新疆维普尔自治区 西北堵河 布尔津河阿勒泰地区拉制单元 布尔津河 布尔津河大桥 阿勒泰 布尔津县
6Point W1484 新疆维吾尔白治区 西北诸河 车尔臣河巴音郭楞豪古自治州拉制单元 车尔臣河 塔提让 II II 巴音邦 且末县 巴音郭楞豪古自治州：且末
7Point W1485 新疆维普尔自治区 西北堵河 额尔齐斯河阿勒寨地区北屯大桥拉制单元 额尔齐斯河 北屯大桥 阿动票 阿勒市 阿勒泰地区：阿勒泰市，富
8Point W1486 新疆维吾尔自治区 西北堵河 额尔齐斯河阿勒泰地区布尔津水文站控制单元 额尔齐斯河 布尔津水文站 II II 阿勒票 布尔津县 阿勒寨地区：阿勒泰市，布
9Point W1487 新疆维吾尔自治区 四北诸河 额尔齐斯河阿勒泰地区额河南湾控制单元 额尔齐斯河 额河南湾 II II 阿动寨 哈巴河县 阿勒寨地区：哈巴河县，吉
10Point W1488 新疆维晋尔自治区 西北堵河 额尔齐斯河阿勒泰地区高道大桥控制单元 额尔齐斯河 蕴大桥 11 II 阿动票 高道县 阿勒泰地区：高道县
11Point W1489 新疆维普尔自治区 西北堵河 顿敏河塔城地区控制单元 额敏河 巴士拜大桥 II1 塔城 裕民县 塔城地区：额敏县，塔城市
12Point W1490 新疆维普尔自治区 西北诸河 巩乃斯河伊翠州控制单元 巩乃斯河 羊场大桥 II II 伊型 尼勒克县 巴音郭榜蒙古自治州：和静
13Point W1491 新疆维晋尔自治区 西北堵河 喀拉喀什河和田地区拉制单元 喀拉喀什河 喀河大桥 和田 和田市 和田地区：和田县，星玉县
14Point W1492 新疆维善尔自治区 西北诸河 喀什河伊州控制单元 喀什河 喀什河大桥 II 伊型 伊宁县 伊率哈萨克自治州：尼勒克
16Point 15Point W1493 新疆维普尔自治区 西北诸河 开都河巴音榜聚古自治州拉制单元 开都河 哈尔英教 I1 巴音邦 和静县 巴音郭榜票古自治州：和静 昌吉回族自治州：卓崇市，
17Point W1494 新疆维晋尔自治区 西北堵河 开屋河昌吉州控制单元 开星河 老奇台 I1 II 昌吉 新台县
W1495 新疆维普尔自治区 西北诸河 克孜河克孜勒苏柯尔克孜自治州控制单元 克孜河 三级电站 I1 I1 喀什 疏附县 喀什地区：疏附县：克孜勒
18Point W1496 新疆维哥尔自治区 西北堵河 孔雀河巴音都楞聚古自治州汇合口拉制单元 孔雀河 汇合口 I1 II 巴营邦 时县 巴音郭楞戴古自治州：摩尔
19Point W1497 新疆维荟尔自治区 西北诺河 孔雀河巴音楞乘古自治州兰干控制单元 孔省河 兰干 巴音扣 库尔勒市 巴音楞蒙古自治州：库尔
20Point W1498 新疆维著尔白治区 西北诸河 奎屯河塔城地区控制单元 雀屯河 老龙口 I1 II 审型 雀屯市 塔城地区：乌苏市
21Point W1499 新疆维普尔自治区 西北堵河 查屯河伊翠州拉制单元 座屯河 黄沟二库 胡杨河 克拉玛依市：独山子区：伊犁
22Point W1500 新疆维吾尔自治区 西北墙河 赛里木湖博尔塔拉豪古自治州控制单元 赛里木湖 湖2 III 博尔塔 博乐市 博尔塔拉蒙古自治州：博乐
23Point W1501 新疆维吾尔自治区 西北清河 三屯河昌吉州拉制单元 三屯河 三屯河首 II 昌吉市 品古回族自治州： 昌吉市，
24Point W1502 新疆维晋尔自治区 西北诸河 水磨河乌鲁木齐市拉制单元 水河 七纺桥 IV IV 乌餐木 水磨沟区 乌餐木齐市： 米东区，沙依
25Point 26Point T1503 新疆维普尔自治区 西北诸河 塔里木河阿克苏地区控制单元 塔里木河 轮台 贰化物不参与 阿克苏 轮台县 阿克苏地区：拜城县，库车
W1504 新疆维吾尔白治区 西北诸河 塔里木河巴音郭楞豪古自治州拉制单元 塔里木河 尉 赢化物不参与 巴音 时华县 伊翠哈萨克自治州：特克斯 巴音楞豪古自治州：轮台
27Point W1505 新疆维普尔自治区 西北诸河 特克斯河伊翠州科布大桥控制单元 特克斯河 科布大桥 II 特克斯县
28Point W1506 新疆维普尔自治区 西北堵河 特克斯河伊型州龙口大桥控制单元 特克斯河 龙口大桥 I1 II 伊率 巩留县 伊翠哈萨克自治州：巩留县
29Point W1507 新疆维吾尔自治区 西北诸河 提孜郑南河喀什地区控制单元 提孜那甫河 萨依巴格 II 客什 叶城县 喀什地区：叶城县，泽普县
30Point W1508 新疆维晋尔自治区 西北堵河 托什干河阿克苏地区控制单元 托什干河 阿热力 II 阿克苏 温宿县 阿克苏地区：温宿县，乌什
31Point W1509 新疆维晋尔自治区 西北诸河 乌鲁木齐河乌鲁木齐市青年渠拉制单元 乌鲁木齐河 青年 II 乌鲁木 天山区 乌鲁木齐市：达板城区，乌鲁
32Point W1510 新疆维吾尔自治区 西北诸河 乌鲁木齐河乌鲁木齐市英维桥拉制单元 乌鲁木齐河 英雄桥 II II 乌鲁木 乌鲁木齐 乌鲁木齐市：新市区
33Point W1511 新疆维善尔自治区 西北堵河 乌鲁木齐河乌鲁木齐市跃进桥控制单元 乌鲁木齐河 跃进桥 11 I1 乌鲁木 乌鲁木齐 乌鲁木齐市： 乌鲁木齐县
35Point 34Point W1512 新疆维吾尔自治区 西北堵河 乌伦古湖阿勒泰地区控制单元 乌伦古河阿勒泰地区控制单元 乌伦古河 项山 II1 阿勒 福海县 阿勒泰地区： 高道县， 青河
36Point W1513 新疆维普尔自治区 西北诸河 乌伦古湖 南邮渔政点 V- COD. 氧化物 阿动泰 福海县 阿勒泰地区：福海县， 吉木
37Point W1514 新疆维晋尔自治区 西北堵河 乌伦古潮码头 V- COD. 氧化物 阿动 福海县
38Point W1515 新疆维善尔自治区 西北诸河 西北诸河 叶尔莞河喀什地区阿瓦提镇拉制单元 乌伦古湖湖中心 V- COD. 氧化物 阿勒泰 福海县 莎车县 喀什地区：巴楚县，麦盖捷
39Point W1516 新疆维普尔自治区 叶尔莞河 阿瓦提镇 II II 喀什
40|Point W1517 新疆维萧尔自治区 西北诸河 叶尔莞河喀什地区卡群控制单元 叶尔莞河 卡群 客什 莎车县 喀什地区： 莎车县， 塔什库
w1518 西北请河叶尔羊河域什协区依干基济口格制单元 叶尔羊河 依干基济口 TTT ITTT 苏车 什协区： 药车县、
1 (0outof55Selected)
water station] water_shtation_e

### 第 145 页

![page 145](004-空间数据-知识点回顾/page_145.jpg)

ArcGIS中字段类型 (type)
Field Type Explanation ExainplesShort Integersstored as2-bytebinarynumbers 255
Rangeofvalues-32,000 to+32,000 12001
Long Integersstored as10-bytebinarynumbers 156000
Rangeofvalues-2.14billionto+2.14billion 457890
Floating-point values witheight significant digits in 1.289385e12
Floatthemantissa 1.5647894e-02
Double Double-precision floating-point valueswith 161.12114118119141e13
significantdigitsin themantissa
"MapleSt'
Text Alphanumericstrings
‘JohnH.SmithDate 07/12/92
Dateformat10/17/63
Binarylargeobject;anycomplexbinarydataBLOB*
includingimages,documents,etc.
>Short/Long: 整数（Integer）
>Float/Double：小数（Float）

### 第 146 页

![page 146](004-空间数据-知识点回顾/page_146.jpg)

Integer vs. float
》为了存储十进制数据，电脑采用科学计数
法进行存储（包含小数和指数部分）
3.2957239e04 = 32957.239
-3.2957239e04 = -32957.2393.2957239e-04 = 0.00032957239
数学中的科学计数法：
3.2957239 x 104 = 3.2957239e04

### 第 147 页

![page 147](004-空间数据-知识点回顾/page_147.jpg)

Float数据精度
》较大的数字开始出现精度丢失，因为尾数
中有效数字的数量是有限的（如）。
·3295723956249.723
·3.2957239e12 = 3295723900000
>双精度浮点数据（double）为尾数值分配
了更多的存储空间
·3.295723956249723e12 =3295723956249.723

### 第 148 页

![page 148](004-空间数据-知识点回顾/page_148.jpg)

ArcGIS 属性表界面
调整字段宽度
将鼠标悬停
cd110
OBJECTID* Shape NAME ARTY DISTRICTID STFIPS STATE 在两字段交
Polygon Robert A.Brady mocrat 4201 4222422422422 PA2Polygon ChakaFattah Democrat 4202 AAAAAAA 界处，鼠标
3Polygon PhilEnglish Republican 42034Polygon Jason Atmire Democrat 42045Polygon John E.Peterson Republican 4205 呈双箭头后
6Polygon JimGerlach Republican 42067Polygon JoeSestak Democrat 4207 拖动
8Polygon PatrickJ.Murphy Democrat 4208
(0outof437Selected)
US Counties
·临时变化，不会影响文件的存储

### 第 149 页

![page 149](004-空间数据-知识点回顾/page_149.jpg)

ArcGIS 属性表界面
Field Properties 鼠标右键单价字段
Table Name: 名称
Alias: POINT_XDian_A Calcu Type: DoubleFID Sha rC OINTX POINT_YOPoint Prope Display SortAscending 3729637729249323858828
Paint TurnfieldoffStatisticsof Dian_ Coc SortDescendingMakefieldreadonly AdvancedSorting...
FieldPOINTX Highlight fieldStatistics: Number Format: Numeric Summarize...
Minimum:779045.79 Count: 4856 Statistics...
Maximum:796885.44 DataSum: 3838514551 FieldCalculator...
Mean: 790468.40 Units: PrecisionStandardDeviation:2 CalculateGeometry...
Nulls: 0 ScaleTurnFieldOffAbou-
18 Point 15101 3081 DeleteField19PointOK Cancel Properties...
ApplyDianA dem30m
展状态栏
有

### 第 150 页

![page 150](004-空间数据-知识点回顾/page_150.jpg)

ArcGIS 属性表界面
Field Properties POP2010 POP2010
Name: POINTY 1309580 1,310,000
NumberFormat6756150 6.760,000
Category:
None Rounding 983932 984,000
Curency Numberof decimal placesNumenc Numberof significant digits 1338645 1,340,000
DirectionPercentageCustom 662194 662,000
Rate AlignmentFraction 827263 827,000
Scientific LeftAngle ORight characters548154 548.000
Show thousands separatorsPadwithzerosShow plus signGeneraloptionsforthedisplayof numbers 》小数位数、数字有效位数
OK Cancel 对齐方式
OK Cancel Apply 位数补齐...

### 第 151 页

![page 151](004-空间数据-知识点回顾/page_151.jpg)

ArcGIS 属性表界面
选项菜单
三
Find and Replace...
电 Select By Attributes... SUB_REGION STATEABB POP2000 POP2007 POPOO SQMI POIClear Selection Pacific HI 1211537 1299555 189.9
SwitchSelection Pacific WA 5894121 6516384 87.6
SelectAll Mountain MT 902195 959171 6.1
NewEngland ME 1274923 1352536 39.6
AddField... West North Central ND 642200 657816 9.1
Turn AllFields On WestNorthCentral SD 754844 805562 9.8
ShowField Aliases Mountain WY 493782 523174 5
Arrange Tables NewHorizontal TabGroup 5363675 5687426 95.6
NewVertical TabGroup 1293953 1513708 15.5
Restore Default Column WidthsRestoreDefaultFieldOrder Move toPreviousTab GroupJoins and Relates Move to Next Tab GroupRelated TablesCreate Graph...
Add TabletoLayoutReload CachePrint...
ReportsExpor...
Appearance...

### 第 152 页

![page 152](004-空间数据-知识点回顾/page_152.jpg)

ArcGIS属性表界面
Select byAttributes
关找切换选 删除选中项
EnteraWHEREclause toselectrecordsinthe tablewindow.
Method: Create anew selection
"FID"
Table "Id"
"ID_T"
"markero"
"markerG"
StatesSTATENAME STATEFIPS SUB REGION ST <> LikeHawail 15 Pacific AndFind and Replace.... Pacific
<= OrSelectBy Attributes.... MountainClear Selection NewEngland 0 NotWestNorth Central Get Unique Values GoTo:
Switch Selection WestNorth Central Is In NullSelectAll Mountain SELECTFROMDian_AWHERE:
AddField... EastNorthCentralTurn All FieldsOn Mountain IDShow Field Aliases 191
(0outof51Selected) 12121212
ArrangeTables 661661 Clear Verify Help Load. Save.
Restore Default Column WidthsApply CloseRestore DefaultField OrderJoins and RelatesRelated Tables

### 第 153 页

![page 153](004-空间数据-知识点回顾/page_153.jpg)

ArcGIS属性表界面一查询 (query)
Select by Attributes 面
Find&keplaceEnteraWHEREclauseto selectrecordsin the tablewindow. 面 SelectByAttributes...
Method: Create a new selection ClearSelection
"FID" SwitchSelection
"Pl SelectAll
"ID_T""
"markerO" 一些有效的查询
"markerG"
Like "POP1990">1000000
"STATE NAME"=‘AlabamaNot [POP2000]>=[POP1990]
Null Get UniqueValues GoTo:
SELECT·FROMDian AWHERE: DBF表格的字段名用引号括起
来("")
1919191919 Clear Venfy Hep Load... Save. Geodatabase表的字段名用方括
Apply Close 号括起来(1)

### 第 154 页

![page 154](004-空间数据-知识点回顾/page_154.jpg)

ArcGIS属性表界面一查询 J（query)
>使用AND或OR进行多个条件查询
"STATE"=‘Alabama’OR"STATE"="Texas’
[Value]>5000AND[Value]<100005000<[Value]<10000

### 第 155 页

![page 155](004-空间数据-知识点回顾/page_155.jpg)

显示选定项目
SELECT*FROMstatesWHERE:
"P0P2000">2000000
Table xUS States XOBJ Shape NAME ST SUB REGION ABBR POP2000 POP20107 Polygon Wyoming 56 Mountain WY 493782 548.0008 Polygon Wisconsin 55 East North Central WI 5363675 5.740.0009 Polygon Idaho 16 Mountain10 Polygon Vemont 50 NewEnglar Table112 Polygon Minnesota 27 WestNorthPolygon Oregon 41 Pacific13 Polygon New Hampshire 33 NewEnglar US States X1415 Polygon lowa 19 West North OBJ Shape NAME ST SUBREGION ABBR POP2000 POP2010
Polygon Massachusetts 25 NewEnglar Polygon Washington 53 Pacific WA 5894121 6,760.00016Polvaon Nebrask. North 8 2 Polygon Wisconsin 55 East North Central WI 5363675 5.740.00011 Polygon Minnesota 27 West NorthCentral MN 4919479 5.330.0000 (34outof51Sele 12 Polygon Oregon 41 Pacific OR 3421399 3.870.000
USStates 14 Polygon lowa 19 West NorthCentral IA 2926324 3,060,00015 Polygon Massachusetts 25 New England MA 6349097 6.560.00017 Polygon NewYork 36 MiddleAtlantic NY 18976457 19,500,00018 Polygon Pennsylvania 42 Middle Atlantic PA 12281054 12,600,00019 Polygon Connecticut 09 NewEngland CT 3405565 3.540.00021Polvaon 34 lleAtlantic NJ 8414350 8.820.000
(34outof51 elected)
USStates

### 第 156 页

![page 156](004-空间数据-知识点回顾/page_156.jpg)

添加字段
Table 口
xinjiang_cityFID Shape ARBA PBRIMBTBR SHID SHI_D_ID SHI OI0Polygon 116798000000 2096580 10 9 654300
Table 1 Polygon 94874500000 2687920 12 6542003Polygon 2 Polygon 3031240 10716.4 16 65900020032500 34022.8 20 23 23 2229333340 19 18 6590004Polygon 896150000 175066 19 659000
Polygon 7334930000 633100 22 6502006 Polygon 24853600000 985175 24 652700
Polygon 55391000000 1678520 26 6540008Polygon 26657500000 924662 28 6523009Polygon 1171760000 189288 32 65400010 Polygon 46828900000 1138420 33 65230011 Polygon 14202700000 1033380 37 65010012 Polyson 399172000 106625 42 39 65020013 Polygon 137217000000 1691910 40 65220014Polygon 457281000 114874 41 659000 try...
15 Polygon 740451000 227948 43 42 65900016 Polygon 471538000000 4310220 103 102 65280017 Polygon 69325800000 1445060 189 188 65210018 Polyeon 127783000000 2271210 190 189 652900 Lolumn19 Polygon 69899200000 2489520 216 215 65300020Polygon 167685000000 2756660 257 256 62090021 Polygon 111463000000 3401670 259 258 65310022 Polygon 3927410000 419426 260 259 65900023 Polyson 1915670000 331813 266 265 659000 Cancel24Polygon 248088000000 2732210 272 271 65320025 Polygon 253024000000 3282980 659 658 63280026Polygon 337204000000 4618910 828 827 54250027 Polygon 352242000000 4892010 836 835 54240028Polveon 204940000000 3502800 878 877 632700
在添加字段之前，一定考虑好字段名称/类型！

### 第 157 页

![page 157](004-空间数据-知识点回顾/page_157.jpg)

Adding multiple fieldsFeature ClassProperties ？ XIndexes Subtypes Relationships RepresentationsGeneral XYCoordinate System Tolerance Resolution Domain Fields
>Catalog窗口 FieldName Data TypeHSE_UNTS Long IntegerVACANT LongIntegerOWNER_OCC Long Integer
空白行输入字段名 RENTER_OCC LongIntegerNO_FARMS07 DoubleAVG_SIZE07 DoubleCROP_ACR07 Double
设置字段数据类型 AVG_SALE07 DoubleSQMI LongIntegerShape_Length Double
设置字段属性，如别 Shape_Area DoubleHISP_PERCShort Integer
名、空值、默认值等 Click any field to seeits properties. LongIntegerField Properties Float DoubleAlias HISP_PERC Text
应用设置 AllowNULLvalues Yes Date BlobDefaultValue GuidRasterImport...
Toaddanewfeld,typethenameintoanemptyrowintheFieldNamecolumn,likintheData Typecolumn to choose the data type,then edit theFieldProperties.
慎重确定字段名称和字段
的数据类型
OK Cancel Apply

### 第 158 页

![page 158](004-空间数据-知识点回顾/page_158.jpg)

Adding multiple fieldsCatalog窗口→选中目标文件点击鼠标右键→propertiesShapefileProperties FeatureClassPropertiesGeneralXY CoordinateSystemFieldsIndexesFeature Extent General EditorTrackingIndexes Subtypes Feature Extent Relationships RepresentationsXY CoordinateSystem Domain,ResolutionandTolerance FieldsFieldName DataTypeFID ObjectID FieldName Data TypeShape LongInteger Geometry OBJECTID Shape ObjectID Geometryexp Float AREA PERIMETER Float FloatSHENG_ Long IntegerSHENG_ID Long integerSHENG ShortIntegerShape_Length name TextDoubleShape_Area DoubleClickanyfeld toseeitsproperties. Clickanyfield to see its properties.
Field Properties FieldPropertiesPrecision 0 Alias OBJECTDScaleToaddanewfeld，typethenameintoanemptyrowintheFieldNamecolumn，likin ToaddanewfeldtyethenameintoanemptyrowinthFieldNamecolumndikinthe Data Type column to choose the data type,thenedithe Field Properties. the Data Type column to choose the data type,then edit the Field Properties.
确定 取消 应用（A） 确定 取消 应用（A)

### 第 159 页

![page 159](004-空间数据-知识点回顾/page_159.jpg)

字段编辑与计算
Editing and calculating fields

### 第 160 页

![page 160](004-空间数据-知识点回顾/page_160.jpg)

编辑记录
开始编辑
Start EditingThismap contains datafrommore thanonedatabase orfolder.
Pleasechoose thelayerorworkspace toedit. Editordem30m.vatDian_A 选中需要编辑的图 StartEditing
层，并点击OK Stop EditingSaveEditsDoyou want to saveyouredits? 存编辑、停止编辑
是(M） 否（N) 取消
EditorSource Typee:\spatialdata\dem30\dem30m\ ArcInfo Workspace Start EditingG:\Rs_InterpretationspatialPointsClustered Shapefiles/dBaseFilesStop EditingSave EditsAboutediting andworkspaces OK Cancel

### 第 161 页

![page 161](004-空间数据-知识点回顾/page_161.jpg)

字段计算
SortAscendingField Calculator ？
SortDescendingAdvanced Sorting... ParserVBScript PythonSummarize... Fields: Type: Functions:
Shape ONumber Abs()
Statistics... STATE_NAME At()
STATE_FIPS sting Cos()
Field Calculator... SUB_REGION Exp() Fix（)
Date Int()
CalculateGeometry... STATE_ABBR Log(）
POP2000 Sin()
TurnFieldOff POPOO_SQMI POP2010 ()bs Tan()
Freeze/UnfreezeColumn POP10_SQMIshowCodeblock &
DeleteField +
Properties.. [HISPANIC]/[POP2000]*100
选择字段，点击右键；
计算的字段通常为“空字段
字段计算无法执行撤销操作， Clear Load... Save... Hep
除非是在编辑模式下 OK Cancel

### 第 162 页

![page 162](004-空间数据-知识点回顾/page_162.jpg)

字段计算 （高级处理）
级类型 二级类型
编号 名称 编号 名称 含义
水域 指天然陆地水域和水利设施用地。
41 河渠 指天然形成或人工开挖的河流及主干常年水位以下的土
地。人工渠包括堤岸。
42 湖泊 指天然形成的积水区常年水位以下的土地。
43 水库坑 指人工修建的蓄水区常年水位以下的土地。
塘
永久性
44 冰川雪 指常年被冰川和积雪所覆盖的土地。
地
45 滩涂 指沿海大潮高潮位与低潮位之间的潮浸地带。
46 滩地 指河、湖水域平水期水位与洪水期水位之间的土地。 LUC1995.TIF
城乡、工 OID Value Count
矿、居民 指城乡居民点及其以外的工矿、交通等用地。 0 11 6738377
用地 218345842 1506090851 地 城镇用 指大、中、小城市及县镇以上建成区用地。 3 94174234 898738152 农村居 民点 指独立于城镇以外的农村居民点。 6 1577774 294277550453153 其它建指厂矿、大型工业区、油田、盐场、采石场等用地以及交 设用地通道路、机场及特殊用地。 8 13503685195
未利用土 10 1122
b 地 目前还未利用的土地，包括难利用的土地。 72411
指地表为沙覆盖，植被覆盖度在5%以下的土地，包括沙 1105561 沙地 漠，不包括水系中的沙漠。 204555653462 戈壁 指地表以碎砾石为主，植被覆盖度在5%以下的土地。 26974

### 第 163 页

![page 163](004-空间数据-知识点回顾/page_163.jpg)

字段计算 （高级处理）
FieldCalculator FieldCalculatorParser ParserOvBScript OPython OVBScript OPythonFields: Type: Functions: Fields: Type: Functions:
OID ONumber Abs（) Atn(） OID ONumber .conjugateOValue Ostring (so Value .denominatorOCount Exp() Count Ostring .numeratorO .imag0
luc ODate Fix(） luc ODate .realoInt（) .as_integer_ratio0
Log() .fromhexoSin(） .hexoSqr(） .is_integerOTan() math.acos()
math.acosh()
math.asin()
showCodeblock ShowCodeblockluc= Pre-Loqic Script Code:
deftransform(x):
if0<x<20: return耕地”
elif20<=x<30:
return“林地”
elif30<=x<40:
rehn草+thtransform(!Value!jAboutcalculatingfields Clear Load... Save... Aboutcalculatinq fields Clear Load... Save...
OK Cancel OK Cancel

### 第 164 页

![page 164](004-空间数据-知识点回顾/page_164.jpg)

字段计算 （高级处理）
Python代码 1221 22
def transform(x): 23 2431 32
if0<x<20: 41 33
return"耕地" □42 4346 51
elif20<=x<30: 52 53
return"林地"
elif30<=x<40:
return"草地"
elif40<=x<50:
return"水域"
else:
return"建筑用地” LUC1995
津筑电 ucLUC1995.TIF 材地 水城
普联地
OID Value Count luc0 11 6738377 耕地
21834584耕地
2 15060908 林地
9417423 林地
4 8987381 林地
5 294277 林地
6 1577774 苹地
5504531 苹地
8 135036草地
9 85195水城
1122水城
72411水城
11055水城
204555注筑用地
6534注筑用地
26974注筑用地

### 第 165 页

![page 165](004-空间数据-知识点回顾/page_165.jpg)

ArcGIS中的除法
>数学中1/2=0.5;
>ArcGIS软件常用Python2.7进行工具的编写；
>在python2.7中/表示除法（IntegerDivision），
1/3=0,1/2=0,2/3=0,5/2=2，向下取整
>避免错误：将Integer转化为float.
E.g. 1.0/3 = 0.33, 1/2.0=0.5, 2.0/3.0 = 0.67, 5.0/2 = 2.5

### 第 166 页

![page 166](004-空间数据-知识点回顾/page_166.jpg)

矢量数据的几何测量
自动创建与维护（Geodatabasefeaturesclasses)
字段通常位于属性表的末端
·Shape_AreaShape_Length
单位将匹配坐标系中的单位
US StatesAVG_SIZE07 CROPACROAVG_SALE07 SQMI ShapeLength Shape_Area149 177626 68.29 10931 1275835.715167 16513001143.5337381 7609210 172.92 71297 3004175.455006 164442316568.0452079 18241710 94.94 14703 2859079.544323 359662292212.805166 529253 75.86 39555 1804888.364454 78384814218.17521241 27527180 190.31 70698 1753454.614357 173072126682.4011401 19094311 210.8 77115 1943874.72695 187970221480.162726 2576017 104.58 97813 1960001.350821 238004239410.541194 10116279 114.2959822 1968992.210358 136605586997.204
(0outof51Selected)

### 第 167 页

![page 167](004-空间数据-知识点回顾/page_167.jpg)

矢量数据的几何测量 （Shapefile）
>Shapefiles不会自动创建或维护Area/Length
字段！
·必须手动创建和更新
一些函数和操作可以改变features的长度和面积
如果您找到一个AREA字段，则不能保证它是
正确的.
watershedsFID Shape AREA PERIMETER NAME AREA_ACRE0Polygon 5265900 16620 Nameless Cave 1301.231 Polygon 765900 5700 RobbinsdaleParkEast 189.2572 Polygon 1311120 27480RedRockCanyon 3239.84013Polygon 2283300 9780 WonderlandDrive 564.213014 Polygon 511200 4140 Highway79IndustrialPark 126.325 Polygon 4786200 15780 SouthRobbinsdale 1182.68999 Polygon 1192060 25782.6 Landfil 2945.62991014020 22000.6 TeolDD 2505.C000

### 第 168 页

![page 168](004-空间数据-知识点回顾/page_168.jpg)

Be careful!
Table XwatershedsFID Shape AREA PERIMETER NAME AREAACRE PERCENT Shapefiles文件
0 Polygon 5265900 16620 Nameless Cave 1301.23 3.0465
Polygon 765900 5700 RobbinsdaleParkEast 189.257 0.443099 发生变化时
2 Polygon 1311120 27480 Red RockCanyon 3239.8401 7.585283 Polygon 2283300 9780 WonderlandDrive 564.21301 1.320974 Polygon 511200 4140 Highway79 Industial Park 126.32 0.295747 （裁剪、融合、
5 Polygon 4786200 15780 South Robbinsdale 1182.6899 2.768986 Polygon 1192060 25782.6 Landfill 2945.6299 6.89646
Pahinan 1014020 220086 TnilR.Pae 25056899 586647 编辑）属性表
(0outof26Selected) 中的
watershedsAREA/LENGTH/PERIMETER字段不会
自动更新。
Before After

### 第 169 页

![page 169](004-空间数据-知识点回顾/page_169.jpg)

使用几何计算工具
选择空字段或需更
新字段，点击右键 选择需要计算的几何类
选择“Calculate 型、坐标系以及单位
GeometryCalculateGeometry ？
AREAACRE PERCENTIE Property: Area13012 SortAscending Coordinate System189.2 SortDescending OUsecoordinatesystem of thedata source:
3239.84 PCS:NAD 1927UTMZone 13N564.213 Advanced Sorting..
126. Usecoordinate systemof thedata frame:
1182.68 Summarize... PCS:North America Equidistant Conic2945.62 Statistics...
250568 Units: Acres Us[ac]
Field Calculator...
Calculate Geometry... Calculate selectedrecordsonlyTurnField Off Help OK Cancel
