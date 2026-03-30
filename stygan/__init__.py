import os
import numpy as np
import PIL.Image
import torch
import dnnlib
import legacy
from typing import List, Optional


class StyleGANImageGenerator:
    def __init__(self, network_pkl: str, outdir: str, truncation_psi: float = 1.0, noise_mode: str = 'const'):
        """
        初始化 StyleGAN 图像生成器。

        :param network_pkl: 预训练网络的路径（本地路径或URL）
        :param outdir: 输出图片保存的目录
        :param truncation_psi: Truncation 参数（默认为 1.0）
        :param noise_mode: 噪声模式（默认为 'const'）
        """
        self.network_pkl = network_pkl
        self.outdir = outdir
        self.truncation_psi = truncation_psi
        self.noise_mode = noise_mode

        # 加载网络
        print(f'Loading networks from "{self.network_pkl}"...')
        # 优先用 GPU，有就用，没有就退回 CPU，避免 "Torch not compiled with CUDA enabled" 报错
        if torch.cuda.is_available():
            self.device = torch.device('cuda')
        else:
            self.device = torch.device('cpu')
        with dnnlib.util.open_url(self.network_pkl) as f:
            self.G = legacy.load_network_pkl(f)['G_ema'].to(self.device)  # type: ignore

        os.makedirs(self.outdir, exist_ok=True)

    def generate_images(self, seeds: List[int], class_idx: Optional[int] = None, projected_w: Optional[str] = None):
        """
        根据随机种子生成图像并保存到指定目录。

        :param seeds: 随机种子列表，用于生成不同的图像
        :param class_idx: 类别标签（如果是条件生成）
        :param projected_w: 投影结果文件（可选，使用投影的 W 向量生成图像）
        """
        # 如果是从投影的W生成图像
        if projected_w is not None:
            if seeds is not None:
                print('Warning: --seeds 被忽略，因为你使用了 --projected-w')
            print(f'从投影W文件 "{projected_w}" 生成图像')
            self._generate_from_projected_w(projected_w)
            return

        # 没有指定 --projected-w，必须有 --seeds 参数
        if seeds is None:
            raise ValueError('--seeds 参数是必需的，除非使用 --projected-w')

        # 生成条件标签
        label = torch.zeros([1, self.G.c_dim], device=self.device)
        if self.G.c_dim != 0:
            if class_idx is None:
                raise ValueError('如果使用条件网络，必须指定 --class 标签')
            label[:, class_idx] = 1
        else:
            if class_idx is not None:
                print('Warning: 在无条件网络下，--class=lbl 参数被忽略')

        # 生成图像
        for seed_idx, seed in enumerate(seeds):
            print(f'为种子 {seed} 生成图像 ({seed_idx + 1}/{len(seeds)}) ...')
            z = torch.from_numpy(np.random.RandomState(seed).randn(1, self.G.z_dim)).to(self.device)
            img = self.G(z, label, truncation_psi=self.truncation_psi, noise_mode=self.noise_mode)
            img = (img.permute(0, 2, 3, 1) * 127.5 + 128).clamp(0, 255).to(torch.uint8)
            PIL.Image.fromarray(img[0].cpu().numpy(), 'RGB').save(f'{self.outdir}/{seed:d}.png')

            # 生成完每张图后清理内存 / 显存
            del z, img
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

    def _generate_from_projected_w(self, projected_w: str):
        """ 从投影的W向量生成图像 """
        ws = np.load(projected_w)['w']
        ws = torch.tensor(ws, device=self.device)  # pylint: disable=not-callable
        assert ws.shape[1:] == (self.G.num_ws, self.G.w_dim)
        for idx, w in enumerate(ws):
            img = self.G.synthesis(w.unsqueeze(0), noise_mode=self.noise_mode)
            img = (img.permute(0, 2, 3, 1) * 127.5 + 128).clamp(0, 255).to(torch.uint8)
            img = PIL.Image.fromarray(img[0].cpu().numpy(), 'RGB')
            img.save(f'{self.outdir}/proj{idx:02d}.png')

            # 清理内存 / 显存
            del w, img
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

    def release_memory(self):
        """显式释放网络的显存"""
        del self.G
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


# 示例用法：
# generator = StyleGANImageGenerator(
#     network_pkl='https://nvlabs-fi-cdn.nvidia.com/stylegan2-ada-pytorch/pretrained/ffhq.pkl',
#     outdir='./output',
#     truncation_psi=0.7
# )
# generator.generate_images(seeds=[1, 2, 3])
