import numpy as np
import numpy.ma as ma
import pytest

from truthdiscovery.input import Dataset


class TestDataset:
    def test_create(self):
        # From a regular numpy array
        normal_arr = np.ones((2, 3))
        Dataset(normal_arr)

        # From masked array
        masked_arr = ma.array(normal_arr,
                              mask=[[True, False, True], [False, True, False]])
        Dataset(masked_arr)

    def test_num_sources_variables_claims(self):
        mat = Dataset(np.array([
            [1, 4, 5],
            [2, 0, 5],
            [1, 1, 5],
            [3, 2, 5]
        ]))
        assert mat.num_sources == 4
        assert mat.num_variables == 3
        assert mat.num_claims == 8

    def test_dimension(self):
        with pytest.raises(ValueError):
            arr = np.zeros((3, 3, 3))
            m = Dataset(arr)

    def test_from_csv(self, tmpdir):
        filepath = tmpdir.join("data.csv")
        csv_file = filepath.write("\n".join([
            "1,,3,2,6",
            ",9,2,2,5",
            "3,9,,,1",
            "1,9,5,3,4",
            "5,1,3,1,1"
        ]))

        data = Dataset.from_csv(str(filepath))
        expected_matrix = ma.masked_values([
            [1, 0, 3, 2, 6],
            [0, 9, 2, 2, 5],
            [3, 9, 0, 0, 1],
            [1, 9, 5, 3, 4],
            [5, 1, 3, 1, 1]
        ], 0)
        assert data.num_sources == 5
        assert data.num_variables == 5
        assert data.num_claims == 15
        assert (data.sv.mask == expected_matrix.mask).all()
        assert (data.sv == expected_matrix).all()

    def test_claims_matrix(self):
        data = Dataset(ma.masked_values([
            [7, 4, 7], [5, 1, -1], [-1, 2, 4], [7, -1, 2],
            [-1, 1, 2]
        ], -1))
        expected_claim_mat = np.array([
            [1, 0, 1, 0, 0, 1, 0, 0],
            [0, 1, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 1, 0],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [0, 0, 0, 1, 0, 0, 0, 1]
        ])
        assert data.sc.shape == expected_claim_mat.shape
        assert (data.sc == expected_claim_mat).all()

    def test_claim_var_val_mapping(self):
        data = Dataset(ma.masked_values([
            # X Y  Z
            [7, 4, 7],
            [5, 1, 0],
            [0, 2, 4],
            [7, 0, 2],
            [0, 1, 2]
        ], 0))

        test_data = (
            (0, 0, 7),  # X = 7
            (1, 0, 5),  # X = 5
            (2, 1, 4),  # Y = 4
            (3, 1, 1),  # Y = 1
            (4, 1, 2),  # Y = 2
            (5, 2, 7),  # Z = 7
            (6, 2, 4),  # Z = 4
            (7, 2, 2),  # Z = 2
        )

        for claim_num, var_num, val in test_data:
            claim = data.claims[claim_num]
            assert claim.var == var_num
            assert claim.val == val

    def test_mutual_exclusion_matrix(self):
        data = Dataset(ma.masked_values([
            [7, 4, 7], [5, 1, -1], [-1, 2, 4], [7, -1, 2],
            [-1, 1, 2]
        ], -1))
        expected_mut_ex_mat = np.array([
            [1, 1, 0, 0, 0, 0, 0, 0],
            [1, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 1, 1, 0, 0, 0],
            [0, 0, 1, 1, 1, 0, 0, 0],
            [0, 0, 1, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 1, 1],
            [0, 0, 0, 0, 0, 1, 1, 1],
            [0, 0, 0, 0, 0, 1, 1, 1]
        ])
        assert data.mut_ex.shape == expected_mut_ex_mat.shape
        assert (data.mut_ex == expected_mut_ex_mat).all()
