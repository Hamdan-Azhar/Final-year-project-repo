from modal import Function

c = Function.from_name("model-deployment", "predict_dl")

# url = "https://storage.googleapis.com/fyp-data-bucket/20250412180444_22_3.mp4"
url = "https://storage.googleapis.com/fyp-data-bucket/20250412180014_75_3.mp4"
# url = "https://storage.googleapis.com/fyp-data-bucket/20250511153850_31_3.mp4"
# url = "https://storage.googleapis.com/fyp-data-bucket/20250420154210_25_3.mp4"
# url = "https://storage.googleapis.com/fyp-data-bucket/20250403200938_23_1.mp4"
# url = "https://storage.googleapis.com/fyp-data-bucket/20250511154221_38_2.mp4"
# url = "https://storage.googleapis.com/fyp-data-bucket/20250328065203_3_2.MOV"
# url = "https://storage.googleapis.com/fyp-data-bucket/20250403195252_23_1.mp4"
print(c.remote(url))

