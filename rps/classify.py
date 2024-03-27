import os

import cv2
import numpy as np
import torch
import torchvision.transforms as T

from rps import constants


# Load the model. TODO: make the path configurable instead of hard coded in constants
the_model = torch.load(constants.model_path)
the_model.eval()

source = 0  # Index determining the source of the video


def process_frame(video_frame: np.array) -> torch.tensor:
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


def get_choice_from_video() -> tuple[np.array, str]:
    """Gets a human rock, paper, scissors choice from a video frame"""
    cap = cv2.VideoCapture(source)

    while(True):
        # Capture the video frame by frame
        _, frame = cap.read()
        img = frame.copy()  # Copy so that we don't return something with text on it
        height, _ = frame.shape[:2]
        tensor = process_frame(frame)

        outputs = the_model(tensor)
        _, preds = torch.max(outputs, 1)
        prediction = constants.PLAYER_CHOICES[preds[0]]

        cv2.putText(frame, f'Your choice: {prediction.name}', (10, 50), 
                    constants.font, 
                    constants.choice_font_scale, 
                    constants.choice_font_color, 
                    constants.choice_font_thickness, 
                    constants.font_line_type)
        cv2.putText(frame, 'Press SPACE to select choice, q to quit', (10, height-10), 
                    constants.font, 1, constants.choice_font_color, 2, constants.font_line_type)
        # Display the resulting frame
        cv2.imshow('Rock, Paper, Scissors', frame)

        key = cv2.waitKey(1) & 0xFF
        if key == 32:
            # Press SPACE to end and return the current prediction
            value = prediction
            break
        elif key == ord('q'):
            value = constants.QUIT
            break

    # Release the capture object
    cap.release()
    # Destroy all the windows
    cv2.destroyAllWindows()

    return img, value
