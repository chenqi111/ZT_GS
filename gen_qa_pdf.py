#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Surgical-TSplineGS 四问四答 PDF —— 通俗易懂版，标注代码来源。"""

from fpdf import FPDF
import os

FONT_REG = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FONT_BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
NAVY = (0, 51, 102)
STEEL = (31, 73, 125)
DGREY = (40, 40, 40)
LIGHT = (238, 242, 248)
CODE_BG = (244, 246, 249)
Q_BG = (229, 242, 255)
A_BD = (0, 102, 204)


class QAPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font("Noto", "", FONT_REG)
        self.add_font("Noto", "B", FONT_BOLD)
        self.add_font("Noto", "I", FONT_REG)
        self.add_font("Mono", "", FONT_MONO)

    def footer(self):
        self.set_y(-12)
        self.set_font("Noto", "", 7.5)
        self.set_text_color(140, 140, 140)
        self.cell(0, 5, f"\u7b2c {self.page_no()} \u9875", align="R")

    def q_block(self, num, text):
        self.ln(3)
        self.set_fill_color(*Q_BG)
        self.set_draw_color(*A_BD)
        self.set_font("Noto", "B", 12)
        self.set_text_color(*NAVY)
        self.set_x(10)
        self.multi_cell(0, 7.5, f"Q{num}.  {text}", border=1, fill=True)
        self.ln(2)

    def body(self, text):
        self.set_font("Noto", "", 10.2)
        self.set_text_color(*DGREY)
        self.multi_cell(0, 6.2, text)
        self.ln(1.5)

    def lead(self, text):
        self.set_font("Noto", "B", 10.5)
        self.set_text_color(*STEEL)
        self.multi_cell(0, 6.4, text)
        self.ln(0.5)

    def bullet(self, text, indent=6):
        self.set_font("Noto", "", 10.2)
        self.set_text_color(*DGREY)
        self.set_x(self.get_x() + indent)
        self.cell(4, 6.2, "\u25aa")
        self.multi_cell(0, 6.2, text)
        self.ln(0.8)

    def code(self, text):
        self.set_font("Mono", "", 8)
        self.set_text_color(35, 45, 60)
        self.set_fill_color(*CODE_BG)
        self.ln(1)
        for line in text.split("\n"):
            self.set_x(13)
            self.cell(0, 4.4, line if line else " ", fill=True)
            self.ln(4.4)
        self.ln(1.5)

    def src(self, text):
        self.set_font("Noto", "I", 8.6)
        self.set_text_color(120, 120, 120)
        self.set_x(12)
        self.multi_cell(0, 5, "\u4ee3\u7801\u51fa\u5904\uff1a" + text)
        self.ln(1)

    def verdict(self, text):
        self.set_fill_color(245, 250, 240)
        self.set_draw_color(90, 140, 60)
        self.set_font("Noto", "B", 10)
        self.set_text_color(60, 100, 40)
        self.ln(1)
        self.set_x(10)
        self.multi_cell(0, 6, "\u4e00\u53e5\u7ed3\u8bba\uff1a" + text, border=1, fill=True)
        self.ln(3)


def build():
    pdf = QAPDF()
    pdf.set_auto_page_break(auto=True, margin=16)

    # ---- 封面 ----
    pdf.add_page()
    pdf.ln(26)
    pdf.set_draw_color(*NAVY)
    pdf.set_line_width(0.5)
    pdf.rect(14, 28, 182, 78)
    pdf.ln(18)
    pdf.set_font("Noto", "B", 26)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 13, "Surgical-TSplineGS", align="C")
    pdf.ln(15)
    pdf.set_font("Noto", "B", 14)
    pdf.set_text_color(*STEEL)
    pdf.cell(0, 8, "\u56db\u4e2a\u5173\u952e\u95ee\u9898\u7684\u901a\u4fd7\u89e3\u8bfb", align="C")
    pdf.ln(9)
    pdf.set_font("Noto", "", 11)
    pdf.set_text_color(*DGREY)
    pdf.cell(0, 7, "COLMAP-free?  \u5185\u53c2?  \u521d\u59cb\u9ad8\u65af?  \u5148\u9a8c?", align="C")
    pdf.ln(22)
    pdf.set_font("Noto", "", 10)
    pdf.set_text_color(110, 110, 110)
    pdf.cell(0, 6, "\u2014\u2014 \u57fa\u4e8e\u6e90\u7801\u5b9e\u8bc1\uff0c\u6bcf\u6761\u7ed3\u8bba\u5747\u9644\u4ee3\u7801\u51fa\u5904", align="C")
    pdf.ln(10)
    pdf.set_font("Noto", "I", 9)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 6, "\u4f9b\u4e0e\u590f\u8001\u5e08\u6c9f\u901a\u4f7f\u7528", align="C")

    # ---- 引言 ----
    pdf.add_page()
    pdf.lead("\u5199\u5728\u524d\u9762")
    pdf.body(
        "\u8fd9\u4efd\u6750\u6599\u4e13\u95e8\u56de\u7b54\u590f\u8001\u5e08\u63d0\u51fa\u7684\u56db\u4e2a\u95ee\u9898\u3002"
        "\u4e3a\u4e86\u8ba9\u4e0d\u719f\u6089\u4ee3\u7801\u7ec6\u8282\u7684\u4eba\u4e5f\u80fd\u8bfb\u61c2\uff0c\u6211\u4eec\u7528\u201c\u767d\u8bdd\u201d\u8bb2\u6e05\u695a\u539f\u7406\uff0c"
        "\u5e76\u5728\u6bcf\u6761\u7ed3\u8bba\u540e\u7ed9\u51fa\u5bf9\u5e94\u7684\u4ee3\u7801\u6587\u4ef6\u548c\u884c\u53f7\uff0c\u65b9\u4fbf\u6838\u67e5\u3002"
        "\u6240\u6709\u7ed3\u8bba\u90fd\u662f\u4ece\u6e90\u7801\u91cc\u5b9e\u8bc1\u51fa\u6765\u7684\uff0c\u4e0d\u662f\u731c\u7684\u3002"
    )

    # ---- Q1 ----
    pdf.add_page()
    pdf.q_block("1", "\u8fd9\u4e2a\u9879\u76ee\u5b8c\u5168\u662f COLMAP-free \u5417\uff1f\u9700\u4e0d\u9700\u8981\u5148\u9a8c\uff1f")

    pdf.lead("\u76f4\u63a5\u7ed3\u8bba\uff1a\u514d COLMAP\uff0c\u4f46\u4e0d\u514d\u201c\u5148\u9a8c\u201d")
    pdf.body(
        "\u5148\u8bf4\u6e05 COLMAP \u5728\u4f20\u7edf 3DGS \u91cc\u5e72\u4ec0\u4e48\u3002COLMAP \u4e00\u822c\u63d0\u4f9b\u4e24\u6837\u4e1c\u897f\uff1a"
        "(1) \u6bcf\u5e20\u56fe\u7684\u76f8\u673a\u4f4d\u59ff\uff08SfM \u4f30\u8ba1\uff09\uff1b"
        "(2) \u4e00\u4e2a\u7a00\u758f 3D \u70b9\u4e91\uff08MVS \u91cd\u5efa\uff09\u3002"
        "\u4f20\u7edf 3DGS \u5fc5\u987b\u5148\u8dd1\u4e00\u904d COLMAP\uff0c\u62ff\u5230\u8fd9\u4e24\u6837\u624d\u80fd\u5f00\u59cb\u8bad\u7ec3\u3002"
    )
    pdf.body(
        "\u672c\u9879\u76ee\u628a\u8fd9\u4e24\u6837\u90fd\u66ff\u6362\u6389\u4e86\uff0c\u6240\u4ee5\u53eb COLMAP-free\uff1a"
        "\u76f8\u673a\u4f4d\u59ff \u2192 \u7528\u4e00\u4e2a\u5c0f\u795e\u7ecf\u7f51\u7edc\uff08pose_network\uff09\u4ece\u96f6\u5f00\u59cb\u5b66\u51fa\u6765\uff1b"
        "\u521d\u59cb\u70b9\u4e91 \u2192 \u7528\u5355\u76ee\u6df1\u5ea6\u4f30\u8ba1\u7684\u7ed3\u679c\u53cd\u63a8\u51fa\u6765\u3002"
        "\u6e90\u7801\u91cc\u76f4\u63a5\u6709\u6ce8\u91ca\u5199\u7740 \"Identity camera (COLMAP-free, optimized via pose_network)\"\u3002"
    )
    pdf.src("scene/dataset_readers.py:622\uff08\u624b\u672f\u573a\u666f\uff09\u3001:378\uff08Nvidia \u573a\u666f\uff09\u5747\u4e3a C2W = np.eye(4)\uff0c\u5355\u4f4d\u9635\u8d77\u6b65")

    pdf.body(
        "\u4f46\u201c\u514d COLMAP\u201d\u4e0d\u7b49\u4e8e\u201c\u4ec0\u4e48\u90fd\u4e0d\u9700\u8981\u201d\u3002"
        "\u5b83\u4ecd\u7136\u9700\u8981\u4e24\u7c7b\u5148\u9a8c\u4f5c\u4e3a\u76d1\u7763\u4fe1\u606f\uff1a"
    )
    pdf.bullet("\u5355\u76ee\u6df1\u5ea6\u5148\u9a8c\uff1aUniDepth\uff08\u5e26\u7edd\u5bf9\u5c3a\u5ea6\uff09\u6216 Depth-Anything\uff08\u53ea\u6709\u89c6\u5dee\uff09\u9884\u5904\u7406\u6bcf\u5e40\u56fe")
    pdf.bullet("\u70b9\u8f68\u8ff9\u5148\u9a8c\uff1aCoTracker3 \u5728\u6574\u6bb5\u89c6\u9891\u4e0a\u8ffd\u8e2a\u5bc6\u96c6\u70b9\u7684 2D \u8f68\u8ff9")
    pdf.body(
        "\u6362\u53e5\u8bdd\u8bf4\uff1a\u5b83\u628a COLMAP \u90a3\u5957\u201c\u51e0\u4f55\u91cd\u5efa\u6d41\u6c34\u7ebf\u201d\u6362\u6210\u4e86\u201c\u6df1\u5ea6\u7f51\u7edc + \u70b9\u8ddf\u8e2a\u7f51\u7edc\u201d\uff0c"
        "\u4e8e\u662f\u4e0d\u9700\u8981\u5728\u8bad\u7ec3\u524d\u8dd1 COLMAP\u3002"
        "\u4f46\u8fd9\u4e9b\u7f51\u7edc\u672c\u8eab\u662f\u5728\u5916\u90e8\u5927\u6570\u636e\u4e0a\u9884\u8bad\u7ec3\u8fc7\u7684\uff0c\u6240\u4ee5\u5148\u9a8c\u662f\u201c\u6362\u4e86\u4e2a\u5730\u65b9\u5b58\u7740\u201d\uff0c\u4e0d\u662f\u201c\u51ed\u7a7a\u6d88\u5931\u201d\u3002"
    )
    pdf.src("README.md \u63cf\u8ff0\u4e86\u53cc\u73af\u5883\u6d41\u6c34\u7ebf\uff1agen_depth.sh\uff08UniDepth/Depth-Anything\uff09\u3001gen_tracks.sh\uff08CoTracker3\uff09")

    pdf.verdict("\u662f COLMAP-free\uff0c\u4f46\u5e76\u975e prior-free\u3002\u5b83\u7528\u5b66\u4e60\u578b\u51e0\u4f55\u5148\u9a8c\u66ff\u4ee3\u4e86 COLMAP\u3002")

    # ---- Q2 ----
    pdf.add_page()
    pdf.q_block("2", "\u5185\u53c2\uff08\u7126\u8ddd/\u4e3b\u70b9\uff09\u662f\u6807\u5b9a\u6765\u7684\u8fd8\u662f\u4f18\u5316\u6765\u7684\uff1f")

    pdf.lead("\u7b54\uff1a\u4e0d\u662f\u79bb\u7ebf\u6807\u5b9a\uff0c\u662f\u201c\u81ea\u6807\u5b9a\u201d\u2014\u2014\u7126\u8ddd\u9760\u5b66\uff0c\u4e3b\u70b9\u7eaf\u731c")
    pdf.body(
        "\u5148\u8bb2\u7126\u8ddd\u3002\u4ee3\u7801\u91cc\u6709\u4e00\u4e2a\u53eb focal_bias \u7684\u53ef\u5b66\u4e60\u53c2\u6570\uff0c"
        "\u5b83\u521d\u59cb\u5316\u6210 log(500)\uff0c\u4e5f\u5c31\u662f\u8bf4\u7126\u8ddd\u521d\u503c = exp(log(500)) = 500\uff0c\u8fd9\u53ea\u662f\u4e2a\u5360\u4f4d\u7b26\u3002"
        "\u7136\u540e\u5728\u8bad\u7ec3\u8fc7\u7a0b\u4e2d\uff0c\u8fd9\u4e2a\u53c2\u6570\u4f1a\u968f\u7740\u635f\u5931\u4e00\u8d77\u88ab\u68af\u5ea6\u4e0b\u964d\u3001\u4e00\u8d77\u66f4\u65b0\u2014\u2014\u5c31\u662f\u201c\u5b66\u51fa\u6765\u7684\u201d\u3002"
        "\u6bcf\u4e00\u6b65\u8bad\u7ec3\u90fd\u4f1a\u7528\u5f53\u524d\u5b66\u5230\u7684\u7126\u8ddd\u91cd\u65b0\u8bbe\u7f6e\u76f8\u673a\u7684\u6295\u5f71\u77e9\u9635\u3002"
    )
    pdf.code(
        "# scene/deformation.py:51\n"
        "self.focal_bias = nn.Parameter(torch.ones(1) * math.log(500), requires_grad=True)\n"
        "# => focal = exp(focal_bias), init=500, learned during training\n\n"
        "# train.py:347 (refresh camera with learned focal each step)\n"
        "viewpoint_cam.update_cam(..., focal=dyn_gaussians._posenet.focal_bias.exp())"
    )
    pdf.body(
        "\u518d\u8bb2\u4e3b\u70b9\uff08\u56fe\u50cf\u4e2d\u5fc3\u70b9\uff09\u3002\u8fd9\u4e2a\u9879\u76ee\u6ca1\u6709\u6807\u5b9a\u4e3b\u70b9\uff0c"
        "\u800c\u662f\u76f4\u63a5\u5047\u5b9a\u4e3b\u70b9\u5c31\u5728\u56fe\u50cf\u4e2d\u5fc3\uff0c\u5373 (width/2, height/2)\u3002"
        "\u8fd9\u662f\u4e2a\u201c\u7406\u60f3\u5316\u5047\u8bbe\u201d\uff0c\u771f\u5b9e\u5185\u7a91\u955c\u5934\u5982\u679c\u6709\u504f\u5fc3/\u7578\u53d8\uff0c\u8fd9\u91cc\u4f1a\u6709\u7cfb\u7edf\u8bef\u5dee\u3002"
        "\u4f46\u5bf9\u5185\u7a91\u8fd9\u79cd\u8fd1\u4e4e\u9488\u5b54\u3001\u955c\u5934\u4e0d\u53ef\u6362\u7684\u573a\u666f\uff0c\u8fd9\u4e2a\u5047\u8bbe\u5f88\u5408\u7406\uff0c\u4e5f\u662f\u4e1a\u754c\u5e38\u89c1\u505a\u6cd5\u3002"
    )
    pdf.code(
        "# scene/dataset_readers.py:635 (surgical) / :392 (nvidia)\n"
        "principal_point = np.array([sh[1] / 2.0, sh[0] / 2.0])  # image center\n"
        "\n"
        "# scene/dataset_readers.py:598\n"
        "focal_length = 500  # dummy initial, optimized via pose_network"
    )
    pdf.verdict("\u7126\u8ddd\u662f\u7aef\u5230\u7aef\u5b66\u51fa\u6765\u7684\uff08\u4e0d\u662f\u6807\u5b9a\uff09\uff1b\u4e3b\u70b9\u786c\u7f16\u4e3a\u56fe\u50cf\u4e2d\u5fc3\uff08\u7406\u60f3\u5316\u5047\u8bbe\uff09\u3002")

    # ---- Q3 ----
    pdf.add_page()
    pdf.q_block("3", "\u521d\u59cb\u7684 3DGS \u600e\u4e48\u6765\u7684\uff1f\u968f\u673a\u521d\u59cb\u8fd8\u662f\u6df1\u5ea6/\u8ddf\u8e2a\u70b9\u6295\u5f71\uff1f")

    pdf.lead("\u7b54\uff1a\u4e0d\u662f\u968f\u673a\uff0c\u662f\u201c\u6df1\u5ea6\u53cd\u63a8 + \u8ddf\u8e2a\u70b9\u8d4b\u8f68\u201d\u4e24\u6b65\u6784\u9020")
    pdf.body(
        "\u5148\u770b\u52a0\u8f7d\u9636\u6bb5\u3002\u6570\u636e\u52a0\u8f7d\u65f6\u5b58\u7684 PLY \u70b9\u4e91\u5176\u5b9e\u53ea\u6709 1 \u4e2a\u539f\u70b9\uff0c\u662f\u4e2a\u5360\u4f4d\u7b26\uff0c\u4e0d\u662f\u771f\u70b9\u4e91\u3002"
    )
    pdf.code(
        "# scene/dataset_readers.py:663 (surgical)\n"
        "xyz = np.zeros((1, 3))   # only 1 point, placeholder\n"
        "rgb = np.zeros((1, 3))\n"
        "storePly(ply_path, ...)"
    )
    pdf.body(
        "\u771f\u6b63\u7684\u521d\u59cb\u5316\u53d1\u751f\u5728 warm-up\uff08\u9884\u70ed\uff09\u9636\u6bb5\u7ed3\u675f\u65f6\u3002\u8fd9\u65f6 pose_network \u5df2\u7ecf\u5b66\u4e86\u4f4d\u59ff\u3001\u7126\u8ddd\u3001\u6df1\u5ea6\u5c3a\u5ea6\uff0c"
        "\u7136\u540e\u7528\u8fd9\u4e9b\u5b66\u5230\u7684\u91cf\u628a\u6df1\u5ea6\u56fe\u53cd\u63a8\u6210 3D \u70b9\u4e91\u3002\u8fd9\u5c31\u662f\u201c\u6df1\u5ea6\u53cd\u63a8\u201d\u3002"
    )
    pdf.code(
        "# train.py:1068 (build point cloud at end of warm-up)\n"
        "points = deformation.points_from_DRTK(CVD, w2c_target, K_tensor)\n"
        "# CVD = depth_prior * learned_scale_factor, back-projected to 3D"
    )
    pdf.body(
        "\u63a5\u4e0b\u6765\u662f\u201c\u8ddf\u8e2a\u70b9\u8d4b\u8f68\u201d\u3002\u4e0a\u4e00\u6b65\u53cd\u63a8\u51fa\u6765\u7684\u662f\u9759\u6001 3D \u70b9\uff1b"
        "\u5bf9\u52a8\u6001\u70b9\uff0c\u7cfb\u7edf\u7528 CoTracker3 \u7684 2D \u8f68\u8ff9\u628a\u6bcf\u4e2a\u52a8\u6001\u70b9\u5728\u5404\u5e27\u7684\u4f4d\u7f6e\u4e32\u6210\u4e00\u6761\u65f6\u95f4\u8f68\u8ff9\uff0c"
        "\u8fd9\u5c31\u5f97\u5230\u4e86\u52a8\u6001\u9ad8\u65af\u7684\u521d\u59cb\u8f68\u8ff9\uff08\u540e\u7eed\u518d\u7528 Hermite \u6837\u6761\u7ec6\u5316\uff09\u3002"
    )
    pdf.code(
        "# train.py:1120-1146 (assign CoTracker trajectories to dynamic pts)\n"
        "tracklet = viewpoint_stack[0].target_tracks        # CoTracker3 2D tracks\n"
        "dyn_tracklet_index = ...argmin(-1)                  # match dyn pts to tracks\n"
        "dyn_tracjectory = grid_sample(points_list, ...)    # sample 3D pos along tracks"
    )
    pdf.body(
        "\u800c\u4e14\u9759\u6001/\u52a8\u6001\u70b9\u7684\u5212\u5206\u4e5f\u4e0d\u662f\u968f\u673a\u7684\uff1a"
        "\u7528\u201c\u7d2f\u8ba1\u5149\u5ea6\u8bef\u5dee + \u5668\u68b0\u906e\u6321 mask\u201d\u6765\u533a\u5206\u2014\u2014"
        "\u8bef\u5dee\u5c0f\u4e14\u6ca1\u88ab\u906e\u6321\u7684\u662f\u9759\u6001\u80cc\u666f\uff0c\u8bef\u5dee\u5927\u6216\u88ab\u906e\u6321\u7684\u662f\u52a8\u6001\u533a\u3002"
    )
    pdf.code(
        "# train.py:1091-1101 (static/dynamic point split)\n"
        "stat_points = points[(accum_error == 0) & (motion_error == 0)]   # static\n"
        "dyn_points  = points[(accum_error == 1) & (motion_error == 1)]   # dynamic"
    )
    pdf.verdict("\u521d\u59cb 3DGS = \u6df1\u5ea6\u5148\u9a8c\u53cd\u63a8\u6210\u70b9\u4e91 + CoTracker \u8f68\u8ff9\u7ed9\u52a8\u6001\u70b9\u8d4b\u65f6\u95f4\u7ef4\uff0c\u5b8c\u5168\u4e0d\u6d89 COLMAP \u70b9\u4e91\uff0c\u4e5f\u4e0d\u968f\u673a\u3002")

    # ---- Q4 ----
    pdf.add_page()
    pdf.q_block("4", "\u5982\u679c\u7528\u4e86\u6df1\u5ea6\u76f8\u5173\u5148\u9a8c\uff0c\u8bf4\u6210 COLMAP-free \u5408\u9002\u5417\uff1f")

    pdf.lead("\u7b54\uff1a\u5408\u9002\uff0c\u4f46\u8981\u628a\u201cCOLMAP-free\u201d\u548c\u201c\u65e0\u5148\u9a8c\u201d\u533a\u5206\u5f00\u8bf4")
    pdf.body(
        "\u5728 3DGS \u8fd9\u4e2a\u5c0f\u5708\u5b50\u91cc\uff0c\u201cCOLMAP-free\u201d\u662f\u4e2a\u7ea6\u5b9a\u4fd7\u6210\u7684\u672f\u8bed\uff0c"
        "\u4e13\u6307\u201c\u4e0d\u8dd1 COLMAP \u7684 SfM\uff08\u4f4d\u59ff\u4f30\u8ba1\uff09+ MVS\uff08\u70b9\u4e91\u91cd\u5efa\uff09\u6d41\u6c34\u7ebf\u201d\u3002"
        "\u539f\u7248 Dynamic-3DGS / Deformable-3DGS \u90fd\u5f3a\u4f9d\u8d56 COLMAP\uff1b\u672c\u9879\u76ee\u8fd9\u4e00\u652f\u7684\u5356\u70b9\u5c31\u662f\u201c\u7528\u5b66\u4e60\u578b\u51e0\u4f55\u5148\u9a8c\u66ff\u6362 COLMAP\u201d\u3002"
        "\u6240\u4ee5\u5728\u8fd9\u4e2a\u8c31\u7cfb\u91cc\u8bf4 COLMAP-free \u662f\u51c6\u786e\u7684\uff0c\u4e5f\u6709\u5bf9\u6bd4\u4ef7\u503c\u3002"
    )
    pdf.body(
        "\u4f46\u201c\u65e0\u5148\u9a8c\u201d\u5c31\u4e0d\u5bf9\u4e86\u3002\u6df1\u5ea6\u7f51\u7edc\u672c\u8eab\u662f\u5728\u5916\u90e8\u5927\u6570\u636e\u4e0a\u9884\u8bad\u7ec3\u8fc7\u7684\uff0c"
        "\u5b9e\u9645\u4e0a\u662f\u628a\u201cSfM \u5148\u9a8c\u201d\u6362\u6210\u4e86\u201c\u6570\u636e\u9a71\u52a8\u7684\u5b66\u4e60\u578b\u5148\u9a8c\u201d\u3002"
        "\u5148\u9a8c\u53ea\u662f\u6362\u4e86\u4e2a\u5730\u65b9\u5b58\u653e\uff0c\u5e76\u6ca1\u6709\u51ed\u7a7a\u6d88\u5931\u3002"
    )
    pdf.lead("\u5efa\u8bae\u5982\u4f55\u8868\u8ff0\uff08\u4f9b\u8bba\u6587/\u6c47\u62a5\u4f7f\u7528\uff09")
    pdf.body(
        "\u5efa\u8bae\u907f\u514d\u8bf4\u201c\u672c\u65b9\u6cd5\u65e0\u9700\u4efb\u4f55\u5148\u9a8c\u201d\uff0c\u6539\u4e3a\u7c7b\u4f3c\u4e0b\u9762\u7684\u8bf4\u6cd5\uff1a"
    )
    pdf.code(
        '"This method removes the COLMAP SfM/MVS pipeline,\n'
        ' replacing it with UniDepth metric depth / Depth-Anything disparity\n'
        ' and CoTracker3 long-range tracks for geometry & motion supervision.\n'
        ' Camera pose, focal length and per-frame depth scale are jointly\n'
        ' estimated via differentiable optimization."'
    )
    pdf.body(
        "\u8fd9\u6837\u5199\u65e2\u5b88\u4f4f\u4e86 COLMAP-free \u7684\u5bf9\u6bd4\u4ef7\u503c\uff08\u786e\u5b9e\u4e0d\u8dd1 COLMAP\uff09\uff0c"
        "\u53c8\u4e0d\u5938\u5927\u6210\u201c\u4ec0\u4e48\u90fd\u4e0d\u9700\u8981\u201d\u3002\u5ba1\u7a3f\u4eba\u5e38\u95ee\u7684\u4e00\u4e2a\u70b9\u662f\uff1a"
        "\u6df1\u5ea6\u5148\u9a8c\u7f51\u7edc\u7684\u9884\u8bad\u7ec3\u6570\u636e\u662f\u5426\u8986\u76d6\u4e86\u624b\u672f\u573a\u666f\u2014\u2014"
        "\u8fd9\u662f\u8be5\u7c7b\u65b9\u6cd5\u5171\u6709\u7684\u9690\u542b\u524d\u63d0\uff0c\u5efa\u8bae\u5728\u8ba8\u8bba\u91cc\u70b9\u660e\u3002"
    )
    pdf.verdict("\u201cCOLMAP-free\u201d\u5408\u9002\uff1b\u201c\u65e0\u5148\u9a8c/prior-free\u201d\u4e0d\u5408\u9002\u3002\u5efa\u8bae\u8868\u8ff0\u4e3a\u201c\u7528\u5b66\u4e60\u578b\u51e0\u4f55\u5148\u9a8c\u66ff\u4ee3 COLMAP\u201d\u3002")

    # ---- 一页速查表 ----
    pdf.add_page()
    pdf.lead("\u56db\u95ee\u901f\u67e5\u8868")
    pdf.ln(1)
    rows = [
        ("Q1 COLMAP-free?", "\u662f\uff0c\u4f46\u9700\u6df1\u5ea6+\u8ddf\u8e2a\u5148\u9a8c", "dataset_readers.py:622/378\uff08\u5355\u4f4d\u9635\u8d77\u6b65\uff09"),
        ("Q2 \u5185\u53c2\u6765\u6e90", "\u7126\u8ddd\u5b66\u51fa / \u4e3b\u70b9\u786c\u7f16\u4e3a\u56fe\u50cf\u4e2d\u5fc3", "deformation.py:51 / dataset_readers.py:635"),
        ("Q3 \u521d\u59cb3DGS", "\u6df1\u5ea6\u53cd\u63a8 + CoTracker\u8d4b\u8f68\uff0c\u975e\u968f\u673a", "train.py:1068 / 1120 / 1091"),
        ("Q4 \u201cCOLMAP-free\u201d\u63aa\u8f9e", "\u5408\u9002\uff0c\u4f46\u5e94\u8bf4\u201c\u7528\u5b66\u4e60\u5148\u9a8c\u66ff COLMAP\u201d", "README.md \u53cc\u73af\u5883\u63cf\u8ff0"),
    ]
    pdf.set_font("Noto", "", 9.5)
    for i, (q, a, s) in enumerate(rows):
        pdf.set_fill_color(*LIGHT) if i % 2 == 0 else pdf.set_fill_color(255, 255, 255)
        pdf.set_text_color(*NAVY); pdf.set_font("Noto", "B", 9.5)
        pdf.cell(40, 8, q, border=1, fill=True)
        pdf.set_text_color(*DGREY); pdf.set_font("Noto", "", 9.5)
        pdf.cell(78, 8, a, border=1, fill=True)
        pdf.set_text_color(120, 120, 120); pdf.set_font("Noto", "I", 8.6)
        pdf.cell(68, 8, s, border=1, fill=True)
        pdf.ln(8)

    pdf.ln(4)
    pdf.body(
        "\u5982\u9700\u8fdb\u4e00\u6b65\u6838\u67e5\uff0c\u53ef\u6309\u4e0a\u8ff0\u4ee3\u7801\u4f4d\u7f6e\u76f4\u63a5\u6253\u5f00\u6e90\u7801\u67e5\u770b\u4e0a\u4e0b\u6587\u3002"
        "\u6240\u6709\u7ed3\u8bba\u5747\u4e0e\u4ee3\u7801\u4e00\u4e00\u5bf9\u5e94\uff0c\u53ef\u4ee5\u76f4\u63a5\u4f5c\u4e3a\u4e0e\u590f\u8001\u5e08\u6c9f\u901a\u7684\u4f9d\u636e\u3002"
    )

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Surgical_TSplineGS_QA.pdf")
    pdf.output(out)
    print(f"PDF generated: {out}")
    print(f"Pages: {pdf.page_no()}")


if __name__ == "__main__":
    build()
