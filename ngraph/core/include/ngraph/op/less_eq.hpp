// Copyright (C) 2018-2021 Intel Corporation
// SPDX-License-Identifier: Apache-2.0
//

#pragma once

#include "ngraph/op/util/binary_elementwise_comparison.hpp"

namespace ngraph
{
    namespace op
    {
        namespace v1
        {
            /// \brief Elementwise less-than-or-equal operation.
            class NGRAPH_API LessEqual : public util::BinaryElementwiseComparison
            {
            public:
                NGRAPH_RTTI_DECLARATION;
                /// \brief Constructs a less-than-or-equal operation.
                LessEqual()
                    : util::BinaryElementwiseComparison(AutoBroadcastSpec::NUMPY)
                {
                }

                /// \brief Constructs a less-than-or-equal operation.
                ///
                /// \param arg0 Node that produces the first input tensor.
                /// \param arg1 Node that produces the second input tensor.
                /// \param auto_broadcast Auto broadcast specification
                LessEqual(const Output<Node>& arg0,
                          const Output<Node>& arg1,
                          const AutoBroadcastSpec& auto_broadcast =
                              AutoBroadcastSpec(AutoBroadcastType::NUMPY));

                virtual std::shared_ptr<Node>
                    clone_with_new_inputs(const OutputVector& new_args) const override;
                bool evaluate(const HostTensorVector& outputs,
                              const HostTensorVector& inputs) const override;
            };
        } // namespace v1
    }     // namespace op
} // namespace ngraph
