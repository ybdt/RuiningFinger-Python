import json


# 去除重复指纹
def Func1():
    with open("Ruining-Finger.json", "r") as fr:
        with open("new-Ruining-Finger.json", "w") as fw:
            fingerprint = json.load(fr)
            finger_list = fingerprint["fingerprint"]
            print("去重前指纹数：{}个".format(len(finger_list)))
            
            # 指纹去重
            count = 1  # 计算重复个数
            duplicate_flag_list = []  # 存储指纹，用于去重比对
            new_finger_list = []  # 此列表用于存储新指纹
            for each in finger_list:
                cms = each["cms"]
                method = each["method"]
                location = each["location"]
                keyword = each["keyword"]
                finger_str = cms + method + location + str(keyword)
                if finger_str.lower() in duplicate_flag_list:
                    print("{}   {}, {}, {}, {}".format(count, cms, method, location, keyword))
                    count += 1
                    continue
                else:
                    duplicate_flag_list.append(finger_str.lower())
                    new_finger_list.append(each)
                    count += 1
            
            print("去重后指纹数：{}个".format(len(new_finger_list)))
            new_finger_dict = {"fingerprint": new_finger_list}
            new_finger_str = json.dumps(new_finger_dict, indent=4, ensure_ascii=False)
            fw.write(new_finger_str)


# 查看字段cms、method、location的值是否有列表，经检测，字段cms、method、location的值没有列表
def Func2():
    with open("Ruining-Finger.json", "r") as fr:
        fingerprint = json.load(fr)
        finger_list = fingerprint["fingerprint"]
        for each in finger_list:
            cms = each["cms"]
            method = each["method"]
            location = each["location"]
            if isinstance(cms, list):
                print(each)
            if isinstance(method, list):
                print(each)
            if isinstance(location, list):
                print(each)


# 挑出包含多个指纹的CMS
def Func3():
    with open("Ruining-Finger.json", "r") as fr:
        fingerprint = json.load(fr)
        finger_list = fingerprint["fingerprint"]
        cms_list = []  # 存储cms，用于去重比对
        count = 1
        for each in finger_list:
            cms = each["cms"]
            if cms not in cms_list:
                cms_list.append(cms)
            else:
                print(f"{count}   {each}")
                count += 1