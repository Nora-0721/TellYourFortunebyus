#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2020/5/9 14:15
# @Author  : Lelsey
# @Site    : 
# @File    : create_data.py
# @Software: PyCharm

from tensorflow.keras.preprocessing import image
import numpy as np
import os

from tensorflow.python import keras


def predict_3d(y_pre):
	y_pre_list = y_pre[0].tolist()	
	print(y_pre_list)
	index_max1 = y_pre_list.index(max(y_pre_list))
	y_pre_list[index_max1] = 0
	index_max2 = y_pre_list.index(max(y_pre_list))
	y_pre_list[index_max2] = 0
	index_max3 = y_pre_list.index(max(y_pre_list))
	return index_max1,index_max2,index_max3
		
def create_jobbox():
	list = []
	str1="企业规划家、通信工程师、运动员、技术经理"
	ESTJ = str1.split('、')
	list.append(ESTJ)

	str2="市场销售、市场广告策划、销售总监、营销主管、广告销售、广告策划和市场营销"
	ESTP = str2.split('、')
	list.append(ESTP)

	str3="开发工程师、慈善家、嵌入式工程师、运维工程师、后台工程师、前端工程师"
	ESFJ = str3.split('、')
	list.append(ESFJ)

	str4="金融管家、金融专家、金融顾问"
	ESFP = str4.split('、')
	list.append(ESFP)

	str5="银行大堂经理、银行经理、技术人员、银行前台、银行客服人员"
	ENTJ = str5.split('、')
	list.append(ENTJ)

	str6="企业构架师、外科医生、企业家、医疗器械销售、数据分析师"
	ENTP = str6.split('、')
	list.append(ENTP)

	str7="初中教师、幼师、高中老师、大学教授、讲师、副教授"
	ENFJ = str7.split('、')
	list.append(ENFJ)

	str8="会计、咨询顾问、慈善家、企业管理咨询、销售经理、演员"
	ENFP = str8.split('、')
	list.append(ENFP)

	str9="科学家、企业构架师、建筑设计师、软件工程师、企业家"
	ISTJ = str9.split('、')
	list.append(ISTJ)

	np.save("list_job9.npy",list)

def get_index(filename):
	img = image.load_img(filename, target_size=(112,112))
	x = np.expand_dims(img, axis=0)
	data = np.array(x,dtype=np.float16)
	model = keras.models.load_model("test8_mode4000_0_max_v0_adam.h5")
	y = model.predict(data)
	index_max1,index_max2,index_max3 = predict_3d(y)
	return index_max1,index_max2,index_max3
	
def get_randomjob(filename):
	number = 3
	seed = 1
	list_job = np.load("list_job9.npy")
	index_max1,index_max2,index_max3 = get_index(filename)
	print(list_job)
	print(index_max1+index_max2+index_max3)
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
	print(str_job)
	return str_job
if __name__ == '__main__':

    # img = image.load_img("1.jpg", target_size=(112,112))
    # x = np.expand_dims(img, axis=0)
    # data = np.array(x,dtype=np.float16)
    # model = keras.models.load_model("test8_mode4000_0_max_v0_adam.h5")
    # y = model.predict(data)
    # print(y)
    # print(predict_3d(y))
	create_jobbox()