"""
 Copyright (c) 2023 Intel Corporation
 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at
      http://www.apache.org/licenses/LICENSE-2.0
 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
"""

from typing import Optional

import onnx

from nncf.data import Dataset
from nncf.quantization.telemetry_extractors import CompressionStartedWithQuantizeApi
from nncf.scopes import IgnoredScope
from nncf.parameters import ModelType
from nncf.parameters import TargetDevice
from nncf.common.quantization.structs import QuantizationPreset
from nncf.quantization.algorithms.post_training.algorithm import PostTrainingQuantization
from nncf.quantization.algorithms.post_training.algorithm import PostTrainingQuantizationParameters
from nncf.quantization.algorithms.definitions import Granularity
from nncf.telemetry import tracked_function
from nncf.telemetry.events import NNCF_ONNX_CATEGORY
from nncf.common.logging.logger import nncf_logger


@tracked_function(NNCF_ONNX_CATEGORY, [CompressionStartedWithQuantizeApi(), "target_device", "preset"])
def quantize_impl(model: onnx.ModelProto,
                  calibration_dataset: Dataset,
                  preset: QuantizationPreset,
                  target_device: TargetDevice,
                  subset_size: int,
                  fast_bias_correction: bool,
                  model_type: Optional[ModelType] = None,
                  ignored_scope: Optional[IgnoredScope] = None) -> onnx.ModelProto:
    """
    Implementation of the `quantize()` method for the ONNX backend.
    """
    additional_params = {}
    if target_device == TargetDevice.CPU_SPR:
        raise RuntimeError('target_device == CPU_SPR is not supported.')
    if model.opset_import[0].version < 10:
        raise RuntimeError('ONNX models with opset version < 10 do not support quantization.')
    if model.opset_import[0].version < 13:
        nncf_logger.warning('ONNX models with 10 < opset version < 13 do not support per-channel quantization.'
                            ' Per-tensor quantization will be applied.')
        additional_params = {'weight_granularity': Granularity.PERTENSOR,
                             'activation_granularity': Granularity.PERTENSOR}

    quantization_parameters = PostTrainingQuantizationParameters(
        preset=preset,
        target_device=target_device,
        number_samples=subset_size,
        ignored_scopes=ignored_scope,
        fast_bias_correction=fast_bias_correction,
        model_type=model_type,
        **additional_params
    )

    quantization_algorithm = PostTrainingQuantization(quantization_parameters)
    quantized_model = quantization_algorithm.apply(model, dataset=calibration_dataset)

    return quantized_model
