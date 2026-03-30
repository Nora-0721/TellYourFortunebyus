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
    im = im.resize((400, 400));
    bigsize = (im.size[0] * 3, im.size[1] * 3)
    #遮罩对象
    mask = Image.new('L', bigsize, 0)
    draw = ImageDraw.Draw(mask) 
        #画椭圆的方法
    draw.ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(im.size, Image.ANTIALIAS)
    im.putalpha(mask)
    background.paste(im, (150*4, 700), im)
    return background


def _resolve_path(path: str) -> str:
    """将传入的相对 URL 风格路径转换为本地绝对文件路径。

    示例: "./media/image/%E8%AF%81%E4%BB%B6.jpg" ->
          E:/Web/tellyourfortune/media/image/证件照.jpg
    """
    # 去掉前导 ./ 或 /
    rel = path.lstrip('./').lstrip('\\')
    # 反 URL 编码，得到真正的文件名
    rel = urllib.parse.unquote(rel)
    # 组合为绝对路径
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, rel.replace('/', os.sep))

def test_image_height(avatarUrl,qrcodeUrl,title_lucky_color,astr_lucky_color,title_lucky_location,astr_lucky_location,title_doing,astr_doing,title_astr_eye,astr_eye,title_astr_nose,astr_nose,title_astr_mouth,astr_mouth,title_all,astr_all,title_couple,astr_couple):
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
    avatar = Image.open(_resolve_path(avatarUrl), "r")
    qrcode_img = Image.open(_resolve_path(qrcodeUrl), "r")
    
    #加载头像图片
    #logo_img = Image.open(logoUrl,"r")
    
    #edge_img = Image.open(edgeUrl, 'r')

    # 将背景图片和圆形头像合成之后当成新的背景图片
    back_img=drawCircleAvatar(avatar,im)
    
    draw = ImageDraw.Draw(back_img)
    font = ImageFont.truetype('./simhei.ttf', 20*4) 
    w, h = draw.textsize("面相报告", font=font)
    draw.text(((MAX_W - w)/2, 520), "面相报告", font=font,fill=(0, 0, 0))

    #将二维码图片粘贴在背景图片上
    region = qrcode_img
    region = region.resize((100, 100))
    back_img.paste(region,(10,573))
    
    
    pad = 10*4
    font = ImageFont.truetype('./simhei.ttf', 12*4) 
    back_img, cureent_h = insert_word_recommand(title_lucky_color,astr_lucky_color, width, back_img, font, cureent_h, pad)
    back_img, cureent_h = insert_word_recommand(title_lucky_location,astr_lucky_location, width, back_img, font, cureent_h, pad)
    back_img, cureent_h = insert_word_recommand(title_doing,astr_doing, width, back_img, font, cureent_h, pad)
    cureent_h += 20*4
    back_img, cureent_h = insert_word(title_astr_eye,astr_eye, width, back_img, font, cureent_h, pad)
    cureent_h += 10*4
    back_img, cureent_h = insert_word(title_astr_nose,astr_nose, width, back_img, font, cureent_h, pad)
    cureent_h += 10*4
    back_img, cureent_h = insert_word(title_astr_mouth,astr_mouth, width, back_img, font, cureent_h, pad)
    cureent_h += 10*4
    back_img, cureent_h = insert_word(title_all,astr_all, width, back_img, font, cureent_h, pad)
    cureent_h += 10*4
    back_img, cureent_h = insert_word_recommand(title_couple,astr_couple, width, back_img, ImageFont.truetype('./simhei.ttf', 15*4) , cureent_h, pad)

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
    w, h = draw.textsize(title_astr+astr, font=font)
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
    font1 = ImageFont.truetype('./simhei.ttf', 15*4) 
    draw = ImageDraw.Draw(image)
    w, h = draw.textsize(title_astr, font=font1)
    draw.text((30*4, current_h), title_astr, font=font1,fill=(0, 0, 0))
    current_h += h + pad  
    para = textwrap.wrap(astr, width)
    for line in para: 
        w, h = draw.textsize(line, font=font) 
        draw.text((50*4, current_h), line, font=font,fill=(0, 0, 0)) 
        current_h += h + pad 
        
    return image, current_h # 返回图片和当前高度

def generate_report(backgroundUrl,avatarUrl,qrcodeUrl,couple_1_Url,couple_2_Url,astr_lucky_color,
                   astr_lucky_location,astr_doing,astr_eye,astr_nose,astr_mouth,astr_all,
                   match_rate_1,match_rate_2,x,y):
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
    
    title_couple = "您的对象像谁？"
    astr_couple =""
    
  #  match_rate_1 = "80%"
  #  match_rate_2 = "80%"
    
    max_height = test_image_height(avatarUrl,qrcodeUrl,title_lucky_color,astr_lucky_color,title_lucky_location,
	astr_lucky_location,title_doing,astr_doing,title_astr_eye,astr_eye,title_astr_nose,astr_nose,title_astr_mouth,astr_mouth,title_all,astr_all,title_couple,astr_couple)
    
    MAX_H = max_height+1800
    #加载背景图片
    background=Image.open(_resolve_path(backgroundUrl),'r')
    background = background.resize((MAX_W,MAX_H))
    #加载二维码图片
    avatar = Image.open(_resolve_path(avatarUrl),"r")
    w_avatar,h_avatar = avatar.size
    min_location = np.min([w_avatar-x,h_avatar-y,x,y])
    cropped = avatar.crop((x-min_location,y-min_location,x+min_location,y+min_location))
    
    
    qrcode_img = Image.open(_resolve_path(qrcodeUrl),"r")
    
    #加载头像图片
    #logo_img = Image.open(logoUrl,"r")
    
    #edge_img = Image.open(edgeUrl, 'r')

    # 将背景图片和圆形头像合成之后当成新的背景图片
    back_img=drawCircleAvatar(cropped,background)
    
    draw = ImageDraw.Draw(back_img)
    font = ImageFont.truetype('./simhei.ttf', 20*4) 
    w, h = draw.textsize("人工智能大数据命理分析报告", font=font)
    draw.text(((MAX_W - w)/2, 520), "人工智能大数据命理分析报告", font=font,fill=(0, 0, 0))

    #将二维码图片粘贴在背景图片上
    region = qrcode_img
    region = region.resize((100*4, 100*4))
    back_img.paste(region,(150*4,MAX_H-180*4))  # 130
    
    # 将logo粘贴到背景图片上
   # region = logo_img
   # region = region.resize((100, 100))
   # back_img.paste(region,(150,MAX_H-100))
     
    pad = 10*4
    font = ImageFont.truetype('./simhei.ttf', 12*4) 
    back_img, cureent_h = insert_word_recommand(title_lucky_color,astr_lucky_color, width, back_img, font, cureent_h, pad)
    back_img, cureent_h = insert_word_recommand(title_lucky_location,astr_lucky_location, width, back_img, font, cureent_h, pad)
    back_img, cureent_h = insert_word_recommand(title_doing,astr_doing, width, back_img, font, cureent_h, pad)
    cureent_h += 20*4
    back_img, cureent_h = insert_word(title_astr_eye,astr_eye, width, back_img, font, cureent_h, pad)
    cureent_h += 10*4
    back_img, cureent_h = insert_word(title_astr_nose,astr_nose, width, back_img, font, cureent_h, pad)
    cureent_h += 10*4
    back_img, cureent_h = insert_word(title_astr_mouth,astr_mouth, width, back_img, font, cureent_h, pad)
    cureent_h += 10*4
    back_img, cureent_h = insert_word(title_all,astr_all, width, back_img, font, cureent_h, pad)
    cureent_h += 10*4
    back_img, cureent_h = insert_word_recommand(title_couple,astr_couple, width, back_img, ImageFont.truetype('./simhei.ttf', 15*4) , cureent_h, pad)
    
    couple_1 = Image.open(_resolve_path(couple_1_Url),'r')
    couple_1 = couple_1.resize((400,400))
    back_img.paste(couple_1,(80*4,cureent_h+20))
    
    couple_2 = Image.open(_resolve_path(couple_2_Url),'r')
    couple_2 = couple_2.resize((400,400))
    back_img.paste(couple_2,(220*4,cureent_h+20))
    
    match_rate_1 = "吻合度：" +match_rate_1
    match_rate_2 = "吻合度：" +match_rate_2
    draw.text((100*4, cureent_h+80+400), match_rate_1, font=font,fill=(0, 0, 0))
    draw.text((240*4, cureent_h+80+400), match_rate_2, font=font,fill=(0, 0, 0))
    
    back_img.save('out.png') #保存图片
    


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

