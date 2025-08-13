import modal

model_image = (
    modal.Image.debian_slim(python_version="3.11.11").apt_install("libgl1", "libglib2.0-0").pip_install("pandas==2.2.2", "numpy==1.26.4", 
    "scikit-learn==1.6.1", "ultralytics==8.3.88", "scipy==1.14.1", "joblib==1.4.2", "opencv-python==4.11.0.86", "fastapi[standard]","reportlab",
        "google-cloud-storage","google-auth" )
    .add_local_file("scaler_fold_2.joblib", remote_path="/root/scaler_fold_2.joblib")
    .add_local_file("lda_fold_2.joblib", remote_path="/root/lda_fold_2.joblib").add_local_file("svm_fold_2.joblib", remote_path="/root/svm_fold_2.joblib")
    .add_local_file("best_model_fold_0.pth", remote_path="/root/best_model_fold_0.pth").add_local_file("scaler_angle_fold_0.joblib", remote_path="/root/scaler_angle_fold_0.joblib")
    .add_local_file("scaler_dist_fold_0.joblib", remote_path="/root/scaler_dist_fold_0.joblib").add_local_file("scaler_hof_fold_0.joblib", remote_path="/root/scaler_hof_fold_0.joblib")
    .add_local_file("scaler_ltp_fold_0.joblib", remote_path="/root/scaler_ltp_fold_0.joblib").add_local_file("scaler_vel_fold_0.joblib", remote_path="/root/scaler_vel_fold_0.joblib")
)

app = modal.App(name="model-deployment", image=model_image)

# check a funnction like this example
# modal run main.py::predict_dl --video-url=https://storage.googleapis.com/fyp-data-bucket/20250805171433_2_2.MOV

import modal

# video checking code (can be pasted in a new python file)
# video_url = "https://storage.googleapis.com/fyp-data-bucket/20250718035456_17_1.mp4"
# classification_func = modal.Function.from_name("model-deployment", "predict_ml")
# classification_result = classification_func.remote(video_url)

# print("classification result", classification_result)

# 64_1, 17_1, 18_2, 2_2, 38_2, 25_3, 28_3, 21_2  example videos that are classified correctly by both pipelines

@app.function(gpu="T4", secrets=[modal.Secret.from_name("google cloud storage")])
def predict_dl(video_url: str):
    """
    Processes video and returns the activity performed in it using deep learning.

    Input:
        video_url: video url to be processed

    Output:
        activity performed in the video
    """
    import numpy as np
    import joblib
    import torch
    import torch.nn as nn
    import os
    import json

    CLASSES = ["doing own work", "passing paper", "looking at other's work"]

    selected_features_len = {
        "dist": 12,
        "angle": 15,
        "hof": 18,
        "vel": 14,
        "ltp": 512
    }

    selected_features = ["dist", "angle", "hof", "ltp", "vel"]

    silhouettes = segmentation(video_url, 41)
    keypoints, middle_frame_image, boxes, track_ids, frame_keypoints = keypoints_extraction(video_url, 41)
    hof = hof_extraction(silhouettes)
    dist = dist_feat_extraction(keypoints)
    angle = angle_feat_extraction(keypoints)
    vel = velocity_feat_extraction(keypoints)
    ltp = ltp_feat_extraction(silhouettes)
    
    X_test = np.concatenate((dist, angle, hof, ltp, vel), axis=1)
    X_test = np.expand_dims(X_test, axis=0)
    
    standard_X_test = None
    prev_feat_length = 0

    for feature in selected_features:
          X_test_subset = X_test[:, :, prev_feat_length:prev_feat_length + selected_features_len[feature]].reshape(X_test.shape[0], -1)

          scaler = joblib.load(f"scaler_{feature}_fold_0.joblib")
          X_test_subset = scaler.transform(X_test_subset)

          X_test_subset = X_test_subset.reshape(X_test.shape[0], 40, -1)

          if standard_X_test is None:
              standard_X_test = X_test_subset
          else:
              standard_X_test = np.concatenate((standard_X_test, X_test_subset), axis=2)

          prev_feat_length += selected_features_len[feature]

    X_test = standard_X_test

    class BiLSTM(nn.Module):
        def __init__(self, input_dim, hidden_dim, output_dim, num_layers):
            super(BiLSTM, self).__init__()
            self.hidden_dim = hidden_dim
            self.num_layers = num_layers

            # LSTM Layer (Bi-directional if specified)
            self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers, batch_first=True, bidirectional=True)

            # Output Layer
            self.fc = nn.Linear(hidden_dim * 2, output_dim)

            # ReLU activation and Dropout for regularization
            self.relu = nn.ReLU()
            self.dropout = nn.Dropout(0.3)

        def forward(self, x):
            # LSTM Layer - Get output and hidden state (we don't need the hidden state here)
            lstm_out, _ = self.lstm(x)  # LSTM output shape: (batch_size, seq_len, hidden_dim * 2)

            # We take the concatenation of the forward and backward hidden states at the last time step
            final_hidden_state = torch.cat((lstm_out[:, -1, :self.hidden_dim], lstm_out[:, 0, self.hidden_dim:]), dim=-1)

            # Apply Dropout, then fully connected layer
            output = self.fc(self.dropout(self.relu(final_hidden_state)))

            return output


    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    input_dim = X_test.shape[2]  # input dimension
    hidden_dim = 128 
    num_classes = len(CLASSES)
    num_layers = 1

    model = BiLSTM(input_dim, hidden_dim, num_classes, num_layers).to(device)

    # Load the saved model state
    model_path = "best_model_fold_0.pth"
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()

    # Convert input to tensor and move to device
    input_tensor = torch.tensor(X_test, dtype=torch.float32).to(device)  # Add batch dimension

    # Make prediction
    with torch.no_grad():
      output = model(input_tensor)
      prediction = torch.argmax(output, dim=1).item()

    return generate_pdf_report(silhouettes, keypoints, middle_frame_image,
                    boxes, track_ids, frame_keypoints,CLASSES[prediction], 
                    json.loads(os.environ["GOOGLE_APPLICATION_CREDENTIALS"]), 
                    os.environ["GCS_BUCKET_NAME"], "dl")
    



@app.function(gpu="T4", secrets=[modal.Secret.from_name("google cloud storage")])
def predict_ml(video_url: str):
    """
    Processes video and returns the activity performed in it using machine learning.

    Input:
        video_url: video url to be processed

    Output:
        activity performed in the video
    """
    import numpy as np
    import joblib
    import os
    import json

    CLASSES = ["doing own work", "passing paper", "looking at other's work"]

    silhouettes = segmentation(video_url, 41)
    keypoints, middle_frame_image, boxes, track_ids, frame_keypoints = keypoints_extraction(video_url, 41)
    hof = hof_extraction(silhouettes)
    dist_feat = dist_feat_extraction(keypoints)
    angle_feat = angle_feat_extraction(keypoints)
    feat_vect = np.concatenate((dist_feat, angle_feat, hof), axis=1).reshape(1, -1)

    scalar = joblib.load("scaler_fold_2.joblib")
    feat_vect = scalar.transform(feat_vect)

    lda = joblib.load("lda_fold_2.joblib")
    feat_vect = lda.transform(feat_vect)

    svm = joblib.load("svm_fold_2.joblib")
    prediction = svm.predict(feat_vect)[0]
    
    return generate_pdf_report(silhouettes, keypoints, middle_frame_image,
                        boxes, track_ids, frame_keypoints, CLASSES[prediction], 
                        json.loads(os.environ["GOOGLE_APPLICATION_CREDENTIALS"]), 
                        os.environ["GCS_BUCKET_NAME"])
    


# segmentation
def segmentation(video_path, frames_no, batch_size=16):
    """Extract silhouettes for middle {frames_no} frames of a video and store in memory."""
    import numpy as np
    import torch
    import torchvision
    from torchvision.models.detection import maskrcnn_resnet50_fpn, MaskRCNN_ResNet50_FPN_Weights
    import cv2
    import time

    def silhouette_extraction(frame, prediction):
        """Extract grayscale silhouette from a given frame using segmentation masks."""

        new_width, new_height = 480, 320

        # Resize and convert to grayscale
        resized_frame = cv2.resize(frame, (new_width, new_height))
        gray_image = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)

        # Initialize empty mask
        masks_image = np.zeros_like(gray_image, dtype=np.uint8)

        # Process segmentation masks
        masks = prediction['masks']
        for i in range(masks.shape[0]):
            if prediction['labels'][i] == 1 and prediction['scores'][i] > 0.5:  # Person class
                mask = masks[i].cpu().numpy().squeeze()
                masks_image[mask > 0.4] = 1  # Apply threshold

        return gray_image * masks_image  # Multiply with grayscale frame

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # Load the pre-downloaded model
    model = maskrcnn_resnet50_fpn(weights=MaskRCNN_ResNet50_FPN_Weights.DEFAULT)
    model.to(device)
    model.eval()

    start_time = time.time()
    
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if total_frames < frames_no:
        raise ValueError(f"Video has only {total_frames} frames, but {frames_no} are required.")

    # Define the middle 50 frames
    start_frame = total_frames // 2 - (frames_no // 2)
    selected_frames = list(range(start_frame, start_frame + frames_no))

    silhouettes_list = []
    tensor_frames = []
    frames = []

    # --- Read frames ---
    for frame_no in selected_frames:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
        success, frame = cap.read()
        if not success:
            raise ValueError(f"Failed to read frame {frame_no} from the video!")

        frames.append(frame)

        # Convert frame to tensor
        resized_frame = cv2.resize(frame, (480, 320))
        resized_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
        transform = torchvision.transforms.ToTensor()
        tensor_frames.append(transform(resized_frame).unsqueeze(0))  # Add batch dimension

    cap.release()

    # --- Process in batches ---
    for i in range(0, len(tensor_frames), batch_size):
        batch = torch.cat(tensor_frames[i:i + batch_size], dim=0).to(device)

        with torch.no_grad():
            predictions = model(batch)

        # Extract silhouettes
        for j, prediction in enumerate(predictions):
            silhouette = silhouette_extraction(frames[i + j], prediction)
            silhouettes_list.append(silhouette)

    end_time = time.time()
    print(f"Segmentation completed in {end_time - start_time:.2f} seconds.")

    return np.array(silhouettes_list)

# keypoints extraction 
def keypoints_extraction(video_path, frames_no, batch_size=20):
    """Extract keypoints from the middle {frames_no} of frames using batch processing for speed."""
    import cv2
    import numpy as np
    from ultralytics import YOLO
    import torch
    import time

    # Define keypoints to retain
    SPECIFIC_INDEXES = [0, 5, 6, 7, 8, 9, 10]  # 7 keypoints per person
    NUM_KEYPOINTS = len(SPECIFIC_INDEXES)

    device = '0' if torch.cuda.is_available() else 'cpu'
    # Load YOLO model
    model = YOLO("yolo11n-pose.pt")
    
    start_time = time.time()

    # Open video
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Select middle frames_no of frames
    if total_frames < frames_no:
        raise ValueError(f"Video has only {total_frames} frames, but 40 frames are required.")

    start_frame = (total_frames // 2) - (frames_no // 2)
    selected_frames = list(range(start_frame, start_frame + frames_no))
    
    
    middle_frame_image = None
    middle_frame_boxes = None
    middle_frame_track_ids = None
    middle_frame_index = frames_no // 2

    # Placeholder for keypoints (frames_no, num_keypoints * 2, 2) → (x, y)
    keypoints = np.zeros((frames_no, NUM_KEYPOINTS * 2, 2), dtype=np.float32)

    # Process frames in batches of batch_size
    for batch_start in range(0, frames_no, batch_size):
        batch_frames = []
        batch_indices = selected_frames[batch_start: batch_start + batch_size]

        # Read batch frames
        for frame_num in batch_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            success, frame = cap.read()

            if not success:
                break
            batch_frames.append(frame)

        # Run YOLO inference on batch
        results = model.track(batch_frames, persist=True, max_det=2, classes=[0], verbose=False, device=device)

        # Process each frame in the batch
        for i, result in enumerate(results):
            global_index = batch_start + i
            # Extract keypoints and track IDs
            frame_keypoints = result.keypoints.data.cpu().numpy() if result.keypoints is not None else []
            track_ids = result.boxes.id.int().cpu().tolist() if result.boxes.id is not None else []
            boxes = result.boxes.xyxy.cpu().numpy() if result.boxes.xyxy is not None else []

              # Store middle frame info
            if global_index == middle_frame_index:
                middle_frame_image = batch_frames[i]  # store BGR image
                middle_frame_boxes = boxes            # shape: (2, 4)
                middle_frame_track_ids = track_ids    # list of 2 IDs
                middle_frame_keypoints = frame_keypoints

            # Ensure exactly 2 people are detected
            if len(track_ids) != 2:
                keypoints[global_index] = np.zeros((NUM_KEYPOINTS * 2, 2), dtype=np.float32)
                continue

            # Process keypoints for both persons
            for j, person_data in enumerate(frame_keypoints):  # Ensure only 2 persons
                for k, index in enumerate(SPECIFIC_INDEXES):
                    keypoints[global_index, j * NUM_KEYPOINTS + k] = person_data[index][:2]

    cap.release()

    first_frame = keypoints[0]

    sum_x_1 = first_frame[:NUM_KEYPOINTS][0].sum()  # First person's x-coordinates sum
    sum_x_2 = first_frame[NUM_KEYPOINTS:][0].sum()  # Second person's x-coordinates sum


    if sum_x_1 > sum_x_2:  # Right person stored first, so swap
        keypoints[:, :NUM_KEYPOINTS], keypoints[:, NUM_KEYPOINTS:] = (
            keypoints[:, NUM_KEYPOINTS:].copy(), keypoints[:, :NUM_KEYPOINTS].copy()
    )

    end_time = time.time()
    print(f"Keypoints extraction completed in {end_time - start_time:.2f} seconds.")

    return keypoints, middle_frame_image, middle_frame_boxes, middle_frame_track_ids, middle_frame_keypoints

# hof features extraction
def hof_extraction(silhouettes):
    """
    Processes a NumPy array of silhouette frames to compute HOF features.

    Input:
        silhouettes: np.ndarray of shape (num_frames, height, width)

    Output:
        hof_features_array: np.ndarray of shape (num_frames - 1, 18)
    """
    import numpy as np
    import cv2

    num_frames = silhouettes.shape[0]

    if num_frames < 2:
        raise ValueError("At least two frames are required to compute HOF.")

    hof_feat = np.zeros((num_frames - 1, 18), dtype=np.float32)

    for i in range(1, num_frames):  # Start from second frame

        prev_frame = silhouettes[i - 1]
        curr_frame = silhouettes[i]
        
        flow = cv2.calcOpticalFlowFarneback(prev_frame, curr_frame, None,
                                        pyr_scale=0.5, levels=3, winsize=15,
                                        iterations=3, poly_n=5, poly_sigma=1.2,
                                        flags=0)

        # Compute magnitude and angle of flow vectors
        magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1], angleInDegrees=True)

        # Compute HOF features (18-bin histogram)
        num_bins = 18
        bin_edges = np.linspace(0, 360, num_bins + 1)
        hof_features = np.histogram(angle, bins=bin_edges, weights=magnitude, density=True)[0]

        # Replace NaNs with zeros
        hof_features = np.nan_to_num(hof_features)

        # Compute HOF features
        hof_feat[i-1] = hof_features

    return hof_feat


# ltp features extraction
def ltp_feat_extraction(frames):
    """
    Process silhouette frames and extract LTP features in parallel.
    
    Input:
        silhouettes: np.ndarray of shape (num_frames, height, width)

    Output:
        ltp_features_array: np.ndarray of shape (num_frames, 512)
    """
    import numpy as np
    import cv2
    from scipy.ndimage import shift
    from joblib import Parallel, delayed

    num_frames = frames.shape[0]
    def extract_ltp_feat_for_frame(image, radius=1, neighbors=8, threshold=5):
        """
        Extract LTP histogram features efficiently.
        """
        image = image.astype(np.float32)
        padded_image = cv2.copyMakeBorder(image, radius, radius, radius, radius, cv2.BORDER_REFLECT)

        h, w = image.shape
        ltp_pos = np.zeros((h, w), dtype=np.uint8)
        ltp_neg = np.zeros((h, w), dtype=np.uint8)

        offsets = [
            (int(np.round(radius * np.sin(2 * np.pi * n / neighbors))),
            int(np.round(radius * np.cos(2 * np.pi * n / neighbors))))
            for n in range(neighbors)
        ]

        # Create stacked neighbor shifts
        neighbors_matrix = np.stack([
            shift(padded_image, shift=(dy, dx), mode='nearest')[radius:-radius, radius:-radius]
            for dy, dx in offsets
        ], axis=-1)  # Shape: (h, w, neighbors)

        center_matrix = image[..., None]  # Shape: (h, w, 1)
        diff = neighbors_matrix - center_matrix  # Compute differences

        # Compute LTP codes using NumPy boolean indexing (Vectorized)
        ltp_pos = np.sum((diff > threshold) * (1 << np.arange(neighbors)), axis=-1, dtype=np.uint8)
        ltp_neg = np.sum((diff < -threshold) * (1 << np.arange(neighbors)), axis=-1, dtype=np.uint8)

        # Compute histograms efficiently
        pos_hist = np.bincount(ltp_pos.ravel(), minlength=256)
        neg_hist = np.bincount(ltp_neg.ravel(), minlength=256)

        # Concatenate histograms and convert to float32
        return np.concatenate((pos_hist, neg_hist)).astype(np.float32)

    # Use Joblib for parallel processing
    features = Parallel(n_jobs=-1)(
        delayed(extract_ltp_feat_for_frame)(frames[i]) for i in range(1, num_frames)
    )

    return np.array(features, dtype=np.float32)


# velocity features extraction
def velocity_feat_extraction(keypoints):
    """
    Compute velocity features for each frame.

    Input:
        keypoints: np.ndarray of shape (num_frames, keypoints * 2, 2)

    Output:
        velocity_features: np.ndarray of shape (num_frames, num_features)
    """
    import numpy as np
    prev_coords = keypoints[:-1, :, :]  # All frames except last
    curr_coords = keypoints[1:, :, :]   # All frames except first

    # Compute Euclidean distance for velocity (frame-to-frame displacement)
    velocity_feat = np.linalg.norm(curr_coords - prev_coords, axis=2)  # Shape: (59, num_persons * num_keypoints)

    return velocity_feat


# angle features extraction
def angle_feat_extraction(keypoints):
    """
    Compute intra and inter angle changes for a given sequence of keypoints.

    Input:
        keypoints: np.ndarray of shape (num_frames, keypoints * 2, 2)

    Output:
        angles_feat: np.ndarray of shape (num_frames, num_features)
    """
    import numpy as np

    indices = {
        'N1': 0, 'LS1': 1, 'RS1': 2, 'LE1': 3, 'RE1': 4,
        'LW1': 5, 'RW1': 6,
        'N2': 7, 'LS2': 8, 'RS2': 9, 'LE2': 10, 'RE2': 11,
        'LW2': 12, 'RW2': 13,
    }
    
    intra_angle_mapping = {
        "N1": ["RS1", "LS1"], "RS1": ["RE1"], "LS1": ["LE1"],
        "RE1": ["RW1"], "LE1": ["LW1"],

        "N2": ["RS2", "LS2"], "RS2": ["RE2"], "LS2": ["LE2"],
        "RE2": ["RW2"], "LE2": ["LW2"],
    }

    inter_angle_mapping = {
        "LW1": ["RW2"], "LE1": ["RE2"], "LS1": ["RS1"],
    }
    keypoints = keypoints[1:]
    num_frames = keypoints.shape[0]
    num_features = sum(len(targets) for targets in intra_angle_mapping.values()) + \
                   sum(len(targets) for targets in inter_angle_mapping.values())

    angles_feat = np.zeros((num_frames, num_features), dtype=np.float32)

    for frame_idx in range(num_frames):
        feat_idx = 0
        coords = keypoints[frame_idx]  # Shape: (keypoints * 2, 2)

        # Compute intra-person angles
        for joint_name, target_joints in intra_angle_mapping.items():
            joint_idx = indices[joint_name]

            for target_joint in target_joints:
                target_joint_idx = indices[target_joint]

                delta_x = coords[target_joint_idx, 0] - coords[joint_idx, 0]
                delta_y = coords[target_joint_idx, 1] - coords[joint_idx, 1]
                angle = np.arctan2(delta_y, delta_x)

                angles_feat[frame_idx, feat_idx] = angle
                feat_idx += 1

        # Compute inter-person angles
        for joint_name, target_joints in inter_angle_mapping.items():
            joint_idx = indices[joint_name]

            for target_joint in target_joints:
                target_joint_idx = indices[target_joint]

                delta_x = coords[target_joint_idx, 0] - coords[joint_idx, 0]
                delta_y = coords[target_joint_idx, 1] - coords[joint_idx, 1]
                angle = np.arctan2(delta_y, delta_x)

                angles_feat[frame_idx, feat_idx] = angle
                feat_idx += 1

    return angles_feat



# distance features extraction
def dist_feat_extraction(keypoints):
    """
    Compute intra and inter distance changes for a given sequence of keypoints.

    Input:
        keypoints: np.ndarray of shape (num_frames, keypoints * 2, 2)

    Output:
        intra_inter_distances: np.ndarray of shape (num_frames, num_features)
    """
    import numpy as np

    indices = {
        'N1': 0, 'LS1': 1, 'RS1': 2, 'LE1': 3, 'RE1': 4,
        'LW1': 5, 'RW1': 6,
        'N2': 7, 'LS2': 8, 'RS2': 9, 'LE2': 10, 'RE2': 11,
        'LW2': 12, 'RW2': 13,
    }

    intra_distance_mapping = {
        "N1": ["RW1"], "LS1": ["LW1"], "RE1": ["RW1"], "LE1": ["LW1"],
        "N2": ["RW2"], "LS2": ["LW2"], "RE2": ["RW2"], "LE2": ["LW2"],
    }

    inter_distance_mapping = {
        "LS1": ["RS2"], "LW1": ["RW2"], "LE1": ["RE2"], "N1": ["N2"],
    }
    
    keypoints = keypoints[1:]
    num_frames = keypoints.shape[0]
    num_features = len(intra_distance_mapping) + len(inter_distance_mapping)

    dist_feat = np.zeros((num_frames, num_features), dtype=np.float32)

    for frame_idx in range(num_frames):
        feat_idx = 0
        coords = keypoints[frame_idx]  # Shape: (keypoints * 2, 2)

        # Compute intra-person distances
        for joint_name, target_joints in intra_distance_mapping.items():

            joint_idx = indices[joint_name]

            for target_joint in target_joints:
                target_joint_idx = indices[target_joint]
                euclidean_distance = np.linalg.norm(
                    coords[joint_idx] - coords[target_joint_idx]
                )
                dist_feat[frame_idx, feat_idx] = euclidean_distance
                feat_idx += 1

        # Compute inter-person distances
        for joint_name, target_joints in inter_distance_mapping.items():
            joint_idx = indices[joint_name]

            for target_joint in target_joints:
                target_joint_idx = indices[target_joint]

                euclidean_distance = np.linalg.norm(
                    coords[joint_idx] - coords[target_joint_idx]
                )
                dist_feat[frame_idx, feat_idx] = euclidean_distance
                feat_idx += 1

    return dist_feat


def add_page_number(canvas_obj, doc):
    page_num = canvas_obj.getPageNumber()
    text = f"{page_num}"  # just the number

    canvas_obj.setFont("Helvetica", 12)
    width = canvas_obj.stringWidth(text, "Helvetica", 12)

    # Position near bottom-right: 
    # X = page width - margin - text width
    # Y = small margin from bottom (e.g., 15)
    margin = 40
    x = doc.pagesize[0] - margin - width
    y = 15
    canvas_obj.drawString(x, y, text)

def compute_ltp_for_visualization(image, radius=1, neighbors=8, threshold=5):
    """
    Compute Local Ternary Patterns (LTP) for a grayscale image efficiently.
    Uses NumPy vectorized operations and SciPy shift to improve speed.
    """
    import cv2
    import numpy as np
    from scipy.ndimage import shift

    image = image.astype(np.float32)
    padded_image = cv2.copyMakeBorder(image, radius, radius, radius, radius, cv2.BORDER_REFLECT)

    h, w = image.shape
    ltp_pos = np.zeros((h, w), dtype=np.uint8)
    ltp_neg = np.zeros((h, w), dtype=np.uint8)

    offsets = [
        (int(np.round(radius * np.sin(2 * np.pi * n / neighbors))),
         int(np.round(radius * np.cos(2 * np.pi * n / neighbors))))
        for n in range(neighbors)
    ]

    # Create stacked neighbor shifts
    neighbors_matrix = np.stack([
        shift(padded_image, shift=(dy, dx), mode='nearest')[radius:-radius, radius:-radius]
        for dy, dx in offsets
    ], axis=-1)  # Shape: (h, w, neighbors)

    center_matrix = image[..., None]  # Shape: (h, w, 1)
    diff = neighbors_matrix - center_matrix  # Compute differences

    # Compute LTP codes using NumPy boolean indexing (Vectorized)
    ltp_pos = np.sum((diff > threshold) * (1 << np.arange(neighbors)), axis=-1, dtype=np.uint8)
    ltp_neg = np.sum((diff < -threshold) * (1 << np.arange(neighbors)), axis=-1, dtype=np.uint8)

    return ltp_pos, ltp_neg


def get_silhouette_contours(silhouette):

    import cv2
    import numpy as np
    # Find contours in the silhouette image
    contours, _ = cv2.findContours(silhouette, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours[0] if contours else np.array([])

def draw_optical_flow_on_contours(prev_frame, curr_frame, contours, step=16):

    import cv2
    import numpy as np

    flow = cv2.calcOpticalFlowFarneback(prev_frame, curr_frame, None,
                                        pyr_scale=0.5, levels=3, winsize=15,
                                        iterations=3, poly_n=5, poly_sigma=1.2,
                                        flags=0)

    vis = np.zeros_like(prev_frame) # black background

    # Convert to BGR for drawing arrows
    vis_bgr = cv2.cvtColor(vis, cv2.COLOR_GRAY2BGR)

    # Draw optical flow vectors on contour points
    for contour_point in contours:  # Use every `step`-th point on the contour
        x, y = contour_point[0]
        flow_vector = flow[y, x]
        end_point = (int(x + flow_vector[0]), int(y + flow_vector[1]))

        cv2.arrowedLine(vis_bgr, (x, y), end_point, (0, 255, 0), 1, tipLength=0.4)

    # Blend the silhouette with the black background and arrows
    vis_bgr[prev_frame > 0] = 255

    return vis_bgr


def calculate_angle(start_point, end_point):
    import math

    delta_x = end_point[0] - start_point[0]
    delta_y = end_point[1] - start_point[1]
    angle = math.degrees(math.atan2(delta_y, delta_x))
    return angle

def generate_pdf_report(silhouettes, keypoints, middle_frame_image,
                        boxes, track_ids, middle_frame_keypoints, classification_result,
                        storage_credentials, gcs_bucket, model_type="ml"):
    import cv2
    import matplotlib.pyplot as plt
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from io import BytesIO
    from google.oauth2 import service_account
    from google.cloud import storage
    from datetime import datetime
    import uuid
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.styles import ParagraphStyle
    import numpy as np

    # Constants
    middle_index = len(silhouettes) // 2
    SPECIFIC_INDEXES = [0, 5, 6, 7, 8, 9, 10]
    COLORS = {1: 'red', 2: 'blue', 3: 'yellow', 4: 'green'}
    styles = getSampleStyleSheet()

    centered_heading2_style = ParagraphStyle(
        name='CenteredHeading2',
        parent=styles['Heading2'],
        alignment=TA_CENTER
    )

    # Create an in-memory PDF buffer
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
    story = []

    # Title
    story.append(Paragraph('<font color="#9333ea">Exam Guard</font>', styles['Title']))
    story.append(Paragraph("Activity Classification Report", styles['Title']))
    story.append(Spacer(1, 20))

    # --- Original Frame ---
    buf_img = BytesIO()
    plt.figure(figsize=(6, 4))
    plt.imshow(cv2.cvtColor(middle_frame_image, cv2.COLOR_BGR2RGB))
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(buf_img, format='png', bbox_inches='tight', pad_inches=0)
    plt.close()
    buf_img.seek(0)

    story.append(Paragraph("Original Middle Frame", centered_heading2_style))
    story.append(Spacer(1, 8))
    story.append(Image(buf_img, width=480, height=320))
    story.append(Spacer(1, 170))

    # --- Silhouette ---
    middle_silhouette = silhouettes[middle_index].copy()
    middle_silhouette[middle_silhouette == 0] = 255

    buf_seg = BytesIO()
    plt.figure(figsize=(6, 4))
    plt.imshow(middle_silhouette, cmap='gray')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(buf_seg, format='png', bbox_inches='tight', pad_inches=0)
    plt.close()
    buf_seg.seek(0)

    story.append(Paragraph("Segmentation Result", centered_heading2_style))
    story.append(Spacer(1, 8))
    story.append(Image(buf_seg, width=480, height=320))
    story.append(Spacer(1, 260))

    buf_kp = BytesIO()

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.imshow(cv2.cvtColor(middle_frame_image, cv2.COLOR_BGR2RGB))
    ax.axis('off')

    # Plot keypoints and boxes of both persons
    for person_data, track_id in zip(middle_frame_keypoints, track_ids):  # Ensure only 2 persons
        for k, index in enumerate(SPECIFIC_INDEXES):
            ax.scatter(person_data[index][:2][0], person_data[index][:2][1], color=COLORS.get(track_id, 'pink'), s=40)

    for box, track_id in zip(boxes, track_ids):
        x_min, y_min, x_max, y_max = box
        ax.plot([x_min, x_max, x_max, x_min, x_min], [y_min, y_min, y_max, y_max, y_min], color= COLORS.get(track_id, 'green'), linewidth=2)
        # Visualize track ID
        ax.text(x_min, y_min - 20, f"ID {track_id}", color=COLORS.get(track_id, 'green'), fontsize=12, weight="bold")
    
    fig.tight_layout()
    fig.savefig(buf_kp, format='png', bbox_inches='tight', pad_inches=0)
    plt.close(fig)
    buf_kp.seek(0)

    story.append(Paragraph("Keypoints Detection Result", centered_heading2_style))
    story.append(Spacer(1, 8))
    story.append(Image(buf_kp, width=480, height=320))
    story.append(Spacer(1, 260))

    if model_type == "dl":
        middle_silhouette = silhouettes[middle_index].copy()
        # Create binary mask
        _, binary_mask = cv2.threshold(middle_silhouette, 1, 255, cv2.THRESH_BINARY)
        # Compute LTP features
        ltp_pos, ltp_neg = compute_ltp_for_visualization(middle_silhouette, 1, 8, 5)

        combined_ltp = ltp_pos + ltp_neg

        # Normalize LTP codes for visualization
        combined_ltp_norm = cv2.normalize(combined_ltp, None, 0, 255, cv2.NORM_MINMAX)

        # Apply jet colormap
        jet_colormap = plt.get_cmap('jet')
        colored_ltp = jet_colormap(combined_ltp_norm)[:, :, :3]  # Convert to RGB (0-1 float)

        # Create white background image
        white_bg = np.ones_like(colored_ltp)

        # Convert binary mask to 3-channel and boolean
        mask_3d = binary_mask[:, :, np.newaxis] > 0

        # Blend: where mask is True use colored_ltp, else use white
        ltp_image = np.where(mask_3d, colored_ltp, white_bg)

        # --- LTP frame ---
        buf_ltp = BytesIO()
        plt.figure(figsize=(6, 4))
        plt.imshow(ltp_image)
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(buf_ltp, format='png', bbox_inches='tight', pad_inches=0)
        plt.close()
        buf_ltp.seek(0)

        story.append(Paragraph("LTP features Visualization", centered_heading2_style))
        story.append(Spacer(1, 8))
        story.append(Image(buf_ltp, width=480, height=320))
        story.append(Spacer(1, 260))

    curr_silhouette = silhouettes[middle_index].copy()
    prev_silhouette = silhouettes[middle_index - 5].copy()
    contours = get_silhouette_contours(prev_silhouette)

    flow_image = draw_optical_flow_on_contours(prev_silhouette, curr_silhouette, contours)
    flow_image = 255 - flow_image

    pink = np.array([255, 0, 255])  # Pure pink (R=255, G=0, B=255)
    green = np.array([0, 255, 0])   # Pure green (R=0, G=255, B=0)

    # Create a mask for all pink pixels (exact match)
    pink_mask = (flow_image == pink).all(axis=-1)

    # Replace pink with green
    flow_image[pink_mask] = green

    buf_hof = BytesIO()
    plt.figure(figsize=(6, 4))
    plt.imshow(flow_image)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(buf_hof, format='png', bbox_inches='tight', pad_inches=0)
    plt.close()
    buf_hof.seek(0)

    story.append(Paragraph("HOF features Visualization", centered_heading2_style))
    story.append(Spacer(1, 8))
    story.append(Image(buf_hof, width=480, height=320))
    story.append(Spacer(1, 260))


    indices = {
        'N1': 0, 'LS1': 1, 'RS1': 2, 'LE1': 3, 'RE1': 4,
        'LW1': 5, 'RW1': 6,
        'N2': 7, 'LS2': 8, 'RS2': 9, 'LE2': 10, 'RE2': 11,
        'LW2': 12, 'RW2': 13,
    }


    intra_angle_mapping = {
        "N1": ["RS1", "LS1"],
        "RS1": ["RE1"],
        "LS1": ["LE1"],
        "RE1": ["RW1"],
        "LE1": ["LW1"],

        "N2": ["RS2", "LS2"],
        "RS2": ["RE2"],
        "LS2": ["LE2"],
        "RE2": ["RW2"],
        "LE2": ["LW2"]

    }

    inter_angle_mapping = {
        "LW1": ["RW2"],
        "LE1": ["RE2"],
        "LS1": ["RS2"]
    }

    middle_silhouette = silhouettes[middle_index].copy()

    height, width, _ = middle_frame_image.shape

    middle_silhouette = cv2.resize(middle_silhouette, (width, height))
    _, middle_silhouette = cv2.threshold(middle_silhouette, 0, 255, cv2.THRESH_BINARY_INV)
    middle_silhouette = cv2.cvtColor(middle_silhouette, cv2.COLOR_GRAY2BGR)

    mid_keypoint = keypoints[middle_index]

     # visualize keypoints
    for x, y in mid_keypoint:
        cv2.circle(middle_silhouette, (int(x), int(y)), 10, (0, 255, 0), -1)
    # Draw angles with lines and arcs
    for joint, connected_joints in intra_angle_mapping.items():

        start_point = (int(mid_keypoint[indices[joint]][0]),
                      int(mid_keypoint[indices[joint]][1]))

        if np.array_equal(start_point, [0, 0]):
          continue

        # Base line through the joint (x-axis)
        base_line_end = (start_point[0] + 50, start_point[1])
        base_line_start = (start_point[0] - 50, start_point[1])
        cv2.line(middle_silhouette, base_line_start, base_line_end, (0, 0, 0), 5)  # black base line

        for connected_joint in connected_joints:

            end_point = (int(mid_keypoint[indices[connected_joint]][0]),
                        int(mid_keypoint[indices[connected_joint]][1]))

            if np.array_equal(end_point, [0, 0]):
              continue

            # Draw the connecting line
            cv2.line(middle_silhouette, start_point, end_point, (0, 0, 255), 5)  # Red connecting line

            # Calculate angle between the base line and the connecting line
            angle = calculate_angle(start_point, end_point)

            # Draw the arc to represent the angle
            cv2.ellipse(middle_silhouette, start_point, (20, 20), 0, 0, angle, (0, 0, 255), 5)

     # Draw inter angles with lines and arcs
    for joint, connected_joints in inter_angle_mapping.items():

        start_point = (int(mid_keypoint[indices[joint]][0]),
                      int(mid_keypoint[indices[joint]][1]))

        if np.array_equal(start_point, [0, 0]):
          continue

        # Base line through the joint (x-axis)
        base_line_end = (start_point[0] + 50, start_point[1])
        base_line_start = (start_point[0] - 50, start_point[1])
        cv2.line(middle_silhouette, base_line_start, base_line_end, (0, 0, 0), 5)  # Green base line

        for connected_joint in connected_joints:
            end_point = (int(mid_keypoint[indices[connected_joint]][0]),
                        int(mid_keypoint[indices[connected_joint]][1]))

            if np.array_equal(end_point, [0, 0]):
              continue
            # Draw the connecting line
            cv2.line(middle_silhouette, start_point, end_point, (255, 0, 0), 5)  # Blue connecting line

            # Calculate angle between the base line and the connecting line
            angle = calculate_angle(start_point, end_point)

            # Draw the arc to represent the angle
            cv2.ellipse(middle_silhouette, start_point, (20, 20), 0, 0, angle, (255, 0, 0), 5)

    buf_angle = BytesIO()
    plt.figure(figsize=(6, 4))
    plt.imshow(middle_silhouette)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(buf_angle, format='png', bbox_inches='tight', pad_inches=0)
    plt.close()
    buf_angle.seek(0)

    story.append(Paragraph("Angle features Visualization", centered_heading2_style))
    story.append(Spacer(1, 8))
    story.append(Image(buf_angle, width=480, height=320))
    story.append(Spacer(1, 260))

        
    intra_distance_mapping = {
        "N1": ["RW1"],
        "LS1": ["LW1"],
        "RE1": ["RW1"],
        "LE1": ["LW1"],

        "N2": ["RW2"],
        "LS2": ["LW2"],
        "RE2": ["RW2"],
        "LE2": ["LW2"],
    }

    inter_distance_mapping = {
        "LS1": ["RS2"],
        "LW1": ["RW2"],
        "LE1": ["RE2"],
        "N1": ["N2"],
    }

    middle_silhouette = silhouettes[middle_index].copy()
    
    height, width, _  = middle_frame_image.shape
    middle_silhouette = cv2.resize(middle_silhouette, (width, height))
    _, middle_silhouette = cv2.threshold(middle_silhouette, 0, 255, cv2.THRESH_BINARY_INV)
    middle_silhouette = cv2.cvtColor(middle_silhouette, cv2.COLOR_GRAY2BGR)

    # visualize keypoints
    for x, y in mid_keypoint:
        cv2.circle(middle_silhouette, (int(x), int(y)), 10, (0, 255, 0), -1)

    # Draw intra distance
    for joint, connected_joints in intra_distance_mapping.items():
            start_point = (int(mid_keypoint[indices[joint]][0]),
                              int(mid_keypoint[indices[joint]][1]))
            if np.array_equal(start_point, [0, 0]):
               continue

            for connected_joint in connected_joints:
                end_point = (int(mid_keypoint[indices[connected_joint]][0]),
                            int(mid_keypoint[indices[connected_joint]][1]))
                if np.array_equal(end_point, [0, 0]):
                  continue
                cv2.line(middle_silhouette, start_point, end_point, (0, 0, 255), 5)  # Red line

    # Draw inter-distance blue lines
    for joint, connected_joints in inter_distance_mapping.items():
        start_point = (int(mid_keypoint[indices[joint]][0]),
                          int(mid_keypoint[indices[joint]][1]))
        if np.array_equal(start_point, [0, 0]):
          continue

        for connected_joint in connected_joints:
            end_point = (int(mid_keypoint[indices[connected_joint]][0]),
                        int(mid_keypoint[indices[connected_joint]][1]))
            if np.array_equal(end_point, [0, 0]):
              continue
            cv2.line(middle_silhouette, start_point, end_point, (255, 0, 0), 5)  # Blue line

    buf_dist = BytesIO()
    plt.figure(figsize=(6, 4))
    plt.imshow(middle_silhouette)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(buf_dist, format='png', bbox_inches='tight', pad_inches=0)
    plt.close()
    buf_dist.seek(0)

    story.append(Paragraph("Distance features Visualization", centered_heading2_style))
    story.append(Spacer(1, 8))
    story.append(Image(buf_dist, width=480, height=320))

    if model_type == "dl":
        story.append(Spacer(1, 260))
        curr_silhouette = silhouettes[middle_index].copy()
        curr_silhouette = cv2.resize(curr_silhouette, (width, height))
        _, curr_silhouette = cv2.threshold(curr_silhouette, 0, 255, cv2.THRESH_BINARY_INV)
        heatmap = cv2.cvtColor(curr_silhouette, cv2.COLOR_GRAY2BGR)

        curr_keypoint = keypoints[middle_index].copy()
        prev_keypoint = keypoints[middle_index - 5].copy()

        velocity = np.linalg.norm(curr_keypoint - prev_keypoint, axis=1)
        norm_velocity = (velocity - velocity.min()) / (velocity.max() - velocity.min() + 1e-6)  # avoid divide by 0

        threshold = 0.5  # Skip keypoints with velocity less than 5% of max
        for (x, y), v in zip(curr_keypoint, norm_velocity):
            if v < threshold:
                continue  # Skip low-intensity keypoints
            intensity = int(255 * v)
            cv2.circle(heatmap, (int(x), int(y)), 10, (intensity, 0, 0), -1)  # Blue channel for velocity

        buf_vel = BytesIO()
        plt.figure(figsize=(6, 4))
        plt.imshow(cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB))
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(buf_vel, format='png', bbox_inches='tight', pad_inches=0)
        plt.close()
        buf_vel.seek(0)

        story.append(Paragraph("Velocity features Visualization", centered_heading2_style))
        story.append(Spacer(1, 8))
        story.append(Image(buf_vel, width=480, height=320))

    story.append(Spacer(1, 20))

    if model_type == "dl":
        model_type = "Deep Learning Pipeline"
    else:
        model_type = "Machine Learning Pipeline"
    # --- Classification Result ---
    story.append(Paragraph("Classification Result", centered_heading2_style))
    story.append(Spacer(1, 8))
    story.append(Paragraph(f"<b>Predicted Activity by {model_type}:</b> {classification_result}", styles['Normal']))
    story.append(Spacer(1, 12))

    # Build PDF in memory
    doc.build(story,onFirstPage=add_page_number, onLaterPages=add_page_number)
    pdf_buffer.seek(0)

    # Upload to GCS
    credentials = service_account.Credentials.from_service_account_info(storage_credentials)
    client = storage.Client(credentials=credentials)
    bucket = client.bucket(gcs_bucket)

    # Unique filename
    filename = f"classification_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.pdf"
    blob = bucket.blob(filename)
    blob.upload_from_file(pdf_buffer, content_type='application/pdf')

    # print("public url", blob.public_url)

    return blob.public_url
