# imp dl: 75_3, 38_2, 17_1
# imp ml: 23_1, 25_3, 18_2, 17_``

# # from modal import Function

# # c = Function.from_name("model-deployment", "predict_dl")

# # # url = "https://storage.googleapis.com/fyp-data-bucket/20250412180444_22_3.mp4"
# # url = "https://storage.googleapis.com/fyp-data-bucket/20250412180014_75_3.mp4"
# # # url = "https://storage.googleapis.com/fyp-data-bucket/20250511153850_31_3.mp4"
# # # url = "https://storage.googleapis.com/fyp-data-bucket/20250420154210_25_3.mp4"
# # # url = "https://storage.googleapis.com/fyp-data-bucket/20250403200938_23_1.mp4"
# # # url = "https://storage.googleapis.com/fyp-data-bucket/20250511154221_38_2.mp4"
# # # url = "https://storage.googleapis.com/fyp-data-bucket/20250328065203_3_2.MOV"
# # # url = "https://storage.googleapis.com/fyp-data-bucket/20250403195252_23_1.mp4"
# # print(c.remote(url))
# import cv2
# import numpy as np
# import matplotlib.pyplot as plt
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
# from reportlab.lib.pagesizes import letter
# from reportlab.lib.styles import getSampleStyleSheet
# from io import BytesIO
# from datetime import datetime
# from reportlab.lib.enums import TA_CENTER
# from reportlab.lib.styles import ParagraphStyle


# def add_page_number(canvas_obj, doc):
#     page_num = canvas_obj.getPageNumber()
#     text = f"{page_num}"  # just the number

#     canvas_obj.setFont("Helvetica", 12)
#     width = canvas_obj.stringWidth(text, "Helvetica", 12)

#     # Position near bottom-right: 
#     # X = page width - margin - text width
#     # Y = small margin from bottom (e.g., 15)
#     margin = 40
#     x = doc.pagesize[0] - margin - width
#     y = 15
#     canvas_obj.drawString(x, y, text)

# def test_generate_pdf_report():
#     # Dummy Constants
#     SPECIFIC_INDEXES = [0, 5, 6, 7, 8, 9, 10]
#     COLORS = {1: 'red', 2: 'blue', 3: 'yellow', 4: 'green'}
#     styles = getSampleStyleSheet()

#     # Dummy Data
#     height, width = 480, 640
#     silhouettes = [np.random.randint(0, 2, (height, width), dtype=np.uint8) * 255 for _ in range(3)]
#     keypoints = [
#         [np.random.randint(100, 400, (17, 2)) for _ in range(2)] for _ in range(3)
#     ]
#     middle_frame_image = np.full((height, width, 3), 200, dtype=np.uint8)
#     boxes = [[150, 100, 300, 300], [320, 120, 470, 310]]
#     track_ids = [1, 2]
#     classification_result = "Running"

#     middle_index = len(silhouettes) // 2

#     centered_heading2_style = ParagraphStyle(
#         name='CenteredHeading2',
#         parent=styles['Heading2'],
#         alignment=TA_CENTER
#     )

#     # PDF setup
#     doc = SimpleDocTemplate("test_classification_report.pdf", pagesize=letter)
#     story = []
#     story.append(Paragraph('<font color="#9333ea">Exam Guard</font>', styles['Title']))
#     story.append(Paragraph("Activity Classification Report", styles['Title']))
#     story.append(Spacer(1, 20))

#     # --- Original Middle Frame ---
#     buf_img = BytesIO()
#     plt.figure(figsize=(6, 4))
#     plt.imshow(cv2.cvtColor(middle_frame_image, cv2.COLOR_BGR2RGB))
#     plt.axis('off')
#     plt.tight_layout()
#     plt.savefig(buf_img, format='png', bbox_inches='tight', pad_inches=0)
#     plt.close()
#     buf_img.seek(0)
#     story.append(Paragraph("Original Middle Frame", centered_heading2_style))
#     story.append(Spacer(1, 8))
#     story.append(Image(buf_img, width=480, height=320))
#     story.append(Spacer(1, 170))

#     # --- Silhouette ---
#     middle_silhouette = silhouettes[middle_index]
#     middle_silhouette[middle_silhouette == 0] = 255
#     buf_seg = BytesIO()
#     plt.figure(figsize=(6, 4))
#     plt.imshow(middle_silhouette, cmap='gray')
#     plt.axis('off')
#     plt.tight_layout()
#     plt.savefig(buf_seg, format='png', bbox_inches='tight', pad_inches=0)
#     plt.close()
#     buf_seg.seek(0)
#     story.append(Paragraph("Segmentation Result", centered_heading2_style))
#     story.append(Spacer(1, 8))
#     story.append(Image(buf_seg, width=480, height=320))
#     story.append(Spacer(1, 260))

#     # --- Keypoints ---
#     frame_keypoints = keypoints[middle_index]
#     buf_kp = BytesIO()
#     fig, ax = plt.subplots(figsize=(6, 4))
#     ax.imshow(cv2.cvtColor(middle_frame_image, cv2.COLOR_BGR2RGB))
#     ax.axis('off')
#     ax.set_title("Middle Frame with Keypoints")

#     for person_data, track_id in zip(frame_keypoints, track_ids):
#         for index in SPECIFIC_INDEXES:
#             ax.scatter(person_data[index][0], person_data[index][1],
#                        color=COLORS.get(track_id, 'pink'), s=40)

#     for box, track_id in zip(boxes, track_ids):
#         x_min, y_min, x_max, y_max = box
#         ax.plot([x_min, x_max, x_max, x_min, x_min],
#                 [y_min, y_min, y_max, y_max, y_min],
#                 color=COLORS.get(track_id, 'green'), linewidth=2)
#         ax.text(x_min, y_min - 20, f"ID {track_id}", color=COLORS.get(track_id, 'green'),
#                 fontsize=12, weight="bold")

#     fig.tight_layout()
#     fig.savefig(buf_kp, format='png', bbox_inches='tight', pad_inches=0)
#     plt.close(fig)
#     buf_kp.seek(0)

#     story.append(Paragraph("Keypoints Detection Result", styles['Heading2']))
#     story.append(Spacer(1, 8))
#     story.append(Image(buf_kp, width=480, height=320))
#     story.append(Spacer(1, 20))

#     # --- Classification Result ---
#     story.append(Paragraph("Classification Result", styles['Heading2']))
#     story.append(Spacer(1, 8))
#     story.append(Paragraph(f"<b>Predicted Activity:</b> {classification_result}", styles['Normal']))
#     story.append(Spacer(1, 12))

#     # Save PDF to disk
#     doc.build(story,onFirstPage=add_page_number, onLaterPages=add_page_number)
#     print("✅ PDF saved as test_classification_report.pdf")

# if __name__ == "__main__":
#     test_generate_pdf_report()

# import matplotlib.pyplot as plt
# import seaborn as sns
# import numpy as np

# # Class labels
# classes = ["Doing own work", "Passing paper", "Looking at other's work"]

# # Confusion matrices
# cm1 = np.array([
#     [0.90, 0.00, 0.10],
#     [0.00, 0.97, 0.03],
#     [0.13, 0.07, 0.80]
# ])

# cm2 = np.array([
#     [0.90, 0.00, 0.10],
#     [0.07, 0.90, 0.03],
#     [0.17, 0.00, 0.83]
# ])

# # Setup figure
# fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# # Plot each confusion matrix
# titles = ["DL Pipeline - Confusion Matrix", "ML Pipeline - Confusion Matrix"]

# for ax, cm, title in zip(axes, [cm1, cm2], titles):
#     sns.heatmap(cm, annot=True, fmt=".2f", cmap="Blues", xticklabels=classes, yticklabels=classes, ax=ax, cbar=False)
#     ax.set_title(title, fontsize=14)
#     ax.set_xlabel("Predicted Label", fontsize=12)
#     ax.set_ylabel("True Label", fontsize=12)
#     ax.tick_params(axis='x', rotation=30)
#     ax.tick_params(axis='y', rotation=30)

# plt.tight_layout()

# # Save the figure
# plt.savefig("confusion_matrices.png", dpi=300)

# # Display the figure
# plt.show()

# import matplotlib.pyplot as plt
# import numpy as np

# # Metric values for ML Pipeline
# ml_precision = [0.80883838, 1.0, 0.86349206]
# ml_recall = [0.89722222, 0.91111111, 0.83333333]
# ml_f1 = [0.84898589, 0.95215311, 0.83832442]
# ml_mean_precision = np.mean(ml_precision)
# ml_mean_recall = np.mean(ml_recall)
# ml_mean_f1 = np.mean(ml_f1)

# # Metric values for DL Pipeline
# dl_precision = [0.86969697, 0.93333333, 0.85555556]
# dl_recall = [0.91111111, 0.97222222, 0.8]
# dl_f1 = [0.88615137, 0.94847021, 0.82631579]
# dl_mean_precision = np.mean(dl_precision)
# dl_mean_recall = np.mean(dl_recall)
# dl_mean_f1 = np.mean(dl_f1)

# # Class names
# classes = ["Doing own work", "Passing paper", "Looking at others"]

# # Create figure
# fig, axes = plt.subplots(1, 2, figsize=(16, 6))
# fig.suptitle("Pipeline Evaluation Metrics", fontsize=16, fontweight='bold')

# def plot_metrics_table(ax, pipeline_name, precision, recall, f1, mean_precision, mean_recall, mean_f1):
#     data = []
#     for i in range(len(classes)):
#         data.append([classes[i], f"{precision[i]:.2f}", f"{recall[i]:.2f}", f"{f1[i]:.2f}"])
#     data.append(["Average", f"{mean_precision:.2f}", f"{mean_recall:.2f}", f"{mean_f1:.2f}"])

#     col_labels = ["Class", "Precision", "Recall", "F1 Score"]
#     cell_colours = []

#     for i in range(len(data)):
#         if i == len(data) - 1:  # Average row
#             cell_colours.append(["#f0f0f0"] * 4)
#         elif i % 2 == 0:
#             cell_colours.append(["#f8f9fa"] * 4)
#         else:
#             cell_colours.append(["#ffffff"] * 4)

#     table = ax.table(cellText=data, colLabels=col_labels, cellColours=cell_colours,
#                      loc='center', cellLoc='center', colLoc='center')

#     for (row, col), cell in table.get_celld().items():
#         if row == 0:
#             cell.set_fontsize(12)
#             cell.set_text_props(weight='bold', color='black')
#             cell.set_facecolor("#cfe2ff")
#         else:
#             cell.set_fontsize(11)

#     # table.scale(1, 2)
#     table.scale(1.5, 2.5)
#     ax.axis('off')
#     ax.set_title(pipeline_name, fontsize=14, fontweight='bold')

# # Plot the two metric tables
# plot_metrics_table(axes[0], "DL Pipeline", dl_precision, dl_recall, dl_f1,
#                    dl_mean_precision, dl_mean_recall, dl_mean_f1)

# plot_metrics_table(axes[1], "ML Pipeline", ml_precision, ml_recall, ml_f1,
#                    ml_mean_precision, ml_mean_recall, ml_mean_f1)

# # Save image
# plt.tight_layout(rect=[0, 0, 1, 0.95])
# plt.savefig("pipeline_metrics_corrected.png", dpi=300)
# plt.show()
