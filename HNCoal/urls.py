"""HNCoal URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from . import views,data_views
from UserManagement import urls as userManagement_urls
from QA_Module import urls as qa_module_urls
# from KnowledgeExtraction import url as KnowledgeExtraction_urls
urlpatterns = [
    path('admin/', admin.site.urls),
    # path('map',data_views.queryDeviceNumber),
    path('map',data_views.queryDeviceNumber2),  # 设备数量统计_peng
    path('queryNeo4jInfoByname',views.queryNeo4jInfoByname),
    path('queryNeo4jInfoByID',views.queryNeo4jInfoByID),
    path('FuzzyQueryName',views.FuzzyQueryName),
    path('downloadInstructions',views.downloadInstructions), # 下载说明书
    path('saveNodeToCSV',data_views.saveNodeToCSV), # 保存为excel
    path('saveNodeToWorld',data_views.saveNodeToWorld), # 保存为world
    path('showNodeForTable',data_views.showNodeForTable), # 前端表格展示所需数据
    path('uploadExcelData',views.uploadExcelData),
    path('classifyNode',views.classifyNode),
    path('User/',include(userManagement_urls)),  # 登陆管理
    path('QA/',include(qa_module_urls)),
    path('queryAllLargeEquipment',views.queryAllLargeEquipment),
    path('entityImport',views.entityImport),
    path('tripleImport',views.tripleImport),
    path('uploadTXT_WORD_PDF',views.uploadTXT_WORD_PDF)
]
