# 🎓 Student Activity Classification System (Final Year Project)

**An intelligent AI-powered system for recognizing student activities from classroom video footage using advanced machine learning and deep learning pipelines.**

[🔗 Live Demo](https://fyp-frontend-ajmm.onrender.com)  
🎬 [Watch Video Demo](#) <!-- Replace with your actual YouTube/demo link -->

---

## 🚀 Overview

This project is a web-based platform built as part of our **Final Year Project**, aimed at automating the classification of student activities like **passing paper**, **looking at others' work**, and **doing own work** in a classroom setting. The system leverages two separate systems: **machine learning based pipeline** and **deep learning based pipeline** for classification.

It combines:
- 💡 **Computer Vision**
- 🧠 **Machine Learning & Deep Learning**
- ☁️ **Cloud-Based Deployment**

---

## 🧠 Core AI Pipelines

### 🔍 Segmentation with Mask R-CNN
- Utilizes **pre-trained Mask R-CNN** (from COCO dataset) for person-level segmentation
- Converts frames into **grayscale silhouettes** to reduce background noise and highlight body motion

📸 _Recommended Image Placement:_
```markdown
![Segmentation Results](assets/segmentation_output.png)
```

---

### 📐 Machine Learning Pipeline
- **Features Used:**  
  - Histogram of Optical Flow (HOF)  
  - Keypoint Angles  
  - Inter/Intra-body Distances  
- **Optimization:**  
  - **Fisher’s Linear Discriminant Analysis (LDA)** for dimensionality reduction  
- **Classifier:**  
  - **Multi-class Support Vector Machine (SVM)** with Sigmoid kernel  

📊 _Performance:_  
- **Accuracy:** 79.84%  
- **Best for:** Simpler or lightweight usage

📸 _Recommended Image Placement:_
```markdown
![ML Pipeline Architecture](assets/ml_pipeline_arch.png)
![LDA Visualization](assets/lda_plot.png)
```

---

### 🔁 Deep Learning Pipeline
- **Features Used:** All five: HOF, Angles, Distances, Velocity, and Local Ternary Patterns (LTP)
- **Classifier:** **Bidirectional LSTM (BiLSTM)**
- **Input:** Frame-level matrix with concatenated features  
- **Output:** Softmax classification into one of the three interaction categories

📊 _Performance:_  
- **Accuracy:** 92.38%  
- **Best for:** More nuanced and context-heavy interactions

📸 _Recommended Image Placement:_
```markdown
![BiLSTM Architecture](assets/bilstm_architecture.png)
```

---

## 📊 Experimental Results

| Model | Accuracy | Avg. Precision | Avg. Recall | Avg. F1-Score |
|-------|----------|----------------|-------------|---------------|
| Machine Learning (SVM) | 79.84% | 0.79 | 0.80 | 0.79 |
| Deep Learning (BiLSTM) | 92.38% | 0.92 | 0.93 | 0.92 |

📸 _Recommended Image Placement:_
```markdown
![Confusion Matrix Comparison](assets/confusion_matrices.png)
```

---

## 🧰 Tools, Technologies & Skills Used

### 📦 AI/ML & Deep Learning
- **Python**, **Google Colab**, **NumPy**, **Pandas**
- **PyTorch** (for BiLSTM)
- **Scikit-learn** (for SVM, LDA)
- **OpenCV**, **Matplotlib**
- **Mask R-CNN**, **Ultralytics YOLOv11-Pose** for keypoint detection

### 🌐 Full Stack Development
- **Frontend:** Next.js (React)
- **Backend:** Django + Django REST Framework
- **Cloud Storage:** Google Cloud Storage (GCS)
- **Database:** MongoDB Atlas
- **Model Hosting:** Modal (AI Inference)

### 🧪 Dev & Ops
- **Visual Studio Code**, **Postman**, **Git/GitHub**, **Render (Hosting)**

---

## 💡 System Features

- Role-based access (Admin, Subscribed, Unsubscribed)
- Model selection (ML or DL)
- Secure login & OTP verification
- Cloud video storage for subscribed users
- Historical classification results and visualization
- Admin dashboard for user/subscription management

📸 _Recommended Image Placement:_
```markdown
![App Screenshot – Upload & Classify](assets/frontend_classify_ui.png)
![Admin Panel](assets/admin_panel_ui.png)
```

---

## 🧪 How to Use Locally

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/fyp-interaction-classification.git
```

### 2. Run Frontend (Next.js)
```bash
cd frontend
npm install
npm run dev
```

### 3. Run Backend (Django)
```bash
cd backend
python manage.py runserver
```

> _Note: ML/DL models are deployed remotely and integrated via REST APIs. For retraining or experimentation, use the provided Jupyter notebooks on Google Colab._

---

## 📽 Demo Video

🎬 _You can embed the video here:_
```markdown
[![Watch the demo](assets/demo_thumbnail.png)](https://your-demo-video-link.com)
```

---

## 📁 Assets Folder

Create an `assets/` folder in your repo and include:
- `segmentation_output.png`
- `ml_pipeline_arch.png`
- `lda_plot.png`
- `bilstm_architecture.png`
- `confusion_matrices.png`
- `frontend_classify_ui.png`
- `admin_panel_ui.png`
- `demo_thumbnail.png` (optional)

---

## 🤝 Acknowledgements

Special thanks to:
- **Dr. Ahmad Jalal** – Project Supervisor
- Our peers, friends, and families for support
- Open-source community for the incredible libraries and tools

---

## ⭐ Final Notes

This project represents months of dedicated research and engineering, blending AI innovation with real-world educational needs. It's designed to be scalable, deployable, and adaptable to other human activity classification domains.

If you find this project interesting, consider ⭐ starring the repo or reaching out for collaboration!

---
