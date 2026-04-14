# 先是这里合作仓库怎么开发的说明
### 1.下次上传要忽略的大文件和无意义文件：
我这个云端仓库gitignore排除的东西有：IDE 配置：.idea/.vscode/  虚拟环境：.venv（这个你自己本地新建一个去下东西，如果本来就跑通了挪过来就好）/  Python 缓存：__pycache__/  输出文件与图片：output/ out.png  （从老师那个私密仓库拉下来就一堆图，没什么用，估计训练数据）备份文件：requirements.txt.bak requirements.txt.bak2
模型文件：stygan/ffhq.pkl（因为这个是GAN的，我们不用了）

因为这种配置文件和大文件太大了，会超出GitHub提交容量的上限，所以我们本地跑测归本地的，上传的时候忽略这些文件即可。你下次提交问一下ai就会很简单。
### 2.这个仓库从今往后就我俩管
我不用刘老师给的那个gitea私密仓库是因为那个我上传之后估计还要等他审核你才能看到我的版本，他比较忙，所以不如我们两个改完给他看过了再传。他有时会冒出奇怪的需求（）。
你改你负责的功能的时候让ai帮你在我这个版本上创建一个分支，在你自己的分支上改，本地也可以创建多分支改坏了随时回滚，确定没问题之后再提交push到云端的main。我没有设置你提交的代码需要给我审核，因为我懒，如果提交到main的有问题你自己回滚就行。

以上管理用Git命令行[忽略这个视频标题](https://www.bilibili.com/video/BV1Hkr7YYEh8/?spm_id_from=333.337.search-card.all.click&vd_source=f826d8c9e6eb7ace5b7fcc9ce6838df9)都可以实现，但是我还是推荐你可以下一个GitHubdesktop[教程](https://www.bilibili.com/video/BV13W411U7HY/?spm_id_from=333.337.search-card.all.click&vd_source=f826d8c9e6eb7ace5b7fcc9ce6838df9)，因为图形化操作比较方便。国产大模型和copilot免费版写命令行都宛若智障。（呃我知道我们可以直接打包压缩包扔来扔去改代码但是这样的话每次都得处理一下虚拟环境的问题，而且我保证不让你白花时间接触，🥺找实习简历上肯定要写你会用的。）

我默认你已经可以跑通初始版本了，就是登录这种没做你直接叫ai给你写一个本地测试用的账号密码登进去就行。requirements.txt不是所有东西都要下。都下要等一亿年。如果不清楚要安装哪些依赖，就等跑完报错之后抛给ai。

# 以下是3.30 To ljq ：APIkey获取说明
飞书文档也会给你，我写成readme方便你拉下来在ide里问ai。如果你没有GitHub Copilot Pro可以用杭电邮箱开通：[点这个链接](https://zeeklog.com/copilotxue-sheng-ren-zheng-2026-github-copilotxue-sheng-ren-zheng-shou-ba-shou-jiao-hui-8/)
这个我推荐给皓宇哥过😋🥰😃🙂✌🏻🤗
## 一、本地跑通项目的命令行

        # 通义千问密钥（LLM算命用）
        $env:DASHSCOPE_API_KEY=" "
        
        # 开关：启用LLM
        $env:USE_DASHSCOPE="1"
        
        # 腾讯云密钥（生图用）
        $env:TENCENTCLOUD_SECRET_ID=" "
        $env:TENCENTCLOUD_SECRET_KEY=" "
        
        # 地域：我们用广州（默认稳定）
        $env:TENCENTCLOUD_REGION="ap-guangzhou"
        
        # 开关：启用生图
        $env:USE_HUNYUAN_IMAGE="1"
        
## 二、APIkey获取位置（我找的都是有免费额度的OvO）：
### 1.通义千问的在阿里云百炼
https://bailian.console.aliyun.com/cn-beijing?tab=model#/api-key
这个地方，你先注册阿里云的账号，然后在这里创建APIKEY就可以
<img width="1367" height="256" alt="image" src="https://github.com/user-attachments/assets/74627968-9e37-44a1-9ba7-85a1916a92ac" />

LLM只用得到这一个apikey。
### 2.腾讯混元的文生图极速轻量版
API接口文档
【腾讯混元生图 混元生图（极速版）_腾讯云】 https://cloud.tencent.com/document/api/1668/120721?from=copy
<img width="1280" height="450" alt="image" src="https://github.com/user-attachments/assets/3a57f357-be3a-440e-aac0-bed0c7a530eb" />

https://console.cloud.tencent.com/aiart/hunyuan-image-fast-create

这个是试用入口，应该有个地方叫你开通服务的，要先开通服务你才能在这里输入prompt试用，apikey才有效。但是具体哪里我有点忘了，你可以自己问豆包找一下，很好找的。大概就是上图所说内容步骤。

开通之后，https://console.cloud.tencent.com/cam/capi
<img width="1280" height="477" alt="image" src="https://github.com/user-attachments/assets/67097918-5314-48d1-b2c4-658955c98431" />

这里创建秘钥，需要一个ID,一个KEY，填入“一”中的命令行里，创建的时候会给你复制的机会，如果没复制就看不到了，可以删除重建一个。
- 然后要下载腾讯的sdk，可以让ai给你写命令行下载，大概需要二十分钟。API文档里也有github地址。
## 三、跑通项目的最后一步
跑完“一”的命令行之后run server，比如我的是这样：
```shell
d:/tellyourfortune/.venv/Scripts/python.exe manage.py runserver
```
会给你输出一个localhost的地址打开上传照片就可以，报错都会在本地终端输出，你发给ide的ai问一下就好。
（注意跑的时候不要开梯子，因为我们腾讯混元的服务地域用的国内的。）
## 四、你短期内需要修改的
<img width="1280" height="729" alt="image" src="https://github.com/user-attachments/assets/a6a61758-7b5e-491e-899e-0684470142f6" />

1.就是这个下载的png报告格式，要把新增的算命文本放上去，图片也做替换。至于那个奇奇怪怪的二维码如果你想删掉可以问问刘老师。
2.就是这个项目有移动端，辛苦你看看手机上的格式问题。改完之后可以发给刘老师。他最近挺忙的也没空管我们，我觉得慢慢来也可以。反正我们写的ddl不是到清明假之后了嘛。而且他现在肯定还没看过schedule来不及可以改。（）
<img width="1280" height="708" alt="image" src="https://github.com/user-attachments/assets/5e6111b2-0bc7-4794-b16b-a5eb47db8736" />

3.第二页我现在是把提示词用小字体打印出来了，后面做得差不多了把这个显示去掉就好。
还有就是我现在用的这个轻量模型对发型这种提示词是不敏感的，生成的人像一定会雷同，不管换什么用户的照片都会雷同。因为即使提示词变化了模型也没有分辨能力。
我在试用的地方https://console.cloud.tencent.com/aiart/hunyuan-image-three-create
看了一下效果似乎确实是这样的，换成混元的2.0和3.0可能大概也许或许probablymaybe会好一点，但是我好像是免费额度用完的问题有报错，你可以自己试试看。或者对比一下你原来选用的模型哪个稍微好一点让ai帮忙vibecoding换一下。
<img width="1280" height="840" alt="image" src="https://github.com/user-attachments/assets/54d20c33-c5b5-44f4-8bdd-410f9616db3e" />
