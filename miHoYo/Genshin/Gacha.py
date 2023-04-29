##

import getpass
import json
from os import chdir
import time
from os.path import exists
from urllib import parse

import requests
from pandas import DataFrame, ExcelWriter
from tabulate import tabulate

GachaPools = {
    301: "角色限定祈愿",
    302: "神铸赋形",
    200: "奔行世间",
    100: "新手祈愿",
}


def getDefaultLogPath():
    """log的默认路径"""
    user = getpass.getuser()
    # replace("原神","Genshin Impact") #global
    return f"C:\\Users\\{user}\\AppData\\LocalLow\\miHoYo\\原神\\output_log.txt"


def getGachaLogPage_deprecated():
    """读取Log中的祈愿记录页面链接"""
    with open(getDefaultLogPath(), "r", encoding="utf-8") as log:
        for line in log.readlines():
            if line.startswith("OnGetWebViewPageFinish") and -1 != line.find("gacha"):
                return line[23:-1]
    raise Exception("getGachaLogPage : log中没有祈愿记录链接.")


def get_params(url: str):
    """获取链接中的参数"""
    p = parse.urlparse(url=url)
    qs = p.query.split("&")

    params = {}
    for q in qs:
        s = q.split("=")
        params[s[0]] = s[1]

    if "ext" in params:
        params["ext"] = json.loads(parse.unquote(params["ext"]))

    if "authkey" in params:
        params["authkey"] = parse.unquote(params["authkey"])

    return params


def make_url_with_param(url, params):
    return url + "?" + "&".join([f"{key}={parse.quote(params[key])}" for key in params])


def write_params_to_file(params: dict):
    """查询参数写入本地"""
    with open("gacha_params.json", "w", encoding="utf-8") as file:
        json.dump(params, file, ensure_ascii=False, indent=4)


def item_in_data_raw(end_id, data):
    # 本地数据的最新end_id是否包含在data中
    index = 0
    for dat in data:
        if dat["id"] == end_id:
            return True, index
        index = index + 1
    return False, -1


def item_in_data(item, data):
    return item_in_data_raw(item["id"], data)


class QueryGachaLog(object):

    def __init__(self, gacha_type, page_size) -> None:
        self.gacha_type = gacha_type
        self.page_size = page_size
        self.end_id = 0
        self.all_data = []

    def Get(self, page_num):
        resp = requests.get(
            # url
        )

        # 解析数据
        rb = json.loads(resp.content)
        retcode = rb["retcode"]
        print(f"page:{page_num}  end_id:{self.end_id}  code:{retcode}  msg:{rb['message']}")

        # 服务器正常响应并处理
        if retcode == 0:
            return rb["data"]

        # 服务器未正常处理请求
        print("getGachaLog Failed : ", retcode, rb["message"])
        raise Exception("getGachaLog : request failed.")

    def GetAll(self, last_query_end_id):
        page_num = 1
        while True:
            ls = self.Get(page_num=page_num)["list"]

            # 查询结束
            if not len(ls):
                break

            # 查询结果包含在本地数据中
            i, p = item_in_data_raw(last_query_end_id, ls)
            if i:
                self.all_data.extend(ls[:p])
                # self.all_data.extend(ls[:self.all_data.index(ls[-1])])
                break

            # 合并数据
            self.all_data.extend(ls)

            # 更新end_id
            self.end_id = ls[-1]["id"]

            # 更新页码
            page_num = page_num + 1

            # 降低接口访问频率
            time.sleep(0.2)

        return self.all_data


class GachaLog(object):

    def __init__(self, gacha_type) -> None:
        self._Gacha_Type = gacha_type
        self._Log_Data = GachaLog.Read_NewBetter(gacha_type=gacha_type)
        self.__Five_Update = True
        self._Fives = []

    # 上一次查询的最后一个祈愿的id,作为本查询的输入,代表从这里开始
    def getEndID(self):
        return self._Log_Data[0]["id"]

    # 从祈愿记录页更新
    def update(self):
        """从祈愿记录页更新本地数据"""

        print(f"updating {GachaPools[self._Gacha_Type]} end_id:{self.getEndID()}")

        # 获取新数据
        qgl = QueryGachaLog(self._Gacha_Type, 20)
        all_data = qgl.GetAll(self.getEndID())

        if all_data:
            # all_data_size = len(all_data)
            repeat_len = 0
            i, p = item_in_data(all_data[-1], self._Log_Data)
            # if all_data[-1] in self._Log_Data:
            if i:
                repeat_len = p  # self._Log_Data.index(all_data[-1])
            self._Log_Data = all_data + self._Log_Data[repeat_len:]
            self.__Five_Update = True
        else:
            print(f"did not update {GachaPools[self._Gacha_Type]} end_id:{self.getEndID()}")

    # 写入本地文件
    def save(self):
        with open(f"{self._Gacha_Type}_nb.json", "w", encoding="utf-8") as file:
            json.dump(obj=self._Log_Data, fp=file, ensure_ascii=False, indent=4)

    # 统计五星数量
    def countFive(self):
        if self.__Five_Update:
            local_data = list(reversed(self._Log_Data))
            gacha_times = 0  # 没五星的祈愿数量
            for data in local_data:
                gacha_times += 1
                if data["rank_type"] == "5":
                    self._Fives.append({"name": data["name"], "times": gacha_times})
                    gacha_times = 0
            self._Fives.append({"name": "当前", "times": gacha_times})
            self.__Five_Update = False
        return self._Fives

    @staticmethod
    def Read_NewBetter(gacha_type: int) -> list:
        """读取本地抽卡记录"""
        filename = f"{gacha_type}_nb.json"
        if not exists(filename):
            return []

        with open(filename, "r", encoding="utf-8") as file:
            return json.load(fp=file)

    @staticmethod
    def Get_EndId(gacha_type: int):
        with open(str(gacha_type) + "_nb.json", "r", encoding="utf-8") as file:
            return json.load(fp=file)[0]["id"]


class GachaLink(object):
    def __init__(self, url) -> None:
        self._Param = get_params(url)

    def Query(pageNum: int):
        return


def Print_Console(all_five: dict, export: bool = False):
    """输出五星统计表格到控制台"""
    all_ff = {}
    max_len = max([len(five) for five in all_five.values()])  # 5星最多的池子里5星数量
    for five in all_five:
        fives = all_five[five]
        all_ff[five] = [f"{f['name']}[{f['times']}]" for f in fives]  # name[times]
        all_ff[five].extend([None] * (max_len - len(all_ff[five])))  # 长度对齐

    # 控制台输出
    # pandas.set_option('display.unicode.ambiguous_as_wide', True)
    # pandas.set_option('display.unicode.east_asian_width', True)
    # pandas.set_option('display.width', 360)
    df = DataFrame(all_ff)
    print(tabulate(df, headers=df.head(0), tablefmt="fancy_grid"))

    # 导出excel
    if export:
        with ExcelWriter(f"export.xlsx") as writer:
            for five in all_five:
                DataFrame(all_five[five]).to_excel(
                    writer,
                    sheet_name=five,
                    index=False,
                    encoding="utf-8",
                )


if __name__ == "__main__":
    chdir("GachaData")
    gl = GachaLog(302)
    gl.update()
