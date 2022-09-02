# Copyright (C) 2018-2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import numpy as np
import pytest
import tensorflow as tf

from common.tf_layer_test_class import CommonTFLayerTest


class TestNonMaxSupression(CommonTFLayerTest):

    # overload inputs generation to suit NMS use case
    def _prepare_input(self, inputs_dict):
        channel = ':0' if self.use_old_api else ''
        input_data = {}
        for input in inputs_dict.keys():
            input_data[input + channel] = np.random.uniform(low=0, high=1,
                                                            size=inputs_dict[input]).astype(np.float32)
        return input_data

    def create_nms_net(self, test_params: dict, with_scores: bool = False):

        tf.compat.v1.reset_default_graph()
        with tf.compat.v1.Session() as sess:

            # parametrized inputs
            number_of_boxes = test_params["number_of_boxes"]
            max_output_size = tf.constant(test_params["max_output_size"])
            iou_threshold = tf.constant(test_params["iou_threshold"])
            score_threshold = tf.constant(test_params["score_threshold"])

            # inputs to be generated
            boxes = tf.compat.v1.placeholder(tf.float32, [number_of_boxes, 4], "Input")

            # randomize boxes' confidence scores
            np.random.seed(42)
            scores = np.random.uniform(low=0.2, high=1.0, size=[number_of_boxes])

            if with_scores:
                soft_nms_sigma = tf.constant(test_params["soft_nms_sigma"])
                _ = tf.image.non_max_suppression_with_scores(boxes, scores, max_output_size,
                                             iou_threshold, score_threshold, soft_nms_sigma, name="NMS")
            else:
                _ = tf.image.non_max_suppression(boxes, scores, max_output_size,
                                                iou_threshold, score_threshold, name="NMS")
            tf_net = sess.graph_def

        ref_net = None
        return tf_net, ref_net

    test_params = [
            (
                {
                    "number_of_boxes": 50,
                    "max_output_size": 5,
                    "iou_threshold": 0.7,
                    "score_threshold": 0.8,
                    "soft_nms_sigma": 0.1
                }
            ),
            (
                {
                    "number_of_boxes": 50,
                    "max_output_size": 9,
                    "iou_threshold": 0.7,
                    "score_threshold": 0.7,
                    "soft_nms_sigma": 0.4
                }
            ),
            (
                {
                    "number_of_boxes": 50,
                    "max_output_size": 3,
                    "iou_threshold": 0.3,
                    "score_threshold": 0.8,
                    "soft_nms_sigma": 0.7
                }
            )
        ]

    @pytest.mark.parametrize("test_params", test_params)
    @pytest.mark.nightly
    @pytest.mark.precommit
    def test_NonMaxSupression(self, test_params, ie_device, precision, ir_version, temp_dir,
                              use_new_frontend, use_old_api):
        if ie_device == 'GPU':
            pytest.skip("Skip TF NonMaxSuppresion test on GPU")
        self.use_old_api = use_old_api
        self._test(*self.create_nms_net(test_params), ie_device, precision,
                   ir_version, temp_dir=temp_dir, use_new_frontend=use_new_frontend,
                   use_old_api=use_old_api)

    @pytest.mark.parametrize("test_params", test_params)
    @pytest.mark.nightly
    @pytest.mark.precommit
    def test_NonMaxSupressionWithScores(self, test_params, ie_device, precision, ir_version, temp_dir,
                                        use_new_frontend, use_old_api):
        if ie_device == 'GPU':
            pytest.skip("Skip TF NonMaxSuppresionWithScores test on GPU")
        self.use_old_api = use_old_api
        self._test(*self.create_nms_net(test_params, with_scores=True), ie_device, precision,
                   ir_version, temp_dir=temp_dir, use_new_frontend=use_new_frontend,
                   use_old_api=use_old_api)
