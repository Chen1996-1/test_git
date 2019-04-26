# -*- coding: utf-8 -*-
import numpy as np
# 实现插值的模块
from scipy import interpolate
# 画图的模块
import matplotlib.pyplot as plt
#引入相关模块
import requests
import re
#setp one 获取港口信息
def get_dir_code():
	#定义一个字典用于存放港口名称与港口编号
    dir_code = {}
    # get 访问url,得到json 数据，其实就是字典
    url = 'http://www.oceanguide.org.cn/hyyj/index/seaArea.htm'
    response = requests.get(url)
    # response 对象的 text 为字符串类型，通过eval()方法转为字典对象。
    text = eval(response.text)
    #拿到data
    data_list = text["data"]
    #获取 showname:code
    for data in data_list:
    	name = data['name']
    	showName = data['showName']
    	a = {showName:name}
    	dir_code.update(a)
    	# print(name, showName)
    print('okkk')
    #数据本地化，以后可以将以下部分改为存储数据库

    a=open('港口信息.txt','w+')
    a.write(str(dir_code))
    a.close()
    print('港口信息.txt 已写入')
    return dir_code

#step two 获取港口对应code，return code
def get_code():
	while True:
		name = input('请输入查询港口：')
		f = open('港口信息.txt')
		dir_code = eval(f.read())
		code = dir_code.get(name,'没找到输入的港口')
		if code == '没找到输入的港口':
			print(code)
		else:
			False
			return code


#step three 获取指定港口水位数据,return file_name
def get_data_water(code):

	get_water_url = 'http://www.oceanguide.org.cn/hyyj/index/seaAreaData.htm?code={}'.format(code)
	response = requests.get(get_water_url)
	text = eval(response.text)
	if text['message'] != '数据为空！':
		data_list = text.get('data')

		#本地化数据
		file_name = data_list[0]['code']+data_list[0]['updateDate']
		f = open(file_name+'.txt', 'w+')
		for data in data_list:
			#时间
			bizDate = data['bizDate']

			tides = data.get('tide',{'tide':'0','stormTide':'0'})
			#天文潮汐
			tide = tides['tide']
			#涨水高度
			stormTide = tides['stormTide']
			#最终水位
			water = eval(tide) + eval(stormTide)
			#时间	水位
			tex = "{}\t{}\n".format(bizDate[-9:],water)
			f.write(tex)

		f.close()

		print('{}.txt 已写入'.format(file_name))
	else:
		print(text['message']+'暂不能查询')
	return file_name


# 获取y_list return y_list
def get_flie_data(file_name):
	f = open(file_name+'.txt')
	x= f.readlines()
	y_list = []
	for i in x:
		a,b = i.split('\t')
		y = eval(b)
		y_list.append(y)
	return y_list



#求出拟合后的水位，yNew
def mtplb(y_list,file_name):

	# y 表示纵轴，水位
	y = np.array(y_list)
	# x是一个横轴，时间（类似时间），从0 到数据端点，间隔为6，表示小时
	x_end_point  = len(y_list)*6
	x = np.array([num for num in range(0,x_end_point,6)])

	# 插值法之后的x轴值，表示从0 到 数据端点，每个数据间插入5个值，得出每十分钟
	xnew = np.arange(0, x_end_point-6, 1)

	"""
	kind方法：
	nearest、zero、slinear、quadratic、cubic
	实现函数func
	"""
	func = interpolate.interp1d(x, y, kind='cubic')
	# 利用xnew和func函数生成ynew，xnew的数量等于ynew数量
	ynew = func(xnew)
	f = open('{}-plot-tide.txt'.format(file_name),'w+')
	f.write(str(ynew))
	f.close()
	print('文件已写入{}-plot-tide.txt'.format(file_name))
	# 画图部分
	# 原图
	plt.plot(x, y, color='g', marker='',label=u"old")
	# 拟合之后的平滑曲线图
	plt.plot(xnew, ynew, color = 'r' ,label=u"thenew")


	plt.legend(loc='upper left')
	plt.show()

#运行函数

get_dir_code()
file_name = get_data_water(get_code())
y_list = get_flie_data(file_name)

mtplb(y_list,file_name)