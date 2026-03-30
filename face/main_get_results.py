# coding: utf-8
from PIL import Image,ImageFont,ImageDraw
import time,sys
import textwrap
import numpy as np
from face_test import cal_rate,cal_pipei
from generate_report import generate_report

"""
将头像变成圆形绘制在背景图片上，然后将合成的图片对象返回
"""
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
    
    #加载二维码图片
    avatar = Image.open(avatarUrl,"r")
    qrcode_img = Image.open(qrcodeUrl,"r")
    
    #加载头像图片
    #logo_img = Image.open(logoUrl,"r")
    
    #edge_img = Image.open(edgeUrl, 'r')

    # 将背景图片和圆形头像合成之后当成新的背景图片
    back_img=drawCircleAvatar(avatar,im)
    
    draw = ImageDraw.Draw(back_img)
    font = ImageFont.truetype('/Users/jacky/Desktop/Tellyourfortune_Project/face/simhei.ttf', 20*4) 
    w, h = draw.textsize("面相报告", font=font)
    draw.text(((MAX_W - w)/2, 520), "面相报告", font=font,fill=(0, 0, 0))

    #将二维码图片粘贴在背景图片上
    region = qrcode_img
    region = region.resize((100, 100))
    back_img.paste(region,(10,573))
    
    
    pad = 10*4
    font = ImageFont.truetype('/Users/jacky/Desktop/Tellyourfortune_Project/face/simhei.ttf', 12*4) 
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
    back_img, cureent_h = insert_word_recommand(title_couple,astr_couple, width, back_img, ImageFont.truetype('/Users/jacky/Desktop/Tellyourfortune_Project/face/simhei.ttf', 15*4) , cureent_h, pad)

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
    font1 = ImageFont.truetype('/Users/jacky/Desktop/Tellyourfortune_Project/face/simhei.ttf', 15*4) 
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
    background=Image.open(backgroundUrl,'r')
    background = background.resize((MAX_W,MAX_H))
    #加载二维码图片
    avatar = Image.open(avatarUrl,"r")
    avatar = avatar.resize((400,400)) ##20240216 新加图片大小设置
    w_avatar,h_avatar = avatar.size
    min_location = np.min([w_avatar-x,h_avatar-y,x,y])
    cropped = avatar.crop((x-min_location,y-min_location,x+min_location,y+min_location))
    
    
    qrcode_img = Image.open(qrcodeUrl,"r")
    
    #加载头像图片
    #logo_img = Image.open(logoUrl,"r")
    
    #edge_img = Image.open(edgeUrl, 'r')

    # 将背景图片和圆形头像合成之后当成新的背景图片
    back_img=drawCircleAvatar(cropped,background)
    
    draw = ImageDraw.Draw(back_img)
    font = ImageFont.truetype('/Users/jacky/Desktop/Tellyourfortune_Project/face/simhei.ttf', 20*4) 
    w, h = draw.textsize("人工智能大数据命理分析报告", font=font)
    draw.text(((MAX_W - w)/2, 520), "人工智能大数据命理分析报告", font=font,fill=(0, 0, 0))

    # #将二维码图片粘贴在背景图片上
    # region = qrcode_img
    # region = region.resize((100*4, 100*4))
    # back_img.paste(region,(150*4,MAX_H-180*4))  # 130
    
    # 将logo粘贴到背景图片上
   # region = logo_img
   # region = region.resize((100, 100))
   # back_img.paste(region,(150,MAX_H-100))
     
    pad = 10*4
    font = ImageFont.truetype('/Users/jacky/Desktop/Tellyourfortune_Project/face/simhei.ttf', 12*4) 
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
    back_img, cureent_h = insert_word_recommand(title_couple,astr_couple, width, back_img, ImageFont.truetype('/Users/jacky/Desktop/Tellyourfortune_Project/face/simhei.ttf', 15*4) , cureent_h, pad)
    
    couple_1 = Image.open(couple_1_Url,'r')
    couple_1 = couple_1.resize((400,400))
    back_img.paste(couple_1,(80*4,cureent_h+20))
    
    couple_2 = Image.open(couple_2_Url,'r')
    couple_2 = couple_2.resize((400,400))
    back_img.paste(couple_2,(220*4,cureent_h+20))
    
    match_rate_1 = "吻合度：" +match_rate_1
    match_rate_2 = "吻合度：" +match_rate_2
    draw.text((100*4, cureent_h+80+400), match_rate_1, font=font,fill=(0, 0, 0))
    draw.text((240*4, cureent_h+80+400), match_rate_2, font=font,fill=(0, 0, 0))
    
    back_img.save('out.png') #保存图片


if __name__ == '__main__':
    gender = 1
    if gender == 1:
        image_path = "/Users/jacky/Desktop/Tellyourfortune_Project/face/static/meinv/"
    else:
        image_path = "/Users/jacky/Desktop/Tellyourfortune_Project/face/static/meinan/"
    # image_path= "/static/meinan/"
    input_face_filename = "/Users/jacky/Desktop/Tellyourfortune_Project/face/face/test_img3.jpg"
    output = cal_rate(input_face_filename)
    eye_path = output[0]
    eye_block_str = output[1]
    nose_path = output[2]
    nose_block_str = output[3]
    lip_path = output[4]
    lip_block_str = output[5]
    person_str = output[6]
    job_message = output[7]
    landmarks_json = output[8]
    color= output[9]
    address = output[10]
    index_image1 = output[11]
    index_image2 = output[12]
    image1_url = image_path+str((index_image1%20))+".jpg"
    image2_url = image_path+str(((index_image2)%20))+".jpg"
    wehnhedu1 = str(output[13]) + "%"
    wehnhedu2 = str(output[14]) + "%"
    face_x = output[15]
    face_y = output[16]
    # avatarUrl = post.cover.url[:-4]+"_400"+post.cover.url[-4:]
    # print(avatarUrl)
    # print('.' + post.cover.url)
    generate_report(backgroundUrl="/Users/jacky/Desktop/Tellyourfortune_Project/face/static/picture/report.png",
                    avatarUrl=input_face_filename,
                    qrcodeUrl="/Users/jacky/Desktop/Tellyourfortune_Project/face/static/picture/qrcode.png",
                    couple_1_Url=image1_url,
                    couple_2_Url=image2_url,
                    astr_lucky_color=color,
                    astr_lucky_location=address,
                    astr_doing=job_message,
                    astr_eye=eye_block_str,
                    astr_nose=nose_block_str,
                    astr_mouth=lip_block_str,
                    astr_all=person_str,
                    match_rate_1=wehnhedu1,
                    match_rate_2=wehnhedu2,
                    x=face_x,
                    y=face_y)