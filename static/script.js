/**
 * 西南交通大学希望学院 · 基础部 · 数字图像处理教学平台
 * 设计：李康乐    技术支持：李康乐
 * 前端交互逻辑 —— v3.0 全12章完整版 实时拖动调参
 */

document.addEventListener('DOMContentLoaded', function () {
    if (!document.getElementById('operationSelect')) return;
    initOperationPage();
});

/* ================================================================
   章节 → 操作映射（第3-11章，每章至少5个操作）
   ================================================================ */
var CHAPTER_OPS = {
    1: [
        { id: 'sampling_demo',            name: '采样过程演示' },
        { id: 'quantization_demo',        name: '量化过程演示' },
        { id: 'resolution_compare',       name: '空间分辨率对比' },
        { id: 'pixel_neighbors',          name: '像素邻域可视化' },
        { id: 'distance_metrics',         name: '距离度量演示' },
        { id: 'interpolation_demo',       name: '图像插值对比' },
        { id: 'case_01_satellite',        name: '综合工程案例：遥感图像采样分析' }
    ],
    2: [
        { id: 'sampling_demo',            name: '采样过程演示' },
        { id: 'quantization_demo',        name: '量化过程演示' },
        { id: 'resolution_compare',       name: '空间分辨率对比' },
        { id: 'pixel_neighbors',          name: '像素邻域可视化' },
        { id: 'distance_metrics',         name: '距离度量演示' },
        { id: 'interpolation_demo',       name: '图像插值对比' },
        { id: 'case_02_document',         name: '综合工程案例：文档几何校正' }
    ],
    3: [
        { id: 'image_inversion',        name: '图像反转' },
        { id: 'log_transform',          name: '对数变换' },
        { id: 'contrast_stretch',       name: '对比度拉伸' },
        { id: 'histogram_equalization', name: '直方图均衡化' },
        { id: 'clahe',                  name: '自适应直方图均衡(CLAHE)' },
        { id: 'gamma_correction',       name: '伽马校正' },
        { id: 'median_blur',            name: '中值滤波' },
        { id: 'gaussian_blur',          name: '高斯滤波' },
        { id: 'bilateral_filter',       name: '双边滤波' },
        { id: 'laplacian',              name: '拉普拉斯锐化' },
        { id: 'unsharp_mask',           name: 'USM锐化' },
        { id: 'sobel_sharpen',          name: 'Sobel锐化' },
        { id: 'case_03_defect',           name: '综合工程案例：零件缺陷检测' }
    ],
    4: [
        { id: 'ideal_lowpass',          name: '理想低通滤波' },
        { id: 'ideal_highpass',         name: '理想高通滤波' },
        { id: 'butterworth_lowpass',    name: '巴特沃斯低通滤波' },
        { id: 'butterworth_highpass',   name: '巴特沃斯高通滤波' },
        { id: 'gaussian_lowpass',       name: '高斯低通滤波' },
        { id: 'gaussian_highpass',      name: '高斯高通滤波' },
        { id: 'bandpass_filter',        name: '带通滤波' },
        { id: 'case_04_ct_denoise',     name: '综合工程案例：CT图像去噪' }
    ],
    5: [
        { id: 'gaussian_noise',         name: '添加高斯噪声' },
        { id: 'sp_noise',               name: '添加椒盐噪声' },
        { id: 'mean_filter_restore',    name: '均值滤波去噪' },
        { id: 'median_restore',         name: '中值滤波去噪' },
        { id: 'nlm_denoise',            name: '非局部均值去噪(NLM)' },
        { id: 'wiener_filter',          name: '维纳滤波复原' },
        { id: 'sobel',                  name: 'Sobel边缘检测' },
        { id: 'canny',                  name: 'Canny边缘检测' },
        { id: 'case_05_photo_restore',  name: '综合工程案例：老照片复原' }
    ],
    6: [
        { id: 'rgb_split',              name: 'RGB通道分离' },
        { id: 'rgb_to_hsv',             name: 'RGB→HSV转换' },
        { id: 'hue_adjust',             name: '色调调整' },
        { id: 'saturation_adjust',      name: '饱和度调整' },
        { id: 'brightness_adjust',      name: '亮度调整' },
        { id: 'color_balance',          name: '色彩平衡调整' },
        { id: 'pseudo_color',           name: '假彩色增强' },
        { id: 'color_hist_eq',          name: '彩色直方图均衡化' },
        { id: 'case_06_drone_veg',      name: '综合工程案例：航拍植被增强' }
    ],
    7: [
        { id: 'gaussian_pyramid',       name: '高斯金字塔' },
        { id: 'laplacian_pyramid',      name: '拉普拉斯金字塔' },
        { id: 'pyramid_blend',          name: '多分辨率融合' },
        { id: 'dwt_denoise',            name: '离散小波降噪' },
        { id: 'dwt_edge_enhance',       name: '小波边缘增强' },
        { id: 'case_07_panorama',       name: '综合工程案例：多分辨率融合' }
    ],
    8: [
        { id: 'dct_visualize',          name: 'DCT变换可视化' },
        { id: 'jpeg_simulate',          name: 'JPEG压缩模拟' },
        { id: 'jpeg_compare',           name: '压缩质量对比' },
        { id: 'binary_rle',             name: '二值化与游程编码' },
        { id: 'binary_huffman',         name: '哈夫曼编码模拟' },
        { id: 'case_08_jpeg_opt',       name: '综合工程案例：JPEG压缩优化' }
    ],
    9: [
        { id: 'erosion_dilation',       name: '腐蚀与膨胀' },
        { id: 'open_close',             name: '开运算与闭运算' },
        { id: 'morph_gradient',         name: '形态学梯度' },
        { id: 'tophat',                 name: '顶帽变换' },
        { id: 'blackhat',               name: '黑帽变换' },
        { id: 'skeletonize',            name: '骨架提取' },
        { id: 'case_09_pcb_inspect',    name: '综合工程案例：PCB缺陷检测' }
    ],
    10: [
        { id: 'otsu_threshold',         name: 'Otsu阈值分割' },
        { id: 'adaptive_threshold',     name: '自适应阈值分割' },
        { id: 'kmeans_segment',         name: 'K-means聚类分割' },
        { id: 'mean_shift_segment',     name: 'Mean Shift分割' },
        { id: 'watershed',              name: '分水岭算法' },
        { id: 'grabcut',                name: 'GrabCut分割' },
        { id: 'case_10_water_extract',  name: '综合工程案例：遥感水体提取' }
    ],
    11: [
        { id: 'contour_extract',        name: '轮廓提取' },
        { id: 'convex_hull',            name: '凸包检测' },
        { id: 'min_enclosing',          name: '最小外接矩形' },
        { id: 'contour_approx',         name: '轮廓近似' },
        { id: 'hu_moments',             name: 'Hu矩特征' },
        { id: 'shape_match',            name: '形状匹配' },
        { id: 'fourier_descriptor',     name: '傅里叶描述子' },
        { id: 'case_11_part_classify',  name: '综合工程案例：零件分类识别' }
    ],
    12: [
        { id: 'template_matching',      name: '模板匹配' },
        { id: 'hough_lines',            name: '霍夫线检测' },
        { id: 'hough_circles',          name: '霍夫圆检测' },
        { id: 'corner_harris',          name: 'Harris角点检测' },
        { id: 'sift_features',          name: 'SIFT特征检测' },
        { id: 'hog_features',           name: 'HOG特征提取' },
        { id: 'case_12_traffic_sign',   name: '综合工程案例：交通标志检测' }
    ]
};

/* ================================================================
   参数定义
   ================================================================ */
var OP_PARAMS = {
    // 第三章
    'image_inversion': [],
    'log_transform': [
        { key: 'c', label: '缩放系数 c', type: 'range', min: 1, max: 100, step: 1, default: 20 }
    ],
    'contrast_stretch': [
        { key: 'low_percent', label: '低百分比', type: 'range', min: 0, max: 50, step: 1, default: 2 },
        { key: 'high_percent', label: '高百分比', type: 'range', min: 50, max: 100, step: 1, default: 98 }
    ],
    'histogram_equalization': [],
    'clahe': [
        { key: 'clip_limit', label: '对比度限制', type: 'range', min: 0.5, max: 10, step: 0.5, default: 2.0 },
        { key: 'tile_size', label: '网格大小', type: 'select', options: [4, 8, 16, 32], default: 8 }
    ],
    'gamma_correction': [
        { key: 'gamma', label: 'γ 值', type: 'range', min: 0.1, max: 3.0, step: 0.05, default: 1.0 }
    ],
    'median_blur': [
        { key: 'ksize', label: '核大小', type: 'select', options: [3, 5, 7, 9, 11, 13, 15], default: 5 }
    ],
    'gaussian_blur': [
        { key: 'ksize', label: '核大小', type: 'select', options: [3, 5, 7, 9, 11, 13, 15], default: 5 },
        { key: 'sigma', label: 'σ 值', type: 'range', min: 0.1, max: 5.0, step: 0.1, default: 1.0 }
    ],
    'bilateral_filter': [
        { key: 'd', label: '邻域直径', type: 'range', min: 3, max: 25, step: 2, default: 9 },
        { key: 'sigma_color', label: '颜色σ', type: 'range', min: 5, max: 150, step: 1, default: 75 },
        { key: 'sigma_space', label: '空间σ', type: 'range', min: 5, max: 150, step: 1, default: 75 }
    ],
    'laplacian': [],
    'unsharp_mask': [
        { key: 'amount', label: '锐化强度', type: 'range', min: 0.1, max: 5.0, step: 0.1, default: 1.5 },
        { key: 'radius', label: '模糊半径', type: 'range', min: 1, max: 10, step: 1, default: 3 }
    ],
    'sobel_sharpen': [
        { key: 'ksize', label: '核大小', type: 'select', options: [1, 3, 5, 7], default: 3 }
    ],

    // 第四章
    'ideal_lowpass': [
        { key: 'cutoff', label: '截止频率', type: 'range', min: 5, max: 200, step: 1, default: 50 }
    ],
    'ideal_highpass': [
        { key: 'cutoff', label: '截止频率', type: 'range', min: 5, max: 200, step: 1, default: 30 }
    ],
    'butterworth_lowpass': [
        { key: 'cutoff', label: '截止频率', type: 'range', min: 10, max: 200, step: 1, default: 50 }
    ],
    'butterworth_highpass': [
        { key: 'cutoff', label: '截止频率', type: 'range', min: 10, max: 200, step: 1, default: 30 }
    ],
    'gaussian_lowpass': [
        { key: 'cutoff', label: '截止频率', type: 'range', min: 10, max: 200, step: 1, default: 50 }
    ],
    'gaussian_highpass': [
        { key: 'cutoff', label: '截止频率', type: 'range', min: 10, max: 200, step: 1, default: 30 }
    ],
    'bandpass_filter': [
        { key: 'low_cutoff', label: '低频截止', type: 'range', min: 5, max: 100, step: 1, default: 20 },
        { key: 'high_cutoff', label: '高频截止', type: 'range', min: 30, max: 200, step: 1, default: 80 }
    ],

    // 第五章
    'gaussian_noise': [
        { key: 'sigma', label: '噪声强度 σ', type: 'range', min: 5, max: 100, step: 1, default: 25 }
    ],
    'sp_noise': [
        { key: 'amount', label: '噪声密度', type: 'range', min: 0.01, max: 0.5, step: 0.01, default: 0.05 }
    ],
    'mean_filter_restore': [
        { key: 'ksize', label: '核大小', type: 'select', options: [3, 5, 7, 9, 11], default: 5 }
    ],
    'median_restore': [
        { key: 'ksize', label: '核大小', type: 'select', options: [3, 5, 7, 9, 11], default: 5 }
    ],
    'nlm_denoise': [
        { key: 'h', label: '滤波强度 h', type: 'range', min: 3, max: 50, step: 1, default: 10 }
    ],
    'wiener_filter': [
        { key: 'ksize', label: '核大小', type: 'select', options: [3, 5, 7, 9], default: 5 }
    ],
    'sobel': [
        { key: 'ksize', label: '核大小', type: 'select', options: [1, 3, 5, 7], default: 3 }
    ],
    'canny': [
        { key: 'low_threshold', label: '低阈值', type: 'range', min: 0, max: 255, step: 1, default: 50 },
        { key: 'high_threshold', label: '高阈值', type: 'range', min: 0, max: 255, step: 1, default: 150 }
    ],

    // 第六章
    'rgb_split': [
        { key: 'channel', label: '显示通道', type: 'select', options: ['R', 'G', 'B', '合并显示'], default: '合并显示' }
    ],
    'rgb_to_hsv': [
        { key: 'channel', label: '显示通道', type: 'select', options: ['H', 'S', 'V', '合并显示'], default: '合并显示' }
    ],
    'hue_adjust': [
        { key: 'shift', label: '色调偏移', type: 'range', min: -180, max: 180, step: 1, default: 0 }
    ],
    'saturation_adjust': [
        { key: 'factor', label: '饱和度因子', type: 'range', min: 0, max: 3.0, step: 0.05, default: 1.0 }
    ],
    'brightness_adjust': [
        { key: 'beta', label: '亮度增量', type: 'range', min: -100, max: 100, step: 1, default: 0 }
    ],
    'color_balance': [
        { key: 'r_gain', label: '红色增益', type: 'range', min: 0.5, max: 2.0, step: 0.05, default: 1.0 },
        { key: 'g_gain', label: '绿色增益', type: 'range', min: 0.5, max: 2.0, step: 0.05, default: 1.0 },
        { key: 'b_gain', label: '蓝色增益', type: 'range', min: 0.5, max: 2.0, step: 0.05, default: 1.0 }
    ],
    'pseudo_color': [
        { key: 'colormap', label: '伪彩色映射', type: 'select', options: ['jet', 'hot', 'cool', 'bone', 'rainbow', 'turbo', 'ocean', 'pink'], default: 'jet' }
    ],
    'color_hist_eq': [],

    // 第七章
    'gaussian_pyramid': [
        { key: 'levels', label: '金字塔层数', type: 'range', min: 1, max: 5, step: 1, default: 3 }
    ],
    'laplacian_pyramid': [
        { key: 'levels', label: '金字塔层数', type: 'range', min: 1, max: 5, step: 1, default: 3 }
    ],
    'pyramid_blend': [
        { key: 'levels', label: '融合层数', type: 'range', min: 1, max: 5, step: 1, default: 3 }
    ],
    'dwt_denoise': [
        { key: 'threshold', label: '降噪阈值', type: 'range', min: 5, max: 100, step: 1, default: 30 }
    ],
    'dwt_edge_enhance': [
        { key: 'gain', label: '边缘增益', type: 'range', min: 0.5, max: 5.0, step: 0.1, default: 2.0 }
    ],

    // 第八章
    'dct_visualize': [],
    'jpeg_simulate': [
        { key: 'quality', label: '压缩质量', type: 'range', min: 5, max: 100, step: 1, default: 50 }
    ],
    'jpeg_compare': [
        { key: 'quality', label: '压缩质量', type: 'range', min: 5, max: 100, step: 1, default: 30 }
    ],
    'binary_rle': [
        { key: 'threshold', label: '二值化阈值', type: 'range', min: 0, max: 255, step: 1, default: 128 }
    ],
    'binary_huffman': [
        { key: 'threshold', label: '二值化阈值', type: 'range', min: 0, max: 255, step: 1, default: 128 }
    ],

    // 第九章
    'erosion_dilation': [
        { key: 'mode', label: '操作模式', type: 'select', options: ['腐蚀', '膨胀'], default: '腐蚀' },
        { key: 'ksize', label: '结构元素大小', type: 'select', options: [3, 5, 7, 9, 11], default: 3 },
        { key: 'iterations', label: '迭代次数', type: 'range', min: 1, max: 10, step: 1, default: 1 }
    ],
    'open_close': [
        { key: 'mode', label: '操作模式', type: 'select', options: ['开运算', '闭运算'], default: '开运算' },
        { key: 'ksize', label: '结构元素大小', type: 'select', options: [3, 5, 7, 9, 11], default: 5 }
    ],
    'morph_gradient': [
        { key: 'ksize', label: '结构元素大小', type: 'select', options: [3, 5, 7], default: 3 }
    ],
    'tophat': [
        { key: 'ksize', label: '结构元素大小', type: 'select', options: [3, 5, 7, 9, 11], default: 9 }
    ],
    'blackhat': [
        { key: 'ksize', label: '结构元素大小', type: 'select', options: [3, 5, 7, 9, 11], default: 9 }
    ],
    'skeletonize': [],

    // 第十章
    'otsu_threshold': [],
    'adaptive_threshold': [
        { key: 'block_size', label: '邻域大小', type: 'select', options: [3, 5, 7, 9, 11, 13, 15], default: 11 },
        { key: 'c', label: '常数 C', type: 'range', min: -10, max: 30, step: 1, default: 2 }
    ],
    'kmeans_segment': [
        { key: 'k', label: '聚类数 K', type: 'range', min: 2, max: 8, step: 1, default: 3 }
    ],
    'mean_shift_segment': [
        { key: 'sp', label: '空间半径', type: 'range', min: 5, max: 100, step: 1, default: 30 },
        { key: 'sr', label: '颜色半径', type: 'range', min: 5, max: 100, step: 1, default: 30 }
    ],
    'watershed': [
        { key: 'thresh', label: '前景阈值', type: 'range', min: 0, max: 255, step: 1, default: 100 }
    ],
    'grabcut': [
        { key: 'iters', label: '迭代次数', type: 'range', min: 1, max: 10, step: 1, default: 5 }
    ],

    // 第十一章
    'contour_extract': [
        { key: 'mode', label: '提取模式', type: 'select', options: ['所有轮廓', '最外层'], default: '所有轮廓' }
    ],
    'convex_hull': [],
    'min_enclosing': [
        { key: 'mode', label: '外接形状', type: 'select', options: ['矩形', '旋转矩形', '圆形', '全部显示'], default: '全部显示' }
    ],
    'contour_approx': [
        { key: 'epsilon', label: '近似精度', type: 'range', min: 0.001, max: 0.1, step: 0.001, default: 0.01 }
    ],
    'hu_moments': [],
    'shape_match': [],
    'fourier_descriptor': [
        { key: 'num_descriptors', label: '描述子数量', type: 'range', min: 5, max: 50, step: 1, default: 20 }
    ],

    // 第一章/第二章 数字图像基础
    'sampling_demo': [
        { key: 'sample_rate', label: '采样率', type: 'range', min: 0.05, max: 1.0, step: 0.05, default: 0.5 }
    ],
    'quantization_demo': [
        { key: 'bit_depth', label: '量化位深', type: 'select', options: [1, 2, 3, 4, 5, 6, 7, 8], default: 4 }
    ],
    'resolution_compare': [
        { key: 'scale', label: '缩放比例', type: 'range', min: 0.1, max: 1.0, step: 0.1, default: 0.5 }
    ],
    'pixel_neighbors': [
        { key: 'mode', label: '邻域类型', type: 'select', options: ['4-邻域', '8-邻域', '对角邻域'], default: '4-邻域' }
    ],
    'distance_metrics': [
        { key: 'mode', label: '距离类型', type: 'select', options: ['欧几里得距离', 'D4城市街区距离', 'D8棋盘距离'], default: '欧几里得距离' }
    ],
    'interpolation_demo': [
        { key: 'method', label: '插值方法', type: 'select', options: ['最近邻插值', '双线性插值', '双三次插值'], default: '双线性插值' }
    ],

    // 第十二章 目标检测与识别
    'template_matching': [
        { key: 'method', label: '匹配方法', type: 'select', options: ['平方差匹配', '归一化平方差', '归一化互相关', '相关系数匹配'], default: '归一化互相关' }
    ],
    'hough_lines': [
        { key: 'threshold', label: '投票阈值', type: 'range', min: 50, max: 300, step: 10, default: 150 },
        { key: 'min_length', label: '最小线长', type: 'range', min: 10, max: 200, step: 5, default: 50 }
    ],
    'hough_circles': [
        { key: 'dp', label: '累加器分辨率', type: 'range', min: 1.0, max: 2.0, step: 0.1, default: 1.2 },
        { key: 'min_dist', label: '圆心最小距离', type: 'range', min: 10, max: 200, step: 5, default: 50 },
        { key: 'param1', label: 'Canny高阈值', type: 'range', min: 50, max: 300, step: 10, default: 100 },
        { key: 'param2', label: '圆心检测阈值', type: 'range', min: 10, max: 100, step: 5, default: 30 }
    ],
    'corner_harris': [
        { key: 'block_size', label: '邻域大小', type: 'range', min: 2, max: 10, step: 1, default: 2 },
        { key: 'ksize', label: 'Sobel核大小', type: 'select', options: [3, 5, 7], default: 3 },
        { key: 'k', label: 'Harris参数k', type: 'range', min: 0.01, max: 0.1, step: 0.01, default: 0.04 }
    ],
    'sift_features': [],
    'hog_features': [
        { key: 'cell_size', label: 'Cell大小', type: 'select', options: [4, 8, 16], default: 8 },
        { key: 'block_size', label: 'Block大小', type: 'select', options: [2, 3, 4], default: 2 }
    ],
    // ── 综合工程案例参数 ──
    'case_01_satellite': [],
    'case_02_document': [],
    'case_03_defect': [],
    'case_04_ct_denoise': [],
    'case_05_photo_restore': [],
    'case_06_drone_veg': [],
    'case_07_panorama': [],
    'case_08_jpeg_opt': [],
    'case_09_pcb_inspect': [],
    'case_10_water_extract': [],
    'case_11_part_classify': [],
    'case_12_traffic_sign': []
};

// ---- 全局状态 ----
var uploadedFile = null;
var resultImageBase64 = null;
var processingTimer = null;       // debounce 定时器
var isProcessing = false;         // 是否正在处理中
var originalImageBase64 = null;  // 原始上传图片的 base64

function initOperationPage() {
    var params = new URLSearchParams(window.location.search);
    var chapter = parseInt(params.get('chapter'), 10) || 3;
    var chapterNames = {
        1: '第一章：绪论',
        2: '第二章：数字图像基础',
        3: '第三章：灰度变换与空间滤波',
        4: '第四章：频率域滤波',
        5: '第五章：图像复原与重建',
        6: '第六章：彩色图像处理',
        7: '第七章：小波变换与多分辨率处理',
        8: '第八章：图像压缩',
        9: '第九章：形态学图像处理',
        10: '第十章：图像分割',
        11: '第十一章：表示和描述',
        12: '第十二章：目标检测与识别'
    };
    var chapterName = chapterNames[chapter] || chapterNames[3];
    document.getElementById('chapterTitle').textContent =
        '西南交通大学希望学院 · 基础部 · 数字图像处理教学平台 — ' + chapterName;

    // 动态设置返回链接指向对应章节详情页
    var backLink = document.getElementById('topBackLink');
    if (backLink) {
        backLink.href = '/chapter/' + chapter;
    }

    // 填充操作下拉框
    var select = document.getElementById('operationSelect');
    var ops = CHAPTER_OPS[chapter] || [];
    ops.forEach(function (op) {
        var option = document.createElement('option');
        option.value = op.id;
        option.textContent = op.name;
        select.appendChild(option);
    });

    bindEvents();

    // 支持 URL ?operation=X 参数——直接跳转单个算法实操
    var opParam = params.get('operation');
    if (opParam) {
        var selectEl = document.getElementById('operationSelect');
        // 查找匹配的 option
        for (var i = 0; i < selectEl.options.length; i++) {
            if (selectEl.options[i].value === opParam) {
                selectEl.value = opParam;
                // 触发 change 事件加载参数和理论
                selectEl.dispatchEvent(new Event('change'));
                break;
            }
        }
    }
}

function bindEvents() {
    // 图片上传
    var uploadZone = document.getElementById('uploadZone');
    var imageInput = document.getElementById('imageInput');
    uploadZone.addEventListener('click', function () { imageInput.click(); });
    uploadZone.addEventListener('dragover', function (e) {
        e.preventDefault();
        uploadZone.style.borderColor = 'var(--primary-light)';
        uploadZone.style.background = 'rgba(41,128,185,0.05)';
    });
    uploadZone.addEventListener('dragleave', function () {
        uploadZone.style.borderColor = '';
        uploadZone.style.background = '';
    });
    uploadZone.addEventListener('drop', function (e) {
        e.preventDefault();
        uploadZone.style.borderColor = '';
        uploadZone.style.background = '';
        if (e.dataTransfer.files.length > 0) handleFile(e.dataTransfer.files[0]);
    });
    imageInput.addEventListener('change', function () {
        if (imageInput.files.length > 0) handleFile(imageInput.files[0]);
    });

    // 操作选择 → 动态生成参数，加载理论，自动触发处理，更新代码面板
    document.getElementById('operationSelect').addEventListener('change', function () {
        var opId = this.value;
        renderParams(opId);
        // 加载并展示理论内容、代码面板
        if (opId) {
            fetchTheory(opId);
            updateCodePanel(opId);
            // 更新 AI 助手上下文
            var opName = this.selectedOptions[0].textContent;
            if (window.AIAssistant) {
                window.AIAssistant.setContext({
                    operationId: opId,
                    operationName: opName
                });
            }
        } else {
            // 恢复占位选项：清空理论、代码、结果
            hideTheory();
            resetCodePanel();
            clearResultArea();
        }
        // 切换操作时自动处理
        if (uploadedFile && opId) {
            triggerProcess();
        }
    });

    // AI分析按钮
    document.getElementById('viewAnalysisBtn').addEventListener('click', startAnalyze);
    initModalEvents();
    // 下载按钮
    document.getElementById('downloadBtn').addEventListener('click', downloadResult);
}

function handleFile(file) {
    var allowed = ['image/jpeg', 'image/png', 'image/bmp', 'image/tiff'];
    if (allowed.indexOf(file.type) === -1) {
        alert('不支持的文件类型。请上传 JPG / PNG / BMP / TIFF 图片。');
        return;
    }
    if (file.size > 5 * 1024 * 1024) {
        alert('文件大小超过 5MB，请选择较小的图片。');
        return;
    }
    uploadedFile = file;
    var reader = new FileReader();
    reader.onload = function (e) {
        var preview = document.getElementById('uploadPreview');
        document.getElementById('uploadPlaceholder').style.display = 'none';
        preview.src = e.target.result;
        originalImageBase64 = e.target.result;
        preview.style.display = 'block';
    };
    reader.readAsDataURL(file);
    setStatus('idle', '图片已上传：「' + file.name + '」，请选择操作。');
    // 如果已选择操作，自动触发处理
    var opId = document.getElementById('operationSelect').value;
    if (opId) triggerProcess();
}

function renderParams(operationId) {
    var paramsSection = document.getElementById('paramsSection');
    var container = document.getElementById('paramsContainer');
    container.innerHTML = '';

    if (!operationId) {
        paramsSection.style.display = 'none';
        return;
    }

    var defs = OP_PARAMS[operationId] || [];
    if (defs.length === 0) {
        paramsSection.style.display = 'none';
    } else {
        paramsSection.style.display = 'block';
    }
    document.getElementById('processBtn').textContent = '拖动参数即可实时预览';

    defs.forEach(function (def) {
        var row = document.createElement('div');
        row.className = 'param-row';

        if (def.type === 'select') {
            var label = document.createElement('label');
            label.className = 'param-label';
            label.textContent = def.label;
            row.appendChild(label);
            var select = document.createElement('select');
            select.className = 'styled-select';
            select.dataset.paramKey = def.key;
            def.options.forEach(function (v) {
                var opt = document.createElement('option');
                opt.value = v;
                opt.textContent = v;
                if (v === def.default) opt.selected = true;
                select.appendChild(opt);
            });
            // 下拉框变化时实时处理
            select.addEventListener('change', function () {
                if (uploadedFile) triggerProcess();
            });
            row.appendChild(select);

        } else if (def.type === 'range') {
            var label = document.createElement('label');
            label.className = 'param-label';
            label.innerHTML = def.label + ' <span class="param-value-display">' + def.default + '</span>';
            row.appendChild(label);
            var slider = document.createElement('input');
            slider.type = 'range';
            slider.className = 'param-slider';
            slider.min = def.min;
            slider.max = def.max;
            slider.step = def.step;
            slider.value = def.default;
            slider.dataset.paramKey = def.key;
            slider.addEventListener('input', function () {
                var display = this.parentElement.querySelector('.param-value-display');
                if (display) display.textContent = this.value;
                // 拖动时实时触发（debounce）
                if (uploadedFile) triggerProcess();
            });
            row.appendChild(slider);
        }
        container.appendChild(row);
    });
}

function collectParams() {
    var params = {};
    var inputs = document.querySelectorAll('#paramsContainer [data-param-key]');
    var stringParams = ['channel', 'mode', 'colormap'];
    inputs.forEach(function (el) {
        var key = el.dataset.paramKey;
        if (el.tagName === 'SELECT') {
            var val = el.value;
            if (stringParams.indexOf(key) !== -1 || isNaN(parseInt(val, 10))) {
                params[key] = val;
            } else {
                params[key] = parseInt(val, 10);
            }
        } else if (el.type === 'range') {
            var val = parseFloat(el.value);
            if (['cutoff', 'low_cutoff', 'high_cutoff', 'ksize', 'low_threshold', 'high_threshold',
                 'iterations', 'k', 'levels', 'quality', 'threshold', 'num_descriptors',
                 'thresh', 'block_size', 'tile_size', 'd', 'radius', 'c', 'shift', 'beta',
                 'sp', 'sr', 'iters'].indexOf(key) !== -1) {
                params[key] = Math.round(val);
            } else {
                params[key] = val;
            }
        }
    });
    return params;
}

/**
 * 防抖触发处理（300ms）
 */
function triggerProcess() {
    if (processingTimer) clearTimeout(processingTimer);
    processingTimer = setTimeout(function () {
        startProcess();
    }, 300);
}

/**
 * 开始处理图像（实时调参模式）
 */
function startProcess() {
    if (!uploadedFile) return;
    var operationId = document.getElementById('operationSelect').value;
    if (!operationId) return;
    if (isProcessing) {
        // 如果正在处理中，延迟重试
        processingTimer = setTimeout(startProcess, 200);
        return;
    }

    isProcessing = true;
    var params = collectParams();
    var operationName = document.getElementById('operationSelect').selectedOptions[0].textContent;
    var chapterId = (new URLSearchParams(window.location.search)).get('chapter') || '';

    setStatus('processing', '正在处理：' + operationName + '…');

    var formData = new FormData();
    formData.append('image', uploadedFile);
    formData.append('operation', operationId);
    formData.append('params', JSON.stringify(params));

    var startTime = Date.now();

    fetch('/process', {
        method: 'POST',
        body: formData
    })
    .then(function (resp) {
        if (!resp.ok) return resp.json().then(function (err) { throw new Error(err.message); });
        return resp.json();
    })
    .then(function (data) {
        var durationMs = Date.now() - startTime;
        if (data.status === 'success') {
            resultImageBase64 = data.image_base64;
            var area = document.getElementById('resultImageArea');
            area.innerHTML = '<img src="' + data.image_base64 + '" class="result-image" alt="处理结果">';
            document.getElementById('resultActions').style.display = 'block';
            document.getElementById('viewAnalysisBtn').style.display = 'inline-block';
            document.getElementById('viewAnalysisBtn').disabled = false;
            setStatus('done', '处理完成 — ' + data.operation_name);
            // 主动AI分析卡片
            showAIAnalysisCard(data.ai_analysis);
            // 操作埋点：成功
            logOperation(chapterId, operationId, operationName, params, uploadedFile.name, 'success', null, durationMs);
        } else {
            setStatus('error', '处理失败：' + (data.message || '未知错误'));
            // 主动AI引导提示
            showAIGuidance(data.ai_guidance, data.message);
            // 操作埋点：失败
            logOperation(chapterId, operationId, operationName, params, uploadedFile.name, 'error', data.message, durationMs);
        }
    })
    .catch(function (err) {
        var errMsg = err.message || '';
        // 中文化常见错误
        if (errMsg.indexOf('grayscale') > -1 || errMsg.indexOf('gray') > -1) {
            errMsg = '该图像为灰度图，请上传彩色图像';
        } else if (errMsg.indexOf('size') > -1 || errMsg.indexOf('small') > -1) {
            errMsg = '图像尺寸过小，无法进行该操作';
        } else if (errMsg.indexOf('empty') > -1) {
            errMsg = '未收到图像数据，请重新上传';
        } else if (errMsg.length > 100) {
            errMsg = '处理失败，请检查输入参数后重试';
        }
        setStatus('error', '处理失败：' + errMsg);
        logOperation(chapterId, operationId, operationName, params, uploadedFile.name, 'error', errMsg, Date.now() - startTime);
    })
    .finally(function () {
        isProcessing = false;
    });
}

// ========== 主动AI分析卡片 ==========
function showAIAnalysisCard(analysis) {
    var card = document.getElementById('aiAnalysisCard');
    if (!card) return;
    if (!analysis) {
        card.style.display = 'none';
        return;
    }
    card.style.display = 'block';
    card.innerHTML =
        '<div class="ai-card-header">' +
        '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a4 4 0 0 1 4 4c0 1.5-.8 2.8-2 3.5V10h-4V9.5C8.8 8.8 8 7.5 8 6a4 4 0 0 1 4-4z"/><path d="M5 20a7 7 0 0 1 14 0"/></svg>' +
        '<span>AI 智能分析</span>' +
        '<span class="ai-card-badge">自动生成</span>' +
        '</div>' +
        '<div class="ai-card-body">' + formatAIAnalysis(analysis) + '</div>';
}

function formatAIAnalysis(text) {
    if (!text) return '';
    var parts = text.split(/\n+/).filter(function (l) { return l.trim(); });
    return parts.map(function (line) {
        return '<p style="margin:0.4rem 0;line-height:1.7;">' + escapeHtml(line) + '</p>';
    }).join('');
}

// ========== 主动AI引导提示 ==========
function showAIGuidance(guidance, errMsg) {
    if (!guidance) return;
    var overlay = document.getElementById('aiGuidanceOverlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'aiGuidanceOverlay';
        overlay.className = 'ai-guidance-overlay';
        document.body.appendChild(overlay);
    }
    overlay.innerHTML =
        '<div class="ai-guidance-modal">' +
        '<div class="ai-guidance-header">' +
        '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>' +
        '<span>AI 操作引导</span>' +
        '</div>' +
        '<div class="ai-guidance-body">' + formatAIAnalysis(guidance) + '</div>' +
        '<div class="ai-guidance-footer"><button class="ai-guidance-close" onclick="closeAIGuidance()">我知道了</button></div>' +
        '</div>';
    overlay.style.display = 'flex';
}

function closeAIGuidance() {
    var overlay = document.getElementById('aiGuidanceOverlay');
    if (overlay) overlay.style.display = 'none';
}

function startAnalyze() {
    if (!resultImageBase64) {
        alert('请先完成图像处理。');
        return;
    }
    var operationId = document.getElementById('operationSelect').value;
    var params = collectParams();
    var btn = document.getElementById('viewAnalysisBtn');
    var modal = document.getElementById('analysisModal');
    var modalBody = document.getElementById('modalBody');

    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> 分析中…';
    modal.style.display = 'flex';
    modalBody.innerHTML = '<p style="text-align:center;color:var(--primary-light);"><span class="spinner"></span> 正在生成量化分析报告…</p>';

    fetch('/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            original_image_base64: originalImageBase64 || resultImageBase64,
            image_base64: resultImageBase64,
            operation: operationId,
            params: params
        })
    })
    .then(function (resp) {
        if (!resp.ok) return resp.json().then(function (err) { throw new Error(err.message); });
        return resp.json();
    })
    .then(function (data) {
        if (data.status === 'success') {
            modalBody.innerHTML = '<pre style="margin:0;white-space:pre-wrap;font-family:inherit;font-size:0.84rem;line-height:1.75;">' + escapeHtml(data.analysis) + '</pre>';
        } else {
            modalBody.innerHTML = '<p style="color:#e74c3c;text-align:center;">' + escapeHtml(data.message) + '</p>';
        }
    })
    .catch(function (err) {
        var errMsg = escapeHtml(err.message || '');
        if (errMsg.length > 100) errMsg = '分析失败，请检查输入后重试';
        modalBody.innerHTML = '<p style="color:#e74c3c;text-align:center;">分析失败：' + errMsg + '</p>';
    })
    .finally(function () {
        btn.disabled = false;
        btn.innerHTML = '<span class="spinner" style="display:none;"></span> 查看分析报告';
    });
}

function closeAnalysisModal() {
    document.getElementById('analysisModal').style.display = 'none';
}

function initModalEvents() {
    document.getElementById('modalClose').addEventListener('click', closeAnalysisModal);
    document.getElementById('modalCloseBtn').addEventListener('click', closeAnalysisModal);
    document.getElementById('analysisModal').addEventListener('click', function(e) {
        if (e.target === this) closeAnalysisModal();
    });
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') closeAnalysisModal();
    });
}

function downloadResult() {
    if (!resultImageBase64) return;
    var a = document.createElement('a');
    a.href = resultImageBase64;
    a.download = 'processed_image.png';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

function setStatus(type, message) {
    var area = document.getElementById('statusArea');
    switch (type) {
        case 'idle':
            area.innerHTML = escapeHtml(message);
            break;
        case 'processing':
            area.innerHTML = '<span class="spinner"></span> ' + escapeHtml(message);
            break;
        case 'done':
            area.innerHTML = '<span style="color:#27ae60;font-weight:600;">&#10003;</span> ' + escapeHtml(message);
            break;
        case 'error':
            area.innerHTML = '<span style="color:#e74c3c;font-weight:600;">&#10007;</span> ' + escapeHtml(message);
            break;
    }
}

function escapeHtml(str) {
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
}

/* ================================================================
   理论展示 —— 从 /theory/<op_id> 加载并渲染理论内容
   ================================================================ */

var theoryCache = {};  // 缓存理论数据，避免重复请求

function fetchTheory(opId) {
    // 检查缓存
    if (theoryCache[opId]) {
        renderTheory(theoryCache[opId]);
        return;
    }

    var theoryCard = document.getElementById('theoryCard');
    var sections = document.getElementById('theorySections');
    sections.innerHTML = '<div class="theory-loading"><span class="spinner"></span> 加载理论内容…</div>';
    theoryCard.style.display = 'block';

    fetch('/theory/' + opId)
        .then(function (resp) {
            if (!resp.ok) return resp.json().then(function (err) { throw new Error(err.message); });
            return resp.json();
        })
        .then(function (data) {
            if (data.status === 'success') {
                theoryCache[opId] = data.data;
                renderTheory(data.data);
            } else {
                sections.innerHTML = '<p class="theory-error">理论数据加载失败: ' + escapeHtml(data.message) + '</p>';
            }
        })
        .catch(function (err) {
            sections.innerHTML = '<p class="theory-error">理论数据加载失败: ' + escapeHtml(err.message) + '</p>';
        });
}

function renderTheory(data) {
    var theoryCard = document.getElementById('theoryCard');
    var badge = document.getElementById('theoryBadge');
    var opName = document.getElementById('theoryOpName');
    var sections = document.getElementById('theorySections');

    badge.textContent = data.chapter_name || ('第' + data.chapter + '章');
    opName.textContent = '  ·  ' + data.name + '  ·  理论解析';

    var iconMap = {
        'book': '&#128214;',
        'formula': '&#8721;',
        'steps': '&#9881;',
        'params': '&#9881;'
    };

    var html = '';
    for (var i = 0; i < data.sections.length; i++) {
        var sec = data.sections[i];
        var icon = iconMap[sec.icon] || '';
        html += '<details class="theory-section" open>';
        html += '<summary class="theory-section-title">';
        html += '<span class="theory-section-icon">' + icon + '</span>';
        html += sec.title;
        html += '</summary>';
        html += '<div class="theory-section-body">';
        // 将换行转为段落
        var content = sec.content
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
        // 处理公式中的上标和下标
        content = content.replace(/²/g, '<sup>2</sup>');
        content = content.replace(/³/g, '<sup>3</sup>');
        content = content.replace(/⁴/g, '<sup>4</sup>');
        content = content.replace(/₀/g, '<sub>0</sub>');
        content = content.replace(/₁/g, '<sub>1</sub>');
        content = content.replace(/₂/g, '<sub>2</sub>');
        content = content.replace(/₃/g, '<sub>3</sub>');
        content = content.replace(/₄/g, '<sub>4</sub>');
        content = content.replace(/₅/g, '<sub>5</sub>');
        content = content.replace(/₆/g, '<sub>6</sub>');
        content = content.replace(/₇/g, '<sub>7</sub>');
        content = content.replace(/₈/g, '<sub>8</sub>');
        content = content.replace(/₉/g, '<sub>9</sub>');
        // 转换希腊字母
        content = content.replace(/σ/g, '<em>&sigma;</em>');
        content = content.replace(/μ/g, '<em>&mu;</em>');
        content = content.replace(/θ/g, '<em>&theta;</em>');
        content = content.replace(/λ/g, '<em>&lambda;</em>');
        content = content.replace(/ω/g, '<em>&omega;</em>');
        content = content.replace(/φ/g, '<em>&phi;</em>');
        content = content.replace(/α/g, '<em>&alpha;</em>');
        content = content.replace(/β/g, '<em>&beta;</em>');
        content = content.replace(/γ/g, '<em>&gamma;</em>');
        content = content.replace(/ε/g, '<em>&epsilon;</em>');
        content = content.replace(/Δ/g, '<em>&Delta;</em>');
        content = content.replace(/Σ/g, '<em>&Sigma;</em>');
        content = content.replace(/Π/g, '<em>&Pi;</em>');
        content = content.replace(/∇/g, '<em>&nabla;</em>');
        content = content.replace(/∞/g, '<em>&infin;</em>');
        content = content.replace(/∂/g, '<em>&part;</em>');
        content = content.replace(/√/g, '&radic;');
        content = content.replace(/·/g, '&middot;');
        content = content.replace(/×/g, '&times;');
        // 将 • 开头的行包装
        content = content.replace(/•/g, '<br>•');
        // 将以 Step 开头的行突出
        content = content.replace(/(Step \d+)/g, '<strong>$1</strong>');
        // 将换行符转换为 <br>，确保算法步骤等每行独立显示
        content = content.replace(/\n/g, '<br>');
        html += '<p>' + content + '</p>';
        html += '</div>';
        html += '</details>';
    }

    sections.innerHTML = html;
    theoryCard.style.display = 'block';
}

function hideTheory() {
    document.getElementById('theoryCard').style.display = 'none';
    document.getElementById('theorySections').innerHTML = '';
}

/* ================================================================
   Python 代码库（完整可运行，含 import 和核心逻辑）
   ================================================================ */
var OP_CODE = {
    "image_inversion": `import cv2
import numpy as np

# 读取图像
img = cv2.imread('input.jpg')
# 图像反转：s = 255 - r
result = cv2.bitwise_not(img)
cv2.imwrite('output.jpg', result)`,
    "log_transform": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
c = 20  # 缩放系数
# 对数变换：s = c * log(1 + r)
result = c * np.log1p(gray.astype(np.float64) / 255.0 * 255)
result = np.clip(result / result.max() * 255, 0, 255).astype(np.uint8)
cv2.imwrite('output.jpg', result)`,
    "histogram_equalization": `import cv2

img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# 直方图均衡化
result = cv2.equalizeHist(gray)
cv2.imwrite('output.jpg', result)`,
    "clahe": `import cv2

img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# 自适应直方图均衡化 (CLAHE)
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
result = clahe.apply(gray)
cv2.imwrite('output.jpg', result)`,
    "gamma_correction": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
gamma = 1.0  # gamma值
# 伽马校正：s = 255 * (r/255)^(1/gamma)
inv_gamma = 1.0 / gamma
table = np.array([(i / 255.0) ** inv_gamma * 255 for i in range(256)]).astype(np.uint8)
result = cv2.LUT(gray, table)
cv2.imwrite('output.jpg', result)`,
    "median_blur": `import cv2

img = cv2.imread('input.jpg')
ksize = 5  # 核大小（奇数）
result = cv2.medianBlur(img, ksize)
cv2.imwrite('output.jpg', result)`,
    "gaussian_blur": `import cv2

img = cv2.imread('input.jpg')
ksize = 5   # 核大小（奇数）
sigma = 1.0 # 标准差
result = cv2.GaussianBlur(img, (ksize, ksize), sigma)
cv2.imwrite('output.jpg', result)`,
    "bilateral_filter": `import cv2

img = cv2.imread('input.jpg')
d = 9             # 邻域直径
sigma_color = 75  # 颜色空间标准差
sigma_space = 75  # 坐标空间标准差
result = cv2.bilateralFilter(img, d, sigma_color, sigma_space)
cv2.imwrite('output.jpg', result)`,
    "laplacian": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# 拉普拉斯锐化
lap = cv2.Laplacian(gray, cv2.CV_64F)
result = np.uint8(np.absolute(lap))
cv2.imwrite('output.jpg', result)`,
    "unsharp_mask": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
amount = 1.5  # 锐化强度
radius = 3    # 模糊半径
blurred = cv2.GaussianBlur(img, (radius * 2 + 1, radius * 2 + 1), radius)
# USM锐化: g = f + amount * (f - blurred)
result = cv2.addWeighted(img, 1.0 + amount, blurred, -amount, 0)
result = np.clip(result, 0, 255).astype(np.uint8)
cv2.imwrite('output.jpg', result)`,
    "sobel_sharpen": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
ksize = 3  # Sobel核大小
gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=ksize)
gy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=ksize)
result = np.uint8(np.sqrt(gx**2 + gy**2))
cv2.imwrite('output.jpg', result)`,
    "ideal_lowpass": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# 缩放到偶数尺寸
h, w = gray.shape
if h % 2: h -= 1
if w % 2: w -= 1
gray = gray[:h, :w]
cutoff = 50  # 截止频率
# DFT
dft = cv2.dft(np.float32(gray), flags=cv2.DFT_COMPLEX_OUTPUT)
dft_shift = np.fft.fftshift(dft)
# 理想低通掩码
y, x = np.ogrid[:h, :w]
cy, cx = h // 2, w // 2
mask = (np.sqrt((y - cy)**2 + (x - cx)**2) <= cutoff).astype(np.float32)
dft_shift *= mask[:, :, np.newaxis]
# 逆DFT
f_ishift = np.fft.ifftshift(dft_shift)
img_back = cv2.idft(f_ishift)
result = cv2.magnitude(img_back[:,:,0], img_back[:,:,1])
result = cv2.normalize(result, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
cv2.imwrite('output.jpg', result)`,
    "gaussian_noise": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
sigma = 25  # 噪声标准差
noise = np.random.normal(0, sigma, img.shape).astype(np.int16)
result = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
cv2.imwrite('output.jpg', result)`,
    "sp_noise": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
amount = 0.05  # 噪声比例
result = img.copy()
h, w = result.shape[:2]
for c in range(3):
    n_salt = int(w * h * amount / 2)
    xs = np.random.randint(0, w, n_salt)
    ys = np.random.randint(0, h, n_salt)
    result[ys, xs, c] = 255
    n_pepper = int(w * h * amount / 2)
    xp = np.random.randint(0, w, n_pepper)
    yp = np.random.randint(0, h, n_pepper)
    result[yp, xp, c] = 0
cv2.imwrite('output.jpg', result)`,
    "sobel": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
ksize = 3
gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=ksize)
gy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=ksize)
result = np.uint8(np.sqrt(gx**2 + gy**2))
cv2.imwrite('output.jpg', result)`,
    "canny": `import cv2

img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
low = 50   # 低阈值
high = 150 # 高阈值
result = cv2.Canny(gray, low, high)
cv2.imwrite('output.jpg', result)`,
    "otsu_threshold": `import cv2

img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# Otsu自动阈值
_, result = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
cv2.imwrite('output.jpg', result)`,
    "sift_features": `import cv2

img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
sift = cv2.SIFT_create()
keypoints, descriptors = sift.detectAndCompute(gray, None)
# 绘制关键点
result = cv2.drawKeypoints(img, keypoints, None,
    flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
cv2.imwrite('output.jpg', result)`,
    "corner_harris": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
gray_f = np.float32(gray)
# Harris角点检测
dst = cv2.cornerHarris(gray_f, blockSize=2, ksize=3, k=0.04)
dst = cv2.dilate(dst, None)
result = img.copy()
result[dst > 0.01 * dst.max()] = [0, 0, 255]
cv2.imwrite('output.jpg', result)`,
    "contrast_stretch": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
low_percent = 2   # 低百分比剪裁
high_percent = 98 # 高百分比剪裁
# 对比度拉伸：将像素值线性映射到 [low_percent%, high_percent%] 范围
low_val = np.percentile(gray, low_percent)
high_val = np.percentile(gray, high_percent)
result = np.clip((gray.astype(np.float32) - low_val) * 255.0 / (high_val - low_val + 1e-6), 0, 255).astype(np.uint8)
cv2.imwrite('output.jpg', result)`,
    "ideal_highpass": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# 缩放到偶数尺寸
h, w = gray.shape
if h % 2: h -= 1
if w % 2: w -= 1
gray = gray[:h, :w]
cutoff = 30  # 截止频率
# DFT
dft = cv2.dft(np.float32(gray), flags=cv2.DFT_COMPLEX_OUTPUT)
dft_shift = np.fft.fftshift(dft)
# 理想高通掩码
y, x = np.ogrid[:h, :w]
cy, cx = h // 2, w // 2
mask = (np.sqrt((y - cy)**2 + (x - cx)**2) > cutoff).astype(np.float32)
dft_shift *= mask[:, :, np.newaxis]
# 逆DFT
f_ishift = np.fft.ifftshift(dft_shift)
img_back = cv2.idft(f_ishift)
result = cv2.normalize(cv2.magnitude(img_back[:,:,0], img_back[:,:,1]), None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
cv2.imwrite('output.jpg', result)`,
    "butterworth_lowpass": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
h, w = gray.shape
if h % 2: h -= 1
if w % 2: w -= 1
gray = gray[:h, :w]
cutoff = 50  # 截止频率 D0
order = 4    # 巴特沃斯阶数
# DFT
dft = cv2.dft(np.float32(gray), flags=cv2.DFT_COMPLEX_OUTPUT)
dft_shift = np.fft.fftshift(dft)
y, x = np.ogrid[:h, :w]
d = np.sqrt((y - h//2)**2 + (x - w//2)**2)
# 巴特沃斯低通: H = 1 / (1 + (D/D0)^(2n))
mask = (1.0 / (1.0 + (d / cutoff)**(2 * order))).astype(np.float32)
dft_shift *= mask[:, :, np.newaxis]
f_ishift = np.fft.ifftshift(dft_shift)
img_back = cv2.idft(f_ishift)
result = cv2.normalize(cv2.magnitude(img_back[:,:,0], img_back[:,:,1]), None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
cv2.imwrite('output.jpg', result)`,
    "butterworth_highpass": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
h, w = gray.shape
if h % 2: h -= 1
if w % 2: w -= 1
gray = gray[:h, :w]
cutoff = 30  # 截止频率 D0
order = 4    # 巴特沃斯阶数
# DFT
dft = cv2.dft(np.float32(gray), flags=cv2.DFT_COMPLEX_OUTPUT)
dft_shift = np.fft.fftshift(dft)
y, x = np.ogrid[:h, :w]
d = np.sqrt((y - h//2)**2 + (x - w//2)**2)
# 巴特沃斯高通: H = 1 / (1 + (D0/D)^(2n))
mask = (1.0 / (1.0 + (cutoff / (d + 1e-6))**(2 * order))).astype(np.float32)
dft_shift *= mask[:, :, np.newaxis]
f_ishift = np.fft.ifftshift(dft_shift)
img_back = cv2.idft(f_ishift)
result = cv2.normalize(cv2.magnitude(img_back[:,:,0], img_back[:,:,1]), None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
cv2.imwrite('output.jpg', result)`,
    "gaussian_lowpass": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
h, w = gray.shape
if h % 2: h -= 1
if w % 2: w -= 1
gray = gray[:h, :w]
cutoff = 50  # 截止频率 D0
# DFT
dft = cv2.dft(np.float32(gray), flags=cv2.DFT_COMPLEX_OUTPUT)
dft_shift = np.fft.fftshift(dft)
y, x = np.ogrid[:h, :w]
d = np.sqrt((y - h//2)**2 + (x - w//2)**2)
# 高斯低通: H = exp(-D^2 / (2*D0^2))
mask = np.exp(-d**2 / (2 * cutoff**2)).astype(np.float32)
dft_shift *= mask[:, :, np.newaxis]
f_ishift = np.fft.ifftshift(dft_shift)
img_back = cv2.idft(f_ishift)
result = cv2.normalize(cv2.magnitude(img_back[:,:,0], img_back[:,:,1]), None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
cv2.imwrite('output.jpg', result)`,
    "gaussian_highpass": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
h, w = gray.shape
if h % 2: h -= 1
if w % 2: w -= 1
gray = gray[:h, :w]
cutoff = 30  # 截止频率 D0
# DFT
dft = cv2.dft(np.float32(gray), flags=cv2.DFT_COMPLEX_OUTPUT)
dft_shift = np.fft.fftshift(dft)
y, x = np.ogrid[:h, :w]
d = np.sqrt((y - h//2)**2 + (x - w//2)**2)
# 高斯高通: H = 1 - exp(-D^2 / (2*D0^2))
mask = (1.0 - np.exp(-d**2 / (2 * cutoff**2))).astype(np.float32)
dft_shift *= mask[:, :, np.newaxis]
f_ishift = np.fft.ifftshift(dft_shift)
img_back = cv2.idft(f_ishift)
result = cv2.normalize(cv2.magnitude(img_back[:,:,0], img_back[:,:,1]), None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
cv2.imwrite('output.jpg', result)`,
    "bandpass_filter": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
h, w = gray.shape
if h % 2: h -= 1
if w % 2: w -= 1
gray = gray[:h, :w]
low_cutoff = 20   # 低频截止
high_cutoff = 80  # 高频截止
# DFT
dft = cv2.dft(np.float32(gray), flags=cv2.DFT_COMPLEX_OUTPUT)
dft_shift = np.fft.fftshift(dft)
y, x = np.ogrid[:h, :w]
d = np.sqrt((y - h//2)**2 + (x - w//2)**2)
# 带通 = 高通 * 低通
lowpass = np.exp(-d**2 / (2 * high_cutoff**2))
highpass = 1.0 - np.exp(-d**2 / (2 * low_cutoff**2))
mask = (lowpass * highpass).astype(np.float32)
dft_shift *= mask[:, :, np.newaxis]
f_ishift = np.fft.ifftshift(dft_shift)
img_back = cv2.idft(f_ishift)
result = cv2.normalize(cv2.magnitude(img_back[:,:,0], img_back[:,:,1]), None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
cv2.imwrite('output.jpg', result)`,
    "mean_filter_restore": `import cv2

img = cv2.imread('input.jpg')
ksize = 5  # 核大小（奇数）
# 均值滤波：用邻域像素平均值替换中心像素
result = cv2.blur(img, (ksize, ksize))
cv2.imwrite('output.jpg', result)`,
    "median_restore": `import cv2

img = cv2.imread('input.jpg')
ksize = 5  # 核大小（奇数）
# 中值滤波：用邻域像素中值替换中心像素，对椒盐噪声效果极佳
result = cv2.medianBlur(img, ksize)
cv2.imwrite('output.jpg', result)`,
    "nlm_denoise": `import cv2

img = cv2.imread('input.jpg')
h = 10  # 滤波强度，值越大去噪越强但细节损失越多
# 非局部均值去噪 (Non-Local Means Denoising)
result = cv2.fastNlMeansDenoisingColored(img, None, h, h, 7, 21)
cv2.imwrite('output.jpg', result)`,
    "wiener_filter": `import cv2
import numpy as np
from scipy.signal import wiener

img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
ksize = 5  # 滤波器窗口大小
# 维纳滤波：最小均方误差准则下的自适应滤波器
result = wiener(gray.astype(np.float64), (ksize, ksize))
result = np.clip(result, 0, 255).astype(np.uint8)
cv2.imwrite('output.jpg', result)`,
    "rgb_split": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
# RGB通道分离
b, g, r = cv2.split(img)
# 合并显示：R=红色通道, G=绿色通道, B=蓝色通道
zeros = np.zeros_like(b)
# 显示蓝色通道
result = cv2.merge([b, zeros, zeros])
cv2.imwrite('output.jpg', result)`,
    "rgb_to_hsv": `import cv2

img = cv2.imread('input.jpg')
# RGB → HSV 色彩空间转换
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
# 转回BGR以正常显示
result = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
cv2.imwrite('output.jpg', result)`,
    "hue_adjust": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
shift = 30  # 色相偏移量 [-180, 180]
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
# 色调调整：H通道加上偏移量
hsv[:, :, 0] = np.mod(hsv[:, :, 0] + shift, 180)
hsv = hsv.astype(np.uint8)
result = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
cv2.imwrite('output.jpg', result)`,
    "saturation_adjust": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
factor = 1.5  # 饱和度因子 [0, 3]
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
# 饱和度调整：S通道乘以因子
hsv[:, :, 1] = np.clip(hsv[:, :, 1] * factor, 0, 255)
hsv = hsv.astype(np.uint8)
result = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
cv2.imwrite('output.jpg', result)`,
    "brightness_adjust": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
beta = 30  # 亮度增量 [-100, 100]
# 亮度调整：所有像素值加上偏移量
result = np.clip(img.astype(np.int16) + beta, 0, 255).astype(np.uint8)
cv2.imwrite('output.jpg', result)`,
    "color_balance": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
r_gain = 1.2  # 红色通道增益
g_gain = 1.0  # 绿色通道增益
b_gain = 0.9  # 蓝色通道增益
# 色彩平衡：分别调整RGB各通道增益
b, g, r = cv2.split(img.astype(np.float32))
b = np.clip(b * b_gain, 0, 255)
g = np.clip(g * g_gain, 0, 255)
r = np.clip(r * r_gain, 0, 255)
result = cv2.merge([b, g, r]).astype(np.uint8)
cv2.imwrite('output.jpg', result)`,
    "pseudo_color": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# 假彩色增强：使用COLORMAP_JET将灰度图映射到伪彩色
result = cv2.applyColorMap(gray, cv2.COLORMAP_JET)
cv2.imwrite('output.jpg', result)`,
    "color_hist_eq": `import cv2

img = cv2.imread('input.jpg')
# 彩色直方图均衡化：在HSV空间对V通道做均衡化
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
hsv[:, :, 2] = cv2.equalizeHist(hsv[:, :, 2])
result = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
cv2.imwrite('output.jpg', result)`,
    "gaussian_pyramid": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
levels = 3  # 金字塔层数
# 高斯金字塔：逐层降采样（先高斯模糊再缩小一半）
pyramid = [img]
for i in range(levels):
    img = cv2.pyrDown(img)
    pyramid.append(img)
# 显示最顶层（分辨率最低的图像）
result = pyramid[-1]
# 放大回原始尺寸以便对比
for _ in range(levels):
    result = cv2.pyrUp(result)
result = cv2.resize(result, (pyramid[0].shape[1], pyramid[0].shape[0]))
cv2.imwrite('output.jpg', result)`,
    "laplacian_pyramid": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
levels = 3  # 金字塔层数
# 拉普拉斯金字塔：L_i = G_i - pyrUp(pyrDown(G_i))
gaussian = [img.astype(np.float32)]
for i in range(levels):
    gaussian.append(cv2.pyrDown(gaussian[-1]).astype(np.float32))
laplacian = []
for i in range(levels):
    expanded = cv2.pyrUp(gaussian[i + 1])
    if expanded.shape != gaussian[i].shape:
        expanded = cv2.resize(expanded, (gaussian[i].shape[1], gaussian[i].shape[0]))
    lap = gaussian[i] - expanded
    lap_norm = cv2.normalize(lap, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    laplacian.append(lap_norm)
# 显示第一层拉普拉斯（包含高频细节）
result = laplacian[0]
cv2.imwrite('output.jpg', result)`,
    "pyramid_blend": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
levels = 3
# 多分辨率融合：重建拉普拉斯金字塔
gaussian = [img.astype(np.float32)]
for i in range(levels):
    gaussian.append(cv2.pyrDown(gaussian[-1]).astype(np.float32))
# 从最底层开始逐层重建
recon = gaussian[-1]
for i in range(levels - 1, -1, -1):
    recon = cv2.pyrUp(recon)
    if recon.shape != gaussian[i].shape:
        recon = cv2.resize(recon, (gaussian[i].shape[1], gaussian[i].shape[0]))
result = np.clip(recon, 0, 255).astype(np.uint8)
cv2.imwrite('output.jpg', result)`,
    "dwt_denoise": `import cv2
import numpy as np
import pywt

img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
threshold = 30  # 小波阈值系数
# DWT降噪：对图像做2级小波分解，对高频系数做软阈值处理
coeffs = pywt.wavedec2(gray, 'db4', level=2)
# 保留近似系数不变，对细节系数做阈值处理
coeffs_thresh = [coeffs[0]]
for detail in coeffs[1:]:
    cH, cV, cD = detail
    cH = pywt.threshold(cH, threshold, mode='soft')
    cV = pywt.threshold(cV, threshold, mode='soft')
    cD = pywt.threshold(cD, threshold, mode='soft')
    coeffs_thresh.append((cH, cV, cD))
# 小波重构
result = pywt.waverec2(coeffs_thresh, 'db4')
result = np.clip(result, 0, 255).astype(np.uint8)
cv2.imwrite('output.jpg', result)`,
    "dwt_edge_enhance": `import cv2
import numpy as np
import pywt

img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# DWT边缘增强：放大细节系数
coeffs = pywt.wavedec2(gray, 'db4', level=2)
# 放大细节系数以增强边缘
coeffs_enhanced = [coeffs[0]]
for detail in coeffs[1:]:
    cH, cV, cD = detail
    coeffs_enhanced.append((cH * 1.5, cV * 1.5, cD * 1.5))
result = pywt.waverec2(coeffs_enhanced, 'db4')
result = np.clip(result, 0, 255).astype(np.uint8)
cv2.imwrite('output.jpg', result)`,
    "dct_visualize": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
# DCT变换可视化
dct = cv2.dct(gray)
# 对数幅度谱以便可视化
magnitude = np.log(np.abs(dct) + 1)
result = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
cv2.imwrite('output.jpg', result)`,
    "jpeg_simulate": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
quality = 80  # JPEG质量 [1, 100]
# JPEG压缩模拟：编码-解码流程
encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
_, encoded = cv2.imencode('.jpg', img, encode_param)
result = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
cv2.imwrite('output.jpg', result)`,
    "jpeg_compare": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
quality = 50  # JPEG质量 [5, 100]
# JPEG压缩质量对比：不同质量参数下的编解码
encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
_, encoded = cv2.imencode('.jpg', img, encode_param)
result = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
cv2.imwrite('output.jpg', result)`,
    "binary_rle": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# 二值化
_, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
# 游程编码 (Run-Length Encoding)
flat = binary.flatten()
rle = []
count = 1
for i in range(1, len(flat)):
    if flat[i] == flat[i-1]:
        count += 1
    else:
        rle.append((int(flat[i-1]), count))
        count = 1
rle.append((int(flat[-1]), count))
compression_ratio = len(flat) / (len(rle) * 2)
print(f"压缩比: {compression_ratio:.2f}:1")
result = binary
cv2.imwrite('output.jpg', result)`,
    "binary_huffman": `import cv2
import numpy as np
from collections import Counter
import heapq

img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# 哈夫曼编码模拟：统计灰度频率构建编码表
freq = Counter(gray.flatten())
# 构建哈夫曼树
heap = [[weight, [pixel, ""]] for pixel, weight in freq.items()]
heapq.heapify(heap)
while len(heap) > 1:
    lo = heapq.heappop(heap)
    hi = heapq.heappop(heap)
    for pair in lo[1:]: pair[1] = '0' + pair[1]
    for pair in hi[1:]: pair[1] = '1' + pair[1]
    heapq.heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])
huffman = sorted(heapq.heappop(heap)[1:], key=lambda p: (len(p[1]), p[0]))
entropy = -sum((c / gray.size) * np.log2(c / gray.size) for c in freq.values() if c > 0)
print(f"图像熵: {entropy:.2f} bits/pixel")
result = gray
cv2.imwrite('output.jpg', result)`,
    "erosion_dilation": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
ksize = 5  # 结构元大小
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (ksize, ksize))
# 腐蚀：消除边界像素，收缩前景区域
eroded = cv2.erode(binary, kernel, iterations=1)
# 膨胀：扩展边界像素，扩大前景区域
dilated = cv2.dilate(binary, kernel, iterations=1)
# 并排显示腐蚀(左)和膨胀(右)
result = np.hstack([eroded, dilated])
cv2.imwrite('output.jpg', result)`,
    "open_close": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
ksize = 5  # 结构元大小
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (ksize, ksize))
# 开运算 = 先腐蚀后膨胀：消除小噪点，平滑轮廓
opened = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
# 闭运算 = 先膨胀后腐蚀：填充小孔洞，连接断裂区域
closed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
result = np.hstack([opened, closed])
cv2.imwrite('output.jpg', result)`,
    "morph_gradient": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
ksize = 5  # 结构元大小
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (ksize, ksize))
# 形态学梯度 = 膨胀 - 腐蚀：提取物体边界
result = cv2.morphologyEx(binary, cv2.MORPH_GRADIENT, kernel)
cv2.imwrite('output.jpg', result)`,
    "tophat": `import cv2

img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
ksize = 9  # 结构元大小
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (ksize, ksize))
# 顶帽变换 = 原图 - 开运算：提取亮细节（比邻域亮的区域）
result = cv2.morphologyEx(gray, cv2.MORPH_TOPHAT, kernel)
cv2.imwrite('output.jpg', result)`,
    "blackhat": `import cv2

img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
ksize = 9  # 结构元大小
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (ksize, ksize))
# 黑帽变换 = 闭运算 - 原图：提取暗细节（比邻域暗的区域）
result = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, kernel)
cv2.imwrite('output.jpg', result)`,
    "skeletonize": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
# 骨架提取：迭代细化直到得到单像素宽骨架
skeleton = np.zeros(binary.shape, dtype=np.uint8)
element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
while True:
    eroded = cv2.erode(binary, element)
    temp = cv2.dilate(eroded, element)
    temp = cv2.subtract(binary, temp)
    skeleton = cv2.bitwise_or(skeleton, temp)
    binary = eroded.copy()
    if cv2.countNonZero(binary) == 0:
        break
result = cv2.bitwise_not(skeleton)
cv2.imwrite('output.jpg', result)`,
    "adaptive_threshold": `import cv2

img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
block_size = 11  # 邻域块大小（奇数）
c = 2            # 常数偏移
# 自适应阈值：根据局部邻域统计信息为每个像素计算独立阈值
result = cv2.adaptiveThreshold(gray, 255,
    cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_size, c)
cv2.imwrite('output.jpg', result)`,
    "kmeans_segment": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
k = 3  # 聚类数
# K-means聚类分割
pixels = img.reshape((-1, 3)).astype(np.float32)
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
_, labels, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
centers = centers.astype(np.uint8)
result = centers[labels.flatten()].reshape(img.shape)
cv2.imwrite('output.jpg', result)`,
    "mean_shift_segment": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
# Mean Shift分割：基于颜色空间密度的聚类
sp = 15   # 空间窗口半径
sr = 40   # 颜色窗口半径
result = cv2.pyrMeanShiftFiltering(img, sp, sr)
cv2.imwrite('output.jpg', result)`,
    "watershed": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# 分水岭算法
_, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
# 去噪
kernel = np.ones((3, 3), np.uint8)
opening = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=2)
# 确定背景区域
sure_bg = cv2.dilate(opening, kernel, iterations=3)
# 距离变换确定前景
dist = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
_, sure_fg = cv2.threshold(dist, 0.3 * dist.max(), 255, 0)
sure_fg = sure_fg.astype(np.uint8)
# 未知区域
unknown = cv2.subtract(sure_bg, sure_fg)
# 标记
_, markers = cv2.connectedComponents(sure_fg)
markers = markers + 1
markers[unknown == 255] = 0
# 应用分水岭
markers = cv2.watershed(img, markers)
# 在原始图像上绘制边界
result = img.copy()
result[markers == -1] = [0, 0, 255]
cv2.imwrite('output.jpg', result)`,
    "grabcut": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
# GrabCut分割
mask = np.zeros(img.shape[:2], np.uint8)
bgd_model = np.zeros((1, 65), np.float64)
fgd_model = np.zeros((1, 65), np.float64)
# 初始矩形（图像中央80%区域作为前景猜测）
h, w = img.shape[:2]
rect = (w//10, h//10, w*8//10, h*8//10)
cv2.grabCut(img, mask, rect, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_RECT)
# 提取前景
mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype(np.uint8)
result = img * mask2[:, :, np.newaxis]
cv2.imwrite('output.jpg', result)`,
    "contour_extract": `import cv2

img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
# 轮廓提取：在原始图像上绘制所有轮廓
contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
result = img.copy()
cv2.drawContours(result, contours, -1, (0, 255, 0), 2)
cv2.imwrite('output.jpg', result)`,
    "convex_hull": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
result = img.copy()
for cnt in contours:
    # 凸包检测：计算包围轮廓的最小凸多边形
    hull = cv2.convexHull(cnt)
    cv2.drawContours(result, [hull], -1, (0, 0, 255), 2)
    cv2.drawContours(result, [cnt], -1, (0, 255, 0), 1)
cv2.imwrite('output.jpg', result)`,
    "min_enclosing": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
result = img.copy()
for cnt in contours:
    if len(cnt) < 5: continue
    # 最小外接矩形
    rect = cv2.minAreaRect(cnt)
    box = cv2.boxPoints(rect).astype(np.int32)
    cv2.drawContours(result, [box], -1, (255, 0, 0), 2)
cv2.imwrite('output.jpg', result)`,
    "contour_approx": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
result = img.copy()
for cnt in contours:
    epsilon = 0.02 * cv2.arcLength(cnt, True)  # 近似精度
    approx = cv2.approxPolyDP(cnt, epsilon, True)
    cv2.drawContours(result, [approx], -1, (0, 255, 255), 2)
    # 标注顶点数
    x, y = approx[0][0]
    cv2.putText(result, str(len(approx)), (x, y-10),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
cv2.imwrite('output.jpg', result)`,
    "hu_moments": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
result = img.copy()
for i, cnt in enumerate(contours):
    # Hu矩：7个旋转、缩放、平移不变矩
    moments = cv2.moments(cnt)
    hu = cv2.HuMoments(moments)
    # 对数归一化
    hu_log = -np.sign(hu) * np.log10(np.abs(hu) + 1e-10)
    x, y, w, h_rect = cv2.boundingRect(cnt)
    cv2.rectangle(result, (x, y), (x+w, y+h_rect), (0, 255, 0), 2)
    cv2.putText(result, f'Hu[{i}]: {hu_log[0,0]:.2f}', (x, y-5),
        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
cv2.imwrite('output.jpg', result)`,
    "shape_match": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
result = img.copy()
if len(contours) >= 2:
    # 形状匹配：使用Hu矩比较两个轮廓的相似度
    score = cv2.matchShapes(contours[0], contours[1], cv2.CONTOURS_MATCH_I2, 0)
    cv2.drawContours(result, contours[:2], -1, (0, 255, 0), 2)
    cv2.putText(result, f'Similarity: {score:.4f}', (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
cv2.imwrite('output.jpg', result)`,
    "fourier_descriptor": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
result = img.copy()
for cnt in contours:
    # 傅里叶描述子：将轮廓坐标视为复数序列做DFT
    cnt_complex = cnt[:, 0, 0] + 1j * cnt[:, 0, 1]
    descriptors = np.fft.fft(cnt_complex)
    # 保留前16个描述子（低频部分）重构轮廓
    num_descriptors = 16
    descriptors[num_descriptors:] = 0
    reconstructed = np.fft.ifft(descriptors)
    pts = np.stack([reconstructed.real, reconstructed.imag], axis=1).astype(np.int32)
    cv2.drawContours(result, [pts.reshape(-1, 1, 2)], -1, (0, 255, 0), 2)
cv2.imwrite('output.jpg', result)`,
    "sampling_demo": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
sample_factor = 4  # 采样间隔（每sample_factor个像素取一个）
# 采样过程演示：每隔固定间隔取像素
h, w = img.shape[:2]
sampled = np.zeros_like(img)
sampled[::sample_factor, ::sample_factor] = img[::sample_factor, ::sample_factor]
# 用空像素的邻域填充使其可见
kernel = np.ones((sample_factor, sample_factor), np.uint8)
result = cv2.resize(sampled, (w // sample_factor, h // sample_factor),
    interpolation=cv2.INTER_NEAREST)
result = cv2.resize(result, (w, h), interpolation=cv2.INTER_NEAREST)
cv2.imwrite('output.jpg', result)`,
    "quantization_demo": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
levels = 4  # 量化级别（2^levels个灰度级）
# 量化过程演示：将256级灰度压缩到更少级别
factor = 256 // (2**levels)
result = (gray // factor) * factor + factor // 2
result = result.astype(np.uint8)
cv2.imwrite('output.jpg', result)`,
    "resolution_compare": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
# 空间分辨率对比：将图像缩小再放大
h, w = img.shape[:2]
scale = 0.25  # 缩放因子
small = cv2.resize(img, (int(w * scale), int(h * scale)),
    interpolation=cv2.INTER_NEAREST)
# 放大回原尺寸对比
result = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
cv2.imwrite('output.jpg', result)`,
    "pixel_neighbors": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# 像素邻域可视化：对每个像素显示其4邻域和8邻域
result = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
step = 20  # 采样步长
h, w = gray.shape
for y in range(step//2, h, step):
    for x in range(step//2, w, step):
        cv2.circle(result, (x, y), 2, (0, 0, 255), -1)  # 中心像素
        # 4邻域 (N4)
        for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ny, nx = y + dy*step, x + dx*step
            if 0 <= ny < h and 0 <= nx < w:
                cv2.line(result, (x, y), (nx, ny), (0, 255, 0), 1)
cv2.imwrite('output.jpg', result)`,
    "distance_metrics": `import cv2
import numpy as np

# 距离度量演示：D4(城市街区)、D8(棋盘)、欧氏距离
size = 200
result = np.zeros((size, size, 3), dtype=np.uint8)
cx, cy = size // 2, size // 2
for y in range(size):
    for x in range(size):
        d4 = abs(x - cx) + abs(y - cy)         # 城市街区距离
        d8 = max(abs(x - cx), abs(y - cy))      # 棋盘距离
        de = np.sqrt((x-cx)**2 + (y-cy)**2)     # 欧氏距离
        # 等距离轮廓可视化
        if abs(d4 - 50) < 1: result[y, x] = (255, 0, 0)
        if abs(d8 - 50) < 1: result[y, x] = (0, 255, 0)
        if abs(de - 50) < 1: result[y, x] = (0, 0, 255)
cv2.circle(result, (cx, cy), 3, (255, 255, 255), -1)
cv2.imwrite('output.jpg', result)`,
    "interpolation_demo": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
h, w = img.shape[:2]
scale = 4.0  # 放大倍数
# 插值对比：最邻近(上) vs 双线性(下)
nearest = cv2.resize(img, (int(w*scale), int(h*scale)),
    interpolation=cv2.INTER_NEAREST)
bilinear = cv2.resize(img, (int(w*scale), int(h*scale)),
    interpolation=cv2.INTER_LINEAR)
result = np.vstack([nearest, bilinear])
cv2.imwrite('output.jpg', result)`,
    "template_matching": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# 模板匹配：使用图像中央区域作为模板
h, w = gray.shape
th, tw = h // 4, w // 4
template = gray[h//2-th//2:h//2+th//2, w//2-tw//2:w//2+tw//2]
# 归一化相关系数匹配
result_match = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
_, max_val, _, max_loc = cv2.minMaxLoc(result_match)
# 绘制匹配框
result = img.copy()
cv2.rectangle(result, max_loc, (max_loc[0]+tw, max_loc[1]+th), (0, 255, 0), 2)
cv2.imwrite('output.jpg', result)`,
    "hough_lines": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
edges = cv2.Canny(gray, 50, 150)
# 霍夫线检测
lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=150)
result = img.copy()
if lines is not None:
    for line in lines[:20]:  # 最多显示20条线
        rho, theta = line[0]
        a, b = np.cos(theta), np.sin(theta)
        x0, y0 = a * rho, b * rho
        pt1 = (int(x0 + 1000*(-b)), int(y0 + 1000*(a)))
        pt2 = (int(x0 - 1000*(-b)), int(y0 - 1000*(a)))
        cv2.line(result, pt1, pt2, (0, 255, 0), 2)
cv2.imwrite('output.jpg', result)`,
    "hough_circles": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
gray = cv2.medianBlur(gray, 5)
# 霍夫圆检测
circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=1, minDist=30,
    param1=50, param2=30, minRadius=10, maxRadius=100)
result = img.copy()
if circles is not None:
    circles = np.uint16(np.around(circles))
    for circle in circles[0]:
        cv2.circle(result, (circle[0], circle[1]), circle[2], (0, 255, 0), 2)
cv2.imwrite('output.jpg', result)`,
    "hog_features": `import cv2
import numpy as np

img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# HOG特征提取
win_size = (64, 128)
block_size = (16, 16)
block_stride = (8, 8)
cell_size = (8, 8)
nbins = 9
hog = cv2.HOGDescriptor(win_size, block_size, block_stride, cell_size, nbins)
# 缩放图像到窗口大小
resized = cv2.resize(gray, win_size)
hog_features = hog.compute(resized)
# 可视化HOG特征方向
result = cv2.cvtColor(resized, cv2.COLOR_GRAY2BGR)
cell_gradient = np.zeros((win_size[1]//cell_size[1], win_size[0]//cell_size[0], nbins))
# 简化可视化：绘制梯度方向线
for y in range(0, win_size[1], cell_size[1]):
    for x in range(0, win_size[0], cell_size[0]):
        gx = cv2.Sobel(resized[y:y+cell_size[1], x:x+cell_size[0]], cv2.CV_32F, 1, 0)
        gy = cv2.Sobel(resized[y:y+cell_size[1], x:x+cell_size[0]], cv2.CV_32F, 0, 1)
        mag, ang = cv2.cartToPolar(gx, gy)
        cx, cy = x + cell_size[0]//2, y + cell_size[1]//2
        dx = int(np.mean(mag) * np.cos(np.mean(ang)) * 0.3)
        dy = int(np.mean(mag) * np.sin(np.mean(ang)) * 0.3)
        cv2.arrowedLine(result, (cx-dx, cy-dy), (cx+dx, cy+dy), (0, 255, 0), 1)
cv2.imwrite('output.jpg', result)`,
    // ── 综合工程案例完整流水线代码 ──
    "case_01_satellite": `import cv2
import numpy as np

# ═══ 综合工程案例：遥感图像采样分析 ═══
# 完整流水线：原始 → 降采样 → 量化退化 → 对比展示
img = cv2.imread('input.jpg')
h, w = img.shape[:2]

# 步骤1：降采样（空间分辨率降低）
small = cv2.resize(img, (w // 4, h // 4), interpolation=cv2.INTER_AREA)
up_small = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)

# 步骤2：低比特量化（灰度分辨率降低）
def quantize(image, levels):
    step = 256 // levels
    return (image // step) * step

quant_2 = quantize(img, 2)
quant_4 = quantize(img, 4)

# 步骤3：拼接对比图（原图 | 降采样 | 2bit | 4bit）
top = np.hstack([img, up_small])
bottom = np.hstack([quant_2, quant_4])
result = np.vstack([top, bottom])
cv2.imwrite('output.jpg', result)`,
    "case_02_document": `import cv2
import numpy as np

# ═══ 综合工程案例：文档几何校正 ═══
# 完整流水线：透视校正 → 最近邻 vs 双三次插值对比
img = cv2.imread('input.jpg')
h, w = img.shape[:2]

# 步骤1：透视变换校正（假设文档四角坐标）
src = np.float32([[0, 0], [w-1, 0], [0, h-1], [w-1, h-1]])
dst = np.float32([[50, 20], [w-50, 20], [20, h-20], [w-20, h-20]])
M = cv2.getPerspectiveTransform(src, dst)
corrected = cv2.warpPerspective(img, M, (w, h), flags=cv2.INTER_NEAREST)

# 步骤2：双三次插值高质量校正
corrected_bicubic = cv2.warpPerspective(img, M, (w, h), flags=cv2.INTER_CUBIC)

# 步骤3：对比展示
result = np.hstack([corrected, corrected_bicubic])
cv2.imwrite('output.jpg', result)`,
    "case_03_defect": `import cv2
import numpy as np

# ═══ 综合工程案例：零件缺陷检测 ═══
# 完整流水线：中值滤波 → Sobel边缘 → 热力图叠加
img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# 步骤1：中值滤波去噪
denoised = cv2.medianBlur(gray, 5)

# 步骤2：Sobel边缘检测
gx = cv2.Sobel(denoised, cv2.CV_64F, 1, 0, ksize=3)
gy = cv2.Sobel(denoised, cv2.CV_64F, 0, 1, ksize=3)
edges = np.uint8(np.clip(np.sqrt(gx**2 + gy**2), 0, 255))

# 步骤3：热力图叠加
heatmap = cv2.applyColorMap(edges, cv2.COLORMAP_JET)
result = cv2.addWeighted(img, 0.6, heatmap, 0.4, 0)
cv2.imwrite('output.jpg', result)`,
    "case_04_ct_denoise": `import cv2
import numpy as np

# ═══ 综合工程案例：CT图像去噪 ═══
# 完整流水线：DFT → 高斯低通滤波 → IDFT → 对比
img = cv2.imread('input.jpg', 0)
h, w = img.shape

# 步骤1：DFT变换到频域
dft = np.fft.fft2(img.astype(np.float32))
dft_shift = np.fft.fftshift(dft)

# 步骤2：高斯低通滤波器（D0=30）
y, x = np.mgrid[-h//2:h//2, -w//2:w//2]
D0 = 30
H = np.exp(-(x**2 + y**2) / (2 * D0**2))
filtered = dft_shift * H

# 步骤3：IDFT回到空间域
idft = np.fft.ifftshift(filtered)
result = np.uint8(np.clip(np.real(np.fft.ifft2(idft)), 0, 255))
cv2.imwrite('output.jpg', result)`,
    "case_05_photo_restore": `import cv2
import numpy as np

# ═══ 综合工程案例：老照片复原 ═══
# 完整流水线：NLM去噪 → USM锐化 → CLAHE增强
img = cv2.imread('input.jpg')

# 步骤1：非局部均值去噪
denoised = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)

# 步骤2：USM锐化
blur = cv2.GaussianBlur(denoised, (0, 0), 3)
sharpened = cv2.addWeighted(denoised, 1.5, blur, -0.5, 0)

# 步骤3：CLAHE对比度增强
lab = cv2.cvtColor(sharpened, cv2.COLOR_BGR2LAB)
l, a, b = cv2.split(lab)
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
l = clahe.apply(l)
result = cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)
cv2.imwrite('output.jpg', result)`,
    "case_06_drone_veg": `import cv2
import numpy as np

# ═══ 综合工程案例：航拍植被增强 ═══
# 完整流水线：HSV饱和度增强 → LAB-CLAHE亮度均衡
img = cv2.imread('input.jpg')

# 步骤1：HSV空间增强饱和度
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
hsv[:, :, 1] = cv2.multiply(hsv[:, :, 1], 1.4)
hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 255)
boosted = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

# 步骤2：LAB空间CLAHE均衡亮度
lab = cv2.cvtColor(boosted, cv2.COLOR_BGR2LAB)
l, a, b = cv2.split(lab)
clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
l = clahe.apply(l)
result = cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)
cv2.imwrite('output.jpg', result)`,
    "case_07_panorama": `import cv2
import numpy as np

# ═══ 综合工程案例：多分辨率融合 ═══
# 完整流水线：高斯金字塔 → 拉普拉斯金字塔 → 融合
imgA = cv2.imread('input.jpg')
imgB = cv2.resize(imgA, imgA.shape[:2][::-1])

# 步骤1：构建高斯金字塔
def build_gaussian(img, levels=4):
    gp = [img]
    for _ in range(levels - 1):
        gp.append(cv2.pyrDown(gp[-1]))
    return gp

# 步骤2：构建拉普拉斯金字塔
def build_laplacian(gp):
    lp = [gp[-1]]
    for i in range(len(gp) - 1, 0, -1):
        up = cv2.pyrUp(gp[i], dstsize=gp[i-1].shape[:2][::-1])
        lp.append(cv2.subtract(gp[i-1], up))
    return lp[::-1]

gpA = build_gaussian(imgA)
gpB = build_gaussian(imgB)
lpA = build_laplacian(gpA)
lpB = build_laplacian(gpB)

# 步骤3：融合（左半A，右半B）
ls = []
for la, lb in zip(lpA, lpB):
    rows, cols = la.shape[:2]
    blend = np.hstack([la[:, :cols//2], lb[:, cols//2:]])
    ls.append(blend)

# 重建
result = ls[0]
for i in range(1, len(ls)):
    result = cv2.add(cv2.pyrUp(result, dstsize=ls[i].shape[:2][::-1]), ls[i])
cv2.imwrite('output.jpg', result)`,
    "case_08_jpeg_opt": `import cv2
import numpy as np

# ═══ 综合工程案例：JPEG压缩优化 ═══
# 完整流水线：DCT分块 → 量化 → 反量化 → 重建 → PSNR评估
img = cv2.imread('input.jpg', 0).astype(np.float32)
h, w = img.shape
Q = 50  # 质量参数

# 步骤1：8x8分块DCT + 量化
qtable = np.array([[16,11,10,16,24,40,51,61],
                   [12,12,14,19,26,58,60,55],
                   [14,13,16,24,40,57,69,56],
                   [14,17,22,29,51,87,80,62],
                   [18,22,37,56,68,109,103,77],
                   [24,35,55,64,81,104,113,92],
                   [49,64,78,87,103,121,120,101],
                   [72,92,95,98,112,100,103,99]]) * (100 // Q)
result = np.zeros_like(img)
for y in range(0, h, 8):
    for x in range(0, w, 8):
        block = img[y:y+8, x:x+8] - 128
        dct = cv2.dct(block)
        quant = np.round(dct / qtable) * qtable
        result[y:y+8, x:x+8] = cv2.idct(quant) + 128

result = np.uint8(np.clip(result, 0, 255))
# PSNR评估
mse = np.mean((img - result) ** 2)
psnr = 10 * np.log10(255**2 / mse)
print(f'PSNR = {psnr:.2f} dB')
cv2.imwrite('output.jpg', result)`,
    "case_09_pcb_inspect": `import cv2
import numpy as np

# ═══ 综合工程案例：PCB缺陷检测 ═══
# 完整流水线：灰度 → Otsu二值化 → 开运算 → 形态学梯度
img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# 步骤1：Otsu自动阈值二值化
_, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

# 步骤2：开运算去除噪点
kernel = np.ones((5, 5), np.uint8)
opened = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

# 步骤3：形态学梯度突出缺陷边界
gradient = cv2.morphologyEx(opened, cv2.MORPH_GRADIENT, kernel)
result = cv2.cvtColor(gradient, cv2.COLOR_GRAY2BGR)
cv2.imwrite('output.jpg', result)`,
    "case_10_water_extract": `import cv2
import numpy as np

# ═══ 综合工程案例：遥感水体提取 ═══
# 完整流水线：灰度 → Otsu二值化 → 闭运算填充 → 开运算去噪
img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# 步骤1：Otsu自动阈值
_, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

# 步骤2：闭运算填充水体内部空洞
kernel_close = np.ones((5, 5), np.uint8)
closed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel_close)

# 步骤3：开运算去除孤立噪点
kernel_open = np.ones((3, 3), np.uint8)
result_gray = cv2.morphologyEx(closed, cv2.MORPH_OPEN, kernel_open)
result = cv2.cvtColor(result_gray, cv2.COLOR_GRAY2BGR)
cv2.imwrite('output.jpg', result)`,
    "case_11_part_classify": `import cv2
import numpy as np

# ═══ 综合工程案例：零件分类识别 ═══
# 完整流水线：灰度 → Otsu二值化 → 轮廓提取 → Hu矩 + 几何特征
img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# 步骤1：Otsu二值化
_, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

# 步骤2：轮廓提取
contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
result = img.copy()

# 步骤3：特征计算与分类
for cnt in contours:
    area = cv2.contourArea(cnt)
    if area < 500: continue
    # Hu矩（平移/旋转/缩放不变）
    moments = cv2.HuMoments(cv2.moments(cnt)).flatten()
    # 几何特征
    perimeter = cv2.arcLength(cnt, True)
    circularity = 4 * np.pi * area / (perimeter ** 2) if perimeter > 0 else 0
    approx = cv2.approxPolyDP(cnt, 0.02 * perimeter, True)
    vertices = len(approx)
    # 分类判断
    if circularity > 0.8:
        label = '圆形件'
    elif vertices <= 4:
        label = '多边形件'
    else:
        label = '复杂形状件'
    cv2.drawContours(result, [cnt], -1, (0, 255, 0), 2)
    M = cv2.moments(cnt)
    cx, cy = int(M['m10']/M['m00']), int(M['m01']/M['m00'])
    cv2.putText(result, label, (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
cv2.imwrite('output.jpg', result)`,
    "case_12_traffic_sign": `import cv2
import numpy as np

# ═══ 综合工程案例：交通标志检测 ═══
# 完整流水线：灰度 → Canny边缘 → 霍夫圆 + Harris角点 → 标注
img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# 步骤1：Canny边缘检测
edges = cv2.Canny(gray, 50, 150)

# 步骤2：霍夫圆检测
circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=1, minDist=30,
                           param1=50, param2=30, minRadius=10, maxRadius=100)
result = img.copy()
if circles is not None:
    circles = np.uint16(np.around(circles))
    for c in circles[0, :]:
        cv2.circle(result, (c[0], c[1]), c[2], (0, 255, 0), 2)
        cv2.circle(result, (c[0], c[1]), 2, (0, 0, 255), 3)

# 步骤3：Harris角点辅助定位
corners = cv2.cornerHarris(gray, blockSize=2, ksize=3, k=0.04)
corners = cv2.dilate(corners, None)
result[corners > 0.01 * corners.max()] = [0, 0, 255]
cv2.imwrite('output.jpg', result)`,
};

// ===== 根据 operation ID 生成通用代码模板 =====
function getDefaultCode(opId) {
    return `import cv2
import numpy as np

# 读取图像
img = cv2.imread('input.jpg')

# TODO: 实现「${opId}」算法

cv2.imwrite('output.jpg', result)`;
}

function resetCodePanel() {
    document.getElementById('codeContent').textContent =
        '选择操作后显示对应的 Python 代码\n（含完整 import 和核心逻辑）';
}

function updateCodePanel(opId) {
    var codeEl = document.getElementById('codeContent');
    var code = OP_CODE[opId] || getDefaultCode(opId);
    codeEl.textContent = code;
}

function clearResultArea() {
    document.getElementById('resultImageArea').innerHTML =
        '<p class="result-placeholder">处理完成后，结果图像将显示在此处。</p>';
    document.getElementById('resultActions').style.display = 'none';
    resultImageBase64 = null;
}

function copyCode() {
    var codeEl = document.getElementById('codeContent');
    var btn = document.getElementById('copyCodeBtn');
    navigator.clipboard.writeText(codeEl.textContent).then(function() {
        btn.textContent = '已复制!';
        btn.classList.add('copied');
        setTimeout(function() {
            btn.textContent = '复制代码';
            btn.classList.remove('copied');
        }, 2000);
    }).catch(function() {
        // 降级方案
        var textarea = document.createElement('textarea');
        textarea.value = codeEl.textContent;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        btn.textContent = '已复制!';
        btn.classList.add('copied');
        setTimeout(function() {
            btn.textContent = '复制代码';
            btn.classList.remove('copied');
        }, 2000);
    });
}

/* ================================================================
   操作埋点（上传到服务器 operation_logs / ai_analysis_logs 表）
   作者：李康乐
   ================================================================ */
function logOperation(chapterId, operationId, operationName, params, imageFilename, resultType, errorMsg, durationMs) {
    try {
        fetch('/auth/api/log/operation', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                chapter_id: chapterId,
                operation_id: operationId,
                operation_name: operationName,
                params: params,
                image_filename: imageFilename,
                result_type: resultType,
                error_msg: errorMsg || null,
                duration_ms: durationMs
            })
        });
    } catch (e) {}
}

function logAIAnalysis(operationLogId, analysisContent) {
    try {
        fetch('/auth/api/log/ai_analysis', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                operation_log_id: operationLogId,
                analysis_content: analysisContent
            })
        });
    } catch (e) {}
}

