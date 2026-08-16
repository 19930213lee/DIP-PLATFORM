"""
西南交通大学希望学院 · 基础部 · 数字图像处理教学平台
后端 Flask 应用 —— v3.0 全12章完整版 共78个操作

设计：李康乐    技术支持：李康乐

━━━━━━━━━━━━━━ 配置说明 ━━━━━━━━━━━━━━
AI 助手功能使用 DeepSeek API（deepseek-chat 模型）。
设置环境变量以启用：
  export DEEPSEEK_API_KEY=" "
  （可选）export DEEPSEEK_API_BASE="https://api.deepseek.com/v1"
若不设置，AI 助手将提示"服务未配置"。
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os
import io
import base64
import json
import time


def _load_dotenv():
    """加载项目根目录 .env 文件（若存在），用于本地开发环境变量配置。"""
    try:
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                k, v = line.split('=', 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k and k not in os.environ:
                    os.environ[k] = v
    except FileNotFoundError:
        pass


_load_dotenv()
import hashlib
import numpy as np
import requests as http_requests
from flask import Flask, request, jsonify, render_template, Response, send_from_directory, session, redirect, url_for
from PIL import Image, ImageEnhance
import cv2

import db
from auth_route import auth_bp, login_required, get_current_user

app = Flask(__name__)
app.secret_key = 'dip-platform-secret-key-2026'  # 固定密钥，避免容器重启后 session 失效
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

app.register_blueprint(auth_bp, url_prefix='/auth')

# 初始化数据库和默认管理员
db.init_db()
is_new, init_pw = db.create_initial_admin()
if is_new:
    print(f"\n{'='*60}")
    print(f"  管理员账户已创建")
    print(f"  用户名: admin    密码: {init_pw}")
    print(f"  请在首次登录后修改密码")
    print(f"{'='*60}\n")

OPERATION_NAMES = {
    # 1/2 数字图像基础
    'sampling_demo':           '采样过程演示',
    'quantization_demo':       '量化过程演示',
    'resolution_compare':      '空间分辨率对比',
    'pixel_neighbors':         '像素邻域可视化',
    'distance_metrics':        '距离度量演示',
    'interpolation_demo':      '图像插值对比',
    # 3 灰度变换与空间滤波
    'image_inversion':         '图像反转',
    'log_transform':           '对数变换',
    'contrast_stretch':        '对比度拉伸',
    'histogram_equalization':  '直方图均衡化',
    'clahe':                   '自适应直方图均衡(CLAHE)',
    'gamma_correction':        '伽马校正',
    'median_blur':             '中值滤波',
    'gaussian_blur':           '高斯滤波',
    'bilateral_filter':        '双边滤波',
    'laplacian':               '拉普拉斯锐化',
    'unsharp_mask':            'USM锐化',
    'sobel_sharpen':           'Sobel锐化',
    # 4 频率域滤波
    'ideal_lowpass':           '理想低通滤波',
    'ideal_highpass':          '理想高通滤波',
    'butterworth_lowpass':     '巴特沃斯低通滤波',
    'butterworth_highpass':    '巴特沃斯高通滤波',
    'gaussian_lowpass':        '高斯低通滤波',
    'gaussian_highpass':       '高斯高通滤波',
    'bandpass_filter':         '带通滤波',
    # 5 图像复原与重建
    'gaussian_noise':          '添加高斯噪声',
    'sp_noise':                '添加椒盐噪声',
    'mean_filter_restore':     '均值滤波去噪',
    'median_restore':          '中值滤波去噪',
    'nlm_denoise':             '非局部均值去噪(NLM)',
    'wiener_filter':           '维纳滤波复原',
    'sobel':                   'Sobel边缘检测',
    'canny':                   'Canny边缘检测',
    # 6 彩色图像处理
    'rgb_split':               'RGB通道分离',
    'rgb_to_hsv':              'RGB→HSV转换',
    'hue_adjust':              '色调调整',
    'saturation_adjust':       '饱和度调整',
    'brightness_adjust':       '亮度调整',
    'color_balance':           '色彩平衡调整',
    'pseudo_color':            '假彩色增强',
    'color_hist_eq':           '彩色直方图均衡化',
    # 7 小波变换与多分辨率处理
    'gaussian_pyramid':        '高斯金字塔',
    'laplacian_pyramid':       '拉普拉斯金字塔',
    'pyramid_blend':           '多分辨率融合',
    'dwt_denoise':             '离散小波降噪',
    'dwt_edge_enhance':        '小波边缘增强',
    # 8 图像压缩
    'dct_visualize':           'DCT变换可视化',
    'jpeg_simulate':           'JPEG压缩模拟',
    'jpeg_compare':            '压缩质量对比',
    'binary_rle':              '二值化与游程编码',
    'binary_huffman':          '哈夫曼编码模拟',
    # 9 形态学图像处理
    'erosion_dilation':        '腐蚀与膨胀',
    'open_close':              '开运算与闭运算',
    'morph_gradient':          '形态学梯度',
    'tophat':                  '顶帽变换',
    'blackhat':                '黑帽变换',
    'skeletonize':             '骨架提取',
    # 10 图像分割
    'otsu_threshold':          'Otsu阈值分割',
    'adaptive_threshold':      '自适应阈值分割',
    'kmeans_segment':          'K-means聚类分割',
    'mean_shift_segment':      'Mean Shift分割',
    'watershed':               '分水岭算法',
    'grabcut':                 'GrabCut分割',
    # 11 表示和描述
    'contour_extract':         '轮廓提取',
    'convex_hull':             '凸包检测',
    'min_enclosing':           '最小外接矩形',
    'contour_approx':          '轮廓近似',
    'hu_moments':              'Hu矩特征',
    'shape_match':             '形状匹配',
    'fourier_descriptor':      '傅里叶描述子',
    # 12 目标检测与识别
    'template_matching':       '模板匹配',
    'hough_lines':             '霍夫线检测',
    'hough_circles':           '霍夫圆检测',
    'corner_harris':           'Harris角点检测',
    'sift_features':           'SIFT特征检测',
    'hog_features':            'HOG特征提取',
    'prewitt':                 'Prewitt边缘检测',
    'roberts':                 'Roberts边缘检测',
    'region_growing':          '区域生长分割',
    # 综合工程案例（每章一个完整流水线）
    'case_01_satellite':       '综合工程案例：遥感图像采样分析',
    'case_02_document':        '综合工程案例：文档几何校正',
    'case_03_defect':          '综合工程案例：零件缺陷检测',
    'case_04_ct_denoise':      '综合工程案例：CT图像去噪',
    'case_05_photo_restore':   '综合工程案例：老照片复原',
    'case_06_drone_veg':       '综合工程案例：航拍色彩增强',
    'case_07_panorama':        '综合工程案例：多分辨率融合',
    'case_08_jpeg_opt':        '综合工程案例：JPEG压缩优化',
    'case_09_pcb_inspect':     '综合工程案例：PCB缺陷检测',
    'case_10_water_extract':   '综合工程案例：遥感水体提取',
    'case_11_part_classify':   '综合工程案例：零件分类识别',
    'case_12_traffic_sign':    '综合工程案例：交通标志检测',
}

# ========================= 工具函数 =========================
def img_to_base64(pil_img):
    buf = io.BytesIO()
    pil_img.save(buf, format='PNG')
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode('utf-8')

def pil_to_cv2(pil_img):
    arr = np.array(pil_img.convert('RGB'))
    return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)

def cv2_to_pil(cv_img):
    if len(cv_img.shape) == 2:
        return Image.fromarray(cv_img, mode='L')
    return Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))

def resize_for_fft(img):
    """缩放到偶数尺寸用于FFT"""
    h, w = img.shape[:2]
    h2, w2 = h if h % 2 == 0 else h - 1, w if w % 2 == 0 else w - 1
    return cv2.resize(img, (w2, h2)) if (h != h2 or w != w2) else img.copy()

def fft_filter(img_cv, mask_gen):
    """通用的频域滤波函数。mask_gen(rows, cols) 返回掩码矩阵"""
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv
    gray = resize_for_fft(gray)
    dft = cv2.dft(np.float32(gray), flags=cv2.DFT_COMPLEX_OUTPUT)
    dft_shift = np.fft.fftshift(dft)
    rows, cols = gray.shape
    mask = mask_gen(rows, cols)
    dft_shift *= mask[:, :, np.newaxis]
    f_ishift = np.fft.ifftshift(dft_shift)
    img_back = cv2.idft(f_ishift)
    img_back = cv2.magnitude(img_back[:, :, 0], img_back[:, :, 1])
    cv2.normalize(img_back, img_back, 0, 255, cv2.NORM_MINMAX)
    return img_back.astype(np.uint8)


# ========================= 第3章: 灰度变换与空间滤波 =========================
def process_image_inversion(img_cv, params):
    return cv2.bitwise_not(img_cv)

def process_log_transform(img_cv, params):
    c = params.get('c', 20)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv
    s = c * np.log1p(gray.astype(np.float64) / 255.0 * 255)
    s = np.clip(s / s.max() * 255, 0, 255).astype(np.uint8)
    return s

def process_contrast_stretch(img_cv, params):
    low_p = params.get('low_percent', 2)
    high_p = params.get('high_percent', 98)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv
    low = np.percentile(gray, low_p)
    high = np.percentile(gray, high_p)
    stretched = np.clip((gray.astype(float) - low) / (high - low + 1e-5) * 255, 0, 255).astype(np.uint8)
    return stretched

def process_histogram_equalization(img_cv, params):
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv
    return cv2.equalizeHist(gray)

def process_clahe(img_cv, params):
    clip_limit = params.get('clip_limit', 2.0)
    tile_size = params.get('tile_size', 8)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(tile_size, tile_size))
    return clahe.apply(gray)

def process_gamma_correction(img_cv, params):
    gamma = params.get('gamma', 1.0)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv
    inv = 1.0 / gamma
    table = np.array([(i / 255.0) ** inv * 255 for i in range(256)]).astype(np.uint8)
    return cv2.LUT(gray, table)

def process_median_blur(img_cv, params):
    ksize = params.get('ksize', 5)
    if ksize % 2 == 0:
        ksize += 1
    return cv2.medianBlur(img_cv, ksize)

def process_gaussian_blur(img_cv, params):
    ksize = params.get('ksize', 5)
    sigma = params.get('sigma', 1.0)
    if ksize % 2 == 0:
        ksize += 1
    return cv2.GaussianBlur(img_cv, (ksize, ksize), sigma)

def process_bilateral_filter(img_cv, params):
    d = params.get('d', 9)
    sigma_color = params.get('sigma_color', 75)
    sigma_space = params.get('sigma_space', 75)
    return cv2.bilateralFilter(img_cv, d, sigma_color, sigma_space)

def process_laplacian(img_cv, params):
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv
    lap = cv2.Laplacian(gray, cv2.CV_64F)
    lap = np.uint8(np.absolute(lap))
    return lap

def process_unsharp_mask(img_cv, params):
    amount = params.get('amount', 1.5)
    radius = params.get('radius', 3)
    blurred = cv2.GaussianBlur(img_cv, (radius * 2 + 1, radius * 2 + 1), radius)
    sharp = cv2.addWeighted(img_cv, 1.0 + amount, blurred, -amount, 0)
    return np.clip(sharp, 0, 255).astype(np.uint8)

def process_sobel_sharpen(img_cv, params):
    ksize = params.get('ksize', 3)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv
    sx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=ksize)
    sy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=ksize)
    return np.uint8(np.sqrt(sx ** 2 + sy ** 2))


# ========================= 第4章: 频率域滤波 =========================
def process_ideal_lowpass(img_cv, params):
    cutoff = params.get('cutoff', 50)
    def mask_gen(r, c):
        y, x = np.ogrid[:r, :c]
        cy, cx = r // 2, c // 2
        d = np.sqrt((y - cy) ** 2 + (x - cx) ** 2)
        return (d <= cutoff).astype(np.float32)
    return fft_filter(img_cv, mask_gen)

def process_ideal_highpass(img_cv, params):
    cutoff = params.get('cutoff', 30)
    def mask_gen(r, c):
        y, x = np.ogrid[:r, :c]
        cy, cx = r // 2, c // 2
        d = np.sqrt((y - cy) ** 2 + (x - cx) ** 2)
        return (d >= cutoff).astype(np.float32)
    return fft_filter(img_cv, mask_gen)

def process_butterworth_lowpass(img_cv, params):
    cutoff = params.get('cutoff', 50)
    def mask_gen(r, c):
        y, x = np.ogrid[:r, :c]
        cy, cx = r // 2, c // 2
        d = np.sqrt((y - cy) ** 2 + (x - cx) ** 2)
        return (1.0 / (1.0 + (d / (cutoff + 1e-6)) ** 4)).astype(np.float32)
    return fft_filter(img_cv, mask_gen)

def process_butterworth_highpass(img_cv, params):
    cutoff = params.get('cutoff', 30)
    def mask_gen(r, c):
        y, x = np.ogrid[:r, :c]
        cy, cx = r // 2, c // 2
        d = np.sqrt((y - cy) ** 2 + (x - cx) ** 2)
        return (1.0 / (1.0 + ((cutoff + 1e-6) / (d + 1e-6)) ** 4)).astype(np.float32)
    return fft_filter(img_cv, mask_gen)

def process_gaussian_lowpass(img_cv, params):
    cutoff = params.get('cutoff', 50)
    def mask_gen(r, c):
        y, x = np.ogrid[:r, :c]
        cy, cx = r // 2, c // 2
        d = np.sqrt((y - cy) ** 2 + (x - cx) ** 2)
        return np.exp(-d ** 2 / (2 * cutoff ** 2)).astype(np.float32)
    return fft_filter(img_cv, mask_gen)

def process_gaussian_highpass(img_cv, params):
    cutoff = params.get('cutoff', 30)
    def mask_gen(r, c):
        y, x = np.ogrid[:r, :c]
        cy, cx = r // 2, c // 2
        d = np.sqrt((y - cy) ** 2 + (x - cx) ** 2)
        return (1.0 - np.exp(-d ** 2 / (2 * cutoff ** 2))).astype(np.float32)
    return fft_filter(img_cv, mask_gen)

def process_bandpass_filter(img_cv, params):
    low = params.get('low_cutoff', 20)
    high = params.get('high_cutoff', 80)
    def mask_gen(r, c):
        y, x = np.ogrid[:r, :c]
        cy, cx = r // 2, c // 2
        d = np.sqrt((y - cy) ** 2 + (x - cx) ** 2)
        return ((d >= low) & (d <= high)).astype(np.float32)
    return fft_filter(img_cv, mask_gen)


# ========================= 第5章: 图像复原与重建 =========================
def process_gaussian_noise(img_cv, params):
    sigma = params.get('sigma', 25)
    noise = np.random.normal(0, sigma, img_cv.shape).astype(np.int16)
    return np.clip(img_cv.astype(np.int16) + noise, 0, 255).astype(np.uint8)

def process_sp_noise(img_cv, params):
    amount = params.get('amount', 0.05)
    out = img_cv.copy()
    h, w = out.shape[:2]
    for c in range(3):
        num_salt = int(w * h * amount / 2)
        xs = np.random.randint(0, w, num_salt)
        ys = np.random.randint(0, h, num_salt)
        out[ys, xs, c] = 255
        num_pepper = int(w * h * amount / 2)
        xp = np.random.randint(0, w, num_pepper)
        yp = np.random.randint(0, h, num_pepper)
        out[yp, xp, c] = 0
    return out

def process_mean_filter_restore(img_cv, params):
    ksize = params.get('ksize', 5)
    if ksize % 2 == 0:
        ksize += 1
    return cv2.blur(img_cv, (ksize, ksize))

def process_median_restore(img_cv, params):
    ksize = params.get('ksize', 5)
    if ksize % 2 == 0:
        ksize += 1
    return cv2.medianBlur(img_cv, ksize)

def process_nlm_denoise(img_cv, params):
    h_val = params.get('h', 10)
    return cv2.fastNlMeansDenoisingColored(img_cv, None, h_val, h_val, 7, 21)

def process_wiener_filter(img_cv, params):
    ksize = params.get('ksize', 5)
    if ksize % 2 == 0:
        ksize += 1
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv
    local_mean = cv2.blur(gray.astype(np.float64), (ksize, ksize))
    local_var = cv2.blur((gray.astype(np.float64) - local_mean) ** 2, (ksize, ksize))
    noise_var = np.mean(local_var)
    result = local_mean + np.maximum(local_var - noise_var, 0) / np.maximum(local_var, 1e-8) * (gray.astype(np.float64) - local_mean)
    return np.clip(result, 0, 255).astype(np.uint8)

def process_sobel(img_cv, params):
    ksize = params.get('ksize', 3)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv
    sx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=ksize)
    sy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=ksize)
    return np.uint8(np.sqrt(sx ** 2 + sy ** 2))

def process_canny(img_cv, params):
    low = params.get('low_threshold', 50)
    high = params.get('high_threshold', 150)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv
    return cv2.Canny(gray, low, high)


# ========================= 第6章: 彩色图像处理 =========================
def process_rgb_split(img_cv, params):
    channel = params.get('channel', '合并显示')
    if channel == '合并显示':
        h, w = img_cv.shape[:2]
        h2 = h // 2
        w2 = w // 2
        resized = cv2.resize(img_cv, (w2 * 2, h2 * 2))
        canvas = np.zeros((h2 * 2 + 10, w2 * 2 + 10, 3), dtype=np.uint8)
        b, g, r = cv2.split(resized)
        canvas[0:h2, 0:w2] = cv2.merge([b, np.zeros_like(g), np.zeros_like(r)])
        canvas[0:h2, w2+10:w2*2+10] = cv2.merge([np.zeros_like(b), g, np.zeros_like(r)])
        canvas[h2+10:h2*2+10, 0:w2] = cv2.merge([np.zeros_like(b), np.zeros_like(g), r])
        canvas[h2+10:h2*2+10, w2+10:w2*2+10] = resized
        return canvas
    idx = {'R': 2, 'G': 1, 'B': 0}[channel]
    c = img_cv[:, :, idx]
    return cv2.merge([c, c, c])

def process_rgb_to_hsv(img_cv, params):
    channel = params.get('channel', '合并显示')
    hsv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2HSV)
    if channel == '合并显示':
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    idx = {'H': 0, 'S': 1, 'V': 2}[channel]
    c = hsv[:, :, idx]
    if idx == 0:
        c_show = (c.astype(np.float32) / 180.0 * 255).astype(np.uint8)
    else:
        c_show = c
    return cv2.merge([c_show, c_show, c_show])

def process_hue_adjust(img_cv, params):
    shift = params.get('shift', 0)
    hsv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2HSV).astype(np.int16)
    hsv[:, :, 0] = (hsv[:, :, 0] + shift) % 180
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

def process_saturation_adjust(img_cv, params):
    factor = params.get('factor', 1.0)
    hsv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * factor, 0, 255)
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

def process_brightness_adjust(img_cv, params):
    beta = params.get('beta', 0)
    return np.clip(img_cv.astype(np.int16) + beta, 0, 255).astype(np.uint8)

def process_color_balance(img_cv, params):
    r_gain = params.get('r_gain', 1.0)
    g_gain = params.get('g_gain', 1.0)
    b_gain = params.get('b_gain', 1.0)
    out = img_cv.astype(np.float32)
    out[:, :, 2] *= r_gain
    out[:, :, 1] *= g_gain
    out[:, :, 0] *= b_gain
    return np.clip(out, 0, 255).astype(np.uint8)

def process_pseudo_color(img_cv, params):
    colormap_name = params.get('colormap', 'jet')
    colormaps = {
        'jet': cv2.COLORMAP_JET, 'hot': cv2.COLORMAP_HOT, 'cool': cv2.COLORMAP_COOL,
        'bone': cv2.COLORMAP_BONE, 'rainbow': cv2.COLORMAP_RAINBOW, 'turbo': cv2.COLORMAP_TURBO,
        'ocean': cv2.COLORMAP_OCEAN, 'pink': cv2.COLORMAP_PINK
    }
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv
    return cv2.applyColorMap(gray, colormaps.get(colormap_name, cv2.COLORMAP_JET))

def process_color_hist_eq(img_cv, params):
    ycrcb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2YCrCb)
    ycrcb[:, :, 0] = cv2.equalizeHist(ycrcb[:, :, 0])
    return cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)


# ========================= 第7章: 小波变换与多分辨率处理 =========================
def process_gaussian_pyramid(img_cv, params):
    levels = params.get('levels', 3)
    img = img_cv.copy()
    pyramid = []
    for i in range(levels):
        pyramid.append(img)
        img = cv2.pyrDown(img)
    h, w = pyramid[0].shape[:2]
    total_w = sum(p.shape[1] for p in pyramid) + (len(pyramid) - 1) * 4
    canvas = np.zeros((h, total_w, 3), dtype=np.uint8)
    x = 0
    for p in pyramid:
        ph, pw = p.shape[:2]
        canvas[(h - ph) // 2:(h - ph) // 2 + ph, x:x + pw] = p
        x += pw + 4
    return canvas

def process_laplacian_pyramid(img_cv, params):
    levels = params.get('levels', 3)
    g = img_cv.copy()
    gp = [g]
    for i in range(levels):
        g = cv2.pyrDown(g)
        gp.append(g)
    images = []
    for i in range(levels):
        up = cv2.pyrUp(gp[i + 1], dstsize=(gp[i].shape[1], gp[i].shape[0]))
        lap = cv2.subtract(gp[i], up)
        lap_show = cv2.convertScaleAbs(lap, alpha=2, beta=128)
        images.append(lap_show)
    h = images[0].shape[0]
    total_w = sum(im.shape[1] for im in images) + (len(images) - 1) * 4
    canvas = np.zeros((h, total_w, 3), dtype=np.uint8)
    x = 0
    for im in images:
        canvas[:im.shape[0], x:x + im.shape[1]] = im
        x += im.shape[1] + 4
    return canvas

def process_pyramid_blend(img_cv, params):
    """多分辨率融合: 将图片左右一半进行拉普拉斯金字塔融合"""
    levels = params.get('levels', 3)
    h, w = img_cv.shape[:2]
    half = w // 2
    A = img_cv[:, :half].copy()
    B = img_cv[:, half:].copy()
    if B.shape[1] < half:
        B = cv2.resize(B, (half, h))
    gpA, gpB = [A.astype(np.float32)], [B.astype(np.float32)]
    for i in range(levels):
        gpA.append(cv2.pyrDown(gpA[-1]))
        gpB.append(cv2.pyrDown(gpB[-1]))
    lpA, lpB = [], []
    for i in range(levels):
        la = gpA[i] - cv2.pyrUp(gpA[i + 1], dstsize=(gpA[i].shape[1], gpA[i].shape[0]))
        lb = gpB[i] - cv2.pyrUp(gpB[i + 1], dstsize=(gpB[i].shape[1], gpB[i].shape[0]))
        lpA.append(la)
        lpB.append(lb)
    lpA.append(gpA[-1])
    lpB.append(gpB[-1])
    ls = []
    for la, lb in zip(lpA, lpB):
        r, c = la.shape[:2]
        mx = np.ones((r, c // 2, 3), dtype=np.float32)
        mask = np.hstack([mx, np.zeros((r, c - c // 2, 3), dtype=np.float32)])
        ls.append(la * mask + lb * (1 - mask))
    result = ls[-1]
    for i in range(levels - 1, -1, -1):
        result = cv2.pyrUp(result, dstsize=(ls[i].shape[1], ls[i].shape[0]))
        result += ls[i]
    return np.clip(result, 0, 255).astype(np.uint8)

def process_dwt_denoise(img_cv, params):
    threshold = params.get('threshold', 30)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv
    h, w = gray.shape
    if h % 2: h -= 1
    if w % 2: w -= 1
    gray = gray[:h, :w].astype(np.float32)
    coeffs = cv2.dct(gray)
    mask = np.abs(coeffs) > threshold
    denoised = cv2.idct(coeffs * mask.astype(np.float32))
    denoised = np.clip(denoised, 0, 255).astype(np.uint8)
    return denoised

def process_dwt_edge_enhance(img_cv, params):
    gain = params.get('gain', 2.0)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv
    h, w = gray.shape
    if h % 2: h -= 1
    if w % 2: w -= 1
    gray = gray[:h, :w].astype(np.float32)
    coeffs = cv2.dct(gray)
    center_h, center_w = h // 2, w // 2
    coeffs[center_h - 10:center_h + 10, center_w - 10:center_w + 10] *= gain
    result = cv2.idct(coeffs)
    return np.clip(result, 0, 255).astype(np.uint8)


# ========================= 第8章: 图像压缩 =========================
def process_dct_visualize(img_cv, params):
    """DCT变换可视化"""
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv
    h, w = gray.shape
    if h % 2: h -= 1
    if w % 2: w -= 1
    gray = gray[:h, :w].astype(np.float32)
    dct = cv2.dct(gray)
    dct_log = np.log(np.abs(dct) + 1)
    dct_norm = ((dct_log - dct_log.min()) / (dct_log.max() - dct_log.min() + 1e-8) * 255).astype(np.uint8)
    return dct_norm

def process_jpeg_simulate(img_cv, params):
    quality = params.get('quality', 50)
    _, buf = cv2.imencode('.jpg', img_cv, [cv2.IMWRITE_JPEG_QUALITY, quality])
    return cv2.imdecode(buf, cv2.IMREAD_COLOR)

def process_jpeg_compare(img_cv, params):
    """压缩质量对比：上排原始图 vs 压缩图，下排差值"""
    quality = params.get('quality', 30)
    _, buf = cv2.imencode('.jpg', img_cv, [cv2.IMWRITE_JPEG_QUALITY, quality])
    jpeg_img = cv2.imdecode(buf, cv2.IMREAD_COLOR)
    diff = cv2.absdiff(img_cv, jpeg_img)
    diff_amp = cv2.convertScaleAbs(diff, alpha=5)
    h, w = img_cv.shape[:2]
    canvas = np.zeros((h * 2, w * 2, 3), dtype=np.uint8)
    canvas[:h, :w] = img_cv
    canvas[:h, w:] = jpeg_img
    canvas[h:, :w] = diff_amp
    text = f'PSNR: {cv2.PSNR(img_cv, jpeg_img):.2f} dB  |  Quality: {quality}'
    cv2.putText(canvas, text, (10, h * 2 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    return cv2.resize(canvas, (w * 2, h * 2))

def process_binary_rle(img_cv, params):
    threshold = params.get('threshold', 128)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv
    _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
    flat = binary.flatten()
    runs = []
    count = 0
    current = flat[0]
    for v in flat:
        if v == current:
            count += 1
        else:
            runs.append(count)
            count = 1
            current = v
    runs.append(count)
    ratio = len(runs) * 100.0 / len(flat)
    canvas = np.zeros((binary.shape[0] + 40, binary.shape[1], 3), dtype=np.uint8)
    canvas[:binary.shape[0], :] = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
    cv2.putText(canvas, f'RLE encode: {len(runs)} runs, ratio={ratio:.1f}%',
                (10, binary.shape[0] + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
    return canvas

def process_binary_huffman(img_cv, params):
    """哈夫曼编码模拟：显示二值图像并统计0/1编码压缩比"""
    threshold = params.get('threshold', 128)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv
    _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
    flat = binary.flatten()
    total = len(flat)
    ones = np.sum(flat > 0)
    zeros = total - ones
    p0 = zeros / total
    p1 = ones / total
    entropy = -p0 * np.log2(p0 + 1e-10) - p1 * np.log2(p1 + 1e-10)
    ratio = entropy / 8.0
    canvas = np.zeros((binary.shape[0] + 40, binary.shape[1], 3), dtype=np.uint8)
    canvas[:binary.shape[0], :] = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
    cv2.putText(canvas, f'Huffman: entropy={entropy:.2f} bit/pixel, ratio={ratio:.1%}',
                (10, binary.shape[0] + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
    return canvas


# ========================= 第9章: 形态学图像处理 =========================
def _get_kernel(size):
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (size, size))

def process_erosion_dilation(img_cv, params):
    mode = params.get('mode', '腐蚀')
    ksize = params.get('ksize', 3)
    iters = params.get('iterations', 1)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv
    kernel = _get_kernel(ksize)
    # 支持中文/英文两种模式名
    if mode in ('腐蚀', 'erosion'):
        result = cv2.erode(gray, kernel, iterations=iters)
    else:
        result = cv2.dilate(gray, kernel, iterations=iters)
    return result

def process_open_close(img_cv, params):
    mode = params.get('mode', '开运算')
    ksize = params.get('ksize', 5)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv
    kernel = _get_kernel(ksize)
    if mode in ('开运算', 'open'):
        return cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
    else:
        return cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)

def process_morph_gradient(img_cv, params):
    ksize = params.get('ksize', 3)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv
    kernel = _get_kernel(ksize)
    return cv2.morphologyEx(gray, cv2.MORPH_GRADIENT, kernel)

def process_tophat(img_cv, params):
    ksize = params.get('ksize', 9)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv
    kernel = _get_kernel(ksize)
    return cv2.morphologyEx(gray, cv2.MORPH_TOPHAT, kernel)

def process_blackhat(img_cv, params):
    ksize = params.get('ksize', 9)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv
    kernel = _get_kernel(ksize)
    return cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, kernel)

def process_skeletonize(img_cv, params):
    """骨架提取 (Zhang-Suen 细化算法)"""
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
    binary = binary // 255
    skel = np.zeros(binary.shape, dtype=np.uint8)
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    while True:
        eroded = cv2.erode(binary, kernel)
        temp = cv2.dilate(eroded, kernel)
        temp = cv2.subtract(binary, temp)
        skel = cv2.bitwise_or(skel, temp)
        binary = eroded.copy()
        if cv2.countNonZero(binary) == 0:
            break
    return (skel * 255).astype(np.uint8)


# ========================= 第10章: 图像分割 =========================
def process_otsu_threshold(img_cv, params):
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv
    _, result = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return result

def process_adaptive_threshold(img_cv, params):
    block_size = params.get('block_size', 11)
    c = params.get('c', 2)
    if block_size % 2 == 0:
        block_size += 1
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv
    return cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                  cv2.THRESH_BINARY, block_size, c)

def process_kmeans_segment(img_cv, params):
    k = params.get('k', 3)
    data = img_cv.reshape((-1, 3)).astype(np.float32)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    _, labels, centers = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_PP_CENTERS)
    centers = np.uint8(centers)
    return centers[labels.flatten()].reshape(img_cv.shape)

def process_mean_shift_segment(img_cv, params):
    sp = params.get('sp', 30)
    sr = params.get('sr', 30)
    return cv2.pyrMeanShiftFiltering(img_cv, sp, sr)

def process_watershed(img_cv, params):
    thresh = params.get('thresh', 100)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    sure_bg = cv2.dilate(binary, kernel, iterations=3)
    dist = cv2.distanceTransform(binary, cv2.DIST_L2, 5)
    _, sure_fg = cv2.threshold(dist, 0.35 * dist.max(), 255, 0)
    sure_fg = np.uint8(sure_fg)
    unknown = cv2.subtract(sure_bg, sure_fg)
    _, markers = cv2.connectedComponents(sure_fg)
    markers += 1
    markers[unknown == 255] = 0
    markers = cv2.watershed(img_cv, markers)
    result = img_cv.copy()
    result[markers == -1] = [0, 0, 255]
    return result

def process_grabcut(img_cv, params):
    iters = params.get('iters', 5)
    h, w = img_cv.shape[:2]
    mask = np.zeros((h, w), np.uint8)
    bgd = np.zeros((1, 65), np.float64)
    fgd = np.zeros((1, 65), np.float64)
    margin = 10
    rect = (margin, margin, w - 2 * margin, h - 2 * margin)
    cv2.grabCut(img_cv, mask, rect, bgd, fgd, iters, cv2.GC_INIT_WITH_RECT)
    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
    result = img_cv * mask2[:, :, np.newaxis]
    return result


# ========================= 第11章: 表示和描述 =========================
def process_contour_extract(img_cv, params):
    mode = params.get('mode', '所有轮廓')
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    retrieve = cv2.RETR_TREE if mode == '所有轮廓' else cv2.RETR_EXTERNAL
    contours, _ = cv2.findContours(binary, retrieve, cv2.CHAIN_APPROX_SIMPLE)
    result = np.zeros((img_cv.shape[0], img_cv.shape[1], 3), dtype=np.uint8)
    for i, cnt in enumerate(contours):
        color = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
                 (255, 0, 255), (0, 255, 255), (128, 255, 0), (255, 128, 0)][i % 8]
        cv2.drawContours(result, [cnt], -1, color, 2)
        area = cv2.contourArea(cnt)
        if area > 100:
            M = cv2.moments(cnt)
            if M['m00'] != 0:
                cx, cy = int(M['m10'] / M['m00']), int(M['m01'] / M['m00'])
                cv2.putText(result, str(i + 1), (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1)
    return result

def process_convex_hull(img_cv, params):
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    result = img_cv.copy()
    for cnt in contours:
        hull = cv2.convexHull(cnt)
        cv2.drawContours(result, [hull], -1, (0, 255, 0), 2)
        cv2.drawContours(result, [cnt], -1, (0, 0, 255), 1)
    return result

def process_min_enclosing(img_cv, params):
    mode = params.get('mode', '全部显示')
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    result = img_cv.copy()
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 100:
            continue
        if mode in ('矩形', '全部显示'):
            x, y, w_box, h_box = cv2.boundingRect(cnt)
            cv2.rectangle(result, (x, y), (x + w_box, y + h_box), (255, 0, 0), 2)
        if mode in ('旋转矩形', '全部显示'):
            rect = cv2.minAreaRect(cnt)
            box = cv2.boxPoints(rect)
            box = np.int32(box)
            cv2.polylines(result, [box], True, (0, 255, 0), 2)
        if mode in ('圆形', '全部显示'):
            (cx, cy), radius = cv2.minEnclosingCircle(cnt)
            cv2.circle(result, (int(cx), int(cy)), int(radius), (0, 0, 255), 2)
    return result

def process_contour_approx(img_cv, params):
    epsilon_factor = params.get('epsilon', 0.01)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    result = img_cv.copy()
    for cnt in contours:
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon_factor * peri, True)
        cv2.drawContours(result, [cnt], -1, (0, 0, 255), 1)
        cv2.drawContours(result, [approx], -1, (0, 255, 0), 2)
        if len(approx) < 10:
            for pt in approx:
                cv2.circle(result, tuple(pt[0]), 4, (255, 0, 0), -1)
    return result

def process_hu_moments(img_cv, params):
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    result = img_cv.copy()
    offset = 30
    for idx, cnt in enumerate(contours):
        if cv2.contourArea(cnt) < 100:
            continue
        moments = cv2.moments(cnt)
        hu = cv2.HuMoments(moments)
        cv2.drawContours(result, [cnt], -1, (0, 255, 0), 2)
        for j in range(7):
            text = f'H{j + 1}={hu[j][0]:.2e}'
            cv2.putText(result, text, (10, offset), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1)
            offset += 15
        offset += 10
        if idx >= 2:
            break
    return result

def process_shape_match(img_cv, params):
    """形状匹配：对检测到的轮廓进行匹配度评分"""
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    result = img_cv.copy()
    valid = [c for c in contours if cv2.contourArea(c) > 200]
    colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]
    for i, cnt in enumerate(valid):
        matches = []
        for j, other in enumerate(valid):
            if i != j:
                score = cv2.matchShapes(cnt, other, cv2.CONTOURS_MATCH_I1, 0.0)
                matches.append((j, score))
        cv2.drawContours(result, [cnt], -1, colors[i % len(colors)], 2)
        M = cv2.moments(cnt)
        if M['m00'] != 0:
            cx, cy = int(M['m10'] / M['m00']), int(M['m01'] / M['m00'])
            if matches:
                best = min(matches, key=lambda x: x[1])
                cv2.putText(result, f'{i}: best match #{best[0]} ({best[1]:.3f})',
                            (cx - 40, cy - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, colors[i % len(colors)], 1)
    return result

def process_fourier_descriptor(img_cv, params):
    num_d = params.get('num_descriptors', 20)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    result = img_cv.copy()
    for cnt in contours[:3]:
        if len(cnt) < num_d:
            continue
        cv2.drawContours(result, [cnt], -1, (0, 0, 255), 1)
        cnt_c = cnt.squeeze().astype(np.float64)
        c = cnt_c[:, 0] + 1j * cnt_c[:, 1]
        fd = np.fft.fft(c)
        fd[num_d:-num_d] = 0
        reconstructed = np.fft.ifft(fd)
        pts = np.stack([reconstructed.real, reconstructed.imag], axis=1).astype(np.int32)
        for pt in pts:
            cv2.circle(result, tuple(pt), 1, (0, 255, 0), -1)
    cv2.putText(result, f'FD: {num_d} descriptors', (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    return result


# ========================= 第1/2章: 数字图像基础 =========================
def process_sampling_demo(img_cv, params):
    """采样过程演示：降采样后再放大回原尺寸，展示采样率对图像质量的影响"""
    sample_rate = params.get('sample_rate', 0.5)
    h, w = img_cv.shape[:2]
    new_h, new_w = max(4, int(h * sample_rate)), max(4, int(w * sample_rate))
    down = cv2.resize(img_cv, (new_w, new_h), interpolation=cv2.INTER_NEAREST)
    up = cv2.resize(down, (w, h), interpolation=cv2.INTER_NEAREST)
    # 拼接对比：原图 | 采样结果
    canvas = np.zeros((h, w * 2, 3), dtype=np.uint8)
    canvas[:, :w] = img_cv
    canvas[:, w:] = up
    cv2.putText(canvas, f'原图 ({w}x{h})', (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    cv2.putText(canvas, f'采样率={sample_rate:.0%} ({new_w}x{new_h})', (w + 10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    return canvas


def process_quantization_demo(img_cv, params):
    """量化过程演示：将灰度值离散化到特定位深，展示量化对图像的影响"""
    bit_depth = params.get('bit_depth', 4)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv
    levels = 2 ** bit_depth
    step = 256 // levels
    quantized = (gray // step) * step + step // 2
    quantized = quantized.astype(np.uint8)
    # 拼接对比
    h, w = gray.shape
    canvas = np.zeros((h + 30, w * 2), dtype=np.uint8)
    canvas[:h, :w] = gray
    canvas[:h, w:] = quantized
    canvas = cv2.cvtColor(canvas, cv2.COLOR_GRAY2BGR)
    cv2.putText(canvas, f'原图 (256级)', (10, h + 22),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(canvas, f'{bit_depth}位量化 ({levels}级)', (w + 10, h + 22),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    return canvas


def process_resolution_compare(img_cv, params):
    """空间分辨率对比：缩放图像展示不同分辨率下的视觉效果"""
    scale = params.get('scale', 0.5)
    h, w = img_cv.shape[:2]
    new_h, new_w = max(8, int(h * scale)), max(8, int(w * scale))
    # 用不同插值方法放大回原尺寸展示
    small = cv2.resize(img_cv, (new_w, new_h), interpolation=cv2.INTER_NEAREST)
    nn_up = cv2.resize(small, (w * 2 // 3, h * 2 // 3), interpolation=cv2.INTER_NEAREST)
    bilinear_up = cv2.resize(small, (w * 2 // 3, h * 2 // 3), interpolation=cv2.INTER_LINEAR)
    bicubic_up = cv2.resize(small, (w * 2 // 3, h * 2 // 3), interpolation=cv2.INTER_CUBIC)
    # 四宫格布局
    out_h, out_w = h // 2, w // 2
    canvas = np.zeros((out_h * 2 + 10, out_w * 2 + 10, 3), dtype=np.uint8)
    orig = cv2.resize(img_cv, (out_w, out_h))
    nn = cv2.resize(nn_up, (out_w, out_h))
    bl = cv2.resize(bilinear_up, (out_w, out_h))
    bc = cv2.resize(bicubic_up, (out_w, out_h))
    canvas[:out_h, :out_w] = orig
    canvas[:out_h, out_w + 10:out_w * 2 + 10] = nn
    canvas[out_h + 10:out_h * 2 + 10, :out_w] = bl
    canvas[out_h + 10:out_h * 2 + 10, out_w + 10:out_w * 2 + 10] = bc
    cv2.putText(canvas, '原图', (5, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    cv2.putText(canvas, f'最近邻 ({new_w}x{new_h})', (out_w + 15, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    cv2.putText(canvas, f'双线性 ({new_w}x{new_h})', (5, out_h + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    cv2.putText(canvas, f'双三次 ({new_w}x{new_h})', (out_w + 15, out_h + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    return canvas


def process_pixel_neighbors(img_cv, params):
    """像素邻域可视化：高亮中心像素及其邻域"""
    mode = params.get('mode', '4-邻域')
    h, w = img_cv.shape[:2]
    cy, cx = h // 2, w // 2
    box_size = 60
    result = img_cv.copy()
    # 绘制中心像素标记
    cv2.rectangle(result, (cx - box_size // 2, cy - box_size // 2),
                  (cx + box_size // 2, cy + box_size // 2), (0, 255, 0), 2)
    cv2.circle(result, (cx, cy), 4, (0, 0, 255), -1)
    # 绘制邻域
    if mode == '4-邻域':
        neighbors = [(cx, cy - box_size), (cx, cy + box_size),
                     (cx - box_size, cy), (cx + box_size, cy)]
        label = '4-邻域: N4(p) = {(x,y+1),(x,y-1),(x-1,y),(x+1,y)}'
    elif mode == '8-邻域':
        neighbors = [(cx + dx, cy + dy) for dx in [-box_size, 0, box_size]
                     for dy in [-box_size, 0, box_size] if not (dx == 0 and dy == 0)]
        label = '8-邻域: N8(p) = N4(p) U ND(p)'
    else:
        neighbors = [(cx - box_size, cy - box_size), (cx + box_size, cy - box_size),
                     (cx - box_size, cy + box_size), (cx + box_size, cy + box_size)]
        label = '对角邻域: ND(p) = {(x-1,y-1),(x+1,y-1),(x-1,y+1),(x+1,y+1)}'
    for nx, ny in neighbors:
        cv2.circle(result, (nx, ny), 3, (255, 255, 0), -1)
        cv2.line(result, (cx, cy), (nx, ny), (0, 255, 255), 1)
    cv2.rectangle(result, (0, 0), (w, 50), (0, 0, 0), -1)
    cv2.putText(result, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    return result


def process_distance_metrics(img_cv, params):
    """距离度量演示：展示不同距离度量下的等距线"""
    mode = params.get('mode', '欧几里得距离')
    h, w = 400, 400
    center = (w // 2, h // 2)
    canvas = np.zeros((h, w, 3), dtype=np.uint8)
    # 绘制网格
    for x in range(0, w, 20):
        cv2.line(canvas, (x, 0), (x, h), (50, 50, 50), 1)
    for y in range(0, h, 20):
        cv2.line(canvas, (0, y), (w, y), (50, 50, 50), 1)
    # 绘制等距圆
    for r in range(20, min(w, h) // 2, 30):
        if mode == '欧几里得距离':
            cv2.circle(canvas, center, r, (0, 255, 255), 1)
        elif mode == 'D4城市街区距离':
            pts = np.array([[center[0] + r, center[1]], [center[0], center[1] + r],
                            [center[0] - r, center[1]], [center[0], center[1] - r]], np.int32)
            cv2.polylines(canvas, [pts], True, (0, 255, 255), 1)
        else:
            side = int(r * 0.707)
            cv2.rectangle(canvas, (center[0] - side, center[1] - side),
                          (center[0] + side, center[1] + side), (0, 255, 255), 1)
    cv2.circle(canvas, center, 5, (0, 0, 255), -1)
    cv2.rectangle(canvas, (0, 0), (w, 30), (0, 0, 0), -1)
    label = f'距离度量: {mode}  |  等距线间隔=30像素'
    cv2.putText(canvas, label, (10, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    return canvas


def process_interpolation_demo(img_cv, params):
    """图像插值对比：缩小后放大展示不同插值方法的差异"""
    method = params.get('method', '双线性插值')
    h, w = img_cv.shape[:2]
    small_size = (max(4, w // 4), max(4, h // 4))
    small = cv2.resize(img_cv, small_size, interpolation=cv2.INTER_AREA)
    inter_map = {'最近邻插值': cv2.INTER_NEAREST, '双线性插值': cv2.INTER_LINEAR, '双三次插值': cv2.INTER_CUBIC}
    inter = inter_map.get(method, cv2.INTER_LINEAR)
    up = cv2.resize(small, (w, h), interpolation=inter)
    # 拼接对比
    canvas = np.zeros((h, w * 3, 3), dtype=np.uint8)
    canvas[:, :w] = img_cv
    small_disp = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
    canvas[:, w:w * 2] = small_disp
    canvas[:, w * 2:] = up
    cv2.putText(canvas, '原图', (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    cv2.putText(canvas, f'缩小1/4 ({small_size[0]}x{small_size[1]})', (w + 10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(canvas, f'{method} 放大还原', (w * 2 + 10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    return canvas


# ========================= 第12章: 目标检测与识别 =========================
def process_template_matching(img_cv, params):
    """模板匹配：用图像中心区域作为模板在全图上搜索匹配"""
    method_name = params.get('method', '归一化互相关')
    methods = {
        '平方差匹配': cv2.TM_SQDIFF_NORMED,
        '归一化平方差': cv2.TM_SQDIFF_NORMED,
        '归一化互相关': cv2.TM_CCORR_NORMED,
        '相关系数匹配': cv2.TM_CCOEFF_NORMED
    }
    method = methods.get(method_name, cv2.TM_CCORR_NORMED)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv
    h, w = gray.shape
    # 取中心作为模板
    th, tw = h // 3, w // 3
    cy, cx = h // 2, w // 2
    template = gray[cy - th // 2:cy + th // 2, cx - tw // 2:cx + tw // 2]
    result_map = cv2.matchTemplate(gray, template, method)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result_map)
    if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
        top_left = min_loc
        score = min_val
    else:
        top_left = max_loc
        score = max_val
    result = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    cv2.rectangle(result, (cx - tw // 2, cy - th // 2), (cx + tw // 2, cy + th // 2), (0, 255, 0), 2)
    cv2.rectangle(result, top_left, (top_left[0] + tw, top_left[1] + th), (0, 0, 255), 2)
    cv2.putText(result, '模板', (cx - tw // 2, cy - th // 2 - 8),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    cv2.putText(result, f'匹配 {method_name} score={score:.3f}',
                (top_left[0], top_left[1] - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
    return result


def process_hough_lines(img_cv, params):
    """霍夫线检测：检测图像中的直线段"""
    threshold = params.get('threshold', 150)
    min_length = params.get('min_length', 50)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv
    edges = cv2.Canny(gray, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold,
                             minLineLength=min_length, maxLineGap=10)
    result = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    count = 0
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(result, (x1, y1), (x2, y2), (0, 255, 0), 2)
            count += 1
    cv2.putText(result, f'检测到 {count} 条直线 (threshold={threshold}, min_len={min_length})',
                (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    return result


def process_hough_circles(img_cv, params):
    """霍夫圆检测：检测图像中的圆形"""
    dp = params.get('dp', 1.2)
    min_dist = params.get('min_dist', 50)
    param1 = params.get('param1', 100)
    param2 = params.get('param2', 30)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp, min_dist,
                                param1=param1, param2=param2, minRadius=10, maxRadius=200)
    result = img_cv.copy()
    count = 0
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for c in circles[0, :]:
            cv2.circle(result, (c[0], c[1]), c[2], (0, 255, 0), 2)
            cv2.circle(result, (c[0], c[1]), 3, (0, 0, 255), -1)
            count += 1
    cv2.putText(result, f'检测到 {count} 个圆', (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    return result


def process_corner_harris(img_cv, params):
    """Harris角点检测"""
    block_size = params.get('block_size', 2)
    ksize = params.get('ksize', 3)
    k = params.get('k', 0.04)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv
    gray_f = np.float32(gray)
    dst = cv2.cornerHarris(gray_f, block_size, ksize, k)
    dst = cv2.dilate(dst, None)
    result = img_cv.copy()
    result[dst > 0.01 * dst.max()] = [0, 0, 255]
    num_corners = np.sum(dst > 0.01 * dst.max())
    cv2.putText(result, f'Harris角点: {num_corners}个 (block={block_size}, k={k:.2f})',
                (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    return result


def process_sift_features(img_cv, params):
    """SIFT特征检测：检测并绘制关键点"""
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv
    sift = cv2.SIFT_create()
    keypoints, descriptors = sift.detectAndCompute(gray, None)
    result = cv2.drawKeypoints(img_cv, keypoints, None,
                                flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    cv2.putText(result, f'SIFT关键点: {len(keypoints)} 个', (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    return result


def process_hog_features(img_cv, params):
    """HOG特征提取：可视化梯度方向直方图"""
    cell_size = params.get('cell_size', 8)
    block_size = params.get('block_size', 2)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv
    h, w = gray.shape
    win_size = ((w // cell_size) * cell_size, (h // cell_size) * cell_size)
    if win_size[0] < cell_size * 2 or win_size[1] < cell_size * 2:
        return img_cv
    gray = gray[:win_size[1], :win_size[0]]
    hog = cv2.HOGDescriptor(win_size, (cell_size * block_size, cell_size * block_size),
                             (cell_size, cell_size), (cell_size, cell_size), 9)
    hog_feat = hog.compute(gray)
    # 可视化：在图像上绘制梯度方向
    gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=1)
    gy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=1)
    mag, angle = cv2.cartToPolar(gx, gy, angleInDegrees=True)
    result = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    step = cell_size
    for y in range(step // 2, h, step):
        for x in range(step // 2, w, step):
            if y >= win_size[1] or x >= win_size[0]:
                continue
            m = mag[y, x]
            a = angle[y, x] * np.pi / 180.0
            if m > 10:
                dx = int(np.cos(a) * step * 0.4)
                dy = int(np.sin(a) * step * 0.4)
                cv2.arrowedLine(result, (x, y), (x + dx, y + dy),
                                (0, 255, 0), 1, tipLength=0.3)
    cv2.putText(result, f'HOG: cell={cell_size}px, block={block_size}x{block_size}, 9 bins, feat_dim={len(hog_feat)}',
                (5, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    return result


def process_prewitt(img_cv, params):
    """Prewitt边缘检测：使用Prewitt算子计算梯度幅值"""
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv
    # Prewitt卷积核
    kernel_x = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]], dtype=np.float32)
    kernel_y = np.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]], dtype=np.float32)
    gx = cv2.filter2D(gray, cv2.CV_64F, kernel_x)
    gy = cv2.filter2D(gray, cv2.CV_64F, kernel_y)
    mag = np.sqrt(gx ** 2 + gy ** 2)
    mag = np.clip(mag, 0, 255).astype(np.uint8)
    return mag


def process_roberts(img_cv, params):
    """Roberts边缘检测：使用2x2对角差分算子"""
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv
    # Roberts算子：g(x,y) = sqrt((z9-z5)^2 + (z8-z6)^2)
    gx = cv2.filter2D(gray.astype(np.float32), cv2.CV_64F,
                        np.array([[0, 0, 0], [0, -1, 0], [0, 0, 1]], dtype=np.float32))
    gy = cv2.filter2D(gray.astype(np.float32), cv2.CV_64F,
                        np.array([[0, 0, 0], [0, 0, -1], [0, 1, 0]], dtype=np.float32))
    mag = np.sqrt(gx ** 2 + gy ** 2)
    mag = np.clip(mag, 0, 255).astype(np.uint8)
    return mag


def process_region_growing(img_cv, params):
    """区域生长分割：从种子点出发，根据灰度相似性合并邻域像素"""
    threshold = params.get('threshold', 20)
    max_iter = params.get('max_iter', 100)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv
    h, w = gray.shape
    # 以图像中心为种子点
    seed_y, seed_x = h // 2, w // 2
    seed_val = int(gray[seed_y, seed_x])

    # 区域生长
    segmented = np.zeros((h, w), dtype=np.uint8)
    visited = np.zeros((h, w), dtype=bool)
    queue = [(seed_y, seed_x)]
    visited[seed_y, seed_x] = True

    directions = [(-1, -1), (-1, 0), (-1, 1),
                  (0, -1),           (0, 1),
                  (1, -1),  (1, 0),  (1, 1)]

    count = 0
    while queue and count < max_iter:
        count += 1
        y, x = queue.pop(0)
        segmented[y, x] = 255
        for dy, dx in directions:
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and not visited[ny, nx]:
                if abs(int(gray[ny, nx]) - seed_val) <= threshold:
                    visited[ny, nx] = True
                    queue.append((ny, nx))

    # 在原图上标记分割区域
    result = img_cv.copy()
    overlay = np.zeros_like(result)
    overlay[segmented == 255] = [0, 255, 0]
    result = cv2.addWeighted(result, 0.7, overlay, 0.3, 0)
    cv2.circle(result, (seed_x, seed_y), 5, (0, 0, 255), -1)
    cv2.putText(result, f'区域生长: 种子({seed_x},{seed_y}) val={seed_val}, 阈值={threshold}, 像素数={count}',
                (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    return result


# ========================= 综合工程案例流水线 =========================

def _ensure_gray_cv(img_cv):
    """统一转灰度图（保持 BGR 格式为灰度）"""
    return cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv


def process_case_01_satellite(img_cv, params):
    """Ch1-2 综合案例：遥感图像采样分析流水线
    预处理 -> 降采样退化 -> 量化退化 -> 拼接对比图"""
    gray = _ensure_gray_cv(img_cv)
    h, w = gray.shape
    # 降采样：每2个像素取1个
    ds2 = cv2.resize(gray, (w // 2, h // 2), interpolation=cv2.INTER_AREA)
    ds2_up = cv2.resize(ds2, (w, h), interpolation=cv2.INTER_NEAREST)
    # 量化退化：8bit -> 4bit
    levels = 16
    q4 = (gray // (256 // levels)) * (256 // (levels - 1))
    q4 = np.clip(q4, 0, 255).astype(np.uint8)
    # 拼接
    row1 = np.hstack([gray, ds2_up])
    row2 = np.hstack([q4, np.zeros_like(gray)])
    combined = np.vstack([row1, row2])
    result = cv2.cvtColor(combined, cv2.COLOR_GRAY2BGR)
    cv2.putText(result, 'Original', (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
    cv2.putText(result, '2x Downsample + Nearest', (w+10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
    cv2.putText(result, '4-bit Quantized (16 levels)', (10, h+20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
    cv2.putText(result, '(原图右下对照区)', (w+10, h+20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (128,128,128), 2)
    return result


def process_case_02_document(img_cv, params):
    """Ch1-2 综合案例：文档几何校正流水线
    预处理 -> 旋转校正 -> 透视变换 -> 双三次插值对比"""
    gray = _ensure_gray_cv(img_cv)
    h, w = gray.shape
    angle = params.get('angle', 15)
    # 旋转
    M = cv2.getRotationMatrix2D((w/2, h/2), angle, 1.0)
    rotated = cv2.warpAffine(gray, M, (w, h))
    # 最近邻插值校正
    corrected_nn = cv2.warpAffine(rotated, cv2.getRotationMatrix2D((w/2, h/2), -angle, 1.0), (w, h),
                                   flags=cv2.INTER_NEAREST)
    # 双三次插值校正
    corrected_bc = cv2.warpAffine(rotated, cv2.getRotationMatrix2D((w/2, h/2), -angle, 1.0), (w, h),
                                   flags=cv2.INTER_CUBIC)
    row = np.hstack([gray, rotated, corrected_nn, corrected_bc])
    result = cv2.cvtColor(row, cv2.COLOR_GRAY2BGR)
    cv2.putText(result, 'Original', (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
    cv2.putText(result, f'Rotated {angle}deg', (w+10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
    cv2.putText(result, 'Nearest Corr', (2*w+10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
    cv2.putText(result, 'Bicubic Corr', (3*w+10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
    return result


def process_case_03_defect(img_cv, params):
    """Ch3 综合案例：零件缺陷检测流水线
    预处理 -> 中值滤波去噪 -> Sobel边缘提取 -> 缺陷热力叠加"""
    gray = _ensure_gray_cv(img_cv)
    denoised = cv2.medianBlur(gray, 5)
    sobel_x = cv2.Sobel(denoised, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(denoised, cv2.CV_64F, 0, 1, ksize=3)
    edge = np.sqrt(sobel_x**2 + sobel_y**2)
    edge = np.clip(edge, 0, 255).astype(np.uint8)
    edge_color = cv2.applyColorMap(edge, cv2.COLORMAP_HOT)
    result = cv2.addWeighted(img_cv, 0.6, edge_color, 0.4, 0)
    cv2.putText(result, 'Case03: MedianBlur(5) + Sobel Edge Overlay (HOT)', 
                (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
    return result


def process_case_04_ct_denoise(img_cv, params):
    """Ch4 综合案例：CT图像去噪流水线
    预处理 -> DFT -> 高斯低通滤波 -> IDFT -> 对比"""
    gray = _ensure_gray_cv(img_cv)
    h, w = gray.shape
    dft = cv2.dft(np.float32(gray), flags=cv2.DFT_COMPLEX_OUTPUT)
    dft_shift = np.fft.fftshift(dft)
    crow, ccol = h // 2, w // 2
    d0 = params.get('d0', 30)
    mask = np.zeros((h, w, 2), np.float32)
    for i in range(h):
        for j in range(w):
            d = np.sqrt((i - crow)**2 + (j - ccol)**2)
            mask[i, j] = np.exp(-d**2 / (2 * d0**2))
    filtered = dft_shift * mask
    idft = cv2.idft(np.fft.ifftshift(filtered))
    denoised = cv2.magnitude(idft[:, :, 0], idft[:, :, 1])
    denoised = cv2.normalize(denoised, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    row = np.hstack([gray, denoised])
    result = cv2.cvtColor(row, cv2.COLOR_GRAY2BGR)
    cv2.putText(result, 'Original (Noisy CT)', (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
    cv2.putText(result, f'GLPF d0={d0} (No Ringing)', (w+10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
    return result


def process_case_05_photo_restore(img_cv, params):
    """Ch5 综合案例：老照片复原流水线
    预处理 -> 去噪(快速NLM) -> 锐化 -> 对比度增强"""
    gray = _ensure_gray_cv(img_cv)
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    blurred = cv2.GaussianBlur(denoised, (0, 0), 2.0)
    sharpened = cv2.addWeighted(denoised, 1.8, blurred, -0.8, 0)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(sharpened)
    row = np.hstack([gray, denoised, enhanced])
    result = cv2.cvtColor(row, cv2.COLOR_GRAY2BGR)
    cv2.putText(result, 'Original (Old Photo)', (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
    cv2.putText(result, 'NLM Denoised', (w//3+10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
    cv2.putText(result, 'Sharpened + CLAHE', (2*w//3+10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
    return result


def process_case_06_drone_veg(img_cv, params):
    """Ch6 综合案例：航拍色彩增强流水线
    预处理 -> RGB->HSV -> 饱和度增强 -> 亮度均衡 -> HSV->RGB"""
    hsv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2HSV)
    s_factor = params.get('saturation', 1.5)
    v_factor = params.get('brightness', 1.1)
    hsv = hsv.astype(np.float32)
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * s_factor, 0, 255)
    hsv[:, :, 2] = np.clip(hsv[:, :, 2] * v_factor, 0, 255)
    hsv = hsv.astype(np.uint8)
    enhanced = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    # CLAHE 在 LAB 亮度通道
    lab = cv2.cvtColor(enhanced, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    l_eq = clahe.apply(l)
    lab_eq = cv2.merge([l_eq, a, b])
    final = cv2.cvtColor(lab_eq, cv2.COLOR_LAB2BGR)
    row = np.hstack([img_cv, enhanced, final])
    result = row
    cv2.putText(result, 'Original (Low Sat)', (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
    cv2.putText(result, 'HSV S+V Enhanced', (img_cv.shape[1]+10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
    cv2.putText(result, '+ LAB CLAHE', (2*img_cv.shape[1]+10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
    return result


def process_case_07_panorama(img_cv, params):
    """Ch7 综合案例：多分辨率金字塔融合流水线
    预处理 -> 高斯金字塔 -> 拉普拉斯金字塔 -> 重建"""
    gray = _ensure_gray_cv(img_cv)
    h, w = gray.shape
    g1 = gray.copy()
    g2 = cv2.GaussianBlur(gray, (31, 31), 8)
    # 拉普拉斯金字塔
    l1 = cv2.subtract(g1.astype(np.int16), cv2.pyrUp(cv2.pyrDown(g1)).astype(np.int16)[:h, :w])
    l1 = np.clip(l1, 0, 255).astype(np.uint8)
    l2 = cv2.subtract(g2.astype(np.int16), cv2.pyrUp(cv2.pyrDown(g2)).astype(np.int16)[:h, :w])
    l2 = np.clip(l2, 0, 255).astype(np.uint8)
    # 融合中间带
    mask = np.zeros((h,), dtype=np.float32)
    mask[w//4:3*w//4] = np.linspace(0, 1, w//2)
    mask_2d = np.tile(mask.reshape((1, w)), (h, 1))
    fused = (l1.astype(np.float32) * (1 - mask_2d) + l2.astype(np.float32) * mask_2d).astype(np.uint8)
    row = np.hstack([l1, mask_2d, l2, fused])
    row = np.clip(row, 0, 255).astype(np.uint8)
    result = cv2.cvtColor(row, cv2.COLOR_GRAY2BGR)
    cv2.putText(result, 'Laplacian L1', (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
    cv2.putText(result, 'Blend Mask', (w+10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
    cv2.putText(result, 'Laplacian L2', (2*w+10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
    cv2.putText(result, 'Fused Result', (3*w+10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
    return result


def process_case_08_jpeg_opt(img_cv, params):
    """Ch8 综合案例：JPEG压缩优化流水线
    预处理 -> JPEG 多质量压缩 -> PSNR计算 -> 对比展示"""
    gray = _ensure_gray_cv(img_cv)
    h, w = gray.shape
    quality = params.get('quality', 75)
    encode_params = [cv2.IMWRITE_JPEG_QUALITY, quality]
    _, enc = cv2.imencode('.jpg', gray, encode_params)
    compressed = cv2.imdecode(enc, cv2.IMREAD_GRAYSCALE)
    # PSNR
    mse = np.mean((gray.astype(np.float64) - compressed.astype(np.float64))**2)
    psnr = 100 if mse == 0 else 20 * np.log10(255.0 / np.sqrt(mse))
    ratio = gray.nbytes / max(len(enc), 1)
    row = np.hstack([gray, compressed])
    result = cv2.cvtColor(row, cv2.COLOR_GRAY2BGR)
    cv2.putText(result, f'Original', (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
    cv2.putText(result, f'Q={quality} | PSNR={psnr:.1f}dB | CR={ratio:.1f}:1',
                (w+10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,255), 2)
    return result


def process_case_09_pcb_inspect(img_cv, params):
    """Ch9 综合案例：PCB缺陷检测流水线
    预处理 -> 灰度 -> 二值化 -> 开运算 -> 形态学梯度 -> 缺陷叠加"""
    gray = _ensure_gray_cv(img_cv)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    opened = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)
    gradient = cv2.morphologyEx(opened, cv2.MORPH_GRADIENT, kernel)
    # 缺陷叠加
    defect_mask = cv2.cvtColor(gradient, cv2.COLOR_GRAY2BGR)
    defect_mask[:, :, 2] = gradient
    result = cv2.addWeighted(img_cv, 0.7, defect_mask, 0.3, 0)
    cv2.putText(result, 'Case09: Otsu -> Open(3x3) -> MorphGradient (Red=Defects)',
                (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
    return result


def process_case_10_water_extract(img_cv, params):
    """Ch10 综合案例：遥感水体提取流水线
    预处理 -> 灰度 -> Otsu -> 形态学后处理 -> 水体叠加"""
    gray = _ensure_gray_cv(img_cv)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    closed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    opened = cv2.morphologyEx(closed, cv2.MORPH_OPEN, kernel)
    water_mask = cv2.cvtColor(opened, cv2.COLOR_GRAY2BGR)
    water_mask[:, :, 0] = opened
    result = cv2.addWeighted(img_cv, 0.7, water_mask, 0.3, 0)
    cv2.putText(result, 'Case10: Otsu -> Close(5x5) -> Open(5x5) (Blue=Water)',
                (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
    return result


def process_case_11_part_classify(img_cv, params):
    """Ch11 综合案例：零件分类识别流水线
    预处理 -> 二值化 -> 轮廓提取 -> 形状特征计算 -> 标注"""
    gray = _ensure_gray_cv(img_cv)
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    result = img_cv.copy()
    min_area = (gray.shape[0] * gray.shape[1]) * 0.005
    colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]
    idx = 0
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < min_area:
            continue
        M = cv2.moments(cnt)
        cx = int(M['m10'] / M['m00']) if M['m00'] != 0 else 0
        cy = int(M['m01'] / M['m00']) if M['m00'] != 0 else 0
        perimeter = cv2.arcLength(cnt, True)
        circularity = 4 * np.pi * area / (perimeter * perimeter) if perimeter > 0 else 0
        approx = cv2.approxPolyDP(cnt, 0.02 * perimeter, True)
        vertices = len(approx)
        color = colors[idx % len(colors)]
        cv2.drawContours(result, [cnt], -1, color, 2)
        label = f'#{idx+1}: A={area:.0f} V={vertices}'
        if circularity > 0.85:
            label += ' ~Circle'
        elif vertices <= 6:
            label += ' ~Polygon'
        else:
            label += ' ~Complex'
        cv2.putText(result, label, (cx - 30, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        idx += 1
    cv2.putText(result, f'Case11: Found {idx} parts (filtered >{min_area:.0f}px)',
                (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
    return result


def process_case_12_traffic_sign(img_cv, params):
    """Ch12 综合案例：交通标志检测流水线
    预处理 -> Canny边缘 -> ROI筛选 -> 霍夫圆 + Harris角点"""
    gray = _ensure_gray_cv(img_cv)
    blurred = cv2.GaussianBlur(gray, (5, 5), 1.0)
    edges = cv2.Canny(blurred, 50, 150)
    # 霍夫圆检测
    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=min(gray.shape)//8,
                                param1=100, param2=35, minRadius=15, maxRadius=min(gray.shape)//3)
    result = img_cv.copy()
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i, c in enumerate(circles[0, :5]):
            cv2.circle(result, (c[0], c[1]), c[2], (0, 255, 255), 2)
            cv2.circle(result, (c[0], c[1]), 3, (0, 0, 255), -1)
            cv2.putText(result, f'Sign#{i+1}', (c[0]-20, c[1]-c[2]-5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,255), 2)
    # Harris 角点（红色小点）
    harris = cv2.cornerHarris(gray, blockSize=3, ksize=3, k=0.04)
    harris_dilate = cv2.dilate(harris, None)
    thresh = 0.01 * harris.max()
    ys, xs = np.where(harris_dilate > thresh)
    for x, y in zip(xs[::3], ys[::3]):
        cv2.circle(result, (x, y), 2, (0, 0, 255), -1)
    cv2.putText(result, f'Case12: Canny+HoughCircles(Yellow) + Harris(Red dots, sub-sampled)',
                (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
    return result


# ========================= 操作映射表 =========================
OPERATION_MAP = {
    'sampling_demo':           process_sampling_demo,
    'quantization_demo':       process_quantization_demo,
    'resolution_compare':      process_resolution_compare,
    'pixel_neighbors':         process_pixel_neighbors,
    'distance_metrics':        process_distance_metrics,
    'interpolation_demo':      process_interpolation_demo,
    'image_inversion':         process_image_inversion,
    'log_transform':           process_log_transform,
    'contrast_stretch':        process_contrast_stretch,
    'histogram_equalization':  process_histogram_equalization,
    'clahe':                   process_clahe,
    'gamma_correction':        process_gamma_correction,
    'median_blur':             process_median_blur,
    'gaussian_blur':           process_gaussian_blur,
    'bilateral_filter':        process_bilateral_filter,
    'laplacian':               process_laplacian,
    'unsharp_mask':            process_unsharp_mask,
    'sobel_sharpen':           process_sobel_sharpen,
    'ideal_lowpass':           process_ideal_lowpass,
    'ideal_highpass':          process_ideal_highpass,
    'butterworth_lowpass':     process_butterworth_lowpass,
    'butterworth_highpass':    process_butterworth_highpass,
    'gaussian_lowpass':        process_gaussian_lowpass,
    'gaussian_highpass':       process_gaussian_highpass,
    'bandpass_filter':         process_bandpass_filter,
    'gaussian_noise':          process_gaussian_noise,
    'sp_noise':                process_sp_noise,
    'mean_filter_restore':     process_mean_filter_restore,
    'median_restore':          process_median_restore,
    'nlm_denoise':             process_nlm_denoise,
    'wiener_filter':           process_wiener_filter,
    'sobel':                   process_sobel,
    'canny':                   process_canny,
    'rgb_split':               process_rgb_split,
    'rgb_to_hsv':              process_rgb_to_hsv,
    'hue_adjust':              process_hue_adjust,
    'saturation_adjust':       process_saturation_adjust,
    'brightness_adjust':       process_brightness_adjust,
    'color_balance':           process_color_balance,
    'pseudo_color':            process_pseudo_color,
    'color_hist_eq':           process_color_hist_eq,
    'gaussian_pyramid':        process_gaussian_pyramid,
    'laplacian_pyramid':       process_laplacian_pyramid,
    'pyramid_blend':           process_pyramid_blend,
    'dwt_denoise':             process_dwt_denoise,
    'dwt_edge_enhance':        process_dwt_edge_enhance,
    'dct_visualize':           process_dct_visualize,
    'jpeg_simulate':           process_jpeg_simulate,
    'jpeg_compare':            process_jpeg_compare,
    'binary_rle':              process_binary_rle,
    'binary_huffman':          process_binary_huffman,
    'erosion_dilation':        process_erosion_dilation,
    'open_close':              process_open_close,
    'morph_gradient':          process_morph_gradient,
    'tophat':                  process_tophat,
    'blackhat':                process_blackhat,
    'skeletonize':             process_skeletonize,
    'otsu_threshold':          process_otsu_threshold,
    'adaptive_threshold':      process_adaptive_threshold,
    'kmeans_segment':          process_kmeans_segment,
    'mean_shift_segment':      process_mean_shift_segment,
    'watershed':               process_watershed,
    'grabcut':                 process_grabcut,
    'contour_extract':         process_contour_extract,
    'convex_hull':             process_convex_hull,
    'min_enclosing':           process_min_enclosing,
    'contour_approx':          process_contour_approx,
    'hu_moments':              process_hu_moments,
    'shape_match':             process_shape_match,
    'fourier_descriptor':      process_fourier_descriptor,
    'template_matching':       process_template_matching,
    'hough_lines':             process_hough_lines,
    'hough_circles':           process_hough_circles,
    'corner_harris':           process_corner_harris,
    'sift_features':           process_sift_features,
    'hog_features':            process_hog_features,
    'prewitt':                 process_prewitt,
    'roberts':                 process_roberts,
    'region_growing':          process_region_growing,
    'case_01_satellite':       process_case_01_satellite,
    'case_02_document':        process_case_02_document,
    'case_03_defect':          process_case_03_defect,
    'case_04_ct_denoise':      process_case_04_ct_denoise,
    'case_05_photo_restore':   process_case_05_photo_restore,
    'case_06_drone_veg':       process_case_06_drone_veg,
    'case_07_panorama':        process_case_07_panorama,
    'case_08_jpeg_opt':        process_case_08_jpeg_opt,
    'case_09_pcb_inspect':     process_case_09_pcb_inspect,
    'case_10_water_extract':   process_case_10_water_extract,
    'case_11_part_classify':   process_case_11_part_classify,
    'case_12_traffic_sign':    process_case_12_traffic_sign,
}


# ========================= 路由 =========================

@app.context_processor
def inject_user():
    return {'current_user': get_current_user()}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chapters')
@login_required
def chapters():
    return render_template('chapters.html', user=get_current_user())

CHAPTER_TITLES = {
    1:  ('第一章：绪论 & 第二章：数字图像基础', '01-02'),
    3:  ('第三章：灰度变换与空间滤波', '03'),
    4:  ('第四章：频率域滤波', '04'),
    5:  ('第五章：图像复原与重建', '05'),
    6:  ('第六章：彩色图像处理', '06'),
    7:  ('第七章：小波变换与多分辨率处理', '07'),
    8:  ('第八章：图像压缩', '08'),
    9:  ('第九章：形态学图像处理', '09'),
    10: ('第十章：图像分割', '10'),
    11: ('第十一章：表示和描述', '11'),
    12: ('第十二章：目标检测与识别', '12'),
}

@app.route('/chapter/<int:chapter_id>')
@login_required
def chapter_detail(chapter_id):
    if chapter_id not in CHAPTER_TITLES:
        return "章节不存在", 404
    title, badge = CHAPTER_TITLES[chapter_id]
    return render_template('chapter_detail.html',
                           chapter_id=chapter_id,
                           chapter_title=title,
                           chapter_badge=badge)

@app.route('/download/ppt/<filename>')
def download_ppt(filename):
    """提供课件PPT下载"""
    ppt_dir = os.path.join(os.path.dirname(__file__), 'ppt')
    return send_from_directory(ppt_dir, filename, as_attachment=True)

@app.route('/images/<path:filename>')
def serve_case_images(filename):
    """提供案例素材图片访问"""
    images_dir = os.path.join(os.path.dirname(__file__), 'images')
    return send_from_directory(images_dir, filename)

# ════════════════════════════════════════════
# AI分析缓存（同图同参数不重复调API）
# ════════════════════════════════════════════
_ai_analysis_cache = {}

@app.route('/compare')
@login_required
def compare():
    group_id = request.args.get('group', '')
    chapter_id = request.args.get('chapter', '1')
    return render_template('compare.html',
                           group_id=group_id,
                           chapter_id=int(chapter_id))

@app.route('/operation')
@login_required
def operation():
    return render_template('operation.html')

@app.route('/process', methods=['POST'])
@login_required
def process():
    try:
        image_file = request.files.get('image')
        if not image_file:
            return jsonify({'status': 'error', 'message': '未收到图片，请先上传一张图片后再处理'}), 400

        operation = request.form.get('operation', '')
        params_str = request.form.get('params', '{}')
        try:
            params = json.loads(params_str)
        except:
            params = {}

        try:
            pil_img = Image.open(image_file.stream).convert('RGB')
        except Exception:
            return jsonify({'status': 'error', 'message': '图像文件读取失败，请确认文件为有效的图片格式'}), 400
        img_cv = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

        if operation not in OPERATION_MAP:
            return jsonify({'status': 'error', 'message': f'不支持的操作「{operation}」，请选择有效的处理算法'}), 400

        result_cv = OPERATION_MAP[operation](img_cv, params)

        if len(result_cv.shape) == 2:
            result_pil = Image.fromarray(result_cv, mode='L')
        else:
            result_pil = Image.fromarray(cv2.cvtColor(result_cv, cv2.COLOR_BGR2RGB))

        b64 = img_to_base64(result_pil)
        op_name = OPERATION_NAMES.get(operation, operation)

        # 生成参数摘要
        params_summary_parts = []
        for k, v in params.items():
            if k in ('mode',):
                continue
            if isinstance(v, float) and v == int(v):
                v = int(v)
            params_summary_parts.append(f'{k}={v}')
        params_summary = ', '.join(params_summary_parts) if params_summary_parts else None

        # 主动AI分析：同图同参数缓存，避免重复调API
        ai_analysis = _generate_proactive_analysis(
            original_b64=img_to_base64(pil_img),
            result_b64=b64,
            operation=operation,
            params=params,
            op_name=op_name
        )

        return jsonify({
            'status': 'success',
            'result_image': b64,
            'image_base64': b64,
            'operation_name': op_name,
            'params_summary': params_summary,
            'ai_analysis': ai_analysis
        })

    except Exception as e:
        err_msg = str(e)
        # 中文化常见错误
        err_lower = err_msg.lower()
        if 'grayscale' in err_lower or 'cannot write mode' in err_lower or '单通道' in err_msg:
            err_msg = '该图像为灰度图，请上传彩色图像'
        elif 'shape' in err_lower and ('empty' in err_lower or 'none' in err_lower):
            err_msg = '未收到有效图像数据，请重新上传'
        elif 'size' in err_lower or 'too small' in err_lower or 'dimension' in err_lower:
            err_msg = '图像尺寸过小，无法进行该操作'
        elif 'memory' in err_lower or 'allocation' in err_lower:
            err_msg = '图像过大导致内存不足，请使用较小尺寸的图像'
        elif 'not supported' in err_lower or 'unsupported' in err_lower:
            err_msg = '该图像格式不受支持，请上传 JPG/PNG/BMP/TIFF 图片'
        elif 'corrupt' in err_lower or 'truncated' in err_lower:
            err_msg = '图像文件损坏或不完整，请重新选择文件'
        elif len(err_msg) > 200:
            err_msg = '处理失败，请检查输入参数后重试'

        # 主动AI引导：错误时同步生成引导提示
        ai_guidance = _generate_error_guidance(
            operation=operation,
            params=params,
            error_msg=err_msg
        )
        return jsonify({
            'status': 'error',
            'message': err_msg,
            'ai_guidance': ai_guidance
        }), 500

# ────────────── AI 量化分析辅助函数 ──────────────

def _base64_to_cv2(b64_str):
    """将 base64 字符串解码为 OpenCV BGR 图像"""
    if ',' in b64_str:
        b64_str = b64_str.split(',', 1)[1]
    img_bytes = base64.b64decode(b64_str)
    np_arr = np.frombuffer(img_bytes, np.uint8)
    return cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

def _ensure_gray(img):
    """统一转灰度图"""
    if len(img.shape) == 3:
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img

def _align_images(img_a, img_b):
    """将两图对齐到相同尺寸"""
    if img_a.shape[:2] != img_b.shape[:2]:
        h = min(img_a.shape[0], img_b.shape[0])
        w = min(img_a.shape[1], img_b.shape[1])
        img_a = img_a[:h, :w]
        img_b = img_b[:h, :w]
    return img_a, img_b

def _image_mean(img_gray):
    return float(np.mean(img_gray))

def _image_std(img_gray):
    return float(np.std(img_gray))

def _rms_contrast(img_gray):
    """RMS 对比度：像素值标准差的归一化度量"""
    return float(np.std(img_gray.astype(np.float64)))

def _image_entropy(img_gray):
    """计算图像信息熵（bit）"""
    hist = cv2.calcHist([img_gray], [0], None, [256], [0, 256])
    hist = hist.ravel() / hist.sum()
    hist = hist[hist > 0]
    return float(-np.sum(hist * np.log2(hist)))

def _laplacian_variance(img_gray):
    """拉普拉斯方差——图像锐度指标"""
    lap = cv2.Laplacian(img_gray, cv2.CV_64F)
    return float(lap.var())

def _psnr(img_a_gray, img_b_gray):
    """峰值信噪比 PSNR (dB)"""
    mse = np.mean((img_a_gray.astype(np.float64) - img_b_gray.astype(np.float64)) ** 2)
    if mse == 0:
        return float('inf')
    return float(20 * np.log10(255.0 / np.sqrt(mse)))

def _mse(img_a_gray, img_b_gray):
    """均方误差 MSE"""
    return float(np.mean((img_a_gray.astype(np.float64) - img_b_gray.astype(np.float64)) ** 2))

def _mae(img_a_gray, img_b_gray):
    """平均绝对误差 MAE"""
    return float(np.mean(np.abs(img_a_gray.astype(np.float64) - img_b_gray.astype(np.float64))))

def _edge_density(img_gray):
    """Canny 边缘密度（边缘像素占比）"""
    edges = cv2.Canny(img_gray, 50, 150)
    return float(np.count_nonzero(edges) / edges.size)

def _gradient_magnitude_mean(img_gray):
    """Sobel 梯度幅值均值"""
    gx = cv2.Sobel(img_gray, cv2.CV_64F, 1, 0, ksize=3)
    gy = cv2.Sobel(img_gray, cv2.CV_64F, 0, 1, ksize=3)
    mag = np.sqrt(gx ** 2 + gy ** 2)
    return float(np.mean(mag))

def _histogram_distance(img_a_gray, img_b_gray):
    """计算直方图 Bhattacharyya 距离和 KL 散度"""
    hist_a = cv2.calcHist([img_a_gray], [0], None, [256], [0, 256]).ravel()
    hist_b = cv2.calcHist([img_b_gray], [0], None, [256], [0, 256]).ravel()
    eps = 1e-10
    hist_a = (hist_a + eps) / (hist_a.sum() + eps * 256)
    hist_b = (hist_b + eps) / (hist_b.sum() + eps * 256)

    bc = np.sum(np.sqrt(hist_a * hist_b))
    bhattacharyya = -np.log(max(bc, eps))
    kl_div = np.sum(hist_a * np.log(hist_a / hist_b))
    return float(bhattacharyya), float(kl_div)

def _count_connected_components(img_gray):
    """二值图像的连通域数量"""
    _, binary = cv2.threshold(img_gray, 127, 255, cv2.THRESH_BINARY)
    num_labels, _, _, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)
    return num_labels - 1  # 减去背景

def _frequency_energy_ratio(img_gray):
    """频谱能量分布：高频能量 / 总能量"""
    f = np.fft.fft2(img_gray.astype(np.float64))
    fshift = np.fft.fftshift(f)
    mag = np.abs(fshift)
    rows, cols = mag.shape
    crow, ccol = rows // 2, cols // 2
    r = 30
    mask_center = np.zeros((rows, cols), dtype=np.float64)
    mask_center[crow - r:crow + r, ccol - r:ccol + r] = 1
    low_energy = np.sum((mag * mask_center) ** 2)
    total_energy = np.sum(mag ** 2)
    if total_energy == 0:
        return 0.0
    return float(1.0 - low_energy / total_energy)


# ════════════════════════════════════════════
# 操作分类映射（用于专项分析维度选择）
# ════════════════════════════════════════════

DENOISE_OPS = {
    'mean_filter_restore', 'median_restore', 'nlm_denoise',
    'wiener_filter', 'bilateral_filter', 'dwt_denoise'
}

NOISE_OPS = {'gaussian_noise', 'sp_noise'}

EDGE_OPS = {
    'sobel', 'canny', 'laplacian', 'sobel_sharpen',
    'unsharp_mask', 'dwt_edge_enhance', 'prewitt', 'roberts'
}

FREQ_OPS = {
    'ideal_lowpass', 'ideal_highpass', 'butterworth_lowpass',
    'butterworth_highpass', 'gaussian_lowpass', 'gaussian_highpass',
    'bandpass_filter',
    'fourier_transform', 'fft_magnitude_phase', 'dct_visualize',
    'jpeg_simulate', 'jpeg_compare'
}

MORPH_OPS = {
    'erosion_dilation', 'open_close', 'morph_gradient',
    'tophat', 'blackhat', 'skeletonize'
}

SEGMENT_OPS = {
    'otsu_threshold', 'adaptive_threshold', 'kmeans_segment',
    'mean_shift_segment', 'watershed', 'grabcut', 'region_growing'
}

BASICS_OPS = {
    'sampling_demo', 'quantization_demo', 'resolution_compare',
    'pixel_neighbors', 'distance_metrics', 'interpolation_demo'
}

DETECT_OPS = {
    'template_matching', 'hough_lines', 'hough_circles',
    'corner_harris', 'sift_features', 'hog_features'
}

HIST_OPS = {
    'histogram_equalization', 'clahe', 'gamma_correction',
    'contrast_stretch', 'log_transform', 'image_inversion',
    'color_hist_eq'
}

COLOR_OPS = {
    'rgb_split', 'rgb_to_hsv', 'hue_adjust', 'saturation_adjust',
    'brightness_adjust', 'color_balance', 'pseudo_color'
}


# ════════════════════════════════════════════
# 理论论述库（按操作类别）
# ════════════════════════════════════════════

THEORY_LIBRARY = {
    'sobel': (
        "Sobel算子通过计算图像亮度函数的一阶梯度近似来检测边缘。其核心是两组3×3的卷积核，"
        "分别对水平方向和垂直方向求导。梯度幅值反映了该像素点亮度变化的剧烈程度——幅值越大，"
        "越可能是边缘。边缘密度和梯度均值是衡量边缘检测强度的两个关键指标。"
    ),
    'canny': (
        "Canny边缘检测器是公认的最优边缘检测算法之一（冈萨雷斯第10章）。它遵循三条准则："
        "低错误率（不漏检、不错检）、良好定位（检测点靠近真实边缘中心）、单一边缘响应。"
        "Canny通过高斯平滑→梯度计算→非极大值抑制→双阈值连接四步完成，双阈值的设定直接决定"
        "边缘密度和连续性。"
    ),
    'laplacian': (
        "拉普拉斯算子是基于二阶导数的边缘检测方法，对灰度突变更为敏感。其缺点是对噪声极其"
        "敏感——因为二阶导会放大高频噪声。通常需要先进行高斯平滑（即LoG——高斯拉普拉斯算子）"
        "来抑制噪声。拉普拉斯方差较小说明图像较平滑，较大则说明纹理和细节丰富。"
    ),
    'unsharp_mask': (
        "非锐化掩蔽（Unsharp Masking）源自印刷行业，原理是从原图中减去其模糊版本以增强细节。"
        "数学上相当于在原图上叠加高通滤波结果。锐度提升程度取决于σ（模糊半径）和权重因子。"
        "过度的锐化会引入光晕伪影（halo artifact），表现为边缘附近的亮度振铃。"
    ),
    'sobel_sharpen': (
        "Sobel锐化利用Sobel梯度幅值来增强边缘。在处理后的图像中叠加梯度信息，"
        "使边缘区域的对比度得到加强。梯度幅值加权控制锐化强度：权重越大边缘越锐利，"
        "但噪声也会被同步放大。"
    ),
    'dwt_edge_enhance': (
        "小波边缘增强利用DWT将图像分解为多级子带（LL/LH/HL/HH），通过放大高频子带"
        "（LH、HL、HH）的系数来增强边缘和细节，再逆变换重建。这种方法可以独立控制"
        "不同尺度和方向的增强强度，比空间域锐化更精细。"
    ),
    'gaussian_pyramid': (
        "高斯金字塔通过对图像逐级高斯低通滤波+降采样（隔行隔列采样）构建多分辨率表示"
        "（冈萨雷斯第7章）。第l层 G_l=down(G_{l-1}*g_σ)，每层尺寸约为上一层的1/4。"
        "低层保留丰富的细节信息，高层反映全局结构。高斯金字塔是尺度空间分析的基础，"
        "也是构建拉普拉斯金字塔和SIFT特征提取的前置步骤。"
    ),
    'laplacian_pyramid': (
        "拉普拉斯金字塔保存高斯金字塔相邻层之间的高频残差（冈萨雷斯第7章）。"
        "第l层 L_l = G_l - up(G_{l+1})，即当前高斯层减去上一层上采样的结果。"
        "每层对应一个带通信号——包含边缘、纹理和细节信息。从顶层开始通过"
        "G_l = L_l + up(G_{l+1}) 可精确重建原始图像，是图像融合和压缩的核心工具。"
    ),
    'pyramid_blend': (
        "多分辨率融合（Burt-Adelson方法）在拉普拉斯金字塔域中加权融合两幅图像（冈萨雷斯第7章）。"
        "步骤：①构建两图的拉普拉斯金字塔；②对每层构建权重高斯金字塔（基于梯度/灰度）；"
        "③L_F^l = W_A^l·L_A^l + W_B^l·L_B^l；④从顶层开始重建。"
        "这种方法避免直接拼接产生的接缝伪影，同时保留全局结构和局部细节。"
    ),
    'dwt_denoise': (
        "小波降噪利用离散小波变换（DWT）将图像分解为低频近似子带（LL）和高频细节子带"
        "（LH/HL/HH），噪声主要集中在小波系数较小的高频子带（冈萨雷斯第7章）。"
        "通过阈值处理（软阈值 η(w)=sign(w)·max(|w|-λ,0) 或硬阈值）抑制噪声系数后，"
        "逆DWT重建去噪图像。VisuShrink通用阈值 λ=σ√(2lnN)，其中σ为噪声标准差。"
    ),

    'histogram_equalization': (
        "直方图均衡化通过将灰度概率密度函数变换为均匀分布来增强对比度（冈萨雷斯3.3节）。"
        "其变换函数是累积分布函数CDF的离散近似。均衡化后图像熵应趋近于理论最大值log₂(L)=8 bit"
        "（对256级灰度），但可能产生不自然的过度增强和棋盘效应。"
    ),
    'clahe': (
        "CLAHE（对比度受限自适应直方图均衡化）解决了全局直方图均衡化的两个缺陷："
        "噪声放大和不均匀增强。它将图像划分为小区域（tile），在每个区域内独立均衡化，"
        "并通过对比度限幅（clip limit）抑制噪声放大。clip limit越小，增强越温和但噪声抑制越好。"
    ),
    'gamma_correction': (
        "伽马校正（幂律变换）源于CRT显示器的非线性响应特性。s = c·r^γ 中，γ<1 拉伸暗区压缩亮区"
        "（变亮），γ>1 压缩暗区拉伸亮区（变暗）。人眼对暗区的亮度变化更敏感（韦伯定律），"
        "因此在显示系统中通常使用γ≈2.2的校正。"
    ),
    'contrast_stretch': (
        "对比度拉伸（线性拉伸）将原始灰度范围 [min, max] 线性映射到 [0, 255]。"
        "这是最简单的对比度增强方法，在不改变直方图形状的前提下充分利用显示动态范围。"
        "缺点是容易受极端像素值（outliers）的干扰。"
    ),
    'log_transform': (
        "对数变换 s = c·log(1+r) 将窄范围的低灰度值映射到宽范围的输出灰度值，"
        "适合增强图像暗区的细节。同时将宽范围的高灰度值压缩，避免亮区过曝。"
        "常应用于傅里叶频谱的可视化——频谱动态范围极大，取对数后便于观察。"
    ),
    'image_inversion': (
        "图像反转 s = L-1-r 是最简单的灰度变换。对灰度图为负片效果，对二值图为黑白翻转。"
        "反转后图像熵不变（灰度分布只是左右镜像），但在视觉上暗区细节可能更容易辨认。"
    ),
    'median_blur': (
        "中值滤波是经典的非线性统计排序滤波器（冈萨雷斯第5章）。它将邻域内像素的灰度值排序后取中值"
        "替代中心像素。中值滤波对椒盐噪声特别有效——因为孤立脉冲点在中值排序中会被邻域值替代，"
        "且不会引入邻域中不存在的新灰度值。核尺寸越大去噪越强，但细节和细线可能丢失。"
        "中值滤波属于非线性操作，不满足叠加原理，边缘保持能力优于线性均值滤波。"
    ),
    'gaussian_blur': (
        "高斯滤波是线性加权平均平滑滤波器（冈萨雷斯第3章），核心是二维高斯核。"
        "二维高斯函数 G(x,y)=1/(2πσ²)·exp(-(x²+y²)/(2σ²))，σ控制平滑程度——σ越大平滑越强。"
        "高斯核具有旋转对称性，傅里叶变换仍为高斯函数（频域低通）。"
        "核半径≈⌈3σ⌉（覆盖99.7%能量），实际使用需归一化保持亮度。"
        "高斯滤波不会产生振铃效应，比理想低通和巴特沃斯滤波器更平滑自然。"
    ),

    'gaussian_noise': (
        "高斯噪声的概率密度函数服从正态分布，是最常见的电子噪声模型。其影响可通过PSNR评估——"
        "PSNR越低说明噪声越严重。高斯噪声在频域表现为全频带均匀分布（白噪声特性），"
        "因此低通滤波可有效抑制。σ参数控制噪声强度，σ越大PSNR越低。"
    ),
    'sp_noise': (
        "椒盐噪声（脉冲噪声）表现为随机出现的白点和黑点，通常由传感器故障或传输错误引起。"
        "中值滤波是最有效的去除方法，因为中值滤波对脉冲噪声有天然的鲁棒性——"
        "孤立脉冲点在中值排序中会被邻域像素值替代。"
    ),

    'mean_filter_restore': (
        "均值滤波（算术平均）是最简单的空间域线性滤波器。它用邻域像素的算术平均值替代中心像素，"
        "本质上是低通滤波。对高斯噪声有效（均值为0时），但对椒盐噪声和边缘保持效果差——"
        "会同时模糊噪声和边缘。核越大，去噪越强但模糊越严重，这是去噪与边缘保持的根本矛盾。"
    ),
    'median_restore': (
        "中值滤波是经典的非线性排序统计滤波器，尤其适合椒盐噪声去除。它的关键优势在于"
        "能在去噪的同时保留边缘锐度——因为中值不会引入邻域中不存在的新值。"
        "对高斯噪声效果逊于均值滤波，但对脉冲噪声的破坏性远小于均值滤波。"
    ),
    'bilateral_filter': (
        "双边滤波是一种保边平滑滤波器，同时考虑空间邻近度（空间域核）和像素值相似度（值域核）。"
        "两个高斯核的乘积构成最终权重：空间上近的权重大，像素值近的权重大。"
        "这使得它能在平滑均匀区域的同时保持边缘不被模糊。σ_color越大去噪越强，"
        "σ_space越大平滑范围越广。代价是计算复杂度O(Nr²)显著高于普通滤波。"
    ),
    'nlm_denoise': (
        "非局部均值（NLM）去噪是Buades等人提出的里程碑式算法。核心思想是利用图像的自相似性："
        "用整张图中所有与当前patch相似的区域的加权平均来估计当前像素值。"
        "NLM对纹理丰富的图像效果优越，能保留精细结构，但计算代价极高。"
    ),
    'wiener_filter': (
        "维纳滤波器是频域自适应滤波器，目标是最小化估计值与真实值之间的均方误差。"
        "它根据局部信噪比自动调整滤波强度——信噪比高的区域保留原值，信噪比低的区域加强平滑。"
        "维纳滤波需要估计噪声功率谱，这一先验知识在实际中往往难以精确获取。"
    ),

    'ideal_lowpass': (
        "理想低通滤波器在频域中直接截断高频成分（矩形窗函数）。虽然概念简单，但在空间域会产生"
        "严重的振铃效应（Gibbs现象）——因为矩形窗的傅里叶逆变换是sinc函数。"
        "实际应用中通常避免使用理想滤波器，转而使用巴特沃斯或高斯滤波器。"
    ),
    'ideal_highpass': (
        "理想高通滤波器与理想低通滤波器对偶——保留高频截断低频。同样存在振铃效应。"
        "高通滤波提取边缘和细节信息，但过强的截断会使图像趋于全黑（直流分量被完全去除）。"
    ),
    'butterworth_lowpass': (
        "巴特沃斯滤波器是理想滤波器的平滑过渡版本，在通带和阻带之间提供了可控的过渡带。"
        "阶数n控制过渡带的陡峭程度：n=1最平滑（无振铃），n→∞趋近理想滤波器。"
        "实际应用通常选n=2（巴特沃斯二阶），在锐截止与无振铃之间取得良好平衡。"
    ),
    'butterworth_highpass': (
        "巴特沃斯高通滤波器平滑地保留高频成分。与低通版本类似，阶数控制过渡带陡峭度。"
        "高通滤波后的图像主要保留边缘和纹理，适合作为后续边缘检测或锐化的预处理步骤。"
    ),
    'gaussian_lowpass': (
        "高斯低通滤波器是唯一在空间域和频域都具有高斯形状的滤波器，其傅里叶逆变换也是高斯的。"
        "它在空间域不会产生振铃效应，平滑效果自然，因此在实践中广泛应用。"
        "截止频率D₀控制平滑程度：D₀越小，保留的低频越少，图像越模糊。"
    ),
    'gaussian_highpass': (
        "高斯高通滤波器平滑地提取图像高频成分（边缘和细节），无振铃效应。"
        "高通滤波结果常叠加回原图以实现锐化（高频增强）。"
    ),
    'bandpass_filter': (
        "带通滤波器保留特定频率范围内的成分，抑制过低和过高的频率。"
        "在图像处理中，带通滤波可用于提取特定尺度的纹理模式或去除周期性噪声。"
        "带宽和中心频率的选择取决于应用目标。"
    ),
    'dct_visualize': (
        "离散余弦变换（DCT）将图像从空间域变换到频率域，是JPEG压缩的核心。"
        "DCT将图像能量集中在低频系数上——左上角（低序数系数）通常包含大部分能量。"
        "通过量化高频系数（DCT系数的右下部分）可以实现有效压缩。"
    ),
    'jpeg_simulate': (
        "JPEG压缩通过DCT变换→量化→熵编码三步骤实现有损压缩。量化表控制压缩率和质量："
        "量化步长越大，高频系数被舍去越多，压缩率越高但块效应（blocking artifact）越明显。"
    ),
    'jpeg_compare': (
        "JPEG压缩质量对比通过不同量化步长展示压缩率与图像质量的权衡（冈萨雷斯第8章）。"
        "量化步长越大，高频DCT系数被舍去越多，压缩率越高但块效应越明显。"
        "PSNR是常用客观指标——PSNR>40dB表示视觉无损，30~40dB为高质量，"
        "<30dB开始出现可见失真。JPEG2000使用小波变换，无块效应但计算更复杂。"
    ),
    'binary_rle': (
        "游程编码（RLE）是一种无损压缩方法，通过记录连续相同像素值的个数来压缩数据"
        "（冈萨雷斯第8章）。对二值图像效果最佳——大块相同像素产生极长的游程。"
        "RLE编码效率取决于图像中连续相同值的频率，随机噪声图像压缩效果差。"
        "编码格式通常为（游程长度，像素值）对，解码时直接展开即可恢复原图。"
    ),
    'binary_huffman': (
        "哈夫曼编码是一种最优前缀编码（冈萨雷斯第8章），通过为高频符号分配短码、"
        "低频符号分配长码来最小化平均码长。平均码长接近信息熵 H = -Σpᵢlog₂pᵢ。"
        "对二值图像，0/1的概率分布决定编码效率；熵编码是无损压缩的最后一步，"
        "JPEG中哈夫曼编码对RLE输出符号再次压缩，进一步去除编码冗余。"
    ),

    'otsu_threshold': (
        "Otsu阈值法通过最大化类间方差自动确定最优阈值。其数学本质是在灰度直方图上寻找"
        "使两类（前景/背景）分离度最大的分割点。类间方差σ²_B = ω₀ω₁(μ₀-μ₁)²，"
        "Otsu方法遍历所有可能阈值取最大σ²_B。它对双峰直方图效果最佳，单峰或多峰时效果下降。"
    ),
    'adaptive_threshold': (
        "自适应阈值根据每个像素的局部邻域计算不同的阈值，解决了全局阈值在光照不均图像上"
        "效果差的问题。邻域大小是核心参数：太小则对噪声敏感，太大则失去局部适应性。"
    ),
    'kmeans_segment': (
        "K-means聚类分割将像素颜色/灰度值分为K个簇，每个簇代表一个分割区域。"
        "聚类中心通过迭代最小化簇内平方误差来优化。K值的选取直接影响分割粒度——"
        "K过小导致欠分割，K过大导致过分割。"
    ),
    'watershed': (
        "分水岭算法将灰度图像视为地形图，通过模拟水浸过程来分割区域。"
        "其核心是找到分水线（区域边界），对粘连目标分离效果极佳。"
        "但原始分水岭容易过分割，通常需要标记前景和背景来控制。"
    ),
    'mean_shift_segment': (
        "Mean Shift（均值漂移）分割是一种基于核密度梯度估计的无监督聚类方法（冈萨雷斯第10章）。"
        "每个像素在5维联合特征空间（空间坐标x,y + 颜色R,G,B）中沿概率密度梯度方向"
        "不断漂移，收敛到密度极大值点（模态），相同模态的像素归为同一区域。"
        "带宽参数sp（空间半径）和sr（颜色半径）控制分割粒度：sp/sr越小分割越细。"
        "Mean Shift无需预设聚类数，边缘保持好，但计算量较大。"
    ),
    'grabcut': (
        "GrabCut是基于图割（Graph Cut）的交互式分割方法（冈萨雷斯第10章）。"
        "用户仅需用矩形框标出前景大致位置，算法通过高斯混合模型（GMM）建模前景/背景颜色分布，"
        "将分割问题转化为能量函数最小化 E(L)=∑D_p(L_p)+λ∑V_{p,q}(L_p,L_q)，D为数据项，V为平滑项。"
        "通过迭代执行图割和GMM参数更新，逐步精化分割边界。"
        "GrabCut分割精度高、交互简单，适合复杂前景提取，但计算代价较高。"
    ),

    'erosion_dilation': (
        "腐蚀和膨胀是形态学中最基本的两个操作（冈萨雷斯第9章）。腐蚀A⊖B收缩目标区域，"
        "消除小噪点和细连接；膨胀A⊕B扩展目标区域，填充小孔和断裂。"
        "结构元素的形状和大小决定了操作的效果——方形SE适合水平和垂直结构，"
        "圆形SE各向同性。迭代次数等价于反复施加同一操作。"
    ),
    'open_close': (
        "开运算（先腐蚀后膨胀）能平滑物体轮廓、断开狭窄连接、消除细毛刺。"
        "闭运算（先膨胀后腐蚀）能填充小孔、弥合断裂、平滑边界凹陷。"
        "两者都是幂等操作——重复施加不会产生额外变化。"
    ),
    'tophat': (
        "顶帽变换（原图-开运算）提取比结构元素小的亮细节，适合在非均匀背景下检测亮目标。"
        "常用于光照不均情况下的目标提取。"
    ),
    'blackhat': (
        "黑帽变换（闭运算-原图）提取比结构元素小的暗细节，适合在亮背景下检测暗目标。"
        "与顶帽变换互补，两者结合可同时提取亮暗特征。"
    ),
    'skeletonize': (
        "骨架提取（形态学细化）将目标区域收缩为单像素宽的「中轴线」，保留原形状的拓扑结构。"
        "骨架不唯一且对边界噪声敏感，是形状分析和字符识别的常用预处理步骤。"
    ),
    'morph_gradient': (
        "形态学梯度定义为膨胀结果减去腐蚀结果：G=(f⊕b)-(f⊖b)（冈萨雷斯第9章）。"
        "它相当于对图像做一次局部最大值减最小值的运算，能有效提取目标边缘。"
        "结构元素越大，提取的边缘越粗。形态学梯度对灰度变化和边缘方向不敏感，"
        "常用于作为后续分割或特征提取的预处理步骤。"
    ),

    'rgb_split': (
        "RGB通道分离将彩色图像分解为R、G、B三个独立分量。各通道的亮度分布反映了"
        "场景在不同波段的响应特性。通道分离是彩色图像处理的基础操作。"
    ),
    'rgb_to_hsv': (
        "HSV空间将颜色解耦为色调(H)、饱和度(S)和亮度(V)三个独立分量，"
        "比RGB更接近人眼对颜色的感知方式。色调表示颜色类型（0~180），"
        "饱和度表示颜色纯度，亮度表示明暗程度。"
    ),
    'color_hist_eq': (
        "彩色直方图均衡化直接在RGB三通道上分别做均衡化，能增强彩色对比度但可能改变色相。"
        "更优的做法是在HSV空间仅均衡化V通道以保持色调不变。"
    ),
    'hue_adjust': (
        "色调（Hue）表示颜色的种类，在HSV空间中以角度表示（0°~180°在OpenCV中）。"
        "色调调整通过对H分量加减偏移量实现——循环旋转色环。色调调整只改变颜色种类，"
        "不影响亮度（V通道）和饱和度（S通道）。常用于色彩风格变换和艺术效果生成。"
    ),
    'saturation_adjust': (
        "饱和度（Saturation）表示颜色偏离灰度的程度：S=0为灰色，S=255为最纯色。"
        "饱和度调整通过线性缩放 S'=α·S 实现，α>1增强（更鲜艳），α<1减弱（趋向灰度）。"
        "饱和度过高会导致颜色不自然，过低则失去色彩信息。人眼对高饱和度颜色更敏感。"
    ),
    'brightness_adjust': (
        "亮度（Value/Intensity）反映图像的明暗程度。亮度调整可通过V通道加减偏置量实现。"
        "在RGB空间等价于三通道同时加减固定值。调整亮度不改变色相和饱和度，"
        "但过度的亮度偏移会导致高光溢出（clipping）或暗部细节丢失。"
    ),
    'color_balance': (
        "色彩平衡用于校正色偏或调整整体色调倾向（冈萨雷斯第6章）。在RGB空间通过对各通道"
        "独立施加增益系数实现：R'=k_R·R, G'=k_G·G, B'=k_B·B。"
        "k_R>k_G,k_B偏红；k_B偏大偏蓝。色彩平衡的核心应用场景包括白平衡校正、"
        "照片色调调整和彩色复原。"
    ),
    'pseudo_color': (
        "假彩色增强（Pseudo-color）将灰度图像映射为彩色图像，利用人眼可分辨上千种颜色"
        "（远超20~30级灰度）的特性来增强细节感知（冈萨雷斯第6章）。"
        "常见方法包括强度分层（Intensity Slicing）和颜色映射（Colormap）。"
        "广泛应用于医学影像（CT/MRI）、红外图像、遥感和温度分布可视化。"
    ),

    'fourier_descriptor': (
        "傅里叶描述子通过对轮廓的复坐标序列做离散傅里叶变换，将形状信息编码为频域系数。"
        "低频系数描述形状的整体轮廓，高频系数描述细节。通过截断高频系数可实现形状的"
        "多尺度描述和旋转/平移/缩放不变性。"
    ),
    'hu_moments': (
        "Hu矩是一组7个非线性组合的归一化中心矩，具有平移、旋转和缩放不变性。"
        "它们是形状识别的经典特征，通过比较Hu矩向量的距离可以度量形状相似度。"
    ),
    'contour_extract': (
        "轮廓提取是形状分析的基础步骤（冈萨雷斯第11章）。在二值图像中，区域的边界"
        "可通过形态学方法提取：β = R - (R⊖B)，即原区域减去腐蚀后的区域得到边界。"
        "轮廓以点序列（链码/Freeman码）表示，支持4-连通和8-连通两种边界定义。"
        "轮廓提取的质量直接影响后续凸包检测、形状匹配和描述子计算的效果。"
    ),
    'convex_hull': (
        "凸包（Convex Hull）是包含点集的最小凸多边形（冈萨雷斯第11章）。"
        "几何直观——用橡皮筋套住所有轮廓点，橡皮筋围成的形状即为凸包。"
        "凸包与原始轮廓之间的差值称为凸缺陷（Convexity Defects），"
        "可用于手势识别和形状复杂度分析。Sklansky算法和Graham Scan是常用计算凸包的方法。"
    ),
    'min_enclosing': (
        "最小外接矩形（Minimum Enclosing Rectangle）是包围目标区域的最小面积矩形"
        "（冈萨雷斯第11章），分为轴对齐矩形（AABB）和可旋转的最小面积矩形（MAR）。"
        "MAR的一条边必与凸包的某条边重合。最小外接矩形可提取方向（Orientation）、"
        "长宽比和倾斜角度等特征，广泛用于目标定位和方向校正。"
    ),
    'contour_approx': (
        "轮廓近似（多边形逼近）用更少的顶点来表示原始轮廓，保留主要形状特征"
        "（冈萨雷斯第11章）。Douglas-Peucker算法是最经典的轮廓近似方法："
        "连接首尾两点作为基准线，找到所有轮廓点中到基准线距离最大的点，"
        "若距离>ε则保留该点并递归分割，否则舍去中间所有点。"
        "ε越小近似越精确（顶点越多），越大则轮廓越简化。"
    ),
    'shape_match': (
        "形状匹配通过计算形状描述子之间的距离来度量形状相似度（冈萨雷斯第11章）。"
        "常用方法包括Hu矩匹配（I1/I2/I3三种距离度量）和傅里叶描述子匹配。"
        "Hu矩基于7个不变矩的加权距离，matchShapes使用对数变换压缩动态范围。"
        "形状匹配对旋转、缩放和位移具有鲁棒性，但对遮挡和非刚性变形敏感。"
        "形状匹配分数越小表示两轮廓越相似。"
    ),
    # 第1/2章 数字图像基础
    'sampling_demo': (
        "采样是将连续空间坐标离散化的过程（冈萨雷斯第2章）。根据奈奎斯特-香农采样定理，"
        "采样频率必须大于等于信号最高频率的两倍，否则会产生混叠（Aliasing）。"
        "采样率决定了图像的空间分辨率——采样间隔越小，细节保留越多，但数据量随之增大。"
    ),
    'quantization_demo': (
        "量化是将连续灰度值映射为有限离散值的过程。若用b位表示灰度，灰度级数=2^b。"
        "量化级数过少会导致伪轮廓（False Contouring）——人眼对灰度渐变的边缘特别敏感。"
        "8位量化（256级）是数字图像的标准，足以覆盖人眼可分辨的灰度范围。"
    ),
    'resolution_compare': (
        "空间分辨率指图像中可分辨的最小细节，通常用每单位距离的像素数或采样间隔表示。"
        "分辨率降低会导致图像模糊、锯齿效应和细节丢失。图像插值（最近邻/双线性/双三次）"
        "是提高分辨率的常用手段，不同插值方法在速度和质量之间各有取舍。"
    ),
    'pixel_neighbors': (
        "像素邻域关系是数字图像处理的基础概念。4-邻域N4(p)包含上下左右四个直接相邻像素；"
        "8-邻域N8(p)在4-邻域基础上增加四个对角像素；对角邻域ND(p)仅包含四个对角像素。"
        "邻域关系决定了连通性、距离度量和滤波器核的覆盖范围。"
    ),
    'distance_metrics': (
        "图像处理中常用的距离度量有三种：欧几里得距离（直线距离）D_e=[(x1-x2)^2+(y1-y2)^2]^(1/2)；"
        "D4城市街区距离 D4=|x1-x2|+|y1-y2|，等距线为菱形；"
        "D8棋盘距离 D8=max(|x1-x2|,|y1-y2|)，等距线为正方形。距离度量影响形态学操作和区域增长算法。"
    ),
    'interpolation_demo': (
        "图像插值通过已知像素估计未知位置的像素值。最近邻插值取最近像素值，速度快但有锯齿效应；"
        "双线性插值利用周围4个像素做线性加权，质量较好；双三次插值利用16个像素做三次多项式拟合，"
        "质量最优但计算量最大。插值是图像缩放、旋转和几何校正的核心技术。"
    ),
    # 第12章 目标检测与识别
    'template_matching': (
        "模板匹配（冈萨雷斯第12章）通过在图像上滑动模板窗口计算相似度来定位目标。"
        "常用相似度度量包括平方差（SQDIFF）、互相关（CCORR）和相关系数（CCOEFF）。"
        "归一化版本对亮度变化具有鲁棒性。模板匹配对目标的旋转、缩放和变形敏感。"
    ),
    'hough_lines': (
        "霍夫变换（Hough Transform）将图像空间中的直线检测转换为参数空间的峰值检测（冈萨雷斯第12章）。"
        "直线在极坐标下表示为 ρ=xcosθ+ysinθ，每个边缘点在(ρ,θ)参数空间投票，得票最多的参数对应"
        "图像中的直线。霍夫变换对部分遮挡和噪声具有较强鲁棒性。"
    ),
    'hough_circles': (
        "霍夫圆检测将圆的检测转换为三维参数空间(a,b,r)的投票问题，其中(a,b)为圆心坐标，r为半径。"
        "OpenCV使用霍夫梯度法：先用Canny检测边缘，再沿梯度方向投票确定圆心，最后在半径维度投票。"
        "该方法比标准三维霍夫变换效率高得多。"
    ),
    'corner_harris': (
        "Harris角点检测器（冈萨雷斯第12章）通过分析图像梯度协方差矩阵的特征值来判断角点。"
        "角点响应函数 R=det(M)-k·trace²(M)，其中M是2×2的梯度协方差矩阵，k通常取0.04~0.06。"
        "R>0且较大时为角点，R<0时为边缘，|R|较小时为平坦区域。Harris角点具有旋转不变性。"
    ),
    'sift_features': (
        "SIFT（尺度不变特征变换，冈萨雷斯第12章）通过四个核心步骤检测和描述局部特征："
        "①尺度空间极值检测（DoG金字塔）；②关键点精确定位；③方向分配（梯度方向直方图）；"
        "④生成128维特征描述子。SIFT具有尺度、旋转、亮度和视角不变性，是计算机视觉的里程碑算法。"
    ),
    'hog_features': (
        "HOG（方向梯度直方图）通过统计局部区域的梯度方向分布来描述形状特征（冈萨雷斯第12章）。"
        "它将图像划分为cells（如8×8像素），每个cell计算9个方向的梯度直方图，"
        "再以block为单位进行归一化。HOG特征结合SVM分类器是经典的行人检测方案。"
    ),
    'prewitt': (
        "Prewitt算子与Sobel算子结构相似，区别在于Prewitt不使用权值加权（冈萨雷斯第10章）。"
        "Prewitt核为 Gx=[-1,0,1; -1,0,1; -1,0,1]，Gy=[-1,-1,-1; 0,0,0; 1,1,1]。"
        "它计算图像亮度函数的一阶梯度近似，对噪声有一定抑制作用（因3×3邻域平均效应）。"
        "Prewitt比Sobel略快（核元素为整数±1），但对角边缘响应不如Sobel敏感（未加权）。"
    ),
    'roberts': (
        "Roberts算子是最早的边缘检测算子之一，使用2×2对角线差分计算梯度（冈萨雷斯第10章）。"
        "Gx = z9-z5（右下减中心），Gy = z8-z6（左下减右上）。Roberts计算速度极快，"
        "对45°方向的边缘响应较好，但因核尺寸仅2×2且无平滑，对噪声极为敏感。"
    ),
    'region_growing': (
        "区域生长是一种基于相似性准则的图像分割方法（冈萨雷斯第10章）。"
        "从种子点出发，检查邻域像素是否满足相似性条件（如灰度差<阈值），"
        "若满足则将其合并到区域中并继续扩展，直到没有像素可以加入。"
        "相似性阈值是关键参数——过小导致欠生长，过大导致过生长。"
    ),
    # ── 综合工程案例 ──
    'case_01_satellite': (
        "本案例完整演示遥感图像从采样到量化的全流程处理方法。采样过程决定空间分辨率——"
        "降采样损失细节但降低数据量；量化过程决定灰度分辨率——低比特量化产生伪轮廓。"
        "根据奈奎斯特采样定理，采样频率必须至少为信号最高频率的2倍才能无损重建。"
        "对比原始图像、降采样图像与量化退化图像，直观理解采样与量化的权衡。"
    ),
    'case_02_document': (
        "文档几何校正涉及仿射变换（旋转、平移、缩放）和透视变换两大核心几何变换。"
        "插值方法的选择直接影响校正质量：最近邻插值速度最快但产生锯齿，双线性插值折中，"
        "双三次插值（Bicubic）质量最高。本案例对比最近邻与双三次插值的校正效果差异。"
    ),
    'case_03_defect': (
        "零件缺陷检测的核心思路是先去除噪声干扰（中值滤波），再提取边缘特征（Sobel），"
        "最后将检测结果叠加回原图形成热力图。中值滤波对椒盐噪声抑制效果优异，"
        "Sobel算子以3×3核计算梯度——缺陷越明显，检测到的边缘响应越强。"
    ),
    'case_04_ct_denoise': (
        "CT图像去噪采用频域滤波方法。DFT将图像从空间域转换到频率域，噪声主要集中在高频区域。"
        "高斯低通滤波器（GLPF）平滑抑制高频分量同时保留低频部分。与理想低通滤波器相比，"
        "高斯低通不会产生振铃效应——因为它的频率响应是光滑的、没有陡峭截断。"
        "截止频率D0越小，去噪越强但细节损失越大，需在两者之间权衡。"
    ),
    'case_05_photo_restore': (
        "老照片复原流水线依次执行：非局部均值去噪（NLM）→ USM锐化 → CLAHE对比度增强。"
        "NLM利用图像中的重复纹理模式进行去噪，去噪后的图像保留了边缘和细节。"
        "USM通过减去高斯模糊版本来增强细节，CLAHE进一步改善局部对比度，三者协同恢复老照片的清晰度。"
    ),
    'case_06_drone_veg': (
        "航拍植被图像色彩增强采用HSV空间转换策略。HSV将色调（H）、饱和度（S）和亮度（V）分离，"
        "可以独立调整每个分量而不引起色偏。增强饱和度使植被颜色更加鲜艳，随后在LAB空间用CLAHE"
        "均衡亮度通道，在保持色调不变的前提下提升整体对比度。"
    ),
    'case_07_panorama': (
        "多分辨率融合技术广泛应用于图像拼接（Image Stitching）中（冈萨雷斯第7章）。"
        "高斯金字塔提供多尺度平滑表示，拉普拉斯金字塔保留各层的高频残差。通过在不同尺度"
        "级别进行混合，可以平滑过渡拼接边界而不产生明显接缝。本案例演示两幅虚拟图像的拉普拉斯金字塔融合。"
    ),
    'case_08_jpeg_opt': (
        "JPEG压缩优化涉及变换编码和量化两个关键步骤。DCT将8×8图像块转换到频率域，"
        "量化表（Q表）通过舍入高频系数实现压缩。质量参数Q控制量化步长：Q越大压缩率越低质量越好，"
        "Q越小压缩率越高但块效应越明显。PSNR（峰值信噪比）是衡量有损压缩后图像失真度的标准指标。"
    ),
    'case_09_pcb_inspect': (
        "PCB缺陷检测采用形态学图像处理方法（冈萨雷斯第9章）。Otsu自动确定二值化阈值后，"
        "开运算（先腐蚀后膨胀）去除细小噪点，形态学梯度（膨胀-腐蚀）突出缺陷边界。"
        "形态学方法对电路板这种具有规则几何结构的图像特别有效，能准确定位短路、断路等缺陷。"
    ),
    'case_10_water_extract': (
        "遥感水体提取流程综合运用了图像分割与形态学后处理。Otsu自动确定最佳阈值进行二值化，"
        "闭运算（先膨胀后腐蚀）填充水体内部空洞，开运算去除孤立噪点。形态学结构元素的尺寸"
        "5×5是经验参数——过大会破坏水体边界，过小则噪点清除不彻底。"
    ),
    'case_11_part_classify': (
        "零件分类识别基于轮廓分析（冈萨雷斯第11章）。通过Otsu二值化分离前景零件后，"
        "提取每个零件的轮廓并计算Hu不变矩——7个具有平移、旋转、缩放不变性的矩特征。"
        "同时计算面积、周长、圆形度、逼近顶点数等几何特征，综合判断零件类型（圆形件/多边形件/复杂形状件）。"
    ),
    'case_12_traffic_sign': (
        "交通标志检测融合基于边缘和区域两种方法。Canny边缘检测提取所有显著边缘（双阈值50/150），"
        "霍夫圆检测从梯度图中投票检测圆形标志牌——圆形是交通标志中最常见的形状。"
        "Harris角点检测提供辅助定位信息——角点往往对应标志牌的轮廓角点。"
        "三者协同使得检测更加鲁棒，减少漏检和误检。"
    ),
}

# 通用理论后备
FALLBACK_THEORY = (
    "该操作的核心原理可参考冈萨雷斯《数字图像处理》第四版相关章节。"
    "图像处理效果的评价应综合考虑主观视觉质量和客观量化指标，两者不可偏废。"
    "参数的选择往往需要在多种约束之间权衡（如去噪强度与细节保留、增强幅度与噪声放大）。"
)


def _format_change(orig, result):
    """格式化变化量"""
    diff = result - orig
    if abs(orig) < 1e-6:
        return "--"
    pct = diff / abs(orig) * 100
    sign = '+' if diff > 0 else ''
    return f"{sign}{pct:.1f}%"


def _build_basic_metrics_table(orig_gray, res_gray):
    """构建基础指标对比表"""
    m_orig = _image_mean(orig_gray)
    m_res = _image_mean(res_gray)
    s_orig = _image_std(orig_gray)
    s_res = _image_std(res_gray)
    c_orig = _rms_contrast(orig_gray)
    c_res = _rms_contrast(res_gray)
    e_orig = _image_entropy(orig_gray)
    e_res = _image_entropy(res_gray)
    l_orig = _laplacian_variance(orig_gray)
    l_res = _laplacian_variance(res_gray)

    lines = []
    lines.append("┌──────────────────┬────────────┬────────────┬──────────┐")
    lines.append("│      指标         │    原图    │   结果图   │  变化率   │")
    lines.append("├──────────────────┼────────────┼────────────┼──────────┤")
    lines.append(f"│ 平均亮度(Mean)    │ {m_orig:>8.2f}  │ {m_res:>8.2f}  │ {_format_change(m_orig, m_res):>8} │")
    lines.append(f"│ 标准差(Std)       │ {s_orig:>8.2f}  │ {s_res:>8.2f}  │ {_format_change(s_orig, s_res):>8} │")
    lines.append(f"│ RMS对比度          │ {c_orig:>8.2f}  │ {c_res:>8.2f}  │ {_format_change(c_orig, c_res):>8} │")
    lines.append(f"│ 图像熵(bit)        │ {e_orig:>8.4f}  │ {e_res:>8.4f}  │ {_format_change(e_orig, e_res):>8} │")
    lines.append(f"│ 锐度(拉普拉斯方差) │ {l_orig:>8.2f}  │ {l_res:>8.2f}  │ {_format_change(l_orig, l_res):>8} │")
    lines.append("└──────────────────┴────────────┴────────────┴──────────┘")
    return "\n".join(lines), {
        'mean_orig': m_orig, 'mean_res': m_res,
        'entropy_orig': e_orig, 'entropy_res': e_res,
        'lap_var_orig': l_orig, 'lap_var_res': l_res,
    }


def _build_specialized_section(operation, orig_gray, res_gray, op_name, params, metrics):
    """根据操作类型生成专项分析段落，返回 (section_text, denoise_metrics_dict)"""
    section = ""
    denoise = {}

    # ── 去噪恢复类 ──
    if operation in DENOISE_OPS:
        psnr_val = _psnr(orig_gray, res_gray)
        mse_val = _mse(orig_gray, res_gray)
        mae_val = _mae(orig_gray, res_gray)
        edge_before = _edge_density(orig_gray)
        edge_after = _edge_density(res_gray)
        snr = 10 * np.log10(np.var(orig_gray.astype(np.float64)) / (mse_val + 1e-10))

        section += "二、去噪质量专项分析\n"
        section += "────────────────────────────────────────\n"
        denoise['psnr'] = psnr_val
        denoise['mse'] = mse_val
        denoise['edge_ratio'] = edge_after / max(edge_before, 1e-6)
        section += f"  PSNR（峰值信噪比）:   {psnr_val:.2f} dB\n"
        section += f"  MSE（均方误差）:       {mse_val:.2f}\n"
        section += f"  MAE（平均绝对误差）:   {mae_val:.2f}\n"
        section += f"  SNR（信噪比）:         {snr:.2f} dB\n"
        section += f"  边缘保留率:   {edge_before:.4f} → {edge_after:.4f}（{'保留' if edge_after >= edge_before * 0.7 else '损失较多，建议调小平滑参数'}）\n"
        section += "\n"
        # 信噪比评级
        if psnr_val > 40:
            section += "  ▎评级：优秀 —— 去噪后与原始图像极为接近，噪声几乎完全消除。\n"
        elif psnr_val > 30:
            section += "  ▎评级：良好 —— 去噪效果明显，图像质量显著提升。\n"
        elif psnr_val > 25:
            section += "  ▎评级：一般 —— 部分噪声残留或过度平滑导致细节损失。\n"
        else:
            section += "  ▎评级：较差 —— 噪声去除不充分或图像已明显失真。建议减小平滑窗/增加参数强度。\n"
        section += "\n"

    # ── 噪声添加类 ──
    elif operation in NOISE_OPS:
        psnr_val = _psnr(orig_gray, res_gray)
        mse_val = _mse(orig_gray, res_gray)
        edge_before = _edge_density(orig_gray)
        edge_after = _edge_density(res_gray)

        section += "二、噪声影响专项分析\n"
        section += "────────────────────────────────────────\n"
        denoise['psnr'] = psnr_val
        section += f"  PSNR（相对于原图）:   {psnr_val:.2f} dB\n"
        section += f"  MSE（均方误差）:       {mse_val:.2f}\n"
        section += f"  边缘密度变化:   {edge_before:.4f} → {edge_after:.4f}\n"
        section += "\n"
        if psnr_val < 20:
            section += "  ▎噪声强度较高，适合测试去噪算法的鲁棒性。\n"
        else:
            section += "  ▎噪声强度适中，可作为去噪算法的标准测试用例。\n"
        section += "\n"

    # ── 边缘检测/锐化类 ──
    elif operation in EDGE_OPS:
        edge_res = _edge_density(res_gray)
        grad_res = _gradient_magnitude_mean(res_gray)
        lap_var_orig = metrics.get('lap_var_orig', 0)
        lap_var_res = metrics.get('lap_var_res', 0)

        section += "二、边缘检测专项分析\n"
        section += "────────────────────────────────────────\n"
        denoise['edge_ratio'] = edge_res
        section += f"  边缘密度:       {edge_res:.4f}（非零边缘像素占比）\n"
        section += f"  梯度幅值均值:   {grad_res:.2f}\n"
        section += f"  锐度变化:       {lap_var_orig:.2f} → {lap_var_res:.2f}\n"
        section += "\n"
        if edge_res < 0.02:
            section += "  ▎检测到的边缘极少，可能阈值过高或图像本身纹理平滑。建议降低阈值参数。\n"
        elif edge_res > 0.15:
            section += "  ▎边缘密度偏高，可能包含了较多噪声伪边缘。建议适当提高阈值或先做平滑预处理。\n"
        else:
            section += "  ▎边缘密度适中，主要结构边缘得到有效提取。\n"
        section += "\n"

    # ── 频域操作类 ──
    elif operation in FREQ_OPS:
        hf_ratio_orig = _frequency_energy_ratio(orig_gray)
        hf_ratio_res = _frequency_energy_ratio(res_gray)

        section += "二、频域特征专项分析\n"
        section += "────────────────────────────────────────\n"
        section += f"  高频能量占比（原图）:    {hf_ratio_orig:.4f}\n"
        section += f"  高频能量占比（结果图）:  {hf_ratio_res:.4f}\n"

        if hf_ratio_res < hf_ratio_orig * 0.5:
            section += "  ▎高频能量显著下降 → 低通滤波/平滑效果明显，图像细节减少。\n"
        elif hf_ratio_res > hf_ratio_orig * 2:
            section += "  ▎高频能量显著上升 → 高通滤波/锐化效果明显，边缘和细节被增强。\n"
        elif abs(hf_ratio_res - hf_ratio_orig) < 0.01:
            section += "  ▎频域分布基本不变，可能是频谱可视化操作（非滤波）。\n"
        else:
            section += "  ▎频域能量分布有轻微变化。\n"
        section += "\n"

    # ── 形态学类 ──
    elif operation in MORPH_OPS:
        edge_before = _edge_density(orig_gray)
        edge_after = _edge_density(res_gray)
        cc_orig = _count_connected_components(orig_gray)
        cc_res = _count_connected_components(res_gray)

        section += "二、形态学专项分析\n"
        section += "────────────────────────────────────────\n"
        section += f"  边缘密度:       {edge_before:.4f} → {edge_after:.4f}\n"
        section += f"  连通域数量(阈值化后): {cc_orig} → {cc_res}\n"
        section += "\n"
        if cc_res < cc_orig:
            section += "  ▎连通域减少 → 小噪点/细结构被消除（腐蚀/开运算效果）。\n"
        elif cc_res > cc_orig:
            section += "  ▎连通域增加 → 原有分离区域被连接（膨胀/闭运算效果）。\n"
        else:
            section += "  ▎连通结构保持稳定。\n"
        section += "\n"

    # ── 分割类 ──
    elif operation in SEGMENT_OPS:
        cc_res = _count_connected_components(res_gray)
        edge_res = _edge_density(res_gray)
        unique_vals = len(np.unique(res_gray))

        section += "二、分割结果专项分析\n"
        section += "────────────────────────────────────────\n"
        section += f"  连通域数量:     {cc_res}\n"
        section += f"  边缘密度:       {edge_res:.4f}\n"
        section += f"  灰度级数:       {unique_vals}\n"
        section += "\n"
        if cc_res < 3:
            section += "  ▎分割区域过少，可能欠分割（阈值不当或聚类数过少）。\n"
        elif cc_res > 200:
            section += "  ▎分割区域过多（过分割），建议调整参数降低粒度。\n"
        else:
            section += "  ▎分割粒度合理，各区域分离度较好。\n"
        section += "\n"

    # ── 直方图/对比度增强类 ──
    elif operation in HIST_OPS:
        bhatt, kl = _histogram_distance(orig_gray, res_gray)
        ent_orig = metrics.get('entropy_orig', 0)
        ent_res = metrics.get('entropy_res', 0)

        section += "二、直方图变换专项分析\n"
        section += "────────────────────────────────────────\n"
        section += f"  Bhattacharyya距离:    {bhatt:.4f}（0=完全相同，越大差异越大）\n"
        section += f"  KL散度:               {kl:.4f}（0=完全相同）\n"
        section += f"  图像熵变化:           {ent_orig:.4f} → {ent_res:.4f} bit\n"
        section += "\n"
        if ent_res > ent_orig * 1.2:
            section += "  ▎信息熵显著增加，对比度增强有效，图像信息量增大。\n"
        elif ent_res < ent_orig * 0.8:
            section += "  ▎信息熵减少，增强可能过度导致灰度级压缩。\n"
        else:
            section += "  ▎信息熵变化不大，增强效果温和。\n"
        section += "\n"

    # ── 色彩类 ──
    elif operation in COLOR_OPS:
        section += "二、色彩特征专项分析\n"
        section += "────────────────────────────────────────\n"
        section += "  色彩操作主要影响视觉感知，建议结合主观评价。\n"
        section += "  量化指标（亮度/对比度/熵）见上方基础指标对比。\n"
        section += "\n"

    # ── 基础类 (第1/2章) ──
    elif operation in BASICS_OPS:
        section += "二、数字图像基础专项分析\n"
        section += "────────────────────────────────────────\n"
        ent_orig = metrics.get('entropy_orig', 0)
        ent_res = metrics.get('entropy_res', 0)
        section += f"  图像熵变化:       {ent_orig:.4f} → {ent_res:.4f} bit\n"
        section += "\n"
        if operation == 'sampling_demo':
            section += "  ▎采样率越低，空间分辨率越低，图像细节丢失越严重。\n"
        elif operation == 'quantization_demo':
            section += "  ▎量化位深越低，灰度级越少，伪轮廓效应越明显。\n"
        elif operation == 'resolution_compare':
            section += "  ▎低分辨率导致锯齿和模糊；插值方法影响放大质量。\n"
        elif operation == 'pixel_neighbors':
            section += "  ▎邻域关系是空间滤波和形态学操作的基础。\n"
        elif operation == 'distance_metrics':
            section += "  ▎不同距离度量影响形态学操作和图像分割的效果。\n"
        elif operation == 'interpolation_demo':
            section += "  ▎最近邻插值速度快但有锯齿；双三次插值质量最好但计算量大。\n"
        section += "\n"

    # ── 目标检测类 (第12章) ──
    elif operation in DETECT_OPS:
        edge_res = _edge_density(res_gray)
        section += "二、目标检测专项分析\n"
        section += "────────────────────────────────────────\n"
        section += f"  边缘密度:       {edge_res:.4f}\n"
        section += "\n"
        if operation == 'template_matching':
            section += "  ▎模板匹配基于滑动窗口互相关，对旋转和缩放敏感。\n"
        elif operation in ('hough_lines', 'hough_circles'):
            section += "  ▎霍夫变换通过参数空间投票检测几何基元，对部分遮挡鲁棒。\n"
        elif operation == 'corner_harris':
            section += "  ▎Harris角点响应函数 R = det(M) - k·trace²(M)，k 通常取 0.04~0.06。\n"
        elif operation == 'sift_features':
            section += "  ▎SIFT具有尺度、旋转和亮度不变性，是经典局部特征描述子。\n"
        elif operation == 'hog_features':
            section += "  ▎HOG通过梯度方向直方图描述局部形状，广泛用于行人检测。\n"
        section += "\n"

    # ── 其他 ──
    else:
        edge_before = _edge_density(orig_gray)
        edge_after = _edge_density(res_gray)
        section += "二、综合专项分析\n"
        section += "────────────────────────────────────────\n"
        section += f"  边缘密度变化:   {edge_before:.4f} → {edge_after:.4f}\n"
        section += "\n"

    return section, denoise


def _build_theory_section(operation):
    """构建理论解释段落"""
    theory = THEORY_LIBRARY.get(operation, FALLBACK_THEORY)
    lines = []
    lines.append("三、理论依据")
    lines.append("────────────────────────────────────────")
    # 按60字符换行
    for sentence in theory.replace('\n', ' ').split('。'):
        sentence = sentence.strip()
        if not sentence:
            continue
        lines.append(f"  {sentence}。")
    lines.append("")
    return "\n".join(lines)


def _build_suggestion_section(operation, params, metrics=None, denoise_metrics=None):
    """构建基于数值分析的具体优化建议"""
    if metrics is None:
        metrics = {}
    if denoise_metrics is None:
        denoise_metrics = {}

    lines = []
    lines.append("四、参数优化建议")
    lines.append("────────────────────────────────────────")

    lap_var_orig = metrics.get('lap_var_orig', 0)
    lap_var_res = metrics.get('lap_var_res', 0)
    ent_orig = metrics.get('entropy_orig', 0)
    ent_res = metrics.get('entropy_res', 0)

    # ── 去噪恢复类：基于 PSNR 的具体建议 ──
    if operation in DENOISE_OPS:
        psnr = denoise_metrics.get('psnr', 0)
        mse = denoise_metrics.get('mse', 0)
        edge_ratio = denoise_metrics.get('edge_ratio', 1.0)

        lines.append(f"  当前 PSNR = {psnr:.2f} dB，MSE = {mse:.2f}")

        # 根据操作类型和 PSNR 给出不同建议
        if psnr > 40:
            lines.append("  ▸ 去噪效果极佳，图像与原始几乎一致，当前参数配置已是最优。")
        elif psnr > 30:
            if edge_ratio < 0.7:
                lines.append("  ▸ 去噪效果良好但边缘保留不足。建议适当减小核尺寸或降低平滑强度。")
                if 'ksize' in params:
                    current = int(params['ksize'])
                    suggested = max(3, current - 2)
                    lines.append(f"     → 核尺寸建议从 {current}×{current} 调整为 {suggested}×{suggested}")
            else:
                lines.append("  ▸ 去噪效果良好，如需进一步提升可微调参数。")
        elif psnr > 25:
            lines.append("  ▸ 中等去噪效果，噪声部分残留或平滑过度。")
            if 'ksize' in params:
                current = int(params['ksize'])
                if current >= 7:
                    lines.append(f"     → 核尺寸 {current}×{current} 偏大，建议减小到 {current-2}×{current-2} 减少过度平滑")
                else:
                    lines.append(f"     → 尝试将核尺寸从 {current} 增大到 {current+2} 以增强去噪")
        else:
            lines.append("  ▸ PSNR 偏低，去噪效果不理想。")
            if operation == 'mean_filter_restore' and 'ksize' in params:
                current = int(params['ksize'])
                if current <= 5:
                    lines.append(f"     → 均值滤波核 {current}×{current} 太小，尝试增加到 {current+2}×{current+2}")
                else:
                    lines.append("     → 均值滤波可能不适合此噪声类型，建议尝试中值滤波或 NLM 去噪")
            elif operation == 'median_restore' and 'ksize' in params:
                current = int(params['ksize'])
                lines.append(f"     → 中值滤波核 {current}×{current}，尝试增大到 {min(current+2, 9)}×{min(current+2, 9)}")
            elif operation == 'nlm_denoise':
                lines.append("     → 尝试将 h 参数增大 1.5~2 倍以增强去噪强度")
            elif operation == 'bilateral_filter':
                lines.append("     → 尝试增大 sigma_color（值域核强度）以增强去噪效果")

    # ── 噪声添加类 ──
    elif operation in NOISE_OPS:
        psnr = denoise_metrics.get('psnr', 0)
        lines.append(f"  当前 PSNR（相对于原图）= {psnr:.2f} dB")
        if psnr < 15:
            lines.append("  ▸ 噪声强度极高，适合极端场景去噪测试。如需弱化可降低 σ 或比例参数。")
        elif psnr < 25:
            lines.append("  ▸ 噪声强度适中，是常用的去噪算法测试级别。")
        else:
            lines.append("  ▸ 噪声强度较低，适合测试去噪算法在低噪条件下的保边能力。如需更多噪声可增大参数。")

    # ── 边缘检测/锐化类 ──
    elif operation in EDGE_OPS:
        edge_ratio = denoise_metrics.get('edge_ratio', 0.05)
        lines.append(f"  当前边缘密度 = {edge_ratio:.4f}")
        if edge_ratio < 0.02:
            lines.append("  ▸ 边缘密度过低，检测到的边缘太少。")
            if operation == 'canny':
                if 'low_threshold' in params:
                    current_low = int(params['low_threshold'])
                    suggested = max(10, current_low - 30)
                    lines.append(f"     → 将低阈值从 {current_low} 降低到 {suggested}，可捕获更多弱边缘")
            elif operation == 'sobel':
                if 'ksize' in params:
                    lines.append(f"     → 尝试将 ksize 从 {params['ksize']} 增大到 5 以增强检测灵敏度")
        elif edge_ratio > 0.15:
            lines.append("  ▸ 边缘密度偏高，可能包含噪声伪边缘。")
            if operation == 'canny' and 'high_threshold' in params:
                current_high = int(params['high_threshold'])
                suggested = min(255, current_high + 20)
                lines.append(f"     → 将高阈值从 {current_high} 提高到 {suggested}，可过滤更多弱响应")
            elif operation in ('unsharp_mask', 'sobel_sharpen'):
                if 'amount' in params:
                    current = float(params['amount'])
                    suggested = max(0.1, round(current * 0.6, 1))
                    lines.append(f"     → 锐化强度从 {current} 降低到 {suggested}，减少过度增强")
        else:
            lines.append("  ▸ 边缘密度适中，结构边缘提取效果良好。")

    # ── 频域操作类 ──
    elif operation in FREQ_OPS:
        lines.append("  ▸ 观察频谱能量分布变化评估滤波效果：")
        lines.append("     - 低通滤波：高频能量占比应显著下降")
        lines.append("     - 高通滤波：高频能量占比应显著上升")
        lines.append("     - 带通滤波：中间频率段得到保留")
        if 'cutoff' in params:
            current = float(params['cutoff'])
            lines.append(f"     → 当前截止频率 D₀ = {current}，增大通过更多频率成分，减小则过滤更强")

    # ── 形态学类 ──
    elif operation in MORPH_OPS:
        if 'ksize' in params:
            current = int(params['ksize'])
            if operation in ('erosion_dilation',):
                if 'iterations' in params:
                    iters = int(params['iterations'])
                    lines.append(f"  当前结构元素 = {current}×{current}，迭代 = {iters} 次")
                    if iters >= 3:
                        lines.append(f"     → 迭代次数 {iters} 偏多，效果可能过度。建议先减少迭代，再逐步调整结构元素大小。")
                    else:
                        lines.append(f"     → 如需更强效果，可先从增大结构元素（{current}→{current+2}）开始，避免盲目增加迭代次数。")

    # ── 分割类 ──
    elif operation in SEGMENT_OPS:
        if operation == 'kmeans_segment' and 'k' in params:
            current_k = int(params['k'])
            lines.append(f"  当前 K = {current_k}")
            lines.append(f"     → 若分割区域过少（欠分割），增大 K 值（{current_k}→{current_k+1} 或 {current_k+2}）")
            lines.append(f"     → 若分割区域过多（过分割），减小 K 值")
        elif operation == 'watershed' and 'thresh' in params:
            current = int(params['thresh'])
            lines.append(f"  当前前景阈值 = {current}")
            if current < 50:
                lines.append(f"     → 阈值 {current} 偏低，可能过分割。建议增大到 {min(255, current+30)}")
            elif current > 200:
                lines.append(f"     → 阈值 {current} 偏高，可能欠分割。建议减小到 {max(0, current-30)}")

    # ── 直方图/增强类 ──
    elif operation in HIST_OPS:
        if ent_res < ent_orig * 0.8:
            lines.append("  ▸ 信息熵显著下降，增强可能过度压缩了灰度级。")
            if operation == 'gamma_correction' and 'gamma' in params:
                current = float(params['gamma'])
                if current > 2:
                    lines.append(f"     → γ={current} 过强，建议减小到 1.5~2.0 范围")
                elif current < 0.5:
                    lines.append(f"     → γ={current} 过强（亮化过度），建议增大到 0.7~1.0 范围")
        elif ent_res > ent_orig * 1.2:
            lines.append("  ▸ 信息熵显著增加，对比度增强效果明显。适当微调即可。")

    # ── 默认建议 ──
    if len(lines) == 2:  # 只有标题和分隔线，没有实际建议
        current_params = ", ".join(f"{k}={v}" for k, v in params.items()) if params else "默认参数"
        lines.append(f"  当前参数: {current_params}")
        lines.append("  建议微调参数并观察指标变化，在效果强度与细节保留之间寻找平衡点。")

    lines.append("")
    return "\n".join(lines)


# ════════════════════════════════════════════
# /analyze 路由
# ════════════════════════════════════════════

@app.route('/analyze', methods=['POST'])
@login_required
def analyze():
    """量化图像分析——对比原图与处理结果，给出理论分析"""
    try:
        data = request.get_json()
        operation = data.get('operation', '')
        params = data.get('params', {})
        result_b64 = data.get('image_base64', '')
        original_b64 = data.get('original_image_base64', result_b64)

        op_name = OPERATION_NAMES.get(operation, operation)

        # 解码图像
        img_orig = _base64_to_cv2(original_b64)
        img_res = _base64_to_cv2(result_b64)

        # 对齐尺寸
        img_orig, img_res = _align_images(img_orig, img_res)

        # 转灰度
        orig_gray = _ensure_gray(img_orig)
        res_gray = _ensure_gray(img_res)

        # 构建分析报告
        lines = []
        lines.append("═" * 48)
        lines.append(f"  {op_name} —— 量化分析报告")
        lines.append("═" * 48)
        lines.append("")

        # 一、基础指标对比
        lines.append("一、图像质量指标对比")
        lines.append("─" * 48)
        table, metrics = _build_basic_metrics_table(orig_gray, res_gray)
        lines.append(table)
        lines.append("")

        # 二、专项分析
        specialized, denoise_metrics = _build_specialized_section(operation, orig_gray, res_gray, op_name, params, metrics)
        lines.append(specialized)

        # 三、理论依据
        theory = _build_theory_section(operation)
        lines.append(theory)

        # 四、参数优化建议
        suggestion = _build_suggestion_section(operation, params, metrics, denoise_metrics)
        lines.append(suggestion)

        lines.append("═" * 48)
        lines.append("  以上分析基于客观量化指标，仅供参考。")
        lines.append("  实际图像处理效果应结合主观视觉评价。")
        lines.append("═" * 48)

        analysis = "\n".join(lines)

        return jsonify({'status': 'success', 'analysis': analysis})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ────────────── 主动AI分析（处理成功后） ──────────────

def _generate_proactive_analysis(original_b64, result_b64, operation, params, op_name):
    """处理成功后主动生成个性化分析，带缓存"""
    try:
        cache_key = hashlib.md5(
            (result_b64[:2000] + '|' + operation + '|' + json.dumps(params, sort_keys=True)).encode('utf-8')
        ).hexdigest()
        if cache_key in _ai_analysis_cache:
            return _ai_analysis_cache[cache_key]

        # 量化指标
        orig_cv = _base64_to_cv2(original_b64)
        res_cv = _base64_to_cv2(result_b64)
        orig_gray = _ensure_gray(orig_cv)
        res_gray = _ensure_gray(res_cv)
        orig_gray, res_gray = _align_images(orig_gray, res_gray)

        metrics = {
            'orig_mean': _image_mean(orig_gray),
            'res_mean': _image_mean(res_gray),
            'orig_std': _image_std(orig_gray),
            'res_std': _image_std(res_gray),
        }
        if len(orig_cv.shape) == 3 and len(res_cv.shape) == 3:
            metrics['is_color'] = True
        else:
            metrics['is_color'] = False

        # 构造提示词
        prompt = f"""你是数字图像处理课程的智能助教。学生刚完成了一次图像处理实操，请基于客观量化指标生成一段个性化分析。

【操作】{op_name}（{operation}）
【参数】{json.dumps(params, ensure_ascii=False)}
【量化指标】
- 原图平均亮度：{metrics['orig_mean']:.1f}，处理后：{metrics['res_mean']:.1f}
- 原图对比度(标准差)：{metrics['orig_std']:.1f}，处理后：{metrics['res_std']:.1f}
- 是否为彩色图：{'是' if metrics['is_color'] else '否'}

请按以下四部分输出（每部分用【】标注，语言简洁、面向本科生）：
【处理效果评价】一句话说明本次处理是否达到预期视觉效果
【参数选择分析】结合参数与指标，说明当前参数是否合理、有何影响
【改进建议】给出1-2条可操作的改进方向
【关联知识点推荐】推荐1个与本操作最相关的后续知识点（注明章节方向）

总字数控制在200字以内。"""

        analysis = _call_deepseek(prompt, max_tokens=600)
        _ai_analysis_cache[cache_key] = analysis
        return analysis
    except Exception:
        return None


def _generate_error_guidance(operation, params, error_msg):
    """错误操作时主动生成引导提示"""
    try:
        prompt = f"""你是数字图像处理课程的智能助教。学生在实操中遇到了错误，请主动给出引导。

【操作】{operation}
【参数】{json.dumps(params, ensure_ascii=False)}
【系统报错】{error_msg}

请按以下三部分输出（每部分用【】标注，语气友好、面向本科生）：
【问题诊断】用通俗语言说明为什么这个操作不适合当前图片/参数
【正确操作建议】给出具体、可操作的下一步建议（如换什么图、调什么参数）
【关联知识点】一句话点出背后的原理

总字数控制在150字以内。"""

        return _call_deepseek(prompt, max_tokens=400)
    except Exception:
        return None


def _call_deepseek(prompt, max_tokens=600):
    """调用DeepSeek API（带超时与降级）"""
    try:
        headers = {
            'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
            'Content-Type': 'application/json'
        }
        payload = {
            'model': 'deepseek-chat',
            'messages': [
                {'role': 'system', 'content': '你是数字图像处理课程的智能助教，回答简洁专业。'},
                {'role': 'user', 'content': prompt}
            ],
            'max_tokens': max_tokens,
            'temperature': 0.7,
            'stream': False
        }
        resp = http_requests.post(
            f'{DEEPSEEK_API_BASE}/chat/completions',
            headers=headers, json=payload, timeout=15
        )
        if resp.status_code == 200:
            return resp.json()['choices'][0]['message']['content'].strip()
        return None
    except Exception:
        return None

# ════════════════════════════════════════════
# 理论路由（导入外部模块）
# ════════════════════════════════════════════
from theory_route import init_theory_routes
init_theory_routes(app, OPERATION_NAMES, THEORY_LIBRARY)


# ════════════════════════════════════════════
# AI 助手路由（DeepSeek Chat API）
# ════════════════════════════════════════════
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')
DEEPSEEK_API_BASE = os.environ.get('DEEPSEEK_API_BASE', 'https://api.deepseek.com/v1')


@app.route('/api/chat', methods=['POST'])
@login_required
def ai_chat():
    """AI 助手对话接口 — 流式响应"""
    if not DEEPSEEK_API_KEY:
        return jsonify({
            'status': 'error',
            'message': 'AI 助手暂未配置。请在启动前设置环境变量 DEEPSEEK_API_KEY。'
        }), 503

    data = request.get_json() or {}
    user_message = data.get('message', '').strip()
    history = data.get('history', [])
    context = data.get('context', {})

    if not user_message:
        return jsonify({'status': 'error', 'message': '请输入问题'}), 400

    # 构建系统提示词
    system_prompt = _build_system_prompt(context)

    # 构建消息列表
    messages = [{'role': 'system', 'content': system_prompt}]
    # 只保留最近 10 轮对话以控制 token
    for h in history[-20:]:
        messages.append({'role': h.get('role', 'user'), 'content': h.get('content', '')})
    messages.append({'role': 'user', 'content': user_message})

    def generate():
        full_text = ''
        try:
            resp = http_requests.post(
                f'{DEEPSEEK_API_BASE}/chat/completions',
                headers={
                    'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
                    'Content-Type': 'application/json',
                },
                json={
                    'model': 'deepseek-chat',
                    'messages': messages,
                    'stream': True,
                    'temperature': 0.7,
                    'max_tokens': 2048,
                },
                timeout=60,
                stream=True,
            )
            if resp.status_code != 200:
                error_msg = resp.text[:200]
                yield f'data: {json.dumps({"error": error_msg})}\n\n'
                yield 'data: [DONE]\n\n'
                return

            for line in resp.iter_lines():
                if not line:
                    continue
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data_str = line[6:]
                    if data_str.strip() == '[DONE]':
                        yield 'data: [DONE]\n\n'
                        break
                    try:
                        chunk = json.loads(data_str)
                        delta = chunk.get('choices', [{}])[0].get('delta', {})
                        content = delta.get('content', '')
                        if content:
                            full_text += content
                            yield f'data: {json.dumps({"choices":[{"delta":{"content":content}}]})}\n\n'
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            yield f'data: {json.dumps({"error": str(e)})}\n\n'
            yield 'data: [DONE]\n\n'

    return Response(generate(), mimetype='text/event-stream',
                    headers={
                        'Cache-Control': 'no-cache',
                        'X-Accel-Buffering': 'no',
                    })


def _build_system_prompt(context):
    """构建 AI 助手系统提示词"""
    chapter_title = context.get('chapterTitle', '')
    chapter_id = context.get('chapterId', '')
    section_title = context.get('sectionTitle', '')
    operation_name = context.get('operationName', '')
    operation_id = context.get('operationId', '')
    result_summary = context.get('resultSummary', '')

    prompt = f"""你是「数字图像处理教学平台」的 AI 学习助手，由西南交通大学希望学院人工智能学院李康乐开发。
你的职责是帮助学生理解数字图像处理的概念、算法和工程应用。

参考教材：冈萨雷斯《数字图像处理》第四版。

当前学生所在上下文：
"""
    if chapter_title:
        prompt += f"- 正在学习「{chapter_title}」\n"
    if section_title:
        prompt += f"- 当前小节：「{section_title}」\n"
    if operation_name:
        prompt += f"- 正在进行实操：「{operation_name}」\n"
    if result_summary:
        prompt += f"- 处理结果概要：{result_summary}\n"

    prompt += """
请遵循以下原则回答问题：
1. 结合学生当前所在章节/操作上下文，给出有针对性的解释
2. 对概念性问题，先给出简洁定义，再展开详细说明，必要时使用数学公式
3. 对实操相关问题，解释算法原理、参数含义和影响、结果解读和优化建议
4. 使用中文回答，专业术语保留英文对照
5. 回答清晰有条理，适当使用 Markdown 格式组织"""
    return prompt


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=9527)
