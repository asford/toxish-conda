def test_torch_import():
    import torch

    assert torch.arange(10)[0] == 0


def test_proj_import():
    import proj
    import torch
    import numpy

    assert proj.foo == "bar"

    numpy.testing.assert_array_equal(proj.bat, torch.arange(1663))
