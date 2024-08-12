from torch.nn.functional import mse_loss
from src.utils import ImageHandler
from skimage.metrics import structural_similarity as ssim

class Criterion:
    def __init__(self) -> None:
        self.image_handler = ImageHandler()

    def total_loss(self, content_features, style_features, output_contents, output_styles, content_weight=2, style_weight=1e8):
        # Content Loss
        content_loss = 0
        for c, o in zip(content_features, output_contents):
            content_loss += mse_loss(c, o)
        
        # Style Loss
        style_loss = 0
        for s, o in zip(style_features, output_styles):
            style_texture = self.image_handler.gram_matrix(s)
            output_texture = self.image_handler.gram_matrix(o)
            style_loss += mse_loss(style_texture, output_texture)
            
        # Total loss
        loss = content_weight * content_loss + style_weight * style_loss
        return loss
    
    def calculate_ssim(self, img1, img2, win_size=11):
        img1 = img1.cpu().detach().numpy().squeeze().transpose(1, 2, 0)
        img2 = img2.cpu().detach().numpy().squeeze().transpose(1, 2, 0)
        
        img1 = img1 * self.image_handler.std.cpu().numpy() + self.image_handler.mean.cpu().numpy()
        img2 = img2 * self.image_handler.std.cpu().numpy() + self.image_handler.mean.cpu().numpy()
        
        img1 = (img1 * 255).astype('uint8')
        img2 = (img2 * 255).astype('uint8')
        
        ssim_value, _ = ssim(img1, img2, win_size=win_size, channel_axis=2, full=True)
        return ssim_value