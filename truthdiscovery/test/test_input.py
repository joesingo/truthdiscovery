from truthdiscovery.input import SourceVariableMatrix, SourceClaimMatrix

import numpy as np
import numpy.ma as ma
import pytest


class TestVariablesMatrix:
    def test_create(self):
        # From a regular numpy array
        normal_arr = np.ones((2, 3))
        mat2 = SourceVariableMatrix(normal_arr)

        # From masked array
        masked_arr = ma.array(normal_arr,
                              mask=[[True, False, True], [False, True, False]])
        mat3 = SourceVariableMatrix(masked_arr)

    def test_num_sources_variables(self):
        mat = SourceVariableMatrix(np.array([[1, 1, 1], [2, 2, 2]]))
        assert mat.num_sources() == 2
        assert mat.num_variables() == 3

    def test_dimension(self):
        with pytest.raises(ValueError):
            arr = np.zeros((3, 3, 3))
            m = SourceVariableMatrix(arr)


class TestSourceClaimMatrix:
    def test_create(self):
        var_mat = SourceVariableMatrix(ma.masked_values([
            [7,   4,  7], [5,   1, -1], [-1,  2,  4], [7,  -1,  2],
            [-1,  1,  2]
        ], -1))

    def test_expected_value(self):
        var_mat = SourceVariableMatrix(ma.masked_values([
            [7,   4,  7], [5,   1, -1], [-1,  2,  4], [7,  -1,  2],
            [-1,  1,  2]
        ], -1))
        expected_claim_mat = np.array([
            [1, 1, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 1, 0],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 1, 0, 0, 1]
        ])
        claim_mat = SourceClaimMatrix(var_mat)
        assert claim_mat.mat.shape == expected_claim_mat.shape
        assert (claim_mat.mat == expected_claim_mat).all()

    def test_claim_var_val_mapping(self):
        var_mat = SourceVariableMatrix(ma.masked_values([
            # X   Y   Z
            [7,   4,  7],
            [5,   1, -1],
            [-1,  2,  4],
            [7,  -1,  2],
            [-1,  1,  2]
        ], -1))
        claim_mat = SourceClaimMatrix(var_mat)

        test_data = (
            (0, 0, 7),  # X = 7
            (1, 1, 4),  # Y = 4
            (2, 2, 7),  # Z = 7
            (3, 0, 5),  # X = 5
            (4, 1, 1),  # Y = 1
            (5, 1, 2),  # Y = 2
            (6, 2, 4),  # Z = 4
            (7, 2, 2),  # Z = 2
        )

        for claim_num, var_num, val in test_data:
            claim = claim_mat.get_claim(claim_num)
            assert claim.var == var_num
            assert claim.val == val

    def test_num_sources_claims(self):
        var_mat = SourceVariableMatrix(ma.masked_values([
            [7,   4,  7], [5,   1, -1], [-1,  2,  4], [7,  -1,  2],
            [-1,  1,  2]
        ], -1))
        claim_mat = SourceClaimMatrix(var_mat)
        assert claim_mat.num_sources() == 5
        assert claim_mat.num_claims() == 8
