import os
import sys
from collections import defaultdict
import torch
from torchvision.datasets import (
    VisionDataset, ImageFolder,
    CIFAR10, CIFAR100, ImageNet, CocoCaptions, Flickr8k, Flickr30k, Food101, SUN397,
    StanfordCars, FGVCAircraft, DTD, OxfordIIITPet, Caltech101, Flowers102,
    MNIST, STL10, EuroSAT, GTSRB, Kitti, Country211, PCAM, RenderedSST2
)
from . import voc2007, flickr, caltech101
from torch.utils.data import default_collate
from PIL import Image


def build_dataset(dataset_name, root="root", transform=None, split="test", download=True, annotation_file=None, **kwargs):
    """
    Main function to use in order to build a dataset instance,

    dataset_name: str
        name of the dataset
    
    root: str
        root folder where the dataset is downloaded and stored. can be shared among datasets.

    transform: torchvision transform applied to images

    split: str
        split to use, depending on the dataset can have different options.
        In general, `train` and `test` are available.
    
    annotation_file: str or None
        only for datasets with captions (used for retrieval) such as COCO
        and Flickr.
    """
    train = (split == "train")
    if dataset_name == "cifar10":
        return CIFAR10(root=root, train=train, transform=transform, download=download, **kwargs)
    elif dataset_name == "cifar100":
        return CIFAR100(root=root, train=train, transform=transform, download=download, **kwargs)
    elif dataset_name == "imagenet1k":
        ds =  ImageNet(root=root, split="train" if train else "val", transform=transform, **kwargs)
        # use classnames from OpenAI
        ds.classes = classnames["imagenet1k"]
        return ds
    elif dataset_name == "voc2007":
        return voc2007.PASCALVoc2007(root=root, set="train" if train else "test", transform=transform, download=download, **kwargs)
    elif dataset_name == "mscoco_captions":
        if not os.path.exists(annotation_file):
            print("You need to download this dataset manually. Please download the dataset from https://cocodataset.org/")
        return CocoCaptions(root=root, annFile=annotation_file, transform=transform, **kwargs)
    elif dataset_name == "flickr30k":
        # downloadable from https://www.kaggle.com/datasets/adityajn105/flickr30k
        if not os.path.exists(annotation_file):
            print("You need to download this dataset manually. Please download the dataset from https://www.kaggle.com/datasets/adityajn105/flickr30k")
            sys.exit(1)
        return flickr.Flickr(root=root, ann_file=annotation_file, transform=transform, **kwargs)
    elif dataset_name == "flickr8k":
        # downloadable from https://www.kaggle.com/datasets/adityajn105/flickr8k
        if not os.path.exists(annotation_file):
            print("You need to download this dataset manually. Please download the dataset from https://www.kaggle.com/datasets/adityajn105/flickr8k")
            sys.exit(1)
        return flickr.Flickr(root=root, ann_file=annotation_file, transform=transform, **kwargs)
    elif dataset_name == "food101":
        ds = Food101(root=root, split="train" if train else "test", transform=transform, download=download, **kwargs)
        # we use the default class names, we just  replace "_" by spaces
        # to delimit words
        ds.classes = list(map(lambda s:" ".join(s.split("_")), ds.classes))
        return ds
    elif dataset_name == "sun397":
        # we use the default class names, we just  replace "_" by spaces
        # to delimit words
        ds = SUN397(root=root, transform=transform, download=download, **kwargs)
        ds.classes = list(map(lambda s:" ".join(s.split("_")), ds.classes ))
        return ds
    elif dataset_name == "cars":
        return StanfordCars(root=root, split="train" if train else "test", transform=transform, download=download, **kwargs)
    elif dataset_name == "fgvc_aircraft":
        return FGVCAircraft(root=root, annotation_level="variant", split="train" if train else "test", transform=transform, download=download, **kwargs)
    elif dataset_name == "dtd":
        return DTD(root=root, split="train" if train else "test", transform=transform, download=download, **kwargs)
    elif dataset_name == "pets":
        return OxfordIIITPet(root=root, split="train" if train else "test", target_types="category", transform=transform, download=download, **kwargs)
    elif dataset_name == "caltech101":
        # broken download link (can't download google drive), fixed by this PR https://github.com/pytorch/vision/pull/5645
        ds = caltech101.Caltech101(root=root, target_type="category", transform=transform, download=download, **kwargs)
        ds.classes = classnames["caltech101"]
        return ds
    elif dataset_name == "flowers":
        ds = Flowers102(root=root, split="train" if train else "test", transform=transform, download=download, **kwargs)
        # class indices started by 1, fixed in this PR (#TODO link)
        # if older torchvision version, fix it using a target transform that decrements label index 
        # TODO figure out torchvision versio needed instead of decrementing
        if ds[0][1] == 1:
            ds.target_transform = lambda y:y-1
        ds.classes = classnames["flowers"]
        return ds
    elif dataset_name == "mnist":
        ds = MNIST(root=root, train=train, transform=transform, download=download, **kwargs)
        ds.classes = classnames["mnist"]
        return ds
    elif dataset_name == "stl10":
        return STL10(root=root, split="train" if train else "test", transform=transform, download=download, **kwargs)
    elif dataset_name == "eurosat":
        ds = EuroSAT(root=root, transform=transform, download=download, **kwargs)
        ds.classes = classnames["eurosat"]
        return ds
    elif dataset_name == "gtsrb":
        ds =  GTSRB(root=root, split="train" if train else "test", transform=transform, download=download, **kwargs)
        ds.classes = classnames["gtsrb"]
        return ds
    elif dataset_name == "country211":
        ds = Country211(root=root, split="train" if train else "test", transform=transform, download=download, **kwargs)
        ds.classes = classnames["country211"]
        return ds
    elif dataset_name == "pcam":
        # Dead link. Fixed by this PR https://github.com/pytorch/vision/pull/5645
        ds =  PCAM(root=root, split="train" if train else "test", transform=transform, download=download, **kwargs)
        ds.classes = classnames["pcam"]
        return ds
    elif dataset_name == "renderedsst2":
        return RenderedSST2(root=root, split="train" if train else "test", transform=transform, download=download, **kwargs)
    elif dataset_name == "fer2013":
        # Donloadable from  https://www.kaggle.com/datasets/msambare/fer2013
        root = os.path.join(root, "train" if train else "test")
        if not os.path.exists(root):
            print("You need to download this dataset manually. Please download the dataset from https://www.kaggle.com/datasets/msambare/fer2013")
        ds = ImageFolder(root=root, transform=transform)
        ds.classes = classnames["fer2013"]
        return ds
    elif dataset_name.startswith("tfds/"):
        # TFDS datasets support using `timm` and `tensorflow_datasets`
        prefix, *name_list = dataset_name.split("/")
        name = "/".join(name_list)
        return build_tfds_dataset(name, download=download, split=split, data_dir=root, transform=transform)
    elif dataset_name.startswith("vtab/"):
        # VTAB datasets support using `tensorflow_datasets` and `task_adaptation`
        prefix, *name_list = dataset_name.split("/")
        name = "/".join(name_list)
        return build_vtab_dataset(name, download=download, split=split, data_dir=root, transform=transform)
    else:
        raise ValueError(f"Unsupported dataset: {dataset_name}.")


def get_dataset_collate_fn(dataset_name):
    if dataset_name in ("mscoco_captions", "flickr30k", "flickr8k"):
        return image_captions_collate_fn
    else:
        return default_collate

def build_vtab_dataset(dataset_name, transform, download=True, split="test", data_dir="root"):
    # Using VTAB splits instead of default TFDS splits
    from .tfds import VTABIterableDataset, disable_gpus_on_tensorflow, download_tfds_dataset
    disable_gpus_on_tensorflow()

    # by default we take classes from TFDS (default behavior if `classes` stays None),
    # except for some datasets that will override `classes``
    classes = None
    if dataset_name == "caltech101":
        from task_adaptation.data.caltech import Caltech101
        tfds_dataset = Caltech101(data_dir=data_dir)
        classes = classnames["caltech101_vtab"]
    elif dataset_name == "cars":
        from task_adaptation.data.cars import CarsData
        tfds_dataset = CarsData(data_dir=data_dir)
    elif dataset_name in ("cifar10", "cifar100"):
        from task_adaptation.data.cifar import CifarData
        tfds_dataset = CifarData(data_dir=data_dir, num_classes=10 if dataset_name == "cifar10" else 100)
    elif dataset_name.startswith("clevr_"):
        from task_adaptation.data.clevr import CLEVRData
        task = _extract_task(dataset_name)
        assert task in ("count_all", "closest_object_distance")
        tfds_dataset = CLEVRData(task=task, data_dir=data_dir)
        if task == "count_all":
            classes = classnames["clevr_count_all"]
        elif task == "closest_object_distance":
            classes = classnames["clevr_closest_object_distance"]
        else:
            raise ValueError(f"non supported: {task}")
    elif dataset_name == "cub":
        from task_adaptation.data.cub import CUB2011Data
        tfds_dataset = CUB2011Data(data_dir=data_dir)
    elif dataset_name == "diabetic_retinopathy":
        from task_adaptation.data.diabetic_retinopathy import RetinopathyData
        tfds_dataset = RetinopathyData(config="btgraham-300", data_dir=data_dir)
        classes = classnames["diabetic_retinopathy"]
    elif dataset_name == "dmlab":
        from task_adaptation.data.dmlab import DmlabData
        download_tfds_dataset("dmlab", data_dir=data_dir) # it's not called in the origina VTAB code, so we do it explictly
        tfds_dataset = DmlabData(data_dir=data_dir)
        classes = classnames["dmlab"]
    elif dataset_name.startswith("dsprites_"):
        from task_adaptation.data.dsprites import DSpritesData
        task = _extract_task(dataset_name)
        assert task in ("label_shape", "label_scale", "label_orientation", "label_x_position", "label_y_position")
        tfds_dataset = DSpritesData(task, data_dir=data_dir)
    elif dataset_name == "dtd":
        from task_adaptation.data.dtd import DTDData
        tfds_dataset = DTDData(data_dir=data_dir)
    elif dataset_name == "eurosat":
        from task_adaptation.data.eurosat import EurosatData
        tfds_dataset = EurosatData(subset="rgb", data_key="image", data_dir=data_dir)
        classes = classnames["eurosat"]
    elif dataset_name == "food101":
        from task_adaptation.data.food101 import Food101Data
        tfds_dataset = Food101Data(data_dir=data_dir)
    elif dataset_name == "inaturalist":
        from task_adaptation.data.inaturalist import INaturalistData
        tfds_dataset = INaturalistData(data_dir=data_dir, year=2017)
    elif dataset_name.startswith("kitti_"):
        from .kitti import KittiData
        task = _extract_task(dataset_name)
        assert task in (
            "count_all", "count_left", "count_far", "count_near", 
            "closest_object_distance", "closest_object_x_location", 
            "count_vehicles", "closest_vehicle_distance",
        )
        tfds_dataset = KittiData(task=task, data_dir=data_dir)
        if task == "closest_vehicle_distance":
            classes = classnames["kitti_closest_vehicle_distance"]
        else:
            raise ValueError(f"Unsupported task: {task}")
    elif dataset_name == "flowers":
        from task_adaptation.data.oxford_flowers102 import OxfordFlowers102Data
        tfds_dataset = OxfordFlowers102Data(data_dir=data_dir)
    elif dataset_name == "pets":
        from task_adaptation.data.oxford_iiit_pet import OxfordIIITPetData
        tfds_dataset = OxfordIIITPetData(data_dir=data_dir)
        classes = classnames["pets"]
    elif dataset_name == "pcam":
        from task_adaptation.data.patch_camelyon import PatchCamelyonData
        tfds_dataset = PatchCamelyonData(data_dir=data_dir)
        classes = classnames["pcam"]
    elif dataset_name == "resisc45":
        from task_adaptation.data.resisc45 import Resisc45Data
        tfds_dataset = Resisc45Data(data_dir=data_dir)
    elif dataset_name.startswith("smallnorb_"):
        from task_adaptation.data.smallnorb import SmallNORBData
        task = _extract_task(dataset_name)
        assert task in ("label_category", "label_elevation", "label_azimuth", "label_lighting")
        tfds_dataset = SmallNORBData(predicted_attribute=task, data_dir=data_dir)
        classes = tfds_dataset._dataset_builder.info.features[task].names
    elif dataset_name == "sun397":
        from task_adaptation.data.sun397 import Sun397Data
        # There is a problem in `sun397`, when TFDS tries download it
        # there is an image that cannot be decoded. for the time being
        # we will use torchvision's SUN397 instead.
        tfds_dataset = Sun397Data(config="tfds", data_dir=data_dir)
    elif dataset_name == "svhn":
        from task_adaptation.data.svhn import SvhnData
        tfds_dataset = SvhnData(data_dir=data_dir)
        classes = classnames["svhn"]
    else:
        raise ValueError(f"Unsupported dataset: {dataset_name}")
    ds =  VTABIterableDataset(
        tfds_dataset, 
        input_name="image", label_name="label", 
        transform=transform, 
        target_transform=int,
        split=split,
        classes=classes,
    )
    return ds

def build_tfds_dataset(name, transform, download=True, split="test", data_dir="root", classes=None):
    from .tfds import disable_gpus_on_tensorflow
    disable_gpus_on_tensorflow()
    import tensorflow_datasets as tfds
    import timm
    builder = tfds.builder(name, data_dir=data_dir)
    if download:
        builder.download_and_prepare()
    splits = list(builder.info.splits.keys())
    assert split in splits, (split, splits)
    ds = timm.data.create_dataset(f"tfds/{name}", data_dir, split=split, transform=transform, target_transform=int)
    ds.classes = builder.info.features['label'].names if classes is None else classes
    return ds


def _extract_task(dataset_name):
    prefix, *task_name_list = dataset_name.split("_")
    task = "_".join(task_name_list)
    return task


def image_captions_collate_fn(batch):
    transposed = list(zip(*batch))
    imgs = default_collate(transposed[0])
    texts = transposed[1]
    return imgs, texts


def get_zeroshot_classification_templates(dataset_name):
    if dataset_name.startswith("tfds/") or dataset_name.startswith("vtab/"):
        name = dataset_name.split("/")[1]
    else:
        name = dataset_name
    return zeroshot_classification_templates.get(name, DEFAULT_ZEROSHOT_CLASSIFICATION_TEMPLATES)

# Zero-shot classification templates, collected from a bunch of sources
# - CLIP paper (https://github.com/openai/CLIP/blob/main/data/prompts.md)
# - Lit Paper (https://arxiv.org/pdf/2111.07991.pdf)
# - SLIP paper (https://github.com/facebookresearch/SLIP/blob/main/templates.json)
# Some are fixed mnaually

zeroshot_classification_templates = {
    "cifar10": [
        "a photo of a {c}.",
        "a blurry photo of a {c}.",
        "a black and white photo of a {c}.",
        "a low contrast photo of a {c}.",
        "a high contrast photo of a {c}.",
        "a bad photo of a {c}.",
        "a good photo of a {c}.",
        "a photo of a small {c}.",
        "a photo of a big {c}.",
        "a photo of the {c}.",
        "a blurry photo of the {c}.",
        "a black and white photo of the {c}.",
        "a low contrast photo of the {c}.",
        "a high contrast photo of the {c}.",
        "a bad photo of the {c}.",
        "a good photo of the {c}.",
        "a photo of the small {c}.",
        "a photo of the big {c}."
    ],
    "cifar100":[
        "a photo of a {c}.",
        "a blurry photo of a {c}.",
        "a black and white photo of a {c}.",
        "a low contrast photo of a {c}.",
        "a high contrast photo of a {c}.",
        "a bad photo of a {c}.",
        "a good photo of a {c}.",
        "a photo of a small {c}.",
        "a photo of a big {c}.",
        "a photo of the {c}.",
        "a blurry photo of the {c}.",
        "a black and white photo of the {c}.",
        "a low contrast photo of the {c}.",
        "a high contrast photo of the {c}.",
        "a bad photo of the {c}.",
        "a good photo of the {c}.",
        "a photo of the small {c}.",
        "a photo of the big {c}."
    ],
    "imagenet1k": [
        "a bad photo of a {c}.",
        "a photo of many {c}.",
        "a sculpture of a {c}.",
        "a photo of the hard to see {c}.",
        "a low resolution photo of the {c}.",
        "a rendering of a {c}.",
        "graffiti of a {c}.",
        "a bad photo of the {c}.",
        "a cropped photo of the {c}.",
        "a tattoo of a {c}.",
        "the embroidered {c}.",
        "a photo of a hard to see {c}.",
        "a bright photo of a {c}.",
        "a photo of a clean {c}.",
        "a photo of a dirty {c}.",
        "a dark photo of the {c}.",
        "a drawing of a {c}.",
        "a photo of my {c}.",
        "the plastic {c}.",
        "a photo of the cool {c}.",
        "a close-up photo of a {c}.",
        "a black and white photo of the {c}.",
        "a painting of the {c}.",
        "a painting of a {c}.",
        "a pixelated photo of the {c}.",
        "a sculpture of the {c}.",
        "a bright photo of the {c}.",
        "a cropped photo of a {c}.",
        "a plastic {c}.",
        "a photo of the dirty {c}.",
        "a jpeg corrupted photo of a {c}.",
        "a blurry photo of the {c}.",
        "a photo of the {c}.",
        "a good photo of the {c}.",
        "a rendering of the {c}.",
        "a {c} in a video game.",
        "a photo of one {c}.",
        "a doodle of a {c}.",
        "a close-up photo of the {c}.",
        "a photo of a {c}.",
        "the origami {c}.",
        "the {c} in a video game.",
        "a sketch of a {c}.",
        "a doodle of the {c}.",
        "a origami {c}.",
        "a low resolution photo of a {c}.",
        "the toy {c}.",
        "a rendition of the {c}.",
        "a photo of the clean {c}.",
        "a photo of a large {c}.",
        "a rendition of a {c}.",
        "a photo of a nice {c}.",
        "a photo of a weird {c}.",
        "a blurry photo of a {c}.",
        "a cartoon {c}.",
        "art of a {c}.",
        "a sketch of the {c}.",
        "a embroidered {c}.",
        "a pixelated photo of a {c}.",
        "itap of the {c}.",
        "a jpeg corrupted photo of the {c}.",
        "a good photo of a {c}.",
        "a plushie {c}.",
        "a photo of the nice {c}.",
        "a photo of the small {c}.",
        "a photo of the weird {c}.",
        "the cartoon {c}.",
        "art of the {c}.",
        "a drawing of the {c}.",
        "a photo of the large {c}.",
        "a black and white photo of a {c}.",
        "the plushie {c}.",
        "a dark photo of a {c}.",
        "itap of a {c}.",
        "graffiti of the {c}.",
        "a toy {c}.",
        "itap of my {c}.",
        "a photo of a cool {c}.",
        "a photo of a small {c}.",
        "a tattoo of the {c}."
    ],
    "food101":[
        'a photo of {c}, a type of food.'
    ],
    "sun397":[
        'a photo of a {c}.',
        'a photo of the {c}.',
    ],
    "cars":[
        'a photo of a {c}.',
        'a photo of the {c}.',
        'a photo of my {c}.',
        'i love my {c}!',
        'a photo of my dirty {c}.',
        'a photo of my clean {c}.',
        'a photo of my new {c}.',
        'a photo of my old {c}.',
    ],
    "fgvc_aircraft":[
        'a photo of a {c}, a type of aircraft.',
        'a photo of the {c}, a type of aircraft.',
    ],
    "dtd":[
        'a photo of a {c} texture.',
        'a photo of a {c} pattern.',
        'a photo of a {c} thing.',
        'a photo of a {c} object.',
        'a photo of the {c} texture.',
        'a photo of the {c} pattern.',
        'a photo of the {c} thing.',
        'a photo of the {c} object.',    
    ],
    "pets":[
        'a photo of a {c}, a type of pet.',
    ],
    "caltech101":[
        'a photo of a {c}.',
        'a painting of a {c}.',
        'a plastic {c}.',
        'a sculpture of a {c}.',
        'a sketch of a {c}.',
        'a tattoo of a {c}.',
        'a toy {c}.',
        'a rendition of a {c}.',
        'a embroidered {c}.',
        'a cartoon {c}.',
        'a {c} in a video game.',
        'a plushie {c}.',
        'a origami {c}.',
        'art of a {c}.',
        'graffiti of a {c}.',
        'a drawing of a {c}.',
        'a doodle of a {c}.',
        'a photo of the {c}.',
        'a painting of the {c}.',
        'the plastic {c}.',
        'a sculpture of the {c}.',
        'a sketch of the {c}.',
        'a tattoo of the {c}.',
        'the toy {c}.',
        'a rendition of the {c}.',
        'the embroidered {c}.',
        'the cartoon {c}.',
        'the {c} in a video game.',
        'the plushie {c}.',
        'the origami {c}.',
        'art of the {c}.',
        'graffiti of the {c}.',
        'a drawing of the {c}.',
        'a doodle of the {c}.',
    ],
    "flowers":[
        'a photo of a {c}, a type of flower.',
    ],
    "mnist": [
        'a photo of the number: "{c}".',
    ],
    "stl10": [
        'a photo of a {c}.',
        'a photo of the {c}.',
    ],
    "eurosat":[
        'a centered satellite photo of {c}.',
        'a centered satellite photo of a {c}.',
        'a centered satellite photo of the {c}.',
    ],
    "gtsrb":[
        'a zoomed in photo of a "{c}" traffic sign.',
        'a centered photo of a "{c}" traffic sign.',
        'a close up photo of a "{c}" traffic sign.',
    ],
    "country211":[
        'a photo i took in {c}.',
        'a photo i took while visiting {c}.',
        'a photo from my home country of {c}.',
        'a photo from my visit to {c}.',
        'a photo showing the country of {c}.',
    ],
    "renderedsst2":[
        'a {c} review of a movie.',
    ],
    "voc2007":[
        'a photo of a {c}.',
    ],
    "fer2013":[
        'a photo of a {c} looking face.',
        'a photo of a face showing the emotion: {c}.',
        'a photo of a face looking {c}.',
        'a face that looks {c}.',
        'they look {c}.',
        'look at how {c} they are.',
    ],
    "clevr_count_all":[
        "a picture of {c} objects"
    ],
    "clevr_closest_object_distance":[
        "{c} shapes."
    ],
    "pcam":[
        "a histopathology slide showing {c}",
        "histopathology image of {c}"
    ],
    "svhn":[
        "a photo of the number {c} written on a sign",
        "an outdoor house number {c}",
        "the number {c} in the center of the image",
        "an outdoor number {c} writte on a sign",
        "an outdoor number {c}",
        "a centered image of the number {c}",
    ],
    "resisc45":[
        "a sattelite image of {c}",
        "an aerial view of {c}",
        "a sattelite photo of {c}",
        "{c} from above",
    ],
    "kitti_closest_vehicle_distance":[
        "{c}"
    ],
    "smallnorb_label_azimuth":[
        "an object rotated at {c}",
        "something rotated at {c}",
        "{c} rotation",
        "something at a {c} angle",
    ],
    "smallnorb_label_elevation":[
        "an object rotated at {c}",
        "something rotated at {c}",
        "{c} rotation",
        "something at a {c} angle",
    ],
    "dsprites_label_x_position": [
        "an object located at position {c}% on the horizontal axis",
    ],
    "dsprites_label_orientation":[
        "an object rotated at {c}",
        "something rotated at {c}",
        "{c} rotation",
        "something at a {c} angle",
    ],
    "dmlab":[
        "{c}"
    ],
    "diabetic_retinopathy":[
        "a retinal image with {c}",        
    ]
}


# Class names for different datasets
# In general, we use the default class names from torchvision or VTAB/TFDS,
# except for the datasets defined in `classnames`
# These classnames are collected from various sources:
# - CLIP paper (https://github.com/openai/CLIP/blob/main/data/prompts.md)
# - Lit Paper (https://arxiv.org/pdf/2111.07991.pdf)
# - SLIP paper (https://github.com/facebookresearch/SLIP/blob/main/templates.json)
# Some are fixed mnaually

classnames = dict(
    flowers = [
        'pink primrose',
        'hard-leaved pocket orchid',
        'canterbury bells',
        'sweet pea',
        'english marigold',
        'tiger lily',
        'moon orchid',
        'bird of paradise',
        'monkshood',
        'globe thistle',
        'snapdragon',
        "colt's foot",
        'king protea',
        'spear thistle',
        'yellow iris',
        'globe flower',
        'purple coneflower',
        'peruvian lily',
        'balloon flower',
        'giant white arum lily',
        'fire lily',
        'pincushion flower',
        'fritillary',
        'red ginger',
        'grape hyacinth',
        'corn poppy',
        'prince of wales feathers',
        'stemless gentian',
        'artichoke',
        'sweet william',
        'carnation',
        'garden phlox',
        'love in the mist',
        'mexican aster',
        'alpine sea holly',
        'ruby-lipped cattleya',
        'cape flower',
        'great masterwort',
        'siam tulip',
        'lenten rose',
        'barbeton daisy',
        'daffodil',
        'sword lily',
        'poinsettia',
        'bolero deep blue',
        'wallflower',
        'marigold',
        'buttercup',
        'oxeye daisy',
        'common dandelion',
        'petunia',
        'wild pansy',
        'primula',
        'sunflower',
        'pelargonium',
        'bishop of llandaff',
        'gaura',
        'geranium',
        'orange dahlia',
        'pink and yellow dahlia',
        'cautleya spicata',
        'japanese anemone',
        'black-eyed susan',
        'silverbush',
        'californian poppy',
        'osteospermum',
        'spring crocus',
        'bearded iris',
        'windflower',
        'tree poppy',
        'gazania',
        'azalea',
        'water lily',
        'rose',
        'thorn apple',
        'morning glory',
        'passion flower',
        'lotus',
        'toad lily',
        'anthurium',
        'frangipani',
        'clematis',
        'hibiscus',
        'columbine',
        'desert-rose',
        'tree mallow',
        'magnolia',
        'cyclamen',
        'watercress',
        'canna lily',
        'hippeastrum',
        'bee balm',
        'air plant',
        'foxglove',
        'bougainvillea',
        'camellia',
        'mallow',
        'mexican petunia',
        'bromelia',
        'blanket flower',
        'trumpet creeper',
        'blackberry lily',
    ],
    gtsrb= [
        'red and white circle 20 kph speed limit',
        'red and white circle 30 kph speed limit',
        'red and white circle 50 kph speed limit',
        'red and white circle 60 kph speed limit',
        'red and white circle 70 kph speed limit',
        'red and white circle 80 kph speed limit',
        'end / de-restriction of 80 kph speed limit',
        'red and white circle 100 kph speed limit',
        'red and white circle 120 kph speed limit',
        'red and white circle red car and black car no passing',
        'red and white circle red truck and black car no passing',
        'red and white triangle road intersection warning',
        'white and yellow diamond priority road',
        'red and white upside down triangle yield right-of-way',
        'stop',
        'empty red and white circle',
        'red and white circle no truck entry',
        'red circle with white horizonal stripe no entry',
        'red and white triangle with exclamation mark warning',
        'red and white triangle with black left curve approaching warning',
        'red and white triangle with black right curve approaching warning',
        'red and white triangle with black double curve approaching warning',
        'red and white triangle rough / bumpy road warning',
        'red and white triangle car skidding / slipping warning',
        'red and white triangle with merging / narrow lanes warning',
        'red and white triangle with person digging / construction / road work warning',
        'red and white triangle with traffic light approaching warning',
        'red and white triangle with person walking warning',
        'red and white triangle with child and person walking warning',
        'red and white triangle with bicyle warning',
        'red and white triangle with snowflake / ice warning',
        'red and white triangle with deer warning',
        'white circle with gray strike bar no speed limit',
        'blue circle with white right turn arrow mandatory',
        'blue circle with white left turn arrow mandatory',
        'blue circle with white forward arrow mandatory',
        'blue circle with white forward or right turn arrow mandatory',
        'blue circle with white forward or left turn arrow mandatory',
        'blue circle with white keep right arrow mandatory',
        'blue circle with white keep left arrow mandatory',
        'blue circle with white arrows indicating a traffic circle',
        'white circle with gray strike bar indicating no passing for cars has ended',
        'white circle with gray strike bar indicating no passing for trucks has ended',
    ],
    country211 = [
        'Andorra',
        'United Arab Emirates',
        'Afghanistan',
        'Antigua and Barbuda',
        'Anguilla',
        'Albania',
        'Armenia',
        'Angola',
        'Antarctica',
        'Argentina',
        'Austria',
        'Australia',
        'Aruba',
        'Aland Islands',
        'Azerbaijan',
        'Bosnia and Herzegovina',
        'Barbados',
        'Bangladesh',
        'Belgium',
        'Burkina Faso',
        'Bulgaria',
        'Bahrain',
        'Benin',
        'Bermuda',
        'Brunei Darussalam',
        'Bolivia',
        'Bonaire, Saint Eustatius and Saba',
        'Brazil',
        'Bahamas',
        'Bhutan',
        'Botswana',
        'Belarus',
        'Belize',
        'Canada',
        'DR Congo',
        'Central African Republic',
        'Switzerland',
        "Cote d'Ivoire",
        'Cook Islands',
        'Chile',
        'Cameroon',
        'China',
        'Colombia',
        'Costa Rica',
        'Cuba',
        'Cabo Verde',
        'Curacao',
        'Cyprus',
        'Czech Republic',
        'Germany',
        'Denmark',
        'Dominica',
        'Dominican Republic',
        'Algeria',
        'Ecuador',
        'Estonia',
        'Egypt',
        'Spain',
        'Ethiopia',
        'Finland',
        'Fiji',
        'Falkland Islands',
        'Faeroe Islands',
        'France',
        'Gabon',
        'United Kingdom',
        'Grenada',
        'Georgia',
        'French Guiana',
        'Guernsey',
        'Ghana',
        'Gibraltar',
        'Greenland',
        'Gambia',
        'Guadeloupe',
        'Greece',
        'South Georgia and South Sandwich Is.',
        'Guatemala',
        'Guam',
        'Guyana',
        'Hong Kong',
        'Honduras',
        'Croatia',
        'Haiti',
        'Hungary',
        'Indonesia',
        'Ireland',
        'Israel',
        'Isle of Man',
        'India',
        'Iraq',
        'Iran',
        'Iceland',
        'Italy',
        'Jersey',
        'Jamaica',
        'Jordan',
        'Japan',
        'Kenya',
        'Kyrgyz Republic',
        'Cambodia',
        'St. Kitts and Nevis',
        'North Korea',
        'South Korea',
        'Kuwait',
        'Cayman Islands',
        'Kazakhstan',
        'Laos',
        'Lebanon',
        'St. Lucia',
        'Liechtenstein',
        'Sri Lanka',
        'Liberia',
        'Lithuania',
        'Luxembourg',
        'Latvia',
        'Libya',
        'Morocco',
        'Monaco',
        'Moldova',
        'Montenegro',
        'Saint-Martin',
        'Madagascar',
        'Macedonia',
        'Mali',
        'Myanmar',
        'Mongolia',
        'Macau',
        'Martinique',
        'Mauritania',
        'Malta',
        'Mauritius',
        'Maldives',
        'Malawi',
        'Mexico',
        'Malaysia',
        'Mozambique',
        'Namibia',
        'New Caledonia',
        'Nigeria',
        'Nicaragua',
        'Netherlands',
        'Norway',
        'Nepal',
        'New Zealand',
        'Oman',
        'Panama',
        'Peru',
        'French Polynesia',
        'Papua New Guinea',
        'Philippines',
        'Pakistan',
        'Poland',
        'Puerto Rico',
        'Palestine',
        'Portugal',
        'Palau',
        'Paraguay',
        'Qatar',
        'Reunion',
        'Romania',
        'Serbia',
        'Russia',
        'Rwanda',
        'Saudi Arabia',
        'Solomon Islands',
        'Seychelles',
        'Sudan',
        'Sweden',
        'Singapore',
        'St. Helena',
        'Slovenia',
        'Svalbard and Jan Mayen Islands',
        'Slovakia',
        'Sierra Leone',
        'San Marino',
        'Senegal',
        'Somalia',
        'South Sudan',
        'El Salvador',
        'Sint Maarten',
        'Syria',
        'Eswatini',
        'Togo',
        'Thailand',
        'Tajikistan',
        'Timor-Leste',
        'Turkmenistan',
        'Tunisia',
        'Tonga',
        'Turkey',
        'Trinidad and Tobago',
        'Taiwan',
        'Tanzania',
        'Ukraine',
        'Uganda',
        'United States',
        'Uruguay',
        'Uzbekistan',
        'Vatican',
        'Venezuela',
        'British Virgin Islands',
        'United States Virgin Islands',
        'Vietnam',
        'Vanuatu',
        'Samoa',
        'Kosovo',
        'Yemen',
        'South Africa',
        'Zambia',
        'Zimbabwe',
    ],
    eurosat = [
        'annual crop land',
        'forest',
        'brushland or shrubland',
        'highway or road',
        'industrial buildings or commercial buildings',
        'pasture land',
        'permanent crop land',
        'residential buildings or homes or apartments',
        'river',
        'lake or sea',
    ],
    fer2013 = [
        "angry",
        "disgusted",
        "fearful",
        "happy",
        "neutral",
        "sad",
        "surprised",
    ],
    caltech101 = [
        'background',
        'off-center face',
        'centered face',
        'leopard',
        'motorbike',
        'accordion',
        'airplane',
        'anchor',
        'ant',
        'barrel',
        'bass',
        'beaver',
        'binocular',
        'bonsai',
        'brain',
        'brontosaurus',
        'buddha',
        'butterfly',
        'camera',
        'cannon',
        'side of a car',
        'ceiling fan',
        'cellphone',
        'chair',
        'chandelier',
        'body of a cougar cat',
        'face of a cougar cat',
        'crab',
        'crayfish',
        'crocodile',
        'head of a  crocodile',
        'cup',
        'dalmatian',
        'dollar bill',
        'dolphin',
        'dragonfly',
        'electric guitar',
        'elephant',
        'emu',
        'euphonium',
        'ewer',
        'ferry',
        'flamingo',
        'head of a flamingo',
        'garfield',
        'gerenuk',
        'gramophone',
        'grand piano',
        'hawksbill',
        'headphone',
        'hedgehog',
        'helicopter',
        'ibis',
        'inline skate',
        'joshua tree',
        'kangaroo',
        'ketch',
        'lamp',
        'laptop',
        'llama',
        'lobster',
        'lotus',
        'mandolin',
        'mayfly',
        'menorah',
        'metronome',
        'minaret',
        'nautilus',
        'octopus',
        'okapi',
        'pagoda',
        'panda',
        'pigeon',
        'pizza',
        'platypus',
        'pyramid',
        'revolver',
        'rhino',
        'rooster',
        'saxophone',
        'schooner',
        'scissors',
        'scorpion',
        'sea horse',
        'snoopy (cartoon beagle)',
        'soccer ball',
        'stapler',
        'starfish',
        'stegosaurus',
        'stop sign',
        'strawberry',
        'sunflower',
        'tick',
        'trilobite',
        'umbrella',
        'watch',
        'water lilly',
        'wheelchair',
        'wild cat',
        'windsor chair',
        'wrench',
        'yin and yang symbol',
    ],
    # same as `caltech1101`, just a different ordering`
    caltech101_vtab = [ 
    'accordion', 'airplane', 'anchor', 'ant', 'background', 'barrel', 'bass', 'beaver', 'binocular', 'bonsai', 'brain', 'brontosaurus', 'buddha', 'butterfly', 'camera', 'cannon', 'side of a car', 'ceiling fan', 'cellphone', 'chair', 'chandelier', 'body of a cougar cat', 'face of a cougar cat', 'crab', 'crayfish', 'crocodile', 'head of a  crocodile', 'cup', 'dalmatian', 'dollar bill', 'dolphin', 'dragonfly', 'electric guitar', 'elephant', 'emu', 'euphonium', 'ewer', 'off-center face', 'centered face', 'ferry', 'flamingo', 'head of a flamingo', 'garfield', 'gerenuk', 'gramophone', 'grand piano', 'hawksbill', 'headphone', 'hedgehog', 'helicopter', 'ibis', 'inline skate', 'joshua tree', 'kangaroo', 'ketch', 'lamp', 'laptop', 'leopard', 'llama', 'lobster', 'lotus', 'mandolin', 'mayfly', 'menorah', 'metronome', 'minaret', 'motorbike', 'nautilus', 'octopus', 'okapi', 'pagoda', 'panda', 'pigeon', 'pizza', 'platypus', 'pyramid', 'revolver', 'rhino', 'rooster', 'saxophone', 'schooner', 'scissors', 'scorpion', 'sea horse', 'snoopy (cartoon beagle)', 'soccer ball', 'stapler', 'starfish', 'stegosaurus', 'stop sign', 'strawberry', 'sunflower', 'tick', 'trilobite', 'umbrella', 'watch', 'water lilly', 'wheelchair', 'wild cat', 'windsor chair', 'wrench', 'yin and yang symbol'
    ],
    imagenet1k = [
        "tench", "goldfish", "great white shark", "tiger shark", "hammerhead shark", "electric ray", "stingray", "rooster", 
        "hen", "ostrich", "brambling", "goldfinch", "house finch", "junco", "indigo bunting", "American robin", "bulbul", 
        "jay", "magpie", "chickadee", "American dipper", "kite (bird of prey)", "bald eagle", "vulture", "great grey owl",
        "fire salamander", "smooth newt", "newt", "spotted salamander", "axolotl", "American bullfrog", "tree frog", "tailed frog", 
        "loggerhead sea turtle", "leatherback sea turtle", "mud turtle", "terrapin", "box turtle", "banded gecko", "green iguana", 
        "Carolina anole", "desert grassland whiptail lizard", "agama", "frilled-necked lizard", "alligator lizard", "Gila monster", 
        "European green lizard", "chameleon", "Komodo dragon", "Nile crocodile", "American alligator", "triceratops", "worm snake", 
        "ring-necked snake", "eastern hog-nosed snake", "smooth green snake", "kingsnake", "garter snake", "water snake", "vine snake", 
        "night snake", "boa constrictor", "African rock python", "Indian cobra", "green mamba", "sea snake", "Saharan horned viper",
        "eastern diamondback rattlesnake", "sidewinder rattlesnake", "trilobite", "harvestman", "scorpion", "yellow garden spider",
        "barn spider", "European garden spider", "southern black widow", "tarantula", "wolf spider", "tick", "centipede", "black grouse",
        "ptarmigan", "ruffed grouse", "prairie grouse", "peafowl", "quail", "partridge", "african grey parrot", "macaw", "sulphur-crested cockatoo", 
        "lorikeet", "coucal", "bee eater", "hornbill", "hummingbird", "jacamar", "toucan", "duck", "red-breasted merganser", "goose", "black swan", 
        "tusker", "echidna", "platypus", "wallaby", "koala", "wombat", "jellyfish", "sea anemone", "brain coral", "flatworm", "nematode", 
        "conch", "snail", "slug", "sea slug", "chiton", "chambered nautilus", "Dungeness crab", "rock crab", "fiddler crab", "red king crab", 
        "American lobster", "spiny lobster", "crayfish", "hermit crab", "isopod", "white stork", "black stork", "spoonbill", "flamingo", 
        "little blue heron", "great egret", "bittern bird", "crane bird", "limpkin", "common gallinule", "American coot", "bustard", 
        "ruddy turnstone", "dunlin", "common redshank", "dowitcher", "oystercatcher", "pelican", "king penguin", "albatross", "grey whale", 
        "killer whale", "dugong", "sea lion", "Chihuahua", "Japanese Chin", "Maltese", "Pekingese", "Shih Tzu", "King Charles Spaniel", 
        "Papillon", "toy terrier", "Rhodesian Ridgeback", "Afghan Hound", "Basset Hound", "Beagle", "Bloodhound", "Bluetick Coonhound", 
        "Black and Tan Coonhound", "Treeing Walker Coonhound", "English foxhound", "Redbone Coonhound", "borzoi", "Irish Wolfhound", 
        "Italian Greyhound", "Whippet", "Ibizan Hound", "Norwegian Elkhound", "Otterhound", "Saluki", "Scottish Deerhound", "Weimaraner", 
        "Staffordshire Bull Terrier", "American Staffordshire Terrier", "Bedlington Terrier", "Border Terrier", "Kerry Blue Terrier", 
        "Irish Terrier", "Norfolk Terrier", "Norwich Terrier", "Yorkshire Terrier", "Wire Fox Terrier", "Lakeland Terrier", "Sealyham Terrier", 
        "Airedale Terrier", "Cairn Terrier", "Australian Terrier", "Dandie Dinmont Terrier", "Boston Terrier", "Miniature Schnauzer", 
        "Giant Schnauzer", "Standard Schnauzer", "Scottish Terrier", "Tibetan Terrier", "Australian Silky Terrier", "Soft-coated Wheaten Terrier", 
        "West Highland White Terrier", "Lhasa Apso", "Flat-Coated Retriever", "Curly-coated Retriever", "Golden Retriever", "Labrador Retriever", 
        "Chesapeake Bay Retriever", "German Shorthaired Pointer", "Vizsla", "English Setter", "Irish Setter", "Gordon Setter", "Brittany dog", 
        "Clumber Spaniel", "English Springer Spaniel", "Welsh Springer Spaniel", "Cocker Spaniel", "Sussex Spaniel", "Irish Water Spaniel", "Kuvasz", 
        "Schipperke", "Groenendael dog", "Malinois", "Briard", "Australian Kelpie", "Komondor", "Old English Sheepdog", "Shetland Sheepdog", "collie",
        "Border Collie", "Bouvier des Flandres dog", "Rottweiler", "German Shepherd Dog", "Dobermann", "Miniature Pinscher", "Greater Swiss Mountain Dog", 
        "Bernese Mountain Dog", "Appenzeller Sennenhund", "Entlebucher Sennenhund", "Boxer", "Bullmastiff", "Tibetan Mastiff", "French Bulldog", 
        "Great Dane", "St. Bernard", "husky", "Alaskan Malamute", "Siberian Husky", "Dalmatian", "Affenpinscher", "Basenji", "pug", "Leonberger", 
        "Newfoundland dog", "Great Pyrenees dog", "Samoyed", "Pomeranian", "Chow Chow", "Keeshond", "brussels griffon", "Pembroke Welsh Corgi", 
        "Cardigan Welsh Corgi", "Toy Poodle", "Miniature Poodle", "Standard Poodle", "Mexican hairless dog (xoloitzcuintli)", "grey wolf", 
        "Alaskan tundra wolf", "red wolf or maned wolf", "coyote", "dingo", "dhole", "African wild dog", "hyena", "red fox", "kit fox", "Arctic fox",
        "grey fox", "tabby cat", "tiger cat", "Persian cat", "Siamese cat", "Egyptian Mau", "cougar", "lynx", "leopard", "snow leopard", "jaguar", 
        "lion", "tiger", "cheetah", "brown bear", "American black bear", "polar bear", "sloth bear", "mongoose", "meerkat", "tiger beetle", "ladybug",
        "ground beetle", "longhorn beetle", "leaf beetle", "dung beetle", "rhinoceros beetle", "weevil", "fly", "bee", "ant", "grasshopper", 
        "cricket insect", "stick insect", "cockroach", "praying mantis", "cicada", "leafhopper", "lacewing", "dragonfly", "damselfly", 
        "red admiral butterfly", "ringlet butterfly", "monarch butterfly", "small white butterfly", "sulphur butterfly", "gossamer-winged butterfly", 
        "starfish", "sea urchin", "sea cucumber", "cottontail rabbit", "hare", "Angora rabbit", "hamster", "porcupine", "fox squirrel", "marmot", 
        "beaver", "guinea pig", "common sorrel horse", "zebra", "pig", "wild boar", "warthog", "hippopotamus", "ox", "water buffalo", "bison", 
        "ram (adult male sheep)", "bighorn sheep", "Alpine ibex", "hartebeest", "impala (antelope)", "gazelle", "arabian camel", "llama", "weasel",
        "mink", "European polecat", "black-footed ferret", "otter", "skunk", "badger", "armadillo", "three-toed sloth", "orangutan", "gorilla", 
        "chimpanzee", "gibbon", "siamang", "guenon", "patas monkey", "baboon", "macaque", "langur", "black-and-white colobus", "proboscis monkey", 
        "marmoset", "white-headed capuchin", "howler monkey", "titi monkey", "Geoffroy's spider monkey", "common squirrel monkey", "ring-tailed lemur", 
        "indri", "Asian elephant", "African bush elephant", "red panda", "giant panda", "snoek fish", "eel", "silver salmon", "rock beauty fish", 
        "clownfish", "sturgeon", "gar fish", "lionfish", "pufferfish", "abacus", "abaya", "academic gown", "accordion", "acoustic guitar", 
        "aircraft carrier", "airliner", "airship", "altar", "ambulance", "amphibious vehicle", "analog clock", "apiary", "apron", "trash can", 
        "assault rifle", "backpack", "bakery", "balance beam", "balloon", "ballpoint pen", "Band-Aid", "banjo", "baluster / handrail", "barbell", 
        "barber chair", "barbershop", "barn", "barometer", "barrel", "wheelbarrow", "baseball", "basketball", "bassinet", "bassoon", "swimming cap", 
        "bath towel", "bathtub", "station wagon", "lighthouse", "beaker", "military hat (bearskin or shako)", "beer bottle", "beer glass", "bell tower",
        "baby bib", "tandem bicycle", "bikini", "ring binder", "binoculars", "birdhouse", "boathouse", "bobsleigh", "bolo tie", "poke bonnet", "bookcase",
        "bookstore", "bottle cap", "hunting bow", "bow tie", "brass memorial plaque", "bra", "breakwater", "breastplate", "broom", "bucket", "buckle", 
        "bulletproof vest", "high-speed train", "butcher shop", "taxicab", "cauldron", "candle", "cannon", "canoe", "can opener", "cardigan", 
        "car mirror", "carousel", "tool kit", "cardboard box / carton", "car wheel", "automated teller machine", "cassette", "cassette player", 
        "castle", "catamaran", "CD player", "cello", "mobile phone", "chain", "chain-link fence", "chain mail", "chainsaw", "storage chest", 
        "chiffonier", "bell or wind chime", "china cabinet", "Christmas stocking", "church", "movie theater", "cleaver", "cliff dwelling", "cloak", 
        "clogs", "cocktail shaker", "coffee mug", "coffeemaker", "spiral or coil", "combination lock", "computer keyboard", "candy store", 
        "container ship", "convertible", "corkscrew", "cornet", "cowboy boot", "cowboy hat", "cradle", "construction crane", "crash helmet", 
        "crate", "infant bed", "Crock Pot", "croquet ball", "crutch", "cuirass", "dam", "desk", "desktop computer", "rotary dial telephone", 
        "diaper", "digital clock", "digital watch", "dining table", "dishcloth", "dishwasher", "disc brake", "dock", "dog sled", "dome", "doormat", 
        "drilling rig", "drum", "drumstick", "dumbbell", "Dutch oven", "electric fan", "electric guitar", "electric locomotive", "entertainment center", 
        "envelope", "espresso machine", "face powder", "feather boa", "filing cabinet", "fireboat", "fire truck", "fire screen", "flagpole", "flute",
        "folding chair", "football helmet", "forklift", "fountain", "fountain pen", "four-poster bed", "freight car", "French horn", "frying pan", 
        "fur coat", "garbage truck", "gas mask or respirator", "gas pump", "goblet", "go-kart", "golf ball", "golf cart", "gondola", "gong", "gown", 
        "grand piano", "greenhouse", "radiator grille", "grocery store", "guillotine", "hair clip", "hair spray", "half-track", "hammer", "hamper", 
        "hair dryer", "hand-held computer", "handkerchief", "hard disk drive", "harmonica", "harp", "combine harvester", "hatchet", "holster", 
        "home theater", "honeycomb", "hook", "hoop skirt", "gymnastic horizontal bar", "horse-drawn vehicle", "hourglass", "iPod", "clothes iron", 
        "carved pumpkin", "jeans", "jeep", "T-shirt", "jigsaw puzzle", "rickshaw", "joystick", "kimono", "knee pad", "knot", "lab coat", "ladle", 
        "lampshade", "laptop computer", "lawn mower", "lens cap", "letter opener", "library", "lifeboat", "lighter", "limousine", "ocean liner", 
        "lipstick", "slip-on shoe", "lotion", "music speaker", "loupe magnifying glass", "sawmill", "magnetic compass", "messenger bag", "mailbox",
        "tights", "one-piece bathing suit", "manhole cover", "maraca", "marimba", "mask", "matchstick", "maypole", "maze", "measuring cup", 
        "medicine cabinet", "megalith", "microphone", "microwave oven", "military uniform", "milk can", "minibus", "miniskirt", "minivan", 
        "missile", "mitten", "mixing bowl", "mobile home", "ford model t", "modem", "monastery", "monitor", "moped", "mortar and pestle", 
        "graduation cap", "mosque", "mosquito net", "vespa", "mountain bike", "tent", "computer mouse", "mousetrap", "moving van", "muzzle", 
        "metal nail", "neck brace", "necklace", "baby pacifier", "notebook computer", "obelisk", "oboe", "ocarina", "odometer", "oil filter", 
        "pipe organ", "oscilloscope", "overskirt", "bullock cart", "oxygen mask", "product packet / packaging", "paddle", "paddle wheel", 
        "padlock", "paintbrush", "pajamas", "palace", "pan flute", "paper towel", "parachute", "parallel bars", "park bench", "parking meter", 
        "railroad car", "patio", "payphone", "pedestal", "pencil case", "pencil sharpener", "perfume", "Petri dish", "photocopier", "plectrum", 
        "Pickelhaube", "picket fence", "pickup truck", "pier", "piggy bank", "pill bottle", "pillow", "ping-pong ball", "pinwheel", "pirate ship", 
        "drink pitcher", "block plane", "planetarium", "plastic bag", "plate rack", "farm plow", "plunger", "Polaroid camera", "pole", "police van", 
        "poncho", "pool table", "soda bottle", "plant pot", "potter's wheel", "power drill", "prayer rug", "printer", "prison", "missile", 
        "projector", "hockey puck", "punching bag", "purse", "quill", "quilt", "race car", "racket", "radiator", "radio", "radio telescope", 
        "rain barrel", "recreational vehicle", "fishing casting reel", "reflex camera", "refrigerator", "remote control", "restaurant", "revolver",
        "rifle", "rocking chair", "rotisserie", "eraser", "rugby ball", "ruler measuring stick", "sneaker", "safe", "safety pin", "salt shaker",
        "sandal", "sarong", "saxophone", "scabbard", "weighing scale", "school bus", "schooner", "scoreboard", "CRT monitor", "screw", "screwdriver",
        "seat belt", "sewing machine", "shield", "shoe store", "shoji screen / room divider", "shopping basket", "shopping cart", "shovel", 
        "shower cap", "shower curtain", "ski", "balaclava ski mask", "sleeping bag", "slide rule", "sliding door", "slot machine", "snorkel", 
        "snowmobile", "snowplow", "soap dispenser", "soccer ball", "sock", "solar thermal collector", "sombrero", "soup bowl", "keyboard space bar",
        "space heater", "space shuttle", "spatula", "motorboat", "spider web", "spindle", "sports car", "spotlight", "stage", "steam locomotive", 
        "through arch bridge", "steel drum", "stethoscope", "scarf", "stone wall", "stopwatch", "stove", "strainer", "tram", "stretcher", "couch",
        "stupa", "submarine", "suit", "sundial", "sunglasses", "sunglasses", "sunscreen", "suspension bridge", "mop", "sweatshirt", 
        "swim trunks / shorts", "swing", "electrical switch", "syringe", "table lamp", "tank", "tape player", "teapot", "teddy bear", "television",
        "tennis ball", "thatched roof", "front curtain", "thimble", "threshing machine", "throne", "tile roof", "toaster", "tobacco shop", 
        "toilet seat", "torch", "totem pole", "tow truck", "toy store", "tractor", "semi-trailer truck", "tray", "trench coat", "tricycle", "trimaran",
        "tripod", "triumphal arch", "trolleybus", "trombone", "hot tub", "turnstile", "typewriter keyboard", "umbrella", "unicycle", "upright piano",
        "vacuum cleaner", "vase", "vaulted or arched ceiling", "velvet fabric", "vending machine", "vestment", "viaduct", "violin", "volleyball",
        "waffle iron", "wall clock", "wallet", "wardrobe", "military aircraft", "sink", "washing machine", "water bottle", "water jug", "water tower",
        "whiskey jug", "whistle", "hair wig", "window screen", "window shade", "Windsor tie", "wine bottle", "airplane wing", "wok", "wooden spoon", 
        "wool", "split-rail fence", "shipwreck", "sailboat", "yurt", "website", "comic book", "crossword", "traffic or street sign", "traffic light",
        "dust jacket", "menu", "plate", "guacamole", "consomme", "hot pot", "trifle", "ice cream", "popsicle", "baguette", "bagel", "pretzel", 
        "cheeseburger", "hot dog", "mashed potatoes", "cabbage", "broccoli", "cauliflower", "zucchini", "spaghetti squash", "acorn squash", 
        "butternut squash", "cucumber", "artichoke", "bell pepper", "cardoon", "mushroom", "Granny Smith apple", "strawberry", "orange", "lemon", 
        "fig", "pineapple", "banana", "jackfruit", "cherimoya (custard apple)", "pomegranate", "hay", "carbonara", "chocolate syrup", "dough", 
        "meatloaf", "pizza", "pot pie", "burrito", "red wine", "espresso", "tea cup", "eggnog", "mountain", "bubble", "cliff", "coral reef", 
        "geyser", "lakeshore", "promontory", "sandbar", "beach", "valley", "volcano", "baseball player", "bridegroom", "scuba diver", "rapeseed", 
        "daisy", "yellow lady's slipper", "corn", "acorn", "rose hip", "horse chestnut seed", "coral fungus", "agaric", "gyromitra", 
        "stinkhorn mushroom", "earth star fungus", "hen of the woods mushroom", "bolete", "corn cob", "toilet paper"
    ],
    clevr_count_all = [
        "three", "four", "five", "six", "seven", "eight", "nine", "ten",
    ],
    clevr_closest_object_distance = [
        "very nearby",
        "nearby",
        "near",
        "",
        "distant",
        "very distant",
    ],
    mnist = [
       "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
    ],
    svhn = [
        "zero", "one", "two", "three", "four",
        "five", "six", "seven", "eight", "nine",
    ],
    kitti_closest_vehicle_distance = [
        "a photo i took of a car on my left or right side.",
        "a photo i took with a car nearby.",
        "a photo i took with a car in the distance.",
        "a photo i took with no car.",
    ],
    dmlab = [
        "nearby apple/melon",
        "far apple/melon",
        "very far apple/melon",
        "nearby lemon",
        "far lemon",
        "very far lemon",
    ],
    pets = [
    'Abyssinian', 'American Bulldog', 'American Pit Bull Terrier', 'Basset Hound', 'Beagle', 'Bengal', 'Birman', 'Bombay', 'Boxer', 'British Shorthair', 'Chihuahua', 
    'Egyptian Mau', 'English Cocker Spaniel', 'English Setter', 'German Shorthaired', 'Great Pyrenees', 'Havanese', 'Japanese Chin', 
    'Keeshond', 'Leonberger', 'Maine Coon', 'Miniature Pinscher', 'Newfoundland', 'Persian', 'Pomeranian', 'Pug', 'Ragdoll', 
    'Russian Blue', 'Saint Bernard', 'Samoyed', 'Scottish Terrier', 'Shiba Inu', 'Siamese', 'Sphynx', 'Staffordshire Bull Terrier', 
    'Wheaten Terrier', 'Yorkshire Terrier'
    ],
    pcam = [
      "lymph node",
      "lymph node containing metastatic tumor tissue",
    ],
    diabetic_retinopathy = [
        "no diabetic retinopathy",
        "mild diabetic retinopathy",
        "moderate diabetic retinopathy",
        "severe diabetic retinopathy",
        "proliferative diabetic retinopathy"
    ],
)

DEFAULT_ZEROSHOT_CLASSIFICATION_TEMPLATES = zeroshot_classification_templates["imagenet1k"]

VTAB_19TASKS = [
    "vtab/caltech101",
    "vtab/cifar100",
    "vtab/clevr_count_all",
    "vtab/clevr_closest_object_distance",
    "vtab/diabetic_retinopathy",
    "vtab/dmlab",
    "vtab/dsprites_label_orientation",
    "vtab/dsprites_label_x_position",
    "vtab/dtd",
    "vtab/eurosat",
    "vtab/kitti_closest_vehicle_distance",
    "vtab/flowers",
    "vtab/pets",
    "vtab/pcam",
    "vtab/resisc45",
    "vtab/smallnorb_label_azimuth",
    "vtab/smallnorb_label_elevation",
    "sun397",
    "vtab/svhn",
]