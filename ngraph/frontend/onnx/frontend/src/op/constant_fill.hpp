// Copyright (C) 2018-2021 Intel Corporation
// SPDX-License-Identifier: Apache-2.0
//

#pragma once

#include <memory>

#include "ngraph/node.hpp"
#include "onnx_import/core/node.hpp"

namespace ngraph {
namespace onnx_import {
namespace op {
namespace set_1 {
// ConstantFill is a deprecated experimental operator removed in ONNX 1.4
OutputVector constant_fill(const Node& node);
}  // namespace set_1

}  // namespace op

}  // namespace onnx_import

}  // namespace ngraph
