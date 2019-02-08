import numpy as np
import numpy.ma as ma
import pytest

from truthdiscovery.input import Dataset, SupervisedDataset, SyntheticDataset
from truthdiscovery.output import Result


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


class TestSupervisedDataset:
    @pytest.fixture
    def matrix(self):
        return ma.masked_values([
            [1, 2, 3, 4],
            [1, 0, 3, 4],
            [0, 2, 3, 4]
        ], 0)

    def test_from_csv(self, tmpdir):
        filepath = tmpdir.join("data.csv")
        csv_file = filepath.write("\n".join([
            "7,8,,100,",  # true values
            "1,,3,2,6",
            ",9,2,2,5",
            "3,9,,,1",
            "1,9,5,3,4",
            "5,1,3,1,1"
        ]))

        data = SupervisedDataset.from_csv(str(filepath))
        expected_matrix = ma.masked_values([
            [1, 0, 3, 2, 6],
            [0, 9, 2, 2, 5],
            [3, 9, 0, 0, 1],
            [1, 9, 5, 3, 4],
            [5, 1, 3, 1, 1]
        ], 0)
        expected_values = ma.masked_values([
            7, 8, 0, 100, 0
        ], 0)
        assert data.num_sources == 5
        assert data.num_variables == 5
        assert data.num_claims == 15
        assert np.all(data.sv.mask == expected_matrix.mask)
        assert np.all(data.sv == expected_matrix)
        assert np.all(data.values.mask == expected_values.mask)
        assert np.all(data.values == expected_values)

    def test_invalid_values_shape(self, matrix):
        invalid_values = (
            np.array([]),
            np.array([0.5]),
            np.array([0.5, 0.4]),
            np.array([0.5, 0.4, 0.3]),
            np.array([0.5, 0.4, 0.3, 0.2, 0.1]),
            np.array([
                [0.5, 0.5],
                [0.5, 0.5]
            ])
        )
        for values in invalid_values:
            with pytest.raises(ValueError):
                SupervisedDataset(matrix, values)

    def test_valid_values(self, matrix):
        valid_values = (
            np.array([1, 2, 3, 4]),
            np.array([-1, -2, -3, -4]),
            ma.masked_values([1, 2, -1, 4], -1)
        )
        for values in valid_values:
            try:
                SupervisedDataset(matrix, values)
            except ValueError:  # pragma: no cover
                assert False, "Unexpected error for values = {}".format(values)

    def test_accuracy(self, matrix):
        data = SupervisedDataset(matrix, ma.masked_values([5, 6, -1, 8], -1))
        test_data = (
            (2 / 3, [{5: 1.0, 15: 0.8, -10: 0.5},           # correct
                     {1: 0.99, 2: 0.8},                     # wrong
                     {7: 0.5, 6: 0.7, -10: 0.999},          # unknown
                     {1: 0.1, 2: 0.1, 3: 0.1, 8: 0.101}]),  # correct

            # Results where a variable has only one claimed value
            (1 / 2, [{5: 1.0},                              # correct, only one
                     {1: 0.99, 2: 0.8},                     # wrong
                     {7: 0.5, 6: 0.7, -10: 0.999},          # unknown
                     {1: 0.1, 2: 0.1, 3: 0.1, 8: 0.101}])   # correct
        )

        for expected_acc, belief in test_data:
            res = Result(trust=[1.5, 0.5, 0.5], belief=belief)
            got_acc = data.get_accuracy(res)
            assert got_acc == expected_acc

        # Results where there is a tie for most believed value
        var_beliefs = [
            {5: 0.8, 5000: 0.8, 4: 0.6},  # tie: either correct or incorrect
            {6: 0.7, 1: 0.2},             # correct
            {1: 0.5, 2: 0.4},             # unknown
            {1: 0.5, 2: 0.4}              # wrong
        ]
        res = Result(trust=[1.5, 0.5, 0.5], belief=var_beliefs)
        assert data.get_accuracy(res) in (1 / 3, 2 / 3)

    def test_no_true_values_known(self, matrix):
        data = SupervisedDataset(matrix, ma.masked_all((4,)))
        res = Result(trust=[0.5] * 3, belief=[{4: 1}] * 4)
        with pytest.raises(ValueError):
            data.get_accuracy(res)


class TestResult:
    """
    Test the Result class
    """
    def test_most_believed_values(self):
        test_data = (
            ({10: 0.5, 11: 0.7, 12: 0.7}, {11, 12}),
            ({-1: 0.1, -2: 0.1, 3: 0.05}, {-1, -2}),
            ({5: 0.9, 5000: 0.8}, {5}),
            ({123.456: 0.0001}, {123.456})
        )
        trust = [0.5] * 10
        for var_belief, exp in test_data:
            res = Result(trust, [var_belief])
            assert set(res.get_most_believed_values(0)) == exp


class TestSyntheticDataset:
    """
    Test the SyntheticDataset class
    """
    def test_invalid_trust_vector_shape(self):
        invalid_trust_scores = (
            np.array([]),
            np.array([
                [0.5, 0.5],
                [0.5, 0.5]
            ])
        )
        for trust in invalid_trust_scores:
            with pytest.raises(ValueError):
                SyntheticDataset(trust, 10)

    def test_trust_range_error(self):
        invalid_trust_scores = (
            np.array([-1, 0, 0]),
            np.array([2, 0, 0]),
            np.array([np.nan, 0, 0]),
            np.array([0, 1.1, 0])
        )
        for trust in invalid_trust_scores:
            with pytest.raises(ValueError):
                SyntheticDataset(trust, 10)

    def test_valid_trusts(self):
        valid_trust_scores = (
            np.array([0, 0, 0]),
            np.array([1, 1, 1]),
            np.array([1 / 3, 0.5, 0.4444444]),
        )
        for trust in valid_trust_scores:
            try:
                SyntheticDataset(trust, 10)
            except ValueError:  # pragma: no cover
                assert False, "Unexpected error for trust = {}".format(trust)

    def test_claim_probability(self):
        trust = np.full((5,), 0.5)
        prob = SyntheticDataset(trust, claim_probability=1)
        # If claims made with p=1 then all possible claims should be made
        assert (~prob.sv.mask).all()

    def test_invalid_claim_probability(self):
        invalid_probs = (0, -1, -0.5, -0.0000001, 1.0000001)
        trust = np.full((5,), 0.5)
        for prob in invalid_probs:
            with pytest.raises(ValueError):
                SyntheticDataset(trust, claim_probability=prob)

    def test_domain_size(self):
        invalid_domain_sizes = (-1, 0, 1)
        trust = np.full((5,), 0.5)
        for ds in invalid_domain_sizes:
            with pytest.raises(ValueError):
                SyntheticDataset(trust, domain_size=ds)
