# importing torch  
import torch  
# get index of currently selected device  
print(torch.cuda.current_device()) # returns 0 in my case  
# get number of GPUs available  
print(torch.cuda.device_count()) # returns 1 in my case  
# get the name of the device  
print(torch.cuda.get_device_name(0))