"""Render RGB, depth, and normal maps from a trained ZT-GS checkpoint (video_5)."""
import os
import sys
import torch
import numpy as np
from PIL import Image
from argparse import ArgumentParser

sys.path.append(os.path.join(sys.path[0], "."))

from arguments import ModelHiddenParams, ModelParams, OptimizationParams, PipelineParams
from gaussian_renderer import render
from scene import GaussianModel, Scene, dataset_readers
from scene.dataset_readers import get_normals
from utils.main_utils import get_pixels


def colorize_depth(depth, cmap="turbo"):
    """Map a depth tensor [H, W] (invalid=0) to a colorized uint8 image [H, W, 3]."""
    d = depth.detach().cpu().numpy()
    valid = d > 0
    if not valid.any():
        return np.zeros((d.shape[0], d.shape[1], 3), dtype=np.uint8)
    dmin, dmax = np.percentile(d[valid], 1), np.percentile(d[valid], 99)
    norm = np.clip((d - dmin) / max(dmax - dmin, 1e-8), 0, 1)
    norm = (norm * 255).astype(np.uint8)
    import cv2
    colored = cv2.applyColorMap(norm, cv2.COLORMAP_TURBO)
    colored[~valid] = 0
    return colored


def main():
    parser = ArgumentParser(description="Render video_5 RGB/depth/normal")
    lp = ModelParams(parser)
    op = OptimizationParams(parser)
    pp = PipelineParams(parser)
    hp = ModelHiddenParams(parser)
    parser.add_argument("--checkpoint", type=str, required=True)
    parser.add_argument("--expname", type=str, default="video_5")
    parser.add_argument("--configs", type=str, default="")
    parser.add_argument("--out_dir", type=str, default=None)
    args = parser.parse_args(sys.argv[1:])

    if args.configs:
        import mmengine as mmcv
        from utils.params_utils import merge_hparams
        config = mmcv.Config.fromfile(args.configs)
        args = merge_hparams(args, config)

    dataset = lp.extract(args)
    hyper = hp.extract(args)
    stat_gaussians = GaussianModel(dataset)
    dyn_gaussians = GaussianModel(dataset)
    opt = op.extract(args)

    scene = Scene(dataset, dyn_gaussians, stat_gaussians, load_coarse=None)
    dyn_gaussians.create_pose_network(hyper, scene.getTrainCameras())

    bg_color = [0] * 9 + [0]
    background = torch.tensor(bg_color, dtype=torch.float32, device="cuda")
    pipe = pp.extract(args)

    train_cams = scene.getTrainCameras()
    test_cams = scene.getTestCameras()
    viewpoint_stack = [i for i in train_cams]
    my_test_cams = [i for i in test_cams]

    # Load checkpoint
    ckpt = args.checkpoint
    dyn_gaussians.load_ply(os.path.join(ckpt, "point_cloud.ply"))
    stat_gaussians.load_ply(os.path.join(ckpt, "point_cloud_static.ply"))
    dyn_gaussians.flatten_control_point()
    dyn_gaussians.load_model(ckpt)
    dyn_gaussians._posenet.eval()

    # Update camera poses from pose network
    pixels = get_pixels(
        scene.train_camera.dataset[0].metadata.image_size_x,
        scene.train_camera.dataset[0].metadata.image_size_y,
        use_center=True,
    )
    batch_shape = pixels.shape[:-1]
    pixels = np.reshape(pixels, (-1, 2))
    y = (pixels[..., 1] - scene.train_camera.dataset[0].metadata.principal_point_y) / \
        dyn_gaussians._posenet.focal_bias.exp().detach().cpu().numpy()
    x = (pixels[..., 0] - scene.train_camera.dataset[0].metadata.principal_point_x) / \
        dyn_gaussians._posenet.focal_bias.exp().detach().cpu().numpy()
    viewdirs = np.stack([x, y, np.ones_like(x)], axis=-1)
    local_viewdirs = viewdirs / np.linalg.norm(viewdirs, axis=-1, keepdims=True)

    with torch.no_grad():
        for cam in viewpoint_stack:
            time_in = torch.tensor(cam.time).float().cuda()
            pred_R, pred_T = dyn_gaussians._posenet(time_in.view(1, 1))
            R_ = torch.transpose(pred_R, 2, 1).detach().cpu().numpy()
            t_ = pred_T.detach().cpu().numpy()
            cam.update_cam(
                R_[0], t_[0], local_viewdirs, batch_shape,
                dyn_gaussians._posenet.focal_bias.exp().detach().cpu().numpy(),
            )
        for view_id in range(len(my_test_cams)):
            my_test_cams[view_id].update_cam(
                viewpoint_stack[0].R, viewpoint_stack[0].T, local_viewdirs, batch_shape,
                dyn_gaussians._posenet.focal_bias.exp().detach().cpu().numpy(),
            )

    out_dir = args.out_dir or os.path.join("output", args.expname, "render_results")
    for sub in ["rgb", "depth", "normal", "gt"]:
        os.makedirs(os.path.join(out_dir, sub), exist_ok=True)

    import cv2

    def render_set(cameras, name_prefix, split):
        with torch.no_grad():
            for idx, cam in enumerate(cameras):
                render_pkg = render(cam, scene.stat_gaussians, scene.dyn_gaussians, background)
                rgb = torch.clamp(render_pkg["render"], 0.0, 1.0)
                depth = render_pkg.get("depth")
                rgb_np = (rgb.permute(1, 2, 0).detach().cpu().numpy() * 255).astype(np.uint8)

                # Save RGB
                Image.fromarray(rgb_np).save(os.path.join(out_dir, "rgb", f"{split}_{idx:03d}.png"))

                # Save depth
                if depth is not None:
                    if depth.dim() > 2:
                        depth = depth.squeeze(0)
                    depth_col = colorize_depth(depth)
                    cv2.imwrite(os.path.join(out_dir, "depth", f"{split}_{idx:03d}.png"), depth_col)
                    depth_raw = depth.detach().cpu().numpy()
                    np.save(os.path.join(out_dir, "depth", f"{split}_{idx:03d}.npy"), depth_raw.astype(np.float32))

                    # Compute normal from rendered depth via dataset_readers.get_normals
                    try:
                        z = depth.detach()[None]  # [1, H, W]
                        normal = get_normals(z, cam.metadata)
                        normal = normal.squeeze(0).cpu().numpy().transpose(1, 2, 0)
                        normal_vis = ((normal * 0.5 + 0.5) * 255).clip(0, 255).astype(np.uint8)
                        cv2.imwrite(os.path.join(out_dir, "normal", f"{split}_{idx:03d}.png"), normal_vis)
                    except Exception as e:
                        print(f"[normal] frame {idx} failed: {e}")

                # Save GT
                gt_np = (cam.original_image.permute(1, 2, 0).detach().cpu().numpy() * 255).astype(np.uint8)
                Image.fromarray(gt_np).save(os.path.join(out_dir, "gt", f"{split}_{idx:03d}.png"))

                if idx % 5 == 0:
                    print(f"[{split}] rendered {idx+1}/{len(cameras)}")

    print(f"=== Rendering {len(my_test_cams)} test views ===")
    render_set(my_test_cams, "test", "test")
    print(f"=== Rendering {len(viewpoint_stack)} train views ===")
    render_set(viewpoint_stack, "train", "train")
    print(f"=== Done. Results saved to {out_dir} ===")


if __name__ == "__main__":
    main()
