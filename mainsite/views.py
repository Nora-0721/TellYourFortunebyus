print("views.py loaded (模块已加载)")
import random
import json

from deepface import DeepFace
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView, CreateView  # new
from django.urls import reverse_lazy  # new

from ai import DashScopeChat, generate_ideal_partner_profile, generate_ideal_partner_image
from stygan import StyleGANImageGenerator
from .forms import PostForm, PostPhoneForm  # new
from .models import Post, PostNew, PostNewImage, FaceFeature, SeedToFace

from django.template.loader import get_template
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.utils.encoding import escape_uri_path
from django.core.cache import cache
from PIL import Image
from face.face_test import cal_rate,cal_pipei
from face.generate_report import generate_report
import random
from django.http import Http404
import time
import numpy as np
import cv2

def test_set(request):
    str = get_code()
    cache.set("name", str, 60)
    print(str)
    return  HttpResponse('start!!!!!')

def get_code(n=6,alpha=True):
    s = ''
    for i in range(n):
            num = random.randint(0,9)
            if alpha:
                upper_alpha = chr(random.randint(65,90))
                lower_alpha = chr(random.randint(97,122))
                num = random.choice([num,upper_alpha,lower_alpha])
            s = s + str(num)
    return s
# 随机生成code，存入redis
def test_get(request):
    str = get_code()
    cache.set("name", str, 600)
    str = "http://127.0.0.1:8000/login/?code="+cache.get("name")
    return HttpResponse(str)

def xieyi(request):
    html = get_template('input_xieyi.html')
    return HttpResponse(html.render())

def phone_xieyi(request):
    html = get_template('input_phone_xieyi.html')
    return HttpResponse(html.render())




def loginMy(request):
    if request.method=="GET":
        logout(request)
        return render(request,'login.html')
    if request.method=="POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        # 使用 Django 的 authenticate 函数验证用户
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # 登录用户，保存登录状态
            login(request,user)
            # 重定向到协议页面
            return HttpResponseRedirect('/xieyi/')
        else:
            # 登录失败，返回错误信息
            return render(request, 'login.html', {'error': '用户名或密码错误'})
def login_bak(request):
    print(cache.get("name"))
    code = request.GET.get('code')
    datadic = np.load("./datadic.npy", allow_pickle=True).item()
    print("登录code信息:"+str(datadic))
    # 如果datadic中存在code
    if datadic.get(code, 1) == 0:
        # cache.set("flag", "true", 600)
        # cache.set("name", code, 600)
        # print(code)
        # datadic[code] = 1
        # np.save("datadic", datadic)
        return HttpResponseRedirect('/xieyi/')
    else:
        if cache.get("name") is None:
                return HttpResponse("not allowed!!!!")
        else:
            if cache.get("name") == str(code):
                cache.set("flag", "true", 600)
                print(cache.get("flag") )
                return  HttpResponseRedirect('/xieyi/')
            else:
                return HttpResponse("not allowed!!!!")


def home_page_ch(request):
    print("home_page_ch接口被调用 (上传分析入口)")
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')
    try:
        # 读取最近一次上传的数据（性别、图片）
        post = PostNew.objects.latest('pub_date')
    except Exception as e:  # 修正拼写错误
        raise Http404("数据为空:" + str(e))

    template = get_template('showpage.html')

    # 恢复原本人分析链路：沿用历史 cal_rate 输出，不改原有业务口径。
    if str(post.sex) == "1":
        image_path = "/static/meinv/"
    elif str(post.sex) == "2":
        image_path = "/static/meinan/"
    else:
        image_path = ""

    try:
        output = cal_rate('.' + post.cover.url, int(post.sex))
    except Exception as e:
        print("home_page_ch: cal_rate 失败，降级展示。错误={}".format(e))
        output = None

    if output is not None:
        eye_path = output[0]
        eye_block_str = output[1]
        nose_path = output[2]
        nose_block_str = output[3]
        lip_path = output[4]
        lip_block_str = output[5]
        person_str = output[6]
        job_message = output[7]
        landmarks_json = output[8]
        color = output[9]
        address = output[10]
        index_image1 = output[11]
        index_image2 = output[12]
        image1_url = image_path + str((index_image1 % 20)) + ".jpg"
        image2_url = image_path + str((index_image2 % 20)) + ".jpg"
        wehnhedu1 = str(output[13]) + "%"
        wehnhedu2 = str(output[14]) + "%"
        face_x = output[15]
        face_y = output[16]
        avatarUrl = post.cover.url[:-4] + "_400" + post.cover.url[-4:]
        generate_report(
            backgroundUrl="./static/picture/report.png",
            avatarUrl='.' + avatarUrl,
            qrcodeUrl="./static/picture/qrcode.png",
            couple_1_Url="." + image1_url,
            couple_2_Url="." + image2_url,
            astr_lucky_color=color,
            astr_lucky_location=address,
            astr_doing=job_message,
            astr_eye=eye_block_str,
            astr_nose=nose_block_str,
            astr_mouth=lip_block_str,
            astr_all=person_str,
            match_rate_1=str(output[13]) + "%",
            match_rate_2=str(output[14]) + "%",
            x=face_x,
            y=face_y,
        )
    else:
        avatarUrl = post.cover.url
        eye_path = ""
        eye_block_str = ""
        nose_path = ""
        nose_block_str = ""
        lip_path = ""
        lip_block_str = ""
        person_str = ""
        job_message = ""
        color = ""
        address = ""

    ideal_partner_image_data_urls = request.session.get("ideal_partner_image_data_urls", [])
    if not isinstance(ideal_partner_image_data_urls, list):
        ideal_partner_image_data_urls = []
    if not ideal_partner_image_data_urls:
        legacy_data_url = request.session.get("ideal_partner_image_data_url", "")
        if legacy_data_url:
            ideal_partner_image_data_urls = [legacy_data_url]
    ideal_partner_image_data_url = ideal_partner_image_data_urls[0] if ideal_partner_image_data_urls else ""
    ideal_partner_image_tip = "正在生成正缘长相，请稍候。"

    # 修正性别反逻辑，确保男用户传入“女”，女用户传入“男”
    sex_label = "男" if str(post.sex) == "1" else ("女" if str(post.sex) == "2" else "未知")
    if str(post.sex) == "1":
        expected_partner_sex = "女"
    elif str(post.sex) == "2":
        expected_partner_sex = "男"
    else:
        expected_partner_sex = "未知"
    age_group = request.session.get("age_group", "")
    user_context = {
        "user_sex": sex_label,
        "expected_partner_sex": expected_partner_sex,
        "user_age_group": age_group,
        "user_eye_insight": eye_block_str,
        "user_nose_insight": nose_block_str,
        "user_lip_insight": lip_block_str,
        "user_personality_summary": person_str,
        "note": "基于本人分析动态生成三候选正缘画像prompt",
    }

    ideal_partner = request.session.get("ideal_partner_profile_json", {})
    if not isinstance(ideal_partner, dict) or not ideal_partner:
        random_pack = request.session.get("ideal_prompt_random_pack", {})
        ideal_partner = generate_ideal_partner_profile(user_context, random_pack=random_pack)
        if ideal_partner:
            request.session["ideal_partner_profile_json"] = ideal_partner
            if isinstance(ideal_partner.get("random_pack"), dict):
                request.session["ideal_prompt_random_pack"] = ideal_partner.get("random_pack")

    if ideal_partner:
        ideal_display_text = ideal_partner.get("display_text", "")
        ideal_visual_prompts = ideal_partner.get("visual_prompts", [])
        if not isinstance(ideal_visual_prompts, list):
            ideal_visual_prompts = []
        if not ideal_visual_prompts:
            fallback_prompt = ideal_partner.get("visual_prompt", "")
            if fallback_prompt:
                ideal_visual_prompts = [fallback_prompt]

        ideal_visual_prompt = ideal_visual_prompts[0] if ideal_visual_prompts else ""
        request.session["ideal_visual_prompts"] = ideal_visual_prompts
        request.session["ideal_visual_prompt"] = ideal_visual_prompt

        print("================ 理想伴侣 / 正缘 LLM 输出 ================")
        print("[display_text]\n{}".format(ideal_display_text))
        print("\n[visual_prompts]")
        for idx, p in enumerate(ideal_visual_prompts[:3]):
            print(f"Prompt {idx+1}: {p}")
        print("\n[full_json]\n{}".format(json.dumps(ideal_partner, ensure_ascii=False, indent=2)))
        print("================  理想伴侣 / 正缘 输出结束  ================")

        # 首次进入页面时尝试生成三候选；失败后由前端按钮/轮询调用轻量接口重试。
        if not ideal_partner_image_data_urls and ideal_visual_prompts:
            for idx, prompt in enumerate(ideal_visual_prompts[:3]):
                print(f"[正缘生图] 开始生成第{idx+1}个候选，Prompt: {prompt}")
                ideal_image_result = generate_ideal_partner_image(
                    prompt=prompt,
                    resolution="1024:1024",
                )
                data_url = ideal_image_result.get("data_url", "")
                if data_url:
                    ideal_partner_image_data_urls.append(data_url)
                    print(f"[正缘生图] 第{idx+1}个候选生成成功，已上传到web。")
                else:
                    print(f"[正缘生图] 第{idx+1}个候选生成失败。")

            if ideal_partner_image_data_urls:
                request.session["ideal_partner_image_data_urls"] = ideal_partner_image_data_urls
                request.session["ideal_partner_image_data_url"] = ideal_partner_image_data_urls[0]
                ideal_partner_image_data_url = ideal_partner_image_data_urls[0]
                ideal_partner_image_tip = "正缘候选画像已生成（{}/3）。".format(len(ideal_partner_image_data_urls))
            else:
                ideal_partner_image_tip = "正在生成正缘长相，请稍候。"
        elif ideal_partner_image_data_urls:
            ideal_partner_image_tip = "正缘候选画像已生成（{}/3）。".format(len(ideal_partner_image_data_urls))
    else:
        ideal_display_text = ""
        ideal_visual_prompts = []
        ideal_visual_prompt = ""

    # 传递当前作用域中的所有变量，并确保三条prompt传递给前端
    html = template.render({
        **locals(),
        "ideal_visual_prompts": ideal_visual_prompts if 'ideal_visual_prompts' in locals() else [],
    })
    return HttpResponse(html)


def ideal_image_status_api(request):
    """仅检查/生成正缘图片，不触发完整分析流程。"""
    if not request.user.is_authenticated:
        return JsonResponse({"status": "unauthorized", "message": "请先登录"}, status=401)

    data_urls = request.session.get("ideal_partner_image_data_urls", [])
    if not isinstance(data_urls, list):
        data_urls = []

    if not data_urls:
        cached_data_url = request.session.get("ideal_partner_image_data_url", "")
        if cached_data_url:
            data_urls = [cached_data_url]

    prompts = request.session.get("ideal_visual_prompts", [])
    if not isinstance(prompts, list):
        prompts = []
    if not prompts:
        legacy_prompt = request.session.get("ideal_visual_prompt", "")
        if legacy_prompt:
            prompts = [legacy_prompt]

    target_count = min(3, len(prompts)) if prompts else 0

    if target_count and len(data_urls) >= target_count:
        return JsonResponse({
            "status": "ready",
            "data_urls": data_urls[:target_count],
            "data_url": data_urls[0],
            "count": target_count,
        })

    if not prompts:
        return JsonResponse({"status": "waiting", "message": "尚未生成可用的正缘提示词"})

    for idx in range(len(data_urls), min(3, len(prompts))):
        print(f"[正缘生图API] 开始生成第{idx+1}个候选，Prompt: {prompts[idx]}")
        result = generate_ideal_partner_image(prompt=prompts[idx], resolution="1024:1024")
        data_url = result.get("data_url", "")
        if data_url:
            data_urls.append(data_url)
            print(f"[正缘生图API] 第{idx+1}个候选生成成功，已上传到web。")
        else:
            print(f"[正缘生图API] 第{idx+1}个候选生成失败。")

    if data_urls:
        request.session["ideal_partner_image_data_urls"] = data_urls
        request.session["ideal_partner_image_data_url"] = data_urls[0]

    if target_count and len(data_urls) >= target_count:
        return JsonResponse({
            "status": "ready",
            "data_urls": data_urls[:target_count],
            "data_url": data_urls[0],
            "count": target_count,
        })

    if data_urls:
        return JsonResponse({
            "status": "waiting",
            "message": "候选画像生成中（{}/{}）".format(len(data_urls), max(1, min(3, len(prompts)))),
            "data_urls": data_urls,
            "count": len(data_urls),
        })

    return JsonResponse({"status": "failed", "message": "混元接口未返回图片，请查看终端日志"})

def home_page_ch_bak(request):
    if cache.get("flag") is None :
        return  HttpResponseRedirect('/login/')
    else:
        if cache.get("flag") == "true":
            try:
                post = PostNew.objects.latest('pub_date')
                if str(post.sex) == "1":
                    image_path = "/static/meinv/"
                elif str(post.sex) == "2":
                    image_path= "/static/meinan/"
                else:
                    image_path=""
                print(post.sex)
            except Exception as e:  # 修正拼写错误
                raise Http404("数据为空:"+str(e))
            # if ("Chinese" == post.language):
            template = get_template('showpage.html')
            # print(post.language)
        
            try:
                output = cal_rate('.' + post.cover.url)
            except :
                raise Http404("图片没找到！")
            if output != None:
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
                avatarUrl = post.cover.url[:-4]+"_400"+post.cover.url[-4:]
                print(avatarUrl)
                print('.' + post.cover.url)
                generate_report(backgroundUrl="./static/picture/report.png",
                                avatarUrl='.' + avatarUrl,
                                qrcodeUrl="./static/picture/qrcode.png",
                                couple_1_Url="."+image1_url,
                                couple_2_Url="."+image2_url,
                                astr_lucky_color=color,
                                astr_lucky_location=address,
                                astr_doing=job_message,
                                astr_eye=eye_block_str,
                                astr_nose=nose_block_str,
                                astr_mouth=lip_block_str,
                                astr_all=person_str,
                                match_rate_1=str(output[13]) + "%",
                                match_rate_2=str(output[14]) + "%",
                                x=face_x,
                                y=face_y)
            html = template.render(locals())
            return HttpResponse(html)
        else:
            return  HttpResponseRedirect('/login/')


def home_page_en(request):
    try:
        post = PostNew.objects.order_by('-pub_date')[0]
    except PostNew.DoseNotExit:
        raise Http404("数据为空")
    # if ("Chinese" == post.language):
    template = get_template('showpage_en.html')
    try:
        output = cal_rate('.' + post.cover.url)
    except:
        raise Http404("图片没找到！")
    if output != None:
        eye_path = output[0]
        eye_block_str = output[1]
        nose_path = output[2]
        nose_block_str = output[3]
        lip_path = output[4]
        lip_block_str = output[5]
        person_str = output[6]
        job_message = output[7]
        landmarks_json = output[8]

    html = template.render(locals())
    return HttpResponse(html)

def home_phone_page(request):
    if cache.get("flag") is None :
        return  HttpResponseRedirect('/login/')
    else:
        if cache.get("flag") == "true":
            try:
                post = PostNew.objects.order_by('-pub_date')[0]
                if str(post.sex) == "1":
                    image_path = "/static/meinv/"
                elif str(post.sex) == "2":
                    image_path= "/static/meinan/"
                else:
                    image_path=""
                print(post.sex)
            except PostNew.DoseNotExit:
                raise Http404("数据为空")
            # if ("Chinese" == post.language):
            template = get_template('show_phone.html')
            # print(post.language)
            try:
                output = cal_rate('.' + post.cover.url)
            except:
                raise Http404("图片没找到！")
            if output != None:
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
                avatarUrl = post.cover.url[:-4] + "_400" + post.cover.url[-4:]
                print(avatarUrl)
                print('.' + post.cover.url)
                generate_report(backgroundUrl="./static/picture/report.png",
                                avatarUrl= '.' +avatarUrl,
                                qrcodeUrl="./static/picture/qrcode.png",
                                couple_1_Url="." + image1_url,
                                couple_2_Url="." + image2_url,
                                astr_lucky_color=color,
                                astr_lucky_location=address,
                                astr_doing=job_message,
                                astr_eye=eye_block_str,
                                astr_nose=nose_block_str,
                                astr_mouth=lip_block_str,
                                astr_all=person_str,
                                match_rate_1=str(output[13]) + "%",
                                match_rate_2=str(output[14]) + "%",
                                x=face_x,
                                y=face_y)
            html = template.render(locals())
            return HttpResponse(html)
        else:
            return HttpResponseRedirect('/login/')



def home_phone_pipei(request):

    try:
        post = PostNewImage.objects.order_by('-pub_date')[0]
        # if str(post.sex) == "1":
            # image_path = "/static/meinv/"
        # elif str(post.sex) == "2":
            # image_path= "/static/meinan/"
        # else:
            # image_path=""
        # print(post.sex)
    except PostNewImage.DoseNotExit:
        raise Http404("数据为空")
    # if ("Chinese" == post.language):
    template = get_template('showpage_pipei.html')
    # print(post.language)
    print("sbsbsbsb")
    print(post.cover1.url)
    try:
        output1 = cal_pipei('.' + post.cover1.url,number=0)
        print("dasdasda")
        output2 = cal_pipei('.' + post.cover2.url,number=1)
    except:
        raise Http404("图片没找到！")
    if output1 != None and output2 !=None:
        fenshu1 = output1[0]
        yuju1 = output1[1]
        fenshu2 = output2[0]
        yuju2 = output2[1]
        avatarUrl1 = post.cover1.url[:-4]+"_400"+post.cover2.url[-4:]
        avatarUrl2 = post.cover2.url[:-4]+"_400"+post.cover2.url[-4:]

    html = template.render(locals())
    return HttpResponse(html)

def input_ch(request):
    # 用户未登录
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')
    # 用户已登录
    # GET访问网页
    if request.method == "GET":
        html = get_template('input_ch.html')
        return HttpResponse(html.render())
    # 如果提交表单，重定向
    if request.method == "POST":
        author_sex = request.POST["sex"]
        age_group = request.POST.get("age_group", "")
        image_name = request.FILES.get('cover')
        print(image_name)
        post = PostNew()
        post.cover = image_name
        post.sex = author_sex
        post.save()
        # 将年龄段暂存到 session，便于后续 LLM 使用
        request.session["age_group"] = age_group
        # 新图上传后清空上一次的正缘缓存，避免显示旧图。
        request.session.pop("ideal_visual_prompt", None)
        request.session.pop("ideal_visual_prompts", None)
        request.session.pop("ideal_prompt_random_pack", None)
        request.session.pop("ideal_partner_profile_json", None)
        request.session.pop("ideal_partner_image_data_url", None)
        request.session.pop("ideal_partner_image_data_urls", None)
        return HttpResponseRedirect('/home_ch/')
    # else:
    #     html = get_template('input_ch.html')
    #     return HttpResponse(html.render())

def input_ch_bak(request):
    if cache.get("flag") is None :
        return  HttpResponseRedirect('/login/')
    else:
        if cache.get("flag") == "true":
            # GET访问网页
            if request.method == "GET":
                html = get_template('input_ch.html')
                return HttpResponse(html.render())
            # 如果提交表单，重定向
            if request.method == "POST":
                author_sex = request.POST["sex"]
                image_name = request.FILES.get('cover')
                print(image_name)
                post = PostNew()
                post.cover = image_name
                post.sex = author_sex
                post.save()
                return HttpResponseRedirect('/home_ch/')
            else:
                html = get_template('input_ch.html')
                return HttpResponse(html.render())
        else:
            return HttpResponseRedirect('/login/')

def phone_ch(request):
    if cache.get("flag") is None :
        return  HttpResponseRedirect('/login/')
    else:
        if cache.get("flag") == "true":
            if request.method == "GET":
                html = get_template('input_phone.html')
                return HttpResponse(html.render())
            if request.method == "POST":
                author_sex = request.POST["sex"]
                age_group = request.POST.get("age_group", "")
                image_name = request.FILES.get('cover')
                print(image_name)
                post = PostNew()
                post.cover = image_name
                post.sex = author_sex
                post.save()
                # 将年龄段暂存到 session，便于后续 LLM 使用
                request.session["age_group"] = age_group
                request.session.pop("ideal_visual_prompt", None)
                request.session.pop("ideal_visual_prompts", None)
                request.session.pop("ideal_prompt_random_pack", None)
                request.session.pop("ideal_partner_profile_json", None)
                request.session.pop("ideal_partner_image_data_url", None)
                request.session.pop("ideal_partner_image_data_urls", None)
                return HttpResponseRedirect('/home_phone/')
            else:
                html = get_template('input_phone.html')
                return HttpResponse(html.render())
        else:
            return HttpResponseRedirect('/login/')

def input_pipei(request):
    # if cache.get("flag") is None :
    #     return  HttpResponseRedirect('/login/')
    # else:
    # if cache.get("flag") == "true":
    if request.method == "GET":
        html = get_template('input_pipei.html')
        return HttpResponse(html.render())
    if request.method == "POST":
        # author_sex = request.POST["sex"]
        image_name1 = request.FILES.get('cover1')
        image_name2 = request.FILES.get('cover2')
        print(image_name1)
        print(image_name2)
        post = PostNewImage()
        post.cover1 = image_name1
        post.cover2 = image_name2
        post.save()
        return HttpResponseRedirect('/pipei_home/')
    else:
        html = get_template('input_pipei.html')
        return HttpResponse(html.render())
        # else:
        #     return HttpResponseRedirect('/login/')

def download(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')
    path = "./out.png"
    print(path)
    with open(path, 'rb') as fr:
        response = HttpResponse(fr.read())
        response['Content-Type'] = 'image/png'
        current_time = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
        file_name = str(current_time) + ".png"
        response['Content-Disposition'] = "attachment;filename={}".format(escape_uri_path(file_name))
    return response

def download_bak(request):
    if cache.get("flag") is None :
        return  HttpResponseRedirect('/login/')
    else:
        if cache.get("flag") == "true":
            path = "./out.png"
            print(path)
            with open(path, 'rb') as fr:
                response = HttpResponse(fr.read())
                response['Content-Type'] = 'image/png'
                current_time = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
                file_name = str(current_time)+".png"
                response['Content-Disposition'] = "attachment;filename={}".format(escape_uri_path(file_name))
            return response

        else:
            return HttpResponseRedirect('/login/')

# class CreatePostViewCh(CreateView):  # new
#     model = PostNew
#     form_class = PostNewForm
#     template_name = 'input_ch.html'
#     print("zhunahua!!!!!!!")
#     success_url = reverse_lazy('home_ch')
#
#
# class CreatePostViewEn(CreateView):  # new
#     model = Post
#     form_class = PostPhoneForm
#     template_name = 'input_en.html'
#     print("zhunahua!!!!!!!")
#     success_url = reverse_lazy('home_en')
#
#
# class PhonePostViewCh(CreateView):  # new
#     model = PostNew
#     form_class = PostNewForm
#     template_name = 'input_phone.html'
#     success_url = reverse_lazy('home_phone')
#
#
# class PhonePostViewEn(CreateView):  # new
#     model = Post
#     form_class = PostPhoneForm
#     template_name = 'input_phone_en.html'
#     success_url = reverse_lazy('home_phone_en')


import os
import cv2
import dlib
import numpy as np
from .models import FaceFeature
def saveDB(request):
    detector = dlib.get_frontal_face_detector()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(current_dir)
    dat_path = os.path.join(base_dir, 'face', 'shape_predictor_68_face_landmarks.dat')
    predictor = dlib.shape_predictor(dat_path)

    # 图片文件夹路径r'C:\Users\29443\Desktop\django\Tellyourfortune\static\match\Male'
    folder_path = os.path.join('static','match', 'Male')
    # 遍历文件夹，处理所有图片文件
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        # 确保是图片文件，后缀名可以根据实际情况进行调整
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            print("正在处理: {}".format(filename))

            # 读取图片
            img_old = cv2.imread(file_path)

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

            # 转为灰度图像
            img_gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)

            # 检测人脸
            rects = detector(img_gray, 1)
            if len(rects) == 1:
                for i, face in enumerate(rects):
                    # 获取人脸的边界框
                    landmarks = np.matrix([[p.x, p.y] for p in predictor(img_resized, rects[0]).parts()])
                    landmarks_list = landmarks.tolist()
                    relative_landmarks = []
                    first_x, first_y = landmarks_list[0]  # 获取第一个坐标的 x 和 y
                    for (x, y) in landmarks_list:
                        relative_x = x - first_x  # 转换为相对坐标
                        relative_y = y - first_y
                        relative_landmarks.append([relative_x, relative_y])

                    # 假设默认性别为 1（男性），如果需要可以调整
                    sex = 1
                    # 保存 FaceFeature 数据
                    faceDB = FaceFeature(sex=sex, image='match/Male/'+filename)
                    faceDB.set_landmarks(relative_landmarks)
                    faceDB.save()

                    # 打印相对坐标
                    print("relative_landmarks for {}: {}".format(filename, relative_landmarks))
            else:
                print("图片 {} 的人脸识别失败，未找到人脸。".format(filename))
        else:
            print("{} 不是有效的图片文件，跳过。".format(filename))

    print("所有图片处理完成！")
    return None


def styleGanSave(request):
    # generator = StyleGANImageGenerator(
    #     network_pkl=r'C:\Users\29443\Desktop\django\Tellyourfortune\stygan\ffhq.pkl',
    #     outdir='./output',
    #     truncation_psi=0.7
    # )
    # generator.generate_images(seeds=list(range(1,1001)))
    global sex
    detector = dlib.get_frontal_face_detector()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(current_dir)
    dat_path = os.path.join(base_dir, 'face', 'shape_predictor_68_face_landmarks.dat')
    predictor = dlib.shape_predictor(dat_path)

    # 图片文件夹路径r'C:\Users\29443\Desktop\django\Tellyourfortune\static\match\Male'
    folder_path = os.path.join('output')
    # 遍历文件夹，处理所有图片文件
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        print("正在路径: {}".format(file_path))
        # 确保是图片文件，后缀名可以根据实际情况进行调整
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            print("正在处理: {}".format(filename))
            seed = os.path.splitext(filename)[0]
            # 读取图片
            img_old = cv2.imread(file_path)

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

            # 转为灰度图像
            img_gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)

            # 检测人脸
            rects = detector(img_gray, 1)
            if len(rects) == 1:
                for i, face in enumerate(rects):
                    # 获取人脸的边界框
                    landmarks = np.matrix([[p.x, p.y] for p in predictor(img_resized, rects[0]).parts()])
                    landmarks_list = landmarks.tolist()
                    relative_landmarks = []
                    first_x, first_y = landmarks_list[0]  # 获取第一个坐标的 x 和 y
                    for (x, y) in landmarks_list:
                        relative_x = x - first_x  # 转换为相对坐标
                        relative_y = y - first_y
                        relative_landmarks.append([relative_x, relative_y])
                    try:
                        objs = DeepFace.analyze(
                            img_path=file_path,
                            actions=['gender']
                        )
                        woman = objs[0]['gender']['Woman']
                        man = objs[0]['gender']['Man']
                        if woman > man:
                            sex = 0
                        else:
                            sex = 1
                        print("分析结果：", objs)
                    except Exception as e:
                        print("发生未知错误：", e)
                        break
                    print(sex)
                    # # 保存 FaceFeature 数据
                    faceDB = SeedToFace(sex=sex,seed = seed)
                    faceDB.set_landmarks(relative_landmarks)
                    faceDB.save()

                    # 打印相对坐标
                    print("relative_landmarks for {}: {}".format(filename, relative_landmarks))
            else:
                print("图片 {} 的人脸识别失败，未找到人脸。".format(filename))
        else:
            print("{} 不是有效的图片文件，跳过。".format(filename))

    print("所有图片处理完成！")
    return None
