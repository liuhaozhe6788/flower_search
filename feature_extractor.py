from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.vgg19 import VGG19, preprocess_input
from tensorflow.keras.models import Model
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
import numpy as np

class FeatureExtractor:
    def __init__(self):
        """
        VGG19模型的初始化
        """
        self.base_model = VGG19(weights="imagenet")  # 使用了转移学习
        self.model = Model(inputs=self.base_model.input, outputs=self.base_model.get_layer("fc1").output)  # fc1层输出

    def extract(self, imgs):
        """
        从图片中提取出特征向量
        :param imgs:使用PILLOW读取的图片列表
        :return:特征向量
        """
        height = 224
        width = 224
        processed_imgs = list(map(lambda x: image.img_to_array(x.resize((height, width)).convert("RGB")), imgs))
        del imgs
        x = np.asarray(processed_imgs)
        # print(np.shape(x))
        # print(self.model.predict(x))
        features = self.model.predict(x)  
        return features/np.linalg.norm(features, axis=1, keepdims=True) # 标准化