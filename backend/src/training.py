import torch
from torch import optim
from src.models import NeuralStyleTransfer
from src.criterion import Criterion
from src.utils import ImageHandler

class Trainer:
    def __init__(self) -> None:
        self.max_epochs = 2500
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.model = NeuralStyleTransfer().to(self.device)
        self.criterion = Criterion()
        self.image_handler = ImageHandler()

    def start_training(self, content_features, style_features, content_image, output):
        print(f'---------------------start training---------------------')
        for epoch in range(1, self.max_epochs+1):
            optimizer = optim.AdamW([output], lr=0.05)
            output_features = self.model(output, layers=["4", "8"])
            loss = self.criterion.total_loss(content_features, style_features, output_features, output_features, style_weight=1e6)
            loss.backward()
            ssim = self.criterion.calculate_ssim(output, content_image)

            optimizer.step()
            optimizer.zero_grad()
            
            if epoch % 100 == 0:
                print(f"Epoch: {epoch:5} | Loss: {loss.item():.5f} | SSIM: {ssim}")
                # _ = image_handler.draw_styled_image(output)
            if epoch == 800 or epoch == 1600 or epoch == 2500:
                output_image_path = f"outputs/output_epoch_{epoch}.png"
                self.image_handler.save_image(output, output_image_path)
                generated_image_name = f"output_epoch_{epoch}.png"
        
        return generated_image_name