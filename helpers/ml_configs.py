import copy
from dataclasses import dataclass
from typing import Dict, Type

from pydantic import BaseModel, validator
from torch import optim
from torch.optim import lr_scheduler
from torchvision.transforms import transforms as T


def get_default_config_options():
    # Offer all torchvision transforms
    transforms = {k.lower(): T.__getattribute__(k) for k in T.__all__}

    # Add custom transform classes if required
    # transforms.update({"swapaxes": SwapAxes})

    optimizers = {"sgd": optim.SGD, "adam": optim.Adam}

    lr_schedulers = {
        "steplr": lr_scheduler.StepLR,
        "cosineannealinglr": lr_scheduler.CosineAnnealingLR,
        "cosineannealingwarmrestarts": lr_scheduler.CosineAnnealingWarmRestarts,
        "exponentiallr": lr_scheduler.ExponentialLR,
    }

    return {"transforms": transforms, "optim": optimizers, "lr_scheduler": lr_schedulers}


CURRENT_FIELD_OPTIONS = get_default_config_options()


class SerializableConfigDict(BaseModel):
    """
    Fully serializable config container. Attributes are just used for convenience. The dict version of any instances should
    always be used (e.g. SerializableConfigDict.default().dict()), in order to ensure serializability.
    Only standard Python datatypes should be used for values. The logic of constructing the actual parameter instances
    should then be implemented in 'InternalConfig', which is a dataclass that can be created from the dict version of this class
    at the start of training.
    """

    transforms: Dict[str, Dict]
    batch_size: int
    epochs: int
    workers: int
    optim: Dict[str, Dict]
    learning_rate: float
    lr_scheduler: Dict[str, Dict]

    class Config:
        allow_mutation = True
        validate_assignment = True

    @staticmethod
    def get_options():
        return CURRENT_FIELD_OPTIONS

    # validators for fields defined in CURRENT_FIELD_OPTIONS
    @validator("optim")
    def _check_valid_optim(cls, v):
        assert len(v) == 1, "Please provide only a single optimizer."
        optim_name = next(iter(v))
        assert (
            optim_name.lower() in CURRENT_FIELD_OPTIONS["optim"]
        ), f"{optim_name} not in the list of known optimizers, check SerializableConfigDict.get_options()."
        return v

    @validator("lr_scheduler")
    def _check_valid_scheduler(cls, v):
        for name in v:
            assert (
                name.lower() in CURRENT_FIELD_OPTIONS["lr_scheduler"]
            ), f"{name} not in the list of known LR schedulers, check SerializableConfigDict.get_options()."
        return v

    @validator("transforms")
    def _check_valid_transforms(cls, v):
        for name in v:
            assert (
                name.lower() in CURRENT_FIELD_OPTIONS["transforms"]
            ), f"{name} not in the list of known transforms, check SerializableConfigDict.get_options()."
        return v

    @classmethod
    def default(cls):
        return cls(
            transforms={
                "RandomCrop": {"size": 256},
                "RandomHorizontalFlip": {},
                "Normalize": {"mean": (122.1, 117.8, 118.6), "std": (19.7, 19.6, 19.1)},
            },
            batch_size=24,
            epochs=8,
            workers=6,
            optim={"adam": {"weight_decay": 1e-3}},
            learning_rate=0.0007,
            lr_scheduler={"cosineannealingwarmrestarts": {"T_0": 3, "eta_min": 1e-6}},
        )


@dataclass
class InternalConfig:
    """
    Config container for internal use in training loops etc. Due to some fields most likely holding things like
    instantiated optims etc., instances of this class will not be serializable.
    The main benefits of creating an instance of this class are type annotations, dot-attribute-access and
    cleaner training functions.
    """

    transforms: T.Compose
    batch_size: int
    epochs: int
    workers: int
    optim: Type[optim.Optimizer]
    learning_rate: float
    optim_params: Dict
    lr_scheduler: Type[lr_scheduler._LRScheduler]
    lr_scheduler_params: Dict

    # If there are params that have been added over time, they can be given default values.
    # That way, 'InternalConfig' can still be constructed from older, serialized versions of 'SerializableConfigDict',
    # in which those values are not present.
    new_param_1: int = 2000
    new_param_2: bool = True
    new_param_3: Dict = {}

    @classmethod
    def from_dict(cls, input_dict: Dict):
        """Implement logic for constructing fields from dictionary here."""

        local_dict = copy.deepcopy(input_dict)
        lookup = SerializableConfigDict.get_options()

        transforms = local_dict.pop("transforms")
        optim_arg = local_dict.pop("optim")
        scheduler_arg = local_dict.pop("lr_scheduler")

        for t in transforms:
            if t.lower() not in CURRENT_FIELD_OPTIONS["transforms"]:
                raise ValueError(
                    f"{t} not in the list of known transforms, check SerializableConfigDict.get_options()."
                )

        transform_instances = [
            lookup["transforms"][name.lower()](**params) for name, params in transforms.items()
        ]
        transforms = T.Compose(transform_instances)

        optim = next(iter(optim_arg.keys()))
        optim_params = next(iter(optim_arg.values()))
        scheduler = next(iter(scheduler_arg.keys()))
        lr_scheduler_params = next(iter(scheduler_arg.values()))

        optim_type = lookup["optim"][optim]

        scheduler_type = lookup["lr_scheduler"][scheduler.lower()]

        return cls(
            transforms=transforms,
            optim=optim_type,
            optim_params=optim_params,
            lr_scheduler=scheduler_type,
            lr_scheduler_params=lr_scheduler_params,
            **local_dict,
        )

    @classmethod
    def default(cls):
        return cls.from_dict(SerializableConfigDict.default().dict())
