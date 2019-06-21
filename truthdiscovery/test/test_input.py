import numpy as np
import numpy.ma as ma
import pytest

from truthdiscovery.algorithm import MajorityVoting
from truthdiscovery.input import (
    Dataset,
    FileDataset,
    FileSupervisedData,
    IDMapping,
    MatrixDataset,
    SupervisedData,
    SyntheticData
)
from truthdiscovery.output import Result


class TestDataset:
    @pytest.fixture
    def data(self):
        triples = (
            ("john", "wind", "very windy"),
            ("paul", "wind", "not very windy"),
            ("george", "wind", "very windy"),
            ("ringo", "wind", "not very windy at all"),

            ("john", "rain", "dry"),
            ("george", "rain", "wet"),

            ("john", "water", "wet"),  # re-use value
            ("paul", "water", "drink"),
            ("george", "water", "drink"),

            # Mix up the order of variables
            ("ringo", "rain", "dry"),
        )
        return Dataset(triples)

    def test_num_sources_variables_claims(self, data):
        assert data.num_sources == 4
        assert data.num_variables == 3
        assert data.num_claims == 7

    def test_claims_matrix(self, data):
        expected_claim_mat = np.array([
            [1, 0, 0, 1, 0, 1, 0],
            [0, 1, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 1, 0, 1],
            [0, 0, 1, 1, 0, 0, 0],
        ])
        assert data.sc.shape == expected_claim_mat.shape
        assert np.array_equal(data.sc.toarray(), expected_claim_mat)

    def test_mut_ex_matrix(self, data):
        expected_mut_ex = np.array([
            [1, 1, 1, 0, 0, 0, 0],
            [1, 1, 1, 0, 0, 0, 0],
            [1, 1, 1, 0, 0, 0, 0],
            [0, 0, 0, 1, 1, 0, 0],
            [0, 0, 0, 1, 1, 0, 0],
            [0, 0, 0, 0, 0, 1, 1],
            [0, 0, 0, 0, 0, 1, 1],
        ])
        assert np.array_equal(data.mut_ex.toarray(), expected_mut_ex)

    def test_source_multiple_claims_for_a_single_variable(self):
        with pytest.raises(ValueError) as excinfo:
            Dataset((
                ("s1", "x", 4),
                ("s2", "x", 5),
                ("s1", "x", 5)
            ))

        err_msg = "Source 's1' claimed more than one value for variable 'x'"
        assert err_msg in str(excinfo.value)

        # Allow multiple claims; first one should be used
        data = Dataset((
            ("s1", "x", 5),
            ("s2", "x", 6),
            ("s3", "x", 5),
            ("s3", "x", 6),
        ), allow_multiple=True)
        exp_sc = np.array([
            [1, 0],
            [0, 1],
            [1, 0]
        ])
        assert np.array_equal(data.sc.toarray(), exp_sc)

    def test_num_connected_components(self):
        ds1 = Dataset([
            ("s1", "x", "a"),
            ("s2", "x", "b"),
            ("s3", "x", "a"),
        ])
        assert ds1.num_connected_components() == 1

        ds2 = Dataset([
            ("s1", "x", "a"),
            ("s2", "x", "b"),
            ("s3", "x", "a"),
            ("s4", "y", "a"),
            ("s5", "z", "a"),
            ("s6", "z", "a")
        ])
        assert ds2.num_connected_components() == 3


class TestIDMapping:
    def test_insert(self):
        mapping = IDMapping()
        # Should insert when querying for the first time
        assert mapping.get_id("hello") == 0
        assert mapping.get_id("goodbye") == 1
        # Should retrieve the same values when calling a second time
        assert mapping.get_id("hello") == 0
        # Labels can be any (hashable) type
        assert mapping.get_id(("this", "is", 4, "tuple")) == 2
        # Raise exception if disallowing inserts
        with pytest.raises(KeyError):
            mapping.get_id("something new", insert=False)
        # Should be bi-directional
        assert mapping.inverse[0] == "hello"
        assert mapping.inverse[1] == "goodbye"
        assert mapping.inverse[2] == ("this", "is", 4, "tuple")


class TestMatrixDataset:
    def test_create(self):
        # From a regular numpy array
        normal_arr = np.ones((2, 3))
        MatrixDataset(normal_arr)

        # From masked array
        masked_arr = ma.array(normal_arr,
                              mask=[[True, False, True], [False, True, False]])
        MatrixDataset(masked_arr)

    def test_num_sources_variables_claims(self):
        mat = MatrixDataset(np.array([
            [1, 4, 5],
            [2, 0, 5],
            [1, 1, 5],
            [3, 2, 5]
        ]))
        assert mat.num_sources == 4
        assert mat.num_variables == 3
        assert mat.num_claims == 8

    def test_dimension(self):
        arr = np.zeros((3, 3, 3))
        with pytest.raises(ValueError):
            MatrixDataset(arr)

    def test_from_csv(self, tmpdir):
        filepath = tmpdir.join("data.csv")
        filepath.write("\n".join([
            "1,,3, 2,6  ",  # extra whitespace should not matter
            ", 9,0,2,5",
            "3,9,  ,,1",
            "1,9  , 5.7,3,4",
            "5,1,3,1,1",
            "\n"  # new lines at the end of file should not matter
        ]))

        data = MatrixDataset.from_csv(filepath.open())
        expected_matrix = ma.masked_values([
            [1, 999, 3, 2, 6],
            [999, 9, 0, 2, 5],
            [3, 9, 999, 999, 1],
            [1, 9, 5.7, 3, 4],
            [5, 1, 3, 1, 1]
        ], 999)
        assert data.num_sources == 5
        assert data.num_variables == 5
        assert data.num_claims == 15
        assert np.array_equal(data.sv.mask, expected_matrix.mask)
        assert (data.sv == expected_matrix).all()

    def test_invalid_csv_shape(self, tmpdir):
        filepath = tmpdir.join("data.csv")
        filepath.write("\n".join([
            "1,2,",
            "1,2"
        ]))
        with pytest.raises(ValueError) as excinfo:
            MatrixDataset.from_csv(filepath.open())
        assert "Expected 3 entries in row 2, got 2" in str(excinfo.value)

    def test_from_csv_empty_rows(self, tmpdir):
        filepath = tmpdir.join("data.csv")
        filepath.write("\n".join([
            "1,2,",
            ",,",
            " ,\t,",
            "3,4,5"
        ]))
        data = MatrixDataset.from_csv(filepath.open())
        expected_matrix = ma.masked_values([
            [1, 2, 0],
            [0, 0, 0],
            [0, 0, 0],
            [3, 4, 5]
        ], 0)
        assert np.array_equal(data.sv.mask, expected_matrix.mask)
        assert (data.sv == expected_matrix).all()

    def test_from_csv_single_row_or_column(self, tmpdir):
        filepath1 = tmpdir.join("data1.csv")
        filepath1.write("1,,3,2,6")
        data1 = MatrixDataset.from_csv(filepath1.open())
        exp_sv1 = ma.masked_values([
            [1, 0, 3, 2, 6]
        ], 0)
        assert data1.num_sources == 1
        assert data1.num_variables == 4
        assert data1.num_claims == 4
        assert np.array_equal(data1.sv.mask, exp_sv1.mask)
        assert (data1.sv == exp_sv1).all()

        filepath2 = tmpdir.join("data2.csv")
        filepath2.write("1\n\n3\n2\n6")
        data2 = MatrixDataset.from_csv(filepath2.open())
        exp_sv2 = exp_sv1.T
        assert data2.num_sources == 4
        assert data2.num_variables == 1
        assert data2.num_claims == 4
        assert np.array_equal(data2.sv.mask, exp_sv2.mask)
        assert (data2.sv == exp_sv2).all()

    def test_claims_matrix(self):
        data = MatrixDataset(ma.masked_values([
            [7, 4, 7],
            [5, 1, -1],
            [-1, 2, 4],
            [7, -1, 2],
            [-1, 1, 2]
        ], -1))
        expected_claim_mat = np.array([
            [1, 1, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 1, 0],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 1, 0, 0, 1]
        ])
        assert data.sc.shape == expected_claim_mat.shape
        assert np.array_equal(data.sc.toarray(), expected_claim_mat)

    def test_mutual_exclusion_matrix(self):
        data = MatrixDataset(ma.masked_values([
            [7, 4, 7], [5, 1, -1], [-1, 2, 4], [7, -1, 2],
            [-1, 1, 2]
        ], -1))
        # Claims are:
        # 0: x=7
        # 1: y=4
        # 2: z=7
        # 3: x=5
        # 4: y=1
        # 5: y=2
        # 6: z=4
        # 7: z=2
        # Mutual exclusion groups are {0, 3}, {1, 4, 5}, {2, 6, 7}
        expected_mut_ex_mat = np.array([
            [1, 0, 0, 1, 0, 0, 0, 0],
            [0, 1, 0, 0, 1, 1, 0, 0],
            [0, 0, 1, 0, 0, 0, 1, 1],
            [1, 0, 0, 1, 0, 0, 0, 0],
            [0, 1, 0, 0, 1, 1, 0, 0],
            [0, 1, 0, 0, 1, 1, 0, 0],
            [0, 0, 1, 0, 0, 0, 1, 1],
            [0, 0, 1, 0, 0, 0, 1, 1],
        ])
        assert data.mut_ex.shape == expected_mut_ex_mat.shape
        assert np.array_equal(data.mut_ex.toarray(), expected_mut_ex_mat)

    def test_export_to_csv(self):
        data = MatrixDataset(ma.masked_values([
            # All full row
            [1, 2, 3, 4, 5, 6, 7, 8],
            # Mixed row
            [1, 2, 0, -123, 4, -2.3, 99.123, -123],
            # All empty row
            [-123, -123, -123, -123, -123, -123, -123, -123]
        ], -123))
        expected = "\n".join((
            "1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0",
            "1.0,2.0,0.0,,4.0,-2.3,99.123,",
            ",,,,,,,"
        ))
        assert data.to_csv() == expected


class TestSupervisedData:
    @pytest.fixture
    def dataset(self):
        return Dataset((
            ("s1", "x", 1), ("s1", "y", 2), ("s1", "z", 3), ("s1", "w", 4),
            ("s2", "x", 1), ("s2", "z", 3), ("s2", "w", 4),
            ("s3", "y", 2), ("s3", "z", 3), ("s3", "w", 4)
        ))

    def test_from_csv(self, tmpdir):
        filepath = tmpdir.join("data.csv")
        filepath.write("\n".join([
            "7,8,,100,",  # true values
            "1,,3,2,6",
            ",9,2,2,5",
            "3,9,,,1",
            "1,9,5,3,4",
            "5,1,3,1,1"
        ]))

        sup = SupervisedData.from_csv(filepath.open())
        data = sup.data
        expected_matrix = ma.masked_values([
            [1, 0, 3, 2, 6],
            [0, 9, 2, 2, 5],
            [3, 9, 0, 0, 1],
            [1, 9, 5, 3, 4],
            [5, 1, 3, 1, 1]
        ], 0)
        expected_values = {0: 7, 1: 8, 3: 100}
        assert data.num_sources == 5
        assert data.num_variables == 5
        assert data.num_claims == 15
        assert np.all(data.sv.mask == expected_matrix.mask)
        assert np.all(data.sv == expected_matrix)
        assert np.all(sup.values == expected_values)

    def test_accuracy(self, dataset):
        sup = SupervisedData(dataset, {"x": 5, "y": 6, "w": 8})
        test_data = (
            (2 / 3, {"x": {5: 1.0, 15: 0.8, -10: 0.5},           # correct
                     "y": {1: 0.99, 2: 0.8},                     # wrong
                     "z": {7: 0.5, 6: 0.7, -10: 0.999},          # unknown
                     "w": {1: 0.1, 2: 0.1, 3: 0.1, 8: 0.101}}),  # correct

            # Results where a variable has only one claimed value
            (1 / 2, {"x": {5: 1.0},                         # correct, only one
                     "y": {1: 0.99, 2: 0.8},                     # wrong
                     "z": {7: 0.5, 6: 0.7, -10: 0.999},          # unknown
                     "w": {1: 0.1, 2: 0.1, 3: 0.1, 8: 0.101}}),  # correct

            # Results where all claimed values are wrong
            (0, {"x": {4: 1, 2: 0.5}, "y": {4: 1}, "z": {4: 1}, "w": {4: 1}})
        )

        for expected_acc, belief in test_data:
            res = Result(
                trust={"s1": 1.5, "s2": 0.5, "s3": 0.5},
                belief=belief,
                time_taken=None
            )
            got_acc = sup.get_accuracy(res)
            assert got_acc == expected_acc

        # Results where there is a tie for most believed value
        var_beliefs = {
            "x": {5: 0.8, 5000: 0.8, 4: 0.6},  # tie: either correct or not
            "y": {6: 0.7, 1: 0.2},             # correct
            "z": {1: 0.5, 2: 0.4},             # unknown
            "w": {1: 0.5, 2: 0.4}              # wrong
        }
        res = Result(
            trust={0: 1.5, 1: 0.5, 2: 0.5}, belief=var_beliefs, time_taken=None
        )
        assert sup.get_accuracy(res) in (1 / 3, 2 / 3)

    def test_unknown_variable(self, dataset):
        sup = SupervisedData(dataset, {"hello": 42, "x": 4})
        res = Result(
            trust={"s1": 1.5, "s2": 0.5, "s3": 0.5},
            belief={
                "x": {4: 1, 2: 0.5},
                "y": {4: 1},
                "z": {4: 1},
                "w": {4: 1}
            },
            time_taken=None
        )
        # The variable "hello" should be ignored
        assert sup.get_accuracy(res) == 1

    def test_no_true_values_known(self, dataset):
        sup = SupervisedData(dataset, {})
        res = Result(
            trust={0: 0.5, 1: 0.5, 2: 0.5},
            belief={i: {4: 1} for i in range(4)},
            time_taken=None
        )
        with pytest.raises(ValueError):
            sup.get_accuracy(res)

    def test_not_enough_claimed_values(self):
        # If all variables have only one claimed value, the accuracy
        # calculation cannot be performed: an exception should be raised
        dataset = Dataset([
            ("s1", "x", 4),
            ("s2", "x", 4),
            ("s3", "x", 4),
            ("s1", "y", 1),
            ("s2", "y", 1),
            ("s3", "y", 1)
        ])
        sup = SupervisedData(dataset, {"x": 4, "y": 2})
        res = Result(
            trust={"s1": 0.3, "s2": 0.4, "s3": 0.4},
            belief={"x": {4: 1}, "y": {1: 1}},
            time_taken=None
        )
        with pytest.raises(ValueError):
            sup.get_accuracy(res)


class TestSyntheticData:
    """
    Test the SyntheticData class
    """
    def test_trust_as_list(self):
        SyntheticData(trust=[0, 1, 0.5])

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
                SyntheticData(trust, 10)

    def test_trust_range_error(self):
        invalid_trust_scores = (
            np.array([-1, 0, 0]),
            np.array([2, 0, 0]),
            np.array([np.nan, 0, 0]),
            np.array([0, 1.1, 0])
        )
        for trust in invalid_trust_scores:
            with pytest.raises(ValueError):
                SyntheticData(trust, 10)

    def test_valid_trusts(self):
        valid_trust_scores = (
            np.array([0, 0, 0]),
            np.array([1, 1, 1]),
            np.array([1 / 3, 0.5, 0.4444444]),
        )
        for trust in valid_trust_scores:
            try:
                SyntheticData(trust, 10)
            except ValueError:  # pragma: no cover
                assert False, "Unexpected error for trust = {}".format(trust)

    def test_claim_probability(self):
        trust = np.full((5,), 0.5)
        synth = SyntheticData(trust, claim_probability=1)
        # If claims made with p=1 then all possible claims should be made
        assert (~synth.data.sv.mask).all()

    def test_invalid_claim_probability(self):
        invalid_probs = (0, -1, -0.5, -0.0000001, 1.0000001)
        trust = np.full((5,), 0.5)
        for prob in invalid_probs:
            with pytest.raises(ValueError):
                SyntheticData(trust, claim_probability=prob)

    def test_domain_size(self):
        invalid_domain_sizes = (-1, 0, 1)
        trust = np.full((5,), 0.5)
        for ds in invalid_domain_sizes:
            with pytest.raises(ValueError):
                SyntheticData(trust, domain_size=ds)

    def test_export_to_csv(self, tmpdir):
        synth = SyntheticData(np.array([0.5, 0.5]), num_variables=10)
        csv_string = synth.to_csv()
        lines = [line for line in csv_string.split("\n") if line]
        assert len(lines) == 3

        filename = tmpdir.join("mydata.csv")
        filename.write(csv_string)
        loaded = SupervisedData.from_csv(filename.open())
        assert np.array_equal(loaded.values, synth.values)
        assert np.array_equal(
            loaded.data.sc.toarray(),
            synth.data.sc.toarray()
        )


class TestImplications:
    @pytest.fixture
    def triples(self):
        return [
            ("s1", "x", 1),
            ("s1", "y", 2),
            ("s1", "z", 3),
            ("s1", "w", 4),

            ("s2", "x", 2),
            ("s2", "z", 4),
            ("s2", "w", 5),

            ("s3", "y", 3),
            ("s3", "z", 3),
            ("s3", "w", 5)
        ]

    def test_implications(self, triples):
        # Test using manually crafted values
        def imp_func(var, val1, val2):
            if var == "x":
                if (val1, val2) == (1, 2):
                    return 0.85
                elif (val1, val2) == (2, 1):
                    return -0.5
                elif (val1, val2) == (1, 1):  # pragma: no cover
                    # Note: this value should not be used
                    return 10000000  # pragma: no cover
            elif var == "y":
                if (val1, val2) == (2, 3):
                    return 1
                elif (val1, val2) == (3, 2):
                    return 0.0001
            elif var == "z":
                if (val1, val2) == (3, 4):
                    return -0.3
                elif (val1, val2) == (4, 3):
                    return None
            elif var == "w":
                if (val1, val2) == (4, 5):
                    return 0.7
                elif (val1, val2) == (5, 4):
                    return -0.654

        data = Dataset(triples, implication_function=imp_func)
        # Claims are:
        # 0: x=1
        # 1: y=2
        # 2: z=3
        # 3: w=4
        # 4: x=2
        # 5: z=4
        # 6: w=5
        # 7: y=3
        expected_imp = np.array([
            [0, 0, 0, 0, 0.85, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, -0.3, 0, 0],
            [0, 0, 0, 0, 0, 0, 0.7, 0],
            [-0.5, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, -0.654, 0, 0, 0, 0],
            [0, 0.0001, 0, 0, 0, 0, 0, 0]
        ])
        assert data.imp.shape == (8, 8)
        assert np.array_equal(data.imp.toarray(), expected_imp)

    def test_invalid_implication_values(self, triples):
        def too_big(var, val1, val2):
            return 1.001

        def too_small(var, val1, val2):
            return -1.001

        with pytest.raises(ValueError):
            Dataset(triples, implication_function=too_big)
        with pytest.raises(ValueError):
            Dataset(triples, implication_function=too_small)


class TestFileDataset:
    @pytest.fixture
    def example_cls(self):
        class ExampleDataset(FileDataset):
            def get_tuples(self, fileobj):
                for line in map(str.strip, fileobj):
                    source, var, value = line.split(" | ")
                    yield (
                        "source {}".format(source),
                        "var {}".format(var),
                        int(value) * 2 + 1
                    )
        return ExampleDataset

    @pytest.fixture
    def file_contents(self):
        return "\n".join([
            "abc | xyz | 42",
            "def | xyz | 3",
            "abc | XYZ | 7",
            "ghi | XYZ | 7",
            "def | XYZ | 6",
        ])

    def test_base(self, file_contents, tmpdir):
        input_file = tmpdir.join("test_input.dataset")
        input_file.write(file_contents)
        with pytest.raises(NotImplementedError):
            FileDataset(str(input_file))

    def test_basic(self, example_cls, file_contents, tmpdir):
        input_file = tmpdir.join("test_input.dataset")
        input_file.write(file_contents)
        dataset = example_cls(str(input_file))
        # Claims should be:
        # 0: xyz = 85
        # 1: xyz = 7
        # 2: XYZ = 15
        # 3: XYZ = 13
        expected_sc = np.array([
            [1, 0, 1, 0],
            [0, 1, 0, 1],
            [0, 0, 1, 0]
        ])
        assert np.array_equal(dataset.sc.toarray(), expected_sc)

        # Use voting algorithm to get results, and check they are as expected
        res = MajorityVoting().run(dataset)

        assert res.trust == {"source abc": 1, "source def": 1, "source ghi": 1}
        assert res.belief == {
            "var xyz": {85: 0.5, 7: 0.5},
            "var XYZ": {15: 1, 13: 0.5}
        }

    def test_implications(self, example_cls, file_contents, tmpdir):
        """
        Check that claim implications can still be used with file datasets
        """
        def imp(var, val1, val2):
            if var == "var xyz":
                if (val1, val2) == (7, 85):
                    return 1
                else:
                    return -1
            else:
                if (val1, val2) == (13, 15):
                    return 0.5
                else:
                    return -0.5

        input_file = tmpdir.join("test_input.dataset")
        input_file.write(file_contents)
        dataset = example_cls(str(input_file), implication_function=imp)

        expected_imp = np.array([
            [0, -1, 0, 0],
            [1, 0, 0, 0],
            [0, 0, 0, -0.5],
            [0, 0, 0.5, 0]
        ])
        assert np.array_equal(dataset.imp.toarray(), expected_imp)


class TestFileSupervisedData:
    @pytest.fixture
    def example_cls(self):
        class ExampleSupervisedData(FileSupervisedData):
            def get_pairs(self, fileobj):
                for line in map(str.strip, fileobj):
                    var, true_val = line.split(" | ")
                    yield (var, true_val)
        return ExampleSupervisedData

    @pytest.fixture
    def file_contents(self):
        return "\n".join([
            "speed of light | c",
            "best programming language | python",
            "favourite cheese | cheddar"
        ])

    def test_base(self, file_contents, tmpdir):
        input_file = tmpdir.join("sup.dataset")
        input_file.write(file_contents)
        with pytest.raises(NotImplementedError):
            FileSupervisedData(None, str(input_file))

    def test_basic(self, example_cls, file_contents, tmpdir):
        input_file = tmpdir.join("sup.dataset")
        input_file.write(file_contents)
        sup = example_cls(None, str(input_file))
        assert sup.values == {
            "speed of light": "c",
            "best programming language": "python",
            "favourite cheese": "cheddar"
        }
