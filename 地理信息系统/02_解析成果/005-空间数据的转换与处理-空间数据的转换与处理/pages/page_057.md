# 空间数据的转换与处理 — 第 57 页

> 来源: 005-空间数据的转换与处理-空间数据的转换与处理.pdf
> 页码: 57
> OCR置信: 91.8%

![page 57](../page_057.jpg)

>投影转化 矢量数据（Feature）
ArcGIS 10.6 Help 口

#### 国 回

#### 隐藏 进 主页 选项（Q）
目录（ 收藏· Project(Data Management)
田Get started ArcGIS 10.6
田Map License LevelBasis standd ocate topi
田Manage data Analyze Summary
田Tools Projects spatial data from one coordinate system to another.
田Extensions UsageCopyright inf License agreeArcGIS Acknc system to the dataset. the data's coordinate system without having to modify the input dataArcScene,and ArcGlobe)are valid input.
To project aCoverage,use the Project tool in the Coverage toolbox.
The tool's GeographicTransformationparameteris optional.When no geographic or datum transformationisrequired,no drop-down list willappear on the parameter and it is left blank.When a transformationisrequired, a drop-down list willbe generated based on theinput and output datums, and a default transformation will be picked. For example,a geographic transformation isnotrequiredwhen projecting fromGCS_North_American_1983 to NAD_1983_UTM_Zone_12Nbecause both the input and output coordinate systems havea NAD_1983
datum.However,projecting fromGCs_North_Amenican_1983 to wGS_1984_UTM_one_12Nrequiresageographictransformationbecause theinputcoordinate systemuses theNAD_1983 datum, while the output coordinate system uses the WGS_1984 datum.
Tip:Transformations are bidirectional.Forexample,if converting data from wGS 1984 to NAD 1927,you can picka transformation called NAD_1927_to_wGS_1984_3,and the tool willapply it correctly.
horyworkspaceisnotsupportedasa location to writetheoutputdataset.
When projecting the complex data typeslisted below,certain operationsneed to be performed on theresulting data:
If theinput participatesin relationship classes(as with feature-linked annotation),the relationship class wilbe transferred to the output.The exception to thisrulerelates toparticipating stand-alone tables.
Depending on the input feature coordinate system,multipoint,line,and polygonmaybe clipped or splitinto more than onepartwhen projecting them.
Features thatfallcompletelyoutside thehorizo These canbe deletedusing the Repair etrytool.
Feature classes participating ina geometricnetwork ca -the entire feature datasetcontaining the networkneeds to beprojected.
Many geoprocessing tools honor the gutputc the output coordinate system environment setting,whichan entirely different coordinate system.
Selection and definition query on layers are ignored by this tool-allfeatures in the datasetreferencedby the layer wilbe projected.If you want to project selected features only,consider using theCopy Features Leam more about geoprocessing environmentstool to create a temporary dataset, which will only contain the selected features,and use this intermediate dataset as input to the Project tool.
Whenafeature class withinafeature datasetisusedasinput,the outputcannotbewritten to thesame feature dataset.Thisisbecausefeature classeswithina featuredatasetmustallhave the same coordinate system.In this case, the output feature class will be written to the geodatabase containing the feature dataset.
The PreserveShape parameter,when checked,creates outputfeatures thatmore accuratelyrepresent their true projected location.Preserve Shae isespecially usefulincases where a line or polygon boundaryisdigitizedasalong,straightlinewithfewvertices.If Preserve Shapeisnotchecked,theexistingverticesof theinputline orpolygonboundaryareprojected,andtheresultmaybeafeature thatisnotaccuratelylocation as computedby the tool.when the value is small,more verticesareadded.Choose avalue that suitsyourneeds.For example,if your projected output is for general smallscale cartographic display,a large projected shape of the feature.The MaximumOffset Deviation parameter controlshow many extravertices are added;itsvalueis the maximum distance the projected feature canbe offset from its exact projected
