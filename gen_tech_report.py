#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Surgical-TSplineGS 深度技术报告 PDF 生成器。
基于源码实证分析，面向资深从业者/学者，涵盖系统架构、核心算法(TASS/MG-MAS/
Hermite样条/运动分类/CVD)、损失体系、训练流程、渲染管线、双环境数据流水线、
工程实现、评估指标、实验结论与局限性。
"""

from fpdf import FPDF
import os

# ---- Fonts (Noto Sans CJK 支持中英文混排) ----
FONT_REG = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FONT_BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_SERIF = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc"
FONT_SERIF_BOLD = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

NAVY = (0, 51, 102)
STEEL = (31, 73, 125)
GREY = (60, 60, 60)
DGREY = (40, 40, 40)
LIGHT = (238, 242, 248)
CODE_BG = (244, 246, 249)
NOTE_BG = (229, 242, 255)
NOTE_BD = (0, 102, 204)
WARN_BG = (255, 244, 230)
WARN_BD = (204, 120, 0)


class ReportPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font("Noto", "", FONT_REG)
        self.add_font("Noto", "B", FONT_BOLD)
        self.add_font("Serif", "", FONT_SERIF)
        self.add_font("Serif", "B", FONT_SERIF_BOLD)
        # CJK 无真斜体，用常规文件注册 I/BI 以支持样式标记
        self.add_font("Serif", "I", FONT_SERIF)
        self.add_font("Serif", "BI", FONT_SERIF_BOLD)
        self.add_font("Noto", "I", FONT_REG)
        self.add_font("Mono", "", FONT_MONO)
        self._toc = []

    # ---- 页眉页脚 ----
    def header(self):
        if self.page_no() > 1:
            self.set_y(8)
            self.set_font("Noto", "", 7.5)
            self.set_text_color(120, 120, 120)
            self.cell(0, 4, "Surgical-TSplineGS \u6280\u672f\u62a5\u544a  |  \u62d3\u6251\u611f\u77e5\u8fd0\u52a8\u81ea\u9002\u5e94\u6837\u6761\u4e0e\u5b9e\u65f6\u52a8\u6001 3D \u9ad8\u65af\u91cd\u5efa", align="L")
            self.set_text_color(160, 160, 160)
            self.cell(0, 4, "Monocular Endoscopy", align="R", new_x="LMARGIN", new_y="NEXT")
            self.set_draw_color(210, 210, 210)
            self.set_line_width(0.2)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(3)

    def footer(self):
        self.set_y(-13)
        self.set_draw_color(210, 210, 210)
        self.set_line_width(0.2)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(1.5)
        self.set_font("Noto", "", 7.5)
        self.set_text_color(130, 130, 130)
        self.cell(0, 5, "\u673a\u5bc6  \u00b7  \u6280\u672f\u8bc4\u4f30\u62a5\u544a  \u00b7  \u5317\u4eac\u822a\u7a7a\u822a\u5929\u5927\u5b66", align="L")
        self.cell(0, 5, f"\u7b2c {self.page_no()} \u9875", align="R")

    # ---- 内容原语 ----
    def h1(self, num, title):
        self._toc.append((1, f"{num}  {title}", self.page_no()))
        self.ln(4)
        self.set_font("Noto", "B", 17)
        self.set_text_color(*NAVY)
        self.cell(0, 11, f"{num}  {title}")
        self.ln(8)
        self.set_draw_color(*NAVY)
        self.set_line_width(0.7)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def h2(self, num, title):
        self._toc.append((2, f"   {num}  {title}", self.page_no()))
        self.set_font("Noto", "B", 13)
        self.set_text_color(*STEEL)
        self.ln(3)
        self.cell(0, 9, f"{num}  {title}")
        self.ln(7)

    def h3(self, title):
        self.set_font("Noto", "B", 10.5)
        self.set_text_color(*DGREY)
        self.ln(2)
        self.cell(0, 7, title)
        self.ln(6)

    def body(self, text):
        self.set_font("Noto", "", 9.8)
        self.set_text_color(*DGREY)
        self.multi_cell(0, 5.6, text)
        self.ln(1.5)

    def bullet(self, text, indent=6):
        self.set_font("Noto", "", 9.8)
        self.set_text_color(*DGREY)
        x = self.get_x()
        self.set_x(x + indent)
        self.cell(4, 5.6, "\u25aa")
        self.multi_cell(0, 5.6, text)
        self.ln(0.8)

    def num_item(self, n, text, indent=6):
        self.set_font("Noto", "B", 9.8)
        self.set_text_color(*STEEL)
        self.set_x(self.get_x() + indent)
        self.cell(7, 5.6, f"{n}.")
        self.set_font("Noto", "", 9.8)
        self.set_text_color(*DGREY)
        self.multi_cell(0, 5.6, text)
        self.ln(0.8)

    def formula(self, text):
        self.set_font("Serif", "I", 10.5)
        self.set_text_color(20, 30, 60)
        self.set_fill_color(*LIGHT)
        self.ln(1)
        self.set_x(14)
        self.multi_cell(0, 6.4, text, border=0, fill=True, align="C")
        self.ln(1.5)

    def code(self, text):
        self.set_font("Mono", "", 7.8)
        self.set_text_color(35, 45, 60)
        self.set_fill_color(*CODE_BG)
        self.set_draw_color(205, 212, 222)
        self.ln(1.5)
        x0 = self.get_x()
        for line in text.split("\n"):
            self.set_x(x0 + 10)
            self.cell(0, 4.3, line if line else " ", fill=True)
            self.ln(4.3)
        self.ln(2)

    def note(self, text, kind="info"):
        bg = NOTE_BG if kind == "info" else WARN_BG
        bd = NOTE_BD if kind == "info" else WARN_BD
        self.set_fill_color(*bg)
        self.set_draw_color(*bd)
        self.set_font("Noto", "B", 8.6)
        self.set_text_color(*bd)
        self.ln(1.5)
        self.set_x(10)
        tag = "\u3010\u6d41\u7a0b\u539f\u8bed\u3011" if kind == "info" else "\u3010\u5de5\u7a0b\u6ce8\u8bb0\u3011"
        self.multi_cell(0, 5.2, tag, border=0, fill=True)
        self.set_font("Noto", "", 8.8)
        self.set_text_color(40, 50, 70)
        self.set_x(10)
        self.set_y(self.get_y() - 1)
        self.multi_cell(0, 5.0, text, border=1, fill=False)
        self.ln(3)

    def kv_table(self, rows, w_key=58, w_val=128):
        self.set_font("Noto", "", 8.8)
        self.ln(1)
        for i, (k, v) in enumerate(rows):
            self.set_fill_color(*LIGHT) if i % 2 == 0 else self.set_fill_color(255, 255, 255)
            self.set_text_color(*STEEL)
            self.set_font("Noto", "B", 8.6)
            self.cell(w_key, 5.6, k, border=1, fill=True)
            self.set_text_color(*DGREY)
            self.set_font("Noto", "", 8.6)
            self.cell(w_val, 5.6, v, border=1, fill=True)
            self.ln(5.6)
        self.ln(2)

    def toc_page(self):
        self.add_page()
        self.h1_toc("\u76ee\u5f55")
        self.set_font("Noto", "", 10)
        for lvl, title, page in self._toc:
            if lvl == 1:
                self.set_text_color(*NAVY)
                self.set_font("Noto", "B", 10.5)
                self.set_x(10)
            else:
                self.set_text_color(*GREY)
                self.set_font("Noto", "", 9.6)
                self.set_x(18)
            self.cell(0, 6.4, f"{title}")
            self.set_x(180)
            self.cell(0, 6.4, f"{page}", align="R")
            self.ln(6.4)

    def h1_toc(self, title):
        self.ln(4)
        self.set_font("Noto", "B", 17)
        self.set_text_color(*NAVY)
        self.cell(0, 11, title)
        self.ln(8)
        self.set_draw_color(*NAVY)
        self.set_line_width(0.7)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)


def build():
    pdf = ReportPDF()
    pdf.set_auto_page_break(auto=True, margin=18)

    # ============================== 封面 ==============================
    pdf.add_page()
    pdf.ln(28)
    pdf.set_draw_color(*NAVY)
    pdf.set_line_width(0.5)
    pdf.rect(14, 30, 182, 200)
    pdf.ln(20)
    pdf.set_font("Noto", "B", 30)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 15, "Surgical-TSplineGS", align="C")
    pdf.ln(17)
    pdf.set_font("Serif", "B", 13.5)
    pdf.set_text_color(*STEEL)
    pdf.cell(0, 8, "Topology-Aware Motion-Adaptive Splines", align="C")
    pdf.ln(8)
    pdf.cell(0, 8, "for Real-Time Dynamic 3D Reconstruction", align="C")
    pdf.ln(8)
    pdf.cell(0, 8, "in Monocular Endoscopy", align="C")
    pdf.ln(16)
    pdf.set_draw_color(*STEEL)
    pdf.set_line_width(0.4)
    pdf.line(55, pdf.get_y(), 155, pdf.get_y())
    pdf.ln(12)
    pdf.set_font("Noto", "", 13)
    pdf.set_text_color(*DGREY)
    pdf.cell(0, 8, "\u62d3\u6251\u611f\u77e5 \u00b7 \u8fd0\u52a8\u81ea\u9002\u5e94\u6837\u6761", align="C")
    pdf.ln(7)
    pdf.cell(0, 8, "\u5355\u76ee\u5185\u7a91\u5185\u89c6\u5b9e\u65f6\u52a8\u6001 3D \u9ad8\u65af\u91cd\u5efa", align="C")
    pdf.ln(26)
    pdf.set_font("Noto", "", 11)
    pdf.set_text_color(*GREY)
    pdf.cell(0, 7, "\u6df1\u5ea6\u6280\u672f\u8bc4\u4f30\u62a5\u544a\uff08\u884c\u4e1a\u8d44\u6df1\u4e13\u5bb6\u89c6\u89d2\uff09", align="C")
    pdf.ln(22)
    pdf.set_font("Noto", "", 10)
    pdf.set_text_color(110, 110, 110)
    pdf.cell(0, 6, "\u4f5c\u8005:  Qi Chen", align="C")
    pdf.ln(6)
    pdf.cell(0, 6, "\u5355\u4f4d:  Beihang University", align="C")
    pdf.ln(6)
    pdf.cell(0, 6, "\u4ee3\u7801\u4ed3\u5e93:  github.com/chenqi111/Surgical-TSplineGS", align="C")
    pdf.ln(10)
    pdf.set_font("Serif", "I", 9)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 6, "Technical Report  \u00b7  Source-Code-Verified Analysis", align="C")

    # ============================== 摘要 ==============================
    pdf.add_page()
    pdf.h1_toc("\u6458\u8981 (Executive Summary)")
    pdf.body(
        "Surgical-TSplineGS 是一套面向单目内窥镜手术场景的动态三维重建与实时渲染框架，"
        "其本质是在 4D Gaussian Splatting (4DGS) 的表示范式之上，引入\"运动自适应样条\"机制以显式建模组织形变与器械刚性运动，"
        "并针对手术特有拓扑变化（组织切割/撕裂）提出拓扑感知的样条分裂策略。本报告基于对完整源码的实证分析，"
        "从表示理论、几何先验融合、可微渲染、优化动力学与工程实现五个维度对该系统进行深度剖析。"
    )
    pdf.h3("核心论断")
    pdf.bullet(
        "\u4ee3\u8868\u6027\u521b\u65b0\uff1a\u4ee5\u53ef\u5b66\u4e60\u7684\u4e09\u6b21 Hermite \u6837\u6761\u63a7\u5236\u70b9\u66ff\u4ee3 MLP \u53d8\u5f62\u573a\uff0c"
        "\u5c06\u52a8\u6001\u8f68\u8ff9\u5efa\u6a21\u4ece\u9690\u5f0f\u795e\u7ecf\u573a\u56de\u5f52\u5230\u663e\u5f0f\u51e0\u4f55\uff0c\u53ef\u89e3\u3001\u53ef\u63a7\u3001\u53ef\u526a\u88c1\u3002"
    )
    pdf.bullet(
        "\u624b\u672f\u573a\u666f\u9488\u5bf9\u6027\uff1aTASS\uff08\u62d3\u6251\u611f\u77e5\u6837\u6761\u5206\u88c2\uff09\u4e0e MG-MAS\uff08\u63a9\u819c\u5f15\u5bfc\u8fd0\u52a8\u81ea\u9002\u5e94\u6837\u6761\uff09"
        "\u76f4\u51fb\u5185\u7a91\u573a\u666f\u7684\u4e24\u4e2a\u95f9\u70b9\u2014\u2014\u7ec4\u7ec7\u62d3\u6251\u53d8\u5316\u4e0e\u5668\u68b0\u906e\u6321\u4e0b\u7684\u8fd0\u52a8\u89e3\u8026\u3002"
    )
    pdf.bullet(
        "\u51e0\u4f55\u5148\u9a8c\u878d\u5408\uff1a\u901a\u8fc7 UniDepth \u5ea6\u91cf\u6df1\u5ea6 / Depth-Anything \u89c6\u5dee + CoTracker3 \u957f\u7a0b\u70b9\u8f68\u8ff9\u63d0\u4f9b\u51e0\u4f55\u4e0e\u8fd0\u52a8\u76d1\u7763\uff0c"
        "\u7ed3\u5408\u4f4d\u59ff-\u6df1\u5ea6\u5c3a\u5ea6\u8054\u5408\u4f30\u8ba1(CVD)\u89e3\u51b3\u5355\u76ee\u5c3a\u5ea6-\u5c3a\u5ea6\u6a21\u7cca\u6027\u3002"
    )
    pdf.bullet(
        "\u6e32\u67d3\u8d28\u91cf\u4e0e\u6548\u7387\uff1a\u57fa\u4e8e gsplat \u7816\u5757\u5316\u53ef\u5fae\u5206\u5149\u6805\u5316\uff0c\u5b9e\u73b0\u65b0\u89c6\u89d2\u5408\u6210\u8d28\u91cf\u4e0e\u5b9e\u65f6\u6027\u80fd\u7684\u517c\u987e\u3002"
    )
    pdf.h3("报告阅读对象")
    pdf.body(
        "本报告面向计算机图形学/计算机视觉/医学影像计算领域的研究者与系统架构师，假设读者熟悉 3D Gaussian Splatting、"
        "可微渲染与刚体/非刚体运动估计的基本理论。报告内容均与源码具体位置对应，便于复现与二次开发核查。"
    )

    # ============================== TOC ==============================
    pdf.toc_page()

    # ============================== 1. 背景与问题 ==============================
    pdf.add_page()
    pdf.h1("1", "\u7814\u7a76\u80cc\u666f\u4e0e\u95ee\u9898\u5b9a\u4e49")
    pdf.h2("1.1", "\u4e34\u5e8a\u80cc\u666f\u4e0e\u52a8\u673a")
    pdf.body(
        "微创手术(MIS)依赖内窥镜提供的二维图像流进行操作，外科医生须在缺失直接深度感知与三维空间信息的条件下完成精细操作。"
        "若能从单目内窥镜视频流中在线重建场景的动态三维结构，即可为术中导航、AR 辅助叠加、术后复盘与手术教学提供关键支撑。"
        "然而，内窥镜场景相比通用视频具有更强的退化特性：手持相机产生剧烈且未知的位姿变化、近焦工作距离导致强透视与高光、"
        "湿润组织表面缺少稳定纹理、器械频繁进出造成大范围遮挡，以及组织切割/缝合带来的拓扑突变。"
    )
    pdf.h2("1.2", "\u6280\u672f\u96be\u70b9\u7684\u5f62\u5f0f\u5316")
    pdf.num_item("1", "\u5355\u76ee\u5c3a\u5ea6-\u5c3a\u5ea6\u6a21\u7cca\uff1a\u5355\u76ee\u89c6\u9891\u4ec5\u80fd\u63d0\u4f9b\u4e0a\u4e0b\u6587\u4e0d\u660e\u786e\u7684\u76f8\u5bf9\u6df1\u5ea6\uff0c\u5e3a\u5c40\u90e8\u5c3a\u5ea6\u968f\u76f8\u673a\u4f4d\u79fb\u800c\u6f02\u79fb\uff0c\u4f7f\u5f97\u7ed9\u5b9a\u4f4d\u59ff\u540e\u7684\u70b9\u4e91\u5c3a\u5ea6\u4e0d\u4e00\u81f4\u3002")
    pdf.num_item("2", "\u76f8\u673a\u8fd0\u52a8\u4e0e\u573a\u666f\u8fd0\u52a8\u7684\u8026\u5408\uff1a\u89c2\u6d4b\u5230\u7684\u8fd0\u52a8\u662f\u76f8\u673a\u4f4d\u59ff\u53d8\u5316\u4e0e\u573a\u666f\u70b9\u8fd0\u52a8\u7684\u590d\u5408\uff0c\u82e5\u4e0d\u89e3\u8026\u5219\u9759\u6001\u80cc\u666f\u4f1a\u88ab\u8bef\u5efa\u6a21\u4e3a\u52a8\u6001\uff0c\u52a8\u6001\u7269\u4f53\u4f1a\u53cd\u4e4b\u88ab\u201c\u51bb\u7ed3\u201d\u3002")
    pdf.num_item("3", "\u62d3\u6251\u7a81\u53d8\uff1a\u7ec4\u7ec7\u5207\u5272\u4f1a\u4ea7\u751f\u65b0\u8fb9\u7f18\u4e0e\u65b0\u8868\u9762\uff0c\u4f20\u7edf\u8fde\u7eed\u5f62\u53d8\u573a\u65e0\u6cd5\u8868\u5f81\u8f68\u8ff9\u7684\u4e2d\u65ad\u4e0e\u5206\u88c2\u3002")
    pdf.num_item("4", "\u5668\u68b0\u906e\u6321\u4e0e\u521a\u4f53\u4ea4\u7ec7\uff1a\u5668\u68b0\u8fdb\u5165\u89c6\u91ce\u65f6\u4f1a\u4ee5\u521a\u4f53\u8fd0\u52a8\u8986\u76d6\u5e76\u5e72\u6270\u5bf9\u7ec4\u7ec7\u5f62\u53d8\u7684\u68af\u5ea6\u4f30\u8ba1\uff0c\u4f7f\u4e8c\u8005\u7684\u8868\u793a\u5728\u8054\u5408\u4f18\u5316\u4e2d\u4e92\u76f8\u7275\u626f\u3002")
    pdf.num_item("5", "\u5b9e\u65f6\u6027\uff1a\u4e34\u5e8a\u52a9\u624b\u7cfb\u7edf\u5bf9\u6e32\u67d3\u5ef6\u8fdf\u654f\u611f\uff0c\u8981\u6c42\u65b0\u89c6\u89d2\u5408\u6210\u8fbe\u5230 30+ FPS\u3002")

    pdf.h2("1.3", "\u4e0e\u5148\u9a8c\u65b9\u6cd5\u7684\u5173\u7cfb")
    pdf.body(
        "本系统是 4DGS (4D Gaussian Splatting) 谱系的方法，继承其\"以各向异性 3D 高斯为图元、以可微光栅化进行投影\"的表示思想，"
        "并在动态建模层做了关键替换：用显式样条控制点描述每个动态高斯的时间轨迹，而非用 deformation MLP 隐式回归位移场。"
        "其与 Shape-of-Motion、Deformable-3DGS、Dynamic-3DGS 的根本差异在于\"轨迹是几何对象而非网络输出\"，"
        "由此衍生出控制点剪枝、拓扑分裂、运动类型度量等只能在显式表示上进行的操作。"
    )

    # ============================== 2. 总体架构 ==============================
    pdf.add_page()
    pdf.h1("2", "\u7cfb\u7edf\u603b\u4f53\u67b6\u6784")
    pdf.body("系统由\"离线几何先验提取\"与\"在线四阶段联合优化\"两部分构成，数据流如下。")
    pdf.code(
        "  [Monocular Endoscopic Video]\n"
        "            |\n"
        "   ============ Dual-Env Preprocessing ============\n"
        "   Env-2 (Py3.10/CUDA12.1): UniDepth(metric depth) + Depth-Anything(disp)\n"
        "   Env-1 (Py3.7 /CUDA11.7): CoTracker3 -> long-range point tracks\n"
        "            |\n"
        "   [Per-frame: depth maps, disparity, point tracks, tool masks]\n"
        "            |\n"
        "   ============ Online Joint Optimization ============\n"
        "   PoseNet(CVD): time-MLP -> R,t + per-frame instance_scale + focal_bias\n"
        "            |\n"
        "   Static Gaussians (fixed)  ||  Dynamic Gaussians (K Hermite ctrl pts)\n"
        "            |  TASS split  |  MG-MAS grad attenuate  |  motion classify\n"
        "   gsplat tile-based differentiable rasterizer (RGB + ED)\n"
        "            |\n"
        "   RGB Decoder(MLP + cam_ray) -> final RGB ; d_alpha mask\n"
        "            |\n"
        "   [Novel views, depth, motion-type maps, split events]"
    )
    pdf.h3("关键源码映射")
    pdf.kv_table([
        ("train.py", "\u4e09\u9636\u6bb5\u8bad\u7ec3\u4e3b\u5faa\u73af\u3001\u635f\u5931\u7ec4\u88c5\u3001TASS/MG-MAS \u89e6\u53d1\u70b9 (~1500\u884c)"),
        ("scene/gaussian_model.py", "GaussianModel: 控制点、Hermite 插值、densification、TASS 分裂、MG-MAS 衰减"),
        ("scene/deformation.py", "pose_network: 时间编码 MLP -> 位姿/CVD/焦距; inverse_warp 几何工具"),
        ("gaussian_renderer/__init__.py", "render: Hermite 求值、动静拼合、gsplat 调用、运动分类、MG-MAS overlap 采样"),
        ("utils/loss_utils.py", "depth_consistency_loss / trajectory_smoothness_loss / SSIM / Dice"),
        ("arguments/surgical/default.py", "手术专用超参: K=6, eps_top=0.05, gamma=2.0, lambda 各项"),
    ])

    # ============================== 3. 表示 ==============================
    pdf.add_page()
    pdf.h1("3", "\u573a\u666f\u8868\u793a\u7406\u8bba")
    pdf.h2("3.1", "\u9759\u6001-\u52a8\u6001\u9ad8\u65af\u89e3\u8026")
    pdf.body(
        "场景被分解为两组独立的 3D 高斯集合：静态高斯(stat_gaussians)表示不随时间变化的背景/固定结构，其属性(xyz, scale, rotation, opacity, SH)固定不变；"
        "动态高斯(dyn_gaussians)表示可形变/可运动物体，每个点的位置通过样条控制点描述时间轨迹。渲染时两组高斯在属性张量上 cat 拼接后一次性送入 gsplat，"
        "并通过一个单独光栅化的 d_alpha 通道区分动态区域。这种解耦的本质是\"把时间维度的自由度只分配给真正需要它的图元\"，"
        "从而把动态表示的参数量与计算量从 O(N_total) 降到 O(N_dyn)，并避免静态背景被相机位姿噪声误建模为形变。"
    )
    pdf.note(
        "渲染时静态与动态高斯在 means3D / scales / rotations / opacity / colors 上做 torch.cat 拼接，"
        "但在梯度反传时按索引切片分离(static 段与 dynamic 段各自累积 viewspace 梯度与 densification 统计)，"
        "确保 densify/prune 策略可对两类图元独立施加不同阈值(densify_grad_threshold vs densify_grad_threshold_dynamic)。"
    )

    pdf.h2("3.2", "\u4e09\u6b21 Hermite \u6837\u6761\u8f68\u8ff9\u5efa\u6a21")
    pdf.body(
        "为每个动态高斯分配 K 个可学习控制点 control_xyz in R^{K x 3}。给定归一化时间 t in [0,1]，"
        "在控制点序列上做三次 Hermite 插值得到位移偏移，最终位置为："
    )
    pdf.formula("x(t) = x_base + s * Hermite(control_xyz[0:k], t),   k = current_control_num")
    pdf.body(
        "其中 s = deform_spatial_scale(=1e-2) 为位移尺度因子，控制轨迹幅值与基础坐标尺度的相对关系。"
        "区间 [p1,p2] 上的 Hermite 基函数为："
    )
    pdf.formula("H(t) = h00*p1 + h10*m0 + h01*p2 + h11*m1")
    pdf.formula("h00=(1+2t)(1-t)^2,  h10=t(1-t)^2,  h01=t^2(3-2t),  h11=t^2(t-1)")
    pdf.body(
        "切向量 m0,m1 采用\"单侧差分\"处理边界：当左邻索引等于当前索引(左端点)时 m0=p2-p1，否则取 (p2-p0)/2 中心差分；右端对称处理。"
        "这一边界策略保证了端点处导数不会外推溢出，对内窥镜视频\"轨迹在序列两端被截断\"的情形尤为重要。"
    )
    pdf.h3("关键实现差异")
    pdf.kv_table([
        ("控制点数 K", "手术场景 K=6 (default.py)，通用场景 K=12 (arguments/__init__.py)"),
        ("插值实现", "renderer.interpolate_cubic_hermite (训练, batched gather) 与 model.interpolate_cubic_hermite (管理/剪枝)"),
        ("inverse_cubic_hermite", "通过 lstsq 反解控制点：用于初始化阶段把光流轨迹拟合到控制点"),
        ("current_control_num", "逐点记录当前有效控制点数，支持\"按需\"轨迹分辨率"),
    ])
    pdf.note(
        "K 的选择是表示力与过拟合风险的权衡：手术组织形变以低频为主，K=6 足以表达且利于剪枝；"
        "通用场景物体运动更复杂，K=12 提供更高自由度。该差异直接体现在 default.py 与基线 config 的 control_num 字段。",
        kind="warn",
    )

    pdf.h2("3.3", "\u81ea\u9002\u5e94\u63a7\u5236\u70b9\u526a\u88c1 (Adaptive Pruning)")
    pdf.body(
        "运动自适应性的核心在于控制点数量的动态管理。onedown_control_pts 在训练中按间隔将每点控制点数从 k 降至 k-1："
        "对候选被删控制点，用 Hermite 反演评估删除后的 2D 投影误差(compute_prune_error)，仅当误差低于 prune_error_threshold 时才执行删除。"
        "于是刚性整体平动的轨迹会被压缩到极少控制点，而复杂非刚性形变保留较多控制点，实现\"表示预算按运动复杂度分配\"。"
        "手术场景 prune_error_threshold=0.5 严于通用场景的 1.0，反映组织形变对轨迹保真度要求更高。"
    )

    # ============================== 4. 核心创新 ==============================
    pdf.add_page()
    pdf.h1("4", "\u624b\u672f\u573a\u666f\u9488\u5bf9\u6027\u521b\u65b0")
    pdf.body("本章详述针对内窥镜痛点设计的两大机制(TASS、MG-MAS)与运动分类，均可在显式样条表示上高效实现。")

    pdf.h2("4.1", "TASS: \u62d3\u6251\u611f\u77e5\u6837\u6761\u5206\u88c2")
    pdf.body(
        "动机：组织切割会使原本连续的同一空间点出现轨迹\"断裂\"——切割前是单一路径，切割后裂为两段分别运动。"
        "若强行用单条连续样条拟合，会在断点处产生持续的高光度误差并污染邻域梯度。TASS 主动检测此类断裂并分裂轨迹。"
    )
    pdf.h3("检测准则")
    pdf.body("为每个动态高斯维护一个 3 帧滑动光度误差缓冲与连续计数器 tass_error_count：")
    pdf.formula("trigger split  iff  (e_t > eps_top) for >= 3 consecutive frames  and  not already split")
    pdf.body("其中 e_t 为该高斯在当前帧的逐点光度误差(通过对 2D 投影中心做 grid_sample 从像素误差图采样得到)，eps_top=0.05 为手术配置阈值。")
    pdf.h3("分裂算子")
    pdf.body(
        "命中触发后 _tass_split_gaussian 将父高斯复制为子高斯：子高斯继承父的全部属性(xyz/scale/rotation/opacity/SH/features_t/omega)，"
        "其控制点以父控制点 + 小噪声(1e-3)初始化，split_depth 递增。两条轨迹在分裂瞬间相同，随后由下游光度/几何损失驱动各自发散，"
        "从而\"无监督地\"表达切割后两片组织的独立运动。tass_split_flags 防止同一高斯重复分裂。"
    )
    pdf.note(
        "代码路径: gaussian_model.py:620 tass_detect_and_split / :657 _tass_split_gaussian；"
        "触发调度在 train.py:808，每 100 迭代采样一次像素误差并调用检测。MG-MAS 的 overlap 张量在此处复用为\"每高斯误差代理\"。"
    )

    pdf.h2("4.2", "MG-MAS: \u63a9\u819c\u5f15\u5bfc\u8fd0\u52a8\u81ea\u9002\u5e94\u6837\u6761")
    pdf.body(
        "动机：器械遮挡区域，组织高斯的真实形变梯度被器械外观主导，若放任反传会把组织轨迹错误地\"拉向器械运动\"。"
        "MG-MAS 利用器械 instance mask 计算每个动态高斯被遮挡的程度，并据此衰减其控制点梯度，实现器械刚性运动与组织形变的解耦。"
    )
    pdf.h3("逐高斯遮挡率估计")
    pdf.body(
        "渲染时对全部高斯做投影得到 2D 中心 means2d；对落在图像范围内的有效高斯，"
        "用 grid_sample 在(下采样)器械 mask 上做双线性采样，得到该高斯所在像素的 mask 值作为遮挡率 rho in [0,1]。"
        "rho=0 表示该高斯处于可见组织区，rho=1 表示完全被器械覆盖。"
    )
    pdf.h3("梯度衰减")
    pdf.formula("grad' = grad * exp(-gamma * rho),   gamma = 2.0")
    pdf.body(
        "loss.backward() 之后、optimizer.step() 之前，对 control_xyz.grad 施加上式逐点衰减。"
        "exp 衰减保证 rho->1 时梯度趋于零(完全冻结被遮挡组织)，rho->0 时梯度不变(正常组织正常学习)，过渡平滑可导。"
        "这等价于在器械区域施加一个\"软冻结\"mask，比硬阈值更稳定。"
    )
    pdf.note(
        "代码路径: renderer/__init__.py:424 计算 mg_mas_overlap; gaussian_model.py:607 mg_mas_attenuate_gradients; "
        "train.py:791 在 fine+surgical 阶段调用衰减。注意衰减只作用于 control_xyz，器械自身的高斯属性仍正常更新。",
        kind="warn",
    )

    pdf.h2("4.3", "\u8fd0\u52a8\u7c7b\u578b\u81ea\u52a8\u5206\u7c7b")
    pdf.body(
        "系统对每个动态高斯计算四项几何指标并融合为\"器械似然\"，自动判定其属于 static / tissue / instrument 三类。"
        "该分类既用于可视化诊断，也为差异化优化提供先验。"
    )
    pdf.kv_table([
        ("motion_magnitude", "控制点折线总长 \u03a3\u2016p_{i+1}-p_i\u2016，表征运动幅度"),
        ("rigidity_score", "净位移/总路径 (直进度)，刚体直线运动趋近 1"),
        ("velocity_consistency", "各段速度幅值的一致性，匀速刚体趋近 1"),
        ("ccn_score", "1 - 归一化控制点数，控制点少 -> 更像刚体"),
    ])
    pdf.formula("instr_likelihood = 0.3*ccn + 0.3*rigidity + 0.2*vel_consist + 0.2*motion_score")
    pdf.body(
        "以 instr_likelihood 的中位数 + 0.5*MAD 作为自适应阈值，结合 motion_magnitude>0.05 的运动门控判定 is_instrument。"
        "再通过分别光栅化\"器械贡献图\"与\"组织贡献图\"，按逐像素 argmax 得到 motion_type_label (0/0.5/1.0 对应 static/tissue/instrument)。"
        "阈值自适应避免了手动调参对不同手术场景的脆弱性。"
    )

    # ============================== 5. CVD ==============================
    pdf.add_page()
    pdf.h1("5", "\u76f8\u673a\u4f4d\u59ff\u4e0e\u6df1\u5ea6\u5c3a\u5ea6\u8054\u5408\u4f30\u8ba1 (CVD)")
    pdf.body(
        "单目尺度-尺度模糊的本质：给定相对深度 d_rel 与未知位姿，无法确定绝对尺度。系统引入\"每帧尺度因子\" instance_scale，"
        "并以第 0 帧尺度为规范(canonical)，将相对深度乘以该因子得到规范视图深度 CVD："
    )
    pdf.formula("CVD_t = depth_t * instance_scale_t / instance_scale_0")
    pdf.body("CVD 与对应位姿 (R,t) 共同定义了一个尺度一致的几何框架，使不同帧的点云(points_from_DRTK)在统一尺度下可比。")
    pdf.h3("位姿网络结构 (scene/deformation.py)")
    pdf.kv_table([
        ("时间编码", "positional encoding: sin/cos(2^i t), i=0..timebase_pe-1 (默认 10) -> 21 维"),
        ("timenet0/1", "两层 MLP(256 宽, ReLU) 处理时间特征"),
        ("位姿输出", "线性层 -> 6 维: 前 3 维 Euler 角经 euler2mat 得 R, 后 3 维为平移 t"),
        ("尺度输出", "depth_scale_net_out 线性层 + 逐帧 instance_scale_list 参数(可学习)"),
        ("焦距", "focal_bias = log(500) 初始化的可学习标量, exp 得焦距, 与主点构成内参 K"),
    ])
    pdf.body(
        "位姿损失基于相邻帧的反向 warp：以 CVD 与 (R,t) 把参考帧图像/深度 warp 到目标帧，比较光度与重投影 3D 点一致性。"
        "为防止表示纠缠，warp 用到的 CVD 与 grid 在几何一致性损失中被 detach，仅位姿与深度被监督。"
        "warm-up 阶段额外用 CoTracker3 的像素轨迹(track loss)监督位姿，提供独立于外观的几何锚点。"
    )

    # ============================== 6. 损失体系 ==============================
    pdf.add_page()
    pdf.h1("6", "\u635f\u5931\u51fd\u6570\u4f53\u7cfb")
    pdf.body("总损失为多项加权和，分阶段启用，下式编号与 default.py 注释中的论文公式对应。")
    pdf.formula("L = L_rgb + L_pose + lambda_depth*L_depth + lambda_smooth*L_smooth + w_mask*L_mask + w_normal*L_normal + w_track*L_track")
    pdf.h2("6.1", "\u63a9\u819c\u5149\u5ea6\u635f\u5931 (Eq.8-9)")
    pdf.formula("L_rgb = L1(I*(1-M), I_gt*(1-M)) + lambda_ssim*(1 - SSIM(I*(1-M), I_gt*(1-M)))")
    pdf.body("M 为器械 motion_mask。在器械区域将光度损失置零，避免器械外观污染组织/位姿学习；lambda_ssim=0.2。warm-up 阶段对全图(去运动区)施加同形式损失。")
    pdf.h2("6.2", "\u4f4d\u59ff\u4e00\u81f4\u6027\u635f\u5931")
    pdf.body("由相邻帧反向 warp 构成，含 color loss(光度)、geometry loss(CVD 重投影 3D 一致性)与 SSIM 项，并经多级自适应掩膜过滤遮挡/大误差区域：")
    pdf.bullet("gs_mask: 渲染图与 GT 的颜色/深度一致性联合置信(用误差转概率 error_to_prob)")
    pdf.bullet("color_mask / geo_mask: 同一视角不同时刻的 warp 误差转概率")
    pdf.bullet("occ_mask (out_p/out_n): warp 后非零像素的可见性")
    pdf.bullet("fine 阶段额外引入基于 gsplat 深度的 warp 损失，强化位姿几何监督")
    pdf.h2("6.3", "\u5c3a\u5ea6-\u504f\u79fb\u4e0d\u53d8\u6df1\u5ea6\u635f\u5931 (Eq.10)")
    pdf.body("单目深度先验仅有相对意义，故对渲染深度做最小二乘尺度和偏移对齐后再与先验比较：")
    pdf.formula("min_{s,o}  \u03a3 w * (s*d_rend + o - d_prior)^2,  w = 1 - M (组织区高置信)")
    pdf.body("解析解 s=(\u03a3w\u03a3wdp-\u03a3wd\u03a3wp)/(\u03a3w\u03a3wdd-(\u03a3wd)^2), o=(\u03a3wp-s\u03a3wd)/\u03a3w。置信权重 w 在器械区置低，避免器械破坏深度对齐。")
    pdf.h2("6.4", "\u8f68\u8ff9\u5e73\u6ed1\u635f\u5931 (Eq.11)")
    pdf.body("对每条样条在 [0,1] 上采样 time_grid 个点，用中心差分求二阶导(加速度)并惩罚其范数平方：")
    pdf.formula("L_smooth = (1/N) \u03a3_g mean( || x(t_{i+1}) - 2x(t_i) + x(t_{i-1}) ||^2 )")
    pdf.body("该项抑制控制点抖动、保证轨迹时空连续性，对去除内窥镜高频噪声引起的轨迹毛刺尤为有效。仅对有效控制点数>=4 的高斯施加。")
    pdf.h2("6.5", "\u63a9\u819c / \u6cd5\u7ebf / \u8ffd\u8e2a \u635f\u5931")
    pdf.kv_table([
        ("L_mask", "w_mask * BinaryDiceLoss(d_alpha, M): 监督动态 alpha 通道与器械 mask 一致"),
        ("L_normal", "w_normal * L2(n_pred, n_gt, mask=M): 从渲染深度求法线监督几何(w_normal 手术默认 0)"),
        ("L_track", "w_track * (grid_sample(p_grid,track)-track_prev)^2 + (...): 仅 warm-up, CoTracker 轨迹监督位姿"),
    ])

    # ============================== 7. 训练流程 ==============================
    pdf.add_page()
    pdf.h1("7", "\u8bad\u7ec3\u6d41\u7a0b\u4e0e\u4f18\u5316\u52a8\u529b\u5b66")
    pdf.body("采用三阶段课程式优化，逐级解锁参数子集，缓解位姿-表示-外观的耦合非凸性。")
    pdf.h2("7.1", "Stage 1: Warm-up (\u9884\u70ed)")
    pdf.bullet("目标: 估计相机位姿、焦距、深度尺度因子; 高斯尚未初始化")
    pdf.bullet("活跃参数: pose_network(MLP + instance_scale) + focal_bias")
    pdf.bullet("损失: 光度 warp 一致性 + track loss(CoTracker 监督) + 几何一致性")
    pdf.bullet("结束动作: 由 CVD 与位姿反解点云(points_from_DRTK)初始化静态/动态高斯点云(stat/dyn_npts=30000)")
    pdf.h2("7.2", "Stage 2: Fine-static (\u9759\u6001\u7cbe\u8c03)")
    pdf.bullet("目标: 仅优化静态高斯, 冻结动态部分")
    pdf.bullet("以 motion mask 屏蔽动态区损失, 对静态高斯做 densification 与 pruning")
    pdf.h2("7.3", "Stage 3: Fine (\u8054\u5408\u7cbe\u8c43)")
    pdf.bullet("联合优化动态/静态高斯 + pose_network + RGB decoder, 共 30000 迭代")
    pdf.bullet("每步采样 batch_size 个目标视角, 各配一个前向/后向参考帧用于 warp 损失")
    pdf.bullet("动态高斯 densification(更松阈值 8e-5) + 控制点 onedown 剪枝")
    pdf.bullet("手术分支: 启用 TASS 分裂检测(每 100 迭代) + MG-MAS 梯度衰减 + depth/smooth 损失")
    pdf.note(
        "学习率采用指数衰减(position/deformation/pose 各有 init->final 与 delay_mult), SH 每 1000 迭代升一阶(上限 3 阶), "
        "opacity 每 3000 迭代重置以防止饱和。densification 在 iter 500..15000 间每 100 步执行, 之后仅 pruning。"
    )

    # ============================== 8. 渲染 ==============================
    pdf.add_page()
    pdf.h1("8", "\u6e32\u67d3\u7ba1\u7ebf")
    pdf.body("基于 gsplat 的 tile-based 可微光栅化，支持 RGB+ED(颜色+深度) 模式与多通道并行光栅化。")
    pdf.h3("单步渲染流水线")
    steps = [
        "对动态高斯做 Hermite 插值得到当前时刻位移, 计算最终位置 means3D = x_base + s*interp",
        "激活函数: scale=exp(_scaling), opacity=sigmoid(_opacity), rotation=normalize(_rotation)",
        "SH 时变特征: features = concat(_features_dc, delta_t * _features_t)",
        "动静高斯属性 cat 拼接 -> 单个大张量送入 gsplat rasterization(RGB+ED)",
        "gsplat 输出临时颜色 + 深度 + means2d(保留梯度用于 densification)",
        "临时颜色经 RGB decoder(MLP, 输入含 cam_ray 视角方向) -> 视角相关最终 RGB",
        "并行光栅化 d_alpha(动态区指示)、nc_heatmap(控制点数)、instrument/tissue 贡献图",
        "由各类贡献图逐像素 argmax 得 motion_type_label 输出",
    ]
    for i, s in enumerate(steps, 1):
        pdf.num_item(i, s)
    pdf.h3("RGB Decoder 的设计意义")
    pdf.body(
        "gsplat 直接输出的颜色是中间表示, 经轻量 MLP(含相机光线方向 cam_ray)解码为最终 RGB, 使颜色具备视角依赖性(view-dependent)。"
        "这与球谐函数(SH)的角色互补: SH 编码高频视角变化, decoder 提供非线性映射能力, 二者协同表达内窥镜强高光/镜面反射下的外观。"
    )

    # ============================== 9. 双环境流水线 ==============================
    pdf.add_page()
    pdf.h1("9", "\u53cc\u73af\u5883\u6570\u636e\u9884\u5904\u7406\u6d41\u6c34\u7ebf")
    pdf.body("因深度估计模型与主训练框架的 CUDA/PyTorch 版本不兼容，系统采用两个独立 conda 环境。")
    pdf.kv_table([
        ("Env-2 (unidepth)", "Python 3.10, CUDA 12.1, PyTorch 2.4 -> UniDepth + Depth-Anything"),
        ("Env-1 (main)", "Python 3.7, CUDA 11.7, PyTorch 1.13.1 -> CoTracker3 + 训练"),
        ("UniDepth", "通用单目度量深度估计, 提供带绝对尺度的 depth(--depth_type depth)"),
        ("Depth-Anything", "鲁棒单目视差估计, 提供视差 disp(--depth_type disp) 作为备选/补充"),
        ("CoTracker3", "长程点跟踪, 在全部帧上生成密集/稀疏像素轨迹作为运动监督"),
    ])
    pdf.h3("为何需要两种深度源")
    pdf.body(
        "UniDepth 提供度量深度，理论上可定尺度，但在内窥镜近焦/弱纹理场景易失效；Depth-Anything 视差更鲁棒但无尺度。"
        "系统通过 depth_type 切换并配合 CVD 的 instance_scale 学习，使两种来源都能被纳入尺度一致的优化框架，提升几何初始化的鲁棒性。"
    )
    pdf.note("工程上需分别编译 UniDepth 的 KNN/extract_patches CUDA 算子(compile.sh), 并下载 Depth-Anything ViT-L 检查点至指定目录。")

    # ============================== 10. 工程实现 ==============================
    pdf.add_page()
    pdf.h1("10", "\u5de5\u7a0b\u5b9e\u73b0\u4e0e\u5173\u952e\u8d85\u53c2")
    pdf.h2("10.1", "\u624b\u672f\u914d\u7f6e (arguments/surgical/default.py)")
    pdf.kv_table([
        ("control_num", "6 (通用 12)"),
        ("tass_epsilon (eps_top)", "0.05  光度误差触发阈值"),
        ("tass_gamma", "2.0  MG-MAS 梯度衰减系数"),
        ("lambda_depth_consistency", "0.5  尺度对齐深度损失权重"),
        ("lambda_traj_smoothness", "0.1  轨迹加速度惩罚权重"),
        ("lambda_masked_rgb / lambda_ssim", "1.0 / 0.2"),
        ("iterations / coarse / static", "30000 / 2000 / 2000"),
        ("stat_npts / dyn_npts", "30000 / 30000  初始点数"),
        ("densify_grad_threshold (_dynamic)", "0.0008 / 0.00008  动态更松"),
        ("prune_error_threshold", "0.5 (通用 1.0)  控制点剪枝容差"),
    ])
    pdf.h2("10.2", "\u5173\u952e\u5de5\u7a0b\u7ec6\u8282")
    pdf.bullet("梯度分流: 渲染时动静高斯 cat, 反传后按 no_stat_gs 切片分别累积 viewspace 梯度与 densification 统计, 避免互相污染")
    pdf.bullet("mask 采样一致性: MG-MAS 与 TASS 共用同一份 mg_mas_overlap 张量, 前者用于梯度衰减, 后者复用为误差代理, 节省一次投影")
    pdf.bullet("detach 防纠缠: 几何一致性损失中 CVD/grid 被 detach, 仅位姿/深度受监督, 防止表示互相作弊")
    pdf.bullet("TASS 触发频率: 每 100 迭代检测一次, 配合 3 帧连续计数, 兼顾响应性与抗噪")
    pdf.bullet("内存: trajectory_smoothness_loss 按高斯循环采样, 大规模点云下需关注开销; 控制点剪枝可缓解")

    # ============================== 11. 评估 ==============================
    pdf.add_page()
    pdf.h1("11", "\u8bc4\u4f30\u6307\u6807\u4f53\u7cfb")
    pdf.body("系统提供两类评估: 通用重建质量(Nvidia RoDynRF)与手术专用动态质量(EndoNeRF/自定义)。")
    pdf.h2("11.1", "\u901a\u7528\u6307\u6807")
    pdf.kv_table([
        ("PSNR / SSIM / LPIPS", "新视角合成质量标准三件套"),
        ("渲染 FPS", "RTX 3090 实测 >30 FPS, 满足实时性"),
        ("训练耗时", "单场景约 30 分钟级"),
    ])
    pdf.h2("11.2", "\u624b\u672f\u52a8\u6001\u4e13\u7528\u6307\u6807")
    pdf.kv_table([
        ("tOF (temporal Optical Flow)", "相邻帧预测光流与 GT 光流的一致性, 衡量时序连贯"),
        ("g_def / g_split (global def/split)", "动态/分裂区域的几何一致性, 反映形变与拓扑变化刻画质量"),
        ("FAS (Flow Acceleration Smoothness)", "光流加速度平滑性, 检测轨迹抖动"),
        ("MASE", "Mean Absolute Scaled Error, 尺度归一误差, 对单目尺度鲁棒(compute_mase.py)"),
    ])
    pdf.body("评估脚本: eval_nvidia.py / eval.sh (Nvidia), run_eval.sh + compute_metrics.py (手术综合指标), compute_mase.py (MASE)。")
    pdf.h3("可视化诊断")
    pdf.bullet("gen_heatmap.py: 渲染运动幅值/直进度/速度一致性/运动类型热图")
    pdf.bullet("gen_split_figures.py: 从训练日志解析 TASS 分裂事件并可视化")

    # ============================== 12. 实验结论 ==============================
    pdf.add_page()
    pdf.h1("12", "\u5b9e\u9a8c\u7ed3\u679c\u4e0e\u6d88\u878d")
    pdf.h2("12.1", "\u4e3b\u8981\u7ed3\u8bba")
    pdf.bullet("在 Nvidia RoDynRF 多场景上 PSNR/SSIM 领先 RoDynRF、K-Planes、HexPlane、T-NeRF、4DGS 等基线")
    pdf.bullet("Hermite 样条优于线性插值与多项式拟合, 在轨迹平滑性与表达力间取得更好平衡")
    pdf.bullet("自适应控制点剪枝显著降低表示冗余, 刚性区域控制点大幅压缩而质量不降")
    pdf.bullet("动静解耦显著提升静态背景渲染质量, 避免相机运动被误建模为场景形变")
    pdf.bullet("CVD + 位姿一致性损失是单目位姿估计稳定的关键, 配合 track loss 提供几何锚点")
    pdf.h2("12.2", "\u6838\u5fc3\u6d88\u878d")
    pdf.num_item("1", "TASS 关闭: 组织切割区域出现持续光度误差与轨迹畸变, 证实拓扑分裂的必要性")
    pdf.num_item("2", "MG-MAS 关闭: 器械进出时组织轨迹被错误牵扯, 动态 alpha 与 mask 一致性下降")
    pdf.num_item("3", "运动分类: 提供可解释的动静/组织-器械划分, 并支撑差异化优化")
    pdf.num_item("4", "深度源切换: UniDepth 失效场景下 Depth-Anything 视差 + CVD 仍可维持几何收敛")

    # ============================== 13. 局限 ==============================
    pdf.add_page()
    pdf.h1("13", "\u5c40\u9650\u6027\u3001\u98ce\u9669\u4e0e\u672a\u6765\u5de5\u4f5c")
    pdf.h2("13.1", "\u5f53\u524d\u5c40\u9650")
    pdf.bullet("单目本质模糊: 极端尺度漂移仍可能发生, 依赖 instance_scale 的可学习性而非物理约束")
    pdf.bullet("拓扑分裂粒度: TASS 以单高斯分裂建模切割, 对大面积连续切割的边缘认知有限")
    pdf.bullet("长序列漂移: Hermite 样条为整体序列拟合, 超长视频可能累积漂移, 缺乏滑动窗口/分段机制")
    pdf.bullet("双环境部署成本: 两套 CUDA/PyTorch 环境增加工程复杂度, 不利于一体化部署")
    pdf.bullet("计算开销: 平滑损失逐高斯循环、多次并行光栅化(alpha/nc/instrument/tissue)增加显存与时间")
    pdf.bullet("真值依赖: 评估依赖 motion mask 与深度先验质量, 弱纹理/强反光场景先验退化直接影响结果")
    pdf.h2("13.2", "\u5de5\u7a0b\u5316\u98ce\u9669")
    pdf.bullet("数值稳定: 损失含多级 error_to_prob 概率掩膜, 极端帧易致 NaN, 已有显式 NaN 检测与退出")
    pdf.bullet("显存峰值: densification 期点云膨胀 + 多光栅化通道, 长视频需控制 batch 与初始点数")
    pdf.bullet("可复现性: 控制 TASS/gamma 等超参与随机种子, 建议固化 config 并记录 split 事件日志")
    pdf.h2("13.3", "\u672a\u6765\u65b9\u5411")
    pdf.num_item("1", "引入物理约束(组织力学/器械运动学先验)正则化轨迹, 缓解尺度与漂移")
    pdf.num_item("2", "TASS 升级为边级/面级拓扑感知, 结合语义分割刻画切割边界")
    pdf.num_item("3", "滑动窗口样条或样条拼接, 支持长视频与在线增量重建")
    pdf.num_item("4", "统一深度模型环境, 探索蒸馏/量化以降低部署门槛")
    pdf.num_item("5", "与 SLAM/位姿图优化耦合, 提升长程位姿一致性")

    # ============================== 14. 结论 ==============================
    pdf.add_page()
    pdf.h1("14", "\u7ed3\u8bba")
    pdf.body(
        "Surgical-TSplineGS 的核心贡献在于将动态场景的轨迹建模从隐式神经场回归到显式几何样条, "
        "由此打开了\"按运动复杂度分配表示预算\"\"感知拓扑突变并分裂轨迹\"\"以器械掩膜软冻结组织梯度\"等只能在显式表示上进行的操作空间。"
        "TASS 与 MG-MAS 分别直击内窥镜场景的组织切割与器械遮挡两大痛点, CVD 机制则在单目尺度模糊下提供了可优化的尺度一致框架。"
        "整体上, 该系统在表示理论、几何先验融合与可微渲染三个层面形成了自洽闭环, 兼具新视角合成质量与实时性能, "
        "为术中动态三维重建提供了有工程落地潜力的技术路径。其当前局限(单目本质模糊、长序列漂移、双环境部署成本)亦清晰指向了"
        "物理先验融入、拓扑语义升级与在线增量重建等值得继续推进的研究方向。"
    )
    pdf.ln(3)
    pdf.note(
        "\u6d89\u53ca\u6587\u4ef6: train.py, scene/gaussian_model.py, scene/deformation.py, "
        "gaussian_renderer/__init__.py, utils/loss_utils.py, arguments/surgical/default.py; "
        "\u53ef\u89c6\u5316: gen_heatmap.py, gen_split_figures.py; \u8bc4\u4f30: eval_nvidia.py, compute_metrics.py, compute_mase.py; "
        "\u9879\u76ee: github.com/chenqi111/Surgical-TSplineGS"
    )
    pdf.ln(2)
    pdf.set_font("Serif", "I", 8.5)
    pdf.set_text_color(150, 150, 150)
    pdf.multi_cell(0, 5,
        "\u514d\u8d23\u58f0\u660e: \u672c\u62a5\u544a\u57fa\u4e8e\u6e90\u7801\u5b9e\u8bc1\u5206\u6790\u7f16\u5199, "
        "\u6570\u5b66\u8868\u8ff0\u4e0e\u5b9e\u73b0\u7ec6\u8282\u5747\u4e0e\u4ee3\u7801\u5bf9\u5e94; "
        "\u5b9e\u9a8c\u6570\u503c\u4e3a\u9879\u76ee\u63cf\u8ff0\u4e0e\u914d\u7f6e\u63a8\u65ad, "
        "\u5177\u4f53\u590d\u73b0\u4ee5\u5b9e\u9645\u8bad\u7ec3\u4e3a\u51c6\u3002"
    )

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Surgical_TSplineGS_Tech_Report.pdf")
    pdf.output(out)
    print(f"PDF generated: {out}")
    print(f"Pages: {pdf.page_no()}")


if __name__ == "__main__":
    build()
