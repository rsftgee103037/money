import xml.etree.ElementTree as ET
#匯入xml函式庫，並命名為ET
import requests #最基本的爬蟲指令
import time #匯入時間函市庫
from openpyxl import Workbook
def xml_to_dict(element):   #把xml轉換為dictionary的函式
    result = {}
    for child in element:
        if len(child) == 0:
            result[child.tag] = child.text
        else:
            result[child.tag] = xml_to_dict(child)
    return result
def returnStrDayList(startYear,startMonth,endYear,endMonth,day = "01"):
    startYear,startMonth,endYear,endMonth = int(startYear),int(startMonth),int(endYear),int(endMonth)
    #把年跟月整數化
    
    result = []#儲存所有的年月日
    if startYear == endYear:#如果只要查詢同年份的話
        for month in range(startMonth,endMonth):
            month = str(month) #轉換成文字格式
            if len(month) == 1: #如果沒有0
                month = "0" + month #補0
            result.append(str(startYear) + month + day)
        return result
    #以下為不同年份的時候
    for year in range(startYear,endYear+1):
        if year == startYear: #代表只讀取startMonth之後的月份
            for month in range(startMonth,13):
                month = str(month)
                if len(month) == 1:
                    month = "0" + month
                result.append(str(year) + month + day)
        elif year == endYear: #代表只需讀取endMonth之前的月份
            for month in range(1,endMonth+1):
                month = str(month)
                if len(month) == 1:
                    month = "0" + month
                result.append(str(year) + month + day)
        else: #代表要讀取一整年的月份
            for month in range(1,13):
                month = str(month)
                if len(month) == 1:
                    month = "0" + month
                result.append(str(year) + month + day)
    return result
def fillSheet(sheet,data,row): #建立填充sheet的function
    """
    sheet:表格名稱
    data:資料
    row:第幾行
    """
    for column, value in enumerate(data,1):
        sheet.cell(row = row,column = column, value = value)
        #將value填入在第row行第column列中
        
tree = ET.parse("setting.xml") #讀取設定檔
root = tree.getroot() #獲取裡面的資料
data = xml_to_dict(root) #把資料轉化為dictionary處理
fields = ["日期","成交股數","成交金額","開盤價","最高價","最低價","收盤價","漲跌價差","成交比數"]
startYear = data["startYear"]
startMonth = data["startMonth"]
endYear = data["endYear"]
endMonth = data["endMonth"]
yearlist = returnStrDayList(startYear,startMonth,endYear,endMonth)
wb = Workbook() #打開excel檔案
sheet = wb.active #啟動excel並建立表格
sheet.title = "每日成交統計表"
row = 1
fillSheet(sheet,fields,row)
row = row + 1
#以下要透過yearlist抓取每一月份的資料
for month in yearlist:
    rq = requests.get(data["url"],params = {
            "date":month,
            "stockNo":data["stockNo"],
            "response":"json"
    })
    print(rq) #確認目前http狀態碼是否正常
    if str(rq) != "<Response [200]>": #狀況不對
        break #停止運行
    jsonData = rq.json()#讀取json格式的資料
    dailyPricesList = jsonData.get("data",[]) #從json裡面抓取data資料，裡面含有日成交資訊
    for dailyPrices in dailyPricesList: #迭代資料
        fillSheet(sheet,dailyPrices,row)
        row = row + 1 #換到下一行

    time.sleep(3)
name = data["excelName"]
wb.save(name + ".xlsx")