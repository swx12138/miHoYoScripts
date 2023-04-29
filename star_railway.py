# -- coding: utf-8 --

import json
from os import mkdir, path
from time import sleep

import requests

from miHoYo.Genshin.Gacha import get_params, item_in_data, item_in_data_raw

gacha_type = {
    11: "角色活动跃迁",
    12: "光锥活动跃迁",
    1: "始发跃迁",
    2: "群星跃迁",
}


class GachaLogContext(object):
    PAGE_SIZE = 20

    def __init__(self, params, gacha_type) -> None:
        self._Api = "https://api-takumi.mihoyo.com/common/gacha_record/api/getGachaLog"
        self._Params = params
        self._Params["end_id"] = "0"  # 从第一页开始
        self._PoolId = self._Params["gacha_type"] = gacha_type
        self._LocalData, self._Local_End_Id = GachaLogContext.ReadLocalData(self._PoolId)
        self._Page = 1
        self._End_Id = "0"

    @staticmethod
    def ReadLocalData(pool_id):
        try:
            with open(f"GachaData\\{pool_id}_sr.json", 'r', encoding="utf-8") as localData:
                data = json.load(localData)
                return data, data[0]['id']
        except FileNotFoundError:
            print("can not found local data.")
        return {}, "0"

    def __GetNextPage(self):
        """ 其实page没啥用，api使用的是end_id定位，page_size决定返回多少 """

        self._Params["size"] = GachaLogContext.PAGE_SIZE
        self._Params["page"] = self._Page
        self._Params["end_id"] = self._End_Id

        print(f"request page:{self._Page}   end_id:{self._End_Id}", end="\t\t")
        resp = requests.get(url=self._Api, params=self._Params)
        data = resp.json()
        if data["retcode"] == 0:
            self._Page += 1
            self._End_Id = data["data"]["list"][-1]["id"]  # 更新end_id
            print("done.")
            return data["data"]
        else:
            raise Exception(f"request failed : page:{self._Page},message:{data['message']}")

    def Update(self, max_page=-1):
        if max_page == -1:
            max_page = 0xfffff  # 一个人应该抽不了520w抽......吧

        # request
        tempory_data = []
        while self._Page < max_page:
            page_data = self.__GetNextPage()["list"]
            tempory_data.extend(page_data)
            if len(page_data) < GachaLogContext.PAGE_SIZE:  # 最后一页了
                break
            elif item_in_data_raw(self._Local_End_Id, page_data)[0]:  # 后面是已经在本地的数据
                break
            else:
                sleep(0.1)  # 降低接口访问频率

        # merge
        if tempory_data:
            if self._LocalData:
                repeat_len = 0
                isInsise, pos = item_in_data(tempory_data[-1], self._LocalData)
                if isInsise:
                    repeat_len = pos
                self._LocalData = tempory_data + self._LocalData[repeat_len + 1:]
                print(f"update succeed.  total:{len(self._LocalData)}, new:{len(tempory_data)-repeat_len-1}")
            else:
                self._LocalData = tempory_data
                print(f"update succeed.  total:{len(self._LocalData)}, new:{len(tempory_data)}")
        else:
            print(f"did not update any dat,pool_id:{self._PoolId}, end_id:{self._Local_End_Id}")

    def CountFive(self):
        local_data = list(reversed(self._LocalData))
        _fives = []
        gacha_times = 0  # 没五星的祈愿数量
        for data in local_data:
            gacha_times += 1
            if data["rank_type"] == "5":
                _fives.append({"name": data["name"], "times": gacha_times})
                gacha_times = 0
        _fives.append({"name": "水位", "times": gacha_times})
        return _fives

    def Save(self):
        with open(f"GachaData\\{self._PoolId}_sr.json", 'w', encoding="utf-8") as localData:
            json.dump(obj=self._LocalData, fp=localData, ensure_ascii=False, indent=4)


def read_params_in_local_txt():
    with open("UserData\\star_railway_gacha.txt") as star_railway_gacha_txt:
        return get_params(star_railway_gacha_txt.read())


if __name__ == "__main__":
    if not path.exists("GachaData"):
        mkdir("GachaData")

    all_fives = {}
    for ty in gacha_type.keys():
        params = read_params_in_local_txt()
        ctx = GachaLogContext(params, ty)
        ctx.Update()
        all_fives[ty] = ctx.CountFive()
        ctx.Save()

    for ty in all_fives.keys():
        print(gacha_type[ty])
        for five in all_fives[ty]:
            print("\t", five)
