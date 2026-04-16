#!/usr/bin/env python
# coding: utf-8

# In[76]:


#!/usr/bin/env python
# coding: utf-8

# In[245]:


# -*- coding: utf-8 -*-
from PIL import Image,ImageFont,ImageDraw
import time,sys
import textwrap
import os
import urllib.parse
import numpy as np
#reload(sys)
#sys.setdefaultencoding('utf-8')


"""将头像变成圆形绘制在背景图片上，然后将合成的图片对象返回"""
def drawCircleAvatar(im,background):
    # 确保图片有Alpha通道
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    
    # 调整头像大小
    im = im.resize((400, 400))
    
    # 创建遮罩
    bigsize = (im.size[0] * 3, im.size[1] * 3)
    mask = Image.new('L', bigsize, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(im.size, Image.Resampling.LANCZOS)
    
    # 应用遮罩
    im.putalpha(mask)
    
    # 粘贴到背景（使用头像自身作为遮罩）
    background.paste(im, (150*4, 700), im)
    print(f"[drawCircleAvatar] 圆形头像已粘贴到背景 (600, 700)")
    return background


def _resolve_path(path: str) -> str:
    """将传入的相对 URL 风格路径转换为本地绝对文件路径。

    示例: "./media/image/%E8%AF%81%E4%BB%B6.jpg" ->
          E:/Web/tellyourfortune/media/image/证件照.jpg

    如果是外部URL（http/https开头），则下载到临时目录并返回本地路径。
    """
    # 如果是URL，先下载到本地临时目录
    if path.startswith('http://') or path.startswith('https://'):
        import uuid
        import tempfile
        from urllib.request import urlretrieve

        url = path
        # 创建临时目录（如果不存在）
        temp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'media', 'temp')
        os.makedirs(temp_dir, exist_ok=True)

        # 生成唯一文件名
        ext = '.png'
        filename = os.path.join(temp_dir, f"temp_couple_{uuid.uuid4().hex}{ext}")

        print(f"[_resolve_path] 下载URL图片: {url[:80]}... -> {filename}")
        try:
            urlretrieve(url, filename)
            return filename
        except Exception as e:
            print(f"[_resolve_path] 下载URL图片失败: {e}")
            # 下载失败时返回原URL（虽然会出错，但不影响主流程）
            return path

    # 去掉前导 ./ 或 /
    rel = path.lstrip('./').lstrip('\\')
    # 反 URL 编码，得到真正的文件名
    rel = urllib.parse.unquote(rel)
    # 组合为绝对路径
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, rel.replace('/', os.sep))

def _get_font_path(font_name: str) -> str:
    """获取字体文件的绝对路径。"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, font_name)

def test_image_height(avatarUrl,qrcodeUrl,title_lucky_color,astr_lucky_color,title_lucky_location,astr_lucky_location,title_doing,astr_doing,title_astr_eye,astr_eye,title_astr_nose,astr_nose,title_astr_mouth,astr_mouth,title_all,astr_all,title_true_love,astr_true_love,title_couple,astr_couple):
    import datetime
    log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'generate_report.log')
    with open(log_file, 'a', encoding='utf-8') as lf:
        lf.write(f"[LOG] test_image_height called\n")
    
    MAX_W, MAX_H = 393, 2000 
    im = Image.new('RGB', (MAX_W, MAX_H), (255, 255, 255, 255)) 
    #backgroundUrl = "./our_background.png"

    #logoUrl = "./logo.png"
    width=25
    MAX_W = 393*4  # 背景图片宽度
    MAX_H = 673  # 背景图片长度
    
    cureent_h = 1100
    
    #加载背景图片
    #background=Image.open(backgroundUrl,'r')
    
    # 加载头像、二维码图片（统一将相对 URL 转为绝对文件路径）
    try:
        with open(log_file, 'a', encoding='utf-8') as lf:
            lf.write(f"[LOG] test_image_height: loading avatar\n")
        avatar_path = _resolve_path(avatarUrl)
        if not os.path.exists(avatar_path):
            # 降级：使用原始图片
            fallback_url = avatarUrl.replace('_400', '')
            avatar_path = _resolve_path(fallback_url)
        avatar = Image.open(avatar_path, "r")
        # 转换为RGBA模式
        if avatar.mode != 'RGBA':
            avatar = avatar.convert('RGBA')
        with open(log_file, 'a', encoding='utf-8') as lf:
            lf.write(f"[LOG] test_image_height: avatar loaded\n")
    except Exception as e:
        print(f"[test_image_height] 头像加载失败: {e}，使用占位图")
        with open(log_file, 'a', encoding='utf-8') as lf:
            lf.write(f"[LOG] test_image_height: avatar load failed, using placeholder\n")
        avatar = Image.new('RGBA', (400, 400), (255, 255, 255, 255))
    
    with open(log_file, 'a', encoding='utf-8') as lf:
        lf.write(f"[LOG] test_image_height: loading qrcode\n")
    qrcode_img = Image.open(_resolve_path(qrcodeUrl), "r")
    with open(log_file, 'a', encoding='utf-8') as lf:
        lf.write(f"[LOG] test_image_height: qrcode loaded\n")
    
    #加载头像图片
    #logo_img = Image.open(logoUrl,"r")
    
    #edge_img = Image.open(edgeUrl, 'r')

    # 将背景图片和圆形头像合成之后当成新的背景图片
    with open(log_file, 'a', encoding='utf-8') as lf:
        lf.write(f"[LOG] test_image_height: calling drawCircleAvatar\n")
    back_img=drawCircleAvatar(avatar,im)
    with open(log_file, 'a', encoding='utf-8') as lf:
        lf.write(f"[LOG] test_image_height: drawCircleAvatar done\n")
    
    with open(log_file, 'a', encoding='utf-8') as lf:
        lf.write(f"[LOG] test_image_height: drawing title\n")
    draw = ImageDraw.Draw(back_img)
    font_path = _get_font_path('simhei.ttf')
    font = ImageFont.truetype(font_path, 20*4) 
    bbox = draw.textbbox((0, 0), "面相报告", font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text(((MAX_W - w)/2, 520), "面相报告", font=font,fill=(0, 0, 0))
    with open(log_file, 'a', encoding='utf-8') as lf:
        lf.write(f"[LOG] test_image_height: title drawn\n")

    #将二维码图片粘贴在背景图片上
    with open(log_file, 'a', encoding='utf-8') as lf:
        lf.write(f"[LOG] test_image_height: pasting qrcode\n")
    region = qrcode_img
    region = region.resize((100, 100))
    back_img.paste(region,(10,573))
    with open(log_file, 'a', encoding='utf-8') as lf:
        lf.write(f"[LOG] test_image_height: qrcode pasted\n")
    
    
    pad = 10*4
    with open(log_file, 'a', encoding='utf-8') as lf:
        lf.write(f"[LOG] test_image_height: drawing text fields\n")
    font_path = _get_font_path('simhei.ttf')
    font = ImageFont.truetype(font_path, 12*4) 
    back_img, cureent_h = insert_word_recommand(title_lucky_color,astr_lucky_color, width, back_img, font, cureent_h, pad)
    with open(log_file, 'a', encoding='utf-8') as lf:
        lf.write(f"[LOG] test_image_height: lucky_color done\n")
    back_img, cureent_h = insert_word_recommand(title_lucky_location,astr_lucky_location, width, back_img, font, cureent_h, pad)
    with open(log_file, 'a', encoding='utf-8') as lf:
        lf.write(f"[LOG] test_image_height: lucky_location done\n")
    back_img, cureent_h = insert_word_recommand(title_doing,astr_doing, width, back_img, font, cureent_h, pad)
    with open(log_file, 'a', encoding='utf-8') as lf:
        lf.write(f"[LOG] test_image_height: job done\n")
    cureent_h += 20*4
    back_img, cureent_h = insert_word(title_astr_eye,astr_eye, width, back_img, font, cureent_h, pad)
    with open(log_file, 'a', encoding='utf-8') as lf:
        lf.write(f"[LOG] test_image_height: eye done\n")
    cureent_h += 10*4
    back_img, cureent_h = insert_word(title_astr_nose,astr_nose, width, back_img, font, cureent_h, pad)
    with open(log_file, 'a', encoding='utf-8') as lf:
        lf.write(f"[LOG] test_image_height: nose done\n")
    cureent_h += 10*4
    back_img, cureent_h = insert_word(title_astr_mouth,astr_mouth, width, back_img, font, cureent_h, pad)
    with open(log_file, 'a', encoding='utf-8') as lf:
        lf.write(f"[LOG] test_image_height: mouth done\n")
    cureent_h += 10*4
    back_img, cureent_h = insert_word(title_all,astr_all, width, back_img, font, cureent_h, pad)
    with open(log_file, 'a', encoding='utf-8') as lf:
        lf.write(f"[LOG] test_image_height: all done\n")
    cureent_h += 10*4
    back_img, cureent_h = insert_word(title_true_love, astr_true_love, width, back_img, font, cureent_h, pad)
    with open(log_file, 'a', encoding='utf-8') as lf:
        lf.write(f"[LOG] test_image_height: true_love done\n")
    cureent_h += 10*4
    with open(log_file, 'a', encoding='utf-8') as lf:
        lf.write(f"[LOG] test_image_height: drawing couple\n")
    font_path_couple = _get_font_path('simhei.ttf')
    back_img, cureent_h = insert_word_recommand(title_couple,astr_couple, width, back_img, ImageFont.truetype(font_path_couple, 15*4) , cureent_h, pad)
    with open(log_file, 'a', encoding='utf-8') as lf:
        lf.write(f"[LOG] test_image_height: couple done, returning\n")

    return cureent_h

# 插入文字
def insert_word_recommand(title_astr, astr, width, image, font, current_h, pad):
    # asrr -- 字符串
    # width -- 文字一行的宽度
    # image -- 背景图片
    # font -- 字体
    # current_h -- 当前高度
    # pad -- 与以前文字的间隔
    draw = ImageDraw.Draw(image)
    bbox = draw.textbbox((0, 0), title_astr+astr, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text((30*4, current_h), title_astr+astr, font=font,fill=(0, 0, 0))
    current_h += h + pad  
        
    return image, current_h # 返回图片和当前高度

# 插入文字
def insert_word(title_astr, astr, width, image, font, current_h, pad):
    # asrr -- 字符串
    # width -- 文字一行的宽度
    # image -- 背景图片
    # font -- 字体
    # current_h -- 当前高度
    # pad -- 与以前文字的间隔
    font1_path = _get_font_path('simhei.ttf')
    font1 = ImageFont.truetype(font1_path, 15*4) 
    draw = ImageDraw.Draw(image)
    bbox = draw.textbbox((0, 0), title_astr, font=font1)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text((30*4, current_h), title_astr, font=font1,fill=(0, 0, 0))
    current_h += h + pad  
    para = textwrap.wrap(astr, width)
    for line in para: 
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        draw.text((50*4, current_h), line, font=font,fill=(0, 0, 0)) 
        current_h += h + pad 
        
    return image, current_h # 返回图片和当前高度

def generate_report(backgroundUrl,avatarUrl,qrcodeUrl,couple_1_Url,couple_2_Url,astr_lucky_color,
                   astr_lucky_location,astr_doing,astr_eye,astr_nose,astr_mouth,astr_all,astr_true_love,
                   astr_couple,match_rate_1,match_rate_2,x,y):
    # 添加日志文件记录执行过程
    import datetime
    log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'generate_report.log')
    with open(log_file, 'a', encoding='utf-8') as lf:
        lf.write(f"\n{'='*60}\n")
        lf.write(f"[{datetime.datetime.now()}] generate_report called\n")
        lf.write(f"  avatarUrl: {avatarUrl}\n")
        lf.write(f"  x={x}, y={y}\n")
    
   # backgroundUrl = "./our_background.png"
   # avatarUrl="./renlian.jpg"
   # qrcodeUrl="./qrcode.png"
   # couple_1_Url = "16.jpg"
   # couple_2_Url = "17.jpg"
    # x, y 人脸的中心坐标
    width=25
    MAX_W = 393*4  # 背景图片宽度
    MAX_H = 673  # 背景图片长度
    
    cureent_h = 1100
    
    title_lucky_color = "幸运颜色："
    #astr_lucky_color = "青"
    
    title_lucky_location = "幸运方位："
    #astr_lucky_location = "东南"
    
    title_doing = "推荐的职业："
   # astr_doing = "企业家 会计师 教师"
    
    title_astr_eye = "根据眼睛的结果："
    #astr_eye = '''不喜与人计较得失错对,为人心地善良，乐于助人。但是，对生活没有太大志向，知足常乐。心思敏感，容易发现生活中的一些细节。遇到事情喜欢先规划如何再去实行，凡事比较较真，都会去认真完成。'''
    
    title_astr_nose = "根据鼻子的结果："
   # astr_nose = "家境比较不错，为人不但聪明，而且性格乐观、开朗。不管面对什么都会有着积极向上的态度，在生活或是职场中的能较好的表现自己的人格魅力，充分展现出自己的优点，有着一定成就，前途一片光明，能够获得丰厚的财富。"
    
    title_astr_mouth = "根据嘴唇的结果："
   # astr_mouth = "金运可达，福禄有余，遵守道德，受人敬爱，贵人提拔，命运通达，大有成功，获得幸福，福禄双收，女命富贵，金运之命。"
    
    title_all = "综合评价："
   # astr_all = "本人有着比较强的创新能力和逻辑推理能力，能够很快的结合自身所有解决遇到的问题。对新的事物会比较好奇。是一位有创造力的思考者，也善于分析解决问题。大多数时候，为人比较机灵，但是，有时候会比较懒散，保守。"
    
    title_true_love = "☆正缘预测："
    # astr_true_love 从参数传入
    
    title_couple = "您的对象像谁？"
    
  #  match_rate_1 = "80%"
  #  match_rate_2 = "80%"
    
    with open(log_file, 'a', encoding='utf-8') as lf:
        lf.write(f"[LOG] Step 1: before test_image_height\n")
    try:
        max_height = test_image_height(avatarUrl,qrcodeUrl,title_lucky_color,astr_lucky_color,title_lucky_location,
	    astr_lucky_location,title_doing,astr_doing,title_astr_eye,astr_eye,title_astr_nose,astr_nose,title_astr_mouth,astr_mouth,title_all,astr_all,title_true_love,astr_true_love,title_couple,astr_couple)
        with open(log_file, 'a', encoding='utf-8') as lf:
            lf.write(f"[LOG] Step 2: after test_image_height, max_height={max_height}\n")
    except Exception as e:
        with open(log_file, 'a', encoding='utf-8') as lf:
            lf.write(f"[LOG] ERROR in test_image_height: {e}\n")
        raise
    
    MAX_H = max_height+1800
    with open(log_file, 'a', encoding='utf-8') as lf:
        lf.write(f"[LOG] Step 3: loading background image\n")
    try:
        #加载背景图片
        with open(log_file, 'a', encoding='utf-8') as lf:
            lf.write(f"[LOG] Step 3.1: opening background\n")
        background=Image.open(_resolve_path(backgroundUrl),'r')
        with open(log_file, 'a', encoding='utf-8') as lf:
            lf.write(f"[LOG] Step 3.2: resizing background to {MAX_W}x{MAX_H}\n")
        background = background.resize((MAX_W,MAX_H))
        with open(log_file, 'a', encoding='utf-8') as lf:
            lf.write(f"[LOG] Step 3.3: background loaded and resized\n")
    except Exception as e:
        with open(log_file, 'a', encoding='utf-8') as lf:
            lf.write(f"[LOG] ERROR loading background: {e}\n")
        raise
    
    # 加载头像图片 - 添加完善的异常处理
    try:
        with open(log_file, 'a', encoding='utf-8') as lf:
            lf.write(f"[LOG] Step 4: processing avatar\n")
        avatar_path = _resolve_path(avatarUrl)
        print(f"[generate_report] 尝试加载头像: {avatarUrl} -> {avatar_path}")
        if not os.path.exists(avatar_path):
            print(f"[generate_report] 警告: 头像文件不存在: {avatar_path}")
            # 降级：使用原始图片（去掉_400后缀）
            fallback_url = avatarUrl.replace('_400', '')
            avatar_path = _resolve_path(fallback_url)
            print(f"[generate_report] 尝试使用原始图片: {fallback_url} -> {avatar_path}")
        
        with open(log_file, 'a', encoding='utf-8') as lf:
            lf.write(f"[LOG] Step 4.1: opening avatar\n")
        avatar = Image.open(avatar_path, "r")
        w_avatar, h_avatar = avatar.size
        print(f"[generate_report] 头像尺寸: {w_avatar}x{h_avatar}, 中心点: ({x},{y})")
        
        # 根据面部中心坐标裁剪正方形区域
        with open(log_file, 'a', encoding='utf-8') as lf:
            lf.write(f"[LOG] Step 4.2: cropping avatar\n")
        min_location = int(np.min([w_avatar-x, h_avatar-y, x, y]))
        if min_location <= 0:
            print(f"[generate_report] 警告: min_location={min_location}，使用整个图片")
            cropped = avatar
        else:
            cropped = avatar.crop((x-min_location, y-min_location, x+min_location, y+min_location))
            print(f"[generate_report] 裁剪区域: ({x-min_location},{y-min_location}) -> ({x+min_location},{y+min_location})")
        with open(log_file, 'a', encoding='utf-8') as lf:
            lf.write(f"[LOG] Step 4.3: avatar cropped successfully\n")
    except Exception as e:
        print(f"[generate_report] 头像处理失败: {e}")
        with open(log_file, 'a', encoding='utf-8') as lf:
            lf.write(f"[LOG] ERROR in avatar processing: {e}\n")
        import traceback
        traceback.print_exc()
        # 降级：创建白色占位图
        cropped = Image.new('RGBA', (400, 400), (255, 255, 255, 255))
        print("[generate_report] 使用白色占位图")
    
    #加载二维码图片
    with open(log_file, 'a', encoding='utf-8') as lf:
        lf.write(f"[LOG] Step 5: loading qrcode\n")
    qrcode_img = Image.open(_resolve_path(qrcodeUrl),"r")
    with open(log_file, 'a', encoding='utf-8') as lf:
        lf.write(f"[LOG] Step 5.1: qrcode loaded\n")
    
    #加载头像图片
    #logo_img = Image.open(logoUrl,"r")
    
    #edge_img = Image.open(edgeUrl, 'r')

    # 将背景图片和圆形头像合成之后当成新的背景图片
    with open(log_file, 'a', encoding='utf-8') as lf:
        lf.write(f"[LOG] Step 6: calling drawCircleAvatar\n")
    back_img=drawCircleAvatar(cropped,background)
    with open(log_file, 'a', encoding='utf-8') as lf:
        lf.write(f"[LOG] Step 6.1: drawCircleAvatar done\n")
    
    draw = ImageDraw.Draw(back_img)
    with open(log_file, 'a', encoding='utf-8') as lf:
        lf.write(f"[LOG] Step 7: loading font and drawing title\n")
    font_path = _get_font_path('simhei.ttf')
    font = ImageFont.truetype(font_path, 20*4) 
    bbox = draw.textbbox((0, 0), "人工智能大数据命理分析报告", font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text(((MAX_W - w)/2, 520), "人工智能大数据命理分析报告", font=font,fill=(0, 0, 0))
    with open(log_file, 'a', encoding='utf-8') as lf:
        lf.write(f"[LOG] Step 7.1: title drawn\n")

    #将二维码图片粘贴在背景图片上
    with open(log_file, 'a', encoding='utf-8') as lf:
        lf.write(f"[LOG] Step 8: pasting qrcode\n")
    region = qrcode_img
    region = region.resize((100*4, 100*4))
    back_img.paste(region,(150*4,MAX_H-180*4))  # 130
    with open(log_file, 'a', encoding='utf-8') as lf:
        lf.write(f"[LOG] Step 8.1: qrcode pasted\n")
    
    # 将logo粘贴到背景图片上
   # region = logo_img
   # region = region.resize((100, 100))
   # back_img.paste(region,(150,MAX_H-100))
     
    pad = 10*4
    with open(log_file, 'a', encoding='utf-8') as lf:
        lf.write(f"[LOG] Step 9: drawing text fields\n")
    font_path = _get_font_path('simhei.ttf')
    font = ImageFont.truetype(font_path, 12*4) 
    back_img, cureent_h = insert_word_recommand(title_lucky_color,astr_lucky_color, width, back_img, font, cureent_h, pad)
    with open(log_file, 'a', encoding='utf-8') as lf:
        lf.write(f"[LOG] Step 9.1: lucky_color drawn\n")
    back_img, cureent_h = insert_word_recommand(title_lucky_location,astr_lucky_location, width, back_img, font, cureent_h, pad)
    with open(log_file, 'a', encoding='utf-8') as lf:
        lf.write(f"[LOG] Step 9.2: lucky_location drawn\n")
    back_img, cureent_h = insert_word_recommand(title_doing,astr_doing, width, back_img, font, cureent_h, pad)
    with open(log_file, 'a', encoding='utf-8') as lf:
        lf.write(f"[LOG] Step 9.3: job drawn\n")
    cureent_h += 20*4
    back_img, cureent_h = insert_word(title_astr_eye,astr_eye, width, back_img, font, cureent_h, pad)
    with open(log_file, 'a', encoding='utf-8') as lf:
        lf.write(f"[LOG] Step 9.4: eye drawn\n")
    cureent_h += 10*4
    back_img, cureent_h = insert_word(title_astr_nose,astr_nose, width, back_img, font, cureent_h, pad)
    with open(log_file, 'a', encoding='utf-8') as lf:
        lf.write(f"[LOG] Step 9.5: nose drawn\n")
    cureent_h += 10*4
    back_img, cureent_h = insert_word(title_astr_mouth,astr_mouth, width, back_img, font, cureent_h, pad)
    with open(log_file, 'a', encoding='utf-8') as lf:
        lf.write(f"[LOG] Step 9.6: mouth drawn\n")
    cureent_h += 10*4
    back_img, cureent_h = insert_word(title_all,astr_all, width, back_img, font, cureent_h, pad)
    with open(log_file, 'a', encoding='utf-8') as lf:
        lf.write(f"[LOG] Step 9.7: all drawn\n")
    cureent_h += 10*4
    back_img, cureent_h = insert_word(title_true_love, astr_true_love, width, back_img, font, cureent_h, pad)
    with open(log_file, 'a', encoding='utf-8') as lf:
        lf.write(f"[LOG] Step 9.7b: true_love drawn\n")
    cureent_h += 10*4
    with open(log_file, 'a', encoding='utf-8') as lf:
        lf.write(f"[LOG] Step 9.8: drawing couple\n")
    font_path_couple = _get_font_path('simhei.ttf')
    back_img, cureent_h = insert_word_recommand(title_couple,astr_couple, width, back_img, ImageFont.truetype(font_path_couple, 15*4) , cureent_h, pad)
    with open(log_file, 'a', encoding='utf-8') as lf:
        lf.write(f"[LOG] Step 9.9: couple drawn\n")
    
    with open(log_file, 'a', encoding='utf-8') as lf:
        lf.write(f"[LOG] Step 10: loading couple images\n")
    couple_1 = Image.open(_resolve_path(couple_1_Url),'r')
    couple_1 = couple_1.resize((400,400))
    back_img.paste(couple_1,(80*4,cureent_h+20))
    with open(log_file, 'a', encoding='utf-8') as lf:
        lf.write(f"[LOG] Step 10.1: couple_1 pasted\n")
    
    couple_2 = Image.open(_resolve_path(couple_2_Url),'r')
    couple_2 = couple_2.resize((400,400))
    back_img.paste(couple_2,(220*4,cureent_h+20))
    with open(log_file, 'a', encoding='utf-8') as lf:
        lf.write(f"[LOG] Step 10.2: couple_2 pasted\n")
    
    match_rate_1 = "吻合度：" +match_rate_1
    match_rate_2 = "吻合度：" +match_rate_2
    with open(log_file, 'a', encoding='utf-8') as lf:
        lf.write(f"[LOG] Step 11: drawing match rates\n")
    draw.text((100*4, cureent_h+80+400), match_rate_1, font=font,fill=(0, 0, 0))
    draw.text((240*4, cureent_h+80+400), match_rate_2, font=font,fill=(0, 0, 0))
    with open(log_file, 'a', encoding='utf-8') as lf:
        lf.write(f"[LOG] Step 11.1: match rates drawn\n")
    
    with open(log_file, 'a', encoding='utf-8') as lf:
        lf.write(f"[LOG] Step 12: saving out.png\n")
    back_img.save('out.png') #保存图片
    
    # 记录保存成功
    with open(log_file, 'a', encoding='utf-8') as lf:
        lf.write(f"[{datetime.datetime.now()}] out.png saved successfully\n")
        lf.write(f"  File size: {os.path.getsize('out.png')} bytes\n")
    


# In[77]:
#
#
# backgroundUrl = "./our_background.png"
# avatarUrl="./test2.jpg"
# qrcodeUrl="./qrcode.png"
# couple_1_Url = "16.jpg"
# couple_2_Url = "17.jpg"
# width=25
# MAX_W = 393*4  # 背景图片宽度
# MAX_H = 673  # 背景图片长度
#
# cureent_h = 250
#
# title_lucky_color = "幸运颜色："
# astr_lucky_color = "青"
#
# title_lucky_location = "幸运方位："
# astr_lucky_location = "东南"
#
# title_doing = "推荐的职业："
# astr_doing = "企业家 会计师 教师"
#
# title_astr_eye = "根据眼睛的结果："
# astr_eye = '''不喜与人计较得失错对,为人心地善良，乐于助人。但是，对生活没有太大志向，知足常乐。心思敏感，容易发现生活中的一些细节。遇到事情喜欢先规划如何再去实行，凡事比较较真，都会去认真完成。'''
#
# title_astr_nose = "根据鼻子的结果："
# astr_nose = "家境比较不错，为人不但聪明，而且性格乐观、开朗。不管面对什么都会有着积极向上的态度，在生活或是职场中的能较好的表现自己的人格魅力，充分展现出自己的优点，有着一定成就，前途一片光明，能够获得丰厚的财富。"
#
# title_astr_mouth = "根据嘴唇的结果："
# astr_mouth = "金运可达，福禄有余，遵守道德，受人敬爱，贵人提拔，命运通达，大有成功，获得幸福，福禄双收，女命富贵，金运之命。"
#
# title_all = "综合评价："
# astr_all = "本人有着比较强的创新能力和逻辑推理能力，能够很快的结合自身所有解决遇到的问题。对新的事物会比较好奇。是一位有创造力的思考者，也善于分析解决问题。大多数时候，为人比较机灵，但是，有时候会比较懒散，保守。"
#
# title_couple = "您的对象像谁？"
# astr_couple =""
#
# match_rate_1 = "80%"
# match_rate_2 = "80%"
#
# generate_report(backgroundUrl,avatarUrl,qrcodeUrl,couple_1_Url,couple_2_Url,astr_lucky_color,
#                    astr_lucky_location,astr_doing,astr_eye,astr_nose,astr_mouth,astr_all,
#                    match_rate_1,match_rate_2)
#
#
# # In[58]:
#
#
# avatarUrl="./renlian.jpg"
# im = Image.open(avatarUrl,'r')
#
# w,h = im.size
#
#
# # In[59]:
#
#
# w
#
#
# # In[60]:
#
#
# h
#
#
# # In[71]:
#
#
# x = 138
# y = 101
#
#
# # In[72]:
#
#
# w-x
#
#
# # In[73]:
#
#
# h-y
#
#
# # In[74]:
#
#
# cropped = im.crop((x-y, y-y, x+y, y+y))
#
#
# # In[75]:
#
#
# cropped.save('save.png')
#
#
# # In[78]:
#
#
# import numpy as np
#
#
# # In[ ]:
#
#
#

