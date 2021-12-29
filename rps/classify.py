import os

import cv2
import torch
import torchvision.transforms as T

from rps import class_names
from rps import QUIT

# Load the model
models_dir = '/Users/chris/Documents/projects/rps/rock-paper-scissors/models'
model_path = os.path.join(models_dir, 'model_2021-12-27_2057.pth')

the_model = torch.load(model_path)
the_model.eval()


source = 0
font = cv2.FONT_HERSHEY_SIMPLEX
font_color = (0, 255, 0)

def process_frame(video_frame):
    height, width = video_frame.shape[:2]
    img = video_frame.copy()
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    transforms = T.Compose([
        T.ToTensor(),
        T.CenterCrop(min(height, width)),
        T.Resize(size=(224, 224)),
        T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    tensor = transforms(img)
    tensor = tensor[None, :]  # Add the first dimension to the tensor so it's what PyTorch expects
    return tensor


def get_choice_from_video():
    """Gets a human rock, paper, scissors choice from a video frame"""
    cap = cv2.VideoCapture(source)

    while(True):
        # Capture the video frame by frame
        _, frame = cap.read()
        height, _ = frame.shape[:2]
        tensor = process_frame(frame)
    
        outputs = the_model(tensor)
        _, preds = torch.max(outputs, 1)
        prediction = class_names[preds[0]]
        
        cv2.putText(frame, prediction, (10, height-10), font, 3, font_color, 2, cv2.LINE_AA)
        # Display the resulting frame
        cv2.imshow('Rock, Paper, Scissors', frame)
          
        key = cv2.waitKey(1) & 0xFF
        if key == 32: 
            # Press SPACE to end and return the current prediction
            value = prediction
            break
        elif key == ord('q'):
            value = QUIT
            break
            
    # Release the capture object
    cap.release()
    # Destroy all the windows
    cv2.destroyAllWindows()

    return value