# 2026.4.14更新的readme.md
## 一、更新说明
在 [对接说明.md](https://github.com/Nora-0721/TellYourFortunebyus/blob/main/%E5%AF%B9%E6%8E%A5%E8%AF%B4%E6%98%8E.md)
和 [八字排盘功能.md](https://github.com/Nora-0721/TellYourFortunebyus/blob/main/%E5%85%AB%E5%AD%97%E6%8E%92%E7%9B%98%E5%8A%9F%E8%83%BD.md)

其中我有写我这次改了什么功能，以及改动了哪些文件和函数。

（1）我主要是改了上传界面 的UI、年龄段输入改成了具体生辰输入、引入了八字排盘功能和十二星次分析、微调了LLM输出给文生图模型的prompt（因为prompt中关于年龄的描述原来是直接取用户选择的年龄段的，现在改成具体生辰输入了，就做成区分自动计算实岁匹配少年青年中年老年了）
（2）具体改动的文件和函数在 对接说明.md 的 ## 4. 我本次功能改动与文件/函数对应清单这里。


## 二、合并上的问题
1.首先说明现在你那个分支跟整个仓库的main和我的分支不同源，你的分支不是从main上长出来的。这样子git没法追踪，后续也没法合并我和你的改动。我今天细看了一下才发现你的分支有问题，，

2.我下午 git log 查了一下你的操作痕迹，发现你那个分支是有两个提交，提交信息一样，哈希值fc33c8f的没有parent字段————em，你是不是，全新init出来了一个仓库直接推上去了？
我不知道你是搞了一个孤儿分支还是拉我代码到你本地的时候没和远程仓库关联、或者自己新建了一个仓库本地改完代码才在远程仓库搞了一个分支推上去，其实正常顺序应该是：从仓库主干 main 拉代码->
->在 main 基础上切分支开发->分支始终关联同一个远程仓库->周期性把 main 同步到分支再继续开发。

你在本地改代码的时候肯定要关联我那个远程仓库的你的分支的，你可能改的时候没关联任何仓库的分支、或者自己新建了一个仓库去关联自己的、又或者分支没长在main上（新分支的起点是 main 的当前 HEAD，历史线是从 main 上延伸出去的，所以有共同祖先，后续合并才能正常工作。）。

😨🫠🥲😭🥺🥹git没有逐行阅读对比我们两个的文件的能力，它能支持合作开发是基于他的追踪功能，只能基于共同的提交历史来追踪每个人改了什么。

你可以看一下我的这个分支，<img width="1652" height="1066" alt="image" src="https://github.com/user-attachments/assets/90739bca-185d-4143-9590-9451bb4973b3" />
每次在本地切到这个分支再去修改，改完传分支云端，然后pullrequest把分支并到main。这是一个标准化的流程，我们的代码要相互merge的前提是我们的分支一定是从共同的最初版本上长出来的，也就是你第一次拉下我的代码的那个版本（你得拉下来关联我的仓库，不是直接下载压缩包然后关联自己的仓库。或者改完才关联。这些常见的Git教程都会说明的，或者自己问一下ai也能懂，我之前没特别提醒你是我以为这种问题应该不会有）
    如果不太会命令行，解决问题很好的办法就是用github desktop的图形化操作界面查看你在哪个仓库哪个分支。其实不管你用什么方法网上都有教程，都是很基础的所以我不给你写教程了。
    <img width="997" height="463" alt="image" src="https://github.com/user-attachments/assets/2026f54c-6914-4edd-a6a3-ad4b68b94bb6" />

     

3.然后关于你这个孤儿分支怎么办，这种情况我也没遇到过，我去问了一下cc，
<img width="928" height="944" alt="image" src="https://github.com/user-attachments/assets/cfc5d054-62be-47fe-a064-14d61a0ba092" />
<img width="928" height="549" alt="image" src="https://github.com/user-attachments/assets/6043047f-be75-4a8d-86a2-d08319f3f437" />

我倒是觉得你如果舍得的话（因为之前只改了模型选型、报告格式、手机端格式适配，这些现在全部都要再改的）直接重新拉最新的代码到本地新的位置，（不要和原来的放在一个路径，你拉到新的位置把原项目文件夹的venv等配置文件移动过去就行了，因为老路径位置的文件只要上传过就会被git追踪的。）确认和云端关联没问题，在main上新建分支开发，切到正确的分支，自己改完之后上传云端，然后再合并merge到main。当攒经验买教训了，以后不会出一样的错了就是赚的。

NewBranch在这里也可以。不管是分支管理，拉代码和上传云端代码，还是合并到主分支，甚至是修改文件，这些操作你用命令行、用github desktop图形化操作、直接在github网页端改其实都可以。多变通。
<img width="2302" height="397" alt="image" src="https://github.com/user-attachments/assets/660587f9-9e62-4b3d-9d6d-7742d830d76a" />









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

