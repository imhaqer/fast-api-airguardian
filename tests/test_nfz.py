from src.fast_api_airguardian.task import is_in_nfz

def test_in_nfz():
    """Test drone positions inside No-Fly-Zone"""

    assert is_in_nfz(100, 110) == False
    assert is_in_nfz(0,0) == True
