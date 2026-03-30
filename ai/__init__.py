import requests
import json
import os
import re
import random
from difflib import SequenceMatcher

# 是否启用 DashScope 在线算命：
#   - 默认 0：不调用 DashScope，只用本地文案；
#   - 设置环境变量 USE_DASHSCOPE=1 才会真的发起 HTTP 请求。
USE_DASHSCOPE = os.getenv("USE_DASHSCOPE", "0") in ["1", "true", "True"]

# 是否启用腾讯混元文生图：
#   - 默认 0：不调用混元文生图；
#   - 设置环境变量 USE_HUNYUAN_IMAGE=1 才会真的发起请求。
USE_HUNYUAN_IMAGE = os.getenv("USE_HUNYUAN_IMAGE", "0") in ["1", "true", "True"]



# ===== 新增：正缘候选特征字典 =====
HAIRSTYLE_DICT = {
    "18-25": {
        "male": [
            "微分碎盖", "纹理烫短发", "侧分短发", "寸头", "飞机头",
            "摩根烫短发", "齐刘海短发", "中分短发", "狼尾短发", "锡纸烫短发"
        ],
        "female": [
            "长直发", "羊毛卷", "法式锁骨发", "空气刘海波波头", "高马尾",
            "双马尾", "丸子头", "齐刘海短发", "大波浪卷发", "鲻鱼头短发"
        ]
    },
    "26-35": {
        "male": [
            "侧分油头", "渐变短发", "商务短发", "纹理烫中短发", "复古油头",
            "短碎发", "偏分短发", "平头", "摩根烫短发", "前刺短发"
        ],
        "female": [
            "锁骨发", "齐肩短发", "大波浪中长发", "低马尾", "法式慵懒卷发",
            "八字刘海中长发", "高层次中长发", "内扣波波头", "羊毛卷中长发", "侧分长直发"
        ]
    },
    "36-45": {
        "male": [
            "经典侧分短发", "渐变寸头", "商务油头", "短碎发", "平头",
            "自然纹理短发", "偏分油头", "成熟短卷发", "后梳短发", "板寸"
        ],
        "female": [
            "齐肩微卷短发", "层次中长发", "大波浪中长发", "低盘发", "波波头短发",
            "侧分中长发", "锁骨卷发", "成熟短卷发", "简约直发中长发", "空气感短发"
        ]
    },
    "45+": {
        "male": [
            "寸头", "经典侧分短发", "渐变短发", "短碎发", "平头",
            "后梳短发", "自然简约短发", "简约短油头", "花白自然短发", "成熟短卷发"
        ],
        "female": [
            "齐耳短发", "蓬松短卷发", "层次短发", "低发髻盘发", "波波头短发",
            "锁骨微卷短发", "自然直中长发", "侧分短发", "短碎发", "优雅盘发"
        ]
    }
}
FACE_SHAPE_LIST = [
    "椭圆脸", "圆脸", "长脸", "方脸", "菱形脸", "窄长脸", "鹅蛋脸"
]
EYE_TYPE_LIST = [
    "桃花眼", "丹凤眼", "杏眼", "瑞凤眼", "柳叶眼", "细长眼", "双眼皮大眼"
]
HAIR_COLOR_LIST = [
    "黑色发色", "棕色发色", "栗色发色", "深色发色", "浅棕发色"
]
LIGHTING_LIST = [
    "自然光", "柔和光影", "明亮光线", "逆光", "侧光"
]
ANGLE_LIST = [
    "正面", "三分之二侧面", "四分之三侧面"
]

RANDOM_PROMPT_POOLS = {
    "hair_colors": HAIR_COLOR_LIST,
    "eye_types": EYE_TYPE_LIST,
    "face_shapes": FACE_SHAPE_LIST,
    "lightings": LIGHTING_LIST,
}


def _pick_n_distinct(values, n):
    values = [str(v).strip() for v in (values or []) if str(v).strip()]
    if not values:
        return [""] * n
    if len(values) >= n:
        return random.sample(values, n)
    out = values[:]
    while len(out) < n:
        out.append(random.choice(values))
    return out


def _normalize_random_pack(random_pack=None, count=3):
    random_pack = random_pack if isinstance(random_pack, dict) else {}
    normalized = {}
    for key, pool in RANDOM_PROMPT_POOLS.items():
        current = random_pack.get(key)
        if isinstance(current, list):
            current_vals = [str(x).strip() for x in current if str(x).strip()]
        elif isinstance(current, str) and current.strip():
            current_vals = [current.strip()]
        else:
            current_vals = []

        if len(current_vals) < count:
            need = count - len(current_vals)
            current_vals.extend(_pick_n_distinct(pool, need))
        normalized[key] = current_vals[:count]
    return normalized


def _take_text(v):
    if isinstance(v, str):
        return v.strip()
    if v is None:
        return ""
    return str(v).strip()


def _unique_keep_order(items):
    out = []
    seen = set()
    for item in items:
        text = _take_text(item)
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
    return out


def _extract_anchor_parts(profile_result, user_context):
    profile_result = profile_result if isinstance(profile_result, dict) else {}
    user_context = user_context if isinstance(user_context, dict) else {}

    appearance = profile_result.get("appearance_tags", {})
    if not isinstance(appearance, dict):
        appearance = {}

    partner_traits = profile_result.get("partner_traits", {})
    partner_profile = profile_result.get("partner_profile", {})

    trait_values = []
    if isinstance(partner_traits, dict):
        trait_values.extend([_take_text(v) for v in partner_traits.values()])
    if isinstance(partner_profile, dict):
        trait_values.extend([_take_text(v) for v in partner_profile.values()])

    expected_partner_sex = _take_text(user_context.get("expected_partner_sex"))
    age_group = _take_text(user_context.get("user_age_group"))
    user_eye = _take_text(user_context.get("user_eye_insight"))
    user_nose = _take_text(user_context.get("user_nose_insight"))
    user_lip = _take_text(user_context.get("user_lip_insight"))
    user_person = _take_text(user_context.get("user_personality_summary"))

    base_parts = [
        "东亚人像",
        "写实肖像",
        "清晰面部细节",
        "简洁背景",
        "自然光",
        expected_partner_sex + "性特征" if expected_partner_sex else "",
        age_group + "左右" if age_group else "",
        _take_text(appearance.get("looks")),
        _take_text(appearance.get("face_shape")),
        _take_text(appearance.get("temperament")),
        _take_text(appearance.get("style")),
        _take_text(appearance.get("personality")),
        user_eye,
        user_nose,
        user_lip,
        user_person,
    ]
    base_parts.extend([x for x in trait_values[:4] if x])

    return _unique_keep_order(base_parts)


def _similarity_ratio(a, b):
    a = _take_text(a)
    b = _take_text(b)
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()



# ===== 新版三候选prompt生成：严格模板拼接，角度固定分配，特征随机 =====
def _build_three_visual_prompts(anchor_parts, random_pack, user_context=None):
    # user_context用于性别、年龄段判断
    sex = "male"
    age_group = "18-25"
    if user_context:
        sex_label = str(user_context.get("expected_partner_sex", "女")).strip()
        if sex_label == "男":
            sex = "male"
        elif sex_label == "女":
            sex = "female"
        age_group = str(user_context.get("user_age_group", "18-25")).strip()
        if not age_group or age_group not in HAIRSTYLE_DICT:
            age_group = "18-25"

    # 随机采样
    hairstyles = random.sample(HAIRSTYLE_DICT[age_group][sex], 3)
    face_shapes = random.sample(FACE_SHAPE_LIST, 3)
    eye_types = random.sample(EYE_TYPE_LIST, 3)
    hair_colors = random.sample(HAIR_COLOR_LIST, 3)
    lightings = random.sample(LIGHTING_LIST, 3)
    angles = ANGLE_LIST  # 固定顺序

    # 模板拼接
    prompts = []
    for i in range(3):
        prompt = "东亚人像，写实肖像，近景头像，清晰面部，简洁背景，{}，{}，{}，{}，{}，{}，{}，{}".format(
            "男" if sex == "male" else "女",
            age_group,
            face_shapes[i],
            eye_types[i],
            hairstyles[i],
            hair_colors[i],
            lightings[i],
            angles[i]
        )
        prompts.append(prompt)
    # 返回prompts和采样包
    normalized_pack = {
        "hairstyles": hairstyles,
        "face_shapes": face_shapes,
        "eye_types": eye_types,
        "hair_colors": hair_colors,
        "lightings": lightings,
        "angles": angles,
    }
    return prompts, normalized_pack


class DashScopeChat:
    def __init__(self, api_key=None, model="qwen-plus"):
        # 不再写死 key，优先从环境变量 DASHSCOPE_API_KEY 读取
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        self.model = model
        self.api_url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

    def ask(self, message):
        """向 DashScope 发送一条对话请求（传统单条算命用）。

        - 如果未开启 USE_DASHSCOPE，直接返回 None，走本地文案。
        - 如果没有配置 DASHSCOPE_API_KEY，也直接返回 None。
        - 所有异常都会被捕获并打印，不会影响主流程。
        """

        if not USE_DASHSCOPE:
            return None

        if not self.api_key:
            print("DashScope 未配置 DASHSCOPE_API_KEY，跳过在线请求。")
            return None

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是算命大师，要给出尽可能合理的的结果，你的回答只要算命结果，不要提到比例和数值信息，每次回答50个字左右",
                },
                {"role": "user", "content": message},
            ],
        }

        try:
            # 显式禁止使用系统 HTTP(S) 代理，避免之前的代理配置错误再次影响请求
            response = requests.post(
                self.api_url,
                headers=headers,
                data=json.dumps(data, ensure_ascii=False).encode("utf-8"),
                timeout=8,
                proxies={"http": None, "https": None},
            )
            response.raise_for_status()
            response_json = response.json()
            return response_json["choices"][0]["message"]["content"]
        except Exception as e:
            print("DashScope 请求错误：{}".format(e))
            return None


def _extract_and_parse_json(text):
    """从模型返回的文本中，尽量抽取并解析 JSON dict。

    优先直接 json.loads；失败时：
    - 尝试截取首个 `{` 到最后一个 `}` 之间的部分；
    - 去掉常见的末尾多余逗号（如 `,"key": 1,}`）。
    任何一步成功且结果为 dict 即返回，否则返回 None。
    """

    if not text:
        return None

    def _try_load(s):
        try:
            return json.loads(s)
        except Exception:
            return None

    # 1. 直接尝试整体解析
    obj = _try_load(text)
    if isinstance(obj, dict):
        return obj

    # 2. 尝试截取大括号包裹的主体
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = text[start : end + 1]
    else:
        candidate = text

    # 3. 去掉常见的尾随逗号
    cleaned = re.sub(r",\s*([}\]])", r"\1", candidate)

    for s in (candidate, cleaned):
        obj = _try_load(s)
        if isinstance(obj, dict):
            return obj

    return None


def generate_ideal_partner_profile(user_context, api_key=None, model="qwen-plus", random_pack=None):
    """调用通义千问，为当前用户生成“理想伴侣/正缘”描述。

    输入：
        user_context: dict，来自 cal_rate 等分析结果整理出的概要信息，
                     建议包含：性别、年龄段、MBTI/性格标签、五官亮点/短板等。

    返回：
        dict，形如：
        {
            "display_text": str,            # 中文正缘报告正文
            "partner_traits": dict,        # 结构化性格特征
            "partner_profile": dict,       # 职业 / 生活方式信息
            "appearance_tags": dict,       # 长相/脸型/气质/风格/性格
            "visual_prompt": str,          # 单条提示词（兼容）
            "visual_prompts": list[str]    # 三候选提示词
        }

    说明：
        - 仅在 USE_DASHSCOPE 开启且存在 DASHSCOPE_API_KEY 时才会真正请求线上接口；
        - 任意阶段出错都会返回空 dict，并打印错误信息，不阻断主流程；
        - 具体 prompt 逻辑与 JSON 结构约束写死在本函数内部，方便统一维护。
    """

    if not USE_DASHSCOPE:
        # 未开启线上服务时，直接返回空结果，方便本地离线调试
        print("generate_ideal_partner_profile: 未启用 DashScope，返回空结果。")
        return {}

    chat = DashScopeChat(api_key=api_key, model=model)
    if not chat.api_key:
        print("generate_ideal_partner_profile: 未配置 DASHSCOPE_API_KEY，返回空结果。")
        return {}

    # System Prompt：约束角色、风格、JSON 结构与字数
    # 说明：
    # - 伴侣性别默认按异性处理（由 user_context 中的 expected_partner_sex 给出，例如 "男" 或 "女"）；
    # - 如有用户年龄段信息（user_age_group），伴侣年龄段应与之相近，可略大或略小，但不要脱离该范围太多；
    # - visual_prompt 仅用于生成大头照/头像，重点描述脸型、五官、肤色、发型、气质和光线背景，避免具体服饰描述。
    system_prompt = (
        "你是一位结合中国面相传统与现代心理学的情感咨询师。"\
        "请根据给定的用户性格与面相分析概要，推演更适合 ta 的长期伴侣/正缘类型，并按说明中的伴侣性别与年龄段要求来设定人物形象。"\
        "你的回答必须遵守以下要求："\
        "1）只输出 JSON，不能有任何多余解释文字；"\
        "2）JSON 顶层包含 display_text、partner_traits、partner_profile、appearance_tags 字段，visual_prompt 可选；"\
        "3）display_text 为中文正文，约 300-450 字，分 3-5 段，用换行分段，语气温和积极，"\
        "   结合命理话术与心理咨询风格，但不要使用极端、歧视或恐吓性的表达；"\
        "4）partner_traits、partner_profile 内部为若干简单键值对，描述性格关键词、相处方式、职业类型等；"\
        "5）appearance_tags 内部必须包含 looks、face_shape、temperament、style、personality 五个键；"\
        "6）visual_prompt（可选）是一小段中文提示词，仅描述外貌与画面风格，长度约 25-60 个汉字，"\
        "   由若干中文短语构成，使用逗号或顿号分隔，例如：东亚人、30多岁男性、瓜子脸、短发、温和眼神、写实风格；"\
        "7）visual_prompt 不得包含“贵人运”“桃花旺”“事业运”等抽象算命词，只能描述可视化特征与画面风格；"\
        "8）visual_prompt 中不要出现具体服饰、品牌或颜色搭配（如“穿黑色西装”“红色连衣裙”），"\
        "   可以轻描淡写背景与光线（如“室内柔和光线、简单背景”），重点仍放在脸部、五官与发型。"
    )

    # User Prompt：将 user_context 打包为一段说明
    try:
        context_str = json.dumps(user_context or {}, ensure_ascii=False)
    except Exception:
        context_str = str(user_context)

    user_prompt = (
        "下面是一位用户的人脸与性格分析概要，使用 JSON 形式给出：\n"\
        + context_str + "\n\n"
        "请你基于这些信息，按照系统指令中给定的 JSON 结构与约束，"\
        "推演出这位用户更适合的长期伴侣/正缘类型，并只返回 JSON。"
    )

    headers = {
        "Authorization": f"Bearer {chat.api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "model": chat.model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    try:
        response = requests.post(
            chat.api_url,
            headers=headers,
            data=json.dumps(data, ensure_ascii=False).encode("utf-8"),
            timeout=15,
            proxies={"http": None, "https": None},
        )
        response.raise_for_status()
        response_json = response.json()
        content = response_json["choices"][0]["message"]["content"]
    except Exception as e:
        print("generate_ideal_partner_profile: DashScope 请求错误：{}".format(e))
        return {}

    result = _extract_and_parse_json(content)
    if isinstance(result, dict):
        anchor_parts = _extract_anchor_parts(result, user_context)
        # 强制用 expected_partner_sex 作为性别参数
        patched_user_context = dict(user_context)
        if "expected_partner_sex" in user_context:
            patched_user_context["expected_partner_sex"] = user_context["expected_partner_sex"]
        prompts, normalized_pack = _build_three_visual_prompts(anchor_parts, random_pack, user_context=patched_user_context)
        result["visual_prompts"] = prompts
        result["random_pack"] = normalized_pack
        if not _take_text(result.get("visual_prompt")) and prompts:
            result["visual_prompt"] = prompts[0]
        return result

    print("generate_ideal_partner_profile: 多次尝试解析 JSON 失败，丢弃本次结果。")
    try:
        # 调试用途：输出原始内容，便于观察是哪类字符导致解析失败
        print("generate_ideal_partner_profile: 原始返回内容:\n{}".format(content))
    except Exception:
        pass
    return {}


def generate_ideal_partner_image(prompt, resolution="1024:1024"):
    """调用腾讯混元文生图轻量版，生成一张正缘画像（base64）。

    环境变量：
        - USE_HUNYUAN_IMAGE=1 时才会调用线上接口；
        - TENCENTCLOUD_SECRET_ID / TENCENTCLOUD_SECRET_KEY 为鉴权密钥。

    返回：
        {
            "img_base64": str,
            "data_url": str,
            "request_id": str
        }
        出错时返回 {}，不阻断主流程。
    """

    if not prompt:
        print("generate_ideal_partner_image: prompt 为空，跳过生成。")
        return {}

    if not USE_HUNYUAN_IMAGE:
        print("generate_ideal_partner_image: 未启用 USE_HUNYUAN_IMAGE，跳过生成。")
        return {}

    secret_id = os.getenv("TENCENTCLOUD_SECRET_ID")
    secret_key = os.getenv("TENCENTCLOUD_SECRET_KEY")
    if not secret_id or not secret_key:
        print("generate_ideal_partner_image: 未配置腾讯云密钥，跳过生成。")
        return {}

    try:
        # 延迟导入，避免未安装 SDK 时影响其他功能。
        from tencentcloud.common import credential
        from tencentcloud.common.profile.client_profile import ClientProfile
        from tencentcloud.common.profile.http_profile import HttpProfile
        from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
        from tencentcloud.aiart.v20221229 import aiart_client, models
    except Exception as e:
        print("generate_ideal_partner_image: 腾讯云 SDK 不可用：{}".format(e))
        print("请先安装依赖：pip install tencentcloud-sdk-python")
        return {}

    payload = {
        "Prompt": prompt,
        "Resolution": resolution,
        "RspImgType": "base64",
    }
    print("generate_ideal_partner_image: 请求参数={}".format(
        json.dumps(payload, ensure_ascii=False)
    ))

    try:
        # 与腾讯云官方 Python 示例一致：密钥走环境变量，endpoint 使用 aiart。
        cred = credential.Credential(secret_id, secret_key)
        http_profile = HttpProfile()
        http_profile.endpoint = "aiart.tencentcloudapi.com"
        client_profile = ClientProfile()
        client_profile.httpProfile = http_profile
        region = os.getenv("TENCENTCLOUD_REGION", "ap-guangzhou")
        client = aiart_client.AiartClient(cred, region, client_profile)

        req = models.TextToImageLiteRequest()
        req.from_json_string(json.dumps(payload, ensure_ascii=False))
        resp = client.TextToImageLite(req)
        resp_json = json.loads(resp.to_json_string())
        print("generate_ideal_partner_image: 完整返回体={}".format(
            json.dumps(resp_json, ensure_ascii=False)
        ))
        response_obj = resp_json.get("Response", {})
        print("generate_ideal_partner_image: 运行模块文件={}".format(__file__))
        print("generate_ideal_partner_image: Response键={}".format(list(response_obj.keys()) if isinstance(response_obj, dict) else type(response_obj)))
        img_base64 = response_obj.get("ResultImage", "") if isinstance(response_obj, dict) else ""
        if not img_base64 and isinstance(response_obj, dict):
            # 兼容少量历史回包结构
            img_base64 = response_obj.get("Data", {}).get("ResultImage", "")
        if not img_base64:
            # SDK 对象属性兜底，避免 to_json_string 结构变化导致取不到。
            img_base64 = getattr(resp, "ResultImage", "")

        request_id = response_obj.get("RequestId", "") if isinstance(response_obj, dict) else ""
        if not request_id:
            request_id = getattr(resp, "RequestId", "")

        if not img_base64:
            print("generate_ideal_partner_image: 返回中无 ResultImage。")
            print("generate_ideal_partner_image: RequestId={}".format(request_id))
            if response_obj.get("Error"):
                print("generate_ideal_partner_image: Error={}".format(
                    json.dumps(response_obj.get("Error"), ensure_ascii=False)
                ))
            return {}

        data_url = img_base64 if str(img_base64).startswith("data:image/") else "data:image/png;base64,{}".format(img_base64)
        return {
            "img_base64": img_base64,
            "data_url": data_url,
            "request_id": request_id,
        }
    except TencentCloudSDKException as e:
        print("generate_ideal_partner_image: 腾讯云 SDK 异常：{}".format(e))
        return {}
    except Exception as e:
        print("generate_ideal_partner_image: 调用混元失败：{}".format(e))
        return {}


if __name__ == "__main__":
    # 简单自测：仅在命令行单独运行 ai/__init__.py 时使用
    chat = DashScopeChat()
    resp = chat.ask("你是谁？")
    if resp:
        print(resp)
