import torch.optim as optim
import torchvision
import torchvision.datasets as datasets
import torchvision.transforms as transforms
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter
from model import Discriminator , Generator , initialize_weights

device=torch.device("cuda" if torch.cuda.is_available() else "cpu")

Learning_rate=2e-5
BATCH_SIZE=1
IMAGE_SIZE=64
CHANNELS_IMG=3
Z_DIM=100
NUM_EPOCHS=2
FEATURES_DISC=64
FEATURES_GEN=64


transforms=transforms.Compose([
    transforms.Resize(IMAGE_SIZE),
    transforms.ToTensor(),
    transforms.Normalize(
    [0.5 for _ in range(CHANNELS_IMG)],[0.5 for _ in range(CHANNELS_IMG)])]

)


dataset=datasets.ImageFolder(root="data",
                                       transform=transforms)
loader=torch.utils.data.DataLoader(dataset=dataset,
                                       batch_size=BATCH_SIZE,shuffle=True)
gen=Generator(Z_DIM,CHANNELS_IMG,FEATURES_GEN)
disc=Discriminator(CHANNELS_IMG,FEATURES_DISC)
initialize_weights(gen)                                 
initialize_weights(disc)
opt_gen=optim.Adam(gen.parameters(),lr=Learning_rate,betas=(0.5,0.999))
opt_disc=optim.Adam(disc.parameters(),lr=Learning_rate,betas=(0.5,0.999))
criterion=nn.BCELoss()
fixed_noise=torch.randn(32,Z_DIM,1,1)
writer_real=SummaryWriter(f"logs/real")
writer_fake=SummaryWriter(f"logs/fake")
step = 0
gen.train()
disc.train()
for epoch in range(NUM_EPOCHS):
    for batch_idx , (real , _) in enumerate(loader):
        real=real 
        noise=torch.randn(BATCH_SIZE,Z_DIM,1,1)
        fake=gen(noise)
        
        disc_real=disc(real).reshape(-1)
        loss_disc_real=criterion(disc_real,torch.ones_like(disc_real))
        disc_fake=disc(fake).reshape(-1)
        loss_disc_fake=criterion(disc_fake,torch.zeros_like(disc_fake))
        loss_disc=(loss_disc_real + loss_disc_fake) / 2
        disc.zero_grad()
        loss_disc.backward(retain_graph=True)
        opt_disc.step()
        
        
        output=disc(fake).reshape(-1)
        loss_gen=criterion(output,torch.ones_like(output))
        gen.zero_grad()
        loss_gen.backward()
        opt_gen.step()
        
        if batch_idx %100 == 0:
            print(
                f"Epoch[{epoch}/{NUM_EPOCHS}] Batch {batch_idx} / {len(loader)}\ Loss D:{loss_disc:.4f},Loss G:{loss_gen:.4f}"
                ) 
            with torch.no_grad():
                fake=gen(fixed_noise)
                img_grid_fake=torchvision.utils.make_grid(fake[:32],normalize=True)
                img_grid_real=torchvision.utils.make_grid(real[:32],normalize=True)
                
                writer_fake.add_image(
                    
                    "Fake",img_grid_fake,global_step=step)
                
                writer_real.add_image(
                    
                    "Real",img_grid_real,global_step=step)
                step+=1
        
        
        
        
        