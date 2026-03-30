from deepface import DeepFace

models = [
  "VGG-Face",
  "Facenet",
  "Facenet512",
  "OpenFace",
  "DeepFace",
  "DeepID",
  "ArcFace",
  "Dlib",
  "SFace",
  "GhostFaceNet"
]

result = DeepFace.verify(
  img1_path ="2.jpg",
  img2_path ="2.jpg",
  model_name= "Dlib"
)
print(result)

objs = DeepFace.analyze(
  img_path ="2.jpg",
  actions = ['age', 'gender', 'race', 'emotion']
)

print(objs)