import modal

model_image = (
    modal.Image.debian_slim(python_version="3.11.11").apt_install("libgl1", "libglib2.0-0").pip_install("pandas==2.2.2", "numpy==1.26.4", 
    "scikit-learn==1.6.1", "ultralytics==8.3.88", "scipy==1.14.1", "joblib==1.4.2", "opencv-python==4.11.0.86", "fastapi[standard]")
    .add_local_file("scaler_fold_2.joblib", remote_path="/root/scaler_fold_2.joblib")
    .add_local_file("lda_fold_2.joblib", remote_path="/root/lda_fold_2.joblib").add_local_file("svm_fold_2.joblib", remote_path="/root/svm_fold_2.joblib")
    .add_local_file("best_model_fold_2.pth", remote_path="/root/best_model_fold_2.pth").add_local_file("scaler_angle_fold_2.joblib", remote_path="/root/scaler_angle_fold_2.joblib")
    .add_local_file("scaler_dist_fold_2.joblib", remote_path="/root/scaler_dist_fold_2.joblib").add_local_file("scaler_hof_fold_2.joblib", remote_path="/root/scaler_hof_fold_2.joblib")
    .add_local_file("scaler_ltp_fold_2.joblib", remote_path="/root/scaler_ltp_fold_2.joblib").add_local_file("scaler_vel_fold_2.joblib", remote_path="/root/scaler_vel_fold_2.joblib")
)

app = modal.App(name="model-deployment", image=model_image)


@app.function(gpu="T4")
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

    CLASSES = ["doing own work", "passing paper", "looking at other's work"]

    selected_features_len = {
        "dist": 12,
        "angle": 15,
        "hof": 18,
        "vel": 14,
        "ltp": 512
    }

    selected_features = ["dist", "angle", "hof", "vel", "ltp"]

    silhouettes = segmentation(video_url, 41)
    keypoints = keypoints_extraction(video_url, 41)
    hof = hof_extraction(silhouettes)
    dist = dist_feat_extraction(keypoints)
    angle = angle_feat_extraction(keypoints)
    vel = velocity_feat_extraction(keypoints)
    ltp = ltp_feat_extraction(silhouettes)
    
    X_test = np.concatenate((dist, angle, hof, vel, ltp), axis=1)
    X_test = np.expand_dims(X_test, axis=0)
    
    standard_X_test = None
    prev_feat_length = 0

    for feature in selected_features:
          X_test_subset = X_test[:, :, prev_feat_length:prev_feat_length + selected_features_len[feature]].reshape(X_test.shape[0], -1)

          scaler = joblib.load(f"scaler_{feature}_fold_2.joblib")
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
    num_layers = 2

    model = BiLSTM(input_dim, hidden_dim, num_classes, num_layers).to(device)

    # Load the saved model state
    model_path = "best_model_fold_2.pth"
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()

    # Convert input to tensor and move to device
    input_tensor = torch.tensor(X_test, dtype=torch.float32).to(device)  # Add batch dimension

    # Make prediction
    with torch.no_grad():
      output = model(input_tensor)
      prediction = torch.argmax(output, dim=1).item()

    return CLASSES[prediction]



@app.function(gpu="T4")
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

    CLASSES = ["doing own work", "passing paper", "looking at other's work"]

    silhouettes = segmentation(video_url, 41)
    keypoints = keypoints_extraction(video_url, 41)
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
    
    return CLASSES[prediction]

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
            # Extract keypoints and track IDs
            frame_keypoints = result.keypoints.data.cpu().numpy() if result.keypoints is not None else []
            track_ids = result.boxes.id.int().cpu().tolist() if result.boxes.id is not None else []

            # Ensure exactly 2 people are detected
            if len(track_ids) != 2:
                keypoints[batch_start + i] = np.zeros((NUM_KEYPOINTS * 2, 2), dtype=np.float32)
                continue

            # Process keypoints for both persons
            for j, person_data in enumerate(frame_keypoints):  # Ensure only 2 persons
                for k, index in enumerate(SPECIFIC_INDEXES):
                    keypoints[batch_start + i, j * NUM_KEYPOINTS + k] = person_data[index][:2]

    cap.release()

    first_frame = keypoints[0]

    sum_x_1 = first_frame[:NUM_KEYPOINTS][0].sum()  # First person's nose x-coordinate
    sum_x_2 = first_frame[NUM_KEYPOINTS:][0].sum()  # Second person's nose x-coordinate


    if sum_x_1 > sum_x_2:  # Right person stored first, so swap
        keypoints[:, :NUM_KEYPOINTS], keypoints[:, NUM_KEYPOINTS:] = (
            keypoints[:, NUM_KEYPOINTS:].copy(), keypoints[:, :NUM_KEYPOINTS].copy()
    )

    end_time = time.time()
    print(f"Keypoints extraction completed in {end_time - start_time:.2f} seconds.")
    return keypoints

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
