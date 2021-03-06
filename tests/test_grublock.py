# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT license.

"""Unit Tests for grublock."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import unittest
import numpy as np
import tensorflow as tf

from tensorflow.contrib import rnn
from tensorflow.python.ops import variable_scope
from backend_test_base import Tf2OnnxBackendTestBase

# pylint: disable=missing-docstring,invalid-name,unused-argument,using-constant-test


# TODO: as a workaround, set batch_size to 1 for now to bypass a onnxruntime bug, revert it when the bug is fixed
class GRUBlockTests(Tf2OnnxBackendTestBase):
    def test_single_dynamic_gru(self):
        units = 5
        batch_size = 1
        x_val = np.array([[1., 1.], [2., 2.], [3., 3.], [4., 4.]], dtype=np.float32)
        x_val = np.stack([x_val] * batch_size)

        x = tf.placeholder(tf.float32, x_val.shape, name="input_1")

        # no scope
        cell = rnn.GRUBlockCell(
            units)
        outputs, cell_state = tf.nn.dynamic_rnn(
            cell,
            x,
            dtype=tf.float32)

        _ = tf.identity(outputs, name="output")
        _ = tf.identity(cell_state, name="cell_state")

        input_names_with_port = ["input_1:0"]
        feed_dict = {"input_1:0": x_val}
        output_names_with_port = ["output:0", "cell_state:0"]
        self.run_test_case(feed_dict, input_names_with_port, output_names_with_port, rtol=1e-3)

    def test_multiple_dynamic_gru(self):
        units = 5
        batch_size = 1
        x_val = np.array([[1., 1.], [2., 2.], [3., 3.], [4., 4.]], dtype=np.float32)
        x_val = np.stack([x_val] * batch_size)

        x = tf.placeholder(tf.float32, x_val.shape, name="input_1")
        _ = tf.placeholder(tf.float32, x_val.shape, name="input_2")

        gru_output_list = []
        gru_cell_state_list = []
        if True:
            # no scope
            cell = rnn.GRUBlockCell(
                units)
            outputs, cell_state = tf.nn.dynamic_rnn(
                cell,
                x,
                dtype=tf.float32)
            gru_output_list.append(outputs)
            gru_cell_state_list.append(cell_state)

        if True:
            # given scope
            cell = rnn.GRUBlockCell(
                units)
            with variable_scope.variable_scope("root1") as scope:
                outputs, cell_state = tf.nn.dynamic_rnn(
                    cell,
                    x,
                    dtype=tf.float32,
                    sequence_length=[4],
                    scope=scope)
            gru_output_list.append(outputs)
            gru_cell_state_list.append(cell_state)

        _ = tf.identity(gru_output_list, name="output")
        _ = tf.identity(gru_cell_state_list, name="cell_state")

        feed_dict = {"input_1:0": x_val}
        input_names_with_port = ["input_1:0"]
        output_names_with_port = ["output:0", "cell_state:0"]
        self.run_test_case(feed_dict, input_names_with_port, output_names_with_port, rtol=1e-3)

    def test_single_dynamic_gru_seq_length_is_const(self):
        units = 5
        batch_size = 1
        x_val = np.array([[1., 1.], [2., 2.], [3., 3.], [4., 4.], [5., 5.]], dtype=np.float32)
        x_val = np.stack([x_val] * batch_size)
        x = tf.placeholder(tf.float32, x_val.shape, name="input_1")

        # no scope
        cell = rnn.GRUBlockCell(
            units)
        outputs, cell_state = tf.nn.dynamic_rnn(
            cell,
            x,
            dtype=tf.float32,
            sequence_length=[5])

        _ = tf.identity(outputs, name="output")
        _ = tf.identity(cell_state, name="cell_state")

        feed_dict = {"input_1:0": x_val}
        input_names_with_port = ["input_1:0"]
        output_names_with_port = ["output:0", "cell_state:0"]
        self.run_test_case(feed_dict, input_names_with_port, output_names_with_port, rtol=1e-3)

    def test_single_dynamic_gru_seq_length_is_not_const(self):
        units = 5
        batch_size = 1
        x_val = np.array([[1., 1.], [2., 2.], [3., 3.], [4., 4.], [5., 5.]], dtype=np.float32)
        x_val = np.stack([x_val] * batch_size)
        x = tf.placeholder(tf.float32, x_val.shape, name="input_1")

        y_val = np.array([5], dtype=np.int32)
        seq_length = tf.placeholder(tf.int32, y_val.shape, name="input_2")

        # no scope
        cell = rnn.GRUBlockCell(
            units)
        outputs, cell_state = tf.nn.dynamic_rnn(
            cell,
            x,
            dtype=tf.float32,
            sequence_length=tf.identity(seq_length))

        _ = tf.identity(outputs, name="output")
        _ = tf.identity(cell_state, name="cell_state")

        feed_dict = {"input_1:0": x_val, "input_2:0": y_val}
        input_names_with_port = ["input_1:0", "input_2:0"]
        output_names_with_port = ["output:0", "cell_state:0"]
        self.run_test_case(feed_dict, input_names_with_port, output_names_with_port, rtol=1e-03)

    def test_single_dynamic_gru_placeholder_input(self):
        units = 5
        x_val = np.array([[1., 1.], [2., 2.], [3., 3.], [4., 4.]], dtype=np.float32)
        x_val = np.stack([x_val] * 1)
        x = tf.placeholder(tf.float32, shape=(None, 4, 2), name="input_1")

        # no scope
        cell = rnn.GRUBlockCell(
            units)
        outputs, cell_state = tf.nn.dynamic_rnn(
            cell,
            x,
            dtype=tf.float32)  # by default zero initializer is used

        _ = tf.identity(outputs, name="output")
        _ = tf.identity(cell_state, name="cell_state")

        feed_dict = {"input_1:0": x_val}
        input_names_with_port = ["input_1:0"]
        output_names_with_port = ["output:0", "cell_state:0"]
        self.run_test_case(feed_dict, input_names_with_port, output_names_with_port, rtol=1e-3)

    def test_single_dynamic_gru_ch_zero_state_initializer(self):
        units = 5
        batch_size = 1
        x_val = np.array([[1., 1.], [2., 2.], [3., 3.], [4., 4.], [5., 5.]], dtype=np.float32)
        x_val = np.stack([x_val] * batch_size)
        x = tf.placeholder(tf.float32, x_val.shape, name="input_1")
        # no scope
        cell = rnn.GRUBlockCell(
            units)

        # defining initial state
        initial_state = cell.zero_state(batch_size, dtype=tf.float32)
        outputs, cell_state = tf.nn.dynamic_rnn(
            cell,
            x,
            initial_state=initial_state,
            dtype=tf.float32)

        _ = tf.identity(outputs, name="output")
        _ = tf.identity(cell_state, name="cell_state")

        feed_dict = {"input_1:0": x_val}
        input_names_with_port = ["input_1:0"]
        output_names_with_port = ["output:0", "cell_state:0"]
        self.run_test_case(feed_dict, input_names_with_port, output_names_with_port, rtol=1e-03)

    @unittest.skip("FIXME: disable for now for accuracy problem")
    def test_single_dynamic_gru_random_weights(self):
        hidden_size = 5
        batch_size = 1
        x_val = np.array([[1., 1.], [2., 2.], [3., 3.], [4., 4.]], dtype=np.float32)
        x_val = np.stack([x_val] * batch_size)

        x = tf.placeholder(tf.float32, x_val.shape, name="input_1")
        # no scope
        cell = rnn.GRUBlockCell(
            hidden_size)

        outputs, cell_state = tf.nn.dynamic_rnn(
            cell,
            x,
            dtype=tf.float32)

        _ = tf.identity(outputs, name="output")
        _ = tf.identity(cell_state, name="cell_state")

        feed_dict = {"input_1:0": x_val}
        input_names_with_port = ["input_1:0"]
        output_names_with_port = ["output:0", "cell_state:0"]
        self.run_test_case(feed_dict, input_names_with_port, output_names_with_port, 0.0001)

    @unittest.skip("FIXME: disable for now for accuracy problem")
    def test_single_dynamic_gru_random_weights2(self):
        hidden_size = 128
        batch_size = 1
        x_val = np.random.randn(1, 133).astype('f')
        x_val = np.stack([x_val] * batch_size)

        x = tf.placeholder(tf.float32, x_val.shape, name="input_1")
        # no scope
        cell = rnn.GRUBlockCell(
            hidden_size)

        outputs, cell_state = tf.nn.dynamic_rnn(
            cell,
            x,
            dtype=tf.float32)

        _ = tf.identity(outputs, name="output")
        _ = tf.identity(cell_state, name="cell_state")

        feed_dict = {"input_1:0": x_val}
        input_names_with_port = ["input_1:0"]
        output_names_with_port = ["output:0", "cell_state:0"]
        self.run_test_case(feed_dict, input_names_with_port, output_names_with_port, 0.01)

    def test_dynamic_bigru(self):
        units = 5
        batch_size = 1
        x_val = np.array([[1., 1.], [2., 2.], [3., 3.]], dtype=np.float32)
        x_val = np.stack([x_val] * batch_size)

        x = tf.placeholder(tf.float32, x_val.shape, name="input_1")

        gru_list = []
        if True:
            # bigru, no scope
            cell1 = rnn.GRUBlockCell(
                units)
            cell2 = rnn.GRUBlockCell(
                units)
            outputs, cell_state = tf.nn.bidirectional_dynamic_rnn(
                cell1,
                cell2,
                x,
                dtype=tf.float32)
            gru_list.append(outputs)

        _ = tf.identity(outputs, name="output")
        _ = tf.identity(cell_state, name="cell_state")

        feed_dict = {"input_1:0": x_val}
        input_names_with_port = ["input_1:0"]
        output_names_with_port = ["output:0", "cell_state:0"]
        self.run_test_case(feed_dict, input_names_with_port, output_names_with_port, rtol=1e-3)

    def test_dynamic_bigru_output_consumed_only(self):
        units = 5
        batch_size = 1
        x_val = np.array([[1., 1.], [2., 2.], [3., 3.]], dtype=np.float32)
        x_val = np.stack([x_val] * batch_size)

        x = tf.placeholder(tf.float32, x_val.shape, name="input_1")

        gru_list = []
        if True:
            # bigru, no scope
            cell1 = rnn.GRUBlockCell(
                units)
            cell2 = rnn.GRUBlockCell(
                units)
            outputs, _ = tf.nn.bidirectional_dynamic_rnn(
                cell1,
                cell2,
                x,
                dtype=tf.float32)
            gru_list.append(outputs)

        _ = tf.identity(outputs, name="output")

        feed_dict = {"input_1:0": x_val}
        input_names_with_port = ["input_1:0"]
        output_names_with_port = ["output:0"]
        self.run_test_case(feed_dict, input_names_with_port, output_names_with_port, rtol=1e-3)

    def test_dynamic_bidirectional_but_one_gru(self):
        units = 5
        batch_size = 1
        x_val = np.array([[1., 1.], [2., 2.], [3., 3.]], dtype=np.float32)
        x_val = np.stack([x_val] * batch_size)

        x = tf.placeholder(tf.float32, x_val.shape, name="input_1")

        gru_list = []
        if True:
            # bigru, no scope
            cell = rnn.GRUBlockCell(
                units)
            outputs, cell_state = tf.nn.bidirectional_dynamic_rnn(
                cell,
                cell,
                x,
                dtype=tf.float32)
            gru_list.append(outputs)

        _ = tf.identity(outputs, name="output")
        _ = tf.identity(cell_state, name="cell_state")

        feed_dict = {"input_1:0": x_val}
        input_names_with_port = ["input_1:0"]
        output_names_with_port = ["output:0", "cell_state:0"]
        self.run_test_case(feed_dict, input_names_with_port, output_names_with_port, rtol=1e-3)

    def test_dynamic_bidirectional_but_one_gru_and_output_consumed_only(self):
        units = 5
        batch_size = 1
        x_val = np.array([[1., 1.], [2., 2.], [3., 3.]], dtype=np.float32)
        x_val = np.stack([x_val] * batch_size)

        x = tf.placeholder(tf.float32, x_val.shape, name="input_1")

        gru_list = []
        if True:
            # bigru, no scope
            cell = rnn.GRUBlockCell(
                units)
            outputs, _ = tf.nn.bidirectional_dynamic_rnn(
                cell,
                cell,
                x,
                dtype=tf.float32)
            gru_list.append(outputs)

        _ = tf.identity(outputs, name="output")

        feed_dict = {"input_1:0": x_val}
        input_names_with_port = ["input_1:0"]
        output_names_with_port = ["output:0"]
        self.run_test_case(feed_dict, input_names_with_port, output_names_with_port, rtol=1e-3)


if __name__ == '__main__':
    Tf2OnnxBackendTestBase.trigger(GRUBlockTests)
