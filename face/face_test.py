import json
import os
import sys

# Windows下修复DeepFace的Unicode编码问题
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import numpy as np
import cv2
import dlib
import random

# 把 DeepFace 的权重目录改到项目内: E:/Web/tellyourfortune/deepface_data
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DEEPFACE_HOME", os.path.join(PROJECT_ROOT, "deepface_data"))

from deepface import DeepFace
from django.conf import settings
from tensorflow.keras.preprocessing import image
import numpy as np
from tensorflow.python import keras
import time

from ai import DashScopeChat
from mainsite.models import FaceFeature, SeedToFace
# from stygan import StyleGANImageGenerator


# from django.conf import settings
def change_path(file_path,str_block):
    str=file_path
    path = str.split('/')
    path[-2]="block_face"
    if "jpg" in path[-1]:
        path[-1]=str_block+".jpg"
    elif "png" in path[-1]:
        path[-1]=str_block+".png"
    elif "bmp" in path[-1]:
        path[-1]=str_block+".bmp"
    elif "jpeg" in path[-1]:
        path[-1]=str_block+".jpeg"
    else:
        path[-1]=str_block+".jpg"
    str='/'
    path_new = "."+str.join(path)
    return path_new

def distance(pos_left, pos_right):
    return np.linalg.norm(pos_left - pos_right)


def eye_cal(landmarks, face):
    eye_width1 = distance(landmarks[42, :], landmarks[45, :])
    eye_width2 = distance(landmarks[36, :], landmarks[39, :])
    eye_width = (eye_width1 + eye_width2) / 2

    eye_avg_left = (landmarks[37, :] + landmarks[38, :]) - (landmarks[41, :] + landmarks[40, :])
    eye_avg_right = (landmarks[43, :] + landmarks[44, :]) - (landmarks[47, :] + landmarks[46, :])
    eye_height = distance(eye_avg_left, eye_avg_right)

    left = face.left()
    top = face.top()
    right = face.right()
    bottom = face.bottom()
    face_height = top - bottom
    face_width = left - right

    eye_rate = eye_width / eye_height
    # print(eye_rate)
    eye_area_rate = (face_height * face_width) / (eye_width * eye_height)

    eye_dis = distance(landmarks[39, :], landmarks[42, :])
    eye_dis_rate = -1 * face_width / eye_dis
    return eye_rate, eye_area_rate, eye_dis_rate

# EISN
def judge_eye(landmarks, face):
    eye_rate, eye_area_rate, eye_dis_rate = eye_cal(landmarks, face)

    if eye_rate <= 6.6 and eye_area_rate <= 210:
        eye_str = 1
        eye_block_str = "天资聪慧，适合从事与脑力有关的工作，这类人有眼力见，并且个人能力极强，适合能赚大钱的事业。"
    elif eye_rate <= 6.6:
        eye_str = 0
        eye_block_str = "为人比较和蔼，待人友善个人，是团队里不可或缺的粘合剂，比较喜欢锻炼，注重体育。"
    elif eye_rate > 6.6 and eye_area_rate <= 210:
        eye_str = 0
        eye_block_str = "性格开朗外向，善于交际和应酬，平常对人态度温和谦逊，十分和气，十分忍让。"
    else:
        eye_str = 1
        eye_block_str = "不喜与人计较得失错对,为人心地善良，乐于助人。但是，对生活没有太大志向，知足常乐。"
    # EI
    if eye_dis_rate > 4.2:
        eyedis_str = 1
        eye_block_str = eye_block_str + "心思敏感，容易发现生活中的一些细节。遇到事情喜欢先规划如何再去实行，凡事比较较真，都会去认真完成。"
    else:
        eyedis_str = 0
        eye_block_str = eye_block_str + "为人心胸宽和，个性显得稳定踏实，不太喜欢和人争锋计较，凡事随缘的态度，也比较不会感情用事。"

    chat = DashScopeChat()
    res = chat.ask("已知eye_width / eye_height, (face_height * face_width) / (eye_width * eye_height), -1 * face_width / eye_dis分别如下"+str(eye_rate)+"、"+str(eye_area_rate)+"、"+str(eye_dis_rate)+"，请你给出算命结果")
    if res!=None:
        eye_block_str = res

    return eye_str, eyedis_str,eye_block_str


def nose_cal(landmarks):
    nose_width = distance(landmarks[31, :], landmarks[35, :])
    nose_height = distance(landmarks[30, :], landmarks[33, :])
    nose_rate = nose_width / nose_height
    # print(nose_rate)
    return nose_rate

# FT
def judge_nose(landmarks):
    nose_rate = nose_cal(landmarks)
    if nose_rate < 2.2:
        nose_str = 1
        nose_block_st = "不管面对什么事情都有很好的态度，能沉着冷静的面对，身边一旦出现了好机会就会好好把握住，对自己各个方面都充满了信心，是个很厉害的人，天生胆子就很大的，给周围的人一种很轻松的感觉，适合在大团队当领导，日后能取得不错的成绩。"
    else:
        nose_str = 0
        nose_block_st ="家境比较不错，为人不但聪明，而且性格乐观、开朗。不管面对什么都会有着积极向上的态度，在生活或是职场中的能较好的表现自己的人格魅力，充分展现出自己的优点，有着一定成就，前途一片光明，能够获得丰厚的财富。"
    chat = DashScopeChat()
    res = chat.ask("已知nose_width / nose_height如下"+str(nose_rate)+"，请你算命结果")
    if res!=None:
        nose_block_st = res
    return nose_str,nose_block_st,nose_rate


def lip_cal(landmarks, face):
    left = face.left()
    top = face.top()
    right = face.right()
    bottom = face.bottom()
    face_height = bottom - top
    face_width = right - left

    lip_top = (landmarks[50, 1] + landmarks[52, 1]) // 2 - landmarks[51, 1]
    lip_width = distance(landmarks[48, :], landmarks[54, :])
    lip_width_rate = face_width / lip_width
    lip_med_5052 = (landmarks[50, :] + landmarks[52, :]) // 2
    lip_med_5658 = (landmarks[56, :] + landmarks[58, :]) // 2


    face_x = (landmarks[50, 0] + landmarks[52, 0])//2
    face_y = (top+bottom)//2
    print("x:"+str(face_x)+"y:"+str(face_y))

    lip_height = distance(lip_med_5052, lip_med_5658)
    lip_height_rate = face_height / lip_height
    return lip_top, lip_width_rate, lip_height_rate,face_x,face_y

# JP
def judge_lip(landmarks, face):
    lip_top, lip_width_rate, lip_height_rate,face_x,face_y = lip_cal(landmarks, face)
    if lip_top < -2:
        if lip_width_rate < 3 and lip_height_rate > 7:
            lip_str = 1
            lip_block_str = "举止优雅，生性高贵，受淤泥而不染，灌清涟而不妖，有一种坚韧不拔不肯屈服的傲气，但是有点爱慕虚荣，人到中年则富贵显。"
        else:
            lip_str =0
            lip_block_str = "为人胸襟壑达，精明干练，不骄不躁，德才兼备，能成事业，诸事顺意，财运旺盛，官居高位，声名显赫。"
    else:
        if lip_width_rate > 2.6 and lip_height_rate < 7:
            lip_str = 0
            lip_block_str = "在生活和事业中，都能充满干劲，积极进取，为人比较聪明，对自己的目标会坚持不懈，不会半途而废，能成大事。"
        else:
            lip_str = 1
            lip_block_str = "金运可达，福禄有余，遵守道德，受人敬爱，贵人提拔，命运通达，大有成功，获得幸福，福禄双收，女命富贵，金运之命。"
    chat = DashScopeChat()
    res = chat.ask("已知face_width/lip_width和face_height/lip_height分别如下" + str(lip_width_rate)+"、"+str(lip_height_rate) + "，请你给出算命结果")
    if res != None:
        chat = DashScopeChat()
        res = chat.ask("已知face_width/lip_width和face_height/lip_height分别如下" + str(lip_width_rate) + "、" + str(
            lip_height_rate) + "，请你给出算命结果")
        lip_block_str = res
    return lip_str,lip_block_str,lip_width_rate,face_x,face_y

def face_block(landmarks,image,file_path):
    # change_path(file_path, str_block)
    # the width of the block
    block_top_x = landmarks[16, 0]+10
    block_bottom_x = landmarks[0, 0] -10
    # the  eye block
    eye_block_top_y = (landmarks[19, 1] + landmarks[24,1]) // 2-5
    eye_block_bottom_y = landmarks[30, 1]+5
    eye_image_block = image[eye_block_top_y:eye_block_bottom_y,block_bottom_x:block_top_x]
    #the nose block
    nose_block_top_y = landmarks[27, 1] -5
    nose_block_bottom_y = landmarks[33, 1]+5
    nose_image_block = image[nose_block_top_y:nose_block_bottom_y,block_bottom_x:block_top_x ]
    #the nose block
    lip_block_top_y = landmarks[33, 1] -5
    lip_block_bottom_y = landmarks[8, 1]
    lip_image_block = image[ lip_block_top_y:lip_block_bottom_y,block_bottom_x:block_top_x]

    eye_path = change_path(file_path, "eye")
    nose_path = change_path(file_path, "nose")
    lip_path = change_path(file_path, "lip")

    cv2.imwrite(eye_path,eye_image_block)
    cv2.imwrite(nose_path,nose_image_block)
    cv2.imwrite(lip_path,lip_image_block)

    return eye_path,nose_path,lip_path

import cv2
import dlib
import json
import numpy as np


# sex=1男，0女
def ganGenerate(relative_landmarks, sex):
    if sex==1:
        face_features = SeedToFace.objects.filter(sex=0)
    else:
        face_features = SeedToFace.objects.filter(sex=1)
    max_similarity = float('inf')  # 初始时设置一个最大值
    best_match = None  # 最佳匹配对象
    best_match2 = None
    # 遍历所有记录，计算相似度
    for face in face_features:
        stored_landmarks = face.get_landmarks()  # 获取存储的 landmarks

        # 计算相似度（可以选择使用欧几里得距离或其他方法）
        similarity = euclidean_distance(relative_landmarks, stored_landmarks)

        # 如果当前的相似度更低，说明找到了更好的匹配
        if similarity < max_similarity:
            max_similarity = similarity
            best_match2 = best_match
            best_match = face  # 保存当前最相似的 face
    if best_match:
        seed = best_match.seed  # 获取图片的 URL（假设你已经配置了静态文件）
        seed2 = best_match2.seed
    else:
        seed = random.randint(0, 1000)
        seed2 = random.randint(0, 1000)

    # 无 GPU 时，直接使用已有的静态 GAN 图片，避免在 CPU 上长时间计算
    import os
    import torch
    static_gan_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'gan')
    fallback_images = ['373.png', '444.png', '733.png', '741.png', '764.png', '817.png', '854.png', '856.png']
    if not torch.cuda.is_available():
        if os.path.isdir(static_gan_dir):
            choices = [img for img in fallback_images if os.path.exists(os.path.join(static_gan_dir, img))]
            if len(choices) >= 2:
                import random as _rand
                img1, img2 = _rand.sample(choices, 2)
                return f'/static/gan/{img1}', f'/static/gan/{img2}'

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    network_pkl_path = os.path.join(base_dir, 'stygan', 'ffhq.pkl')
    generator = StyleGANImageGenerator(
        network_pkl=network_pkl_path,
        outdir='./static/gan',
        truncation_psi=0.7
    )
    generator.generate_images(seeds=[seed, seed2])
    return '/static/gan/'+str(seed)+'.png','/static/gan/'+str(seed2)+'.png'


def imread_unicode(file_path):
    """兼容中文路径的图片读取函数。"""
    import numpy as np
    data = np.fromfile(file_path, dtype=np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    return img


def cal_rate(file_name,sex):
    """根据上传图片计算五官特征等信息。

    参数 file_name 是类似 "./media/image/xxx.jpg" 的相对 URL 路径，
    这里内部会转换出一个本地绝对路径用于读写图片，但在生成
    眼睛/鼻子/嘴巴的局部图片路径时，仍然使用相对路径，
    以保持与原来模板中的引用方式一致（./media/block_face/...）。
    """

    output_list = []
    detector = dlib.get_frontal_face_detector()
    import os
    import urllib.parse
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dat_path = os.path.join(current_dir, 'shape_predictor_68_face_landmarks.dat')
    if not os.path.exists(dat_path):
        raise RuntimeError(f"dat_path not found: {dat_path}")
    predictor = dlib.shape_predictor(dat_path)

    # 1) file_name 是 URL 风格路径，例如 "./media/image/%E8%AF%81%E4%BB%B6.jpg"
    url_path = file_name
    rel_path = url_path.lstrip('./')               # 去掉开头的 ./ 或 /
    rel_path = urllib.parse.unquote(rel_path)      # 解码成真正的中文文件名

    # 2) 构造本地绝对路径，用于 OpenCV 读写
    project_root = os.path.dirname(current_dir)    # E:\Web\tellyourfortune
    abs_file_path = os.path.join(project_root, rel_path.replace('/', os.sep))

    if not os.path.exists(abs_file_path):
        raise RuntimeError(f"image not found: {abs_file_path}")

    img_old = imread_unicode(abs_file_path)
    # 保持纵横比调整图片大小
    max_size = 800  # 设定最大尺寸，避免处理过大的图像
    height, width = img_old.shape[:2]
    if height > max_size or width > max_size:
        if height > width:
            new_height = max_size
            new_width = int(width * max_size / height)
        else:
            new_width = max_size
            new_height = int(height * max_size / width)
        img_resized = cv2.resize(img_old, (new_width, new_height))
    else:
        img_resized = img_old
    # 把缩放后的大图也写回绝对路径
    cv2.imwrite(abs_file_path[:-4]+"_400"+abs_file_path[-4:], img_resized)
    # 转为灰度图像
    img_gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)

    # 检测人脸
    rects = detector(img_gray, 1)
    if len(rects) == 1:
        for i, face in enumerate(rects):
            # 获取人脸的边界框
            landmarks = np.matrix([[p.x, p.y] for p in predictor(img_resized, rects[0]).parts()])
            landmarks_list =landmarks.tolist()
            relative_landmarks = []
            first_x, first_y = landmarks_list[0]  # 获取第一个坐标的 x 和 y
            for (x, y) in landmarks_list:
                relative_x = x - first_x  # 转换为相对坐标
                relative_y = y - first_y
                relative_landmarks.append([relative_x, relative_y])
            # 打印相对坐标
            print("landmarks_list:"+str(landmarks_list))
            print("relative_landmarks"+str(relative_landmarks))
            landmarks_json = json.dumps(landmarks_list)#将点转化为json数据
            SN, EI,eye_block_str = judge_eye(landmarks, face)# 眼睛判别感觉（S）与直觉（N） 外向（E）与内向（I）
            TF,nose_block_st,nose_rate = judge_nose(landmarks)# 鼻子判别思维（T）与情感（F）
            JP,lip_block_str,lip_width_rate,face_x,face_y = judge_lip(landmarks, face)# 脸判断判断（J）与知觉（P）
            # DeepFace 需要本地真实文件路径，这里使用已解码的绝对路径
            person_str, job_message = judge_MBTI(EI, SN, TF, JP, lip_width_rate, nose_rate, abs_file_path)
            address, color, index_image1, index_image2, wenhedu1, wenhedu2 = get_randomaddressandcolor(lip_width_rate,nose_rate)
            # imageUrl1 = get_matchUrl(relative_landmarks,sex)
            imageUrl1,imageUrl2 = ganGenerate(relative_landmarks,sex) #"gan生成"
            # 修改图片：这里仍然传入相对路径（./media/image/xxx.jpg），
            # 以便 change_path 生成 "./media/block_face/..." 形式的路径。
            eye_path, nose_path, lip_path = face_block(landmarks, img_resized, './' + rel_path)
            output_list.append(eye_path)# 0
            output_list.append(eye_block_str)
            output_list.append(nose_path)# 2
            output_list.append(nose_block_st)
            output_list.append(lip_path)
            output_list.append(lip_block_str)# 5
            output_list.append(person_str)
            output_list.append(job_message)# 7
            output_list.append(landmarks_json)# 8
            output_list.append(address)
            output_list.append(color)
            output_list.append(index_image1)# 11
            output_list.append(index_image2)
            output_list.append(wenhedu1)# 13
            output_list.append(wenhedu2)
            output_list.append(face_x)# 14
            output_list.append(face_y)
            output_list.append(imageUrl1)# 17
            output_list.append(imageUrl2)
            
            # 生成正缘预测文本（索引 18）
            true_love_str = generate_true_love_prediction(eye_block_str, nose_block_st, lip_block_str, person_str, sex)
            output_list.append(true_love_str)
            
            landmarks_list = json.loads(landmarks_json)#将json数据还原
    else:
        # 打印未能正确检测到单一人脸的数量，避免字符串与整数拼接错误
        print("图片人脸识别错误:", len(rects))
        return None
    return output_list

def cal_rate_bak(file_name):
    output_list = []
    detector = dlib.get_frontal_face_detector()
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dat_path = os.path.join(current_dir, 'shape_predictor_68_face_landmarks.dat')
    predictor = dlib.shape_predictor(dat_path)

    img_old = cv2.imread(file_name)
    # 取灰度
    size = (400,400)
    img = cv2.resize(img_old, size, interpolation=cv2.INTER_AREA)
    cv2.imwrite(file_name[:-4]+"_400"+file_name[-4:],img)
    img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    # 人脸数rects
    rects = detector(img_gray, 1)
    if len(rects) == 1:
        for i, face in enumerate(rects):
            landmarks = np.matrix([[p.x, p.y] for p in predictor(img, rects[0]).parts()])
            landmarks_list =landmarks.tolist()
            landmarks_json = json.dumps(landmarks_list)#将点转化为json数据
            SN, EI,eye_block_str = judge_eye(landmarks, face)# 眼睛判别感觉（S）与直觉（N） 外向（E）与内向（I）
            TF,nose_block_st,nose_rate = judge_nose(landmarks)# 鼻子判别思维（T）与情感（F）
            JP,lip_block_str,lip_width_rate,face_x,face_y = judge_lip(landmarks, face)# 脸判断判断（J）与知觉（P）
            person_str, job_message,address,color,index_image1,index_image2,wenhedu1,wenhedu2 =judge_MBTI(EI, SN, TF, JP,lip_width_rate,nose_rate,file_name)
            eye_path, nose_path, lip_path =face_block(landmarks, img,file_name)
            output_list.append(eye_path)
            output_list.append(eye_block_str)
            output_list.append(nose_path)
            output_list.append(nose_block_st)
            output_list.append(lip_path)
            output_list.append(lip_block_str)
            output_list.append(person_str)
            output_list.append(job_message)
            output_list.append(landmarks_json)
            output_list.append(address)
            output_list.append(color)
            output_list.append(index_image1)
            output_list.append(index_image2)
            output_list.append(wenhedu1)
            output_list.append(wenhedu2)
            output_list.append(face_x)
            output_list.append(face_y)
            landmarks_list = json.loads(landmarks_json)#将json数据还原

            return  output_list
    else:
        print("图片人脸识别错误")
        return None

def judge_MBTI(EI,SN,TF,JP,lip_width_rate,nose_rate,filename):
    sum = EI*8+SN*4+TF*2+JP
    person_str = ""
	
    if sum>=16:
        print("error!!!")
    elif sum ==15:
        # print("INFP")
        # print("在生活中比较乐于助人，为人十分的善良，而且善于表达自己的想法。平时的时候会比较安静，做事会深思熟虑后再做出决定，为人老实忠厚，善于理解他人的难处与位置，而且有很强的洞察能力。")
        person_str = "在生活中比较乐于助人，为人十分的善良，而且善于表达自己的想法。平时的时候会比较安静，做事会深思熟虑后再做出决定，为人老实忠厚，善于理解他人的难处与位置，而且有很强的洞察能力。"
    elif sum ==14:
        # print("INFJ")
        person_str ="为人比较喜欢安静的地方，对细节十分的敏感。为人的直觉和洞察能力很强善于处理一些细节。而且本人还很可靠，在朋友不开心或者郁闷的时候是一个好的倾听者和安慰者。但是，有时候为人比较理想主义，做事以结果为准。"
        # print("为人比较喜欢安静的地方，对细节十分的敏感。为人的直觉和洞察能力很强善于处理一些细节。而且本人还很可靠，在朋友不开心或者郁闷的时候是一个好的倾听者和安慰者。但是，有时候为人比较理想主义，做事以结果为准。")
    elif sum ==13:
        # print("INTP")
        person_str ="本人有着比较强的创新能力和逻辑推理能力，能够很快的结合自身所有解决遇到的问题。对新的事物会比较好奇。是一位有创造力的思考者，也善于分析解决问题。大多数时候，为人比较机灵，但是，有时候会比较懒散，保守。"
        # print("本人有着比较强的创新能力和逻辑推理能力，能够很快的结合自身所有解决遇到的问题。对新的事物会比较好奇。是一位有创造力的思考者，也善于分析解决问题。大多数时候，为人比较机灵，但是，有时候会比较懒散，保守。")
    elif sum ==12:
        # print("INTJ")
        person_str ="本人有着丰富的想象力思维比较发散，遇到困难的时候，善于分析、策划并解决遇到的问题。做事情很有决心遇到困难一直都是迎难而上。具有对事情的处理具有长远的眼光和有一定的创新精神。生活上比较独立，逻辑比较清晰。"
        # print("本人有着丰富的想象力思维比较发散，遇到困难的时候，善于分析、策划并解决遇到的问题。做事情很有决心遇到困难一直都是迎难而上。具有对事情的处理具有长远的眼光和有一定的创新精神。生活上比较独立，逻辑比较清晰。")
    elif sum ==11:
        # print("ISFP")
        person_str ="本人做事情一般都会提前为此做好准备，而且对突发事件也有很强的适应能力。为人善良，待人真诚友好，比较机灵，思想开放，而且还是一位好的倾听者。"
        # print("本人做事情一般都会提前为此做好准备，而且对突发事件也有很强的适应能力。为人善良，待人友好，比较机灵，思想开放，而且还是是一位好的倾听者。")
    elif sum ==10:
        # print("ISFJ")
        person_str ="做事情的时候很有热情，遇事的时候十分专注，时常给人一种沉稳、踏实的感觉。做事情有着很强的负责心，对遇到的问题都会尽力的去解决，而且做的事情具有高度组织化。"
        # print("做事情的时候很有热情，遇事的时候十分专注、给人一种沉稳、踏实的感觉。有很强的负责心，做事高度组织化。")
    elif sum ==9:
        # print("ISTP")
        person_str ="本人喜欢冒险，好奇心旺盛，而且比较独立，能够高效率的办完需要做的事情，善于分析遇到的问题。性格上比较高冷，气质上比高贵典雅。但是有时候会突然有点小冲动，会去钻牛角尖。"
        # print("本人喜欢冒险，为人比较独立，喜欢高效率的办完事情，善于分析问题。性格上比较高冷。有时候会突然有点冲动，有点古板呆滞。")
    elif sum ==8:
        # print("ISTJ")
        person_str ="比较喜欢安静的待在一个地方。做事十分认真，为人十分务实而且考虑事情还很全面。做事情的时候有着很强的负责感，比较实事求是，在生活中待人真诚友善。"
        # print("比较喜欢安静。做事十分认真、为人务实而且还很全面。做事情的时候很强的负责感，为人比较实事求是，在生活中待人真诚。")
    elif sum ==7:
        # print("ENFP")
        person_str ="善于与人交际沟通，在交际圈内有着较好的名声，对生活一直保有着较高的热情，会给人带来一种蓬勃向上的感觉。为人十分开朗，遇事乐观，而且十分有创意，有理想。"
        # print("善于与人交际沟通，对生活一直保有着较高的热情。为人开朗，乐观，而且有创意，有理想。")
    elif sum ==6:
        # print("ENFJ")
        person_str ="善于与人相处，知道分场合分情况说话，喜欢在朋友遇到困难的时候帮助他人，为人比较外向，而且在对细节上面也很敏感，天生有一种发自内在的魅力。"
        # print("善于与人相处，喜欢服务他人，比较外向，但是为人对细节也很敏感，天生有一种发自内在的魅力。")
    elif sum ==5:
        # print("ENTP")
        person_str ="对未知的事情有着较强的好奇心，而且做事十分睿智，喜欢创新，把创新当作自己生活的一部分，是一个生活中的智多星。但是处事的时候，可能会有点直言不讳。"
        # print("对未知的事情有着较强的好奇心，做事睿智，喜欢创新，是一个生活中的智多星。但是处事的时候，可能会有点直言不讳。")
    elif sum ==4:
        # print("ENTJ")
        person_str ="有着很强的领导能力，能够带领团队取得较好的进展，富有想象力，对事情的思考永远会异于常人，做事果断，性格大胆，为人坦率。是问题的解决者，小伙伴的知识书屋。"
        # print("有着很强的领导能力，富有想象力，做事果断，性格大胆，为人坦率。是问题的解决者，小伙伴的知识书屋。")
    elif sum ==3:
        # print("ESFP")
        person_str ="一直是一个充满活力和热情的人，不管遇到什么事情永不言弃，而且做事实干。但是为人比较喜欢玩，有时候会因为爱玩导致出差错。与人相处时，风趣幽默，机智而且机灵，是大家的欢乐果。"
        # print("一直是一个充满活力和热情的人，比较喜欢玩，但是做事实干。与人相处时，幽默，机智而且机灵，大家的欢乐果。")
    elif sum ==2:
        # print("ESFJ")
        person_str ="乐于助人，喜欢关心他人，比较善于社交，在交际圈内有着较好的名声，做事尽职尽责，喜欢尽自己最大的努力去办成交代的事情，信守承诺是一位很受欢迎的人。"
        # print("乐于助人，喜欢关心他人，比较善于社交，对人尽职尽责、信守承诺是一位很受欢迎的人。")
    elif sum ==1:
        # print("ESTP")
        person_str ="在生活中，很有活力，遇事十分敏锐，能够从微小的细节出发找到最终的答案。为人比较外向，对未知的事物有很强的好奇心，是一个真正的行动主义，讲究务实，是问题的解决者。"
        # print("有活力，遇事敏锐，为人外向，有很强的好奇心，真正的行动主义，务实的问题解决者。")
    elif sum ==0:
        # print("ESTJ")
        person_str ="善于管理和分析问题，是团队里的领导者，能够组织大家向已定的目标前进。而且为人十分有远见，能够提前预测并解决问题。做事勤奋。是大家心中的领头人。"
        # print("善于管理和分析，能够较好的组织大家，为人有远见，勤奋，外向。是大家心中的领头人。")
    job_message = ""
    job_message = get_randomjob(filename,lip_width_rate)
    print(job_message)
    # address,color,index_image1,index_image2,wenhedu1,wenhedu2 = get_randomaddressandcolor(lip_width_rate,nose_rate)

    # DeepFace 不支持带非英文字符的路径，这里复制一份临时英文路径给它用
    import os, shutil, uuid
    safe_filename = filename
    try:
        filename.encode('ascii')
    except UnicodeEncodeError:
        dir_name, base_name = os.path.split(filename)
        ext = os.path.splitext(base_name)[1] or '.jpg'
        safe_filename = os.path.join(dir_name, f"deepface_{uuid.uuid4().hex}{ext}")
        try:
            shutil.copyfile(filename, safe_filename)
        except Exception as copy_err:
            print("copy for DeepFace failed:", copy_err)

    # DeepFace分析 - 添加完善的异常处理
    try:
        attribute = DeepFace.analyze(
            img_path=safe_filename,
            actions=['age', 'gender', 'race', 'emotion'],
            enforce_detection=False,  # 放宽人脸检测要求
            silent=True  # 静默模式，减少日志输出
        )
        if attribute is not None and len(attribute) > 0:
            chat = DashScopeChat()
            res = chat.ask("已知人脸属性如下" + str(attribute) + "，请你给出算命结果")
            if res is not None:
                person_str = res
    except Exception as deepface_err:
        print(f"DeepFace分析失败（降级使用MBTI文案）: {str(deepface_err)[:200]}")
        # 降级：继续使用MBTI的person_str，不影响整体流程
    return person_str,job_message


# 计算两个 landmarks 之间的欧几里得距离
def euclidean_distance(landmarks1, landmarks2):
    landmarks1 = np.array(landmarks1)
    landmarks2 = np.array(landmarks2)
    return np.linalg.norm(landmarks1 - landmarks2)  # 欧几里得距离
def get_matchUrl(relative_landmarks,sex):
    # 获取所有 sex == 1 的记录
    if sex==1:
        face_features = FaceFeature.objects.filter(sex=1)
    else:
        face_features = FaceFeature.objects.filter(sex=1)

    max_similarity = float('inf')  # 初始时设置一个最大值
    best_match = None  # 最佳匹配对象

    # 遍历所有记录，计算相似度
    for face in face_features:
        stored_landmarks = face.get_landmarks()  # 获取存储的 landmarks

        # 计算相似度（可以选择使用欧几里得距离或其他方法）
        similarity = euclidean_distance(relative_landmarks, stored_landmarks)

        # 如果当前的相似度更低，说明找到了更好的匹配
        if similarity < max_similarity:
            max_similarity = similarity
            best_match = face  # 保存当前最相似的 face

    # 返回最佳匹配的 URL 或其他需要的信息
    if best_match:
        match_url = best_match.image.name  # 获取图片的 URL（假设你已经配置了静态文件）
        return match_url
    else:
        return None


def get_randomaddressandcolor(seed1,seed2):
    index = int(seed1*154)%9
    index_image1 = int(seed1*123213)%40
    index_image2 = int(seed2*213867)%40
    if index_image2 == index_image1:
        index_image2 = int((seed1+seed2)*13123)%20
        if index_image2 == index_image1:
            index_image2 = int((seed1 + seed2) * 312312) % 20
            if index_image2 == index_image1:
                index_image2 = int(index_image1+1) % 20

    wenhedu1 = int(seed1*462136)%29+70+int(seed1*31231)%10/10
    wenhedu2 = int(seed2*1392131)%28+70+int(seed2*131231)%10/10
    list1 = ["红","橙","黄","绿","青","蓝","紫","白","黑"]
    list2 = ["东","西","南","北","东南","西北","东北","西南","地中"]
    return list1[index],list2[index],index_image1,index_image2,wenhedu1,wenhedu2

	
def get_randomjob(index,seed):
    number = 3
    list_job = np.load("list_job.npy",allow_pickle=True)
    print(list_job)
    index = int(seed*134)%12
    length_job = int(len(list_job[index]))
    output_list=[]
    job_id = int(seed*134)%length_job
    for i in range(number):        
        output_list.append(list_job[index][job_id])
        job_id = (job_id + 1)%length_job
    str_job=""
    for name in output_list:
        str_job=str_job+name+" "
    
    return str_job

def get_index_new(filename):
    img = image.load_img(filename, target_size=(112,112))
    x = np.expand_dims(img, axis=0)
    data = np.array(x,dtype=np.float16)
    start = time.clock()
    model = settings.MODEL
    mid = time.clock()
    print(mid -start)
    y = model.predict(data)
    end = time.clock()
    print(end - mid)
    index_max1,index_max2,index_max3 = predict_3d_new(y)
    return index_max1,index_max2,index_max3
	
def predict_3d_new(y_pre):
	y_pre_list = y_pre[0].tolist()	
	index_max1 = y_pre_list.index(max(y_pre_list))
	y_pre_list[index_max1] = 0
	index_max2 = y_pre_list.index(max(y_pre_list))
	y_pre_list[index_max2] = 0
	index_max3 = y_pre_list.index(max(y_pre_list))
	return index_max1,index_max2,index_max3
	
	
def get_randomjob_new(filename,seed):
	number = 3
	list_job = np.load("list_job9.npy",allow_pickle=True)
	index_max1,index_max2,index_max3 = get_index_new(filename)

	output_list=[]
	job_id = int(seed*134)

	length_job1 = len(list_job[index_max1])		
	job_id1 = (job_id)%length_job1
	output_list.append(list_job[index_max1][job_id1])

	length_job2 = len(list_job[index_max2])		
	job_id2 = (job_id)%length_job2
	output_list.append(list_job[index_max2][job_id2])

	length_job3 = len(list_job[index_max3])		
	job_id3 = (job_id)%length_job3
	output_list.append(list_job[index_max3][job_id3])

	str_job=""
	for name in output_list:
		str_job=str_job+name+" " 
	# print(str_job)
	return str_job

def create_jobbox():
    list = []
    str1="侦探、业务管理员、保险销售代理、军事领导人、药剂师、运动员、警官、销售代表、律师、法官、教练、教师、财务官员、项目经理"
    ESTJ = str1.split('、')
    list.append(ESTJ)

    str2="企业家、投资专家、娱乐家、营销主管、体育教练、银行家、计算机技术人员、投资者、销售代表、侦探、警官、护理人员、运动员"
    ESTP = str2.split('、')
    list.append(ESTP)

    str3="护士、儿童护理管理员、办公室经理、顾问、销售代表、教师、医生、社会工作者、会计、行政助理、速记员、保健工作者、公共关系主管、卖保险"
    ESFJ = str3.split('、')
    list.append(ESFJ)

    str4="艺术家、时装设计师、室内装潢师、摄影师、销售代表、演员、运动员、顾问、社工、儿童护理、全科医生、环境科学家、酒店服务专业人员、餐饮服务专业人员"
    ESFP = str4.split('、')
    list.append(ESFP)

    str5="行政人员、律师、建筑师、工程师、市场调研人员、分析师、管理顾问、科学家、风险投资、企业家、计算机顾问、企业经理、大学教授"
    ENTJ = str5.split('、')
    list.append(ENTJ)

    str6="心理学家、销售代表、摄影师、房地产开发商、创意总监、工程师、科学家、企业家、演员、营销人员、计算机程序员、政治顾问"
    ENTP = str6.split('、')
    list.append(ENTP)

    str7="心理学家、广告主管、调度者、社会工作者、教师、顾问、销售经理、公关专家、经理、事件协调员、政治家、作家、外交官、人力资源经理"
    ENFJ = str7.split('、')
    list.append(ENFJ)

    str8="企业家、演员、教师、顾问、心理学家、企业规划家、作家、餐馆老板、电视记者、科学家、工程师、计算机程序员、艺术家、政治家、策划"
    ENFP = str8.split('、')
    list.append(ENFP)

    str9="办公室经理、刑事监督官、企业家、会计师、教师、首席财务官、政府雇员、网络开发人员、管理员、执行人员、律师、计算机程序员、法官、警官、空中交通管制员"
    ISTJ = str9.split('、')
    list.append(ISTJ)

    str10="侦探、计算机程序员、土木工程师、系统分析员、警官、经济学家、农民、飞行员、机械师、企业家、运动员、建筑、数据分析员、牧场主、电子技师、建筑承包商"
    ISTP = str10.split('、')
    list.append(ISTP)

    str11="财务顾问、会计师、设计师、速记员、牙医、学校教师、图书管理员、特许经营者、客户服务代表、律师助理、护林员、消防员、办公室经理、行政助理"
    ISFJ = str11.split('、')
    list.append(ISFJ)

    str12="音乐家、艺术家、儿童保育、时装设计师、社会工作者、企业家、教师、兽医、儿科医生、心理学家、咨询师、按摩治疗师、商店经理、教练、企业家"
    ISFP = str12.split('、')
    list.append(ISFP)

    str13="工程师、科学家、教师、牙医、投资银行家、业务经理、军事领导人、计算机程序员、内科医生、组织领导人、业务管理员、财务顾问"
    INTJ = str13.split('、')
    list.append(INTJ)

    str14="建筑师、工程师、科学家、化学家、摄影师、战略规划师、计算机程序员、金融分析师、房地产开发商、软件设计师、大学教授、经济学家、系统分析师、技术作家、机械师"
    INTP = str14.split('、')
    list.append(INTP)

    str15="作家、室内设计师、儿科医生、学校顾问、治疗师、社会工作者、组织顾问、儿童护理、客户服务经理、心理学家、音乐家、摄影师、牙医"
    INFJ = str15.split('、')
    list.append(INFJ)

    str16="作家、编辑、心理学家、平面设计师、物理治疗师、专业教练、社会工作者、音乐家、教师、艺术家、漫画家、图书管理员"
    INFP = str16.split('、')
    list.append(INFP)
    np.save("list_job.npy",list)

def cal_pipei(filename,number=0):
    print("start")
    output_list = []
    detector = dlib.get_frontal_face_detector()
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dat_path = os.path.join(current_dir, 'shape_predictor_68_face_landmarks.dat')
    predictor = dlib.shape_predictor(dat_path)
    img_old = cv2.imread(filename)
    # 取灰度
    size = (400,400)
    img = cv2.resize(img_old, size, interpolation=cv2.INTER_AREA)
    cv2.imwrite(filename[:-4]+"_400"+filename[-4:],img)
    img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    # 人脸数rects
    print(filename)
    rects = detector(img_gray, 1)
    if len(rects) == 1:
        for i, face in enumerate(rects):
            landmarks = np.matrix([[p.x, p.y] for p in predictor(img, rects[0]).parts()])
            landmarks_list =landmarks.tolist()
            landmarks_json = json.dumps(landmarks_list)#将点转化为json数据
            TF,nose_block_st,nose_rate = judge_nose(landmarks)
            JP,lip_block_str,lip_width_rate,face_x,face_y = judge_lip(landmarks, face)
            if number==0:
                fenshu,yuju = get_randomAB(lip_width_rate)
                print(fenshu)
            else:
                fenshu,yuju = get_randomBA(lip_width_rate)
                print(fenshu)
            output_list.append(fenshu)
            output_list.append(yuju)
            landmarks_list = json.loads(landmarks_json)#将json数据还原

            return  output_list
    else:
        print("please use right picture!!!")
    return None

def get_randomAB(seed):
    index = int(seed*1433124)%55
    if index <5:
        str_yuju = "也许下一个会更好，你不想试试吗？"
    elif index <15:
        str_yuju = "特别感谢你对我的喜欢,我也非常希望自己能够爱上你,这是一种福气,但是我却不能欺骗你,现在我真的还不想谈感情,而且对你的也只有友谊。"
    elif index <25:
        str_yuju = "你先回去做饭吧,我要等一会才回去。"
    elif index <35:
        str_yuju = "鱼对水说:你看不见我的眼泪,因为我在水里。水说:我能感觉到你的眼泪,因为你在我心里。"
    elif index <45:
        str_yuju = "在一年的每个日子，在一天每个小时，在一小时的每一分钟，在一分钟的每一秒，我都在想你。"
    else:
        str_yuju = "爱不需要理由，但生活需要理由，生活让我离开你，爱就让它深埋心底！"

    return index+45,str_yuju

def get_randomBA(seed):
    index = int(seed*131234)%55
    if index <5:
        str_yuju = "为了你好，我不想因我的存在，影响你的将来。"
    elif index <15:
        str_yuju = "虽然和你在一起一直都很舒服,一点儿都不会别扭,你知道我所有的糗事,但是我们之间真的不来电,做朋友很OK,但是做情侣太熟了不好下口的。"
    elif index <25:
        str_yuju = "几天不见,你看我想你都想瘦了。"
    elif index <35:
        str_yuju = "想着，某天与你在细雨中静静地散步。让雨点敲打着心扉，在这轻灵的世界里感受彼此那份真实的回音。"
    elif index <45:
        str_yuju = "三十年后，如果还有坚持，我希望它属于我。三十年后，如果还有感动，我希望它属于你。"
    else:
        str_yuju = "等到一切都看透，希望你陪我看细水常流！"

    return index+45,str_yuju


def generate_true_love_prediction(eye_block_str, nose_block_str, lip_block_str, person_str, sex, attribute=None):
    """基于面相分析结果动态生成正缘预测文本

    Args:
        eye_block_str: 眼睛分析结果
        nose_block_str: 鼻子分析结果
        lip_block_str: 嘴唇分析结果
        person_str: 综合评价
        sex: 用户性别（用于调整正缘对象描述）
        attribute: DeepFace 分析属性（可选）

    Returns:
        str: 完整的正缘预测文本，如API失败则返回提示信息
    """
    from ai import USE_DASHSCOPE

    if not USE_DASHSCOPE:
        return "正缘预测功能暂时不可用"

    try:
        chat = DashScopeChat()
        # 构建个性化提示词，强调需要生成两段内容
        prompt = f"""你是专业的面相学大师。根据以下面相分析结果，请为此人预测其正缘伴侣的特征。

面相分析：
- 眼睛特征：{eye_block_str}
- 鼻子特征：{nose_block_str}
- 嘴唇特征：{lip_block_str}
- 综合评价：{person_str}
- 性别：{"男" if str(sex) == "1" else "女"}

请生成约200-300字的正缘预测，包含两部分内容：
1. 基于面相的正缘特质分析（说明此人会吸引什么样的伴侣）
2. 正缘对象的详细描述（年龄范围、职业倾向、性格特点、相处模式等）

要求：语言优美流畅，符合传统面相学理论，给出积极正面的预测。"""

        res = chat.ask(prompt)
        if res:
            return res
        else:
            return "正缘预测功能暂时不可用"
    except Exception as e:
        print(f"正缘预测生成失败: {e}")
        return "正缘预测功能暂时不可用"


if __name__ == '__main__':
    # get_index_new("1.jpg")
    create_jobbox()