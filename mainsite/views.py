print("views.py loaded (模块已加载)")
import random
import json
import re
import os
from datetime import date
from html import escape

from deepface import DeepFace
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView, CreateView  # new
from django.urls import reverse_lazy  # new

from ai import DashScopeChat, generate_ideal_partner_profile, generate_ideal_partner_image, generate_bazi_analysis
from stygan import StyleGANImageGenerator
from .forms import PostForm, PostPhoneForm  # new
from .models import Post, PostNew, PostNewImage, FaceFeature, SeedToFace
from .bazi_skill import build_bazi_profile

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


REQUIRED_BAZI_PROFILE_KEYS = [
    "bazi_str",
    "year_pillar",
    "month_pillar",
    "day_pillar",
    "time_pillar",
    "wuxing_summary",
    "lunar_birth_text",
    "current_year_ganzhi",
    "next_year_ganzhi",
    "current_dayun_ganzhi",
    "flow_year_stem_compare",
    "flow_year_branch_compare",
    "flow_dayun_effect",
]


STAR_SIGNS = [
    {
        "name": "星纪",
        "palace": "摩羯宫",
        "start": (12, 7),
        "end": (1, 5),
        "lunar_range_text": "农历12月7日-1月5日",
        "quote": "“上当星纪，下裂坤维。”",
        "quote_source": "——唐·王勃《广州宝庄严寺舍利塔》",
        "personality": "日月五星轮回的终始，故称“星纪”。作为十二星次的出发点，有根基的含义。信念坚强而勤奋，会朝着自己的目标努力不懈。生性温柔，但若发起脾气，也是势不可挡的。",
        "svg": "星纪.svg",
    },
    {
        "name": "玄枵",
        "palace": "水瓶宫",
        "start": (1, 6),
        "end": (2, 3),
        "lunar_range_text": "农历1月6日-2月3日",
        "quote": "“自须女八度至危十五度为玄枵，於辰在子，齐之分野，属青州。”",
        "quote_source": "——《晋书·天文志上》",
        "personality": "有种子的含义，兼具发展性和神秘感。好奇心旺盛，性格开朗、乐观，兴趣广泛。但同时缺乏耐心，善变，对一件事物的热情不会太持久。",
        "svg": "玄枵.svg",
    },
    {
        "name": "娵訾",
        "palace": "双鱼宫",
        "start": (2, 4),
        "end": (3, 5),
        "lunar_range_text": "农历2月4日-3月5日",
        "quote": "“及其亡也，岁在娵訾之口。”",
        "quote_source": "——《左传·襄公三十年》",
        "personality": "代表植物的核，意指中心。个性强，注重自我。外表冷漠内心却十分热情，而且具有恒心和毅力，一旦决定了某件事，便会以坚强的意志坚持到底。不过这种坚强可能会导致过于自我。",
        "svg": "娵訾.svg",
    },
    {
        "name": "降娄",
        "palace": "白羊宫",
        "start": (3, 6),
        "end": (4, 4),
        "lunar_range_text": "农历3月6日-4月4日",
        "quote": "“自奎五度至胃六度为降娄，於辰在戌，鲁之分野，属徐州。”",
        "quote_source": "——《晋书·天文志上》",
        "personality": "代表植物的茎，像茎向植物无私地输送养分一般，是一个为他人无私奉献的人。性格直率，乐于助人，但容易过于听从别人的想法而失去主见。",
        "svg": "降娄.svg",
    },
    {
        "name": "大梁",
        "palace": "金牛宫",
        "start": (4, 5),
        "end": (5, 5),
        "lunar_range_text": "农历4月5日-5月5日",
        "quote": "“岁在大梁，将集天行。”",
        "quote_source": "——《国语·晋语四》",
        "personality": "象征植物积蓄能量而生长，有结实的意思。头脑灵活，有先见之明，善于规划。但也会比较现实而精于算计。",
        "svg": "大梁.svg",
    },
    {
        "name": "实沈",
        "palace": "双子宫",
        "start": (5, 6),
        "end": (6, 5),
        "lunar_range_text": "农历5月6日-6月5日",
        "quote": "“岁在大梁，将集天行，元年始受实沈之星也。”",
        "quote_source": "——《国语·晋语四》",
        "personality": "代表伸缩自如的柔软性，象征植物的枝条。有韧性，善于随机应变。但有时会缺乏踏实的努力，天赋需要真正的磨练才能转化为才能。",
        "svg": "实沈.svg",
    },
    {
        "name": "鹑首",
        "palace": "巨蟹宫",
        "start": (6, 6),
        "end": (7, 6),
        "lunar_range_text": "农历6月6日-7月6日",
        "quote": "“天文家‘朱鸟’，乃取象於鹑。故南方朱鸟七宿，曰鹑首、鹑火、鹑尾是也。”",
        "quote_source": "——宋·沈括《梦溪笔谈·象数一》",
        "personality": "象征着宁静。沉稳温和，总给人很有内涵而且略有神秘感的印象。外冷内热，有包容力和涵养。但有时会过于计较。",
        "svg": "鹑首.svg",
    },
    {
        "name": "鹑火",
        "palace": "狮子宫",
        "start": (7, 7),
        "end": (8, 7),
        "lunar_range_text": "农历7月7日-8月7日",
        "quote": "“岁在鹑火，是以卒灭。”",
        "quote_source": "——《左传·昭公八年》",
        "personality": "代表不死鸟的心脏，具有燃烧的生命力。精力充沛，热情四溢，毫不做作。但也是典型的忽冷忽热的性格。",
        "svg": "鹑火.svg",
    },
    {
        "name": "鹑尾",
        "palace": "室女宫",
        "start": (8, 8),
        "end": (9, 7),
        "lunar_range_text": "农历8月8日-9月7日",
        "quote": "“岁在寿星及鹑尾，其有此土乎！”",
        "quote_source": "——《国语·晋语四》",
        "personality": "代表着坚实地生长在大地中的根。性格会如同土地中的根一样，坚强而深不可测。外表冷峻，内心温柔，想象力丰富，但有时会不切实际。",
        "svg": "鹑尾.svg",
    },
    {
        "name": "寿星",
        "palace": "天秤宫",
        "start": (9, 8),
        "end": (10, 7),
        "lunar_range_text": "农历9月8日-10月7日",
        "quote": "“东宫则析木之津，寿星之野。”",
        "quote_source": "——唐·杨炯《浑天赋》",
        "personality": "福寿双全之命格，表面上慵懒，但一旦有了目标，就会充满热情地开始实干。但这种热情，往往难以持久，而且不喜欢团体活动。",
        "svg": "寿星.svg",
    },
    {
        "name": "大火",
        "palace": "天蝎宫",
        "start": (10, 8),
        "end": (11, 8),
        "lunar_range_text": "农历10月8日-11月8日",
        "quote": "“大火谓之大辰。”",
        "quote_source": "——《尔雅·释天》",
        "personality": "代表早晨温暖的阳光。给别人的感觉十分温暖，性格安宁恬静而深得大家喜爱，爱家顾家。但容易优柔寡断。",
        "svg": "大火.svg",
    },
    {
        "name": "析木",
        "palace": "射手宫",
        "start": (11, 9),
        "end": (12, 6),
        "lunar_range_text": "农历11月9日-12月6日",
        "quote": "“日月会於析木兮，重阴凄而增肃。”",
        "quote_source": "——晋·傅玄《大寒赋》",
        "personality": "代表着拦截天河的木栅。意志坚强，直面逆境，勤奋上进。但有时一腔热血和不喜欢束缚也意味着固执。",
        "svg": "析木.svg",
    },
]


def _lunar_md_to_key(month, day):
    return int(month) * 100 + int(day)


def _star_sign_match(month, day, item):
    cur = _lunar_md_to_key(month, day)
    start = _lunar_md_to_key(item["start"][0], item["start"][1])
    end = _lunar_md_to_key(item["end"][0], item["end"][1])
    if start <= end:
        return start <= cur <= end
    return cur >= start or cur <= end


def _extract_lunar_month_day(bazi_profile):
    if not isinstance(bazi_profile, dict):
        return None

    lunar_birth_text = str(bazi_profile.get("lunar_birth_text", "")).strip()
    if lunar_birth_text:
        # 先尝试直接从已有农历文本提取，避免对运行环境中的 lunar_python 产生硬依赖。
        m = re.search(r"(\d{1,2})\s*月\s*(\d{1,2})\s*日", lunar_birth_text)
        if m:
            return int(m.group(1)), int(m.group(2))

        cn_month_map = {
            "正": 1,
            "一": 1,
            "二": 2,
            "三": 3,
            "四": 4,
            "五": 5,
            "六": 6,
            "七": 7,
            "八": 8,
            "九": 9,
            "十": 10,
            "冬": 11,
            "十一": 11,
            "腊": 12,
            "十二": 12,
        }

        def _cn_day_to_int(day_text):
            day_map = {
                "初一": 1,
                "初二": 2,
                "初三": 3,
                "初四": 4,
                "初五": 5,
                "初六": 6,
                "初七": 7,
                "初八": 8,
                "初九": 9,
                "初十": 10,
                "十一": 11,
                "十二": 12,
                "十三": 13,
                "十四": 14,
                "十五": 15,
                "十六": 16,
                "十七": 17,
                "十八": 18,
                "十九": 19,
                "二十": 20,
                "廿一": 21,
                "廿二": 22,
                "廿三": 23,
                "廿四": 24,
                "廿五": 25,
                "廿六": 26,
                "廿七": 27,
                "廿八": 28,
                "廿九": 29,
                "三十": 30,
            }
            return day_map.get(day_text)

        cn_match = re.search(r"([正一二三四五六七八九十冬腊]{1,2})月([初十廿一二三四五六七八九]{2})", lunar_birth_text)
        if cn_match:
            month_text = cn_match.group(1)
            day_text = cn_match.group(2)
            month_val = cn_month_map.get(month_text)
            day_val = _cn_day_to_int(day_text)
            if month_val and day_val:
                return month_val, day_val

    birth_date_text = str(bazi_profile.get("birth_date", "")).strip()
    birth_hour = bazi_profile.get("birth_hour", 12)
    if not birth_date_text:
        return None
    try:
        y, m, d = [int(x) for x in birth_date_text.split("-")]
    except Exception:
        return None

    try:
        from lunar_python import Solar  # type: ignore

        solar = Solar.fromYmdHms(y, m, d, int(birth_hour), 0, 0)
        lunar = solar.getLunar()
        lunar_month = abs(int(lunar.getMonth()))
        lunar_day = int(lunar.getDay())
        return lunar_month, lunar_day
    except Exception:
        return None


def _build_star_sign_context(bazi_profile):
    lunar_md = _extract_lunar_month_day(bazi_profile)
    if not lunar_md:
        return None

    lunar_month, lunar_day = lunar_md
    for item in STAR_SIGNS:
        if not _star_sign_match(lunar_month, lunar_day, item):
            continue
        return {
            "name": item["name"],
            "palace": item["palace"],
            "title_line": "【{}】- {}".format(item["name"], item["palace"]),
            "lunar_range_text": item["lunar_range_text"],
            "quote": item["quote"],
            "quote_source": item["quote_source"],
            "personality": item["personality"],
            "svg_url": "/media/stars/{}".format(item["svg"]),
        }
    return None


def _bazi_profile_needs_recompute(profile):
    if not isinstance(profile, dict) or not profile:
        return True
    for key in REQUIRED_BAZI_PROFILE_KEYS:
        value = profile.get(key)
        if value is None:
            return True
        if isinstance(value, str) and not value.strip():
            return True
        if isinstance(value, list) and not value:
            return True
    return False


def _log_bazi_profile_json(profile):
    if not isinstance(profile, dict) or not profile:
        print("[BaziProfileJSON] empty=true")
        return
    print("[BaziProfileJSON] keys={}".format(",".join(sorted(profile.keys()))))
    print("[BaziProfileJSON] full={}".format(json.dumps(profile, ensure_ascii=False)))


def _log_bazi_analysis_json(analysis):
    if not isinstance(analysis, dict) or not analysis:
        print("[BaziAnalysisJSON] empty=true")
        return
    print("[BaziAnalysisJSON] source={}".format(analysis.get("source", "")))
    print("[BaziAnalysisJSON] source_reason={}".format(analysis.get("source_reason", "")))
    print("[BaziAnalysisJSON] full={}".format(json.dumps(analysis, ensure_ascii=False)))


def _has_duplicate_flow_lines(display_text):
    text = str(display_text or "")
    lines = [ln.strip() for ln in text.replace("\\r\\n", "\n").replace("\\n", "\n").splitlines() if ln.strip()]
    if not lines:
        return False
    prefixes = [
        "流年干支",
        "今年天干与命局天干的合冲克关系：",
        "今年地支与命局地支的合冲刑害：",
        "流年干支与当前大运干支的叠加效应：",
        "{}年（今年）：".format(date.today().year),
        "{}年（明年）：".format(date.today().year + 1),
    ]
    counts = {k: 0 for k in prefixes}
    for line in lines:
        for pref in prefixes:
            if line == pref or line.startswith(pref):
                counts[pref] += 1
                break
    return any(v > 1 for v in counts.values())


def _looks_like_template_bazi_text(display_text):
    text = str(display_text or "")
    if not text.strip():
        return True
    bad_markers = [
        "调候气象：结合",
        "次第：先命局后岁运",
        "大忌：单看一柱定全局",
        "按模板输出",
        "请逐柱比对",
        "待推导",
        "e.g.",
    ]
    return any(m in text for m in bad_markers)


def _remove_html_tags(text):
    """去除文本中的HTML标签"""
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def _normalize_bazi_lines(raw_text):
    text = str(raw_text or "").replace("\\r\\n", "\n").replace("\\n", "\n").strip()
    if not text:
        return []
    # 去除HTML标签
    text = _remove_html_tags(text)
    return [ln.strip() for ln in text.splitlines() if ln.strip()]


def _split_bazi_sections(raw_text):
    lines = _normalize_bazi_lines(raw_text)
    if not lines:
        return {
            "flow": [],
            "prosperity": [],
            "strategy": [],
        }

    idx_prosperity = lines.index("旺衰与定局") if "旺衰与定局" in lines else -1
    idx_strategy = lines.index("给命主的“战略箴言”") if "给命主的“战略箴言”" in lines else -1

    if idx_prosperity < 0:
        return {
            "flow": lines,
            "prosperity": [],
            "strategy": [],
        }

    flow_lines = lines[:idx_prosperity]
    if idx_strategy >= 0:
        prosperity_lines = lines[idx_prosperity:idx_strategy]
        strategy_lines = lines[idx_strategy:]
    else:
        prosperity_lines = lines[idx_prosperity:]
        strategy_lines = []

    return {
        "flow": flow_lines,
        "prosperity": prosperity_lines,
        "strategy": strategy_lines,
    }


def _format_bazi_display_html(raw_text):
    lines = _normalize_bazi_lines(raw_text)
    if not lines:
        return ""

    heading_keywords = ["流年干支", "旺衰与定局", "给命主的“战略箴言”"]
    inline_title_prefix = ["生辰（农历）：", "四柱：", "五行："]
    html_parts = []
    for line in lines:
        line_no_dash = re.sub(r"^[-•]\s*", "", line)
        if line_no_dash == "☼八字排盘解析":
            # 页面标题已在模板单独显示，正文中不重复。
            continue

        matched_prefix = ""
        for pref in inline_title_prefix:
            if line_no_dash.startswith(pref):
                matched_prefix = pref
                break

        if matched_prefix:
            suffix = line_no_dash[len(matched_prefix):].strip()
            if matched_prefix == "生辰（农历）：" and "虚岁：" in suffix:
                lunar_text, nominal_age_text = suffix.split("虚岁：", 1)
                html_parts.append(
                    '<div class="bazi-inline"><span class="bazi-heading-inline">{}</span><span class="bazi-body-inline">{}</span><span class="bazi-heading-inline">虚岁：</span><span class="bazi-body-inline">{}</span></div>'.format(
                        escape(matched_prefix),
                        escape(lunar_text.strip()),
                        escape(nominal_age_text.strip()),
                    )
                )
                continue
            html_parts.append(
                '<div class="bazi-inline"><span class="bazi-heading-inline">{}</span><span class="bazi-body-inline">{}</span></div>'.format(
                    escape(matched_prefix),
                    escape(suffix),
                )
            )
            continue

        if any(line_no_dash == k for k in heading_keywords):
            css_class = "bazi-heading"
        else:
            css_class = "bazi-body"
        html_parts.append('<div class="{}">{}</div>'.format(css_class, escape(line_no_dash)))
    return "".join(html_parts)

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
            # 设置缓存 flag，允许访问 /phone_ch/ 和 /ch/ 等页面
            cache.set("flag", "true", 600)
            # 检测是否为移动设备
            ua = request.META.get('HTTP_USER_AGENT', '').lower()
            is_mobile = any(mobile in ua for mobile in ['android', 'iphone', 'ipad', 'blackberry'])
            if is_mobile:
                # 移动设备跳转到手机版协议页面
                return HttpResponseRedirect('/phone_xieyi/')
            else:
                # 桌面设备跳转到桌面版协议页面
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
    print("[home_page_ch] request.path =", request.path)
    if not request.user.is_authenticated:
        print("[home_page_ch] 用户未登录，重定向到login")
        return HttpResponseRedirect('/login/')
    try:
        # 读取最近一次上传的数据（性别、图片）
        post = PostNew.objects.latest('pub_date')
        print("[home_page_ch] 找到最新post: ID=%s, sex=%s, cover=%s" % (post.id, post.sex, post.cover.url))
    except Exception as e:  # 修正拼写错误
        print("[home_page_ch] 获取post失败:", str(e))
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
        print("[home_page_ch] 开始分析图片: .%s, sex=%s" % (post.cover.url, post.sex))
        import sys
        sys.stdout.flush()
        output = cal_rate('.' + post.cover.url, int(post.sex))
        print("[home_page_ch] cal_rate 返回: output=%s" % ('None' if output is None else 'len=%d' % len(output)))
        sys.stdout.flush()
        if output:
            print("[home_page_ch] output[9]=color=%s, output[10]=address=%s" % (output[9], output[10]))
    except Exception as e:
        print("[home_page_ch] cal_rate 失败，降级展示。错误=%s" % e)
        import traceback
        traceback.print_exc()
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
        true_love_str = output[19] if len(output) > 19 else "正缘预测功能暂时不可用"
        # 使用原始图片URL，不再尝试使用不存在的_400压缩版本
        avatarUrl = post.cover.url
        print("[home_page_ch] 分析成功: color=%s, address=%s, job=%s" % (color, address, job_message))


        # 修正性别反逻辑
        sex_label = "男" if str(post.sex) == "1" else ("女" if str(post.sex) == "2" else "未知")
        if str(post.sex) == "1":
            expected_partner_sex = "女"
        elif str(post.sex) == "2":
            expected_partner_sex = "男"
        else:
            expected_partner_sex = "未知"
        bazi_birth_date = request.session.get("bazi_birth_date", "")
        bazi_birth_hour = request.session.get("bazi_birth_hour", "")
        age_group = request.session.get("age_group", "")

        bazi_profile = request.session.get("bazi_profile_json", {})
        if not isinstance(bazi_profile, dict):
            bazi_profile = {}

        profile_needs_recompute = _bazi_profile_needs_recompute(bazi_profile)
        if bazi_birth_date and profile_needs_recompute:
            bazi_profile = build_bazi_profile(
                birth_date_text=bazi_birth_date,
                birth_hour_value=bazi_birth_hour,
                gender=sex_label,
            )
            if bazi_profile:
                request.session["bazi_profile_json"] = bazi_profile
                request.session.pop("bazi_profile_analysis_json", None)
                print("[BaziEvidence] session_profile_recomputed=true")

        _log_bazi_profile_json(bazi_profile)

        if isinstance(bazi_profile, dict) and bazi_profile.get("age_range"):
            age_group = bazi_profile.get("age_range", age_group)

        user_context = {
            "user_sex": sex_label,
            "expected_partner_sex": expected_partner_sex,
            "user_age_group": age_group,
            "user_age": bazi_profile.get("age") if isinstance(bazi_profile, dict) else None,
            "user_age_stage": bazi_profile.get("age_stage") if isinstance(bazi_profile, dict) else "",
            "user_eye_insight": eye_block_str,
            "user_nose_insight": nose_block_str,
            "user_lip_insight": lip_block_str,
            "user_personality_summary": person_str,
            "note": "基于本人分析动态生成三候选正缘画像prompt",
        }

        # 生成八字分析
        bazi_analysis = request.session.get("bazi_profile_analysis_json", {})
        if not isinstance(bazi_analysis, dict):
            bazi_analysis = {}

        # 简单判断八字分析是否需要重新计算
        bazi_analysis_needs_recompute = not bazi_analysis or not bazi_analysis.get("display_text")
        if bazi_profile and bazi_analysis_needs_recompute:
            print("[BaziEvidence] bazi_analysis_needs_recompute=true")
            refreshed = generate_bazi_analysis(bazi_profile=bazi_profile, user_context=user_context)
            if isinstance(refreshed, dict) and refreshed.get("display_text"):
                bazi_analysis = refreshed
                request.session["bazi_profile_analysis_json"] = bazi_analysis

        bazi_display_text = ""
        bazi_display_html_flow = ""
        bazi_display_html_prosperity = ""
        bazi_display_html_strategy = ""
        bazi_text_flow = ""
        bazi_text_prosperity = ""
        bazi_text_strategy = ""
        if isinstance(bazi_analysis, dict):
            bazi_display_text = bazi_analysis.get("display_text", "")
        bazi_sections = _split_bazi_sections(bazi_display_text)
        bazi_display_html_flow = _format_bazi_display_html("\n".join(bazi_sections.get("flow", [])))
        bazi_display_html_prosperity = _format_bazi_display_html("\n".join(bazi_sections.get("prosperity", [])))
        bazi_display_html_strategy = _format_bazi_display_html("\n".join(bazi_sections.get("strategy", [])))
        # 生成纯文本版本用于报告图片
        bazi_text_flow = "\n".join(bazi_sections.get("flow", []))
        bazi_text_prosperity = "\n".join(bazi_sections.get("prosperity", []))
        bazi_text_strategy = "\n".join(bazi_sections.get("strategy", []))

        # 处理正缘 profile 和生图（先于报告生成）
        ideal_partner = request.session.get("ideal_partner_profile_json", {})
        stale_ideal_age_prompt = False
        if isinstance(ideal_partner, dict) and ideal_partner:
            cached_prompts = ideal_partner.get("visual_prompts", [])
            if not isinstance(cached_prompts, list):
                cached_prompts = []
            legacy_prompt = ideal_partner.get("visual_prompt", "")
            merged_prompt_text = " ".join([str(x) for x in cached_prompts if x]) + " " + str(legacy_prompt or "")
            if re.search(r"\d+\s*[-~到]\s*\d+\s*岁|\d+岁|18-25|26-35|36-45|45\+", merged_prompt_text):
                stale_ideal_age_prompt = True

        if stale_ideal_age_prompt:
            print("[IdealPromptEvidence] stale_age_prompt_detected=true")
            request.session.pop("ideal_partner_profile_json", None)
            request.session.pop("ideal_visual_prompt", None)
            request.session.pop("ideal_visual_prompts", None)
            request.session.pop("ideal_partner_image_data_url", None)
            request.session.pop("ideal_partner_image_data_urls", None)
            ideal_partner = {}

        if not isinstance(ideal_partner, dict) or not ideal_partner:
            random_pack = request.session.get("ideal_prompt_random_pack", {})
            ideal_partner = generate_ideal_partner_profile(user_context, random_pack=random_pack)
            if ideal_partner:
                request.session["ideal_partner_profile_json"] = ideal_partner
                if isinstance(ideal_partner.get("random_pack"), dict):
                    request.session["ideal_prompt_random_pack"] = ideal_partner.get("random_pack")

        ideal_partner_image_data_urls = request.session.get("ideal_partner_image_data_urls", [])
        if not isinstance(ideal_partner_image_data_urls, list):
            ideal_partner_image_data_urls = []
        if not ideal_partner_image_data_urls:
            legacy_data_url = request.session.get("ideal_partner_image_data_url", "")
            if legacy_data_url:
                ideal_partner_image_data_urls = [legacy_data_url]

        ideal_display_text = ""
        ideal_visual_prompts = []
        ideal_visual_prompt = ""
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

        # 先生成正缘图片用于报告
        report_couple_1_Url = "." + image1_url
        report_couple_2_Url = "." + image2_url
        if ideal_visual_prompts and len(ideal_partner_image_data_urls) < 2:
            for idx, prompt in enumerate(ideal_visual_prompts[:3]):
                if len(ideal_partner_image_data_urls) >= 2:
                    break
                print(f"[正缘生图] 开始生成第{idx+1}个候选，Prompt: {prompt}")
                ideal_image_result = generate_ideal_partner_image(prompt=prompt, resolution="1024:1024")
                data_url = ideal_image_result.get("data_url", "")
                if data_url:
                    ideal_partner_image_data_urls.append(data_url)
                    print(f"[正缘生图] 第{idx+1}个候选生成成功")
            if ideal_partner_image_data_urls:
                request.session["ideal_partner_image_data_urls"] = ideal_partner_image_data_urls
                request.session["ideal_partner_image_data_url"] = ideal_partner_image_data_urls[0]

        if len(ideal_partner_image_data_urls) >= 2:
            report_couple_1_Url = ideal_partner_image_data_urls[0]
            report_couple_2_Url = ideal_partner_image_data_urls[1]
            print("[home_page_ch] 报告使用豆包生成的图片作为对象像谁")

        ideal_partner_image_data_url = ideal_partner_image_data_urls[0] if ideal_partner_image_data_urls else ""
        ideal_partner_image_tip = "正在生成正缘长相，请稍候。" if not ideal_partner_image_data_urls else "正缘候选画像已生成（{}/3）。".format(len(ideal_partner_image_data_urls))

        try:
            generate_report(
                backgroundUrl="./static/picture/report.png",
                avatarUrl='.' + avatarUrl,
                qrcodeUrl="./static/picture/qrcode.png",
                couple_1_Url=report_couple_1_Url,
                couple_2_Url=report_couple_2_Url,
                astr_lucky_color=color,
                astr_lucky_location=address,
                astr_doing=job_message,
                astr_eye=eye_block_str,
                astr_nose=nose_block_str,
                astr_mouth=lip_block_str,
                astr_all=person_str,
                astr_true_love=ideal_display_text if ideal_display_text else true_love_str,
                astr_couple="",
                astr_bazi_flow=bazi_text_flow if 'bazi_text_flow' in dir() else "",
                astr_bazi_prosperity=bazi_text_prosperity if 'bazi_text_prosperity' in dir() else "",
                astr_bazi_strategy=bazi_text_strategy if 'bazi_text_strategy' in dir() else "",
                match_rate_1=str(output[13]) + "%",
                match_rate_2=str(output[14]) + "%",
                x=face_x,
                y=face_y,
            )
        except Exception as gen_err:
            print("[home_page_ch] generate_report 失败: %s" % gen_err)
            import traceback
            traceback.print_exc()
    else:
        print("[home_page_ch] output为None，使用空变量")
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
    bazi_birth_date = request.session.get("bazi_birth_date", "")
    bazi_birth_hour = request.session.get("bazi_birth_hour", "")
    age_group = request.session.get("age_group", "")

    bazi_profile = request.session.get("bazi_profile_json", {})
    if not isinstance(bazi_profile, dict):
        bazi_profile = {}

    profile_needs_recompute = _bazi_profile_needs_recompute(bazi_profile)
    if bazi_birth_date and profile_needs_recompute:
        bazi_profile = build_bazi_profile(
            birth_date_text=bazi_birth_date,
            birth_hour_value=bazi_birth_hour,
            gender=sex_label,
        )
        if bazi_profile:
            request.session["bazi_profile_json"] = bazi_profile
            # 命盘重算后，旧分析结果可能与新字段不一致，强制失效重算。
            request.session.pop("bazi_profile_analysis_json", None)
            print("[BaziEvidence] session_profile_recomputed=true")

    _log_bazi_profile_json(bazi_profile)

    if isinstance(bazi_profile, dict) and bazi_profile.get("age_range"):
        age_group = bazi_profile.get("age_range", age_group)

    user_context = {
        "user_sex": sex_label,
        "expected_partner_sex": expected_partner_sex,
        "user_age_group": age_group,
        "user_age": bazi_profile.get("age") if isinstance(bazi_profile, dict) else None,
        "user_age_stage": bazi_profile.get("age_stage") if isinstance(bazi_profile, dict) else "",
        "user_eye_insight": eye_block_str,
        "user_nose_insight": nose_block_str,
        "user_lip_insight": lip_block_str,
        "user_personality_summary": person_str,
        "note": "基于本人分析动态生成三候选正缘画像prompt",
    }

    bazi_analysis = request.session.get("bazi_profile_analysis_json", {})
    if not isinstance(bazi_analysis, dict):
        bazi_analysis = {}
    has_dashscope_key = bool(str(os.getenv("DASHSCOPE_API_KEY", "")).strip())
    cached_source = str(bazi_analysis.get("source", ""))
    cached_text = str(bazi_analysis.get("display_text", ""))
    stale_local_fallback = (
        cached_source == "local_fallback"
        and has_dashscope_key
    ) or (
        "离线兜底文本" in cached_text
        and has_dashscope_key
    )

    if bazi_profile and (not bazi_analysis or stale_local_fallback):
        if stale_local_fallback:
            print("[BaziEvidence] refresh_stale_fallback=true")
        bazi_analysis = generate_bazi_analysis(bazi_profile=bazi_profile, user_context=user_context)
        if bazi_analysis:
            request.session["bazi_profile_analysis_json"] = bazi_analysis

    if isinstance(bazi_analysis, dict) and _has_duplicate_flow_lines(bazi_analysis.get("display_text", "")):
        print("[BaziEvidence] duplicate_flow_lines_detected=true")
        refreshed = generate_bazi_analysis(bazi_profile=bazi_profile, user_context=user_context)
        if isinstance(refreshed, dict) and refreshed.get("display_text"):
            bazi_analysis = refreshed
            request.session["bazi_profile_analysis_json"] = bazi_analysis

    if isinstance(bazi_analysis, dict) and _looks_like_template_bazi_text(bazi_analysis.get("display_text", "")):
        print("[BaziEvidence] template_like_cached_output_detected=true")
        refreshed = generate_bazi_analysis(bazi_profile=bazi_profile, user_context=user_context)
        if isinstance(refreshed, dict) and refreshed.get("display_text"):
            bazi_analysis = refreshed
            request.session["bazi_profile_analysis_json"] = bazi_analysis

    _log_bazi_analysis_json(bazi_analysis)

    bazi_display_text = ""
    bazi_display_html_flow = ""
    bazi_display_html_prosperity = ""
    bazi_display_html_strategy = ""
    bazi_text_flow = ""
    bazi_text_prosperity = ""
    bazi_text_strategy = ""
    if isinstance(bazi_analysis, dict):
        bazi_display_text = bazi_analysis.get("display_text", "")
    bazi_sections = _split_bazi_sections(bazi_display_text)
    bazi_display_html_flow = _format_bazi_display_html("\n".join(bazi_sections.get("flow", [])))
    bazi_display_html_prosperity = _format_bazi_display_html("\n".join(bazi_sections.get("prosperity", [])))
    bazi_display_html_strategy = _format_bazi_display_html("\n".join(bazi_sections.get("strategy", [])))
    # 生成纯文本版本用于报告图片
    bazi_text_flow = "\n".join(bazi_sections.get("flow", []))
    bazi_text_prosperity = "\n".join(bazi_sections.get("prosperity", []))
    bazi_text_strategy = "\n".join(bazi_sections.get("strategy", []))
    star_sign = _build_star_sign_context(bazi_profile)
    if bazi_display_text:
        print("[BaziOutput] header_preview={}".format(" | ".join([x for x in bazi_display_text.splitlines()[:3] if x])))

    ideal_partner = request.session.get("ideal_partner_profile_json", {})
    stale_ideal_age_prompt = False
    if isinstance(ideal_partner, dict) and ideal_partner:
        cached_prompts = ideal_partner.get("visual_prompts", [])
        if not isinstance(cached_prompts, list):
            cached_prompts = []
        legacy_prompt = ideal_partner.get("visual_prompt", "")
        merged_prompt_text = " ".join([str(x) for x in cached_prompts if x]) + " " + str(legacy_prompt or "")
        if re.search(r"\d+\s*[-~到]\s*\d+\s*岁|\d+岁|18-25|26-35|36-45|45\+", merged_prompt_text):
            stale_ideal_age_prompt = True

    if stale_ideal_age_prompt:
        print("[IdealPromptEvidence] stale_age_prompt_detected=true")
        request.session.pop("ideal_partner_profile_json", None)
        request.session.pop("ideal_visual_prompt", None)
        request.session.pop("ideal_visual_prompts", None)
        request.session.pop("ideal_partner_image_data_url", None)
        request.session.pop("ideal_partner_image_data_urls", None)
        ideal_partner = {}

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
                                astr_true_love=true_love_str if 'true_love_str' in dir() else "",
                                astr_couple="",
                                astr_bazi_flow="",
                                astr_bazi_prosperity="",
                                astr_bazi_strategy="",
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
                                astr_true_love=true_love_str if 'true_love_str' in dir() else "",
                                astr_couple="",
                                astr_bazi_flow="",
                                astr_bazi_prosperity="",
                                astr_bazi_strategy="",
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
        bazi_birth_date = request.POST.get("bazi_birth_date", "")
        bazi_birth_hour = request.POST.get("bazi_birth_hour", "")
        image_name = request.FILES.get('cover')
        print(image_name)
        post = PostNew()
        post.cover = image_name
        post.sex = author_sex
        post.save()
        # 将生辰暂存到 session；年龄段由八字模块动态计算。
        request.session["bazi_birth_date"] = bazi_birth_date
        request.session["bazi_birth_hour"] = bazi_birth_hour
        request.session["age_group"] = ""
        # 新图上传后清空上一次的正缘缓存，避免显示旧图。
        request.session.pop("ideal_visual_prompt", None)
        request.session.pop("ideal_visual_prompts", None)
        request.session.pop("ideal_prompt_random_pack", None)
        request.session.pop("ideal_partner_profile_json", None)
        request.session.pop("ideal_partner_image_data_url", None)
        request.session.pop("ideal_partner_image_data_urls", None)
        request.session.pop("bazi_profile_json", None)
        request.session.pop("bazi_profile_analysis_json", None)
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
                bazi_birth_date = request.POST.get("bazi_birth_date", "")
                bazi_birth_hour = request.POST.get("bazi_birth_hour", "")
                image_name = request.FILES.get('cover')
                print(image_name)
                post = PostNew()
                post.cover = image_name
                post.sex = author_sex
                post.save()
                request.session["bazi_birth_date"] = bazi_birth_date
                request.session["bazi_birth_hour"] = bazi_birth_hour
                request.session["age_group"] = ""
                request.session.pop("ideal_visual_prompt", None)
                request.session.pop("ideal_visual_prompts", None)
                request.session.pop("ideal_prompt_random_pack", None)
                request.session.pop("ideal_partner_profile_json", None)
                request.session.pop("ideal_partner_image_data_url", None)
                request.session.pop("ideal_partner_image_data_urls", None)
                request.session.pop("bazi_profile_json", None)
                request.session.pop("bazi_profile_analysis_json", None)
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
