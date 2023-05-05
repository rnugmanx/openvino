import itertools

import pytest
import tensorflow as tf

from common.tflite_layer_test_class import TFLiteLayerTest
from common.utils.tflite_utils import data_generators

test_ops = [
    {'op_name': ['SPLIT'], 'op_func': tf.split},
]

test_params = [
    {'shape': [6], 'num_or_size_splits': 2, 'axis': 0},
    {'shape': [2, 1, 6], 'num_or_size_splits': 3, 'axis': 2},
    {'shape': [4, 3, 2, 7], 'num_or_size_splits': 4, 'axis': -4},
]


test_data = list(itertools.product(test_ops, test_params))
for i, (parameters, shapes) in enumerate(test_data):
    parameters.update(shapes)
    test_data[i] = parameters.copy()


class TestTFLiteSplitLayerTest(TFLiteLayerTest):
    inputs = ["Input"]
    outputs = ["Split"]

    def _prepare_input(self, inputs_dict, generator=None):
        if generator is None:
            return super()._prepare_input(inputs_dict)
        return data_generators[generator](inputs_dict)

    def make_model(self, params):
        assert len(set(params.keys()).intersection({'op_name', 'op_func', 'shape', 'num_or_size_splits',
                                                    'axis'})) == 5, \
            'Unexpected parameters for test: ' + ','.join(params.keys())
        self.allowed_ops = params['op_name']
        tf.compat.v1.reset_default_graph()
        with tf.compat.v1.Session() as sess:
            placeholder = tf.compat.v1.placeholder(tf.float32, params['shape'], self.inputs[0])
            params['op_func'](placeholder, params["num_or_size_splits"], params["axis"], name=self.outputs[0])
            net = sess.graph_def
        return net

    @pytest.mark.parametrize("params", test_data)
    @pytest.mark.nightly
    def test_split(self, params, ie_device, precision, temp_dir):
        self._test(ie_device, precision, temp_dir, params)
