def test_torch_import():
    import torch
    assert torch.arange(10)[0] == 0
