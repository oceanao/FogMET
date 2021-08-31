import tensorflow as tf
print(tf.__version__)
import tensorflow_datasets as tfds
import os
os.environ['CUDA_VISIBLE_DEVICES']='1' # '1','2'
tfds.disable_progress_bar()
BATCH_SIZE = 5
IMG_WIDTH = 256
IMG_HEIGHT = 256
project_label = ""
mount_path = None
drive_project_path = None
test_split = 0.2 #

from lib.dataset import DatasetInitializer
datasetInit = DatasetInitializer(256, 256)
datasetInit.dataset_path = './dataset/'
(train_clear, train_fog), (test_clear, test_fog), (sample_clear, sample_fog) = datasetInit.prepare_dataset(
    BATCH_SIZE,
    test_split=test_split,
    random_seed=7)

from lib.models import ModelsBuilder
OUTPUT_CHANNELS = 3
models_builder = ModelsBuilder()
use_transmission_map = False
use_gauss_filter = False
use_resize_conv = False

generator_clear2fog = models_builder.build_generator(use_transmission_map=use_transmission_map,
                                                     use_gauss_filter=use_gauss_filter,
                                                     use_resize_conv=use_resize_conv)
generator_fog2clear = models_builder.build_generator(use_transmission_map=False)


use_intensity_for_fog_discriminator = False
discriminator_fog = models_builder.build_discriminator(use_intensity=use_intensity_for_fog_discriminator)
discriminator_clear = models_builder.build_discriminator(use_intensity=False)

weights_path = "./weights/"

from lib.train import Trainer
trainer = Trainer(generator_clear2fog, generator_fog2clear,
                 discriminator_fog, discriminator_clear)

trainer.configure_checkpoint(weights_path = weights_path, load_optimizers=False)

from lib.plot import plot_clear2fog_intensity,clear2fog_intensity

import cv2
from lib.tools import create_dir

# intensity_path='/common/ahy/dataset/metdata/cyclegan'
intensity_path='/common/ahy/dataset/metdata/cyc'
# clear_input="/common/ahy/SMET/Scripts/SMET/dataset/cityscapes/test_img"
# clear_input="/common/ahy/SMET/Scripts/SMET/dataset/udacity/testing/center"
# clear_input="/common/ahy/dataset/udacity"
clear_input="/common/ahy/dataset/udas"
density={'light':0.1,'heavy':0.3,'dense':0.5,'strong':0.8,'extra':0.9} #density
def create_density():
    for d in density:
        bit=density[d]
        create_dir(intensity_path+"/"+d+"/")
        for filename in os.listdir(clear_input):
            file_path=clear_input+"/"+filename
            image_clear = tf.io.decode_png(tf.io.read_file(file_path), channels=3)
            image_clear, _ = datasetInit.preprocess_image_test(image_clear, 0)
            fig = clear2fog_intensity(generator_clear2fog, image_clear, bit)
            img=cv2.resize(fig*255,(480,480))
            cv2.imwrite(os.path.join(intensity_path+"/"+d+"/"+filename),img)
            print(os.path.join(intensity_path+"/"+d+"/"+filename))
create_density()
