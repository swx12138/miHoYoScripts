##

from os import chdir, mkdir
from os.path import exists

import matplotlib.pyplot as plt

from miHoYo.Genshin.Gacha import GachaLog, GachaPools, Print_Console


# TODO 图表显示
def See_LocalData(all_local: dict):
    """可视化"""

    # 支持中文
    plt.rcParams["font.sans-serif"] = ["SimHei"]  # 用来正常显示中文标签
    plt.rcParams["axes.unicode_minus"] = False  # 用来正常显示负号

    # 每个池子统计
    index = 1
    for pname in all_local:
        # 四星五星数量
        count = {
            "five": 0,
            "four": 0,
            "all": len(all_local[pname]),
        }

        for data in all_local[pname]:
            if data["rank_type"] == "5":
                count["five"] += 1
            elif data["rank_type"] == "4":
                count["four"] += 1

        plt.subplot(2, 2, index)

        plt.pie(
            x=[
                count["five"],
                count["four"],
            ],
            labels=["五星", "四星"],
            colors=["yellow", "purple"],
        )

        index += 1
    plt.title("统计")
    plt.show()


if __name__ == "__main__":
    HOME_PATH = "GachaData"
    if not exists(HOME_PATH):
        mkdir(HOME_PATH)
    chdir(HOME_PATH)

    all_five = {}

    for gacha_type in GachaPools:
        gl = GachaLog(gacha_type=gacha_type)
        gl.update()
        gl.save()
        all_five[GachaPools[gacha_type]] = gl.countFive()

    print("update all done.")

    # 控制台输出5星统计表格
    #   - 可选：输出到excel
    Print_Console(all_five, True)

    # See_LocalData(all_data)
