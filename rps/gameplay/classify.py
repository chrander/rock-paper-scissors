from typing import Union

import cv2
import numpy as np
import torch
import torchvision.transforms as T
from ultralytics import YOLO

from rps import constants


# YOLO model
model = YOLO(constants.model_path)


def process_frame(video_frame: np.array) -> torch.tensor:
    """Preprocesses a video frame before passing to a PyTorch model

    May not be required for YOLO models since the model handles this
    stuff internally.

    Parameters
    ----------
    video_frame : np.array
        The frame to process

    Returns
    -------
    torch.tensor
        The preprocessed frame
    """
    height, width = video_frame.shape[:2]
    img = video_frame.copy()
    # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    transforms = T.Compose([
        T.ToTensor(),
        T.CenterCrop(min(height, width)),
        T.Resize(size=(320, 320))
    ])

    tensor = transforms(img)
    tensor = tensor[None, :]  # Add the first dimension to the tensor so it's what PyTorch expects
    return tensor


def get_choice_from_video() -> tuple[np.array, Union[constants.PlayerChoice, str]]:
    """Get a human rock, paper, or scissors choice from a video stream

    Returns
    -------
    tuple[np.array, str]
        The image and the player choice value. If the player submitted a valid RPS choice,
        it will be the choic value. If the player chose to quit, the string QUIT is returned.
    """
    cap = cv2.VideoCapture(constants.VIDEO_SOURCE)

    while True:
        # Capture the video frame by frame
        _, frame = cap.read()

        img = frame.copy()  # Copy so that we don't return something with text on it
        height, _ = frame.shape[:2]
        # tensor = process_frame(frame)

        # Feed the image to the model and use the max probability as the player choice
        results = model(frame, imgsz=320)
        probs = results[0].probs.data.numpy()
        pred_index = np.argmax(probs)
        prediction = constants.PLAYER_CHOICES[pred_index]

        # Draw the prediction on the frame
        cv2.putText(frame, f'Your choice: {prediction.name}', (10, 50),
                    constants.font,
                    constants.choice_font_scale,
                    constants.choice_font_color,
                    constants.choice_font_thickness,
                    constants.font_line_type)
        cv2.putText(frame, 'Press SPACE to select choice, q to quit', (10, height-10),
                    constants.font, 1, constants.choice_font_color, 2, constants.font_line_type)
        # Display the resulting frame
        cv2.namedWindow(constants.WINDOW_NAME, cv2.WINDOW_NORMAL)
        frame = cv2.resize(frame, constants.IMAGE_SIZE, interpolation=cv2.INTER_LINEAR)
        cv2.imshow(constants.WINDOW_NAME, frame)

        key = cv2.waitKey(1) & 0xFF
        if key == 32:
            # Press SPACE to end the loop and return the current prediction
            value = prediction
            break
        elif key == ord('q'):
            # Press 'q' to quit
            value = constants.QUIT
            break

    # Release the capture object
    cap.release()
    # Destroy all the windows
    cv2.destroyAllWindows()

    return img, value
