import requests
import json
import os
import re
import random
from datetime import date
from difflib import SequenceMatcher

from myskills.bazi_expert import get_bazi_expert_prompt

# 是否启用 DashScope 在线算命：
#   - 默认 0：不调用 DashScope，只用本地文案；
#   - 设置环境变量 USE_DASHSCOPE=1 才会真的发起 HTTP 请求。
USE_DASHSCOPE = os.getenv("USE_DASHSCOPE", "0") in ["1", "true", "True"]

# 是否启用腾讯混元文生图：
#   - 默认 0：不调用混元文生图；
#   - 设置环境变量 USE_HUNYUAN_IMAGE=1 才会真的发起请求。
USE_HUNYUAN_IMAGE = os.getenv("USE_HUNYUAN_IMAGE", "0") in ["1", "true", "True"]



# ===== 新增：正缘候选特征字典（按年龄段） =====
HAIRSTYLE_DICT = {
    "儿童": {
        "male": [
            "自然短碎发", "齐刘海短发", "清爽短发", "锅盖头", "微卷短发",
            "圆寸", "偏分短发", "自然蓬松短发", "学生短发", "清新短发"
        ],
        "female": [
            "齐刘海短发", "双马尾", "高马尾", "丸子头", "短波波头",
            "自然长直发", "侧马尾", "空气刘海短发", "学生短发", "可爱短卷发"
        ]
    },
    "少年": {
        "male": [
            "微分短发", "纹理短发", "侧分短发", "清爽寸头", "自然碎发",
            "齐刘海短发", "中分短发", "蓬松短发", "校园短发", "简约短发"
        ],
        "female": [
            "长直发", "空气刘海长发", "高马尾", "双马尾", "法式锁骨发",
            "齐肩短发", "丸子头", "内扣波波头", "大波浪中长发", "清新短发"
        ]
    },
    "青年": {
        "male": [
            "微分碎盖", "纹理烫短发", "侧分短发", "寸头", "飞机头",
            "摩根烫短发", "齐刘海短发", "中分短发", "狼尾短发", "锡纸烫短发"
        ],
        "female": [
            "长直发", "羊毛卷", "法式锁骨发", "空气刘海波波头", "高马尾",
            "双马尾", "丸子头", "齐刘海短发", "大波浪卷发", "鲻鱼头短发"
        ]
    },
    "中年": {
        "male": [
            "侧分油头", "渐变短发", "商务短发", "纹理烫中短发", "复古油头",
            "短碎发", "偏分短发", "平头", "摩根烫短发", "前刺短发"
        ],
        "female": [
            "锁骨发", "齐肩短发", "大波浪中长发", "低马尾", "法式慵懒卷发",
            "八字刘海中长发", "高层次中长发", "内扣波波头", "羊毛卷中长发", "侧分长直发"
        ]
    },
    "中老年": {
        "male": [
            "经典侧分短发", "渐变寸头", "商务油头", "短碎发", "平头",
            "自然纹理短发", "偏分油头", "成熟短卷发", "后梳短发", "板寸"
        ],
        "female": [
            "齐肩微卷短发", "层次中长发", "大波浪中长发", "低盘发", "波波头短发",
            "侧分中长发", "锁骨卷发", "成熟短卷发", "简约直发中长发", "空气感短发"
        ]
    },
    "老年": {
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


def _age_group_with_years(age_group_text):
    raw = _take_text(age_group_text)
    if not raw:
        return ""
    if "岁" in raw:
        return raw
    return raw + "岁"


def _age_stage_by_real_age(age_value):
    try:
        age = int(age_value)
    except Exception:
        return ""
    if age <= 10:
        return "儿童"
    if age <= 17:
        return "少年"
    if age <= 30:
        return "青年"
    if age <= 49:
        return "中年"
    if age <= 59:
        return "中老年"
    return "老年"


def _resolve_user_age_stage(user_context):
    user_context = user_context if isinstance(user_context, dict) else {}

    stage_by_age = _age_stage_by_real_age(user_context.get("user_age"))
    if stage_by_age:
        return stage_by_age

    stage_text = _take_text(user_context.get("user_age_stage"))
    if stage_text in HAIRSTYLE_DICT:
        return stage_text

    group_text = _take_text(user_context.get("user_age_group"))
    for stage in HAIRSTYLE_DICT.keys():
        if stage in group_text:
            return stage

    nums = [int(x) for x in re.findall(r"\d+", group_text)]
    if nums:
        mid = nums[0] if len(nums) == 1 else (nums[0] + nums[1]) // 2
        stage_by_mid = _age_stage_by_real_age(mid)
        if stage_by_mid:
            return stage_by_mid

    return "青年"


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
    age_stage = _resolve_user_age_stage(user_context)
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
        age_stage + "年龄段" if age_stage else "",
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
    age_stage = "青年"
    if user_context:
        sex_label = str(user_context.get("expected_partner_sex", "女")).strip()
        if sex_label == "男":
            sex = "male"
        elif sex_label == "女":
            sex = "female"
        age_stage = _resolve_user_age_stage(user_context)
        if not age_stage or age_stage not in HAIRSTYLE_DICT:
            age_stage = "青年"

    # 随机采样
    hairstyles = random.sample(HAIRSTYLE_DICT[age_stage][sex], 3)
    face_shapes = random.sample(FACE_SHAPE_LIST, 3)
    eye_types = random.sample(EYE_TYPE_LIST, 3)
    hair_colors = random.sample(HAIR_COLOR_LIST, 3)
    lightings = random.sample(LIGHTING_LIST, 3)
    angles = ANGLE_LIST  # 固定顺序

    # 模板拼接
    prompts = []
    for i in range(3):
        prompt = "东亚人像，{}，{}，写实肖像，近景头像，清晰面部，简洁背景，{}，{}，{}，{}，{}，{}".format(
            "男" if sex == "male" else "女",
            age_stage + "年龄段",
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


def _build_local_bazi_text(bazi_profile):
    bazi_profile = bazi_profile if isinstance(bazi_profile, dict) else {}
    header_title = "☼八字排盘解析"
    header1 = "生辰（农历）：{}  虚岁：{}".format(
        _take_text(bazi_profile.get("lunar_birth_text")) or "未识别",
        _take_text(bazi_profile.get("nominal_age_cn")) or "未识别",
    )
    header2 = "四柱：{}".format(_take_text(bazi_profile.get("bazi_str")) or "未识别")
    header3 = "五行：{}".format(_take_text(bazi_profile.get("wuxing_summary")) or _take_text(bazi_profile.get("wuxing")) or "未识别")

    flow_year = date.today().year
    flow_next = flow_year + 1
    body0 = "流年干支"
    body01 = "{}年（今年）：{}".format(flow_year, _take_text(bazi_profile.get("current_year_ganzhi")) or "待推导")
    body02 = "{}年（明年）：{}".format(flow_next, _take_text(bazi_profile.get("next_year_ganzhi")) or "待推导")
    stem_compare = "；".join(bazi_profile.get("flow_year_stem_compare", []))
    branch_compare = "；".join(bazi_profile.get("flow_year_branch_compare", []))
    dayun_effect = _take_text(bazi_profile.get("flow_dayun_effect"))

    relation = bazi_profile.get("relationships", {}) if isinstance(bazi_profile.get("relationships"), dict) else {}
    relation_chong = "、".join(relation.get("chong", []))
    relation_he = "、".join(relation.get("he", []))
    relation_stem_he = "、".join(relation.get("stem_he", []))

    month_pillar = _take_text(bazi_profile.get("month_pillar"))
    dayun = _take_text(bazi_profile.get("current_dayun_ganzhi"))
    wuxing_summary = _take_text(bazi_profile.get("wuxing_summary"))

    body03 = "今年天干与命局天干的合冲克关系：{}".format(stem_compare) if stem_compare else ""
    body04 = "今年地支与命局地支的合冲刑害：{}".format(branch_compare) if branch_compare else ""
    body05 = "流年干支与当前大运干支的叠加效应：{}".format(dayun_effect) if dayun_effect else ""

    body1 = "旺衰与定局"
    body2 = "旺衰：以月令、透干、根气与岁运叠加综合判断。"
    body3 = "月令司令：{}。".format("月柱{}为本盘季节主气参考".format(month_pillar) if month_pillar else "本盘月令信息可用")

    cond_parts = []
    if relation_chong:
        cond_parts.append("关键：{}".format(relation_chong))
    if relation_he:
        cond_parts.append("关键：{}".format(relation_he))
    if relation_stem_he:
        cond_parts.append("关键：{}".format(relation_stem_he))
    if dayun:
        cond_parts.append("次第：先命局后岁运，当前参考大运{}".format(dayun))
    cond_text = "；".join(cond_parts)
    body4 = ""
    if wuxing_summary:
        if cond_text:
            body4 = "调候气象：结合{}综合判断（{}；大忌：单看一柱定全局）。".format(wuxing_summary, cond_text)
        else:
            body4 = "调候气象：结合{}综合判断。".format(wuxing_summary)

    dingju_main, dingju_desc = _infer_local_dingju(bazi_profile)
    body8 = "建议定局：{}（定局说明：{}）。".format(dingju_main, dingju_desc) if dingju_main and dingju_desc else ""
    body11 = "建议喜用：顺应月令与岁运中有利元素，循序放大优势。"
    body12 = "建议忌神：冲刑害引动阶段避免高风险孤注决策。"

    body13 = "给命主的“战略箴言”"
    body14 = "您的人生底牌是：在变化中持续校准方向与节奏。"
    body15 = "此时此刻的生存哲学：先稳基本盘，再做结构性增量。"
    body16 = "未来三年的战略伏笔：围绕主航道沉淀可复用能力与可信口碑。"
    lines = [
        header_title,
        header1,
        header2,
        header3,
        body0,
        body01,
        body02,
        body03,
        body04,
        body05,
        body1,
        body2,
        body3,
        body4,
        body8,
        body11,
        body12,
        body13,
        body14,
        body15,
        body16,
    ]
    return "\n".join([x for x in lines if _take_text(x)])


STEM_ELEMENT_MAP = {
    "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
    "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水",
}

BRANCH_ELEMENT_MAP = {
    "子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土", "巳": "火",
    "午": "火", "未": "土", "申": "金", "酉": "金", "戌": "土", "亥": "水",
}

GENERATE_REL = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
CONTROL_REL = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}


def _who_generates(target_element: str) -> str:
    for src, dst in GENERATE_REL.items():
        if dst == target_element:
            return src
    return ""


def _wuxing_count_map(profile: dict) -> dict:
    counts = {"金": 0, "木": 0, "水": 0, "火": 0, "土": 0}
    for item in profile.get("wuxing_list", []) if isinstance(profile.get("wuxing_list", []), list) else []:
        text = _take_text(item)
        for ch in text:
            if ch in counts:
                counts[ch] += 1
    return counts


def _infer_local_dingju(profile: dict):
    day_pillar = _take_text(profile.get("day_pillar"))
    month_pillar = _take_text(profile.get("month_pillar"))
    current_year = _take_text(profile.get("current_year_ganzhi"))
    dayun = _take_text(profile.get("current_dayun_ganzhi"))

    if len(day_pillar) < 2 or len(month_pillar) < 2:
        return "", ""

    day_stem = day_pillar[0]
    day_element = STEM_ELEMENT_MAP.get(day_stem, "")
    month_branch = month_pillar[1]
    month_element = BRANCH_ELEMENT_MAP.get(month_branch, "")
    if not day_element:
        return "", ""

    counts = _wuxing_count_map(profile)
    support_element = _who_generates(day_element)
    support_score = counts.get(day_element, 0) + counts.get(support_element, 0)
    drain_score = counts.get(GENERATE_REL.get(day_element, ""), 0) + counts.get(CONTROL_REL.get(day_element, ""), 0)

    if month_element:
        if month_element == day_element or GENERATE_REL.get(month_element, "") == day_element:
            support_score += 1
        if CONTROL_REL.get(month_element, "") == day_element:
            drain_score += 1

    diff = support_score - drain_score
    if diff >= 2:
        main = "日主偏旺，宜财官食伤泄秀"
    elif diff <= -2:
        main = "日主偏弱，宜印比扶身"
    else:
        main = "日主中和偏平，以调候通关为先"

    desc_parts = [
        "日主{}({})".format(day_stem, day_element),
        "月令{}主{}".format(month_branch, month_element or "气"),
        "扶抑对比{}比{}".format(support_score, drain_score),
    ]
    if current_year and dayun:
        desc_parts.append("并参考流年{}与大运{}的引动".format(current_year, dayun))
    return main, "；".join(desc_parts)


def _clean_bazi_template_echo(display_text: str) -> str:
    lines = [ln.strip() for ln in _clamp_bazi_display_text(display_text).splitlines() if ln.strip()]
    bad_markers = [
        "请逐柱比对",
        "按模板输出",
        "待推导",
        "e.g.",
        "当前版本仅输出基础关系项",
        "当前为离线兜底文本",
    ]
    cleaned = []
    for line in lines:
        if any(marker in line for marker in bad_markers):
            continue
        cleaned.append(line)
    return "\n".join(cleaned)


def _clamp_bazi_display_text(display_text: str) -> str:
    text = _take_text(display_text)
    if not text:
        return ""
    # 保留模型分段，仅做转义换行修复和长度保护。
    normalized = text.replace("\\r\\n", "\n").replace("\\n", "\n")
    if len(normalized) > 1600:
        normalized = normalized[:1600]
    return normalized


def _ensure_bazi_required_lines(display_text: str, bazi_profile: dict) -> str:
    text = _clamp_bazi_display_text(display_text)
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

    year_now_prefix = "{}年（今年）：".format(date.today().year)
    year_next_prefix = "{}年（明年）：".format(date.today().year + 1)
    required_by_prefix = [
        ("流年干支", "流年干支"),
        (year_now_prefix, "{}{}".format(year_now_prefix, _take_text(bazi_profile.get("current_year_ganzhi")) or "待推导")),
        (year_next_prefix, "{}{}".format(year_next_prefix, _take_text(bazi_profile.get("next_year_ganzhi")) or "待推导")),
        (
            "今年天干与命局天干的合冲克关系：",
            "今年天干与命局天干的合冲克关系：{}".format("；".join(bazi_profile.get("flow_year_stem_compare", [])) or "待推导"),
        ),
        (
            "今年地支与命局地支的合冲刑害：",
            "今年地支与命局地支的合冲刑害：{}".format("；".join(bazi_profile.get("flow_year_branch_compare", [])) or "待推导"),
        ),
        (
            "流年干支与当前大运干支的叠加效应：",
            "流年干支与当前大运干支的叠加效应：{}".format(_take_text(bazi_profile.get("flow_dayun_effect")) or "待推导"),
        ),
    ]

    # 先做语义去重：同一前缀只保留第一次出现，避免模型输出两套重复描述。
    semantic_prefixes = [x[0] for x in required_by_prefix]
    seen_prefixes = set()
    deduped = []
    for line in lines:
        matched_prefix = ""
        for pref in semantic_prefixes:
            if line == pref or line.startswith(pref):
                matched_prefix = pref
                break
        if matched_prefix:
            if matched_prefix in seen_prefixes:
                continue
            seen_prefixes.add(matched_prefix)
        deduped.append(line)

    out = deduped[:]
    present_prefixes = set()
    for line in out:
        for pref, _ in required_by_prefix:
            if line == pref or line.startswith(pref):
                present_prefixes.add(pref)
                break

    # 若缺失关键行，则插入到“流年干支”分段后方（或尾部）。
    if "流年干支" not in present_prefixes:
        out.append("流年干支")
        present_prefixes.add("流年干支")

    try:
        insert_at = out.index("流年干支") + 1
    except ValueError:
        insert_at = len(out)

    for pref, required_line in required_by_prefix[1:]:
        if pref in present_prefixes:
            continue
        out.insert(insert_at, required_line)
        insert_at += 1

    return "\n".join(out)


def generate_bazi_analysis(bazi_profile, user_context=None, api_key=None, model="qwen-plus"):
    """根据八字结构化 JSON 生成文本分析。"""

    bazi_profile = bazi_profile if isinstance(bazi_profile, dict) else {}
    user_context = user_context if isinstance(user_context, dict) else {}
    if not bazi_profile:
        return {}

    required_keys = [
        "bazi_str",
        "wuxing_summary",
        "current_year_ganzhi",
        "next_year_ganzhi",
        "current_dayun_ganzhi",
        "flow_year_stem_compare",
        "flow_year_branch_compare",
        "flow_dayun_effect",
    ]
    missing_keys = [k for k in required_keys if not bazi_profile.get(k)]
    if missing_keys:
        print("[BaziEvidence] missing_required_keys={}".format(",".join(missing_keys)))

    chat = DashScopeChat(api_key=api_key, model=model)
    # 八字分析优先调用 LLM：只要存在 API Key 就发起请求。
    if not chat.api_key:
        return {
            "display_text": _build_local_bazi_text(bazi_profile),
            "source": "local_fallback",
            "source_reason": "no_api_key",
        }

    payload = {
        "bazi_profile": bazi_profile,
        "flow_context": {
            "current_year_ganzhi": bazi_profile.get("current_year_ganzhi", ""),
            "next_year_ganzhi": bazi_profile.get("next_year_ganzhi", ""),
            "current_dayun_ganzhi": bazi_profile.get("current_dayun_ganzhi", ""),
            "flow_year_stem_compare": bazi_profile.get("flow_year_stem_compare", []),
            "flow_year_branch_compare": bazi_profile.get("flow_year_branch_compare", []),
            "flow_dayun_effect": bazi_profile.get("flow_dayun_effect", ""),
        },
        "user_context": {
            "user_sex": user_context.get("user_sex", ""),
            "expected_partner_sex": user_context.get("expected_partner_sex", ""),
            "user_age_group": user_context.get("user_age_group", ""),
        },
    }

    skill_prompt = get_bazi_expert_prompt()
    if not skill_prompt:
        skill_prompt = (
            "你是八字命理专家。"
            "请只输出最终正文文本，不要输出 JSON。"
            "正文必须按固定模板分段，包含农历生时、四柱、五行、流年与大运关系、旺衰定局。"
        )

    system_prompt = skill_prompt.replace(
        "{{USER_BAZI_DATA}}",
        json.dumps(payload, ensure_ascii=False),
    )

    user_prompt = "请基于上方模板中的<User_Bazi_Data>，按固定结构返回正文文本。"

    print("[BaziEvidence] rule_source=rili-bazi-main/bazi.js + paipan.gx.js")
    print("[BaziEvidence] bazi={}".format(_take_text(bazi_profile.get("bazi_str"))))
    print("[BaziEvidence] wuxing_summary={}".format(_take_text(bazi_profile.get("wuxing_summary"))))
    print("[BaziEvidence] relationships={}".format(json.dumps(bazi_profile.get("relationships", {}), ensure_ascii=False)))
    print("[BaziEvidence] flow_context={}".format(json.dumps(payload.get("flow_context", {}), ensure_ascii=False)))

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
        print("generate_bazi_analysis: DashScope 请求错误：{}".format(e))
        return {
            "display_text": _build_local_bazi_text(bazi_profile),
            "source": "local_fallback",
            "source_reason": "request_error",
        }

    display_text = _take_text(content)
    if display_text.startswith("{"):
        # 兼容旧提示词或模型偶发返回 JSON 的场景。
        parsed = _extract_and_parse_json(display_text)
        if isinstance(parsed, dict):
            display_text = _take_text(parsed.get("display_text"))

    if display_text:
        display_text = _clean_bazi_template_echo(display_text)
        display_text = _ensure_bazi_required_lines(display_text, bazi_profile)
        return {
            "display_text": display_text,
            "source": "dashscope",
            "source_reason": "llm_text",
        }

    return {
        "display_text": _build_local_bazi_text(bazi_profile),
        "source": "local_fallback",
        "source_reason": "empty_content",
    }


if __name__ == "__main__":
    # 简单自测：仅在命令行单独运行 ai/__init__.py 时使用
    chat = DashScopeChat()
    resp = chat.ask("你是谁？")
    if resp:
        print(resp)
