import itertools

import pytest
import tensorflow as tf

from common.tflite_layer_test_class import TFLiteLayerTest
from common.utils.tflite_utils import data_generators, additional_test_params

test_ops = [
    {'op_name': 'MEAN', 'op_func': tf.math.reduce_mean},
    {'op_name': 'REDUCE_ALL', 'op_func': tf.math.reduce_all, 'kwargs_to_prepare_input': 'boolean', 'dtype': tf.bool},
    {'op_name': 'REDUCE_ANY', 'op_func': tf.math.reduce_any, 'kwargs_to_prepare_input': 'boolean', 'dtype': tf.bool},
    {'op_name': 'REDUCE_MAX', 'op_func': tf.math.reduce_max},
    {'op_name': 'REDUCE_MIN', 'op_func': tf.math.reduce_min},
    {'op_name': 'REDUCE_PROD', 'op_func': tf.math.reduce_prod, 'kwargs_to_prepare_input': 'short_range'},
    {'op_name': 'SUM', 'op_func': tf.math.reduce_sum},
]

test_params = [
    {'shape': [2, 10, 10, 3]},
    {'shape': [2, 10]}
]


test_data = list(itertools.product(test_ops, test_params))
for i, (parameters, shapes) in enumerate(test_data):
    parameters.update(shapes)
    test_data[i] = parameters.copy()


test_data = list(itertools.product(test_data, additional_test_params[0]))
for i, (parameters, additional_test_params[0]) in enumerate(test_data):
    parameters.update(additional_test_params[0])
    test_data[i] = parameters.copy()


class TestTFLiteReduceLayerTest(TFLiteLayerTest):
    inputs = ["Input"]
    outputs = ["ReduceOperation"]

    def _prepare_input(self, inputs_dict, generator=None):
        if generator is None:
            return super()._prepare_input(inputs_dict)
        return data_generators[generator](inputs_dict)

    def make_model(self, params):
        assert len(set(params.keys()).intersection({'op_name', 'op_func', 'shape', 'axis'})) == 4, \
            'Unexpected parameters for test: ' + ','.join(params.keys())
        self.allowed_ops = [params['op_name']]
        tf.compat.v1.reset_default_graph()
        with tf.compat.v1.Session() as sess:
            place_holder = tf.compat.v1.placeholder(params.get('dtype', tf.float32), params['shape'],
                                                    name=self.inputs[0])
            params['op_func'](place_holder, axis=params['axis'], name=self.outputs[0])
            net = sess.graph_def
        return net

    @pytest.mark.parametrize("params", test_data)
    @pytest.mark.nightly
    def test_reduce(self, params, ie_device, precision, temp_dir):
        self._test(ie_device, precision, temp_dir, params)
