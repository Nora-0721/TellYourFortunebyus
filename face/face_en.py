import json

import numpy as np
import cv2
import dlib
import random
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
        eye_block_str = "You are talented and intelligent, and suitable for brain-related work. This kind of people have insight and strong personal abilities. You are suitable for businesses that can make a lot of money."
    elif eye_rate <= 6.6:
        eye_str = 0
        eye_block_str ="You are kind and friendly to others, can improve team cohesion, and prefer to exercise and sports."
    elif eye_rate > 6.6 and eye_area_rate <= 210:
        eye_str = 0
        eye_block_str ="You have a cheerful and outgoing personality, and good at communication and socializing. You usually have a gentle and humble attitude towards other people."
    else:
        eye_str = 1
        eye_block_str ="You do not like to compare the gains or losses, right or wrong with people. You are kind and helpful. However, you do not have much ambition for life, and you feel contentment and happiness in life."
    #EI
    if eye_dis_rate > 4.2:
        eyedis_str = 1
        eye_block_str = eye_block_str+"You are mind sensitive, and prefer to find some details in life. You would like to plan how to implement them when deal with things, and done them strictly. "
    else:
        eyedis_str = 0
        eye_block_str = eye_block_str+"You are broad-minded and has a stable personality. You do not like to compete with others and less likely to be emotional."

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
        nose_block_st = "No matter what things you face, you can deal with it calmly. Once you have a good opportunity, you will seize it well. You are full of confidence in all aspects of yourself. You are a very powerful person. You give a relaxed feeling to the people around you and are suitable for being a leader in a large team. You can get great achievements in the feature."
    else:
        nose_str = 0
        nose_block_st ="You come from a well-off family. You are not only smart, but also optimistic and cheerful. No matter what difficulties you face, you always have a positive attitude. In daily life or in the workplace, you can express your personality charm well. You can demonstrate your own advantages fully, have great achievements, and get rich wealth."
    return nose_str,nose_block_st


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

    lip_height = distance(lip_med_5052, lip_med_5658)
    lip_height_rate = face_height / lip_height
    return lip_top, lip_width_rate, lip_height_rate

# JP
def judge_lip(landmarks, face):
    lip_top, lip_width_rate, lip_height_rate = lip_cal(landmarks, face)
    if lip_top < -2:
        if lip_width_rate < 3 and lip_height_rate > 7:
            lip_str = 1
            lip_block_str = "You have elegant manners, noble nature, and grow in mud, yet never contaminates with it, floats on waving water, yet never dances with it. You have a kind of arrogance that is tough and unwilling to succumb, but you are a little vain. You will be rich in the middle age of your life."
        else:
            lip_str =0
            lip_block_str = "You are ambitious, smart, capable of not being arrogant and impatient. You have both integrity and virtue, and can get success in career. Everything goes well in your life, and wealth is prosperous. You can occupy a high position in officials and reputation are outstanding."
    else:
        if lip_width_rate > 2.6 and lip_height_rate < 7:
            lip_str = 0
            lip_block_str = "In daily life or career, you can be full of vigor, aggressive, smarter. You will persevere in your goals, will not give up in the halfway, and can do great things."
        else:
            lip_str = 1
            lip_block_str = "You can achieve golden luck, get a lot of good luck and well fortune, comply with social morality, be respected, and are promoted by nobles, fate is well-reached, can get great success and happiness, good fortune."
    return lip_str,lip_block_str,lip_width_rate

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


def cal_rate_en(file_name):
    output_list = []
    detector = dlib.get_frontal_face_detector()
    import os
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dat_path = os.path.join(BASE_DIR, 'face', 'shape_predictor_68_face_landmarks.dat')
    predictor = dlib.shape_predictor(dat_path)
    img = cv2.imread(file_name)
    # 取灰度
    img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    # 人脸数rects
    rects = detector(img_gray, 1)
    if len(rects) == 1:
        for i, face in enumerate(rects):
            landmarks = np.matrix([[p.x, p.y] for p in predictor(img, rects[0]).parts()])
            landmarks_list =landmarks.tolist()
            landmarks_json = json.dumps(landmarks_list)#将点转化为json数据
            SN, EI,eye_block_str = judge_eye(landmarks, face)
            TF,nose_block_st = judge_nose(landmarks)
            JP,lip_block_str,lip_width_rate = judge_lip(landmarks, face,)
            person_str, job_message =judge_MBTI(EI, SN, TF, JP,lip_width_rate)
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

            landmarks_list = json.loads(landmarks_json)#将json数据还原

            return  output_list
    else:
        print("please use right picture!!!")
        return None

def judge_MBTI(EI,SN,TF,JP,lip_width_rate):
    sum = EI*8+SN*4+TF*2+JP
    person_str = ""
	
    if sum>=16:
        print("error!!!")
    elif sum ==15:
        # print("INFP")
        # print("在生活中比较乐于助人，为人十分的善良，而且善于表达自己的想法。平时的时候会比较安静，做事会深思熟虑后再做出决定，为人老实忠厚，善于理解他人的难处与位置，而且有很强的洞察能力。")
        person_str = "You are eager to help other people, very kind, and good at expressing your own ideas. You are quite usually. When you do something, you will think thoroughly before planning. You are honest, loyal, and good at understanding the difficulties and plights of others. You also have a strong insight."
    elif sum ==14:
        # print("INFJ")
        person_str ="You prefer quiet place and are very sensitive to details. You have strong intuition and insight, and good at handling some details. You are very reliable to others, and a good listener and comforter when your friends are unhappy or depressed. However, you are idealistic sometimes."
        # print("为人比较喜欢安静的地方，对细节十分的敏感。为人的直觉和洞察能力很强善于处理一些细节。而且本人还很可靠，在朋友不开心或者郁闷的时候是一个好的倾听者和安慰者。但是，有时候为人比较理想主义，做事以结果为准。")
    elif sum ==13:
        # print("INTP")
        person_str ="You have a relatively strong innovative ability and logical reasoning ability, and can combine all your own situation to solve all the problems. Be curious about new things. You are a creative thinker, and solving problems. Most of the time, You are smart, but lazy and conservative sometimes."
        # print("本人有着比较强的创新能力和逻辑推理能力，能够很快的结合自身所有解决遇到的问题。对新的事物会比较好奇。是一位有创造力的思考者，也善于分析解决问题。大多数时候，为人比较机灵，但是，有时候会比较懒散，保守。")
    elif sum ==12:
        # print("INTJ")
        person_str ="You have a wealth of imagination and relatively divergent thinking. When encountering difficulties, you are good at analyzing, planning and solving problems. You have strong determination when doing everything, and face the difficulties directly. You have a long-term perspective and a certain innovative spirit when dealing things. You are independent in daily life, and the logic is clear."
        # print("本人有着丰富的想象力思维比较发散，遇到困难的时候，善于分析、策划并解决遇到的问题。做事情很有决心遇到困难一直都是迎难而上。具有对事情的处理具有长远的眼光和有一定的创新精神。生活上比较独立，逻辑比较清晰。")
    elif sum ==11:
        # print("ISFP")
        person_str ="you usually prepare for everything in advance, and have a strong adaptability to emergencies. Be kind, treat others with sincerity and friendliness, be smart, open-minded, and be a good listener."
        # print("本人做事情一般都会提前为此做好准备，而且对突发事件也有很强的适应能力。为人善良，待人友好，比较机灵，思想开放，而且还是是一位好的倾听者。")
    elif sum ==10:
        # print("ISFJ")
        person_str ="You are very enthusiastic when doing everything, and are very focused when he encounters things. You always give others a strong sense of responsibility when doing things and try to solve the problems encountered,. Your work is highly organized."
        # print("做事情的时候很有热情，遇事的时候十分专注、给人一种沉稳、踏实的感觉。有很强的负责心，做事高度组织化。")
    elif sum ==9:
        # print("ISTP")
        person_str ="You like to take risks, have a lot of curiosity, and are independent relatively. You can complete the things that need to be done efficiently, and you are good at analyzing the problems encountered. Your character is cold relatively, the temperament is noble and elegant. But there will be a little impulse suddenly, and go to the horns sometimes."
        # print("本人喜欢冒险，为人比较独立，喜欢高效率的办完事情，善于分析问题。性格上比较高冷。有时候会突然有点冲动，有点古板呆滞。")
    elif sum ==8:
        # print("ISTJ")
        person_str ="You prefer to stay in one place quietly. You are very seriously when doing everything, and are very pragmatic and consider things very comprehensively. When doing things, you have a strong sense of responsibility. You are realistic and treat people with sincerity and friendliness in daily life."
        # print("比较喜欢安静。做事十分认真、为人务实而且还很全面。做事情的时候很强的负责感，为人比较实事求是，在生活中待人真诚。")
    elif sum ==7:
        # print("ENFP")
        person_str ="You are good at communicating with people, have a good reputation in the your circle, and always have a high passion for life. You will give people a vigorous and upward feeling. You are very cheerful, optimistic, and very creative and ideal."
        # print("善于与人交际沟通，对生活一直保有着较高的热情。为人开朗，乐观，而且有创意，有理想。")
    elif sum ==6:
        # print("ENFJ")
        person_str ="You are good at getting along with other people, and know how to talk on different occasions and situations. You like to help others when friends encounter difficulties. You are outgoing, and also sensitive to details, born with an inherent charm."
        # print("善于与人相处，喜欢服务他人，比较外向，但是为人对细节也很敏感，天生有一种发自内在的魅力。")
    elif sum ==5:
        # print("ENTP")
        person_str ="You have a strong curiosity about unknown things, and you are very wise in doing things. You like innovation and regards innovation as a part of your life. You are very smart in daily life. But, you might be a bit outspoken when dealing with things."
        # print("对未知的事情有着较强的好奇心，做事睿智，喜欢创新，是一个生活中的智多星。但是处事的时候，可能会有点直言不讳。")
    elif sum ==4:
        # print("ENTJ")
        person_str ="You have strong leadership skills, and able to lead the team to make better progress. You are full of imagination, and your thinking about somethings are always different from ordinary people. You are decisive, bold and frank. You are a problem solver, a knowledge bookstore for small partners."
        # print("有着很强的领导能力，富有想象力，做事果断，性格大胆，为人坦率。是问题的解决者，小伙伴的知识书屋。")
    elif sum ==3:
        # print("ESFP")
        person_str ="You are always full of energy and enthusiasm. No matter what happens,you never give up, and work hard. But you are like to play, and sometimes make mistakes because of love to play. You are humorous, witty and clever when contact with other people."
        # print("一直是一个充满活力和热情的人，比较喜欢玩，但是做事实干。与人相处时，幽默，机智而且机灵，大家的欢乐果。")
    elif sum ==2:
        # print("ESFJ")
        person_str ="You are helpful, likes to care for others, and good at social intercourse. You have a good reputation in the social circle. You do your job with due diligence. You like to try your best to handle the things for you, and keep your promise. You are a very popular person."
        # print("乐于助人，喜欢关心他人，比较善于社交，对人尽职尽责、信守承诺是一位很受欢迎的人。")
    elif sum ==1:
        # print("ESTP")
        person_str ="In daily life, you are very energetic and very sensitive to incidents. You can find the final answer from the smallest details. You are outgoing and having a strong curiosity about unknown things. You are a real activism, pragmatic, and a problem solver."
        # print("有活力，遇事敏锐，为人外向，有很强的好奇心，真正的行动主义，务实的问题解决者。")
    elif sum ==0:
        # print("ESTJ")
        person_str ="You are good at managing and analyzing problems. You are a leader in the team, and able to organize everyone to move towards the set goals. And you are very visionary, able to predict and solve problems in advance. You are hard-working, and the leader in everyone's heart."
        # print("善于管理和分析，能够较好的组织大家，为人有远见，勤奋，外向。是大家心中的领头人。")
    job_message = ""
    job_message = get_randomjob(sum,lip_width_rate)
    # print(job_message)
    return person_str,job_message


def get_randomjob(index,seed):
    number = 4
    list_job = np.load("list_job_en.npy")
    length_job = len(list_job[index])
    output_list=[]
    job_id = int(seed*134)%length_job
    for i in range(number):        
        output_list.append(list_job[index][job_id])
        job_id = (job_id + 1)%length_job
    str_job=""
    for name in output_list:
        str_job=str_job+name+","
    
    return str_job[:-2]


# def create_jobbox():
    # list = []
    # str1="Detective, business administrator, insurance sales agent, military leader, pharmacist, athlete, police officer, sales representative, lawyer, judge, coach, teacher, finance officer, project manager"
    # ESTJ = str1.split(',')
    # list.append(ESTJ)

    # str2="Entrepreneur, social flower, entertainer, marketing executive, sports coach, banker, computer technician, investor, sales representative, detective, police officer, paramedic, athlete"
    # ESTP = str2.split(',')
    # list.append(ESTP)

    # str3="Nurse, child care administrator, office manager, consultant, sales representative, teacher, doctor, social worker, accountant, administrative assistant, stenographer, health worker, public relations supervisor, selling insurance"
    # ESFJ = str3.split(',')
    # list.append(ESFJ)

    # str4="Artists, fashion designers, interior decorators, photographers, sales representatives, actors, athletes, consultants, social workers, child care, general practitioners, environmental scientists, hotel service professionals, food service professionals"
    # ESFP = str4.split(',')
    # list.append(ESFP)

    # str5="Executives, lawyers, architects, engineers, market researchers, analysts, management consultants, scientists, venture capital, entrepreneurs, computer consultants, business managers, university professors"
    # ENTJ = str5.split(',')
    # list.append(ENTJ)

    # str6="Psychologist, entrepreneur, photographer, real estate developer, creative director, engineer, scientist, sales representative, actor, marketer, computer programmer, political consultant"
    # ENTP = str6.split(',')
    # list.append(ENTP)

    # str7="Psychologist, advertising executive, dispatcher, social worker, teacher, consultant, sales manager, public relations expert, manager, event coordinator, politician, writer, diplomat, human resources manager"
    # ENFJ = str7.split(',')
    # list.append(ENFJ)

    # str8="Entrepreneur, actor, teacher, consultant, psychologist, advertising director, writer, restaurant owner, TV reporter, scientist, engineer, computer programmer, artist, politician, curator"
    # ENFP = str8.split(',')
    # list.append(ENFP)

    # str9="Office manager, criminal supervisor, logistics specialist, accountant, auditor, chief financial officer, government employee, web developer, administrator, executive, lawyer, computer programmer, judge, police officer, air traffic controller"
    # ISTJ = str9.split(',')
    # list.append(ISTJ)

    # str10="Detective, computer programmer, civil engineer, system analyst, police officer, economist, farmer, pilot, mechanic, entrepreneur, athlete, construction, data analyst, rancher, electronics technician, construction contractor"
    # ISTP = str10.split(',')
    # list.append(ISTP)

    # str11="Financial consultants, accountants, designers, stenographers, dentists, school teachers, librarians, franchisees, customer service representatives, paralegals, rangers, firefighters, office managers, administrative assistants"
    # ISFJ = str11.split(',')
    # list.append(ISFJ)

    # str12="Musicians, artists, childcare, fashion designers, social workers, physical therapists, teachers, veterinarians, pediatricians, psychologists, consultants, massage therapists, store managers, coaches, nurses"
    # ISFP = str12.split(',')
    # list.append(ISFP)

    # str13="Engineers, scientists, teachers, dentists, investment bankers, business managers, military leaders, computer programmers, physicians, organization leaders, business administrators, financial consultants"
    # INTJ = str13.split(',')
    # list.append(INTJ)

    # str14="Architect, engineer, scientist, chemist, photographer, strategic planner, computer programmer, financial analyst, real estate developer, software designer, university professor, economist, system analyst, technical writer, mechanic"
    # INTP = str14.split(',')
    # list.append(INTP)

    # str15="Writer, interior designer, pediatrician, school consultant, therapist, social worker, organization consultant, child care, customer service manager, psychologist, musician, photographer, dentist"
    # INFJ = str15.split(',')
    # list.append(INFJ)

    # str16="Writer, editor, psychologist, graphic designer, physiotherapist, professional coach, social worker, musician, teacher, artist, cartoonist, librarian"
    # INFP = str16.split(',')
    # list.append(INFP)
    # np.save("list_job_en.npy",list)


if __name__ == '__main__':
    create_jobbox()
    cal_rate("qingxiumei.jpg")
