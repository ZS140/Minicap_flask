# Minicap_flask
python for minicap
## minicap的使用：
### 准备对应文件：
a、查看CPU架构（adb shell getprop ro.product.cpu.abi）及查看android版本level（adb shell getprop ro.build.version.sdk）

b、根据获取的CPU和版本信息，将适合设备的可执行文件和.so文件push到手机的/data/local/tmp目录下，或者在STF框架的源码下找到vendor/minicap文件夹下

c、adb shell进入到目录下chmod 777 minicap

d、测试一下minicap是否可用：（-P后面跟的参数为你屏幕的尺寸）

 　　adb shell LD_LIBRARY_PATH=/data/local/tmp /data/local/tmp/minicap -P 1080x1920@1080x1920/0 -t
### 本地端口转发：
为了实现socket服务通信，必须将本地端口映射到minicap工具上
adb forward tcp:1717 localabstract:minicap
### 启动手机端服务：
启动一个socket服务
adb shell LD_LIBRARY_PATH=/data/local/tmp /data/local/tmp/minicap -P 1080x1920@1080x1920/0
### 信息发送：
#### 第一部分
>banner模块:这一部分的信息只在连接后，只发送一次，是一些汇总信息，一般为24个16进制字符，每一个字符都表示不同的信息：

    位置	         信息
    0	        版本
    1               该Banner信息的长度，方便循环使用
    2，3，4，5	相加得到进程id号
    6，7，8，9	累加得到设备真实宽度
    10，11，12，13	累加得到设备真实高度
    14，15，16，17	累加得到设备的虚拟宽度
    18，19，20，21	累加得到设备的虚拟高度
    22	        设备的方向
    23	        设备信息获取策略
#### 第二部分
>携带图片大小信息和图片二进制信息模块:得到上面的Banner部分处理完成后，以后不会再发送Banner信息，后续只会发送图片相关的信息。那么接下来就接受图片信息了，第一个过来的图片信息的前4个字符不是图片的二进制信息，而是携带着图片大小的信息，我们需要累加得到图片大小。这一部分的信息除去前四个字符，其他信息也是图片的实际二进制信息，比如我们接受到的信息长度为n，那么4～(n-4)部分是图片的信息，需要保存下来。
#### 第三部分
>只携带图片二进制信息模块：每一个变化的界面都会有上面的[携带图片大小信息和图片二进制信息模块]，当得到大小后，或许发送过来的数据都是要组装成图片的二进制信息，直到当前屏幕的数据发送完成。 
## Python基于flask框架的实现：
>1、创建app应用
>2、创建HTML页面，通过app路由将页面绑定到应用上
>3、创建socketio对象，用于实现前后端的实时通信，
