import sys
import tensorflow as tf
print(tf.__version__)
import tensorflow_datasets as tfds

import os
from IPython.display import clear_output
os.environ['CUDA_VISIBLE_DEVICES']='1' # '1','2'
tfds.disable_progress_bar()
BATCH_SIZE = 5
IMG_WIDTH = 256
IMG_HEIGHT = 256
project_label = "" #@param {type:"string"}
mount_path = None #to suppress warnings
drive_project_path = None
test_split = 0.2 #@param {type:"slider", min:0.05, max:0.95, step:0.05}

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
use_transmission_map = False #@param{type: "boolean"}
use_gauss_filter = False #@param{type: "boolean"}
use_resize_conv = False #@param{type: "boolean"}
generator_clear2fog = models_builder.build_generator(use_transmission_map=use_transmission_map,
                                                     use_gauss_filter=use_gauss_filter,
                                                     use_resize_conv=use_resize_conv)
generator_fog2clear = models_builder.build_generator(use_transmission_map=False)
# tf.keras.utils.plot_model(generator_clear2fog, show_shapes=True, dpi=64, to_file='generator_clear2fog.png');
# tf.keras.utils.plot_model(generator_fog2clear, show_shapes=True, dpi=64, to_file='generator_fog2clear.png');

use_intensity_for_fog_discriminator = False #@param{type: "boolean"}
discriminator_fog = models_builder.build_discriminator(use_intensity=use_intensity_for_fog_discriminator)
discriminator_clear = models_builder.build_discriminator(use_intensity=False)
#
# tf.keras.utils.plot_model(discriminator_fog, show_shapes=True, dpi=64, to_file="discriminator_fog.png");
# tf.keras.utils.plot_model(discriminator_clear, show_shapes=True, dpi=64, to_file="discriminator_clear.png");

weights_path = "./weights/"
from lib.train import Trainer
trainer = Trainer(generator_clear2fog, generator_fog2clear,
                 discriminator_fog, discriminator_clear)

trainer.configure_checkpoint(weights_path = weights_path, load_optimizers=False)
from lib.plot import plot_generators_predictions
for clear, fog in tf.data.Dataset.zip((sample_clear.take(1), sample_fog.take(1))):
    plot_generators_predictions(generator_clear2fog, clear, generator_fog2clear, fog)
from lib.plot import plot_discriminators_predictions
for clear, fog in tf.data.Dataset.zip((sample_clear.take(1), sample_fog.take(1))):
    plot_discriminators_predictions(discriminator_clear, clear, discriminator_fog, fog, use_intensity_for_fog_discriminator)
#train
use_tensorboard = True #@param{type:"boolean"}
# if use_tensorboard:
#     import tensorboard
#     tb = tensorboard.program.TensorBoard()
#     tb.configure(argv=[None, '--logdir', trainer.tensorboard_base_logdir])
#     url = tb.launch()
#     print(url)

trainer.load_config()
use_transmission_map_loss=True #@param{type: "boolean"}
use_whitening_loss=True #@param{type: "boolean"}
use_rgb_ratio_loss=True #@param{type: "boolean"}
save_optimizers=False #@param{type: "boolean"}

trainer.train(
    train_clear, train_fog,
    epochs=100,
    clear_output_callback=lambda: clear_output(wait=True),
    use_tensorboard=use_tensorboard,
    sample_test=(sample_clear, sample_fog),
    load_config_first=False,
    use_transmission_map_loss=use_transmission_map_loss,
    use_whitening_loss=use_whitening_loss,
    use_rgb_ratio_loss=use_rgb_ratio_loss,
    save_optimizers=save_optimizers,
    use_intensity_for_fog_discriminator=use_intensity_for_fog_discriminator
)

# TODO: store predictions
for clear, fog in zip(test_clear.take(5), test_fog.take(5)):
    plot_generators_predictions(generator_clear2fog, clear, generator_fog2clear, fog)
for clear, fog in zip(sample_clear, sample_fog):
    plot_generators_predictions(generator_clear2fog, clear, generator_fog2clear, fog)
from lib.plot import plot_clear2fog_intensity
from matplotlib import pyplot as plt

intensity_path = './intensity/'
from lib.tools import create_dir
create_dir(intensity_path)

image_clear = next(iter(test_clear))[0][0]
step = 0.05
for (ind, i) in enumerate(tf.range(0,1+step, step)):
    fig = plot_clear2fog_intensity(generator_clear2fog, image_clear, i)
    fig.savefig(os.path.join(intensity_path
                             , "{:02d}_intensity_{:0.2f}.jpg".format(ind,i)), bbox_inches='tight', pad_inches=0)


