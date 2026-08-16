/**
 * 数字图像处理教学平台 —— 对比分析模式 v2
 * 作者：李康乐
 * 优化：参数在结果下方 + 代码Tab切换 + 中文错误提示
 */

// ========== 对比分组定义 ==========
const COMPARE_GROUPS = {
    'compare_3_spatial': {
        title: '空间滤波对比',
        desc: '均值滤波 vs 中值滤波 vs 高斯滤波 — 同时对比三种平滑滤波器的去噪效果与边缘保留能力',
        chapter: 3,
        channels: [
            { id: 'mean_filter_restore', name: '均值滤波去噪', params: [
                { key: 'ksize', label: '核大小', type: 'range', min: 3, max: 15, step: 2, default: 5 }
            ]},
            { id: 'median_restore', name: '中值滤波去噪', params: [
                { key: 'ksize', label: '核大小', type: 'range', min: 3, max: 15, step: 2, default: 5 }
            ]},
            { id: 'gaussian_blur', name: '高斯滤波', params: [
                { key: 'ksize', label: '核大小', type: 'range', min: 3, max: 15, step: 2, default: 5 },
                { key: 'sigma', label: 'σ', type: 'range', min: 0.1, max: 5, step: 0.1, default: 1.0 }
            ]},
        ]
    },
    'compare_4_lowpass': {
        title: '低通滤波器对比',
        desc: '理想低通 vs 巴特沃斯低通 vs 高斯低通',
        chapter: 4,
        channels: [
            { id: 'ideal_lowpass', name: '理想低通', params: [
                { key: 'cutoff', label: '截止频率 D₀', type: 'range', min: 5, max: 200, step: 5, default: 50 }
            ]},
            { id: 'butterworth_lowpass', name: '巴特沃斯低通', params: [
                { key: 'cutoff', label: '截止频率 D₀', type: 'range', min: 5, max: 200, step: 5, default: 50 }
            ]},
            { id: 'gaussian_lowpass', name: '高斯低通', params: [
                { key: 'cutoff', label: '截止频率 D₀', type: 'range', min: 5, max: 200, step: 5, default: 50 }
            ]},
        ]
    },
    'compare_4_highpass': {
        title: '高通滤波器对比',
        desc: '理想高通 vs 巴特沃斯高通 vs 高斯高通',
        chapter: 4,
        channels: [
            { id: 'ideal_highpass', name: '理想高通', params: [
                { key: 'cutoff', label: '截止频率 D₀', type: 'range', min: 5, max: 150, step: 5, default: 30 }
            ]},
            { id: 'butterworth_highpass', name: '巴特沃斯高通', params: [
                { key: 'cutoff', label: '截止频率 D₀', type: 'range', min: 5, max: 150, step: 5, default: 30 }
            ]},
            { id: 'gaussian_highpass', name: '高斯高通', params: [
                { key: 'cutoff', label: '截止频率 D₀', type: 'range', min: 5, max: 150, step: 5, default: 30 }
            ]},
        ]
    },
    'compare_5_noise': {
        title: '噪声模型与复原对比',
        desc: '不同噪声添加 + 不同复原方法的效果对比',
        chapter: 5,
        channels: [
            { id: 'gaussian_noise', name: '高斯噪声', params: [
                { key: 'sigma', label: 'σ（标准差）', type: 'range', min: 5, max: 100, step: 5, default: 25 }
            ]},
            { id: 'sp_noise', name: '椒盐噪声', params: [
                { key: 'amount', label: '噪声比例', type: 'range', min: 0.01, max: 0.3, step: 0.01, default: 0.05 }
            ]},
            { id: 'mean_filter_restore', name: '均值滤波复原', params: [
                { key: 'ksize', label: '核大小', type: 'range', min: 3, max: 15, step: 2, default: 5 }
            ]},
            { id: 'median_restore', name: '中值滤波复原', params: [
                { key: 'ksize', label: '核大小', type: 'range', min: 3, max: 15, step: 2, default: 5 }
            ]},
        ]
    },
    'compare_6_color': {
        title: '色彩空间转换对比',
        desc: 'RGB通道分离 vs HSV转换 vs 色调调整 vs 饱和度调整',
        chapter: 6,
        channels: [
            { id: 'rgb_split', name: 'RGB通道分离', params: [] },
            { id: 'rgb_to_hsv', name: 'RGB→HSV转换', params: [] },
            { id: 'hue_adjust', name: '色调调整', params: [
                { key: 'shift', label: '色相偏移', type: 'range', min: -180, max: 180, step: 5, default: 30 }
            ]},
            { id: 'saturation_adjust', name: '饱和度调整', params: [
                { key: 'factor', label: '饱和度因子', type: 'range', min: 0, max: 3, step: 0.1, default: 1.5 }
            ]},
        ]
    },
    'compare_7_wavelet': {
        title: '小波变换对比',
        desc: '高斯金字塔 vs 拉普拉斯金字塔 vs 多分辨率融合 vs DWT降噪',
        chapter: 7,
        channels: [
            { id: 'gaussian_pyramid', name: '高斯金字塔', params: [
                { key: 'levels', label: '层数', type: 'range', min: 1, max: 6, step: 1, default: 3 }
            ]},
            { id: 'laplacian_pyramid', name: '拉普拉斯金字塔', params: [
                { key: 'levels', label: '层数', type: 'range', min: 1, max: 6, step: 1, default: 3 }
            ]},
            { id: 'dwt_denoise', name: 'DWT降噪', params: [
                { key: 'threshold', label: '阈值系数', type: 'range', min: 5, max: 100, step: 5, default: 30 }
            ]},
        ]
    },
    'compare_8_compress': {
        title: '压缩方法对比',
        desc: 'JPEG不同质量压缩对比',
        chapter: 8,
        channels: [
            { id: 'jpeg_compare', name: 'JPEG质量=90', params: [
                { key: 'quality', label: '质量', type: 'range', min: 5, max: 100, step: 5, default: 90 }
            ]},
            { id: 'jpeg_compare', name: 'JPEG质量=50', params: [
                { key: 'quality', label: '质量', type: 'range', min: 5, max: 100, step: 5, default: 50 }
            ]},
            { id: 'jpeg_compare', name: 'JPEG质量=10', params: [
                { key: 'quality', label: '质量', type: 'range', min: 5, max: 100, step: 5, default: 10 }
            ]},
        ]
    },
    'compare_9_morph': {
        title: '形态学操作对比',
        desc: '腐蚀 vs 膨胀 vs 开运算 vs 闭运算 vs 形态学梯度',
        chapter: 9,
        channels: [
            { id: 'erosion_dilation', name: '腐蚀', params: [
                { key: 'ksize', label: '结构元大小', type: 'range', min: 3, max: 15, step: 2, default: 5 },
                { key: 'mode', label: '', type: 'hidden', default: '腐蚀' }
            ]},
            { id: 'erosion_dilation', name: '膨胀', params: [
                { key: 'ksize', label: '结构元大小', type: 'range', min: 3, max: 15, step: 2, default: 5 },
                { key: 'mode', label: '', type: 'hidden', default: '膨胀' }
            ]},
            { id: 'open_close', name: '开运算', params: [
                { key: 'ksize', label: '结构元大小', type: 'range', min: 3, max: 15, step: 2, default: 5 },
                { key: 'mode', label: '', type: 'hidden', default: '开运算' }
            ]},
            { id: 'open_close', name: '闭运算', params: [
                { key: 'ksize', label: '结构元大小', type: 'range', min: 3, max: 15, step: 2, default: 5 },
                { key: 'mode', label: '', type: 'hidden', default: '闭运算' }
            ]},
            { id: 'morph_gradient', name: '形态学梯度', params: [
                { key: 'ksize', label: '结构元大小', type: 'range', min: 3, max: 15, step: 2, default: 5 }
            ]},
        ]
    },
    'compare_10_seg': {
        title: '分割方法对比',
        desc: 'Otsu vs 自适应阈值 vs K-means vs 区域生长 vs 分水岭 vs GrabCut',
        chapter: 10,
        channels: [
            { id: 'otsu_threshold', name: 'Otsu阈值', params: [] },
            { id: 'adaptive_threshold', name: '自适应阈值', params: [
                { key: 'block_size', label: '块大小', type: 'range', min: 3, max: 51, step: 2, default: 11 },
                { key: 'c', label: '常数C', type: 'range', min: -10, max: 20, step: 1, default: 2 }
            ]},
            { id: 'kmeans_segment', name: 'K-means', params: [
                { key: 'k', label: '聚类数K', type: 'range', min: 2, max: 10, step: 1, default: 3 }
            ]},
            { id: 'region_growing', name: '区域生长', params: [
                { key: 'threshold', label: '灰度阈值', type: 'range', min: 5, max: 100, step: 5, default: 20 }
            ]},
            { id: 'watershed', name: '分水岭', params: [] },
            { id: 'grabcut', name: 'GrabCut', params: [] },
        ]
    },
    'compare_11_contour': {
        title: '轮廓与描述对比',
        desc: '轮廓提取 vs 凸包 vs 最小外接矩形 vs Hu矩',
        chapter: 11,
        channels: [
            { id: 'contour_extract', name: '轮廓提取', params: [] },
            { id: 'convex_hull', name: '凸包检测', params: [] },
            { id: 'min_enclosing', name: '最小外接矩形', params: [] },
            { id: 'hu_moments', name: 'Hu矩特征', params: [] },
        ]
    },
    'compare_12_edge': {
        title: '边缘检测对比',
        desc: 'Sobel vs Prewitt vs Roberts vs Canny vs Laplacian',
        chapter: 12,
        channels: [
            { id: 'sobel', name: 'Sobel', params: [
                { key: 'ksize', label: '核大小', type: 'range', min: 3, max: 7, step: 2, default: 3 }
            ]},
            { id: 'prewitt', name: 'Prewitt', params: [] },
            { id: 'roberts', name: 'Roberts', params: [] },
            { id: 'canny', name: 'Canny', params: [
                { key: 'low_threshold', label: '低阈值', type: 'range', min: 10, max: 200, step: 5, default: 50 },
                { key: 'high_threshold', label: '高阈值', type: 'range', min: 50, max: 300, step: 5, default: 150 }
            ]},
            { id: 'laplacian', name: 'Laplacian', params: [] },
        ]
    },
    'compare_12_detect': {
        title: '特征检测对比',
        desc: '模板匹配 vs Harris角点 vs SIFT vs HOG vs 霍夫线检测',
        chapter: 12,
        channels: [
            { id: 'template_matching', name: '模板匹配', params: [] },
            { id: 'corner_harris', name: 'Harris角点', params: [
                { key: 'block_size', label: '邻域大小', type: 'range', min: 2, max: 10, step: 1, default: 2 },
                { key: 'ksize', label: 'Sobel核', type: 'range', min: 3, max: 7, step: 2, default: 3 },
                { key: 'k', label: 'k系数', type: 'range', min: 0.01, max: 0.1, step: 0.01, default: 0.04 }
            ]},
            { id: 'sift_features', name: 'SIFT', params: [] },
            { id: 'hough_lines', name: '霍夫线检测', params: [
                { key: 'threshold', label: '投票阈值', type: 'range', min: 50, max: 300, step: 10, default: 150 }
            ]},
        ]
    },
};

// ========== Python代码库（对比模式用） ==========
const OP_CODE_COMPARE = {
    'mean_filter_restore': `import cv2\n\nimg = cv2.imread('input.jpg')\nksize = 5  # 核大小\nresult = cv2.blur(img, (ksize, ksize))\ncv2.imwrite('output.jpg', result)`,
    'median_restore': `import cv2\n\nimg = cv2.imread('input.jpg')\nksize = 5\nresult = cv2.medianBlur(img, ksize)\ncv2.imwrite('output.jpg', result)`,
    'gaussian_blur': `import cv2\n\nimg = cv2.imread('input.jpg')\nresult = cv2.GaussianBlur(img, (5, 5), 1.0)\ncv2.imwrite('output.jpg', result)`,
    'ideal_lowpass': `import cv2, numpy as np\n\nimg = cv2.imread('input.jpg')\ngray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)\nh,w=gray.shape;h-=h%2;w-=w%2;gray=gray[:h,:w]\ndft=cv2.dft(np.float32(gray),flags=cv2.DFT_COMPLEX_OUTPUT)\ndft_shift=np.fft.fftshift(dft)\ny,x=np.ogrid[:h,:w];D0=50\nmask=(np.sqrt((y-h//2)**2+(x-w//2)**2)<=D0).astype(np.float32)\ndft_shift*=mask[:,:,np.newaxis]\nback=cv2.idft(np.fft.ifftshift(dft_shift))\nresult=cv2.normalize(cv2.magnitude(back[:,:,0],back[:,:,1]),None,0,255,cv2.NORM_MINMAX).astype(np.uint8)\ncv2.imwrite('output.jpg', result)`,
    'butterworth_lowpass': `import cv2, numpy as np\n\nimg = cv2.imread('input.jpg')\ngray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)\nh,w=gray.shape;h-=h%2;w-=w%2;gray=gray[:h,:w]\ndft=cv2.dft(np.float32(gray),flags=cv2.DFT_COMPLEX_OUTPUT)\ndft_shift=np.fft.fftshift(dft)\ny,x=np.ogrid[:h,:w];D0=50;n=4\nd=np.sqrt((y-h//2)**2+(x-w//2)**2)\nmask=(1.0/(1.0+(d/(D0+1e-6))**4)).astype(np.float32)\ndft_shift*=mask[:,:,np.newaxis]\nback=cv2.idft(np.fft.ifftshift(dft_shift))\nresult=cv2.normalize(cv2.magnitude(back[:,:,0],back[:,:,1]),None,0,255,cv2.NORM_MINMAX).astype(np.uint8)\ncv2.imwrite('output.jpg', result)`,
    'gaussian_lowpass': `import cv2, numpy as np\n\nimg = cv2.imread('input.jpg')\ngray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)\nh,w=gray.shape;h-=h%2;w-=w%2;gray=gray[:h,:w]\ndft=cv2.dft(np.float32(gray),flags=cv2.DFT_COMPLEX_OUTPUT)\ndft_shift=np.fft.fftshift(dft)\ny,x=np.ogrid[:h,:w];D0=50\nd=np.sqrt((y-h//2)**2+(x-w//2)**2)\nmask=np.exp(-d**2/(2*D0**2)).astype(np.float32)\ndft_shift*=mask[:,:,np.newaxis]\nback=cv2.idft(np.fft.ifftshift(dft_shift))\nresult=cv2.normalize(cv2.magnitude(back[:,:,0],back[:,:,1]),None,0,255,cv2.NORM_MINMAX).astype(np.uint8)\ncv2.imwrite('output.jpg', result)`,
    'sobel': `import cv2, numpy as np\n\nimg = cv2.imread('input.jpg')\ngray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)\ngx=cv2.Sobel(gray,cv2.CV_64F,1,0,ksize=3)\ngy=cv2.Sobel(gray,cv2.CV_64F,0,1,ksize=3)\nresult=np.uint8(np.sqrt(gx**2+gy**2))\ncv2.imwrite('output.jpg', result)`,
    'canny': `import cv2\n\nimg = cv2.imread('input.jpg')\ngray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)\nresult = cv2.Canny(gray, 50, 150)\ncv2.imwrite('output.jpg', result)`,
    'rgb_split': `import cv2\nimport numpy as np\n\nimg = cv2.imread('input.jpg')\n# RGB通道分离\nb, g, r = cv2.split(img)\n# 合并显示：R=红色通道, G=绿色通道, B=蓝色通道\nzeros = np.zeros_like(b)\n# 显示蓝色通道\nresult = cv2.merge([b, zeros, zeros])\ncv2.imwrite('output.jpg', result)`,
    'rgb_to_hsv': `import cv2\n\nimg = cv2.imread('input.jpg')\n# RGB → HSV 色彩空间转换\nhsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)\n# 转回BGR以正常显示\nresult = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)\ncv2.imwrite('output.jpg', result)`,
    'hue_adjust': `import cv2\nimport numpy as np\n\nimg = cv2.imread('input.jpg')\nshift = 30  # 色相偏移量 [-180, 180]\nhsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)\n# 色调调整：H通道加上偏移量\nhsv[:, :, 0] = np.mod(hsv[:, :, 0] + shift, 180)\nhsv = hsv.astype(np.uint8)\nresult = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)\ncv2.imwrite('output.jpg', result)`,
    'saturation_adjust': `import cv2\nimport numpy as np\n\nimg = cv2.imread('input.jpg')\nfactor = 1.5  # 饱和度因子 [0, 3]\nhsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)\n# 饱和度调整：S通道乘以因子\nhsv[:, :, 1] = np.clip(hsv[:, :, 1] * factor, 0, 255)\nhsv = hsv.astype(np.uint8)\nresult = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)\ncv2.imwrite('output.jpg', result)`,
    'gaussian_pyramid': `import cv2\nimport numpy as np\n\nimg = cv2.imread('input.jpg')\nlevels = 3  # 金字塔层数\n# 高斯金字塔：逐层降采样（先高斯模糊再缩小一半）\npyramid = [img]\nfor i in range(levels):\n    img = cv2.pyrDown(img)\n    pyramid.append(img)\n# 显示最顶层（分辨率最低的图像）\nresult = pyramid[-1]\n# 放大回原始尺寸以便对比\nfor _ in range(levels):\n    result = cv2.pyrUp(result)\nresult = cv2.resize(result, (pyramid[0].shape[1], pyramid[0].shape[0]))\ncv2.imwrite('output.jpg', result)`,
    'laplacian_pyramid': `import cv2\nimport numpy as np\n\nimg = cv2.imread('input.jpg')\nlevels = 3  # 金字塔层数\n# 拉普拉斯金字塔：L_i = G_i - pyrUp(pyrDown(G_i))\ngaussian = [img.astype(np.float32)]\nfor i in range(levels):\n    gaussian.append(cv2.pyrDown(gaussian[-1]).astype(np.float32))\nlaplacian = []\nfor i in range(levels):\n    expanded = cv2.pyrUp(gaussian[i + 1])\n    if expanded.shape != gaussian[i].shape:\n        expanded = cv2.resize(expanded, (gaussian[i].shape[1], gaussian[i].shape[0]))\n    lap = gaussian[i] - expanded\n    lap_norm = cv2.normalize(lap, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)\n    laplacian.append(lap_norm)\n# 显示第一层拉普拉斯（包含高频细节）\nresult = laplacian[0]\ncv2.imwrite('output.jpg', result)`,
    'dwt_denoise': `import cv2\nimport numpy as np\nimport pywt\n\nimg = cv2.imread('input.jpg')\ngray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)\nthreshold = 30  # 小波阈值系数\n# DWT降噪：对图像做2级小波分解，对高频系数做软阈值处理\ncoeffs = pywt.wavedec2(gray, 'db4', level=2)\n# 保留近似系数不变，对细节系数做阈值处理\ncoeffs_thresh = [coeffs[0]]\nfor detail in coeffs[1:]:\n    cH, cV, cD = detail\n    cH = pywt.threshold(cH, threshold, mode='soft')\n    cV = pywt.threshold(cV, threshold, mode='soft')\n    cD = pywt.threshold(cD, threshold, mode='soft')\n    coeffs_thresh.append((cH, cV, cD))\n# 小波重构\nresult = pywt.waverec2(coeffs_thresh, 'db4')\nresult = np.clip(result, 0, 255).astype(np.uint8)\ncv2.imwrite('output.jpg', result)`,
    'jpeg_compare': `import cv2\nimport numpy as np\n\nimg = cv2.imread('input.jpg')\nquality = 50  # JPEG质量 [5, 100]\n# JPEG压缩质量对比：不同质量参数下的编解码\nencode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]\n_, encoded = cv2.imencode('.jpg', img, encode_param)\nresult = cv2.imdecode(encoded, cv2.IMREAD_COLOR)\ncv2.imwrite('output.jpg', result)`,
    'erosion_dilation': `import cv2\nimport numpy as np\n\nimg = cv2.imread('input.jpg')\ngray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)\n_, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)\nksize = 5  # 结构元大小\nkernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (ksize, ksize))\n# 腐蚀：消除边界像素，收缩前景区域\neroded = cv2.erode(binary, kernel, iterations=1)\n# 膨胀：扩展边界像素，扩大前景区域\ndilated = cv2.dilate(binary, kernel, iterations=1)\n# 并排显示腐蚀(左)和膨胀(右)\nresult = np.hstack([eroded, dilated])\ncv2.imwrite('output.jpg', result)`,
    'open_close': `import cv2\nimport numpy as np\n\nimg = cv2.imread('input.jpg')\ngray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)\n_, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)\nksize = 5  # 结构元大小\nkernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (ksize, ksize))\n# 开运算 = 先腐蚀后膨胀：消除小噪点，平滑轮廓\nopened = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)\n# 闭运算 = 先膨胀后腐蚀：填充小孔洞，连接断裂区域\nclosed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)\nresult = np.hstack([opened, closed])\ncv2.imwrite('output.jpg', result)`,
    'morph_gradient': `import cv2\nimport numpy as np\n\nimg = cv2.imread('input.jpg')\ngray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)\n_, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)\nksize = 5  # 结构元大小\nkernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (ksize, ksize))\n# 形态学梯度 = 膨胀 - 腐蚀：提取物体边界\nresult = cv2.morphologyEx(binary, cv2.MORPH_GRADIENT, kernel)\ncv2.imwrite('output.jpg', result)`,
    'adaptive_threshold': `import cv2\n\nimg = cv2.imread('input.jpg')\ngray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)\nblock_size = 11  # 邻域块大小（奇数）\nc = 2            # 常数偏移\n# 自适应阈值：根据局部邻域统计信息为每个像素计算独立阈值\nresult = cv2.adaptiveThreshold(gray, 255,\n    cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_size, c)\ncv2.imwrite('output.jpg', result)`,
    'kmeans_segment': `import cv2\nimport numpy as np\n\nimg = cv2.imread('input.jpg')\nk = 3  # 聚类数\n# K-means聚类分割\npixels = img.reshape((-1, 3)).astype(np.float32)\ncriteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)\n_, labels, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)\ncenters = centers.astype(np.uint8)\nresult = centers[labels.flatten()].reshape(img.shape)\ncv2.imwrite('output.jpg', result)`,
    'watershed': `import cv2\nimport numpy as np\n\nimg = cv2.imread('input.jpg')\ngray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)\n# 分水岭算法\n_, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)\n# 去噪\nkernel = np.ones((3, 3), np.uint8)\nopening = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=2)\n# 确定背景区域\nsure_bg = cv2.dilate(opening, kernel, iterations=3)\n# 距离变换确定前景\ndist = cv2.distanceTransform(opening, cv2.DIST_L2, 5)\n_, sure_fg = cv2.threshold(dist, 0.3 * dist.max(), 255, 0)\nsure_fg = sure_fg.astype(np.uint8)\n# 未知区域\nunknown = cv2.subtract(sure_bg, sure_fg)\n# 标记\n_, markers = cv2.connectedComponents(sure_fg)\nmarkers = markers + 1\nmarkers[unknown == 255] = 0\n# 应用分水岭\nmarkers = cv2.watershed(img, markers)\n# 在原始图像上绘制边界\nresult = img.copy()\nresult[markers == -1] = [0, 0, 255]\ncv2.imwrite('output.jpg', result)`,
    'grabcut': `import cv2\nimport numpy as np\n\nimg = cv2.imread('input.jpg')\n# GrabCut分割\nmask = np.zeros(img.shape[:2], np.uint8)\nbgd_model = np.zeros((1, 65), np.float64)\nfgd_model = np.zeros((1, 65), np.float64)\n# 初始矩形（图像中央80%区域作为前景猜测）\nh, w = img.shape[:2]\nrect = (w//10, h//10, w*8//10, h*8//10)\ncv2.grabCut(img, mask, rect, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_RECT)\n# 提取前景\nmask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype(np.uint8)\nresult = img * mask2[:, :, np.newaxis]\ncv2.imwrite('output.jpg', result)`,
    'contour_extract': `import cv2\n\nimg = cv2.imread('input.jpg')\ngray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)\n_, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)\n# 轮廓提取：在原始图像上绘制所有轮廓\ncontours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)\nresult = img.copy()\ncv2.drawContours(result, contours, -1, (0, 255, 0), 2)\ncv2.imwrite('output.jpg', result)`,
    'convex_hull': `import cv2\nimport numpy as np\n\nimg = cv2.imread('input.jpg')\ngray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)\n_, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)\ncontours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)\nresult = img.copy()\nfor cnt in contours:\n    # 凸包检测：计算包围轮廓的最小凸多边形\n    hull = cv2.convexHull(cnt)\n    cv2.drawContours(result, [hull], -1, (0, 0, 255), 2)\n    cv2.drawContours(result, [cnt], -1, (0, 255, 0), 1)\ncv2.imwrite('output.jpg', result)`,
    'min_enclosing': `import cv2\nimport numpy as np\n\nimg = cv2.imread('input.jpg')\ngray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)\n_, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)\ncontours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)\nresult = img.copy()\nfor cnt in contours:\n    if len(cnt) < 5: continue\n    # 最小外接矩形\n    rect = cv2.minAreaRect(cnt)\n    box = cv2.boxPoints(rect).astype(np.int32)\n    cv2.drawContours(result, [box], -1, (255, 0, 0), 2)\ncv2.imwrite('output.jpg', result)`,
    'hu_moments': `import cv2\nimport numpy as np\n\nimg = cv2.imread('input.jpg')\ngray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)\n_, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)\ncontours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)\nresult = img.copy()\nfor i, cnt in enumerate(contours):\n    # Hu矩：7个旋转、缩放、平移不变矩\n    moments = cv2.moments(cnt)\n    hu = cv2.HuMoments(moments)\n    # 对数归一化\n    hu_log = -np.sign(hu) * np.log10(np.abs(hu) + 1e-10)\n    x, y, w, h_rect = cv2.boundingRect(cnt)\n    cv2.rectangle(result, (x, y), (x+w, y+h_rect), (0, 255, 0), 2)\n    cv2.putText(result, f'Hu[{i}]: {hu_log[0,0]:.2f}', (x, y-5),\n        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)\ncv2.imwrite('output.jpg', result)`,
    'template_matching': `import cv2\nimport numpy as np\n\nimg = cv2.imread('input.jpg')\ngray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)\n# 模板匹配：使用图像中央区域作为模板\nh, w = gray.shape\nth, tw = h // 4, w // 4\ntemplate = gray[h//2-th//2:h//2+th//2, w//2-tw//2:w//2+tw//2]\n# 归一化相关系数匹配\nresult_match = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)\n_, max_val, _, max_loc = cv2.minMaxLoc(result_match)\n# 绘制匹配框\nresult = img.copy()\ncv2.rectangle(result, max_loc, (max_loc[0]+tw, max_loc[1]+th), (0, 255, 0), 2)\ncv2.imwrite('output.jpg', result)`,
    'hough_lines': `import cv2\nimport numpy as np\n\nimg = cv2.imread('input.jpg')\ngray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)\nedges = cv2.Canny(gray, 50, 150)\n# 霍夫线检测\nlines = cv2.HoughLines(edges, 1, np.pi/180, threshold=150)\nresult = img.copy()\nif lines is not None:\n    for line in lines[:20]:  # 最多显示20条线\n        rho, theta = line[0]\n        a, b = np.cos(theta), np.sin(theta)\n        x0, y0 = a * rho, b * rho\n        pt1 = (int(x0 + 1000*(-b)), int(y0 + 1000*(a)))\n        pt2 = (int(x0 - 1000*(-b)), int(y0 - 1000*(a)))\n        cv2.line(result, pt1, pt2, (0, 255, 0), 2)\ncv2.imwrite('output.jpg', result)`,
    'ideal_highpass': `import cv2\nimport numpy as np\n\nimg = cv2.imread('input.jpg')\ngray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)\n# 缩放到偶数尺寸\nh, w = gray.shape\nif h % 2: h -= 1\nif w % 2: w -= 1\ngray = gray[:h, :w]\ncutoff = 30  # 截止频率\n# DFT\ndft = cv2.dft(np.float32(gray), flags=cv2.DFT_COMPLEX_OUTPUT)\ndft_shift = np.fft.fftshift(dft)\n# 理想高通掩码\ny, x = np.ogrid[:h, :w]\ncy, cx = h // 2, w // 2\nmask = (np.sqrt((y - cy)**2 + (x - cx)**2) > cutoff).astype(np.float32)\ndft_shift *= mask[:, :, np.newaxis]\n# 逆DFT\nf_ishift = np.fft.ifftshift(dft_shift)\nimg_back = cv2.idft(f_ishift)\nresult = cv2.normalize(cv2.magnitude(img_back[:,:,0], img_back[:,:,1]), None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)\ncv2.imwrite('output.jpg', result)`,
    'butterworth_highpass': `import cv2\nimport numpy as np\n\nimg = cv2.imread('input.jpg')\ngray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)\nh, w = gray.shape\nif h % 2: h -= 1\nif w % 2: w -= 1\ngray = gray[:h, :w]\ncutoff = 30  # 截止频率 D0\norder = 4    # 巴特沃斯阶数\n# DFT\ndft = cv2.dft(np.float32(gray), flags=cv2.DFT_COMPLEX_OUTPUT)\ndft_shift = np.fft.fftshift(dft)\ny, x = np.ogrid[:h, :w]\nd = np.sqrt((y - h//2)**2 + (x - w//2)**2)\n# 巴特沃斯高通: H = 1 / (1 + (D0/D)^(2n))\nmask = (1.0 / (1.0 + (cutoff / (d + 1e-6))**(2 * order))).astype(np.float32)\ndft_shift *= mask[:, :, np.newaxis]\nf_ishift = np.fft.ifftshift(dft_shift)\nimg_back = cv2.idft(f_ishift)\nresult = cv2.normalize(cv2.magnitude(img_back[:,:,0], img_back[:,:,1]), None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)\ncv2.imwrite('output.jpg', result)`,
    'gaussian_highpass': `import cv2\nimport numpy as np\n\nimg = cv2.imread('input.jpg')\ngray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)\nh, w = gray.shape\nif h % 2: h -= 1\nif w % 2: w -= 1\ngray = gray[:h, :w]\ncutoff = 30  # 截止频率 D0\n# DFT\ndft = cv2.dft(np.float32(gray), flags=cv2.DFT_COMPLEX_OUTPUT)\ndft_shift = np.fft.fftshift(dft)\ny, x = np.ogrid[:h, :w]\nd = np.sqrt((y - h//2)**2 + (x - w//2)**2)\n# 高斯高通: H = 1 - exp(-D^2 / (2*D0^2))\nmask = (1.0 - np.exp(-d**2 / (2 * cutoff**2))).astype(np.float32)\ndft_shift *= mask[:, :, np.newaxis]\nf_ishift = np.fft.ifftshift(dft_shift)\nimg_back = cv2.idft(f_ishift)\nresult = cv2.normalize(cv2.magnitude(img_back[:,:,0], img_back[:,:,1]), None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)\ncv2.imwrite('output.jpg', result)`,
    'gaussian_noise': `import cv2\nimport numpy as np\n\nimg = cv2.imread('input.jpg')\nsigma = 25  # 噪声标准差\nnoise = np.random.normal(0, sigma, img.shape).astype(np.int16)\nresult = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)\ncv2.imwrite('output.jpg', result)`,
    'sp_noise': `import cv2\nimport numpy as np\n\nimg = cv2.imread('input.jpg')\namount = 0.05  # 噪声比例\nresult = img.copy()\nh, w = result.shape[:2]\nfor c in range(3):\n    n_salt = int(w * h * amount / 2)\n    xs = np.random.randint(0, w, n_salt)\n    ys = np.random.randint(0, h, n_salt)\n    result[ys, xs, c] = 255\n    n_pepper = int(w * h * amount / 2)\n    xp = np.random.randint(0, w, n_pepper)\n    yp = np.random.randint(0, h, n_pepper)\n    result[yp, xp, c] = 0\ncv2.imwrite('output.jpg', result)`,
    'otsu_threshold': `import cv2\n\nimg = cv2.imread('input.jpg')\ngray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)\n# Otsu自动阈值\n_, result = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)\ncv2.imwrite('output.jpg', result)`,
    'laplacian': `import cv2\nimport numpy as np\n\nimg = cv2.imread('input.jpg')\ngray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)\n# 拉普拉斯锐化\nlap = cv2.Laplacian(gray, cv2.CV_64F)\nresult = np.uint8(np.absolute(lap))\ncv2.imwrite('output.jpg', result)`,
    'corner_harris': `import cv2\nimport numpy as np\n\nimg = cv2.imread('input.jpg')\ngray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)\ngray_f = np.float32(gray)\n# Harris角点检测\ndst = cv2.cornerHarris(gray_f, blockSize=2, ksize=3, k=0.04)\ndst = cv2.dilate(dst, None)\nresult = img.copy()\nresult[dst > 0.01 * dst.max()] = [0, 0, 255]\ncv2.imwrite('output.jpg', result)`,
    'sift_features': `import cv2\n\nimg = cv2.imread('input.jpg')\ngray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)\nsift = cv2.SIFT_create()\nkeypoints, descriptors = sift.detectAndCompute(gray, None)\n# 绘制关键点\nresult = cv2.drawKeypoints(img, keypoints, None,\n    flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)\ncv2.imwrite('output.jpg', result)`,
};

function getDefaultCompareCode(opId) {
    return `import cv2\nimport numpy as np\n\nimg = cv2.imread('input.jpg')\n\n# 「${opId}」算法实现\n\ncv2.imwrite('output.jpg', result)`;
}

// ========== 全局状态 ==========
let uploadedFile = null;
let uploadedImageData = null;
let currentCodeOpId = null;

// ========== 初始化 ==========
function init() {
    const group = COMPARE_GROUPS[GROUP_ID];
    if (!group) {
        document.getElementById('compareChannels').innerHTML = '<p class="error-msg">未找到对比分组: ' + GROUP_ID + '</p>';
        return;
    }

    document.getElementById('compareTitle').textContent = group.title;
    document.getElementById('compareDesc').textContent = group.desc;
    document.getElementById('chapterBadge').textContent = '第' + group.chapter + '章';

    buildChannels(group);
    buildCodeTabs(group);
    bindUpload();
}

function buildChannels(group) {
    const container = document.getElementById('compareChannels');
    let html = '';
    group.channels.forEach((ch, i) => {
        html += `<div class="compare-channel-v2" data-op-id="${ch.id}" data-channel-idx="${i}">`;
        // 结果在上
        html += `<div class="channel-header">
            <span class="channel-index">${i + 1}</span>
            <h4>${ch.name}</h4>
        </div>`;
        html += `<div class="channel-result" id="result-${i}">
            <div class="result-placeholder-small">处理后显示</div>
        </div>`;
        // 参数在下
        if (ch.params.length > 0) {
            html += '<div class="channel-params">';
            ch.params.forEach(p => {
                if (p.type === 'hidden') {
                    html += `<input type="hidden" class="param-input" data-key="${p.key}" value="${p.default}">`;
                } else if (p.type === 'range') {
                    html += `<div class="param-row">
                        <label>${p.label}</label>
                        <div class="param-range-group">
                            <input type="range" class="param-range" data-key="${p.key}"
                                min="${p.min}" max="${p.max}" step="${p.step}" value="${p.default}"
                                oninput="this.nextElementSibling.value=this.value">
                            <output>${p.default}</output>
                        </div>
                    </div>`;
                }
            });
            html += '</div>';
        }
        html += '</div>';
    });
    container.innerHTML = html;

    document.getElementById('compareActions').style.display = 'flex';
    document.getElementById('compareLayout').style.display = 'flex';
    document.getElementById('processAllBtn').addEventListener('click', processAll);
}

function buildCodeTabs(group) {
    const tabsEl = document.getElementById('codeTabs');
    let html = '';
    group.channels.forEach((ch, i) => {
        html += `<button class="code-tab" data-op-id="${ch.id}" data-idx="${i}" onclick="switchCodeTab('${ch.id}', ${i}, '${ch.name.replace(/'/g, "\\'")}')">${ch.name}</button>`;
    });
    tabsEl.innerHTML = html;
    // 默认选中第一个
    if (group.channels.length > 0) {
        switchCodeTab(group.channels[0].id, 0, group.channels[0].name);
    }
}

function switchCodeTab(opId, idx, name) {
    currentCodeOpId = opId;
    // 更新tab样式
    document.querySelectorAll('.code-tab').forEach(t => t.classList.remove('active'));
    document.querySelector(`.code-tab[data-idx="${idx}"]`).classList.add('active');
    // 更新代码内容
    document.getElementById('currentCodeLabel').textContent = name;
    const code = OP_CODE_COMPARE[opId] || getDefaultCompareCode(opId);
    document.getElementById('compareCodeContent').textContent = code;
}

function copyCompareCode() {
    const code = document.getElementById('compareCodeContent').textContent;
    const btn = document.getElementById('copyCompareCodeBtn');
    navigator.clipboard.writeText(code).then(() => {
        btn.textContent = '已复制!';
        btn.classList.add('copied');
        setTimeout(() => { btn.textContent = '复制代码'; btn.classList.remove('copied'); }, 2000);
    }).catch(() => {
        const ta = document.createElement('textarea');
        ta.value = code;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        btn.textContent = '已复制!';
        btn.classList.add('copied');
        setTimeout(() => { btn.textContent = '复制代码'; btn.classList.remove('copied'); }, 2000);
    });
}

function bindUpload() {
    const zone = document.getElementById('uploadZone');
    const input = document.getElementById('imageInput');
    const placeholder = document.getElementById('uploadPlaceholder');
    const preview = document.getElementById('uploadPreview');

    zone.addEventListener('click', () => input.click());
    zone.addEventListener('dragover', (e) => { e.preventDefault(); zone.classList.add('dragover'); });
    zone.addEventListener('dragleave', () => zone.classList.remove('dragover'));
    zone.addEventListener('drop', (e) => {
        e.preventDefault();
        zone.classList.remove('dragover');
        const file = e.dataTransfer.files[0];
        if (file) handleFile(file);
    });
    input.addEventListener('change', () => {
        if (input.files[0]) handleFile(input.files[0]);
    });

    function handleFile(file) {
        if (!file.type.match(/image\/(jpeg|png|bmp|tiff)/)) {
            alert('请上传 JPG / PNG / BMP / TIFF 格式图片');
            return;
        }
        uploadedFile = file;
        const reader = new FileReader();
        reader.onload = (e) => {
            uploadedImageData = e.target.result;
            preview.src = uploadedImageData;
            preview.style.display = 'block';
            placeholder.style.display = 'none';
        };
        reader.readAsDataURL(file);
    }
}

async function processAll() {
    if (!uploadedImageData) {
        alert('请先上传图片');
        return;
    }

    const group = COMPARE_GROUPS[GROUP_ID];
    const btn = document.getElementById('processAllBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> 处理中…';

    const channels = document.querySelectorAll('.compare-channel-v2');
    const promises = [];

    channels.forEach((chEl, idx) => {
        const opId = chEl.dataset.opId;
        const paramInputs = chEl.querySelectorAll('.param-input, .param-range');
        const params = {};
        paramInputs.forEach(inp => {
            params[inp.dataset.key] = parseFloat(inp.value) || inp.value;
        });

        const formData = new FormData();
        const base64Data = uploadedImageData.split(',')[1];
        const byteChars = atob(base64Data);
        const byteNums = new Array(byteChars.length);
        for (let i = 0; i < byteChars.length; i++) {
            byteNums[i] = byteChars.charCodeAt(i);
        }
        const byteArr = new Uint8Array(byteNums);
        const blob = new Blob([byteArr], { type: 'image/png' });
        formData.append('image', blob, 'upload.png');
        formData.append('operation', opId);
        formData.append('params', JSON.stringify(params));

        promises.push(
            fetch('/process', { method: 'POST', body: formData })
                .then(r => r.json())
                .then(data => ({ idx, opId, data }))
                .catch(err => ({ idx, opId, error: err.message }))
        );
    });

    try {
        const results = await Promise.all(promises);
        displayResults(results);
    } catch (e) {
        console.error('处理失败:', e);
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<svg width="16" height="16" viewBox="0 0 16 16" fill="none" style="vertical-align:middle;margin-right:6px;"><polygon points="2,1 14,8 2,15" fill="currentColor"/></svg>全部处理并对比';
    }
}

function displayResults(results) {
    const group = COMPARE_GROUPS[GROUP_ID];
    results.forEach(r => {
        const resultDiv = document.getElementById('result-' + r.idx);
        if (!resultDiv) return;

        const ch = group.channels[r.idx];
        if (r.error) {
            resultDiv.innerHTML = `<div class="result-error">处理失败：${translateError(r.error)}</div>`;
        } else if (r.data && r.data.status === 'success') {
            let opLabel = ch.name;
            if (r.data.params_summary) {
                opLabel += ' (' + r.data.params_summary + ')';
            }
            resultDiv.innerHTML = `
                <img src="${r.data.result_image}" alt="${opLabel}" class="result-img">
                <div class="result-label">${opLabel}</div>
            `;
        } else {
            resultDiv.innerHTML = `<div class="result-error">处理失败：${translateError(r.data?.message || '未知错误')}</div>`;
        }
    });
}

// ===== 中文错误翻译 =====
function translateError(msg) {
    if (!msg) return '未知错误';
    if (msg.indexOf('grayscale') > -1 || msg.indexOf('gray') > -1 || msg.indexOf('单通道') > -1)
        return '该图像为灰度图，请上传彩色图像';
    if (msg.indexOf('size') > -1 || msg.indexOf('small') > -1 || msg.indexOf('尺寸') > -1)
        return '图像尺寸过小，无法进行该操作';
    if (msg.indexOf('empty') > -1)
        return '未收到图像数据，请重新上传';
    if (msg.indexOf('不支持') > -1)
        return msg;
    if (msg.length > 100)
        return '处理失败，请检查输入参数后重试';
    return msg;
}

document.addEventListener('DOMContentLoaded', init);
