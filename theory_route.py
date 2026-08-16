
"""理论路由模块 —— 为每个操作提供结构化理论内容"""
import json
from flask import jsonify

# 从主模块获取 OPERATION_NAMES 和 THEORY_LIBRARY
OPERATION_NAMES = {}
THEORY_LIBRARY = {}

def init_theory_routes(app, op_names, theory_lib):
    global OPERATION_NAMES, THEORY_LIBRARY
    OPERATION_NAMES = op_names
    THEORY_LIBRARY = theory_lib

    # 将 PARAM_DESCRIPTIONS 注册到 app 中
    app.config['PARAM_DESCRIPTIONS'] = PARAM_DESCRIPTIONS
    app.config['FORMULAS_LIBRARY'] = FORMULAS_LIBRARY
    app.config['STEPS_LIBRARY'] = STEPS_LIBRARY

    @app.route('/theory/<operation_id>')
    def get_theory(operation_id):
        """返回操作的理论内容（概念定义、数学公式、算法步骤、关键参数说明）"""
        if operation_id not in OPERATION_NAMES:
            return jsonify({'status': 'error', 'message': f'不支持的操作: {operation_id}'}), 404

        name = OPERATION_NAMES[operation_id]
        theory_text = THEORY_LIBRARY.get(operation_id, '')
        formulas = FORMULAS_LIBRARY.get(operation_id, [])
        steps = STEPS_LIBRARY.get(operation_id, [])
        params = PARAM_DESCRIPTIONS.get(operation_id, [])

        # 根据操作ID推断章节
        chapter_map = {
            1: ['sampling_demo','quantization_demo','resolution_compare','pixel_neighbors','distance_metrics','interpolation_demo'],
            3: ['image_inversion','log_transform','contrast_stretch','histogram_equalization','clahe','gamma_correction','median_blur','gaussian_blur','bilateral_filter','laplacian','unsharp_mask','sobel_sharpen'],
            4: ['ideal_lowpass','ideal_highpass','butterworth_lowpass','butterworth_highpass','gaussian_lowpass','gaussian_highpass','bandpass_filter'],
            5: ['gaussian_noise','sp_noise','mean_filter_restore','median_restore','nlm_denoise','wiener_filter','sobel','canny'],
            6: ['rgb_split','rgb_to_hsv','hue_adjust','saturation_adjust','brightness_adjust','color_balance','pseudo_color','color_hist_eq'],
            7: ['gaussian_pyramid','laplacian_pyramid','pyramid_blend','dwt_denoise','dwt_edge_enhance'],
            8: ['dct_visualize','jpeg_simulate','jpeg_compare','binary_rle','binary_huffman'],
            9: ['erosion_dilation','open_close','morph_gradient','tophat','blackhat','skeletonize'],
            10: ['otsu_threshold','adaptive_threshold','kmeans_segment','mean_shift_segment','watershed','grabcut','region_growing'],
            11: ['contour_extract','convex_hull','min_enclosing','contour_approx','hu_moments','shape_match','fourier_descriptor'],
            12: ['template_matching','hough_lines','hough_circles','corner_harris','sift_features','hog_features','prewitt','roberts'],
        }
        chapter = 1
        for ch, ops in chapter_map.items():
            if operation_id in ops:
                chapter = ch
                break

        # 章节名
        chapter_names = {
            1: '第一章：绪论 / 第二章：数字图像基础',
            3: '第三章：灰度变换与空间滤波',
            4: '第四章：频率域滤波',
            5: '第五章：图像复原与重建',
            6: '第六章：彩色图像处理',
            7: '第七章：小波变换与多分辨率处理',
            8: '第八章：图像压缩',
            9: '第九章：形态学图像处理',
            10: '第十章：图像分割',
            11: '第十一章：表示和描述',
            12: '第十二章：目标检测与识别',
        }

        return jsonify({
            'status': 'success',
            'data': {
                'name': name,
                'operation_id': operation_id,
                'chapter': chapter,
                'chapter_name': chapter_names.get(chapter, f'第{chapter}章'),
                'sections': [
                    {
                        'title': '概念定义',
                        'content': theory_text if theory_text else _fallback_theory(name),
                        'icon': 'book',
                    },
                    {
                        'title': '数学公式',
                        'content': '\n'.join(formulas) if formulas else '（暂无专项公式，可参考概念定义中的数学描述）',
                        'icon': 'formula',
                    },
                    {
                        'title': '算法步骤',
                        'content': '\n'.join(steps) if steps else '（暂无分步算法描述，可参考概念定义中的流程说明）',
                        'icon': 'steps',
                    },
                    {
                        'title': '关键参数说明',
                        'content': _format_params(params) if params else '（该操作无需额外参数调整）',
                        'icon': 'params',
                    },
                ],
            }
        })

def _fallback_theory(name):
    return f'「{name}」的核心原理可参考冈萨雷斯《数字图像处理》第四版相关章节。图像处理效果的评价应综合考虑主观视觉质量和客观量化指标，两者不可偏废。参数的选择往往需要在多种约束之间权衡（如去噪强度与细节保留、增强幅度与噪声放大）。'

def _format_params(params):
    lines = []
    for p in params:
        lines.append(f'• {p.get("key", "")}：{p.get("desc", "")}')
    return '\n'.join(lines)


# ══════════════════════ 数学公式库 ══════════════════════

FORMULAS_LIBRARY = {
    # Ch1/2
    'sampling_demo': [
        '奈奎斯特频率: f_s ≥ 2·f_max',
        '采样后: f[i,j] = f_c(i·Δx, j·Δy)',
        '空间分辨率: R = 1/Δx × 1/Δy (PPI/DPI)',
    ],
    'quantization_demo': [
        '灰度级数: L = 2^b',
        '量化步长: Δ = 256/L',
        '量化后: q = ⌊r/Δ⌋ × Δ + Δ/2',
        '量化噪声功率: σ²_q = Δ²/12',
    ],
    'resolution_compare': [
        '最近邻: I(x,y) = I_src(⌊x/s⌋, ⌊y/s⌋)',
        '双线性: I(x,y) = Σ_{i=0}¹ Σ_{j=0}¹ w_i·w_j·I_src(x₀+i, y₀+j)',
        '双三次: I(x,y) = Σ_{i=-1}² Σ_{j=-1}² f_{i,j}·W(i-a)·W(j-b)',
    ],
    'pixel_neighbors': [
        '4-邻域: N₄(p) = {(x+1,y),(x-1,y),(x,y+1),(x,y-1)}',
        '对角邻域: N_D(p) = {(x+1,y+1),(x+1,y-1),(x-1,y+1),(x-1,y-1)}',
        '8-邻域: N₈(p) = N₄(p) ∪ N_D(p)',
    ],
    'distance_metrics': [
        '欧几里得: D_e(p,q) = √[(x₁-x₂)² + (y₁-y₂)²]',
        'D₄城市街区: D₄(p,q) = |x₁-x₂| + |y₁-y₂|',
        'D₈棋盘: D₈(p,q) = max(|x₁-x₂|, |y₁-y₂|)',
    ],
    'interpolation_demo': [
        '最近邻: f(x,y) = f(⌊x+0.5⌋, ⌊y+0.5⌋)',
        '双线性: f(x,y) = (1-a)(1-b)f₀₀ + a(1-b)f₁₀ + (1-a)bf₀₁ + abf₁₁',
        '双三次: W(t) = (a+2)|t|³ - (a+3)|t|² + 1 (|t|≤1), W(t) = a|t|³ - 5a|t|² + 8a|t| - 4a (1<|t|≤2)',
    ],
    # Ch3
    'image_inversion': [
        's = L - 1 - r，其中 L=256',
        '直方图关系: h_out(k) = h_in(L-1-k)',
        '平均亮度: μ_out = (L-1) - μ_in（标准差σ不变）',
    ],
    'log_transform': [
        's = c · log(1 + r)',
        '导数（增益）: ds/dr = c/(1+r)（递减函数）',
        '归一化: s = c · log(1 + r_norm · 255)',
    ],
    'contrast_stretch': [
        '线性: s = (r - r_min)/(r_max - r_min) × 255',
        '百分位: s = (r - p_low)/(p_high - p_low) × 255',
        '裁剪: s = clamp(s, 0, 255)',
    ],
    'histogram_equalization': [
        '变换函数: s_k = (L-1) · Σ_{j=0}^{k} p_r(r_j)，p_r(r_j) = n_j/N',
        'CDF: T(r_k) = (L-1) · P_r(r_k)',
        '均衡化后: p_s(s_k) ≈ 1/(L-1)（均匀分布）',
        '最大熵: H_max = log₂(L) = 8 bit（L=256）',
    ],
    'clahe': [
        '直方图裁剪: h_clipped(k) = min(h(k), clip_limit)',
        '重分配: excess = Σ max(h(k)-clip_limit, 0) → 均匀分配',
        '双线性插值: 在 tile 边界平滑过渡消除块效应',
    ],
    'gamma_correction': [
        's = 255 · (r/255)^γ',
        '导数: ds/dr = c·γ·r^{γ-1}',
        'γ<1: 暗区增益大（增亮暗部）；γ>1: 亮区增益大（压暗亮部）',
    ],
    'median_blur': [
        'g(x,y) = median{ f(s,t) | (s,t)∈S_xy }',
        '椒盐噪声下: 脉冲点(0/255)在排序中位于极值位置，中位数取自正常像素',
    ],
    'gaussian_blur': [
        'G(x,y) = 1/(2πσ²) · exp(-(x²+y²)/(2σ²))',
        '可分离: G(x,y) = G_x(x) · G_y(y)',
        '频域: F{G}(u,v) = exp(-2π²σ²(u²+v²))',
        '核半径: r = ⌈3σ⌉（覆盖 99.7% 权重）',
    ],
    'bilateral_filter': [
        'BF[I](p) = (1/W_p)·Σ G_{σ_s}(||p-q||)·G_{σ_r}(|I(p)-I(q)|)·I(q)',
        '空间权重: G_{σ_s}(d) = exp(-d²/(2σ_s²))',
        '值域权重: G_{σ_r}(d) = exp(-d²/(2σ_r²))',
        'W_p = Σ G_{σ_s}·G_{σ_r}（归一化因子）',
    ],
    'laplacian': [
        '∇²f = ∂²f/∂x² + ∂²f/∂y²',
        '四邻域核: [[0,1,0],[1,-4,1],[0,1,0]]',
        '八邻域核: [[1,1,1],[1,-8,1],[1,1,1]]',
        '锐化: g = f - c·∇²f',
    ],
    'unsharp_mask': [
        '高频: h = f - G_σ * f',
        '锐化: g = f + amount · h = (1+amount)·f - amount·(G_σ*f)',
    ],
    'sobel_sharpen': [
        'Gx = [[-1,0,1],[-2,0,2],[-1,0,1]] * I',
        'Gy = [[-1,-2,-1],[0,0,0],[1,2,1]] * I',
        '梯度幅值: G = √(Gx² + Gy²)',
    ],
    # Ch4
    'ideal_lowpass': [
        'H(u,v) = 1 (D≤D₀), 0 (D>D₀)',
        'D(u,v) = √[(u-M/2)²+(v-N/2)²]',
        'G(u,v) = F(u,v)·H(u,v) → g=IDFT{G}',
    ],
    'ideal_highpass': [
        'H(u,v) = 1 (D≥D₀), 0 (D<D₀)',
    ],
    'butterworth_lowpass': [
        'H(u,v) = 1/[1 + (D/D₀)^{2n}]，n=4',
    ],
    'butterworth_highpass': [
        'H(u,v) = 1/[1 + (D₀/D)^{2n}]，n=4',
    ],
    'gaussian_lowpass': [
        'H(u,v) = exp(-D²/(2D₀²))',
        'D=D₀时 H=exp(-1/2)≈0.607',
    ],
    'gaussian_highpass': [
        'H(u,v) = 1 - exp(-D²/(2D₀²))',
    ],
    'bandpass_filter': [
        'H_BP(u,v) = 1 (D_low≤D≤D_high), 0 (otherwise)',
    ],
    # Ch5
    'gaussian_noise': [
        'p(z) = 1/(√(2π)σ) · exp(-(z-μ)²/(2σ²))',
        'I_noisy = clamp(I + N, 0, 255), N~N(0,σ²)',
        'PSNR ≈ 20·log₁₀(255/σ)（经验公式）',
    ],
    'sp_noise': [
        'I_noisy(x,y) = { 0 (P/2), 255 (P/2), I(x,y) (1-P) }',
    ],
    'mean_filter_restore': [
        'g(x,y) = (1/(ksize²)) · Σ f(s,t)',
    ],
    'median_restore': [
        'g(x,y) = median{ f(s,t) | (s,t)∈S_xy }',
    ],
    'nlm_denoise': [
        'NLM[I](p) = (1/C(p))·Σ w(p,q)·I(q)',
        'w(p,q) = exp(-||N(p)-N(q)||²/h²)',
    ],
    'wiener_filter': [
        'g = μ + max(σ²-ν²,0)/max(σ²,ε)·(f-μ)',
        'μ = mean_local(f), σ² = var_local(f), ν² = mean(σ²)',
    ],
    'sobel': [
        'Gx = Sobel_X(f), Gy = Sobel_Y(f)',
        '梯度幅值: G = √(Gx² + Gy²)',
        '梯度方向: θ = arctan(Gy/Gx)',
    ],
    'canny': [
        'NMS: G_nms = G if G = max_{沿θ}(邻域) else 0',
        '双阈值: strong=G≥T_high, weak=T_low≤G<T_high',
        '滞后: weak 与 strong 8-连通 → 保留',
    ],
    # Ch6
    'rgb_to_hsv': [
        'V = max(R,G,B)',
        'S = (V-min)/V (V≠0)',
        'H = 60°×(G-B)/(V-min) if V=R; 120°+60°×(B-R)/(V-min) if V=G; 240°+60°×(R-G)/(V-min) if V=B',
    ],
    'hue_adjust': [
        'H_new = (H + shift) mod 180',
    ],
    'saturation_adjust': [
        'S_new = clamp(factor × S, 0, 255)',
    ],
    'brightness_adjust': [
        'I_new = clamp(I + β, 0, 255)',
    ],
    'color_balance': [
        'R_new = clamp(k_R·R, 0, 255)',
        'G_new = clamp(k_G·G, 0, 255)',
        'B_new = clamp(k_B·B, 0, 255)',
    ],
    # Ch7
    'gaussian_pyramid': [
        'G_0 = I（原图）',
        'G_l = Down(G_{l-1} * G_σ)',
        'scale_l = 2^l, 像素数 = N/4^l',
    ],
    'laplacian_pyramid': [
        'L_l = G_l - Up(G_{l+1})',
        '重建: G_l = L_l + Up(G_{l+1})',
    ],
    'pyramid_blend': [
        'L_F^l = W^l·L_A^l + (1-W^l)·L_B^l',
        '重建: G_F^l = L_F^l + Up(G_F^{l+1})',
    ],
    'dwt_denoise': [
        '硬阈值: w_new = w if |w|≥λ else 0',
        '软阈值: w_new = sign(w)·max(|w|-λ, 0)',
        'VisuShrink: λ = σ·√(2·ln N)',
    ],
    'dwt_edge_enhance': [
        'coeff_new = coeff × gain（中心区域）',
        'I_enhanced = IDCT(coeff_new)',
    ],
    # Ch8
    'dct_visualize': [
        'DCT-II: F(u,v) = α(u)α(v)ΣΣ f(x,y)·cos[πu(2x+1)/(2N)]·cos[πv(2y+1)/(2N)]',
        '可视化: D_vis = log(|F(u,v)|+1)，归一化显示',
    ],
    'jpeg_simulate': [
        'JPEG编码: Block(8×8)→DCT→Quantize(Q(quality))→Zigzag→RLE→Huffman',
        '量化: Q_DCT = round(DCT/Q_table(quality))',
    ],
    'jpeg_compare': [
        'PSNR = 10·log₁₀(255²/MSE)',
        'MSE = (1/MN)·Σ[I(x,y)-K(x,y)]²',
    ],
    'binary_rle': [
        'RLE编码: 序列 → [(run_len₁, val₁), (run_len₂, val₂), ...]',
        '压缩率: CR = N/(2×num_runs)',
    ],
    'binary_huffman': [
        '信息熵: H = -Σ p_i·log₂(p_i)',
        '平均码长: H ≤ L_avg < H+1',
        '压缩率: CR = 8/L_avg',
    ],
    # Ch9
    'erosion_dilation': [
        '腐蚀: A ⊖ B = {z | (B)_z ⊆ A}',
        '膨胀: A ⊕ B = {z | (B̂)_z ∩ A ≠ ∅}',
        '灰度腐蚀: (f⊖b)=min{f(x+s,y+t)-b(s,t)}',
        '灰度膨胀: (f⊕b)=max{f(x-s,y-t)+b(s,t)}',
    ],
    'open_close': [
        '开运算: A∘B = (A⊖B)⊕B',
        '闭运算: A•B = (A⊕B)⊖B',
        '幂等性: (A∘B)∘B = A∘B',
    ],
    'morph_gradient': [
        'G = (f⊕b) - (f⊖b)',
    ],
    'tophat': [
        'T_hat = f - (f∘b)',
    ],
    'blackhat': [
        'B_hat = (f•b) - f',
    ],
    # Ch10
    'otsu_threshold': [
        'σ²_B(T) = ω₀·ω₁·[μ₀-μ₁]²',
        'T* = argmax σ²_B(T), T∈[0,255]',
    ],
    'adaptive_threshold': [
        'T(x,y) = mean_{block}(x,y) - C',
        'I_binary = 255 if I>T else 0',
    ],
    'kmeans_segment': [
        '目标: J = Σ_{i=1}^{K} Σ_{x∈C_i} ||x - μ_i||²',
        'μ_i = (1/|C_i|)·Σ_{x∈C_i} x',
    ],
    'mean_shift_segment': [
        '漂移向量: m(x) = [Σ K(x_i-x)·x_i]/Σ K(x_i-x) - x',
    ],
    'watershed': [
        '距离变换: D(p) = min_{q∈BG} ||p-q||',
        '前景标记: D(p) > thresh·max(D)',
    ],
    'grabcut': [
        '能量: E(α,k,θ,z) = U(α,k,θ,z) + V(α,z)',
        'GMM似然: U = -log p(z|α,k,θ) - log π(α,k)',
        '平滑项: V ∝ exp(-β||z_m-z_n||²)',
    ],
    # Ch11
    'contour_extract': [
        '边界: β(R) = R - (R⊖B)',
        '面积: A = (1/2)·Σ (x_i·y_{i+1} - x_{i+1}·y_i)',
    ],
    'convex_hull': [
        '凸性比: Solidity = Area(Contour)/Area(Hull)',
    ],
    'min_enclosing': [
        '矩形度: Rect = Area_contour/Area_AABB',
    ],
    'contour_approx': [
        'DP: ε = epsilon_factor × 周长',
        '若 max_distance > ε → 保留该点并递归',
    ],
    'hu_moments': [
        '中心矩: μ_pq = ΣΣ (x-x̄)^p (y-ȳ)^q f(x,y)',
        '归一化: η_pq = μ_pq/μ₀₀^{(p+q)/2+1}',
        'Hu矩: φ₁~φ₇ 由2阶/3阶归一化中心矩组合',
    ],
    'shape_match': [
        'I1(A,B) = Σ |1/m_i^A - 1/m_i^B|',
        'I2(A,B) = Σ |m_i^A - m_i^B|',
    ],
    'fourier_descriptor': [
        '复坐标: z_k = x_k + j·y_k',
        'FD: Z(u) = (1/N)·Σ z_k·exp(-j2πuk/N)',
        '截断: Z_trunc(u)=Z(u) for |u|<num_d, else 0',
    ],
    # Ch12
    'template_matching': [
        '平方差: R(x,y) = Σ [I(x+i,y+j)-T(i,j)]²',
        '互相关: R(x,y) = Σ I(x+i,y+j)·T(i,j)',
        '相关系数: R(x,y) = Σ [I-μ_I]·[T-μ_T]',
    ],
    'hough_lines': [
        '极坐标: ρ = x·cosθ + y·sinθ',
        '投票: A(ρ,θ) += 1（每个边缘点）',
    ],
    'hough_circles': [
        '圆方程: (x-a)² + (y-b)² = r²',
        '梯度法: 沿梯度方向投票确定圆心',
    ],
    'corner_harris': [
        'M = Σ_w [[I_x², I_xI_y], [I_xI_y, I_y²]]',
        'R = det(M) - k·trace²(M)',
        'R>0且大→角点, R<0→边缘, |R|小→平坦',
    ],
    'sift_features': [
        'DoG: D(x,y,σ)=[G(kσ)-G(σ)]*I',
        '梯度幅值: m(x,y)=√[(L(x+1)-L(x-1))²+(L(y+1)-L(y-1))²]',
        '描述子: 4×4×8=128维归一化向量',
    ],
    'hog_features': [
        '梯度: Gx = [-1,0,1], Gy = [-1,0,1]ᵀ',
        '9 bins 方向直方图（0°~180°）',
        'Block归一化: L2-norm',
    ],
}

# ══════════════════════ 算法步骤库 ══════════════════════

STEPS_LIBRARY = {
    # Ch1/2
    'sampling_demo': [
        'Step 1: 确定目标采样率（相对于原始分辨率的比例 sample_rate）',
        'Step 2: 计算新尺寸: new_w=w×sample_rate, new_h=h×sample_rate',
        'Step 3: 最近邻插值降采样到目标尺寸',
        'Step 4: 放大回原始尺寸对比信息损失',
        'Step 5: 评估混叠程度和细节保留情况',
    ],
    'quantization_demo': [
        'Step 1: 读取原始灰度图像（256级）',
        'Step 2: 确定量化位深 b，计算灰度级数 L=2^b',
        'Step 3: 计算量化步长 Δ=256/L',
        'Step 4: 逐像素映射: q=round(r/Δ)·Δ+Δ/2',
        'Step 5: 观察伪轮廓效应随位深降低的加剧',
    ],
    'resolution_compare': [
        'Step 1: 将原图按 scale 比例缩小',
        'Step 2: 最近邻插值放大回较大尺寸',
        'Step 3: 双线性插值放大回较大尺寸',
        'Step 4: 双三次插值放大回较大尺寸',
        'Step 5: 四宫格对比三种方法的锯齿/模糊差异',
    ],
    'pixel_neighbors': [
        'Step 1: 在图像中心选定目标像素 p',
        'Step 2: 根据选择的邻域类型高亮对应邻域像素',
        'Step 3: 绘制连线标注连接关系',
        'Step 4: 展示对应的数学定义公式',
    ],
    'distance_metrics': [
        'Step 1: 生成 400×400 空白画布并叠加参考网格',
        'Step 2: 标记中心点为距离原点',
        'Step 3: 以 30 像素间隔绘制等距线',
        'Step 4: 欧几里得→同心圆, D₄→菱形, D₈→正方形',
    ],
    'interpolation_demo': [
        'Step 1: 将原图缩小到 1/4 尺寸',
        'Step 2: 最近邻插值放大回原尺寸',
        'Step 3: 双线性插值放大回原尺寸',
        'Step 4: 双三次插值放大回原尺寸',
        'Step 5: 三列对比原始图/缩小图/放大结果',
    ],
    # Ch3
    'histogram_equalization': [
        'Step 1: 转为灰度图，计算灰度直方图 hist(r)',
        'Step 2: 计算累积分布函数: cdf(k)=Σ_{j=0}^{k} hist(j)/N',
        'Step 3: 生成查找表: lut(k)=round(255·cdf(k))',
        'Step 4: 逐像素查表映射: s(x,y)=lut(r(x,y))',
    ],
    'clahe': [
        'Step 1: 转为灰度图并划分为 tile_size×tile_size 网格',
        'Step 2: 对每个 tile 计算直方图',
        'Step 3: 对比度限幅裁剪（clip_limit）',
        'Step 4: 各 tile 内均衡化',
        'Step 5: 双线性插值消除 tile 边界块效应',
    ],
    'gamma_correction': [
        'Step 1: 转为灰度图',
        'Step 2: 构建查找表: lut[i]=255·(i/255)^(1/γ)',
        'Step 3: 逐像素查表映射',
    ],
    'median_blur': [
        'Step 1: 对每个像素提取 ksize×ksize 邻域',
        'Step 2: 邻域内像素值排序',
        'Step 3: 取中位数替换中心像素',
    ],
    'gaussian_blur': [
        'Step 1: 确定核大小 ksize (≈6σ+1)',
        'Step 2: 生成 ksize×ksize 高斯核: G[i,j]=exp(-(i²+j²)/(2σ²))',
        'Step 3: 归一化核: G/=ΣG',
        'Step 4: 卷积（或利用可分离性分两次一维卷积加速）',
    ],
    'bilateral_filter': [
        'Step 1: 对每个像素 p，遍历 d×d 邻域',
        'Step 2: 空间权重: w_s=exp(-||p-q||²/(2σ_space²))',
        'Step 3: 值域权重: w_r=exp(-|I(p)-I(q)|²/(2σ_color²))',
        'Step 4: 合成权重: w=w_s·w_r',
        'Step 5: 加权求和: I_new(p)=Σ w·I(q)/Σ w',
    ],
    'laplacian': [
        'Step 1: 转为灰度图',
        'Step 2: 拉普拉斯核卷积: ∇²f=I*kernel',
        'Step 3: 取绝对值得到边缘强度: |∇²f|',
        'Step 4: 锐化: g=f-c·∇²f',
    ],
    'unsharp_mask': [
        'Step 1: 高斯模糊: f_blurred=GaussianBlur(f, σ=radius)',
        'Step 2: 提取高频: h=f-f_blurred',
        'Step 3: 叠加高频: g=f+amount·h',
        'Step 4: 裁剪到 [0,255]',
    ],
    # Ch4 (通用频域步骤)
    'ideal_lowpass': [
        'Step 1: 转为灰度图并缩放到偶数尺寸',
        'Step 2: DFT: F=FFT(f)',
        'Step 3: 频谱中心化: F_shift=fftshift(F)',
        'Step 4: 生成频域掩码: H(u,v)=1 if D≤D₀ else 0',
        'Step 5: 滤波: G=F_shift·H',
        'Step 6: 逆中心化→逆FFT: g=IFFT(ifftshift(G))',
        'Step 7: 取幅值并归一化到 [0,255]',
    ],
    # Ch5
    'canny': [
        'Step 1: 高斯滤波去噪（σ=1.4, 5×5核）',
        'Step 2: Sobel算子计算梯度幅值和方向',
        'Step 3: 非极大值抑制（NMS）→ 细化边缘为单像素宽',
        'Step 4: 双阈值检测 → 强/弱/非边缘三类',
        'Step 5: 滞后边缘跟踪 → 弱边缘仅在与强边缘连通时保留',
    ],
    'wiener_filter': [
        'Step 1: 转为灰度图',
        'Step 2: 计算局部均值: μ=blur(f, ksize)',
        'Step 3: 计算局部方差: σ²=blur((f-μ)², ksize)',
        'Step 4: 全局噪声方差估计: ν²=mean(σ²)',
        'Step 5: 自适应滤波: g=μ+max(σ²-ν²,0)/max(σ²,ε)·(f-μ)',
    ],
    # Ch7
    'gaussian_pyramid': [
        'Step 1: 以原图为底层 G₀',
        'Step 2: 高斯模糊（σ=1, 5×5核）',
        'Step 3: 降采样 1/2（仅保留偶数行列）',
        'Step 4: 重复直到目标层数',
        'Step 5: 拼接展示（底部对齐）',
    ],
    'laplacian_pyramid': [
        'Step 1: 构建高斯金字塔 G₀~G_L',
        'Step 2: 每对相邻层: G_{l+1} 上采样到 G_l 尺寸',
        'Step 3: L_l=G_l-Up(G_{l+1})',
        'Step 4: 残差图增强显示（放大+平移）',
    ],
    'pyramid_blend': [
        'Step 1: 图像沿中线分为左右两半 A 和 B',
        'Step 2: 分别构建 A 和 B 的高斯金字塔',
        'Step 3: 构建拉普拉斯金字塔',
        'Step 4: 构建权重金字塔（渐变蒙版）',
        'Step 5: 逐层加权融合→从顶层重建',
    ],
    # Ch8
    'dct_visualize': [
        'Step 1: 转为灰度图并调整到偶数尺寸',
        'Step 2: 执行二维 DCT 变换',
        'Step 3: 对系数取对数: D_log=log(|DCT|+1)',
        'Step 4: 归一化到 [0,255] 并可视化',
        'Step 5: 观察能量集中在左上角（低频区域）',
    ],
    'jpeg_simulate': [
        'Step 1: 用指定 quality 因子压缩图像（JPEG编码）',
        'Step 2: 解压缩重建图像（JPEG解码）',
        'Step 3: 对比压缩前后的差异',
    ],
    'jpeg_compare': [
        'Step 1: 用指定 quality 压缩图像',
        'Step 2: 解压缩得到重建图',
        'Step 3: 差值图: diff=|original-reconstructed|，放大5倍',
        'Step 4: 计算 PSNR 并标注',
        'Step 5: 四宫格: 原图/压缩图/差值图/PSNR',
    ],
    # Ch9
    'erosion_dilation': [
        'Step 1: 转为灰度图',
        'Step 2: 生成结构元素（椭圆形, ksize×ksize）',
        'Step 3: 腐蚀→取邻域最小值; 膨胀→取邻域最大值',
        'Step 4: 重复 iterations 次',
    ],
    'open_close': [
        'Step 1: 转为灰度图',
        'Step 2: 生成结构元素',
        'Step 3: 开运算=先腐蚀再膨胀; 闭运算=先膨胀再腐蚀',
    ],
    'skeletonize': [
        'Step 1: 转为灰度图并二值化',
        'Step 2: 反复细化: 形态学击中击不中+剥离边界',
        'Step 3: 迭代至图像不再变化（收敛）',
        'Step 4: 输出单像素宽骨架',
    ],
    # Ch10
    'otsu_threshold': [
        'Step 1: 转为灰度图',
        'Step 2: 计算灰度直方图 p_i=n_i/N',
        'Step 3: 遍历 T=0~255，计算类间方差 σ²_B(T)',
        'Step 4: 取 σ²_B 最大的 T* 为最优阈值',
        'Step 5: 以 T* 二值化: I_binary=255 if I≥T* else 0',
    ],
    'adaptive_threshold': [
        'Step 1: 转为灰度图',
        'Step 2: 逐像素计算 block_size×block_size 邻域高斯加权均值',
        'Step 3: 局部阈值 T=均值-C',
        'Step 4: 逐像素二值化: I≥T→255, else 0',
    ],
    'kmeans_segment': [
        'Step 1: 图像像素值展平为 (N,3) 数据矩阵',
        'Step 2: K-means++ 初始化 K 个聚类中心',
        'Step 3: 分配每个像素到最近的中心',
        'Step 4: 更新中心为簇均值',
        'Step 5: 重复 Step 3-4 直到收敛',
        'Step 6: 每像素替换为其簇的中心颜色',
    ],
    'watershed': [
        'Step 1: 灰度图→OTSU二值化（反相）',
        'Step 2: 膨胀获取确定背景区域',
        'Step 3: 距离变换→阈值确定前景标记',
        'Step 4: 未知区域=背景-前景（由分水岭决定）',
        'Step 5: 创建标记图→执行分水岭变换',
        'Step 6: 分水线标记为红色',
    ],
    'grabcut': [
        'Step 1: 定义前景矩形框（距边缘10像素的中央区域）',
        'Step 2: 初始化 GMM（前景/背景各5高斯分量）',
        'Step 3: 分配像素到最可能的高斯分量',
        'Step 4: 从分配中重新学习 GMM 参数',
        'Step 5: 图割最小化能量函数',
        'Step 6: 重复 Step 3-5 共 iters 次',
    ],
    # Ch11
    'contour_extract': [
        'Step 1: 灰度图→二值化（阈值127）',
        'Step 2: findContours 检测轮廓',
        'Step 3: 按面积过滤小轮廓（>100px²）',
        'Step 4: 不同颜色绘制轮廓并标注编号',
    ],
    'convex_hull': [
        'Step 1: 灰度图→二值化→检测轮廓',
        'Step 2: 对每个外形轮廓计算凸包',
        'Step 3: 绿色绘制凸包，红色绘制原始轮廓',
    ],
    'min_enclosing': [
        'Step 1: 灰度图→二值化→检测最外层轮廓',
        'Step 2: 根据模式计算 AABB/旋转矩形/外接圆',
        'Step 3: 叠加显示在原始图像上',
    ],
    'contour_approx': [
        'Step 1: 灰度图→二值化→检测最外层轮廓',
        'Step 2: 计算轮廓周长',
        'Step 3: ε=epsilon_factor×周长',
        'Step 4: DP算法提取近似多边形',
        'Step 5: 红色原始轮廓/绿色近似/蓝色顶点',
    ],
    'hu_moments': [
        'Step 1: 灰度图→二值化→检测轮廓',
        'Step 2: 对每个轮廓计算图像矩',
        'Step 3: 从矩计算7个Hu不变矩',
        'Step 4: 显示前3个轮廓的Hu矩数值',
    ],
    'shape_match': [
        'Step 1: 灰度图→二值化→检测轮廓',
        'Step 2: 对每对轮廓计算 matchShapes 距离',
        'Step 3: 为每个轮廓找到最佳匹配并标注分数',
    ],
    'fourier_descriptor': [
        'Step 1: 灰度图→二值化→检测轮廓',
        'Step 2: 对每个轮廓提取复坐标序列',
        'Step 3: FFT计算傅里叶描述子',
        'Step 4: 保留前 num_descriptors 个系数，其余清零',
        'Step 5: IFFT重建近似轮廓（绿色）',
        'Step 6: 红色原始轮廓+绿色重建叠加对比',
    ],
    # Ch12
    'template_matching': [
        'Step 1: 取图像中心 1/3 区域作为模板',
        'Step 2: 选定匹配方法在全图上滑动模板',
        'Step 3: 找到相似度极值位置',
        'Step 4: 绿色框模板区域，红色框最佳匹配位置',
    ],
    'hough_lines': [
        'Step 1: Canny边缘检测',
        'Step 2: 每个边缘点在(ρ,θ)参数空间投票',
        'Step 3: 找出投票超 threshold 的(ρ,θ)参数对',
        'Step 4: 拟合线段并过滤长度<min_length的',
        'Step 5: 绿色绘制检测到的线段',
    ],
    'hough_circles': [
        'Step 1: 灰度图+高斯模糊去噪',
        'Step 2: Canny边缘检测 (param1)',
        'Step 3: 沿梯度方向投票确定圆心',
        'Step 4: 在候选圆心处投票确定半径',
        'Step 5: 非极大值抑制 (min_dist) 去除重复',
        'Step 6: 绿色圆+红点圆心标注',
    ],
    'corner_harris': [
        'Step 1: 转为灰度图',
        'Step 2: Sobel计算梯度 I_x, I_y',
        'Step 3: 在 block_size 窗口内计算协方差矩阵 M',
        'Step 4: 角点响应: R=det(M)-k·trace²(M)',
        'Step 5: 阈值筛选: R>0.01·R_max→标记角点',
        'Step 6: 膨胀后处理，红色标注角点',
    ],
    'sift_features': [
        'Step 1: 构建高斯金字塔和DoG金字塔',
        'Step 2: DoG中搜索3D邻域局部极值',
        'Step 3: 亚像素精确定位+剔除低对比度和边缘点',
        'Step 4: 为每个关键点分配主方向（梯度方向直方图）',
        'Step 5: 生成128维SIFT描述子',
        'Step 6: 可视化: 圆圈(大小=尺度)+径向线(方向)',
    ],
    'hog_features': [
        'Step 1: 计算梯度: Gx=[-1,0,1], Gy=[-1,0,1]ᵀ',
        'Step 2: 梯度幅值 m=√(Gx²+Gy²), 方向 θ=arctan(Gy/Gx)',
        'Step 3: 划分为 cell_size×cell_size 的 cell',
        'Step 4: 每个 cell 统计 9 bin 梯度方向直方图',
        'Step 5: block_size×block_size cells 为一组做L2归一化',
        'Step 6: 在图像上可视化梯度方向',
    ],
}

# 为没有专属公式/步骤的操作补齐频域通用步骤
for _op in ['ideal_highpass', 'butterworth_lowpass', 'butterworth_highpass', 'gaussian_lowpass', 'gaussian_highpass', 'bandpass_filter']:
    if _op not in STEPS_LIBRARY:
        STEPS_LIBRARY[_op] = STEPS_LIBRARY['ideal_lowpass']


# ══════════════════════ 参数描述库 ══════════════════════

PARAM_DESCRIPTIONS = {
    "sampling_demo": [
        {
            "key": "sample_rate",
            "desc": "采样率：0.05~1.0。表示保留原始分辨率的比例。1.0=不降采样，0.1=保留10%像素。越低细节丢失越严重，混叠越明显。"
        }
    ],
    "quantization_demo": [
        {
            "key": "bit_depth",
            "desc": "量化位深：1~8。1位=二值图像（2级灰度）；4位=16级灰度（伪轮廓明显）；8位=256级（视觉无损标准）。位深每减少1，灰度级数减半。"
        }
    ],
    "resolution_compare": [
        {
            "key": "scale",
            "desc": "缩放比例：0.1~1.0。将原图缩小到此比例后再放大还原，对比不同插值方法的差异。比例越小差异越显著。"
        }
    ],
    "pixel_neighbors": [
        {
            "key": "mode",
            "desc": "邻域类型：\"4-邻域\"=上下左右4个相邻像素；\"8-邻域\"=包含全部8个周围像素；\"对角邻域\"=仅4个对角位置。不同邻域定义影响连通性和距离度量。"
        }
    ],
    "distance_metrics": [
        {
            "key": "mode",
            "desc": "距离类型：\"欧几里得距离\"=直线距离（等距线为圆）；\"D4城市街区距离\"=曼哈顿距离（等距线为菱形）；\"D8棋盘距离\"=切比雪夫距离（等距线为正方形）。"
        }
    ],
    "interpolation_demo": [
        {
            "key": "method",
            "desc": "插值方法：\"最近邻插值\"=取最近像素值（速度快但有锯齿）；\"双线性插值\"=2×2邻域线性加权（较平滑）；\"双三次插值\"=4×4邻域三次拟合（最高质量但计算量最大）。"
        }
    ],
    "image_inversion": [],
    "log_transform": [
        {
            "key": "c",
            "desc": "缩放系数c：1~100。控制输出灰度范围——c越大输出越亮。太小则整体偏暗，太大则亮区过曝。通常在10~40范围调节。"
        }
    ],
    "contrast_stretch": [
        {
            "key": "low_percent",
            "desc": "低百分比：0~50。用于确定拉伸的下边界。舍弃低于此百分位的暗像素（如2%即可丢弃最暗的2%像素）。"
        },
        {
            "key": "high_percent",
            "desc": "高百分比：50~100。用于确定拉伸的上边界。舍弃高于此百分位的亮像素（如98%即可丢弃最亮的2%像素）。"
        }
    ],
    "histogram_equalization": [],
    "clahe": [
        {
            "key": "clip_limit",
            "desc": "对比度限制：0.5~10.0。控制直方图裁剪上限。1.0=无限制；2.0=适中增强（推荐）；>5.0=强增强。值越小越保守，噪声抑制越好。"
        },
        {
            "key": "tile_size",
            "desc": "网格大小：4/8/16/32。将图像划分为tile_size×tile_size的小区域各自均衡化。4=极强局部适应性（可能有噪声），8=默认推荐，16/32=接近全局均衡化。"
        }
    ],
    "gamma_correction": [
        {
            "key": "gamma",
            "desc": "γ值：0.1~3.0。γ=1.0=不变；γ<1.0=拉伸暗区增亮暗部（如0.5明显提亮）；γ>1.0=压缩暗区压暗亮部（如2.0明显变暗）。显示器校正标准γ=2.2。"
        }
    ],
    "median_blur": [
        {
            "key": "ksize",
            "desc": "核大小：3/5/7/9/11/13/15（奇数）。3=轻度去噪（保留细节）；5=适中；9+ =强去噪（细节损失增大）。核越大对椒盐噪声去除越强，但细线可能丢失。"
        }
    ],
    "gaussian_blur": [
        {
            "key": "ksize",
            "desc": "核大小：3/5/7/9/11/13/15。核越大平滑范围越广。通常取 ksize≈6σ+1 以保证覆盖99.7%的权重能量。"
        },
        {
            "key": "sigma",
            "desc": "σ值：0.1~5.0。控制高斯核的\"宽度\"——σ小=轻微模糊（保留细节），σ大=强模糊。与ksize配合使用。"
        }
    ],
    "bilateral_filter": [
        {
            "key": "d",
            "desc": "邻域直径：3~25（奇数）。滤波的搜索范围——d越大滤波越强（更多邻域像素参与），但计算越慢（O(d²)）。"
        },
        {
            "key": "sigma_color",
            "desc": "颜色σ：5~150。控制像素值相似度的敏感度。值越大，越大的颜色差异也参与平均（更激进滤波，边缘保持减弱）。"
        },
        {
            "key": "sigma_space",
            "desc": "空间σ：5~150。控制空间距离的敏感度。值越大，越远的像素也参与平均。"
        }
    ],
    "laplacian": [],
    "unsharp_mask": [
        {
            "key": "amount",
            "desc": "锐化强度：0.1~5.0。控制叠加高频细节的权重。1.0=标准锐化；2.0~3.0=强锐化；>4.0=可能产生明显光晕伪影。"
        },
        {
            "key": "radius",
            "desc": "模糊半径：1~10。控制被增强的边缘尺度。小半径(1~2)=增强纹理细节；大半径(5~10)=增强粗轮廓边缘。"
        }
    ],
    "sobel_sharpen": [
        {
            "key": "ksize",
            "desc": "核大小：1/3/5/7。Sobel梯度的计算孔径。3=标准Sobel（最佳平衡）；1=简单中心差分（噪声敏感）；5/7=更大范围梯度（粗边缘）。"
        }
    ],
    "ideal_lowpass": [
        {
            "key": "cutoff",
            "desc": "截止频率D₀：5~200。D₀越小保留的低频越少，图像越模糊。ILPF在D₀处锐截止，会产生振铃效应。"
        }
    ],
    "ideal_highpass": [
        {
            "key": "cutoff",
            "desc": "截止频率D₀：5~200。D₀越小保留的高频越多（但直流分量被滤除，图像偏暗）。同样存在振铃效应。"
        }
    ],
    "butterworth_lowpass": [
        {
            "key": "cutoff",
            "desc": "截止频率D₀：10~200。D₀越小平滑越强。BLPF有平滑过渡带（无振铃），阶数n=4提供适中的过渡陡度。"
        }
    ],
    "butterworth_highpass": [
        {
            "key": "cutoff",
            "desc": "截止频率D₀：10~200。D₀越小保留的高频越多。BHPF平滑保留高频（无振铃），适合边缘提取预处理。"
        }
    ],
    "gaussian_lowpass": [
        {
            "key": "cutoff",
            "desc": "截止频率D₀：10~200。D₀=D₀时H≈0.607（衰减到峰值的60.7%）。GLPF无振铃，平滑效果最自然。"
        }
    ],
    "gaussian_highpass": [
        {
            "key": "cutoff",
            "desc": "截止频率D₀：10~200。D₀越小保留的高频越多。GHPF无振铃，平滑提取边缘和细节。"
        }
    ],
    "bandpass_filter": [
        {
            "key": "low_cutoff",
            "desc": "低频截止：5~100。低于此频率的成分被抑制。控制带通的低频边界。"
        },
        {
            "key": "high_cutoff",
            "desc": "高频截止：30~200。高于此频率的成分被抑制。控制带通的高频边界。带宽=high_cutoff-low_cutoff。"
        }
    ],
    "gaussian_noise": [
        {
            "key": "sigma",
            "desc": "噪声强度σ：5~100。σ越大噪声越严重。σ=10=轻微（PSNR≈28dB）；σ=25=中度（PSNR≈20dB，常用测试级别）；σ=50=重度（PSNR≈14dB）。"
        }
    ],
    "sp_noise": [
        {
            "key": "amount",
            "desc": "噪声密度：0.01~0.5。0.01=1%像素为噪声（轻微）；0.05=5%（中等）；0.2=20%（严重）。密度越高图像退化越严重。"
        }
    ],
    "mean_filter_restore": [
        {
            "key": "ksize",
            "desc": "核大小：3/5/7/9/11。3=轻度去噪；5=适中；9+ =强去噪但边缘模糊严重。均值滤波对椒盐噪声效果差（极端值拉偏均值）。"
        }
    ],
    "median_restore": [
        {
            "key": "ksize",
            "desc": "核大小：3/5/7/9/11。对椒盐噪声，5×5通常效果最佳，核过大会损失细节。中值滤波是椒盐噪声的最佳滤波器。"
        }
    ],
    "nlm_denoise": [
        {
            "key": "h",
            "desc": "滤波强度h：3~50。控制指数权重的衰减速度——h越大权重分布越均匀（去噪越强但纹理保持越弱）。通常h=10为中等强度。"
        }
    ],
    "wiener_filter": [
        {
            "key": "ksize",
            "desc": "核大小：3/5/7/9。控制局部统计窗口大小——越大平滑越强，但自适应能力越弱（局部方差被过度平滑）。"
        }
    ],
    "sobel": [
        {
            "key": "ksize",
            "desc": "核大小：1/3/5/7。3=标准Sobel算子（推荐）；1=简单中心差分；5/7=更大范围梯度估计（边缘变粗但噪声抑制更强）。"
        }
    ],
    "canny": [
        {
            "key": "low_threshold",
            "desc": "低阈值：0~255。低于此值的梯度直接丢弃。通常取high_threshold的1/3~1/2。低阈值越低检测到的弱边缘越多（但可能含噪声）。"
        },
        {
            "key": "high_threshold",
            "desc": "高阈值：0~255。高于此值的梯度确定为强边缘。高阈值越高检测到的边缘越少但越可靠。需配合low_threshold使用。"
        }
    ],
    "rgb_split": [
        {
            "key": "channel",
            "desc": "显示通道：\"R\"=红色通道灰度分量；\"G\"=绿色通道；\"B\"=蓝色通道；\"合并显示\"=四宫格排列B/G/R/原图。"
        }
    ],
    "rgb_to_hsv": [
        {
            "key": "channel",
            "desc": "显示通道：\"H\"=色调分量（0°=黑，180°=白）；\"S\"=饱和度分量；\"V\"=亮度分量；\"合并显示\"=HSV映射回BGR。"
        }
    ],
    "hue_adjust": [
        {
            "key": "shift",
            "desc": "色调偏移：-180~180度。正数顺时针旋转色环（红→黄→绿→青）；负数逆时针。|shift|=180时色相完全反转。"
        }
    ],
    "saturation_adjust": [
        {
            "key": "factor",
            "desc": "饱和度因子：0~3.0。0=完全去色（灰度图）；1.0=不变；1.5=鲜艳；2.0+ =过度饱和（颜色不自然）。"
        }
    ],
    "brightness_adjust": [
        {
            "key": "beta",
            "desc": "亮度增量：-100~100。正值增亮，负值减暗。|beta|>50可能造成高光溢出或暗部压碎（信息不可逆损失）。"
        }
    ],
    "color_balance": [
        {
            "key": "r_gain",
            "desc": "红色增益：0.5~2.0。>1偏红（暖色调），<1偏青。"
        },
        {
            "key": "g_gain",
            "desc": "绿色增益：0.5~2.0。>1偏绿，<1偏品红。人眼对绿色最敏感。"
        },
        {
            "key": "b_gain",
            "desc": "蓝色增益：0.5~2.0。>1偏蓝（冷色调），<1偏黄。"
        }
    ],
    "pseudo_color": [
        {
            "key": "colormap",
            "desc": "伪彩色映射表：jet=蓝→绿→黄→红（最常用）；hot=黑→红→黄→白（强调高温）；turbo=改进jet（更均匀感知）；rainbow=彩虹色。"
        }
    ],
    "color_hist_eq": [],
    "gaussian_pyramid": [
        {
            "key": "levels",
            "desc": "金字塔层数：1~5。1=仅原图；3=标准三层金字塔（每层缩小1/4）；5=深层金字塔。层数越多顶层越抽象（全局结构）。"
        }
    ],
    "laplacian_pyramid": [
        {
            "key": "levels",
            "desc": "金字塔层数：1~5。与高斯金字塔同步，控制分解深度。每层保留高斯金字塔相邻层之间的高频残差。"
        }
    ],
    "pyramid_blend": [
        {
            "key": "levels",
            "desc": "融合层数：1~5。层数越多融合越平滑自然（在更多尺度上过渡），但高层低频差异越大。3层为通常推荐值。"
        }
    ],
    "dwt_denoise": [
        {
            "key": "threshold",
            "desc": "降噪阈值：5~100。阈值越大去噪越强（更多DCT系数被清零），但细节损失也越多。阈值=30为适中强度。"
        }
    ],
    "dwt_edge_enhance": [
        {
            "key": "gain",
            "desc": "边缘增益：0.5~5.0。1.0=不增强；2.0=适度增强（边缘更清晰）；5.0=强增强（可能引入振铃效应）。"
        }
    ],
    "dct_visualize": [],
    "jpeg_simulate": [
        {
            "key": "quality",
            "desc": "压缩质量：5~100。100=最高质量（接近无损）；75=高质量（轻微压缩）；50=中等质量（块效应开始可见）；10=低质量（严重块效应和色块）。"
        }
    ],
    "jpeg_compare": [
        {
            "key": "quality",
            "desc": "压缩质量：5~100。值越低压缩率越高但失真越大。30=明显块效应；50=中等；90=近无损。差值图放大5倍显示失真分布。"
        }
    ],
    "binary_rle": [
        {
            "key": "threshold",
            "desc": "二值化阈值：0~255。灰度≥阈值→255（白），<阈值→0（黑）。128=标准中点。阈值影响黑白比例，进而影响压缩比。"
        }
    ],
    "binary_huffman": [
        {
            "key": "threshold",
            "desc": "二值化阈值：0~255。影响0/1的比例分布，进而影响信息熵和哈夫曼编码的理论压缩比。熵越低压缩率越高。"
        }
    ],
    "erosion_dilation": [
        {
            "key": "mode",
            "desc": "操作模式：\"腐蚀\"=收缩亮区→消除小亮噪点和细连接；\"膨胀\"=扩展亮区→填充小黑孔和断裂。两者是对偶操作。"
        },
        {
            "key": "ksize",
            "desc": "结构元素大小：3/5/7/9/11。SE越大效果越显著（腐蚀更多或膨胀更广）。椭圆形SE具有各向同性。"
        },
        {
            "key": "iterations",
            "desc": "迭代次数：1~10。多次迭代等效于使用更大SE。建议优先增大ksize而非增加迭代次数。"
        }
    ],
    "open_close": [
        {
            "key": "mode",
            "desc": "操作模式：\"开运算\"=先腐蚀后膨胀→去噪+断开窄连接；\"闭运算\"=先膨胀后腐蚀→填孔+弥合断裂。两者均为幂等操作。"
        },
        {
            "key": "ksize",
            "desc": "结构元素大小：3/5/7/9/11。SE应略大于目标特征（要消除的噪点或要填充的孔洞）。"
        }
    ],
    "morph_gradient": [
        {
            "key": "ksize",
            "desc": "结构元素大小：3/5/7。3=细边缘（1~2像素宽）；5=中等；7=粗边缘。SE越大提取的梯度边缘越粗。"
        }
    ],
    "tophat": [
        {
            "key": "ksize",
            "desc": "结构元素大小：3/5/7/9/11。SE应略大于目标亮特征的尺寸——SE太小无法消除背景趋势，太大可能连目标一起消除。"
        }
    ],
    "blackhat": [
        {
            "key": "ksize",
            "desc": "结构元素大小：3/5/7/9/11。SE应略大于目标暗特征的尺寸。与顶帽变换互补，两者结合可同时提取亮暗特征。"
        }
    ],
    "skeletonize": [],
    "otsu_threshold": [],
    "adaptive_threshold": [
        {
            "key": "block_size",
            "desc": "邻域大小：3/5/7/9/11/13/15（奇数）。小值=强局部适应（但对噪声敏感）；大值=趋近全局阈值。11为常用推荐值。"
        },
        {
            "key": "c",
            "desc": "常数C：-10~30。C>0→阈值降低（更多白色前景）；C<0→阈值提高（更多黑色背景）。C=2为常用值，使局部阈值略低于邻域均值。"
        }
    ],
    "kmeans_segment": [
        {
            "key": "k",
            "desc": "聚类数K：2~8。K=2为二值分割（前景/背景）；K=3~5为常用范围；K=8为细粒度分割。K越大分割越细但可能过分割。"
        }
    ],
    "mean_shift_segment": [
        {
            "key": "sp",
            "desc": "空间半径：5~100。控制空间邻域范围——sp越大分割区域越大（更多像素聚合到同一区域）。"
        },
        {
            "key": "sr",
            "desc": "颜色半径：5~100。控制颜色邻域范围——sr越大允许更大的颜色差异归入同一区域（更粗粒度的分割）。"
        }
    ],
    "watershed": [
        {
            "key": "thresh",
            "desc": "前景阈值：0~255。通过距离变换确定前景标记的阈值。阈值越大前景区域越小→分割越保守（减少过分割）。"
        }
    ],
    "grabcut": [
        {
            "key": "iters",
            "desc": "迭代次数：1~10。每次迭代重新估计GMM参数并执行图割。3~5次通常足够收敛；更多迭代边缘更精细但收益递减。"
        }
    ],
    "contour_extract": [
        {
            "key": "mode",
            "desc": "提取模式：\"所有轮廓\"=含内部孔洞和嵌套关系（RETR_TREE）；\"最外层\"=仅外部边界（RETR_EXTERNAL）。"
        }
    ],
    "convex_hull": [],
    "min_enclosing": [
        {
            "key": "mode",
            "desc": "外接形状：\"矩形\"=轴对齐矩形AABB（蓝色）；\"旋转矩形\"=最小面积矩形MAR（绿色）；\"圆形\"=最小外接圆（红色）；\"全部显示\"=三者叠加。"
        }
    ],
    "contour_approx": [
        {
            "key": "epsilon",
            "desc": "近似精度：0.001~0.1。ε=epsilon×周长。0.001=极高精度（接近原始轮廓）；0.01=中等简化；0.05=高度简化（仅保留关键顶点）。"
        }
    ],
    "hu_moments": [],
    "shape_match": [],
    "fourier_descriptor": [
        {
            "key": "num_descriptors",
            "desc": "描述子数量：5~50。5=仅全局形状（近似椭圆）；20=保留主要形状特征（推荐）；50=包含精细边界细节。越多描述子重建越精确。"
        }
    ],
    "template_matching": [
        {
            "key": "method",
            "desc": "匹配方法：\"平方差匹配\"=相减平方和（越小越好）；\"归一化互相关\"=归一化点乘（越大越好，对亮度鲁棒）；\"相关系数匹配\"=去均值后的相关（对亮度变化最鲁棒）。"
        }
    ],
    "hough_lines": [
        {
            "key": "threshold",
            "desc": "投票阈值：50~300。最小投票数——阈值越高检测到的直线越少但每条线越可靠（支持它的边缘点越多）。"
        },
        {
            "key": "min_length",
            "desc": "最小线长：10~200。过滤短于此长度的线段。增大可减少噪点产生的短线段误检。"
        }
    ],
    "hough_circles": [
        {
            "key": "dp",
            "desc": "累加器分辨率：1.0~2.0。1.0=全分辨率（精确但慢）；2.0=半分辨率（快但可能漏检小圆）。"
        },
        {
            "key": "min_dist",
            "desc": "圆心最小距离：10~200。防止同一圆被重复检测——相邻圆心距离小于此值的圆被视为重复。"
        },
        {
            "key": "param1",
            "desc": "Canny高阈值：50~300。用于边缘检测的Canny高阈值。"
        },
        {
            "key": "param2",
            "desc": "圆心检测阈值：10~100。圆心累加器的投票阈值——越小检测到的圆越多（但可能误检非圆形物体）。"
        }
    ],
    "corner_harris": [
        {
            "key": "block_size",
            "desc": "邻域大小：2~10。用于计算梯度协方差矩阵M的窗口大小。2=较小窗口（精细角点检测）；4~6=常用范围。"
        },
        {
            "key": "ksize",
            "desc": "Sobel核大小：3/5/7。梯度计算时的Sobel孔径。3=标准Sobel（推荐）。"
        },
        {
            "key": "k",
            "desc": "Harris参数k：0.01~0.10。角点响应函数R=det(M)-k·trace²(M)中的自由参数，通常取0.04~0.06。"
        }
    ],
    "sift_features": [],
    "hog_features": [
        {
            "key": "cell_size",
            "desc": "Cell大小：4/8/16（像素）。每个cell计算一个9方向梯度直方图。小cell=更细粒度的特征描述。"
        },
        {
            "key": "block_size",
            "desc": "Block大小：2/3/4（以cell为单位）。每个block内的cells做归一化。大block提供更强的光照不变性。"
        }
    ]
}
